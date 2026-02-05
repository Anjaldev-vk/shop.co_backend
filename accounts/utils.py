import random
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings


#-----------------------------Generate OTP----------------------------#
def generate_otp():
    return str(random.randint(100000, 999999))

#-----------------------------OTP Expiry Time----------------------------#
def get_otp_expiry(minutes=5):
    return timezone.now() + timedelta(minutes=minutes)




#-----------------------------Send OTP Email----------------------------#
def send_otp_email(email, otp, purpose="Account Verification"):
    subject = f"{purpose} OTP"
    message = f"""
Hello,

Your OTP for {purpose} is: {otp}

This OTP is valid for a limited time.
If you did not request this, please ignore this email.

Thanks,
Team ShopCo
"""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=False,
    )

