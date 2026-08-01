import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import os
from playwright.sync_api import sync_playwright

ALICI_EMAIL = "Eskici142@gmail.com"
GONDEREN_EMAIL = os.environ.get('GMAIL_USER')
GMAIL_PASSWORD = os.environ.get('GMAIL_PASSWORD')

def temiz_fiyat(ham):
    # "₺39.999,–₺39999,00KDV dahil..." -> "₺39.999"
    m = re.search(r'₺\s?[\d\.]+', ham)
    return m.group(0).strip() if m else ham.split('KDV')[0].strip()

def mediamarkt_fiyat_kontrol():
    print("🔍 Media Markt kontrolü başlatılıyor...")
    urunler = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

        url = "https://www.mediamarkt.com.tr/tr/search.html?query=iPad%20Air%20M4"
        page.goto(url, timeout=60000)

        # Çerez onayını kapat
        try:
            page.click("text=Kabul et", timeout=5000)
        except:
            pass

        page.wait_for_timeout(6000)

        # Tüm ürünleri yüklemek için kaydır
        for _ in range(8):
            page.mouse.wheel(0, 2500)
            page.wait_for_timeout(1500)

        cards = page.query_selector_all('[data-test="mms-product-card"]')
        print(f"✅ {len(cards)} ürün kartı bulundu")

        gorulen = set()
        for card in cards:
            try:
                title_el = card.query_selector('[data-test="product-title"]')
                price_el = card.query_selector('[data-test="mms-price"]')
                if not title_el or not price_el:
                    continue
                title = title_el.inner_text().strip()
                price = temiz_fiyat(price_el.inner_text().strip())

                if 'iPad Air' in title and 'M4' in title and 'Wi-Fi' in title:
                    kapasite = '128 GB' if '128' in title else '256 GB' if '256' in title else '512 GB' if '512' in title else '?'
                    boyut = '11 inç' if '11 inç' in title or '11 inc' in title else '13 inç'
                    anahtar = f"{boyut}-{kapasite}"
                    # Her boyut/kapasite için en düşük fiyatı sakla (renk farkı olabilir)
                    if anahtar not in gorulen:
                        gorulen.add(anahtar)
                        urunler.append({'fiyat': price, 'boyut': boyut, 'kapasite': kapasite})
                        print(f"📱 {boyut} {kapasite}: {price}")
            except Exception:
                continue

        browser.close()

    return urunler

def mail_gonder(urunler):
    print("📧 Mail hazırlanıyor...")
    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")

    def satir(boyut, kap):
        u = next((x for x in urunler if x['boyut'] == boyut and x['kapasite'] == kap), None)
        return f"✅ {kap}: {u['fiyat']}" if u else f"❌ {kap}: Stokta yok"

    body = f"""Merhaba,

Media Markt'tan güncel iPad Air M4 fiyatları:

📱 iPad Air 11 inç M4 Wi-Fi
{satir('11 inç', '128 GB')}
{satir('11 inç', '256 GB')}
{satir('11 inç', '512 GB')}

📱 iPad Air 13 inç M4 Wi-Fi
{satir('13 inç', '128 GB')}
{satir('13 inç', '256 GB')}
{satir('13 inç', '512 GB')}

🔗 https://www.mediamarkt.com.tr/tr/search.html?query=iPad%20Air%20M4

🌩️ Otomatik bulut servisi | 📅 {tarih}
İyi alışverişler! 🛒"""

    msg = MIMEMultipart()
    msg['From'] = GONDEREN_EMAIL
    msg['To'] = ALICI_EMAIL
    msg['Subject'] = f"📱 iPad Air M4 Fiyat Raporu - {datetime.now().strftime('%d.%m.%Y')}"
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(GONDEREN_EMAIL, GMAIL_PASSWORD)
    server.send_message(msg)
    server.quit()
    print("✅ Mail gönderildi!")

if __name__ == "__main__":
    print("=" * 40)
    print("📱 iPad Air M4 Fiyat Takip")
    print("=" * 40)
    urunler = mediamarkt_fiyat_kontrol()
    print(f"\nToplam {len(urunler)} model bulundu")
    mail_gonder(urunler)
    print("✅ Tamamlandı")
