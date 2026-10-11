"""Bolum 1 olcumleri: bir istek OpenAI'ye ne kadar ve ne gonderiyor, ne tutuyor.

Hermes model.base_url'u kayit vekiline (kayit_proxy.py) cevrilmis halde calisir;
her calistirmanin zaman araligindaki istek govdeleri o calistirmaya atanir.
Maliyet = token x resmi fiyat (onbellek yazma dahil).
"""
import csv
import json
import pathlib
import subprocess
import sys
import time

EV = pathlib.Path.home() / "hermes-seri"
D = EV / "b1"
KAYIT = EV / "kayit"
CIKTI = pathlib.Path(__file__).resolve().parent / "b1_olcum.csv"
G, OK, Y, C = 0.20, 0.02, 0.25, 1.20  # gpt-5.6-luna, $/1M token
TEKRAR = int(sys.argv[1]) if len(sys.argv) > 1 else 5
GURULTU = ("[", "/package", "s6-rc", "cont-init", "reconcile", "Syncing", "Done:", "  + ")

DENEY = [  # (kimlik, istem, ek arguman)
    ("merhaba_varsayilan", "Merhaba, kendini tek cümleyle tanıt.", []),
    ("merhaba_daraltilmis", "Merhaba, kendini tek cümleyle tanıt.", ["-t", "memory"]),
    ("dosya_ozet", "Bu klasördeki müşteri dosyasını oku ve iki cümleyle özetle.", []),
    ("komut", "whoami ve hostname komutlarını çalıştır, sonucu yaz.", []),
]


def maliyet(x):
    return (x["input_tokens"] * G + x["cache_read_tokens"] * OK
            + x["cache_write_tokens"] * Y + x["output_tokens"] * C) / 1e6


def calistir(kimlik, istem, ek, t):
    usage = f"/opt/data/usage/{kimlik}_{t}.json"
    time.sleep(2)  # onceki calistirmanin gec gelen istekleri bu pencereye dusmesin
    once = set(KAYIT.glob("*.json"))
    bas = time.time()
    c = subprocess.run(["docker", "run", "--rm", "--network", "hermes-net", "-v",
                        f"{D}:/opt/data", "-w", "/opt/data/calisma",
                        "nousresearch/hermes-agent", "-z", istem, *ek,
                        "--usage-file", usage], capture_output=True, text=True, timeout=400)
    sure = time.time() - bas
    cevap = " ".join(s for s in c.stdout.splitlines()
                     if s.strip() and not s.startswith(GURULTU))
    yeni = sorted(set(KAYIT.glob("*_v1_responses.json")) - once)
    u = json.loads((D / "usage" / f"{kimlik}_{t}.json").read_text())
    a = u["auxiliary"]
    govdeler = sorted((json.loads(p.read_text()) for p in yeni), key=lambda g: -len(g.get("tools", [])))
    musteri_gitti = any("Yilmaz Tekstil" in p.read_text() for p in yeni)
    return {"deney": kimlik, "tur": t, "sure": round(sure, 1),
            "istek_sayisi": len(yeni), "bayt_toplam": sum(p.stat().st_size for p in yeni),
            "en_buyuk_istek_bayt": max((p.stat().st_size for p in yeni), default=0),
            "arac_tanimi": len(govdeler[0].get("tools", [])) if govdeler else 0,
            "girdi": u["input_tokens"], "onbellek_okuma": u["cache_read_tokens"],
            "onbellek_yazma": u["cache_write_tokens"], "cikti": u["output_tokens"],
            "akil": u["reasoning_tokens"], "api": u["api_calls"],
            "maliyet": round(maliyet(u) + maliyet(a), 6),
            "hermes_tahmini": u["total_including_auxiliary"]["estimated_cost_usd"],
            "musteri_verisi_gitti": int(musteri_gitti), "cevap": cevap}


satirlar = []
for t in range(1, TEKRAR + 1):
    for kimlik, istem, ek in DENEY:
        s = calistir(kimlik, istem, ek, t)
        satirlar.append(s)
        print(f"{kimlik:20} t{t} {s['sure']}sn istek={s['istek_sayisi']} {s['bayt_toplam']}B "
              f"arac={s['arac_tanimi']} ${s['maliyet']} veri={s['musteri_verisi_gitti']}", flush=True)
with CIKTI.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(satirlar[0]))
    w.writeheader()
    w.writerows(satirlar)
print(f"\nYazildi: {CIKTI}")
