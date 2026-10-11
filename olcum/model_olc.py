"""Hermes uzerinde model karsilastirmasi: ayni 10 soru, ayni araclar (-t sirket).

Her model kendi veri dizininde (~/hermes-seri/<model>) ve kendi is parcaciginda
calisir; sirket MCP sunucusu cagrilari X-Akis basligiyla modele gore kaydeder.
Maliyet ve token Hermes'in --usage-file raporundan okunur.
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
OLCUM = pathlib.Path(__file__).resolve().parent
CAGRI = OLCUM / "sirket" / "cagri.log"
CIKTI = OLCUM / "model_olcum.csv"
MODELLER = ["gpt-4o-mini", "gpt-4.1-nano", "gpt-5-nano", "gpt-5-mini", "gpt-5.6-luna"]
TEKRAR = int(sys.argv[1]) if len(sys.argv) > 1 else 2

SORU = [  # (kimlik, soru, dogru mu?)
    ("Q1_isgunu", "Bugünden 10 iş günü sonrası hangi tarih?",
     lambda c, n: bool(re.search(r"23 Ekim|2026-10-23|23\.10\.2026", c))),
    ("Q2_tatil", "15 Ekim 2026'dan itibaren 12 iş günü sonrası hangi tarih?",
     lambda c, n: bool(re.search(r"3 Kasım|2026-11-03|0?3\.11\.2026", c))),
    ("Q3_dokuman", "Q3 müşteri memnuniyeti hedefimiz nedir?",
     lambda c, n: bool(re.search(r"%\s?90|yüzde 90|90\s?%", c))),
    ("Q4_toplanti", "Haftalık ekip toplantısı ne zaman yapılıyor?",
     lambda c, n: "Pazartesi" in c and "10:00" in c),
    ("Q5_stok", "HP-250 stokta kaç adet var?",
     lambda c, n: bool(re.search(r"\b240\b", c))),
    ("Q6_cikarim", "VLV-12'den 1500 adet sipariş gelse stok yeter mi?",
     lambda c, n: bool(re.search(r"1\.?200", c)) and bool(
         re.search(r"\b300\b|yetmez|yetersiz|yeterli değil|karşılamıyor|karşılamaz|yeterli olmaz", c))),
    ("Q7_aracsiz", "Merhaba, kendini tek cümleyle tanıt.",
     lambda c, n: n == 0 and len(c) > 0),
    ("Q8_iki_arac", "HP-400 stoğu kaç adet ve bugünden 5 iş günü sonrası hangi tarih?",
     lambda c, n: bool(re.search(r"\b85\b", c)) and bool(re.search(r"16 Ekim|2026-10-16|16\.10\.2026", c))),
    ("Q9_uydurma", "Yıllık izin hakkımız kaç gün?",
     lambda c, n: not re.search(r"\b\d+\s*(iş\s*)?gün", c)),
    ("Q10_masraf", "Masraf formunu en geç ne zaman teslim etmeliyim?",
     lambda c, n: bool(re.search(r"10 iş gün", c))),
]
GURULTU = ("[", "/package", "s6-rc", "cont-init", "reconcile", "Syncing", "Done:")


def dizin_hazirla(model):
    d = EV / model
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(EV / "taban", d, ignore=shutil.ignore_patterns("state.db*", "usage"))
    (d / "usage").mkdir()
    yol = d / "config.yaml"
    yol.write_text(yol.read_text().replace('"AKIS_ADI"', f'"{model}"'))
    return d


def cagri_say(model, bas, bit):
    if not CAGRI.exists():
        return 0, ""
    n, araclar = 0, []
    for s in CAGRI.read_text().splitlines():
        k = json.loads(s)
        if k["akis"] == model and bas <= k["zaman"] <= bit:
            n += 1
            araclar.append(k["arac"])
    return n, "+".join(araclar)


def calistir(model, d, kimlik, soru, t):
    usage = f"/opt/data/usage/{kimlik}_{t}.json"
    bas = time.time()
    c = subprocess.run(["docker", "run", "--rm", "--network", "hermes-net", "-v",
                        f"{d}:/opt/data", "-w", "/opt/data/calisma",
                        "nousresearch/hermes-agent", "-z", soru, "-m", model,
                        "--provider", "openai-api", "-t", "sirket", "--usage-file", usage],
                       capture_output=True, text=True, timeout=400)
    bit = time.time()
    cevap = " ".join(s for s in c.stdout.splitlines()
                     if s.strip() and not s.startswith(GURULTU))
    u = {}
    yol = d / "usage" / f"{kimlik}_{t}.json"
    if yol.exists():
        u = json.loads(yol.read_text())
    n, araclar = cagri_say(model, bas - 1, bit + 1)
    return {"model": model, "soru": kimlik, "tur": t, "cevap": cevap, "arac_sayisi": n,
            "araclar": araclar, "sure": round(bit - bas, 1),
            "maliyet": u.get("total_including_auxiliary", {}).get("estimated_cost_usd", ""),
            "girdi": u.get("input_tokens", ""), "onbellek": u.get("cache_read_tokens", ""),
            "cikti": u.get("output_tokens", ""), "akil": u.get("reasoning_tokens", ""),
            "api": u.get("api_calls", ""), "basarisiz": u.get("failed", "")}


def akis(model):
    d = dizin_hazirla(model)
    sonuc = []
    for t in range(1, TEKRAR + 1):
        for kimlik, soru, dogru in SORU:
            s = calistir(model, d, kimlik, soru, t)
            s["dogru"] = int(dogru(s["cevap"], s["arac_sayisi"]))
            sonuc.append(s)
            print(f"{model:14} {kimlik:12} t{t} dogru={s['dogru']} arac={s['arac_sayisi']} "
                  f"${s['maliyet']} {s['sure']}sn", flush=True)
    return sonuc


with cf.ThreadPoolExecutor(len(MODELLER)) as h:
    hepsi = [s for parca in h.map(akis, MODELLER) for s in parca]

alanlar = ["model", "soru", "tur", "dogru", "arac_sayisi", "araclar", "sure", "maliyet",
           "girdi", "onbellek", "cikti", "akil", "api", "basarisiz", "cevap"]
with CIKTI.open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=alanlar)
    w.writeheader()
    w.writerows(hepsi)
print(f"\nYazildi: {CIKTI}")
