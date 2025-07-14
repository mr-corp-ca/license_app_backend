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
    ('school', 'School'),
]

USER_STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]

USER_STATUS_CHOICES = [
     ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]

COURSE_PROGRESS_CHOICES = [
    ('25', '25'),
    ('50', '50'),
    ('75', '75'),
    ('100', '100'),
    ('done', 'Done'),
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

TRANSACTION_METHOD = [
    ('stripe', 'Stripe'), 
    ('direct cash', 'Direct Cash')
    ]

TRANSACTION_STATUS = [
    ('pending', 'Pending'), 
    ('Accepedt', 'Accepted'),
    ('rejected', 'Rejected'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('rejected', 'Rejected'),
]

NOTIFICATION_TYPE_CHOICES = [
    ('general', 'General'),
]

INSTRUCTOR_REPORT_REASONS = [ 
    ('waiting-too-long','Waiting too long on a location'), 
    ('misbehaving', 'Misbehaving'), 
    ('abusing', 'Abusing'), 
    ('others', 'Others')
]

LEARNER_REPORT_RESONS = [
    ('instructor-communication', 'Instructor Communication'),
    ('punctuality-and-availability','Punctuality and Availability'),
    ('teaching-style', 'Teaching Style'),
    ('professionalism', 'Professionalism'),
    ('comfort-level-with-instructor','Comfort Level with Instructor')
]

REPORTER_CHOICES = [
    ('learner', 'Learner'),
    ('school', 'School'),
]

USER_REFERRAL_TYPE = [
    ('school', 'School'), 
    ('learner', 'Learner')
]

DELETED_REASON = [
    ('duplicate', 'Duplicate'),
    ('inappropriate', 'Inappropriate'),
    ('spam', 'Spam'),
    ('other', 'Other')
    ]

def get_masked_phone_number(user):
    if user.full_name:
        return user.full_name.capitalize()
    if user.phone_number and len(user.phone_number) >= 4:
        return f"{user.phone_number[:2]}{'*' * (len(user.phone_number) - 4)}{user.phone_number[-2:]}"
    else:
        return "Learner"
    