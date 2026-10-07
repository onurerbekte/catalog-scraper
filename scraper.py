"""Kurgusal demo proje / Fictional demo project: catalog to CSV/JSON."""
import argparse
import csv
from decimal import Decimal, InvalidOperation
import json
from pathlib import Path
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser

from bs4 import BeautifulSoup
import httpx

USER_AGENT = "OnurCatalogDemo/1.0"
MAX_BYTES = 2_000_000


def parse_catalog(html):
    soup = BeautifulSoup(html, "html.parser")
    products, errors, seen = [], [], set()
    cards = soup.select("[data-product-id]")
    if not cards:
        raise ValueError("No product cards found / Ürün kartı bulunamadı")
    for index, card in enumerate(cards, 1):
        try:
            product_id = card.get("data-product-id", "").strip()
            title_node, price_node = card.select_one(".name"), card.select_one(".price")
            if not product_id or not title_node or not price_node:
                raise ValueError("Missing id, name or price / Eksik kimlik, ad veya fiyat")
            name = title_node.get_text(" ", strip=True)
            raw = price_node.get("data-price")
            if not name or raw is None:
                raise ValueError("Missing name or numeric price / Eksik ad veya sayısal fiyat")
            amount = Decimal(raw)
            if not amount.is_finite() or amount < 0 or amount.as_tuple().exponent < -2:
                raise ValueError("Invalid non-negative two-decimal price / Geçersiz fiyat")
            if product_id in seen:
                raise ValueError("Duplicate product id / Tekrarlanan ürün kimliği")
            seen.add(product_id)
            products.append({"id":product_id, "name":name, "price_cents":int(amount * 100), "currency":"TRY"})
        except (ValueError, InvalidOperation) as exc:
            errors.append({"card":index, "error":str(exc)})
    return {"products":products, "errors":errors}


def fetch_html(url, client=None):
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError("Use a public HTTP(S) URL without credentials / Kimliksiz HTTP(S) adresi kullan")
    owned = client is None
    client = client or httpx.Client(timeout=10, follow_redirects=False, headers={"User-Agent":USER_AGENT})
    try:
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        robots = client.get(robots_url)
        if robots.status_code == 200:
            rules = RobotFileParser()
            rules.parse(robots.text.splitlines())
            if not rules.can_fetch(USER_AGENT, url):
                raise ValueError("robots.txt disallows this URL / robots.txt bu adresi engelliyor")
        elif robots.status_code != 404:
            raise ValueError("robots.txt could not be verified / robots.txt doğrulanamadı")
        with client.stream("GET", url) as response:
            response.raise_for_status()
            if "text/html" not in response.headers.get("content-type", ""):
                raise ValueError("Expected HTML / HTML bekleniyor")
            content = bytearray()
            for chunk in response.iter_bytes():
                content.extend(chunk)
                if len(content) > MAX_BYTES:
                    raise ValueError("HTML exceeds 2 MB / HTML 2 MB sınırını aşıyor")
            return content.decode(response.encoding or "utf-8", errors="replace")
    finally:
        if owned:
            client.close()


def export(result, directory):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "catalog.csv").open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["id", "name", "price_cents", "currency"])
        writer.writeheader()
        for product in result["products"]:
            # CSV cells starting with spreadsheet operators are stored as text.
            writer.writerow({key:("'"+value if isinstance(value,str) and value.startswith(("=", "+", "-", "@")) else value) for key,value in product.items()})
    (directory / "catalog.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="HTML catalog automation / HTML katalog otomasyonu")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--file", type=Path, default=None)
    source.add_argument("--url", help="Only pages you are allowed to scrape / İzinli sayfalar")
    parser.add_argument("--output", type=Path, default=Path("results"))
    args = parser.parse_args()
    try:
        html = fetch_html(args.url) if args.url else (args.file or Path(__file__).parent / "fixtures/catalog.html").read_text(encoding="utf-8")
        result = parse_catalog(html)
        if not result["products"]:
            raise ValueError("No valid products / Geçerli ürün yok")
        export(result, args.output)
        print(f"Products / Ürünler: {len(result['products'])}; errors / hatalar: {len(result['errors'])}")
    except (ValueError, OSError, httpx.HTTPError) as exc:
        parser.exit(1, f"Failed / Başarısız: {exc}\n")


if __name__ == "__main__":
    main()
