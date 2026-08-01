import smtplib

from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import ALICI_EMAIL, GMAIL_PASSWORD, GONDEREN_EMAIL


MAGAZA_SIRASI = (
    "MediaMarkt",
    "Teknosa",
    "Vatan",
    "Hepsiburada",
    "Amazon",
)


def mail_gonder(urunler: list[dict]) -> None:
    print("📧 Mail hazırlanıyor...")

    if not GONDEREN_EMAIL:
        raise RuntimeError(
            "GMAIL_USER GitHub Secret bulunamadı."
        )

    if not GMAIL_PASSWORD:
        raise RuntimeError(
            "GMAIL_PASSWORD GitHub Secret bulunamadı."
        )

    tarih = datetime.now().strftime("%d.%m.%Y %H:%M")

    bolumler: list[str] = []

    bulunan_magazalar = {
        urun["magaza"]
        for urun in urunler
    }

    for magaza in MAGAZA_SIRASI:
        if magaza not in bulunan_magazalar:
            continue

        magaza_urunleri = [
            urun
            for urun in urunler
            if urun["magaza"] == magaza
        ]

        satirlar = [
            "",
            f"🏪 {magaza}",
            "━━━━━━━━━━━━━━━━━━━━━━━━━━━━",
        ]

        for boyut in ("11 inç", "13 inç"):
            satirlar.append(f"📱 {boyut} M4 Wi-Fi")

            for kapasite in (
                "128 GB",
                "256 GB",
                "512 GB",
            ):
                urun = next(
                    (
                        urun
                        for urun in magaza_urunleri
                        if urun["boyut"] == boyut
                        and urun["kapasite"] == kapasite
                    ),
                    None,
                )

                if urun:
                    satirlar.append(
                        f"✅ {kapasite}: "
                        f"{urun['fiyat']}"
                    )

                    satirlar.append(
                        f"   🔗 {urun['link']}"
                    )
                else:
                    satirlar.append(
                        f"❌ {kapasite}: "
                        "Bulunamadı / stokta yok"
                    )

            satirlar.append("")

        bolumler.append("\n".join(satirlar))

    body = f"""Merhaba,

iPad Air M4 güncel fiyat raporu:

{"".join(bolumler)}

🌩️ Otomatik fiyat takip sistemi
📅 {tarih}

İyi alışverişler! 🛒
"""

    mesaj = MIMEMultipart()
    mesaj["From"] = GONDEREN_EMAIL
    mesaj["To"] = ALICI_EMAIL
    mesaj["Subject"] = (
        "📱 iPad Air M4 Çok Mağazalı Fiyat Raporu - "
        + datetime.now().strftime("%d.%m.%Y")
    )

    mesaj.attach(
        MIMEText(body, "plain", "utf-8")
    )

    with smtplib.SMTP(
        "smtp.gmail.com",
        587,
        timeout=30,
    ) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(
            GONDEREN_EMAIL,
            GMAIL_PASSWORD,
        )
        server.send_message(mesaj)

    print("✅ Mail gönderildi!")
