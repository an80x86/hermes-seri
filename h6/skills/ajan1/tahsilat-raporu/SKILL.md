---
name: tahsilat-raporu
description: Şirket verilerinden günlük tahsilat raporu oluşturur.
version: 0.1.0
author: Workspace User, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tahsilat, muhasebe, rapor, sqlite]
    related_skills: []
---

# Tahsilat Raporu Skill

Bu skill, çalışma dizinindeki `sirket.db` verilerinden günlük tahsilat raporu üretir. Yalnızca vadesi geçmiş ve ödenmemiş faturaları kullanır; rapora telefon ve vergi numarası yazmaz.

## When to Use

- Kullanıcı yalnızca “tahsilat raporunu hazırla” dediğinde.
- Kullanıcı aynı kurallarla günlük tahsilat raporu istediğinde.
- Başka bir tarih açıkça verilirse, “bugün” yerine verilen tarih kullanılabilir.

## Prerequisites

- Çalışma dizininde `sirket.db` bulunmalı.
- Veritabanında `faturalar(no, musteri_id, vade, tutar, odendi)` ve `musteriler(id, unvan, temsilci)` alanları bulunmalı.
- Python standart kütüphanesindeki `sqlite3` kullanılabilir olmalı.

## How to Run

`terminal` ile çalışma dizininde mevcut tarihi UTC olarak al; ardından Python `sqlite3` ile sorguyu çalıştır ve çıktıyı `raporlar/tahsilat_YYYY-AA-GG.md` dosyasına `write_file` ile yaz.

## Procedure

1. `terminal` ile tarihi `YYYY-MM-DD` biçiminde al. Tarih doğrulanmadan rapor üretme.
2. `sirket.db` içinden şu koşulları sağlayan faturaları çek: `vade < rapor_tarihi` ve `odendi = 0`. `faturalar` ile `musteriler` tablolarını `musteri_id = id` üzerinden birleştir.
3. Sonuçları müşteri bazında grupla. Her müşterinin faturalarını `Fatura` sütununda virgülle ayır; gecikmiş tutarı topla; en eski vade tarihini seç.
4. Müşterinin en eski vadesi `rapor_tarihi - 60 gün` tarihinden önceyse müşteri adının başına `[ACİL] ` ekle. Eşit tarih “60 günden eski” sayılmaz.
5. Tüm müşteri toplamlarını topla ve Türkçe para biçiminde, iki ondalıkla yaz: binlik ayırıcı `.`, ondalık ayırıcı `,`, sonuna ` TL`.
6. Markdown dosyasını tam olarak şu yapıda oluştur:
   - Başlık: `# Bugünün Tahsilat Raporu — YYYY-AA-GG`
   - Başlığın hemen altındaki tek satır: `Toplam gecikmiş alacak: <tutar> TL`
   - Tek tablo sütunları: `Müşteri | Temsilci | Fatura | Gecikmiş tutar | En eski vade`
   - Satırlar gecikmiş tutara göre büyükten küçüğe sıralı.
7. `write_file` ile `raporlar/tahsilat_YYYY-AA-GG.md` dosyasını oluştur; gerekirse `raporlar/` dizini oluşturulsun.

## Pitfalls

- Vadesi bugün olan faturaları dahil etme; koşul kesinlikle `vade < bugün` olmalı.
- `odendi = 1` faturaları dahil etme.
- Müşteri başına birden fazla satır yazma.
- Telefon, vergi numarası, şehir veya başka KVKK kapsamındaki alanları rapora ekleme.
- Para değerlerini Python varsayılan gösterimiyle yazma; Türk biçimine dönüştür.
- Fatura numaralarını değiştirme veya normalize etme.

## Verification

- Rapor dosyasını `read_file` ile oku.
- Başlık altındaki toplamın sorgudaki seçili faturaların toplamına eşit olduğunu Python ile doğrula.
- Tablo satır sayısının müşteri sayısına, fatura numarası sayısının seçili fatura sayısına eşit olduğunu doğrula.
- Her faturanın `vade < rapor_tarihi` ve `odendi = 0` koşullarını sağladığını doğrula.
- Satırların toplam tutara göre azalan sırada olduğunu doğrula.
- Dosya içeriğinde `telefon`, `vergi`, `vergi_no` veya telefon/vergi numarası bulunmadığını doğrula.
