import json
import os
import shutil
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

DATA_FILE = '/data/progress.json'
VIDEOS_DIR = '/videos'
WATCHED_DIR = '/videos/視聴済'


def load():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return {}


def save(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass  # suppress access logs

    def send_json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/progress':
            params = parse_qs(parsed.query)
            file = params.get('file', [''])[0]
            data = load()
            self.send_json(200, {'time': data.get(file, 0)})
        else:
            self.send_json(404, {'error': 'not found'})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == '/progress':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            file = body.get('file', '')
            time = float(body.get('time', 0))
            data = load()
            if time == 0:
                data.pop(file, None)
            else:
                data[file] = time
            save(data)
            self.send_json(200, {'ok': True})
        elif parsed.path == '/move':
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length))
            file = body.get('file', '')
            if not file or '/' in file or '..' in file:
                self.send_json(400, {'error': 'invalid filename'})
                return
            src = os.path.join(VIDEOS_DIR, file)
            if not os.path.isfile(src):
                self.send_json(404, {'error': 'file not found'})
                return
            os.makedirs(WATCHED_DIR, exist_ok=True)
            shutil.move(src, os.path.join(WATCHED_DIR, file))
            srt = os.path.splitext(file)[0] + '.srt'
            srt_src = os.path.join(VIDEOS_DIR, srt)
            if os.path.isfile(srt_src):
                shutil.move(srt_src, os.path.join(WATCHED_DIR, srt))
            data = load()
            data.pop(file, None)
            save(data)
            self.send_json(200, {'ok': True})
        else:
            self.send_json(404, {'error': 'not found'})


if __name__ == '__main__':
    HTTPServer(('', 8080), Handler).serve_forever()
