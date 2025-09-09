from django.core.mail import send_mail
from django.conf import settings
import random
from apps.accounts.models import OTP
from django.utils import timezone
from django.utils.timezone import timedelta
from datetime import datetime

def send_notification_email(subject, message, recipient_list):
    send_mail(
        subject, 
        message,
        settings.EMAIL_HOST_USER,
        recipient_list,
        fail_silently=False
    )

def get_otp(email):
    otp_code = random.randint(100000, 999999)
    if OTP.objects.filter(email=email).exists():
        return ({"success": False, "message": "OTP Already sent.\nContact the Admin if you are having issues"})
    try:
        OTP.objects.create(
                email=email,
                code=otp_code)
    except Exception: 
        return ({"success": False, "message": "OTP failed"})
    return ({"success": True, "message": f"OTP generated for {email} \nCheck your Gmail account to verify your email address" })
 