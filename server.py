import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import os

ADMIN_PASSWORD = '0RowwUKM'
DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'announcements.json')
INDEX_FILE = os.path.join(os.path.dirname(__file__), 'index.html')


def load_announcements():
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []


def save_announcements(items):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=True, indent=2)


class Handler(BaseHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path, content_type):
        with open(path, 'rb') as f:
            data = f.read()
        self.send_response(200)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        if self.path == '/api/announcements':
            self._send_json(200, load_announcements())
            return

        if self.path == '/' or self.path == '/index.html':
            self._serve_file(INDEX_FILE, 'text/html; charset=utf-8')
            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):
        if self.path == '/api/announcements':
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                payload = {}

            if payload.get('password') != ADMIN_PASSWORD:
                self._send_json(401, {'error': 'Unauthorized'})
                return

            title = str(payload.get('title', '')).strip()
            body_text = str(payload.get('body', '')).strip()
            if not title or not body_text:
                self._send_json(400, {'error': 'Missing title or body'})
                return

            data = load_announcements()
            data.append({
                'title': title,
                'body': body_text,
                'author': 'Admin',
                'date': __import__('datetime').datetime.now().strftime('%b %d, %Y')
            })
            save_announcements(data)
            self._send_json(200, data)
            return

        self.send_response(404)
        self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/api/announcements/'):
            length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(length)
            try:
                payload = json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                payload = {}

            if payload.get('password') != ADMIN_PASSWORD:
                self._send_json(401, {'error': 'Unauthorized'})
                return

            try:
                index = int(self.path.split('/')[-1])
            except ValueError:
                self._send_json(404, {'error': 'Announcement not found'})
                return

            data = load_announcements()
            if index < 0 or index >= len(data):
                self._send_json(404, {'error': 'Announcement not found'})
                return

            data.pop(index)
            save_announcements(data)
            self._send_json(200, data)
            return

        self.send_response(404)
        self.end_headers()


if __name__ == '__main__':
    server = ThreadingHTTPServer(('0.0.0.0', 3000), Handler)
    print('Server running on http://localhost:3000')
    server.serve_forever()
