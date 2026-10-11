"""Bolum 2, olcum A: tarih sorulari araçsiz / varsayilan araclarla / takvim araciyla.

Her kosul kendi veri dizininde (~/hermes-seri/b2_<kosul>) ve kendi is
parcaciginda. Takvim cagrilari ~/hermes-seri/takvim/cagri.log'dan sayilir;
takvim yalnizca 'takvim' kosulunda acik oldugu icin karisma yok.
Bugun = 2026-10-10 Cumartesi; 29 Ekim resmi tatil.
"""
import concurrent.futures as cf
import csv
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time

EV = pathlib.Path.home() / "hermes-seri"
CIKTI = pathlib.Path(__file__).resolve().parent / "b2_tarih.csv"
CAGRI = EV / "takvim" / "cagri.log"
G, OK, Y, C = 0.20, 0.02, 0.25, 1.20  # gpt-5.6-luna $/1M
TEKRAR = int(sys.argv[1]) if len(sys.argv) > 1 else 5
GURULTU = ("[", "/package", "s6-rc", "cont-init", "reconcile", "Syncing", "Done:", "  + ")
KOSUL = {"aracsiz": ["-t", "memory"], "varsayilan": [], "takvim": ["-t", "takvim"]}
AY = {"10": "Ekim", "11": "Kasım"}


def kalip(iso):
    y, a, g = iso.split("-")
    return rf"\b0?{int(g)}\s*{AY[a]}|{iso}|\b0?{int(g)}[./]{a}[./]{y}"


SORU = [("Q1_bugun10", "Bugünden 10 iş günü sonrası hangi tarih?", "2026-10-23"),
        ("Q2_tatil12", "15 Ekim 2026'dan itibaren 12 iş günü sonrası hangi tarih?", "2026-11-03"),
        ("Q3_bugun5", "Bugünden 5 iş günü sonrası hangi tarih?", "2026-10-16"),
        ("Q4_tatil3", "27 Ekim 2026'dan itibaren 3 iş günü sonrası hangi tarih?", "2026-11-02"),
        ("Q5_bugun15", "Bugünden 15 iş günü sonrası hangi tarih?", "2026-11-02")]


def maliyet(x):
    return (x["input_tokens"] * G + x["cache_read_tokens"] * OK
            + x["cache_write_tokens"] * Y + x["output_tokens"] * C) / 1e6


def hazirla(kosul):
    d = EV / f"b2_{kosul}"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(EV / "b2taban", d, ignore=shutil.ignore_patterns("state.db*", "usage"))
    (d / "usage").mkdir()
    return d


def takvim_cagrilari(bas, bit):
    if not CAGRI.exists():
        return []
    return [json.loads(s) for s in CAGRI.read_text().splitlines()
            if bas <= json.loads(s)["zaman"] <= bit]


def akis(kosul):
    d = hazirla(kosul)
    satirlar = []
    for t in range(1, TEKRAR + 1):
        for kimlik, soru, dogru in SORU:
            u_ad = f"{kimlik}_{t}.json"
            bas = time.time()
            c = subprocess.run(["docker", "run", "--rm", "--network", "hermes-net", "-v",
                                f"{d}:/opt/data", "-w", "/opt/data/calisma",
                                "nousresearch/hermes-agent", "-z", soru, *KOSUL[kosul],
                                "--usage-file", f"/opt/data/usage/{u_ad}"],
                               capture_output=True, text=True, timeout=400)
            bit = time.time()
            cevap = " ".join(s for s in c.stdout.splitlines()
                             if s.strip() and not s.startswith(GURULTU))
            u = json.loads((d / "usage" / u_ad).read_text())
            tk = takvim_cagrilari(bas - 1, bit + 1) if kosul == "takvim" else []
            s = {"kosul": kosul, "soru": kimlik, "tur": t, "beklenen": dogru,
                 "dogru": int(bool(re.search(kalip(dogru), cevap))),
                 "api": u["api_calls"], "takvim_cagri": len(tk),
                 "takvim_girdi": "; ".join(f"{x['baslangic']}+{x['is_gunu']}" for x in tk),
                 "sure": round(bit - bas, 1),
                 "maliyet": round(maliyet(u) + maliyet(u["auxiliary"]), 6), "cevap": cevap}
            satirlar.append(s)
            print(f"{kosul:10} {kimlik:11} t{t} dogru={s['dogru']} api={s['api']} "
                  f"takvim={s['takvim_cagri']} ${s['maliyet']}", flush=True)
    return satirlar


with cf.ThreadPoolExecutor(len(KOSUL)) as h:
    hepsi = [s for parca in h.map(akis, KOSUL) for s in parca]
with CIKTI.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(hepsi[0]))
    w.writeheader()
    w.writerows(hepsi)
print(f"\nYazildi: {CIKTI}")
