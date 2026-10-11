"""Dokuman araci: role gore filtrelenmis anlamsal arama (MCP sunucusu).

Rol, istegin X-Jeton basligindan gelir; agent'in ne dedigine bakilmaz.
Embedding modeli yerelde calisir; dokumanlar arama icin disari gonderilmez.
"""
import json
import pathlib
import time

from mcp.server.mcpserver import Context, MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from sentence_transformers import SentenceTransformer

KOK = pathlib.Path(__file__).resolve().parent / "dokumanlar"
JETON = {"satis-41b7": "satis", "ik-9c2e": "ik", "yonetim-d05a": "yonetim"}
KLASOR = {"satis": {"ortak", "satis"}, "ik": {"ortak", "ik"},
          "yonetim": {"ortak", "satis", "ik", "yonetim"}}
SORU_ONEKI = "Instruct: Şirket dokümanında bu sorunun cevabını bul\nQuery: "

model = SentenceTransformer("intfloat/multilingual-e5-large-instruct")
parcalar = []
for yol in sorted(KOK.glob("*/*.md")):
    baslik = ""
    for satir in yol.read_text(encoding="utf-8").splitlines():
        if satir.startswith("# "):
            baslik = satir[2:]
        elif satir.startswith("## "):
            parcalar.append({"klasor": yol.parent.name, "kaynak": f"{yol.parent.name}/{yol.name}",
                             "bolum": f"{baslik} / {satir[3:]}", "metin": ""})
        elif parcalar and satir.strip():
            parcalar[-1]["metin"] += satir + " "
vektor = model.encode([f"{p['bolum']}. {p['metin']}" for p in parcalar],
                      normalize_embeddings=True)

dokuman = MCPServer("dokuman")


def rol_bul(ctx: Context) -> str | None:
    return JETON.get((ctx.headers or {}).get("x-jeton", ""))


@dokuman.tool()
def dokuman_ara(sorgu: str, ctx: Context) -> str:
    """Sirket dokumanlarinda anlamca en yakin 3 bolumu kaynagiyla dondurur.
    Cevabi yalnizca donen metne dayandir; metinde yoksa bulunamadi de."""
    rol = rol_bul(ctx)
    if rol is None:
        return "Yetkisiz istek."
    puan = vektor @ model.encode(SORU_ONEKI + sorgu, normalize_embeddings=True)
    izinli = [i for i in puan.argsort()[::-1] if parcalar[i]["klasor"] in KLASOR[rol]][:3]
    with open(KOK.parent / "cagri.log", "a") as f:
        f.write(json.dumps({"zaman": time.time(), "rol": rol, "sorgu": sorgu,
                            "kaynaklar": [parcalar[i]["kaynak"] for i in izinli]},
                           ensure_ascii=False) + "\n")
    return "\n\n".join(f"[{parcalar[i]['kaynak']} § {parcalar[i]['bolum']}] "
                       f"{parcalar[i]['metin'].strip()}" for i in izinli)


dokuman.run("streamable-http", host="127.0.0.1", port=8001,
            transport_security=TransportSecuritySettings(
                allowed_hosts=["host.docker.internal:8001"]))
