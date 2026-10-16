"""ERP sunucusunun ortak is mantigi: musteri arama, bakiye, fatura listesi, cagri kaydi.

erp_sunucu.py dort duzende de ayni fonksiyonlari cagirir; duzenler arasindaki fark
yalnizca agent'a hangi araclarin, hangi parametre ve aciklamalarla acildigidir.
Her duzen veritabaninin kendi kopyasini kullanir (sirket_<duzen>.db); her cagri
cagri_<duzen>.log dosyasina yazilir. Klasor ERP_VERI ile degistirilebilir.
"""
import json
import os
import pathlib
import shutil
import sqlite3
import time

KOK = pathlib.Path(os.environ.get("ERP_VERI", pathlib.Path(__file__).resolve().parent))
BUGUN = "2026-10-16"
TR = str.maketrans("İIŞĞÜÖÇ", "iışğüöç")
DUZEN = DB = LOG = None


def ayarla(duzen):
    global DUZEN, DB, LOG
    DUZEN, DB, LOG = duzen, KOK / f"sirket_{duzen}.db", KOK / f"cagri_{duzen}.log"
    if not DB.exists():
        shutil.copy(KOK / "sirket.db", DB)


def kucuk(s):
    return (s or "").translate(TR).lower().strip()


def baglan():
    if DUZEN == "sql_ro":
        return sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    return sqlite3.connect(DB)


def kaydet(arac, girdi, cikti):
    with open(LOG, "a") as f:
        f.write(json.dumps({"zaman": time.time(), "arac": arac, "girdi": girdi,
                            "cikti": cikti[:400]}, ensure_ascii=False) + "\n")
    return cikti


def musteri_ara(ad, sehir):
    db = baglan()
    satir = db.execute("select id, unvan, sehir, temsilci from musteriler").fetchall()
    db.close()
    s = [{"musteri_id": i, "unvan": u, "sehir": sh, "temsilci": t} for i, u, sh, t in satir
         if (not ad or kucuk(ad) in kucuk(u)) and (not sehir or kucuk(sehir) == kucuk(sh))]
    return json.dumps(s, ensure_ascii=False) if s else "Eslesen musteri yok."


def bakiye(musteri_id):
    db = baglan()
    m = db.execute("select unvan from musteriler where id=?", (musteri_id,)).fetchone()
    if not m:
        return "Musteri bulunamadi."
    acik = db.execute("select count(*), coalesce(sum(tutar),0) from faturalar "
                      "where musteri_id=? and odendi=0", (musteri_id,)).fetchone()
    gec = db.execute("select count(*), coalesce(sum(tutar),0), min(vade) from faturalar "
                     "where musteri_id=? and odendi=0 and vade<?", (musteri_id, BUGUN)).fetchone()
    db.close()
    return json.dumps({"unvan": m[0], "acik_fatura_sayisi": acik[0],
                       "acik_bakiye_tl": round(acik[1], 2), "geciken_fatura_sayisi": gec[0],
                       "geciken_tutar_tl": round(gec[1], 2), "en_eski_gecmis_vade": gec[2]},
                      ensure_ascii=False)


def faturalar(musteri_id, durum, baslangic, bitis):
    q, p = "select no, tarih, vade, tutar, odendi from faturalar where musteri_id=?", [musteri_id]
    if durum in ("acik", "odenmemis"):
        q += " and odendi=0"
    elif durum == "odendi":
        q += " and odendi=1"
    elif durum == "geciken":
        q += " and odendi=0 and vade<?"; p.append(BUGUN)
    if baslangic:
        q += " and tarih>=?"; p.append(baslangic)
    if bitis:
        q += " and tarih<=?"; p.append(bitis)
    db = baglan()
    s = [{"no": n, "tarih": t, "vade": v, "tutar_tl": tu, "durum": "odendi" if o else "acik"}
         for n, t, v, tu, o in db.execute(q + " order by tarih", p).fetchall()]
    db.close()
    return json.dumps(s, ensure_ascii=False) if s else "Fatura yok."
