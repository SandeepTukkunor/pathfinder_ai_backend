from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
import random
import string
from django.core.mail import send_mail

class EmailUtils:
    def __init__(self):
        # Email configuration
        self.smtp_server = settings.EMAIL_HOST
        self.smtp_port = settings.EMAIL_PORT
        self.sender_email = settings.EMAIL_HOST_USER
        self.sender_password = settings.EMAIL_HOST_PASSWORD

    def send_verification_email(self, to_email, verification_code):
        # Create a multipart message
        # message = MIMEMultipart()
        # message['From'] = self.sender_email
        # message['To'] = to_email 
        # message['Subject'] = 'Verification Email'

        # Add the verification code to the email body
        body = f'Your verification code is: {verification_code}'
        # message.attach(MIMEText(body, 'plain'))

        # Send the email using Django's send_mail function
        send_mail(
            'Verification Email',
            body,
            self.sender_email,
            [to_email],
            fail_silently=False,
        )
            
    def send_otp(self, to_email):
        # Generate OTP
        otp = ''.join(random.choices(string.digits, k=6))
        # Create a multipart message
        message = MIMEMultipart()
        message['From'] = self.sender_email
        message['To'] = to_email
        message['Subject'] = 'OTP Verification'
        # Add the OTP to the email body
        body = f'Your OTP is: {otp}'
        message.attach(MIMEText(body, 'plain'))
        send_mail(
            'Verification Email',
            body,
            self.sender_email,
            [to_email],
            fail_silently=False,
        )


