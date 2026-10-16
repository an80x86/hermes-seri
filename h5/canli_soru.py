"""Hermes'e erp sunucusunu baglayip tek soru sorar; sunucunun gordugu arac cagrilarini canli yazar.

Hermes'in config.yaml dosyasina eklenen uc satir (iyi duzen, port 8013):
  mcp_servers:
    erp:
      url: http://host.docker.internal:8013/mcp
"""
import json
import os
import pathlib
import subprocess
import time

HERMES = pathlib.Path.home() / "hermes-seri" / "h5_iyi"      # Hermes'in veri klasoru
LOG = pathlib.Path(os.environ.get("ERP_VERI", ".")) / "cagri_iyi.log"
SORU = "Kaya İnşaat'ın açık bakiyesi ne kadar?"

komut = ["docker", "run", "--rm", "-v", f"{HERMES}:/opt/data", "-w", "/opt/data/calisma",
         "nousresearch/hermes-agent", "-z", SORU,
         "-t", "erp"]                 # yalnizca erp araclari: terminal yok, dosya yok
bas = time.time()
hermes = subprocess.Popen(komut, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
print("Soru:", SORU)

gorulen = 0
while hermes.poll() is None:
    time.sleep(0.5)
    cagrilar = [c for c in map(json.loads, LOG.read_text().splitlines()) if c["zaman"] > bas]
    for c in cagrilar[gorulen:]:
        print(f"  arac  {c['arac']}({c['girdi']})")
        print(f"    ->  {c['cikti'][:88]}")
    gorulen = len(cagrilar)

GURULTU = ("[", "s6-rc", "cont-init", "reconcile", "Syncing", "Done:")
cevap = [s for s in hermes.stdout.read().splitlines() if s.strip() and not s.startswith(GURULTU)]
print("Cevap:", *cevap, sep="\n  ")
