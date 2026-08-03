import re

URL = "https://www.vatanbilgisayar.com/arama/ipad-air-m4"


def temiz_fiyat(text):
    m = re.search(r"[\d\.]+", text)
    return m.group(0) if m else text


def urun_bilgilerini_bul(browser, timeout_ms):

    urunler = []

    page = browser.new_page()

    page.goto(URL, timeout=timeout_ms)

    page.wait_for_timeout(5000)

    kartlar = page.locator("a.product-list-link")

    for kart in kartlar.all():

        try:

            isim = kart.locator("h3").inner_text()

            fiyat = kart.locator("span.product-list__price").inner_text()

            link = kart.get_attribute("href")

            if not link.startswith("http"):
                link = "https://www.vatanbilgisayar.com" + link

            if "iPad Air M4" not in isim:
                continue

            boyut = "11 inç" if "11" in isim else "13 inç"

            if "128" in isim:
                kapasite = "128 GB"
            elif "256" in isim:
                kapasite = "256 GB"
            elif "512" in isim:
                kapasite = "512 GB"
            else:
                continue

            urunler.append({
                "magaza": "Vatan",
                "boyut": boyut,
                "kapasite": kapasite,
                "fiyat": temiz_fiyat(fiyat),
                "link": link
            })

            print(f"🏬 Vatan: {boyut} {kapasite} - ₺{temiz_fiyat(fiyat)}")

        except Exception as e:
    print(f"Vatan kart hatası: {e}")

    page.close()

    return urunler
