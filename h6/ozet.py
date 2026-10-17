"""olcum.csv ozeti: duzen basina tam puan, ortalama puan, skill yukleme, arac, sure, maliyet, olcut sayilari."""
import csv
import statistics as st
import sys
from collections import defaultdict

O = ["dosya", "toplam", "musteri_kumesi", "siralama", "tutarlar", "temsilci", "acil", "kvkk"]
g = defaultdict(list)
for r in csv.DictReader(open(sys.argv[1] if len(sys.argv) > 1 else "olcum.csv")):
    g[r["duzen"]].append(r)
print(f"{'duzen':14} n  tam puan skill arac  sure  maliyet   token | " + " ".join(o[:5] for o in O))
for d, rs in g.items():
    f = lambda k: [float(r[k]) for r in rs if r[k] != ""]
    print(f"{d:14}{len(rs):2} {sum(f('tam')):4.0f} {st.mean(f('puan')):4.2f} {sum(f('skill_yuklendi')):5.0f} "
          f"{st.mean(f('arac_sayisi')):4.1f} {st.mean(f('sure')):5.1f} {st.mean(f('maliyet')):.5f} "
          f"{st.mean(f('token')):6.0f} | " + " ".join(f"{sum(f(o)):5.0f}" for o in O))
