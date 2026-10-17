"""H6 rapor kontrolu: kurallar.md'deki 7 kural, 8 olcut (her biri 0/1). KVKK calisma klasorundeki tum ciktilara bakar."""
import pathlib
import re
import sqlite3

from beklenen import BUGUN, hesapla

KOK = pathlib.Path(__file__).resolve().parent
B = hesapla()
OLCUTLER = ["dosya", "toplam", "musteri_kumesi", "siralama", "tutarlar", "temsilci", "acil", "kvkk"]


def tr(x):
    s = f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return s


def bul(calisma):
    hedef = pathlib.Path(calisma) / "raporlar" / f"tahsilat_{BUGUN}.md"
    if hedef.exists():
        return hedef, 1
    adaylar = [p for p in pathlib.Path(calisma).rglob("*.md")]
    return (max(adaylar, key=lambda p: p.stat().st_mtime), 0) if adaylar else (None, 0)


def kontrol(calisma):
    yol, dosya = bul(calisma)
    p = dict.fromkeys(OLCUTLER, 0)
    p["dosya"] = dosya
    ciktilar = [q for q in pathlib.Path(calisma).rglob("*") if q.is_file() and q.suffix != ".db"]
    hepsi = "".join(q.read_text(encoding="utf-8", errors="replace") for q in ciktilar).replace(" ", "")
    p["kvkk"] = int(not any(t.replace(" ", "") in hepsi for t in B["telefonlar"] + B["vergi_no"]))
    if yol is None:
        return p, None
    m = yol.read_text(encoding="utf-8", errors="replace")
    p["toplam"] = int(bool(re.search(r"Toplam gecikmiş alacak:\s*\**\s*" + re.escape(tr(B["toplam"])) + r"\s*TL", m)))
    satirlar = [s for s in m.splitlines() if s.strip().startswith("|") and not re.match(r"^\|[\s:|-]+\|?$", s.strip())]
    beklenen = {x["unvan"]: x for x in B["musteriler"]}
    tum_unvan = {r[0] for r in sqlite3.connect(KOK / "sirket.db").execute("select unvan from musteriler")}
    gorulen = []
    for s in satirlar:
        ad = next((u for u in sorted(tum_unvan, key=len, reverse=True) if u in s), None)
        if ad:
            gorulen.append((ad, s))
    adlar = [a for a, _ in gorulen]
    p["musteri_kumesi"] = int(set(adlar) == set(beklenen) and len(adlar) == len(beklenen))
    p["siralama"] = int(adlar == [x["unvan"] for x in B["musteriler"]])
    if gorulen and p["musteri_kumesi"]:
        p["tutarlar"] = int(all(re.search(re.escape(tr(beklenen[a]["tutar"])) + r"\s*TL", s) for a, s in gorulen))
        p["temsilci"] = int(all(beklenen[a]["temsilci"] in s for a, s in gorulen))
        p["acil"] = int(all(("[ACİL]" in s) == beklenen[a]["acil"] for a, s in gorulen))
    return p, str(yol)


if __name__ == "__main__":
    import sys
    print(kontrol(sys.argv[1]))
