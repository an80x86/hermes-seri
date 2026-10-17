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
1. Veri çalışma dizinindeki `sirket.db` (SQLite). Bugünün tarihini `date +%F` ile al.
2. Şu sorguyu çalıştır (`?` yerine bugünün tarihi):
   ```sql
   select m.unvan, m.temsilci, count(*), sum(f.tutar), min(f.vade)
   from faturalar f join musteriler m on m.id = f.musteri_id
   where f.odendi = 0 and f.vade < ?
   group by m.id order by sum(f.tutar) desc;
   ```
3. Raporu `raporlar/tahsilat_YYYY-AA-GG.md` olarak yaz (klasör yoksa oluştur).

## Biçim
```
# Tahsilat Raporu — YYYY-AA-GG

Toplam gecikmiş alacak: 1.234.567,89 TL

| Müşteri | Temsilci | Fatura | Gecikmiş tutar | En eski vade |
| --- | --- | --- | --- | --- |
| [ACİL] Örnek Ticaret | Ad Soyad | 3 | 123.456,78 TL | 2026-01-15 |
```
- Tutarlar Türk biçiminde: binlik ayırıcı nokta, ondalık virgül, iki hane, sonda " TL".
- En eski vadesi bugünden 60 günden fazla önce olan müşterinin adının başına `[ACİL] ` yaz.
- Satırlar gecikmiş tutara göre büyükten küçüğe.

## Yasak
- Telefon ve vergi numarası rapora asla girmez (KVKK). Sorguya bu kolonları hiç alma.

## Bitirmeden önce kontrol et
- Toplam satırı = tablodaki tutarların toplamı.
- Ödenmiş ya da vadesi gelmemiş fatura yok.
- Dosya adı bugünün tarihini taşıyor.
