import json
from http.server import HTTPServer
from http.server import SimpleHTTPRequestHandler
from threading import Thread

from . import page


class ApplicationServer(HTTPServer):
    class RequestHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            try:
                _, response = self.server.app.url(self.path)
            except page.Error404:
                self.send_response(404)
                self.send_header(
                    'Content-Type', 'application/x-json',
                )
                self.end_headers()
                return self.wfile.write(json.dumps({
                    "ok": False,
                    "status": 404,
                }).encode())
            else:
                self.send_response(200)
                self.send_header(
                    'Content-Type', 'application/x-json',
                )
                self.end_headers()
                return self.wfile.write(json.dumps(response or {
                    "ok": True,
                    "status": 200,
                }).encode())


    def __init__(self, app, address):
        self.app = app
        super().__init__(address, self.RequestHandler)

    def thread_serve(self):
        self.thread = Thread(
            target=self.serve_forever,
        )
        self.thread.setDaemon(True)
        self.thread.start()
        # self.app.on_close(self.thread.kill)
        return self.thread
