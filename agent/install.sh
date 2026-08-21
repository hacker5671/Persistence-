#!/data/data/com.termux/files/usr/bin/bash
pkg update -y
pkg install python python-pip tesseract openssl termux-api -y
pip install -r requirements.txt
echo "Edit config.json with your server IP and token."
echo "Then run: python agent.py"