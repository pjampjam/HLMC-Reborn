"""Serves only /stats.json (the public server stats) on 127.0.0.1:8101 for the Cloudflare tunnel, readable by holylois.com."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

FILE = Path('/var/lib/holylois-stats/stats.json')


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.split('?')[0] not in ('/stats.json', '/'):
            self.send_error(404); return
        try: body = FILE.read_bytes()
        except OSError: self.send_error(503); return
        self.send_response(200)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'public, max-age=120')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def log_message(self, *args): pass


ThreadingHTTPServer(('127.0.0.1', 8101), Handler).serve_forever()
