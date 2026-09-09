from main import clean_text, extract_catalogue_links, extract_book


def test_normalizes_whitespace() -> None:
    assert clean_text("  In\n stock  ") == "In stock"


def test_extracts_absolute_catalogue_links() -> None:
    html = '<article class="product_pod"><h3><a href="catalogue/book/index.html">Book</a></h3></article><li class="next"><a href="page-2.html">next</a></li>'
    links, next_url = extract_catalogue_links(html, "https://books.toscrape.com/")
    assert links == ["https://books.toscrape.com/catalogue/book/index.html"]
    assert next_url == "https://books.toscrape.com/page-2.html"


def test_extracts_missing_description_as_none() -> None:
    html = '''<div class="product_main"><h1> Book </h1><p class="price_color">£12.50</p><p class="availability"> In stock </p><p class="star-rating Three"></p></div>'''
    record = extract_book(html, "https://books.toscrape.com/catalogue/book/index.html", "https://books.toscrape.com/")
    assert record["description"] is None
    assert record["price_gbp"] == 12.5
