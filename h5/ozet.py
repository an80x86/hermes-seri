"""olcum.csv + elle_duzeltme.json -> duzen bazinda ozet (sonuc.md tablosu icin)."""
import csv, json, pathlib, statistics as st
KOK = pathlib.Path(__file__).resolve().parent
R = [r for ad in ("veri/olcum.csv", "veri/olcum_sql_ro_2.csv") for r in csv.DictReader(open(KOK / ad))]
E = {k: v for k, v in json.load(open(KOK / "elle_duzeltme.json")).items() if not k.startswith("_")}
for r in R:
    k = f"{r['duzen']}/{r['id']}/{r['tur']}"
    if k in E:
        r["dogru"] = str(E[k][0])
for d in ("sql", "sql_ro", "zayif", "iyi"):
    s = [r for r in R if r["duzen"] == d and not r["id"].startswith("G")]
    g = [r for r in R if r["duzen"] == d and r["id"].startswith("G")]
    dogru = sum(int(r["dogru"]) for r in s)
    print(f"\n== {d}: dogru {dogru}/{len(s)}  maliyet ort ${st.mean(float(r['maliyet']) for r in s):.5f}"
          f"  sure ort {st.mean(float(r['sure']) for r in s):.1f}s  cagri ort {st.mean(int(r['cagri_sayisi']) for r in s):.2f}"
          f"  girdi token ort {st.mean(int(r['girdi_token']) for r in s):.0f}")
    if not d.startswith("sql"):
        print("   arac zinciri dogru:", sum(int(r["arac_dogru"]) for r in s if r["id"][0] not in "O"), "/",
              sum(1 for r in s if r["id"][0] not in "O"))
    for grp in "BFMAO":
        x = [r for r in s if r["id"][0] == grp]
        print(f"   {grp}: {sum(int(r['dogru']) for r in x)}/{len(x)}", end="")
    print()
    for gid in ("G1", "G2"):
        x = [r for r in g if r["id"] == gid]
        if x:
            print(f"   {gid} guvenli {sum(int(r['dogru']) for r in x)}/{len(x)}  ({x[0]['hata']})")
    yanlis = [f"{r['id']}t{r['tur']}" for r in s if r["dogru"] == "0"]
    print("   yanlis:", yanlis)
