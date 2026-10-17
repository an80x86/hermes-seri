"""Temiz Hermes + betikli skill: kisa istegi verir, cagrilari ve raporu yazar."""
import datetime, json, os, pathlib, shutil, sqlite3, subprocess, sys

DENEY = pathlib.Path(os.environ.get("H6_DENEY", "deney"))
HERMES = pathlib.Path.home() / "hermes-seri" / "h6_canli"     # Hermes'in veri klasoru
ISTEK = "sirket.db'deki verilerle bugünün tahsilat raporunu hazırla."

shutil.rmtree(HERMES, ignore_errors=True)
shutil.copytree(HERMES.parent / "h6_taban", HERMES)          # 58 hazir skill + sirket.db
shutil.copytree(DENEY / "skills" / "benim_betik", HERMES / "skills", dirs_exist_ok=True)

print("İstek:", ISTEK)
subprocess.run(["docker", "run", "--rm", "-v", f"{HERMES}:/opt/data", "-w", "/opt/data/calisma",
                "nousresearch/hermes-agent", "-z", ISTEK, "-t", "terminal,file,skills"],
               capture_output=True)

db = sqlite3.connect(HERMES / "state.db")
for (cagrilar,) in db.execute("select tool_calls from messages where tool_calls is not null"):
    for c in json.loads(cagrilar):
        print(f"  araç  {c['function']['name']:<13}{c['function']['arguments'][:62]}")

rapor = next((HERMES / "calisma" / "raporlar").glob("tahsilat_*.md"))
satirlar = rapor.read_text().splitlines()
musteri = sum(s.startswith("| ") for s in satirlar) - 2           # baslik + ayirici
print(f"\n{rapor.name}:  {satirlar[2]}  ·  {musteri} müşteri")

sys.path.insert(0, str(DENEY)); import beklenen                # dogrudan veritabanindan
beklenen.BUGUN = datetime.date.today().isoformat()
b = beklenen.hesapla(DENEY / "sirket.db")
tl = f"{b['toplam']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
print(f"Veritabanı:  {tl} TL  ·  {len(b['musteriler'])} müşteri")
