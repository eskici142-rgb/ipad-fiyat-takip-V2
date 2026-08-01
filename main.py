from playwright.sync_api import sync_playwright

from config import HEADLESS, TIMEOUT_MS
from mailer import mail_gonder
from stores.mediamarkt import urun_bilgilerini_bul


def main() -> None:
    print("=" * 50)
    print("📱 iPad Air M4 Çok Mağazalı Fiyat Takibi")
    print("=" * 50)

    tum_urunler: list[dict] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=HEADLESS,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
        )

        try:
            mediamarkt_urunleri = urun_bilgilerini_bul(
                browser=browser,
                timeout_ms=TIMEOUT_MS,
            )

            tum_urunler.extend(mediamarkt_urunleri)

        finally:
            browser.close()

    print(f"\n✅ Toplam {len(tum_urunler)} ürün bulundu.")

    if not tum_urunler:
        raise RuntimeError(
            "Hiç ürün bulunamadı. Mail gönderilmedi."
        )

    mail_gonder(tum_urunler)

    print("✅ Program tamamlandı.")


if __name__ == "__main__":
    main()
