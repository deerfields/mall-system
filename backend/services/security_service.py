# security_service.py
# وظیفه: مدیریت لاگ امنیتی و اسکن QR

def log_security_event(data):
    print(f"[SECURITY LOG] {data}")

def scan_worker_qr(qr_data):
    print(f"[SECURITY SCAN] QR Data: {qr_data}") 