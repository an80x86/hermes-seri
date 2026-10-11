"""Takvim araci: baslangic tarihine is gunu ekler (MCP sunucusu).

Hafta sonlarini ve 2026 resmi tatillerini atlar. Hermes bu sunucuya HTTP ile
baglanir; her cagri /takvim/cagri.log dosyasina yazilir.
"""
import datetime as dt
import json
import time

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

# 2026 resmi tatilleri (tam gun). Arife yarim gunleri is gunu sayiliyor.
TATIL = {"2026-01-01", "2026-03-20", "2026-03-21", "2026-03-22", "2026-04-23",
         "2026-05-01", "2026-05-19", "2026-05-27", "2026-05-28", "2026-05-29",
         "2026-05-30", "2026-07-15", "2026-08-30", "2026-10-29", "2027-01-01"}

takvim = MCPServer("takvim")


@takvim.tool()
def is_gunu_ekle(baslangic: str, is_gunu: int) -> str:
    """Baslangic tarihine (YYYY-MM-DD) is gunu ekler. Hafta sonlari ve Turkiye
    resmi tatilleri atlanir. Bugunun tarihi icin 'bugun' yazilabilir."""
    g = dt.date.today() if baslangic == "bugun" else dt.date.fromisoformat(baslangic)
    kalan = is_gunu
    while kalan > 0:
        g += dt.timedelta(days=1)
        if g.weekday() < 5 and g.isoformat() not in TATIL:
            kalan -= 1
    with open("/takvim/cagri.log", "a") as f:
        f.write(json.dumps({"zaman": time.time(), "baslangic": baslangic,
                            "is_gunu": is_gunu, "sonuc": g.isoformat()}) + "\n")
    return g.isoformat()


takvim.run("streamable-http", host="0.0.0.0", port=8000,
           transport_security=TransportSecuritySettings(allowed_hosts=["takvim:8000"]))
