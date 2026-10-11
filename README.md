# Hermes Agent Serisi: kodlar ve ölçümler

YouTube'daki 4 bölümlük **Hermes Agent** serisinin kodları. Seride gerçek
[NousResearch Hermes Agent](https://github.com/NousResearch/hermes-agent) (v0.21.6, resmî Docker imajı)
ve `gpt-5.6-luna` modeliyle şirket içi bir asistan kuruluyor. Her adım ölçülüyor.

| Bölüm | Video | Bu depoda |
|---|---|---|
| 1. Kurulum ve ölçüm | [Merhaba Dedim, OpenAI'ye 59 KB Gitti](https://youtu.be/rfycW1lLRmA) | `bolum1/` |
| 2. Araçlar ve hafıza | [Kendi Aracını Yaz, Hafızayı Ölç](https://youtu.be/nVjnPzj4pUk) | `bolum2/` |
| 3. Doküman asistanı | [Şirket Dokümanı Asistanı, 8/48'den 48/48'e](https://youtu.be/cG9aiFS37x8) | `bolum3/` |
| 4. Telegram'da canlı | [Telegram'dan "Sil" Dedim, Onay Sormadı](https://youtu.be/lopXOY_Vqvk) | `bolum4/` |

Videolardaki bütün sayılar `olcum/OLCUMLER.md` dosyasında, ham veriler `olcum/veri/` klasöründe.

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
