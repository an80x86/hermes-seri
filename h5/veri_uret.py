"""H5 ornek sirket veritabani: musteriler + faturalar (SQLite, sabit tohum).

Bugun 2026-10-16 kabul edilir; vadesi gecmis ve odenmemis fatura "gecikmis" sayilir.
Iki isim bilerek cakisiyor (Yildiz, Ozkan): belirsiz soru testi icin.
"""
import datetime as dt
import pathlib
import random
import sqlite3

DB = pathlib.Path(__file__).with_name("sirket.db")
BUGUN = dt.date(2026, 10, 16)
r = random.Random(5)

MUSTERI = [
    ("Kaya İnşaat", "Ankara"), ("Demir Lojistik", "İstanbul"), ("Ege Gıda", "İzmir"),
    ("Anadolu Kimya", "Kocaeli"), ("Marmara Plastik", "Bursa"), ("Toros Enerji", "Mersin"),
    ("Yıldız Makine", "Konya"), ("Yıldız Tekstil", "Denizli"), ("Özkan Mobilya", "Kayseri"),
    ("Özkan Otomotiv", "Bursa"), ("Kuzey Ambalaj", "Samsun"), ("Akdeniz Tarım", "Antalya"),
    ("Bora Elektrik", "İzmir"), ("Çınar Kağıt", "İstanbul"), ("Defne Kozmetik", "Hatay"),
    ("Ekin Un", "Konya"), ("Fırat Çimento", "Elazığ"), ("Gökay Metal", "Bursa"),
    ("Hisar Cam", "Kırklareli"), ("Işık Medikal", "Ankara"), ("Kartal Boya", "İstanbul"),
    ("Lale Tekstil", "Bursa"), ("Meltem Turizm", "Muğla"), ("Nehir Su", "Sakarya"),
    ("Orkide Gıda", "İzmir"), ("Pınar Ambalaj", "Gaziantep"), ("Rota Nakliyat", "Kocaeli"),
    ("Saray Halı", "Gaziantep"), ("Tunç Döküm", "Eskişehir"), ("Umut Yazılım", "Ankara"),
    ("Vadi Seramik", "Kütahya"), ("Zirve Mimarlık", "İstanbul"), ("Atlas Kauçuk", "Tekirdağ"),
    ("Berk Elektronik", "İzmir"), ("Cevher Madencilik", "Sivas"), ("Doruk Plastik", "Adana"),
    ("Erciyes Gıda", "Kayseri"), ("Filiz Tohum", "Adana"), ("Güneş Enerji", "Konya"),
    ("Hazar Petrol", "Trabzon")]
TEMSILCI = ["Selin Aydın", "Murat Koç", "Elif Şahin", "Can Yılmaz"]


def uret():
    if DB.exists():
        DB.unlink()
    db = sqlite3.connect(DB)
    db.executescript("""
        create table musteriler (id integer primary key, unvan text, sehir text,
            vergi_no text, telefon text, temsilci text);
        create table faturalar (no text primary key, musteri_id integer, tarih text,
            vade text, tutar real, odendi integer);
    """)
    for i, (unvan, sehir) in enumerate(MUSTERI, 1):
        db.execute("insert into musteriler values (?,?,?,?,?,?)",
                   (i, unvan, sehir, f"{r.randrange(10**9, 10**10)}",
                    f"0{r.choice([212, 216, 312, 232, 224, 324])} {r.randrange(100, 999)} "
                    f"{r.randrange(10, 99)} {r.randrange(10, 99)}", TEMSILCI[i % 4]))
    sira = 1
    for i in range(1, len(MUSTERI) + 1):
        for _ in range(r.randint(4, 12)):
            tarih = dt.date(2026, 1, 5) + dt.timedelta(days=r.randrange(0, 280))
            vade = tarih + dt.timedelta(days=r.choice([30, 45, 60]))
            tutar = round(r.randrange(8_000, 240_000) + r.choice([0, 0.5, 0.25, 0.75]), 2)
            # eski faturalarin cogu odenmis, yenilerin cogu acik
            odendi = int(r.random() < (0.9 if vade < BUGUN - dt.timedelta(days=60) else 0.45))
            db.execute("insert into faturalar values (?,?,?,?,?,?)",
                       (f"FTR-2026-{sira:04d}", i, tarih.isoformat(), vade.isoformat(), tutar,
                        odendi))
            sira += 1
    db.commit()
    n = db.execute("select count(*) from faturalar").fetchone()[0]
    print(f"{len(MUSTERI)} musteri, {n} fatura -> {DB.name}")


if __name__ == "__main__":
    uret()
