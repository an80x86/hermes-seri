"""H6 olcumu: ayni kisa istek, sekiz duzen, her biri TEKRAR kez; her calistirma temiz kopya.

  yok           skill yok, yalnizca kisa istek
  prompt        skill yok, kurallar her seferinde istege yapistirilir
  ajan1..3      ajanin kendi yazdigi skill (ajan_skill_uret.py), dogru klasore kondu
  benim         elle yazilmis SKILL.md (aciklama 57 karakter)
  kotu_aciklama ayni govde, aciklama 146 karakter (istem dizininde 57'de kesilir)
  kotu_ad       kotu_aciklama + belirsiz ad (finans-rapor): istem dizininde "tahsilat" hic gecmez
  benim_betik   elle yazilmis SKILL.md + scripts/rapor.py
  kalabalik_*   dort finans skill'i (tahsilat + satis, kasa, borc tuzaklari); _kotu: aciklamalarin ilk 57
                karakteri ayni (kesik), _iyi: kisa ayirt edici aciklamalar. Hedef: finans-rapor

  python3 olc.py                 # hepsi
  python3 olc.py benim 1         # tek duzen, tek tekrar
"""
import concurrent.futures as cf
import csv
import json
import pathlib
import shutil
import sqlite3
import subprocess
import sys
import time

from kontrol import OLCUTLER, kontrol

KOK = pathlib.Path(__file__).resolve().parent
EV = pathlib.Path.home() / "hermes-seri"
CIKTI = EV / "h6_olc"
ISTEK = "sirket.db'deki verilerle bugünün tahsilat raporunu hazırla."
KURAL = (KOK / "kurallar.md").read_text(encoding="utf-8").strip()
HEPSI = ["yok", "prompt", "ajan1", "ajan2", "ajan3", "benim", "kotu_aciklama", "kotu_ad", "benim_betik", "kalabalik_kotu", "kalabalik_iyi"]
DUZENLER = [sys.argv[1]] if len(sys.argv) > 1 else HEPSI
TEKRAR = int(sys.argv[2]) if len(sys.argv) > 2 else 10
G, OK, Y, C = 0.20, 0.02, 0.25, 1.20          # gpt-5.6-luna $/1M: girdi, onbellek okuma/yazma, cikti (H5 ile ayni)


def calistir(duzen, i):
    d = CIKTI / f"{duzen}_{i}"
    if d.exists():
        shutil.rmtree(d)
    shutil.copytree(EV / "h6_taban", d)
    if (KOK / "skills" / duzen).exists():
        shutil.copytree(KOK / "skills" / duzen, d / "skills", dirs_exist_ok=True)
    istek = ISTEK + ("\n\n" + KURAL if duzen == "prompt" else "")
    bas = time.time()
    c = subprocess.run(["docker", "run", "--rm", "-v", f"{d}:/opt/data", "-w", "/opt/data/calisma",
                        "nousresearch/hermes-agent", "-z", istek, "-t", "terminal,file,skills",
                        "--usage-file", "/opt/data/usage/u.json"], capture_output=True, text=True, timeout=900)
    sure = round(time.time() - bas, 1)
    try:
        u = json.loads((d / "usage" / "u.json").read_text())
        m = sum((x["input_tokens"] * G + x["cache_read_tokens"] * OK + x["cache_write_tokens"] * Y
                 + x["output_tokens"] * C) / 1e6 for x in (u, u.get("auxiliary") or {}) if x)
        tok, sid = u["total_tokens"], u["session_id"]
    except Exception:
        m, tok, sid = None, None, None
    db = sqlite3.connect(d / "state.db")
    araclar = [r[0] for r in db.execute("select tool_name from messages where session_id=? and role='tool' "
                                       "order by id", (sid,))]
    cagrilar = [json.loads(r[0]) for r in db.execute("select tool_calls from messages where session_id=? "
                                                     "and tool_calls is not null order by id", (sid,))]
    sv = [json.loads(t["function"]["arguments"]).get("name", "") for cs in cagrilar for t in cs
          if t["function"]["name"] == "skill_view"]
    puan, yol = kontrol(d / "calisma")
    s = {"duzen": duzen, "tekrar": i, **puan, "puan": sum(puan.values()), "tam": int(sum(puan.values()) == 8),
         "skill_yuklendi": int(any("tahsilat" in x or "finans-rapor" in x for x in sv)), "skill_view": " ".join(sv),
         "arac_sayisi": len(araclar), "araclar": " ".join(araclar), "sure": sure,
         "maliyet": round(m, 6) if m else None, "token": tok, "rapor_yolu": yol or "",
         "cevap": "\n".join(x for x in c.stdout.splitlines() if x.strip() and not x.startswith(
             ("[", "/package", "s6-rc", "cont-init", "reconcile", "Syncing", "Done:")))}
    print(f"{duzen:14} {i:2} puan={s['puan']}/8 skill={s['skill_yuklendi']} arac={len(araclar)} "
          f"{sure}s ${s['maliyet']}", flush=True)
    return s


if __name__ == "__main__":
    isler = [(d, i) for i in range(1, TEKRAR + 1) for d in DUZENLER]
    with cf.ThreadPoolExecutor(8) as h:
        hepsi = list(h.map(lambda a: calistir(*a), isler))
    ad = "olcum.csv" if len(sys.argv) == 1 else f"olcum_{'_'.join(sys.argv[1:])}.csv"
    with open(KOK / ad, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(hepsi[0]))
        w.writeheader(); w.writerows(hepsi)
    print(f"\nYazildi: {ad}")
