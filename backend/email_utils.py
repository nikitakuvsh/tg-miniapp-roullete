import aiosmtplib
from email.message import EmailMessage

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "promoakcia0@gmail.com"        # ← Твоя почта
SMTP_PASS = "cyjg ordi zwir vuqm"      # ← Спец. пароль приложения

async def send_promo_code_email(to_email: str, promo_code: str, item_name: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USER
    msg["To"] = to_email
    msg["Subject"] = "Ваш подарок и промокод 🎁"
    msg.set_content(
        f"Поздравляем!\n\nВы получили приз: {item_name}\nВаш уникальный промокод: {promo_code}\n\nСпасибо за участие!"
    )

    await aiosmtplib.send(
        message=msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USER,
        password=SMTP_PASS,
    )
