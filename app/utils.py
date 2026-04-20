import random
from django.core.mail import send_mail

def generate_code():
    return random.randint(100000, 999999)

def send_register_email(to_email, code):
    subject = "Tasdiqlash kodi"
    message = f"Sizning kodingiz: {code}"
    from_email = "admin@novamarket.uz"

    send_mail(subject, message, from_email, [to_email])