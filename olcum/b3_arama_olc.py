"""Bolum 3, olcum A: hangi arama yontemi dogru dokumani buluyor?

Dokumanlar '## ' basliklarindan parcalara bolunur (her parca: dosya + baslik + metin).
24 soru x 4 yontem; olcut: dogru dosya ilk 1 / ilk 3 parcada mi. Model yok, agent yok;
yalnizca arama. Rol filtresi bu olcumde kapali (butun klasorler).
"""
import json
import math
import os
import pathlib
import re
import time

import numpy as np

KOK = pathlib.Path(__file__).resolve().parent.parent / "bolum3"
SORU = json.loads((KOK / "sorular.json").read_text(encoding="utf-8"))["var"]


def kucult(s):
    return s.replace("I", "ı").replace("İ", "i").lower()


def parcala():
    parcalar = []
    for yol in sorted((KOK / "dokumanlar").glob("*/*.md")):
        ad = f"{yol.parent.name}/{yol.name}"
        baslik, bolum = "", None
        for satir in yol.read_text(encoding="utf-8").splitlines():
            if satir.startswith("# "):
                baslik = satir[2:]
            elif satir.startswith("## "):
                bolum = {"dosya": ad, "baslik": f"{baslik} / {satir[3:]}", "metin": ""}
                parcalar.append(bolum)
            elif bolum and satir.strip():
                bolum["metin"] += satir + " "
    return parcalar


P = parcala()
METIN = [f"{p['baslik']}. {p['metin']}" for p in P]


def kelimeler(s):
    return re.findall(r"\w+", kucult(s))


def anahtar(soru, k=3):
    """BM25: soru kelimelerinin parcalarda gecme sikligi (Turkce kok bulma yok)."""
    belgeler = [kelimeler(m) for m in METIN]
    ort = sum(map(len, belgeler)) / len(belgeler)
    puan = []
    for b in belgeler:
        p = 0.0
        for w in set(kelimeler(soru)):
            n = sum(w in d for d in belgeler)
            if not n:
                continue
            idf = math.log(1 + (len(belgeler) - n + 0.5) / (n + 0.5))
            f = b.count(w)
            p += idf * f * 2.2 / (f + 1.2 * (0.25 + 0.75 * len(b) / ort))
        puan.append(p)
    return list(np.argsort(puan)[::-1][:k]), max(puan)


def yerel(model_adi, onek_soru="", onek_belge=""):
    from sentence_transformers import SentenceTransformer
    m = SentenceTransformer(model_adi)
    D = m.encode([onek_belge + t for t in METIN], normalize_embeddings=True)
    return lambda s, k=3: (list(np.argsort(D @ m.encode(onek_soru + s, normalize_embeddings=True))[::-1][:k]), None)


def openai_emb():
    from openai import OpenAI
    c = OpenAI()
    e = lambda xs: np.array([d.embedding for d in c.embeddings.create(
        model="text-embedding-3-small", input=xs).data])
    D = e(METIN)
    D /= np.linalg.norm(D, axis=1, keepdims=True)
    def ara(s, k=3):
        q = e([s])[0]
        return list(np.argsort(D @ (q / np.linalg.norm(q)))[::-1][:k]), None
    return ara


YONTEM = {
    "anahtar_kelime": lambda: anahtar,
    "minilm_ingilizce": lambda: yerel("sentence-transformers/all-MiniLM-L6-v2"),
    "e5_cok_dilli": lambda: yerel("intfloat/multilingual-e5-large-instruct",
                                  "Instruct: Şirket dokümanında bu sorunun cevabını bul\nQuery: "),
    "openai_small": openai_emb,
}

print(f"{len(P)} parca, {len(SORU)} soru")
sonuc = {}
for ad, kur in YONTEM.items():
    ara = kur()
    satir = []
    for s in SORU:
        t = time.time()
        idx, _ = ara(s["soru"])
        dosyalar = [P[i]["dosya"] for i in idx]
        satir.append({"id": s["id"], "tur": s["tur"], "ilk1": int(dosyalar[0] == s["dosya"]),
                      "ilk3": int(s["dosya"] in dosyalar), "bulunan": dosyalar[0],
                      "ms": round((time.time() - t) * 1000)})
    sonuc[ad] = satir
    f = lambda tur, k: sum(x[k] for x in satir if tur in (None, x["tur"]))
    n = lambda tur: sum(1 for x in satir if tur in (None, x["tur"]))
    print(f"{ad:18} ilk1 {f(None,'ilk1')}/{n(None)}  ilk3 {f(None,'ilk3')}/{n(None)}  | "
          f"ayni kelime ilk1 {f('ayni','ilk1')}/{n('ayni')}  farkli kelime ilk1 {f('farkli','ilk1')}/{n('farkli')}")
json.dump(sonuc, open(pathlib.Path(__file__).with_name("b3_arama.json"), "w"), ensure_ascii=False, indent=1)
