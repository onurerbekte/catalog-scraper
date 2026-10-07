import csv
from pathlib import Path
import httpx
import pytest
from scraper import parse_catalog, export, fetch_html


def test_fixture_and_exports(tmp_path):
    result = parse_catalog(Path("fixtures/catalog.html").read_text(encoding="utf-8"))
    assert len(result["products"]) == 3 and not result["errors"]
    assert result["products"][1]["price_cents"] == 13050
    export(result, tmp_path)
    with (tmp_path / "catalog.csv").open(encoding="utf-8-sig", newline="") as file:
        assert len(list(csv.DictReader(file))) == 3
    assert "Latte" in (tmp_path / "catalog.json").read_text(encoding="utf-8")


def test_bad_data_and_duplicate():
    card = '<article data-product-id="one"><h2 class="name">Test</h2><span class="price" data-price="1.25"></span></article>'
    result = parse_catalog(card + card + '<article data-product-id="bad"><h2 class="name">Bad</h2><span class="price" data-price="NaN"></span></article>')
    assert len(result["products"]) == 1 and len(result["errors"]) == 2
    with pytest.raises(ValueError):
        parse_catalog("<p>No catalog</p>")


def test_robots_rejection_and_mocked_download():
    def handler(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /private")
        return httpx.Response(200, text='<p>Demo</p>', headers={"content-type":"text/html; charset=utf-8"})
    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        assert "Demo" in fetch_html("https://example.test/catalog", client)
        with pytest.raises(ValueError, match="disallows"):
            fetch_html("https://example.test/private", client)


def test_csv_formula_is_text(tmp_path):
    export({"products":[{"id":"1","name":"=1+1","price_cents":0,"currency":"TRY"}],"errors":[]}, tmp_path)
    assert "'=1+1" in (tmp_path / "catalog.csv").read_text(encoding="utf-8-sig")
