# -*- coding: utf-8 -*-


# ui/server.py
import http.server
import socketserver
import requests
import os
import sys
from http import HTTPStatus

PORT = 3000
BACKEND = "http://127.0.0.1:8000"  # uvicorn backend
HERE = os.path.dirname(__file__)
INDEX = os.path.join(HERE, "index.html")
LOG_PATH = os.path.abspath(os.path.join(HERE, "..", "logs", "service.log"))

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Serve /api/logs specially
        if self.path.startswith("/api/logs"):
            return self.serve_logs()
        # Proxy API calls starting with /api/
        if self.path.startswith("/api/"):
            return self.proxy_request()
        # Serve static UI file(s) from ui/ dir
        if self.path == "/" or self.path == "/index.html":
            self.path = "/index.html"
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

    def do_POST(self):
        if self.path.startswith("/api/"):
            return self.proxy_request()
        # No other POST endpoints — 404
        self.send_response(HTTPStatus.NOT_FOUND)
        self.end_headers()
        self.wfile.write(b"Not found")

    def proxy_request(self):
        # Forward request to backend
        backend_path = self.path[len("/api"):]  # keep leading slash
        url = BACKEND + backend_path
        method = self.command
        headers = {k: v for k, v in self.headers.items() if k.lower() != 'host'}

        length = int(self.headers.get('Content-Length', 0))
        data = self.rfile.read(length) if length > 0 else None

        try:
            resp = requests.request(method, url, headers=headers, data=data, timeout=12)
        except requests.exceptions.RequestException as e:
            self.send_response(502)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))
            return

        self.send_response(resp.status_code)
        excluded = ['Content-Encoding', 'Transfer-Encoding', 'Content-Length', 'Connection']
        for k, v in resp.headers.items():
            if k not in excluded:
                self.send_header(k, v)
        self.send_header('Content-Type', resp.headers.get('Content-Type', 'application/json'))
        self.end_headers()
        self.wfile.write(resp.content)

    def serve_logs(self):
        if not os.path.exists(LOG_PATH):
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(b'') 
            return
        try:
            # Send plain text contents
            with open(LOG_PATH, 'rb') as f:
                data = f.read()
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode('utf-8'))


if __name__ == "__main__":
    os.chdir(HERE)
    if not os.path.exists(INDEX):
        print("index.html not found in ui/ directory.", file=sys.stderr)
        sys.exit(1)
    try:
        with socketserver.ThreadingTCPServer(("", PORT), ProxyHandler) as httpd:
            print(f"Serving UI at http://127.0.0.1:{PORT} (proxying /api/* -> {BACKEND})")
            httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down.")