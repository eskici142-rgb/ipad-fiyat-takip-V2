import smtplib

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import ALICI_EMAIL, GMAIL_PASSWORD, GONDEREN_EMAIL


def mail_gonder(urunler: list[dict]) -> None:
    print("📧 Mail hazırlanıyor...")

    if not GONDEREN_EMAIL:
        raise RuntimeError("GMAIL_USER GitHub Secret bulunamadı.")

    if not GMAIL_PASSWORD:
        raise RuntimeError("GMAIL_PASSWORD GitHub Secret bulunamadı.")

    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")

    def satir(boyut: str, kapasite: str) -> str:
        urun = next(
            (
                urun
                for urun in urunler
                if urun["boyut"] == boyut
                and urun["kapasite"] == kapasite
            ),
            None,
        )

        if not urun:
            return f"❌ {kapasite}: Stokta yok"

        return (
            f"✅ {kapasite}: {urun['fiyat']}\n"
            f"   🔗 {urun['link']}"
        )

    body = f"""Merhaba,

MediaMarkt güncel iPad Air M4 fiyatları:

📱 iPad Air 11 inç M4 Wi-Fi
{satir("11 inç", "128 GB")}
{satir("11 inç", "256 GB")}
{satir("11 inç", "512 GB")}

📱 iPad Air 13 inç M4 Wi-Fi
{satir("13 inç", "128 GB")}
{satir("13 inç", "256 GB")}
{satir("13 inç", "512 GB")}

🌩️ Otomatik fiyat takip sistemi
📅 {tarih}

İyi alışverişler! 🛒
"""

    mesaj = MIMEMultipart()
    mesaj["From"] = GONDEREN_EMAIL
    mesaj["To"] = ALICI_EMAIL
    mesaj["Subject"] = (
        "📱 iPad Air M4 Fiyat Raporu - "
        + datetime.now().strftime("%d.%m.%Y")
    )

    mesaj.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587, timeout=30) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(GONDEREN_EMAIL, GMAIL_PASSWORD)
        server.send_message(mesaj)

    print("✅ Mail gönderildi!")
