from django.conf import settings
from urllib import response
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.utils.html import strip_tags

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

