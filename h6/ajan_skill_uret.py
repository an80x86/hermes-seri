"""Ajanin kendi skill'i: kurallar bir kez anlatilir, is yapilir, 'skill olarak kaydet' denir.
Uc bagimsiz deneme (ajan1..3); olusan skill skills/ajanN/ altina kopyalanir."""
import concurrent.futures as cf
import json
import pathlib
import shutil
import subprocess

from kontrol import kontrol

KOK = pathlib.Path(__file__).resolve().parent
EV = pathlib.Path.home() / "hermes-seri"
KURAL = (KOK / "kurallar.md").read_text(encoding="utf-8").strip()
ISTEM = ("sirket.db'deki verilerle bugünün tahsilat raporunu hazırla.\n\n" + KURAL +
         "\n\nRaporu hazırladıktan sonra bu işi bir skill olarak kaydet; bundan sonra sadece "
         "\"tahsilat raporunu hazırla\" dediğimde aynı kurallarla yapabilmelisin.")
BUNDLED = {p.parent.relative_to(EV / "h6_taban" / "skills") for p in (EV / "h6_taban" / "skills").rglob("SKILL.md")}


def uret(n):
    d = EV / f"h6_uret_ajan{n}"
    if d.exists():
        raise SystemExit(f"{d} zaten var")
    shutil.copytree(EV / "h6_taban", d)
    c = subprocess.run(["docker", "run", "--rm", "-v", f"{d}:/opt/data", "-w", "/opt/data/calisma",
                        "nousresearch/hermes-agent", "-z", ISTEM, "-t", "terminal,file,skills",
                        "--usage-file", "/opt/data/usage/uret.json"], capture_output=True, text=True, timeout=900)
    yeni = [p.parent for p in (d / "skills").rglob("SKILL.md")
            if p.parent.relative_to(d / "skills") not in BUNDLED]
    hedef = KOK / "skills" / f"ajan{n}"
    for y in yeni:
        shutil.copytree(y, hedef / y.relative_to(d / "skills"))
    u = json.loads((d / "usage" / "uret.json").read_text())
    puan, yol = kontrol(d / "calisma")
    return {"n": n, "skill": [str(y.relative_to(d / "skills")) for y in yeni], "maliyet": u["estimated_cost_usd"],
            "token": u["total_tokens"], "puan": puan, "cevap": c.stdout[-1500:]}


if __name__ == "__main__":
    with cf.ThreadPoolExecutor(3) as h:
        r = list(h.map(uret, [1, 2, 3]))
    (KOK / "ajan_uretim.json").write_text(json.dumps(r, ensure_ascii=False, indent=1))
    for x in r:
        print(x["n"], x["skill"], round(x["maliyet"], 4), sum(x["puan"].values()), "/8")
