"""A9: a small, cached, polite Books to Scrape data pipeline."""

import argparse
import json
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup
from pydantic import BaseModel, ConfigDict, Field, HttpUrl, ValidationError

BASE_URL = "https://books.toscrape.com/"
USER_AGENT = "FlyRankInternshipA9/1.0 (+https://github.com/Leosce/flyrank-task-api)"
REQUEST_TIMEOUT_SECONDS = 10
MINIMUM_DELAY_SECONDS = 0.5
ROOT = Path(__file__).parent
CACHE = ROOT / "cache"
OUTPUT = ROOT / "output"


class BookRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1)
    product_url: HttpUrl
    price_text: str
    price_gbp: float = Field(ge=0)
    availability_text: str
    rating_text: str
    description: str | None
    source_page: HttpUrl
    fetched_at: str


@dataclass
class RunStats:
    started_at: str
    pages_fetched: int = 0
    cache_hits: int = 0
    detail_pages: int = 0
    valid_records: int = 0
    invalid_records: int = 0
    robots_result: str = "not checked"
    failed_pages: list[dict[str, str]] = field(default_factory=list)


class PoliteFetcher:
    def __init__(self, stats: RunStats) -> None:
        self.stats = stats
        self.last_request_at = 0.0

    def fetch(self, url: str, cache_name: str) -> str:
        path = CACHE / cache_name
        if path.exists():
            self.stats.cache_hits += 1
            print(f"CACHE HIT {url} bytes={path.stat().st_size}")
            return path.read_text(encoding="utf-8")

        wait = MINIMUM_DELAY_SECONDS - (time.monotonic() - self.last_request_at)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(2):
            try:
                request = Request(url, headers={"User-Agent": USER_AGENT})
                with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                    if response.status != 200:
                        raise HTTPError(url, response.status, "unexpected response", response.headers, None)
                    body = response.read().decode("utf-8")
                self.last_request_at = time.monotonic()
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(body, encoding="utf-8")
                self.stats.pages_fetched += 1
                print(f"FETCH {url} bytes={len(body.encode('utf-8'))}")
                return body
            except HTTPError as error:
                if error.code not in {408, 429, 500, 502, 503, 504} or attempt == 1:
                    raise
            except URLError:
                if attempt == 1:
                    raise
            time.sleep(1)
        raise RuntimeError("unreachable")


def clean_text(value: str | None) -> str:
    return " ".join((value or "").split())


def cache_name(url: str) -> str:
    parsed = urlparse(url)
    safe = re.sub(r"[^a-zA-Z0-9]+", "-", f"{parsed.netloc}{parsed.path}").strip("-")
    return f"{safe}.html"


def extract_catalogue_links(html: str, page_url: str) -> tuple[list[str], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    links = [urljoin(page_url, item["href"]) for item in soup.select("article.product_pod h3 a[href]")]
    next_link = soup.select_one("li.next a[href]")
    return links, urljoin(page_url, next_link["href"]) if next_link else None


def extract_book(html: str, product_url: str, source_page: str) -> dict[str, Any]:
    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one("div.product_main")
    if product is None:
        raise ValueError("Product content was not found")
    price_text = clean_text(product.select_one(".price_color").get_text() if product.select_one(".price_color") else None)
    price_match = re.search(r"([0-9]+(?:\.[0-9]{1,2})?)", price_text)
    if not price_match:
        raise ValueError("Price could not be normalized")
    description_node = soup.select_one("#product_description + p")
    rating_node = product.select_one("p.star-rating")
    rating_classes = rating_node.get("class", []) if rating_node else []
    rating = next((name for name in rating_classes if name != "star-rating"), "Unrated")
    return {
        "title": clean_text(product.select_one("h1").get_text() if product.select_one("h1") else None),
        "product_url": product_url,
        "price_text": price_text,
        "price_gbp": float(price_match.group(1)),
        "availability_text": clean_text(product.select_one(".availability").get_text() if product.select_one(".availability") else None),
        "rating_text": rating,
        "description": clean_text(description_node.get_text()) if description_node else None,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True), encoding="utf-8")


def run(include_broken_url: bool = False) -> dict[str, Any]:
    started = time.monotonic()
    stats = RunStats(started_at=datetime.now(timezone.utc).isoformat())
    fetcher = PoliteFetcher(stats)
    robots_url = urljoin(BASE_URL, "robots.txt")
    try:
        fetcher.fetch(robots_url, cache_name(robots_url))
        stats.robots_result = "robots.txt fetched successfully"
        stats.pages_fetched -= 1
    except HTTPError as error:
        stats.robots_result = "no robots file found" if error.code == 404 else f"robots request returned HTTP {error.code}"
    except URLError as error:
        stats.robots_result = f"robots request failed: {error.reason}"
    catalogue_url = BASE_URL
    source_pages: list[tuple[str, str]] = []
    discovered: list[tuple[str, str]] = []

    for _ in range(3):
        catalogue_html = fetcher.fetch(catalogue_url, cache_name(catalogue_url))
        source_pages.append((catalogue_url, catalogue_html))
        links, next_url = extract_catalogue_links(catalogue_html, catalogue_url)
        discovered.extend((link, catalogue_url) for link in links)
        if not next_url:
            break
        catalogue_url = next_url

    unique: dict[str, str] = {}
    for link, source_page in discovered:
        unique.setdefault(link, source_page)
    if include_broken_url:
        unique["https://books.toscrape.com/catalogue/not-a-real-book/index.html"] = source_pages[0][0]

    records: dict[str, dict[str, Any]] = {}
    errors: list[dict[str, str]] = []
    for product_url, source_page in unique.items():
        try:
            html = fetcher.fetch(product_url, cache_name(product_url))
            stats.detail_pages += 1
            raw = extract_book(html, product_url, source_page)
            record = BookRecord.model_validate(raw).model_dump(mode="json")
            records[product_url] = record
        except (HTTPError, URLError, ValueError, ValidationError) as error:
            stats.invalid_records += 1
            failure = {"url": product_url, "reason": str(error)}
            stats.failed_pages.append(failure)
            errors.append(failure)

    stats.valid_records = len(records)
    report = {
        **asdict(stats),
        "catalogue_pages": len(source_pages),
        "discovered": len(discovered),
        "unique_urls": len(unique),
        "duration_seconds": round(time.monotonic() - started, 2),
    }
    write_json(OUTPUT / "books.json", list(records.values()))
    write_json(OUTPUT / "errors.json", errors)
    write_json(OUTPUT / "run-report.json", report)
    print(f"catalogue_pages={len(source_pages)} discovered={len(discovered)} unique_urls={len(unique)}")
    print(f"detail_pages={stats.detail_pages} valid_records={stats.valid_records} failed_pages={len(stats.failed_pages)}")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the polite Books to Scrape pipeline.")
    parser.add_argument("--include-broken-url", action="store_true", help="Add one local failure-injection URL.")
    run(include_broken_url=parser.parse_args().include_broken_url)
