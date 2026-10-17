# Sonuç — H6 SKILL.md Anatomisi: Agent'ın Yazdığı Skill mi, Benim Yazdığım mı?

Tarih: 2026-10-16 · Deney: bu klasör · Tekrar: her düzende 10 çalıştırma (toplam 110) + 3 skill üretim oturumu

## Soru
Aynı iş için skill'i ajana mı yazdırmalı, elle mi yazmalı? SKILL.md'nin hangi parçası sonucu belirliyor?

## Düzenek
- Veri: H5'in `sirket.db`'si (40 müşteri, 326 fatura). Bugün 2026-10-16.
- İş: "sirket.db'deki verilerle bugünün tahsilat raporunu hazırla." (her düzende aynı kısa istek)
- Şirket kuralları (`kurallar.md`, 7 kural): dosya adı `raporlar/tahsilat_YYYY-AA-GG.md`;
  yalnızca vadesi geçmiş ve ödenmemiş faturalar; başlık altında "Toplam gecikmiş alacak: … TL";
  müşteri başına tek satırlık tablo (Müşteri | Temsilci | Fatura | Gecikmiş tutar | En eski vade),
  tutara göre azalan; Türk para biçimi; 60 günden eski vadeye [ACİL]; telefon/vergi no yok (KVKK).
- Puan: `kontrol.py`, 8 ölçüt (dosya, toplam satırı, müşteri kümesi, sıralama, tutarlar,
  temsilci, [ACİL], KVKK), beklenen değerler veritabanından (`beklenen.py`): 31 müşteri,
  8.071.788,25 TL, 18 [ACİL]. "Tam" = 8/8.
- Agent: Hermes Agent (Docker), gpt-5.6-luna, araç seti `terminal,file,skills`; profilde 58 hazır
  skill. Her çalıştırma temiz kopya (`~/hermes-seri/h6_olc/<düzen>_<n>`), oturum `-z`,
  hafıza/skill dürtmeleri kapalı. Skill'in yüklenip yüklenmediği `state.db`'deki `skill_view`
  çağrısından okundu. Maliyet H5 ile aynı formül (gpt-5.6-luna $/1M: 0,20 / 0,02 / 0,25 / 1,20).

Düzenler:
| Düzen | Ne |
| --- | --- |
| yok | skill yok, yalnızca kısa istek |
| prompt | skill yok, 7 kural her seferinde isteğe yapıştırılıyor |
| ajan1–3 | ajanın kendi yazdığı skill (kurallar bir kez anlatıldı, "skill olarak kaydet" dendi; 3 bağımsız oturum) |
| benim | elle yazılmış SKILL.md, 1.533 karakter, açıklama 57 karakter |
| benim_betik | elle yazılmış SKILL.md (910 karakter) + `scripts/rapor.py` |
| kotu_aciklama | `benim` gövdesi, açıklama 146 karakter |
| kotu_ad | `kotu_aciklama` + belirsiz ad `finans-rapor` |
| kalabalik_kotu | 4 finans skill'i (tahsilat + satış, kasa, borç); açıklamaların ilk 57 karakteri aynı |
| kalabalik_iyi | aynı 4 skill, kısa ve ayırt edici açıklamalar |

## Sonuç tablosu
| Düzen | Tam (10) | Ort. puan (8) | Skill yüklendi | Araç çağrısı | Süre (sn) | Maliyet ($) | Token |
| --- | --- | --- | --- | --- | --- | --- | --- |
| yok | 0 | 1,00 | — | 8,3 | 45,9 | 0,00975 | 94.341 |
| prompt | **10** | 8,00 | — | 9,9 | 50,5 | 0,01221 | 123.386 |
| ajan1 | 10 | 8,00 | 10 | 9,0 | 48,5 | 0,01124 | 109.375 |
| ajan2 | 10 | 8,00 | 10 | 5,5 | 31,1 | 0,00586 | 49.482 |
| ajan3 | **0** | 7,00 | 10 | 9,7 | 49,8 | 0,01143 | 109.279 |
| benim | 10 | 8,00 | 10 | 7,9 | 40,3 | 0,00728 | 66.067 |
| benim_betik | 10 | 8,00 | 10 | **5,0** | **20,5** | **0,00314** | **34.172** |
| kotu_aciklama | 10 | 8,00 | 10 | 7,5 | 40,8 | 0,00696 | 62.701 |
| kotu_ad | 10 | 8,00 | 10 | 8,3 | 46,3 | 0,00785 | 73.192 |
| kalabalik_kotu | **5** | 5,60 | **5** | 10,0 | 59,1 | 0,01245 | 149.042 |
| kalabalik_iyi | 10 | 8,00 | 10 | 8,0 | 55,4 | 0,00765 | 71.208 |

Ayrıntılar:
- **yok:** 10/10 çalıştırmada gecikmiş toplam (8.071.788,25 TL) doğru hesaplandı, hiçbir çıktıda
  telefon/vergi no yok. Ama şirket kurallarının hiçbiri tutmadı: 3 farklı dosya türü (6 md, 3 txt,
  1 html), 3 farklı dosya adı, kural tablosu yok. Ajan veriyi biliyor, şirketin alışkanlığını bilmiyor.
