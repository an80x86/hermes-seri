"""H6 tahsilat raporu: sirket kurallarina gore beklenen degerler (bugun 2026-10-16)."""
import json
import pathlib
import sqlite3

KOK = pathlib.Path(__file__).resolve().parent
BUGUN = "2026-10-16"


def hesapla(db=KOK / "sirket.db"):
    c = sqlite3.connect(db)
    satir = c.execute("""
        select m.unvan, m.temsilci, count(*), round(sum(f.tutar), 2), min(f.vade),
               max(julianday(?) - julianday(f.vade))
        from faturalar f join musteriler m on m.id = f.musteri_id
        where f.odendi = 0 and f.vade < ?
        group by m.id order by sum(f.tutar) desc""", (BUGUN, BUGUN)).fetchall()
    tel = [r[0] for r in c.execute("select telefon from musteriler")]
    vno = [r[0] for r in c.execute("select vergi_no from musteriler")]
    return {"musteriler": [{"unvan": u, "temsilci": t, "adet": n, "tutar": s, "en_eski": e,
                            "acil": g > 60} for u, t, n, s, e, g in satir],
            "toplam": round(sum(r[3] for r in satir), 2), "telefonlar": tel, "vergi_no": vno}


if __name__ == "__main__":
    b = hesapla()
    print(len(b["musteriler"]), "musteri, toplam", b["toplam"], ", acil",
          sum(m["acil"] for m in b["musteriler"]))
    print(json.dumps(b["musteriler"][:3], ensure_ascii=False))
