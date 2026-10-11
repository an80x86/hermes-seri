"""Olcum icin sahte Telegram Bot API sunucusu (gercek Telegram'a hic gitmez).

Hermes gateway'in platforms.telegram.extra.base_url'u buraya cevrilir. Gateway'in
gercek Telegram kodu calisir; yalnizca karsisindaki sunucu bu dosyadir.
  POST /_gonder   {"uid": 111, "metin": "..."}  -> kullanicidan mesaj gelmis gibi kuyruga koyar
  GET  /_kayit?sonra=N                         -> botun N'den sonraki tum cagrilari (sira, metot, parametre)
  POST /_sifirla                               -> kuyrugu ve kaydi temizler (her gateway oncesi)
"""
import http.server
import json
import threading
import time
import urllib.parse

KILIT = threading.Condition()
GUNCELLEME, KAYIT = [], []
SAYAC = {"update": 0, "mesaj": 1000}
BOT = {"id": 7000000001, "is_bot": True, "first_name": "Ulak", "username": "sahte_ulak_bot",
       "can_join_groups": False, "can_read_all_group_messages": False,
       "supports_inline_queries": False}


def mesaj(chat_id, metin):
    SAYAC["mesaj"] += 1
    return {"message_id": SAYAC["mesaj"], "date": int(time.time()), "from": BOT, "text": metin,
            "chat": {"id": int(chat_id), "type": "private", "first_name": "Kullanici"}}


class Sunucu(http.server.BaseHTTPRequestHandler):
    def _json(self, veri, kod=200):
        govde = json.dumps(veri, ensure_ascii=False).encode()
        self.send_response(kod)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(govde)))
        self.end_headers()
        self.wfile.write(govde)

    def _parametre(self):
        u = urllib.parse.urlparse(self.path)
        p = {k: v[-1] for k, v in urllib.parse.parse_qs(u.query).items()}
        n = int(self.headers.get("Content-Length", 0))
        govde = self.rfile.read(n) if n else b""
        tur = self.headers.get("Content-Type", "")
        if govde and "json" in tur:
            p.update(json.loads(govde))
        elif govde and "multipart" not in tur:
            p.update({k: v[-1] for k, v in urllib.parse.parse_qs(govde.decode()).items()})
        for k, v in list(p.items()):
            if isinstance(v, str) and v[:1] in "[{":
                try:
                    p[k] = json.loads(v)
                except ValueError:
                    pass
        return u.path, p

    def do_GET(self):
        self.do_POST()

    def do_POST(self):
        yol, p = self._parametre()
        if yol == "/_gonder":
            with KILIT:
                SAYAC["update"] += 1
                uid = int(p["uid"])
                GUNCELLEME.append({"update_id": SAYAC["update"], "message": {
                    "message_id": SAYAC["update"], "date": int(time.time()), "text": p["metin"],
                    "from": {"id": uid, "is_bot": False, "first_name": p.get("ad", "Kullanici")},
                    "chat": {"id": uid, "type": "private", "first_name": p.get("ad", "Kullanici")}}})
                KILIT.notify_all()
            return self._json({"ok": True, "sira": len(KAYIT)})
        if yol == "/_sifirla":
            with KILIT:
                GUNCELLEME.clear()
                KAYIT.clear()
            return self._json({"ok": True})
        if yol == "/_kayit":
            sonra = int(p.get("sonra", 0))
            return self._json(KAYIT[sonra:])
        metot = yol.rsplit("/", 1)[-1]
        if metot == "getUpdates":
            ofset, bekle = int(p.get("offset", 0) or 0), min(float(p.get("timeout", 0) or 0), 10)
            with KILIT:
                KILIT.wait_for(lambda: any(g["update_id"] >= ofset for g in GUNCELLEME), bekle)
                yeni = [g for g in GUNCELLEME if g["update_id"] >= ofset]
            return self._json({"ok": True, "result": yeni})
        with KILIT:
            KAYIT.append({"sira": len(KAYIT), "zaman": time.time(), "metot": metot, "p": p})
        if metot == "getMe":
            sonuc = BOT
        elif metot in ("sendMessage", "editMessageText", "sendMessageDraft"):
            sonuc = mesaj(p.get("chat_id", 0), p.get("text", ""))
            if metot == "editMessageText" and "message_id" in p:
                sonuc["message_id"] = int(p["message_id"])
        elif metot == "getChat":
            sonuc = {"id": int(p.get("chat_id", 0)), "type": "private", "first_name": "Kullanici"}
        elif metot == "getWebhookInfo":
            sonuc = {"url": "", "has_custom_certificate": False, "pending_update_count": 0}
        elif metot in ("getMyCommands", "getUpdates"):
            sonuc = []
        else:
            sonuc = True
        self._json({"ok": True, "result": sonuc})

    def log_message(self, *a):
        pass


http.server.ThreadingHTTPServer(("0.0.0.0", 8090), Sunucu).serve_forever()
