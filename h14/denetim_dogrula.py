"""H14: zincirli denetim kaydini dogrula; sonra bir kopyada tek satiri degistirip yakalaniyor mu bak.

  python3 denetim_dogrula.py               # denetim_b.jsonl
  python3 denetim_dogrula.py --kurcala     # kopyada 1 satiri degistir, 1 satiri sil; ikisi de yakalanmali
"""
import hashlib
import json
import pathlib
import sys

KOK = pathlib.Path(__file__).resolve().parent


def dogrula(satirlar: list[str]) -> list[int]:
    """Bozuk satirlarin 1 tabanli numaralari (ilk kirilma yeter, sonrasini da listeler)."""
    bozuk, onceki = [], "0" * 64
    for i, s in enumerate(satirlar, 1):
        k = json.loads(s)
        h = k.pop("hash")
        govde = json.dumps(k, ensure_ascii=False, sort_keys=True)
        if k["onceki"] != onceki or hashlib.sha256(govde.encode()).hexdigest() != h:
            bozuk.append(i)
        onceki = h
    return bozuk


if __name__ == "__main__":
    satirlar = (KOK / "denetim_b.jsonl").read_text().strip().splitlines()
    print(f"denetim_b.jsonl: {len(satirlar)} satır, bozuk: {dogrula(satirlar) or 'yok'}")
    if "--kurcala" in sys.argv:
        hedef = next(i for i, s in enumerate(satirlar) if '"karar": "ret"' in s)
        k = json.loads(satirlar[hedef])
        k["karar"], k["kural"] = "izin", "R3 grup sahibi"     # ret kaydini izin gibi gosterme
        degisik = satirlar[:hedef] + [json.dumps(k, ensure_ascii=False)] + satirlar[hedef + 1:]
        b = dogrula(degisik)
        print(f"{hedef + 1}. satır (ret → izin) değiştirildi: ilk bozuk satır {b[0] if b else 'YOK'}")
        silinmis = satirlar[:hedef] + satirlar[hedef + 1:]
        b = dogrula(silinmis)
        print(f"{hedef + 1}. satır silindi: ilk bozuk satır {b[0] if b else 'YOK'}")
