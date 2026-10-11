"""OpenAI'ye giden istekleri kaydeden ara sunucu (yalnizca olcum icin).

Hermes'in model.base_url'u buraya cevrilir; her istek govdesi /kayit altina
JSON olarak yazilir, sonra aynen api.openai.com'a iletilir. Authorization
basligi kaydedilmez.
"""
import http.server
import json
import pathlib
import time
import urllib.error
import urllib.request
import uuid

KAYIT = pathlib.Path("/kayit")
HEDEF = "https://api.openai.com"
ATLA = ("host", "content-length", "accept-encoding", "connection")


class Vekil(http.server.BaseHTTPRequestHandler):
    def _ilet(self):
        uzunluk = int(self.headers.get("Content-Length", 0))
        govde = self.rfile.read(uzunluk) if uzunluk else None
        if govde:
            ad = f"{time.time():.3f}_{uuid.uuid4().hex[:6]}"
            (KAYIT / f"{ad}{self.path.replace('/', '_')}.json").write_bytes(govde)
        basliklar = {k: v for k, v in self.headers.items() if k.lower() not in ATLA}
        istek = urllib.request.Request(HEDEF + self.path, data=govde, headers=basliklar,
                                       method=self.command)
        try:
            yanit = urllib.request.urlopen(istek, timeout=300)
        except urllib.error.HTTPError as h:
            yanit = h
        self.send_response(yanit.status)
        for k, v in yanit.headers.items():
            if k.lower() not in ("transfer-encoding", "connection", "content-encoding"):
                self.send_header(k, v)
        self.end_headers()
        while parca := yanit.read1(65536) if hasattr(yanit, "read1") else yanit.read():
            self.wfile.write(parca)
            self.wfile.flush()

    do_GET = do_POST = _ilet

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(("0.0.0.0", 8080), Vekil).serve_forever()
