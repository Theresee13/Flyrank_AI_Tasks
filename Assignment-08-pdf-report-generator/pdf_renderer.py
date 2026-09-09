"""HTML-to-PDF rendering with print-safe report tables."""

from datetime import date
from html import escape
from pathlib import Path

from playwright.sync_api import sync_playwright


def money(value: float) -> str:
    return f"GBP {value:,.2f}"


def table_rows(rows: list[dict], columns: list[str]) -> str:
    return "".join(
        "<tr>" + "".join(f"<td>{escape(str(row[column]))}</td>" for column in columns) + "</tr>"
        for row in rows
    )


def build_html(data: dict) -> str:
    product_rows = "".join(
        f"<tr><td>{escape(row['product'])}</td><td>{row['order_count']}</td><td>{money(row['revenue'])}</td></tr>"
        for row in data["top_products"]
    )
    daily_rows = "".join(
        f"<tr><td>{row['day']}</td><td>{row['orders']}</td><td>{money(row['revenue'])}</td></tr>"
        for row in data["daily_orders"]
    )
    order_rows = "".join(
        f"<tr><td>{escape(row['customer'])}</td><td>{escape(row['product'])}</td><td>{money(row['amount'])}</td><td>{row['created_at']}</td></tr>"
        for row in data["orders"]
    )
    return f"""<!doctype html><html><head><meta charset=\"utf-8\"><style>
    @page {{ size: A4; margin: 15mm; }}
    body {{ font-family: Arial, sans-serif; color: #17202a; font-size: 11px; }}
    h1 {{ color: #136f63; margin-bottom: 2px; }} h2 {{ margin-top: 25px; color: #1f4e79; }}
    .summary {{ display: flex; gap: 20px; margin: 20px 0; }} .metric {{ border-left: 4px solid #e67e22; padding-left: 12px; }}
    .metric strong {{ display: block; font-size: 19px; }} table {{ border-collapse: collapse; width: 100%; margin-bottom: 16px; }}
    th {{ background: #136f63; color: white; }} th, td {{ padding: 7px; border: 1px solid #cfd8dc; text-align: left; }}
    tr {{ break-inside: avoid; }} thead {{ display: table-header-group; }}
    </style></head><body>
    <h1>Sales Report</h1><p>Generated {date.today().isoformat()} from the local SQLite dataset.</p>
    <div class=\"summary\"><div class=\"metric\">Total orders<strong>{data['total_orders']}</strong></div><div class=\"metric\">Total revenue<strong>{money(data['total_revenue'])}</strong></div></div>
    <h2>Top products by revenue</h2><table><thead><tr><th>Product</th><th>Orders</th><th>Revenue</th></tr></thead><tbody>{product_rows}</tbody></table>
    <h2>Last seven sales days</h2><table><thead><tr><th>Date</th><th>Orders</th><th>Revenue</th></tr></thead><tbody>{daily_rows}</tbody></table>
    <h2>All orders</h2><table><thead><tr><th>Customer</th><th>Product</th><th>Amount</th><th>Date</th></tr></thead><tbody>{order_rows}</tbody></table>
    </body></html>"""


def render_pdf(data: dict, destination: Path) -> None:
    destination.parent.mkdir(exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.set_content(build_html(data), wait_until="load")
        page.pdf(path=str(destination), format="A4", print_background=True, margin={"top": "15mm", "bottom": "15mm"})
        browser.close()
