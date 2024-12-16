from django.conf import settings
from driving_license import settings
from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from twilio.rest import Client
import firebase_admin
from firebase_admin import messaging

def send_email_code(code, user):
    if code is None:
        return response({
            'message': 'no code'
        })
    
    if user is None:
        return response({
            'message': 'no user'
        })
    
    email = user.email
    print('**********************************', email)
    html_template = render_to_string('license_app/emails/send_otp.html',
                            {
                                'code':code,
                                'user':user
                            })
    text_template = strip_tags(html_template)
    # Getting Email ready
    from_email = '"MR" <{}>'.format(settings.EMAIL_HOST_USER)

    email = EmailMultiAlternatives(
        'Code Verification',
        text_template,
        from_email,
        [email],
    )
    email.attach_alternative(html_template, "text/html")
    try:
        email.send()
    except Exception as e:
        print('******  email  **',e)




if not firebase_admin._apps:
    firebase_admin.initialize_app()

def send_push_notification(user, title, message):
    fcm_token = user.profile.fcm_token

    if fcm_token:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=message,
            ),
            token=fcm_token,
        )

        response = messaging.send(message)

        print(f'Push notification sent: {response}')



def send_sms(phone_number, message):
    account_sid = settings.ACCOUNT_SID
    auth_token = settings.AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=message,
        from_='your_twilio_phone_number',
        to=phone_number
    )

    print(f'SMS sent: {message.sid}')


def send_email_certificate(image, email):
    if image is None:
        return response({
            'message': 'no code'
        })
    
    if email is None:
        return response({
            'message': 'no user'
        })
    
    html_template = render_to_string('license_app/emails/certification.html',
                            {
                                'Certificate': f'{settings.DOMAIN}{image}',

                                'u':email
                            })
    text_template = strip_tags(html_template)
    # Getting Email ready
    from_email = '"MR" <{}>'.format(settings.EMAIL_HOST_USER)

    email = EmailMultiAlternatives(
        'Code Verification',
        text_template,
        from_email,
        [email],
    )
    email.attach_alternative(html_template, "text/html")
    try:
        email.send()
    except Exception as e:
        print('******  email  **',e)
