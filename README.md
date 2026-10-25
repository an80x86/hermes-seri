# Hermes Agent Serisi: kodlar ve ölçümler

YouTube'daki **Hermes Agent** serisinin kodları. Seride gerçek
[NousResearch Hermes Agent](https://github.com/NousResearch/hermes-agent) (v0.21.6, resmî Docker imajı)
ve `gpt-5.6-luna` modeliyle şirket içi bir asistan kuruluyor. Her adım ölçülüyor.

| Bölüm | Video | Bu depoda |
|---|---|---|
| 1. Kurulum ve ölçüm | [Merhaba Dedim, OpenAI'ye 59 KB Gitti](https://youtu.be/rfycW1lLRmA) | `bolum1/` |
| 2. Araçlar ve hafıza | [Kendi Aracını Yaz, Hafızayı Ölç](https://youtu.be/nVjnPzj4pUk) | `bolum2/` |
| 3. Doküman asistanı | [Şirket Dokümanı Asistanı, 8/48'den 48/48'e](https://youtu.be/cG9aiFS37x8) | `bolum3/` |
| 4. Telegram'da canlı | [Telegram'dan "Sil" Dedim, Onay Sormadı](https://youtu.be/lopXOY_Vqvk) | `bolum4/` |
| 5. Kendi MCP sunucun | [Agent'a SQL Verdim, Faturaları Kendi Kapattı](https://youtu.be/Guu4fbOyc7I) | `h5/` |
| 6. SKILL.md anatomisi | [3'te 2: Agent Skill'i Yanlış Yere Kaydetti](https://youtu.be/LBOoQPCtW48) | `h6/` |
| 14. Kimlik, yetki ve denetim | 9'da 9: 'Onayladı' Yazdı, Agent Erişimi Açtı (27 Ekim) | `h14/` |

1-4. bölümlerin sayıları `olcum/OLCUMLER.md` dosyasında, ham veriler `olcum/veri/` klasöründe. 5. bölümün sonuçları `h5/SONUC.md`, ham veriler `h5/veri/`. 6. bölümün sonuçları `h6/SONUC.md`, ham veriler `h6/veri/`. 14. bölümün sonuçları `h14/SONUC.md`, ham veriler aynı klasörde (`olcum.csv`, `log_a.txt`, `denetim_b.jsonl`).

## Klasörler

```
bolum1/  kurulum.sh          Docker'da kurulum, model seçimi, ilk konuşma (--usage-file ile maliyet)
         kayit_proxy.py      Hermes ile OpenAI arasındaki kayıt vekili: giden her isteği kaydeder (anahtar hariç)
bolum2/  takvim_mcp.py       38 satırlık MCP aracı: iş günü hesabı (hafta sonu + 2026 resmî tatilleri)
         temizlik.sh         state.db ve hafıza dosyasından bir bilgiyi gerçekten silmek
bolum3/  dokuman_mcp.py      61 satırlık doküman aracı: rol filtreli anlamsal arama, kaynaklı sonuç
         dokumanlar/         Örnek şirket dokümanları (10 dosya, 4 klasör, hepsi uydurma veri)
         sorular.json        Ölçüm soruları: 24 cevaplı + 6 dokümanda olmayan
bolum4/  canli_kurulum.sh    Hermes'i Telegram botu olarak canlıya alma
         kural.md            SOUL dosyasına eklenen kural (3. bölümdeki + gizli talimat satırı)
         dokuman_mcp_enjeksiyon.py, dokumanlar/   Masraf dokümanına gizli talimat eklenmiş kopya (test için)
h5/      erp_sunucu.py       ERP MCP sunucusu, dört araç tasarımı: sql, sql_ro, zayif, iyi
         erp_veri.py         Ortak iş mantığı (müşteri arama, bakiye, fatura listesi, çağrı kaydı)
         canli_soru.py       Hermes'e tek soru sorar, sunucunun gördüğü araç çağrılarını canlı yazar
         veri_uret.py, soru_uret.py   Örnek veritabanı (40 müşteri, 326 fatura) ve 20 soru + beklenen cevaplar
         olc.py, ozet.py     Ölçüm ve özet (elle_duzeltme.json: elle okunup düzeltilen 11 puan)
h6/      skills/             Ölçülen skill'ler, düzen başına bir klasör (benim, benim_betik, ajan1-3, kotu_*, kalabalik_*)
         canli.py            Temiz Hermes'e betikli skill'i koyup kısa isteği verir; çağrıları ve raporu yazar
         olc.py, kontrol.py  110 çalıştırma ve 8 ölçütlü puanlama (beklenen.py: değerler veritabanından)
         ajan_skill_uret.py  Ajana kuralları anlatıp "skill olarak kaydet" dedirten 3 oturum
                             (ajan_uretim.json'daki maliyet Hermes'in tahmini; doğrusu SONUC.md'de)
         Veritabanı: python3 ../h5/veri_uret.py && cp ../h5/sirket.db .   (H5 ile aynı, birebir)
         Canlı çalıştırma: H6_DENEY=$PWD python3 canli.py
h14/     yardim_sunucu.py    BT yardım masası MCP sunucusu: a (servis hesabı) / b (X-Jeton kimliği + politika + zincirli denetim)
         istekler.json       17 istek ve iki SOUL metni; jetonlar.json: test jetonları (gerçek kimlik bilgisi değil)
         olc.py              4 düzen × 17 istek × 3 tekrar = 204 çalıştırma (sunucular: python yardim_sunucu.py a 8021 / b 8022)
         denetim_dogrula.py  Zinciri doğrular; --kurcala bir satırı değiştirip siler, ikisi de yakalanmalı
         canli.py            Temiz Hermes'e tek mesaj (B sunucusu), cevabı ve denetim kaydının son satırını yazar
                             Önce: python3 canli_hazirla.py (Hermes taban klasörü 2. bölümdeki b2taban'dan)
olcum/   *_olc.py            Ölçüm betikleri (her bölüm için)
         sahte_telegram.py   Ölçümde kullanılan sahte Telegram Bot API sunucusu
         b4_vekil.py         Hermes'e sahte anahtar verip gerçeğini yalnızca vekilde tutan vekil
         OLCUMLER.md         Bütün sonuçlar
```

## Doküman aracını çalıştırmak (3. bölüm)

```sh
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python bolum3/dokuman_mcp.py      # 127.0.0.1:8001, ilk açılışta e5 modeli iner (~1 GB)
```

Hermes'in `config.yaml` dosyasına:

```yaml
mcp_servers:
  dokuman:
    url: http://host.docker.internal:8001/mcp
    headers:
      X-Jeton: "satis-41b7"     # rol jetondan gelir: satis-41b7, ik-9c2e, yonetim-d05a
```

Sonra kuralı (`bolum4/kural.md`) Hermes'in SOUL dosyasının sonuna ekleyin.
Jetonlar örnek değerlerdir; gerçek kullanımda kendi rastgele değerlerinizi koyun.

## MCP sunucusunu çalıştırmak (5. bölüm)

```sh
cd h5
python3 veri_uret.py && python3 soru_uret.py     # sirket.db + sorular.json
pip install mcp                                  # Python MCP SDK 2.0
python3 erp_sunucu.py iyi 8013                   # 127.0.0.1:8013; düzenler: sql 8011, zayif 8012, sql_ro 8014
```

Hermes'in `config.yaml` dosyasına:

```yaml
mcp_servers:
  erp:
    url: http://host.docker.internal:8013/mcp
```

Sonra `-t erp` ile yalnızca bu araç setini açın (`python3 canli_soru.py`). Veritabanındaki isimler ve numaralar uydurmadır;
yayımlanan ham verilerde telefon numaraları ayrıca maskelendi.

## Bilmeniz gerekenler

- **Anahtarlar depoda yok.** Betikler OpenAI anahtarını kabuk değişkeninden ya da `.env` dosyasından okur.
  Telegram token'ı `telegram.env` dosyasında (chmod 600) durur; bu dosyayı depoya koymayın.
- **Telegram'da araç setini kısıtlayın.** Varsayılan `hermes-telegram` setinde terminal ve dosya araçları var;
  ölçümde "dosyaları sil" isteği onay sorulmadan 15/15 dosyayı sildi. `canli_kurulum.sh` 4. adım:
  `hermes config set platform_toolsets.telegram '[dokuman]'`
- **Ölçüm betikleri sizin ortamınıza göre değil.** Yollar (`~/hermes-seri/...`) ve Docker ağı (`hermes-net`)
  benim kurulumuma göre yazıldı; yöntemi görmek için okuyun, çalıştırmadan önce yolları düzeltin.
- Sayılar tek model (`gpt-5.6-luna`) ve küçük bir örnek set için ölçüldü (Ekim 2026). Kendi dokümanlarınızda yeniden ölçün.

## Lisans

MIT. Hermes Agent'ın kendisi NousResearch'e aittir (MIT).
