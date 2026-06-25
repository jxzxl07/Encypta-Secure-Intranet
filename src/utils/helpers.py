import json
import re
import socket

from PyQt5.QtWidgets import QMessageBox
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from ..config import SERVER_IP, STATUS_SERVER_PORT

def Validate_Password(password):
    if len(password) < 8:
        return False
    has_upper = any(char.isupper() for char in password)
    has_lower = any(char.islower() for char in password)
    has_number = any(char.isdigit() for char in password)
    if not has_upper or not has_lower:
        return False
    if not has_number:
        return False
    return True 

def Validate_Email(email):
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(email_pattern, email):
        return True
    else:
        return False
    


def get_ip_address():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except OSError:
        return "127.0.0.1"



def send_status_update(username, status_type, ip_address):
    # Send status update to admin server via sockets
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((SERVER_IP, STATUS_SERVER_PORT))
        # JSON message and sending it
        message = {
            'type': status_type,
            'username': username,
            'ip': ip_address
        }
        client_socket.send(json.dumps(message).encode())
        client_socket.close()
        return True
    # If server is not running, proceed to log in with an info box    
    except (socket.timeout, ConnectionRefusedError):
        QMessageBox.information(None, "Info", "Admin server is not running. Proceeding without sending status update.")
        return False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return False
