# notification_service.py
# وظیفه: ارسال پیامک، ایمیل، پوش

def send_sms(to, message):
    print(f"[SMS] To: {to} | Message: {message}")

def send_email(to, subject, body):
    print(f"[EMAIL] To: {to} | Subject: {subject} | Body: {body}") 