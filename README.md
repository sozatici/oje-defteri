# Oje Defteri

**Kullanmak için:** https://sozatici.github.io/oje-defteri/

Oje koleksiyonu takip uygulaması. Tek dosyalık, kurulum gerektirmeyen bir
web sayfası: hangi ojeler var, ne zaman alındı, kaça alındı, hangisi
kullanımda, hangisi bitti.

## Neler yapar

- Marka, isim/numara, renk, alım tarihi, fiyat, durum, fotoğraf ve not
- Durumlar: Açılmamış · Kullanımda · Bitti · Atıldı
- Renk kutucuklu ızgara; arama, duruma/markaya/renge göre filtre, sıralama
- **Barkod tarama:** mağazadayken "bu oje bende var mı?" sorusunu anında
  cevaplar; barkod önekinden markayı kendi kendine öğrenir
- **Fotoğraftan renk:** çekilen fotoğraftan baskın rengi bulur
- Özet: toplam harcama, durum ve renk dağılımı, ojelerin ortalama dayanma
  süresi, "6 aydır açılmamış" listesi
- Yedek al / yedekten yükle (telefon değiştirirken taşıma yolu)

Veriler yalnızca kullanan kişinin telefonunda durur; hiçbir yere
gönderilmez. Hesap gerekmez.

## Geliştirme

Kaynak `src/oje-defteri.html`. Barkod okuyucu kütüphanesi dağıtılan
dosyanın içine gömülür, bu yüzden düzenlemeden sonra:

```
python build.py
```

Bu komut iki çıktı üretir:

- `oje-defteri.html` — telefona doğrudan atılabilen tek dosya
- `site/index.html` — web adresine konan sürüm (manifest ve ikonlarla)

Tasarım kararları ve gerekçeleri: `docs/superpowers/specs/`
