---
name: tahsilat-raporu
description: "Tahsilat raporu: vadesi geçmiş faturalar, müşteri bazında"
version: 1.0.0
author: Mustafa
metadata:
  hermes:
    tags: [finans, tahsilat, fatura, rapor]
---

# Tahsilat Raporu

## Ne zaman
Kullanıcı tahsilat raporu, gecikmiş alacak, "kim borçlu" ya da vadesi geçmiş fatura listesi istediğinde.

## Adımlar
1. Çalışma dizininde (içinde `sirket.db` olan klasör) bu skill'in betiğini çalıştır:
   `python3 <skill klasörü>/scripts/rapor.py sirket.db`
2. Betik `raporlar/tahsilat_<bugün>.md` dosyasını yazar ve tek satır özet basar. Raporu elle yazma, betiği düzenleme.
3. Kullanıcıya özet satırını ve dosya yolunu bildir.

## Betik neyi garanti eder
- Yalnızca vadesi geçmiş ve ödenmemiş faturalar, müşteri başına bir satır, büyükten küçüğe.
- Türk para biçimi (1.234.567,89 TL), 60 günden eski vadeye [ACİL] etiketi.
- Telefon ve vergi numarası sorguya hiç girmez (KVKK).
