from twilio.rest import Client
import random
from django.conf import settings

# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure


def generateRandomOTP(x, y):
    otp = random.randint(x, y)
    return otp


account_sid = settings.OTP_TWILIO_ACCOUNT
auth_token = settings.OTP_TWILIO_AUTH
verify_sid = settings.VERIFY_SID

# Set up Twilio client
client = Client(account_sid, auth_token)


# Send OTP via SMS
def send_otp(phone_number, otp):
    message = client.messages.create(
        body=f"Your OTP verification code is: {otp}",
        from_=f"+12517662159",
        to=phone_number,
    )
    print("message sent successfully")



# image url configuration

def get_full_profile_picture_url(user):
    if user.profile.profile_picture:
        return f"{settings.MEDIA_URL}{user.profile.profile_picture}"
    return None