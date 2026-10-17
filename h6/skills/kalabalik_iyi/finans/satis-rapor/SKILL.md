---
name: satis-rapor
description: "Satış raporu: dönem içinde kesilen faturalar, ürün bazında"
version: 1.0.0
author: Mustafa
---

# Satış Raporu

## Adımlar
1. `sirket.db` içindeki `faturalar` tablosundan son 30 günde kesilen faturaları (tarih) al.
2. Müşteri bazında topla, `raporlar/satis_YYYY-AA-GG.md` olarak yaz.
3. Ödeme durumuna bakma; satış raporu tahsilatla ilgilenmez.
