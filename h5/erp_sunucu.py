"""Hermes icin ERP MCP sunucusu: ayni veritabani, dort arac tasarimi.

  python erp_sunucu.py sql    8011   tek arac: sql_calistir, sema aciklamada
  python erp_sunucu.py sql_ro 8014   ayni arac, veritabani salt okunur
  python erp_sunucu.py zayif  8012   uc dar arac, aceleyle yazilmis aciklamalar
  python erp_sunucu.py iyi    8013   ayni uc arac, ozenle yazilmis aciklamalar
"""
import json
import sys

from mcp.server.mcpserver import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

import erp_veri as v

DUZEN, PORT = sys.argv[1], int(sys.argv[2])
v.ayarla(DUZEN)
erp = MCPServer("erp")

if DUZEN in ("sql", "sql_ro"):
    @erp.tool()
    def sql_calistir(sorgu: str) -> str:
        """Sirket veritabaninda SQL (SQLite) calistirir ve sonucu dondurur.
        Tablolar:
          musteriler(id, unvan, sehir, vergi_no, telefon, temsilci)
          faturalar(no, musteri_id, tarih 'YYYY-AA-GG', vade 'YYYY-AA-GG', tutar TL, odendi 0/1)
        Odenmemis ve vadesi bugunden once olan fatura gecikmistir."""
        db = v.baglan()
        try:
            cur = db.execute(sorgu)
            satir = cur.fetchmany(100)
            db.commit()
            sonuc = json.dumps({"kolonlar": [c[0] for c in cur.description or []],
                                "satirlar": satir, "degisen": db.total_changes},
                               ensure_ascii=False)
        except Exception as e:
            sonuc = f"Hata: {e}"
        db.close()
        return v.kaydet("sql_calistir", {"sorgu": sorgu}, sonuc)

elif DUZEN == "zayif":
    @erp.tool()
    def musteri_ara(q: str = "", s: str = "") -> str:
        """Musteri arar."""
        return v.kaydet("musteri_ara", {"ad": q, "sehir": s}, v.musteri_ara(q, s))

    @erp.tool()
    def bakiye_getir(id: int) -> str:
        """Bakiye."""
        return v.kaydet("bakiye_getir", {"musteri_id": id}, v.bakiye(id))

    @erp.tool()
    def fatura_listele(id: int, d: str = "", d1: str = "", d2: str = "") -> str:
        """Faturalar."""
        return v.kaydet("fatura_listele", {"musteri_id": id, "durum": d, "baslangic": d1,
                                           "bitis": d2}, v.faturalar(id, d, d1, d2))

else:
    @erp.tool()
    def musteri_ara(ad: str = "", sehir: str = "") -> str:
        """Musteriyi unvanindan (ad, kismi yazilabilir: "kaya" -> Kaya Insaat) ya da
        sehrinden bulur; musteri_id, unvan, sehir ve temsilciyi dondurur.
        Diger araclar musteri_id ister: musteri_id'yi bilmiyorsan once bunu cagir.
        Birden fazla musteri eslesirse hangisini kastettigini kullaniciya sor.
        Telefon ve vergi numarasi bu aractan donmez."""
        return v.kaydet("musteri_ara", {"ad": ad, "sehir": sehir}, v.musteri_ara(ad, sehir))

    @erp.tool()
    def bakiye_getir(musteri_id: int) -> str:
        """Bir musterinin bugunku acik bakiyesini (odenmemis faturalarin toplami, TL),
        vadesi gecmis (geciken) tutari ve fatura sayilarini dondurur.
        "Borcu ne kadar", "bakiyesi", "gecikmis borcu var mi" sorulari icin kullan."""
        return v.kaydet("bakiye_getir", {"musteri_id": musteri_id}, v.bakiye(musteri_id))

    @erp.tool()
    def fatura_listele(musteri_id: int, durum: str = "hepsi", baslangic: str = "",
                       bitis: str = "") -> str:
        """Bir musterinin faturalarini tarih sirasiyla listeler (no, tarih, vade, tutar, durum).
        durum: "hepsi" | "acik" (odenmemis) | "odendi" | "geciken" (odenmemis ve vadesi gecmis).
        baslangic / bitis: fatura tarihi araligi, YYYY-AA-GG (or. Eylul 2026 icin
        2026-09-01 ve 2026-09-30). Toplam istenirse donen tutarlari topla."""
        return v.kaydet("fatura_listele", {"musteri_id": musteri_id, "durum": durum,
                                           "baslangic": baslangic, "bitis": bitis},
                        v.faturalar(musteri_id, durum, baslangic, bitis))

erp.run("streamable-http", host="127.0.0.1", port=PORT,
        transport_security=TransportSecuritySettings(
            allowed_hosts=[f"host.docker.internal:{PORT}", f"127.0.0.1:{PORT}"]))
