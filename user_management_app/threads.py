from django.conf import settings
from driving_license import settings
from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags
from twilio.rest import Client
import firebase_admin
from datetime import datetime
from firebase_admin import messaging
from fcm_django.models import FCMDevice
from firebase_admin.messaging import Message
from firebase_admin.messaging import Notification as FB_Notification
import firebase_admin
from firebase_admin import credentials

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

def send_push_notification(user, title, message, notification_type):
    current_datetime = datetime.now()
    try:
        # Ensure Firebase app is initialized
        if not firebase_admin._apps:
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
            firebase_admin.initialize_app(cred)

        fb_body = {
            'created_at': str(current_datetime),
            'text': str(message),
            'type': 'accept',
            'notification_type': str(notification_type),
        }
        
        devices = FCMDevice.objects.filter(user=user)
        
        for device in devices:
            try:
                response = device.send_message(
                    Message(
                        data=fb_body,
                        notification=FB_Notification(
                            title=str(title),
                            body=str(fb_body['text']),
                        )
                    )
                )
                print('Notification sent:', response)
            except Exception as device_error:
                print(f'Device send error ({device.id}):', device_error)
                
    except ValueError as e:
        print('Firebase init error:', e)
    except Exception as e:
        print('Notification error:', e)

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
