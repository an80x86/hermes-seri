---
name: tahsilat-raporu
description: Sirket veritabanindan gunluk tahsilat raporu hazirlar.
version: 0.1.0
author: Kullanıcı, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tahsilat, fatura, rapor]
    related_skills: []
---

# Tahsilat Raporu Skill

`sirket.db` içindeki faturalar ve müşterilerden günlük tahsilat raporu üretir. Yalnızca vadesi geçmiş ve ödenmemiş faturaları dahil eder; telefon ve vergi numarasını hiçbir çıktıya yazmaz.

## When to Use

- Kullanıcı “tahsilat raporunu hazırla” dediğinde.
- Kullanıcı açıkça günlük tahsilat raporu istediğinde.
- Don't use for: vadesi gelmemiş, ödenmiş veya farklı bir rapor türü istenen faturalar.

## Prerequisites

- Çalışma dizininde `sirket.db` bulunmalıdır.
- Veritabanında `faturalar` ve `musteriler` tabloları bulunmalıdır.
- Raporlar `raporlar/` klasörüne yazılır.

## How to Run

`terminal` ile SQLite sorgusunu çalıştır; bugünün UTC tarihini belirle; sonucu `write_file` ile `raporlar/tahsilat_YYYY-AA-GG.md` dosyasına yaz.

## Procedure

1. `terminal` ile bugünün tarihini `YYYY-AA-GG` biçiminde al. Tamamlanma ölçütü: rapor dosya adı bu tarihle eşleşir.
2. `terminal` veya Python SQLite modülüyle `faturalar` tablosunu `musteriler` tablosuna bağla. Filtre: `vade < bugün` ve `odendi = 0`. Tamamlanma ölçütü: vadesi bugün olan, gelecekteki veya ödenmiş fatura kalmaz.
3. Müşteri başına grupla; fatura numaralarını tek hücrede birleştir; gecikmiş tutarı topla; en eski vade tarihini al; toplamı hesapla. Tamamlanma ölçütü: her müşteri tabloda tam bir satırdır.
4. En eski vade tarihi bugünden 60 günden daha eskiyse müşteri adının başına `[ACİL] ` ekle. Sınır dahil değildir: tam 60 gün eski kayıt acil değildir.
5. Tutarları Türk biçiminde (`1.234.567,89 TL`) biçimlendir ve gecikmiş tutara göre azalan sırala. Tamamlanma ölçütü: sıralı tablo ve toplam birbiriyle tutarlıdır.
6. Başlık, hemen altındaki tek toplam satırı ve şu sütunlara sahip tek tabloyu yaz: `Müşteri | Temsilci | Fatura | Gecikmiş tutar | En eski vade`. Tamamlanma ölçütü: telefon ve vergi numarası metinde hiç geçmez.
7. `write_file` ile `raporlar/tahsilat_YYYY-AA-GG.md` dosyasını oluştur.

## Pitfalls

- Tarih karşılaştırması ISO `YYYY-AA-GG` metinleriyle yapılabilir; eşit tarih vadesi geçmiş sayılmaz.
- Her müşteri için tek satır kullanılmalıdır; faturaları ayrı satırlara bölme.
- `telefon` ve `vergi_no` sütunlarını sorgulama veya rapora aktarma.
- Türkçe ondalık ve binlik ayraçlarını karıştırma.
- Toplam satırını başlığın hemen altına koy; araya açıklama ekleme.

## Verification

- `read_file` ile oluşturulan raporu oku.
- Başlık tarihinin ve dosya adının bugünün tarihiyle eşleştiğini doğrula.
- Toplamın tüm müşteri tutarlarının toplamına eşit olduğunu ve satırların azalan sıralı olduğunu doğrula.
- Her rapor satırının yalnızca `vade < bugün` ve `odendi = 0` kayıtlarından oluştuğunu SQLite sorgusuyla yeniden doğrula.
- Rapor metninde `telefon`, `vergi` veya bu alanların değerlerinin bulunmadığını doğrula.
