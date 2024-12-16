import random
import string
from twilio.rest import Client
from django.conf import settings 



def create_slug_for_store(name):
    from user_management_app.models import User
    # Generate initial slug
    base_slug = name.split()[0].upper()
    slug = f"{base_slug}-{''.join(random.choice(string.digits) for _ in range(4))}"
    
    while User.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{''.join(random.choice(string.digits) for _ in range(4))}"
    
    return slug

def sendSMS(number, otp):
    client = Client(settings.ACCOUNT_SID, settings.AUTH_TOKEN)
    message = client.messages.create(
        body=f'Use this OTP {otp} for login .',
        from_='+15023243748',
        to=f'+92{number}'
    )


USER_TYPE_CHOICES = [
    ('admin', 'Owner Admin'),
    ('learner', 'Learner'),
    ('instructor', 'Instructor'),
]

RATING_CHOICES = [
        (1, '1 - Disappointed'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5 - Satisfied'),
    ]

SOCIAL_PLATFORM_CHOICES = [
    ('facebook', 'Facebook'),
    ('google', 'Google'),
]

TRANSACTION_CHOICES = [
    ('deposit', 'Deposit'), 
    ('withdraw', 'Withdraw')
    ]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]

NOTIFICATION_TYPE_CHOICES = [
    ('sms', 'SMS'),
    ('email', 'EMAIL'),
    ('push-notification', 'Push Notification'),
]