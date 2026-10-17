---
name: tahsilat-raporu
description: Şirket veritabanından günlük tahsilat raporu üretir.
version: 0.1.0
author: Kullanıcı, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tahsilat, muhasebe, faturalar, rapor]
    related_skills: []
---

# Tahsilat Raporu Skill

`sirket.db` içindeki faturalar ve müşterilerden, çalıştırıldığı gün için Türkçe biçimli tahsilat raporu üretir. Yalnızca vadesi geçmiş ve ödenmemiş faturaları dahil eder; telefon ve vergi numarasını hiçbir çıktıya taşımaz.

## When to Use

- Kullanıcı “tahsilat raporunu hazırla” dediğinde.
- Kullanıcı bugünün gecikmiş alacak raporunu istediğinde.
- Kullanma: ödenmiş, vadesi gelmemiş veya farklı tarihli rapor istenen faturalar için; tarih açıkça verilmişse aynı kuralları o tarihe uygula.

## Prerequisites

- Çalışma dizininde `sirket.db` bulunur.
- Python standart kütüphanesi `sqlite3`, `datetime` ve `pathlib` kullanılabilir.
- Veritabanı tabloları `faturalar(no, musteri_id, vade, tutar, odendi)` ve `musteriler(id, unvan, temsilci)` alanlarını içerir.

## How to Run

`terminal` ile çalışma dizininde Python kullanarak raporu üret; tarih için sistemin UTC tarihini `date -u +%F` ile al, raporu `raporlar/tahsilat_YYYY-AA-GG.md` yoluna yaz.

## Procedure

1. Bugünün tarihini ISO biçiminde al ve `D` olarak kullan. Tamamlanma ölçütü: dosya adı bu tarihle eşleşir.
2. `faturalar` ile `musteriler` tablolarını `musteri_id = id` üzerinden birleştir. Filtreyi tam olarak `vade < D AND odendi = 0` yap; `D` tarihindeki vade gecikmiş sayılmaz. Tamamlanma ölçütü: sonuç kümesinde başka fatura bulunmaz.
3. Sonuçları müşteri ve temsilciye göre grupla. Her müşteri için faturaları tek hücrede fatura numarasıyla listele, tutarları topla ve en küçük vadeyi seç. Tamamlanma ölçütü: tabloda her müşteri yalnızca bir satırdır.
4. En küçük vade ile `D` arasındaki gün sayısı 60’tan büyükse müşteri adının başına `[ACİL] ` ekle. Tamamlanma ölçütü: yalnızca 60 günden eski en küçük vadeye sahip müşteriler işaretlidir.
5. Müşterileri toplam gecikmiş tutara göre azalan sırala. Tutarları iki ondalıkla Türk biçiminde (`1.234.567,89 TL`) yaz. Tamamlanma ölçütü: her ardışık tutar bir öncekinden büyük değildir.
6. Markdown dosyasını şu yapıyla yaz:
   - Başlık.
   - Başlığın hemen altında, tek satır olarak toplam: `Toplam gecikmiş alacak: <tutar> TL`.
   - Sütunları tam olarak `Müşteri | Temsilci | Fatura | Gecikmiş tutar | En eski vade` olan tek tablo.
   - Telefon, vergi numarası veya başka kişisel iletişim/vergi alanı yok.
7. Yazma tamamlandıktan sonra `read_file` ile dosyayı kontrol et. Tamamlanma ölçütü: dosya mevcut, toplam satırı ile tablo başlığı doğru sırada ve telefon/vergi numarası metinleri yoktur.

## Quick Reference

- Filtre: `f.vade < ? AND f.odendi = 0`
- Gruplama: müşteri başına tek satır
- Sıralama: toplam gecikmiş tutar, azalan
- Acil eşiği: `D - en_eski_vade > 60 gün`
- Çıktı: `raporlar/tahsilat_<bugün>.md`

## Pitfalls

- SQLite tarihleri ISO `YYYY-MM-DD` metinleri olarak karşılaştırılabilir; yerel tarih biçimine çevirmeden karşılaştır.
- `odendi = 1` faturaları ve vadesi bugün olan faturaları rapora alma.
- Müşteri başına toplam tutarı kullan; tek tek fatura tutarına göre sıralama yapma.
- Tutar biçiminde binlik ayraç nokta, ondalık ayraç virgüldür.
- Rapor ve doğrulama çıktısında `telefon` veya `vergi_no` alanlarını seçme, yazdırma ya da ekleme.

## Verification

- `sirket.db` üzerinde aynı filtreyle yeniden sayım yap; rapordaki müşteri satırları ve toplam tutar sorgu sonucuyla eşleşsin.
- Rapor satırlarının tutarlarını parse ederek azalan sıralamayı doğrula.
- En eski vade yaşı 60 günden büyük olan her müşterinin `[ACİL]` ile başladığını ve diğerlerinin başlamadığını kontrol et.
- Dosya metninde telefon numarası veya vergi numarası desenleri bulunmadığını kontrol et.
