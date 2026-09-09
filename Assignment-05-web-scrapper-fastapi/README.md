# Assignment A9: The Polite Scraper

This project contains a standalone Python pipeline in [`scraper/`](./scraper) that collects exactly the first three catalogue pages and their 60 book pages from [Books to Scrape](https://books.toscrape.com/), a public sandbox made specifically for scraping practice.

## Target classification

- **Target:** Books to Scrape, a practice sandbox rather than a production publisher or shop.
- **Scope:** only its first three catalogue pages and the 60 linked book-detail pages.
- **Data:** public book title, price, stock text, star text, optional description, source page, and fetch timestamp.
- **Robots check:** the runner requests `https://books.toscrape.com/robots.txt` once and records either the result or `no robots file found` in `output/run-report.json`.

I will not reuse this code on another site without checking its rules and terms first.

## Run it

```powershell
cd scraper
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
pytest -q
```

The first run fetches and caches each real response; reruns print `CACHE HIT` and use the saved copies. Every real request identifies itself with `FlyRankInternshipA9/1.0`, uses a ten-second timeout, checks for HTTP 200, and waits at least 500 ms between requests. Retry is limited to one extra attempt for timeouts and temporary HTTP failures; 403 and 404 are logged without retrying.

Use `python main.py --include-broken-url` to prove one failed detail URL is recorded while the good records survive.

## Live verification

Verified locally on 2026-09-09 with Python 3.14 and the included test suite (`3 passed`). The target was the documented Books to Scrape practice sandbox only.

| Check | Observed result |
| --- | --- |
| Initial collection | 3 catalogue pages, 60 discovered URLs, 60 unique URLs, 60 detail pages, 60 valid records, 0 failed pages |
| Cache rerun | 60 records with 60 unique URLs; 63 cache hits; 0 live content pages fetched; completed in 1.81 seconds |
| Failure isolation | Injected `https://books.toscrape.com/catalogue/not-a-real-book/index.html`; 60 valid records remained and `errors.json` recorded one `HTTP Error 404: Not Found` |

The cache rerun also reported `no robots file found`, which is the expected recorded result for the target's `robots.txt` request. The failed-URL run intentionally does not retry the 404, consistent with the retry policy.

## Output and record shape

- `scraper/output/books.json`: schema-validated, de-duplicated records keyed by absolute product URL.
- `scraper/output/errors.json`: rejected records and failed page reasons.
- `scraper/output/run-report.json`: start time, duration, fetches, cache hits, valid/invalid records, and failed pages.

```json
{
  "title": "A Light in the Attic",
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "price_text": "GBP51.77",
  "price_gbp": 51.77,
  "availability_text": "In stock (22 available)",
  "rating_text": "Three",
  "description": null,
  "source_page": "https://books.toscrape.com/",
  "fetched_at": "ISO-8601 timestamp"
}
```

No browser is needed for the core assignment: the data is already in the HTML sent by the server, so a browser would only add cost. Use an official API when one exists; never bypass logins, paywalls, robots rules, or blocks; collect only the data needed for the stated purpose.
