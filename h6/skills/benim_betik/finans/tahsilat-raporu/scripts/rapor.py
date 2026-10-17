"""Tahsilat raporu: python3 rapor.py [sirket.db] -> raporlar/tahsilat_<bugun>.md"""
import datetime
import pathlib
import sqlite3
import sys

db = sys.argv[1] if len(sys.argv) > 1 else "sirket.db"
bugun = datetime.date.today()


def tl(x):
    return f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " TL"


satirlar = sqlite3.connect(db).execute("""
    select m.unvan, m.temsilci, count(*), sum(f.tutar), min(f.vade)
    from faturalar f join musteriler m on m.id = f.musteri_id
    where f.odendi = 0 and f.vade < ?
    group by m.id order by sum(f.tutar) desc""", (bugun.isoformat(),)).fetchall()
toplam = sum(r[3] for r in satirlar)
md = [f"# Tahsilat Raporu — {bugun.isoformat()}", "", f"Toplam gecikmiş alacak: {tl(toplam)}", "",
      "| Müşteri | Temsilci | Fatura | Gecikmiş tutar | En eski vade |", "| --- | --- | --- | --- | --- |"]
for unvan, temsilci, adet, tutar, en_eski in satirlar:
    gun = (bugun - datetime.date.fromisoformat(en_eski)).days
    ad = f"[ACİL] {unvan}" if gun > 60 else unvan
    md.append(f"| {ad} | {temsilci} | {adet} | {tl(tutar)} | {en_eski} |")
yol = pathlib.Path("raporlar") / f"tahsilat_{bugun.isoformat()}.md"
yol.parent.mkdir(exist_ok=True)
yol.write_text("\n".join(md) + "\n", encoding="utf-8")
print(f"{yol}: {len(satirlar)} müşteri, toplam {tl(toplam)}")
