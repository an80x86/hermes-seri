"""Model karsilastirmasi icin sirket araclari: is gunu, dokuman arama, stok.

Her cagri, istegi yapan akisin adiyla (X-Akis basligi) kaydedilir; boylece
hangi modelin hangi araci cagirdigi sonradan sayilabilir.
"""
import csv
import datetime as dt
import json
import pathlib
import time

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.transport_security import TransportSecuritySettings

VERI = pathlib.Path("/sirket")
# 2026 resmi tatilleri (tam gun). Arife yarim gunleri sayilmiyor.
TATIL = {"2026-01-01", "2026-03-20", "2026-03-21", "2026-03-22", "2026-04-23",
         "2026-05-01", "2026-05-19", "2026-05-27", "2026-05-28", "2026-05-29",
         "2026-05-30", "2026-07-15", "2026-08-30", "2026-10-29", "2027-01-01"}

sirket = MCPServer("sirket")


def iz(arac, ctx, **arg):
    akis = (ctx.headers or {}).get("x-akis", "?")
    with open(VERI / "cagri.log", "a") as f:
        f.write(json.dumps({"zaman": time.time(), "akis": akis, "arac": arac, **arg},
                           ensure_ascii=False) + "\n")


@sirket.tool()
def is_gunu_ekle(baslangic: str, is_gunu: int, ctx: Context) -> str:
    """Baslangic tarihine (YYYY-MM-DD) is gunu ekler. Hafta sonlari ve Turkiye
    resmi tatilleri atlanir. Bugunun tarihi icin 'bugun' yazilabilir."""
    iz("is_gunu_ekle", ctx, baslangic=baslangic, is_gunu=is_gunu)
    g = dt.date.today() if baslangic == "bugun" else dt.date.fromisoformat(baslangic)
    kalan = is_gunu
    while kalan > 0:
        g += dt.timedelta(days=1)
        if g.weekday() < 5 and g.isoformat() not in TATIL:
            kalan -= 1
    return g.isoformat()


@sirket.tool()
def dokuman_ara(sorgu: str, ctx: Context) -> str:
    """Sirket dokumanlarinda arar; eslesen satirlari dosya adiyla dondurur."""
    iz("dokuman_ara", ctx, sorgu=sorgu)
    kelimeler = [k for k in sorgu.lower().split() if len(k) > 2]
    bulunan = []
    for d in sorted((VERI / "dokumanlar").glob("*.md")):
        for satir in d.read_text(encoding="utf-8").splitlines():
            if any(k in satir.lower() for k in kelimeler):
                bulunan.append(f"{d.name}: {satir.strip()}")
    return "\n".join(bulunan) or "Eslesen dokuman yok."


@sirket.tool()
def stok_sorgula(urun_kodu: str, ctx: Context) -> str:
    """Urun koduna gore stok adedini dondurur."""
    iz("stok_sorgula", ctx, urun_kodu=urun_kodu)
    with open(VERI / "stok.csv") as f:
        for s in csv.DictReader(f):
            if s["urun_kodu"].lower() == urun_kodu.lower():
                return f"{s['urun_kodu']} ({s['urun_adi']}): {s['stok']} adet"
    return "Urun bulunamadi."


sirket.run("streamable-http", host="0.0.0.0", port=8000,
           transport_security=TransportSecuritySettings(allowed_hosts=["sirket:8000"]))
