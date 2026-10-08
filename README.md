# Katalog otomasyonu / Catalog automation
**Kurgusal demo proje / Fictional demo project.**

## Türkçe
Python ve BeautifulSoup ile HTML ürün kartlarını ayrıştırıp CSV/JSON dosyalarına aktarır. Varsayılan giriş yerel kurgusal katalogdur; internet gerekmez. Eksik fiyat ve tekrarlanan kimlikler hata listesine kaydedilir.

Python 3.12+; bu klasörde sanal ortam oluşturup `python -m pip install -r requirements.txt` çalıştır. Sonra:
```powershell
python scraper.py
python -m pytest -q
```
Çıktı: `results/catalog.csv` ve `results/catalog.json`. Başka dosya: `python scraper.py --file fixtures/catalog.html --output results`. İzinli çevrimiçi kaynak: `python scraper.py --url https://example.com/catalog`; sayfanın aynı `.name`, `.price[data-price]`, `[data-product-id]` yapısına sahip olması gerekir. robots.txt kontrol edilir; yönlendirmeler takip edilmez, 10 saniye zaman aşımı ve 2 MB sınırı vardır. JavaScript ile yüklenen içerik desteklenmez. Gerçek site indirmesi yapılmadı; ağ akışı MockTransport ile test edildi.

## English
Parses HTML product cards with Python/BeautifulSoup and exports CSV/JSON. The default local fictional fixture works offline. Missing prices and duplicate IDs are recorded as errors. Install requirements in a Python 3.12+ virtual environment, then run the commands above. Results appear in `results/`.

`--file` selects a local input; `--url` selects a page you have permission to scrape with the documented selector structure. Online mode checks robots.txt, refuses redirects, times out after 10 seconds, and caps HTML at 2 MB. JavaScript-rendered pages are unsupported. Real online scraping was not performed; networking was tested through a mocked transport.

## Doğrulama notu / Verification note

Mola sitesi Opera'da elle açılıp görsel olarak kontrol edildi. Telegram botu gerçek botla elle test edildi. Chrome eklentisi Opera'da elle test edildi. Docker projesi Docker Desktop ile çalıştırıldı; GET /health, GET /products ve POST /products elle denendi. OpenAI projesi anahtarsız demo modunda. Mobil cihaz testi yapıldı; yalnızca Android/iOS/web paketleri derlendi.

The Mola website was manually opened and visually checked in Opera. The Telegram bot was manually tested with a real bot. The Chrome extension was manually tested in Opera. The Docker project was run with Docker Desktop; GET /health, GET /products and POST /products were manually exercised. The OpenAI project is in key-free demo mode. Mobile device testing was performed; only Android/iOS/web bundles were built.