- **prompt:** kuralları her seferinde yapıştırmak 10/10 tam; ama en pahalı ikinci düzen.
  Kural metni her istekte yeniden okunuyor.
- **benim_betik:** prompt'a göre 3,89 kat ucuz, 2,46 kat hızlı. Ajan betiği çalıştırıp dosyayı
  okuyor; raporu kendisi yazmıyor. `benim` (yalnızca metin) prompt'tan %40 ucuz.

### Ajanın kendi skill'i
- Üretim oturumları (kurallar istekte): 3/3 rapor 8/8; maliyet $0,0158–0,0232 (bir kerelik).
- **3 oturumun 3'ü de "Skill kaydedildi" dedi; hiçbiri `skill_manage` aracını kullanmadı,
  üçü de dosyayı `write_file` ile yazdı.**
- **3'ün 2'sinde dosya `/opt/data/.hermes/skills/` altına yazıldı; Hermes skill'leri
  `/opt/data/skills/`'ten okuyor.** `hermes skills list` bu iki skill'i göstermiyor (0), üçüncüsünü
  gösteriyor (1). Kendiliğinden bırakılsa 3 skill'in 2'si bir daha hiç yüklenmezdi.
  Ölçümde içerik kalitesini görmek için üçü de doğru klasöre elle kondu.
- Ajan skill'leri 3.007–3.822 karakter (benimki 1.533). Üçünün de açıklaması "günlük tahsilat
  raporu" diyor ("vadesi geçmiş" yok).
- **ajan3: 10/10 çalıştırmada 7/8.** Skill toplam satırının tam ifadesini yazmamış ("toplamı
  başlığın altına koy" diyor). Sayı 10/10 doğru, etiket 4 farklı biçimde çıktı: "Toplam gecikmiş
  tutar" (4), "Toplam gecikmiş tutar:" sayısız (3), "Toplam gecikmiş tahsilat" (2), "Toplam
  gecikmiş ve ödenmemiş tutar" (1). Muhasebe "Toplam gecikmiş alacak" satırını arıyorsa bulamaz.
- ajan1 ve ajan3 ajan2'nin yaklaşık 2 katı maliyetli (terminal çağrısı 56 ve 58, ajan2'de 32):
  skill'lerine uzun doğrulama adımları yazmışlar.

### Açıklama (description) ve 60 karakter
- Hermes sistem prompt'undaki skill listesinde açıklamanın yalnızca ilk 57 karakteri + "..."
  görünüyor (`SKILL_PROMPT_DESC_LIMIT = 60`, `agent/skill_utils.py`). `state.db`'deki sistem
  prompt'unda doğrulandı: "Bu beceri, şirketimizin muhasebe ekibinin her hafta ihtiy...".
  Ajanın `skill_manage` ile yazdığı skill'lerde bu sınır zorunlu; elle konan dosyada kesilir.
- Tek finans skill'i varken kesik açıklama zarar vermedi: kotu_aciklama 10/10, belirsiz adla bile
  (kotu_ad) 10/10. Ajan "finans" kategorisinden ve "muhasebe" kelimesinden buldu.
- **Benzer skill'ler yan yana olunca:** ilk 57 karakteri aynı dört skill'de ajan 10 çalıştırmanın
  6'sında önce kasa-rapor'u açtı (1'inde sonra doğrusuna geçti); doğru skill'i 5/10 yükledi;
  tam rapor 5/10. Doğru skill'i yükleyen 5 çalıştırmanın 5'i 8/8; yalnızca kasa-rapor'da kalan
  5 çalıştırma 2–5 puan (2, 2, 2, 5, 5).
  Aynı dört skill kısa ve ayırt edici açıklamalarla: 10/10 doğru skill, 10/10 tam; maliyet
  $0,00765'e karşı $0,01245 (1,63 kat).

## Başlığa girecek sayı
- 3'te 2: ajan "skill'i kaydettim" dedi, Hermes'in okumadığı klasöre yazdı.
- 10'da 5: açıklamalar aynı başlayınca ajan doğru skill'i yarı yarıya buldu (ayırt edici açıklamayla 10/10).
- 3,89 kat: betikli skill, kuralları her seferinde yapıştırmaktan ucuz.

## Beklenmeyen bulgular / sınırlar
- Planın sorusu "ajanın skill'i mi benimki mi" idi; içerik kalitesi yakın çıktı (3 ajan skill'inin
  2'si 10/10). Fark, skill'in **nereye ve nasıl** kaydedildiğinde ve **açıklamanın ilk 57
  karakterinde**.
- Açıklama sınırının etkisi ancak benzer skill'ler varken görüldü; tek skill'de ölçülemedi.
- Tek model (gpt-5.6-luna), tek iş, her düzende 10 tekrar, 3 ajan skill'i. Ajan skill'leri
  istekte kurallar tam verilerek üretildi; kuralları eksik anlatan kullanıcıda sonuç farklı olabilir,
  ölçülmedi.
- Konteynerin saat dilimi UTC; tarih farkı (gece yarısı) etkisi ölçülmedi, videoda söylenmez.
- Ham veri: `veri/olcum_hepsi.csv` (110 satır), `ajan_uretim.json`, skill'ler `skills/`.
