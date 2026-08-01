import re
from urllib.parse import urljoin

from playwright.sync_api import Browser


STORE_NAME = "Teknosa"

SEARCH_URL = "https://www.teknosa.com/arama/?s=ipad%20air%20m4"


def temiz_fiyat(ham_fiyat: str) -> str | None:
    """
    Kart metninden TL fiyatını bulur.

    Örnek:
    41.999 TL
    41.999,00 TL
    """
    eslesmeler = re.findall(
        r"(\d{2,3}(?:\.\d{3})+(?:,\d{2})?)\s*TL",
        ham_fiyat,
        flags=re.IGNORECASE,
    )

    if not eslesmeler:
        return None

    fiyatlar = []

    for eslesme in eslesmeler:
        tam_kisim = eslesme.split(",")[0]
        sayi = int(tam_kisim.replace(".", ""))

        # Taksit, aksesuar veya anlamsız rakamları ele.
        if 20_000 <= sayi <= 150_000:
            fiyatlar.append(sayi)

    if not fiyatlar:
        return None

    en_dusuk = min(fiyatlar)

    return "₺" + f"{en_dusuk:,}".replace(",", ".")


def urun_bilgilerini_bul(
    browser: Browser,
    timeout_ms: int = 60_000,
) -> list[dict]:
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

        page.wait_for_timeout(6_000)

        # Dinamik ürünleri yüklemek için aşağı kaydır.
        for _ in range(8):
            page.mouse.wheel(0, 2_500)
            page.wait_for_timeout(1_200)

        # Teknosa ürün URL'lerinde genellikle "-p-" bulunuyor.
        product_links = page.locator('a[href*="-p-"]')

        print(
            f"✅ {STORE_NAME}: "
            f"{product_links.count()} ürün bağlantısı bulundu."
        )

        gorulen_linkler: set[str] = set()
        en_ucuzlar: dict[str, dict] = {}

        for index in range(product_links.count()):
            link_element = product_links.nth(index)

            try:
                href = link_element.get_attribute("href")

                if not href:
                    continue

                link = urljoin(SEARCH_URL, href)

                if link in gorulen_linkler:
                    continue

                gorulen_linkler.add(link)

                # Bağlantının bulunduğu en yakın ürün kutusunun metnini al.
                kart = link_element.locator(
                    "xpath=ancestor::*[self::article "
                    "or self::li "
                    "or contains(@class,'product')][1]"
                )

                if kart.count() == 0:
                    continue

                kart_metni = kart.inner_text(timeout=3_000).strip()
                baslik = link_element.inner_text(timeout=2_000).strip()

                if not baslik:
                    baslik = kart_metni.split("\n")[0].strip()

                kontrol_metni = (
                    baslik + " " + kart_metni + " " + link
                ).lower()

                if not (
                    "ipad" in kontrol_metni
                    and "air" in kontrol_metni
                    and "m4" in kontrol_metni
                ):
                    continue

                if not (
                    "wi-fi" in kontrol_metni
                    or "wifi" in kontrol_metni
                    or "wi fi" in kontrol_metni
                ):
                    continue

                if "cellular" in kontrol_metni:
                    continue

                if "128gb" in kontrol_metni or "128 gb" in kontrol_metni:
                    kapasite = "128 GB"
                elif "256gb" in kontrol_metni or "256 gb" in kontrol_metni:
                    kapasite = "256 GB"
                elif "512gb" in kontrol_metni or "512 gb" in kontrol_metni:
                    kapasite = "512 GB"
                else:
                    continue

                if (
                    "11 inch" in kontrol_metni
                    or "11 inç" in kontrol_metni
                    or '11"' in kontrol_metni
                ):
                    boyut = "11 inç"
                elif (
                    "13 inch" in kontrol_metni
                    or "13 inç" in kontrol_metni
                    or '13"' in kontrol_metni
                ):
                    boyut = "13 inç"
                else:
                    continue

                fiyat = temiz_fiyat(kart_metni)

                if not fiyat:
                    continue

                fiyat_sayisi = int(
                    fiyat.replace("₺", "").replace(".", "")
                )

                anahtar = f"{boyut}-{kapasite}"

                urun = {
                    "magaza": STORE_NAME,
                    "baslik": baslik,
                    "boyut": boyut,
                    "kapasite": kapasite,
                    "fiyat": fiyat,
                    "fiyat_sayisi": fiyat_sayisi,
                    "link": link,
                }

                mevcut = en_ucuzlar.get(anahtar)

                if (
                    mevcut is None
                    or fiyat_sayisi < mevcut["fiyat_sayisi"]
                ):
                    en_ucuzlar[anahtar] = urun

            except Exception as hata:
                print(
                    f"⚠️ {STORE_NAME} kart okuma hatası: "
                    f"{hata}"
                )

        urunler = list(en_ucuzlar.values())

        for urun in urunler:
            # Diğer modüllerle aynı veri yapısını döndür.
            urun.pop("fiyat_sayisi", None)

            print(
                f"📱 {STORE_NAME}: "
                f"{urun['boyut']} "
                f"{urun['kapasite']} — "
                f"{urun['fiyat']}"
            )

        return urunler

    finally:
        page.close()
