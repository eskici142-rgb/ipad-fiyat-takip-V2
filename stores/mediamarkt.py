import re

from playwright.sync_api import Browser


STORE_NAME = "MediaMarkt"

SEARCH_URL = (
    "https://www.mediamarkt.com.tr/tr/"
    "search.html?query=iPad%20Air%20M4"
)


def temiz_fiyat(ham_fiyat: str) -> str:
    """
    MediaMarkt fiyat metninden ilk fiyatı çıkarır.

    Örnek:
    '₺38.599,– ₺38599,00 KDV dahil'
    sonuc:
    '₺38.599'
    """
    eslesme = re.search(r"₺\s?[\d.]+", ham_fiyat)

    if eslesme:
        return eslesme.group(0).strip()

    return ham_fiyat.split("KDV")[0].strip()


def urun_bilgilerini_bul(
    browser: Browser,
    timeout_ms: int = 60_000,
) -> list[dict]:
    """
    MediaMarkt arama sayfasındaki iPad Air M4 ürünlerini döndürür.
    """

    print(f"🔍 {STORE_NAME} kontrolü başlatılıyor...")

    urunler: list[dict] = []

    page = browser.new_page(
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ),
        locale="tr-TR",
    )

    try:
        page.goto(
            SEARCH_URL,
            wait_until="domcontentloaded",
            timeout=timeout_ms,
        )

        try:
            page.click("text=Kabul et", timeout=5_000)
        except Exception:
            pass

        page.wait_for_timeout(6_000)

        for _ in range(8):
            page.mouse.wheel(0, 2_500)
            page.wait_for_timeout(1_500)

        cards = page.query_selector_all(
            '[data-test="mms-product-card"]'
        )

        print(
            f"✅ {STORE_NAME}: "
            f"{len(cards)} ürün kartı bulundu."
        )

        gorulen: set[str] = set()

        for card in cards:
            try:
                title_element = card.query_selector(
                    '[data-test="product-title"]'
                )

                price_element = card.query_selector(
                    '[data-test="mms-price"]'
                )

                link_element = card.query_selector(
                    '[data-test='
                    '"mms-router-link-product-list-item-link"]'
                )

                if not title_element or not price_element:
                    continue

                title = title_element.inner_text().strip()
                fiyat = temiz_fiyat(
                    price_element.inner_text().strip()
                )

                if not (
                    "iPad Air" in title
                    and "M4" in title
                    and "Wi-Fi" in title
                ):
                    continue

                if "Cellular" in title:
                    continue

                if "128" in title:
                    kapasite = "128 GB"
                elif "256" in title:
                    kapasite = "256 GB"
                elif "512" in title:
                    kapasite = "512 GB"
                else:
                    continue

                if "11 inç" in title or "11 inc" in title:
                    boyut = "11 inç"
                elif "13 inç" in title or "13 inc" in title:
                    boyut = "13 inç"
                else:
                    continue

                link = SEARCH_URL

                if link_element:
                    href = link_element.get_attribute("href")

                    if href:
                        if href.startswith("http"):
                            link = href
                        else:
                            link = (
                                "https://www.mediamarkt.com.tr"
                                + href
                            )

                anahtar = f"{boyut}-{kapasite}"

                if anahtar in gorulen:
                    continue

                gorulen.add(anahtar)

                urun = {
                    "magaza": STORE_NAME,
                    "baslik": title,
                    "boyut": boyut,
                    "kapasite": kapasite,
                    "fiyat": fiyat,
                    "link": link,
                }

                urunler.append(urun)

                print(
                    f"📱 {STORE_NAME}: "
                    f"{boyut} {kapasite} — {fiyat}"
                )

            except Exception as hata:
                print(
                    f"⚠️ {STORE_NAME} kart okuma hatası: "
                    f"{hata}"
                )

        return urunler

    finally:
        page.close()
