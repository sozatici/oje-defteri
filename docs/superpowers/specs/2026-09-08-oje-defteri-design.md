# Oje Defteri — Tasarım Dokümanı

Tarih: 2026-09-08
Durum: Onaylandı

## Amaç

Kişisel bir oje koleksiyonunu takip etmek: hangi ojeler var, ne zaman
alındı, kaça alındı, hangisi kullanımda, hangisi bitti. Kullanıcı
çoğunlukla telefondan bakacak — oje dolabının başındayken hızlıca
"bu renk bende var mı", "bunu ne zaman almıştım" sorularını
cevaplayabilmeli.

Beklenen koleksiyon büyüklüğü: 30–100 kayıt.

## Kısıtlar ve kararlar

**Hesap gerekmez.** Kullanıcının eşi hiçbir servise kaydolmadan, giriş
yapmadan kullanabilmeli.

**Tek dosya.** Dağıtılan ürün tek bir `oje-defteri.html` dosyasıdır.
Çalışırken dışarıdan hiçbir şey yüklemez — CDN, font, uzak kütüphane
yok. İnternet olmadan açılır (yalnız isteğe bağlı ürün adı sorgusu
internet ister ve yoksa sessizce atlanır). Aynı dosya iki şekilde
çalışır: telefona kopyalanıp doğrudan açılarak (`file://`), veya bir
statik web adresine konularak (`https://`).

Barkod okuyucu kütüphanesi dosyanın içine gömülüdür, bu yüzden depo
üç parçaya ayrılır: `src/oje-defteri.html` düzenlenen kaynak,
`vendor/zxing.min.js` gömülecek kütüphane, `python build.py` ikisini
birleştirip kök dizine dağıtılabilir `oje-defteri.html` üretir. Kaynak
dosya doğrudan açılmaz; her değişiklikten sonra build çalıştırılır.

**iOS/Safari riski.** `file://` altında açılan sayfaların depoladığı
veriyi Safari geçici sayıp temizleyebilir. Bu riske karşı önlem yedek
alma/geri yükleme mekanizmasıdır (aşağıda). Ayrıca kamera yalnız güvenli
adreste (`https://`) açılır; dosyadan açıldığında barkod taranamaz,
numara elle yazılır. Her iki kısıt da dosya ücretsiz bir statik
barındırmaya (ör. GitHub Pages) konarak ortadan kalkar; uygulamada
değişiklik gerekmez.

**Arayüz dili: Türkçe.** Tüm etiketler, düğmeler, uyarı ve hata
mesajları Türkçedir.

## Veri modeli

Tek bir kayıt türü: **oje**.

| Alan | Tip | Zorunlu | Not |
|---|---|---|---|
| `id` | metin | evet | Kayıt oluşturulurken üretilir |
| `marka` | metin | hayır | Filtre listesi bu alandan türetilir |
| `isim` | metin | hayır | Ürün adı veya numarası |
| `renk` | `#rrggbb` | evet | Renk seçiciden alınır; ızgarada kutucuk olarak görünür |
| `barkod` | rakam dizisi | hayır | Kameradan okunur veya elle yazılır; 6–14 hane |
| `alimTarihi` | tarih | hayır | "Kaç aydır duruyor" hesabının kaynağı |
| `fiyat` | sayı | hayır | Toplam harcama özetinde kullanılır |
| `durum` | sabit liste | evet | `acilmamis` \| `kullanimda` \| `bitti` \| `atildi` |
| `bitisTarihi` | tarih | hayır | Yalnız `bitti`/`atildi` durumunda sorulur |
| `foto` | küçültülmüş görsel | hayır | Uzun kenar 800 piksele indirilir |
| `not` | metin | hayır | Serbest not |
| `eklenmeZamani` | zaman damgası | evet | Varsayılan sıralamanın kaynağı |

**Renk ailesi** saklanmaz; `renk` alanından hesaplanır (kırmızı, pembe,
nude, kahve, turuncu, sarı, yeşil, mavi, mor, nötr). Filtre bu
hesaplanan değere göre çalışır. Kahve ailesi ayrı tutulur: koyu kahve
ojeler ton olarak kırmızıya düşer ve o etiketle yanlış görünür.

**Dayanma süresi** saklanmaz; `alimTarihi` ile `bitisTarihi`
arasından hesaplanır.

## Depolama

Birincil depo **IndexedDB**. localStorage yerine tercih edilme sebebi
kapasite: fotoğraflar localStorage'ın tipik ~5 MB sınırını aşar.

Bazı tarayıcılar dosyadan açılan sayfalarda IndexedDB'yi engeller
(Firefox bunu her zaman yapar, iOS bazı durumlarda). Bu yüzden depo
katmanı üç kademelidir: IndexedDB açılamazsa localStorage'a düşer,
o da yoksa yalnızca bellekte çalışır ve kullanıcı verinin
kaydedilmediği konusunda açıkça uyarılır. Hangi kademede çalışıldığı
Yedek ekranında dürüstçe yazar; localStorage kademesinde kullanıcıya
alanın sınırlı olduğu ve sık yedek alması gerektiği söylenir.

Yedekleme, veri kaybına karşı asıl korumadır:

- **Yedek al** — tüm koleksiyonu, fotoğraflar dahil, tek bir JSON
  dosyası olarak indirir. Dosya adı yedeğin tarihini taşır
  (`oje-defteri-yedek-YYYY-AA-GG.json`). İçinde bir sürüm alanı
  bulunur, böylece ileride biçim değişirse eski yedekler tanınabilir.
- **Yedekten yükle** — o dosyadan koleksiyonu geri getirir. Telefon
  değiştirildiğinde taşıma yolu da budur.
- Son yedeğin tarihi IndexedDB'de ayrı bir ayar kaydında tutulur. Son
  yedekten 14 gün geçtiyse ana ekranın üstünde yedek almayı hatırlatan
  bir şerit görünür. Şerit kapatılabilir; uyarı bir sonraki eşikte
  tekrar çıkar. Koleksiyon boşken şerit hiç gösterilmez.

## Ekranlar

### 1. Koleksiyon (ana ekran)

Renk kutucuklu ızgara. Telefonda iki–üç sütun, geniş ekranda daha
fazla. Her kutucukta: fotoğraf varsa fotoğraf, yoksa `renk` alanının
dolu kutucuğu; altında marka, isim ve durum rozeti.

Koleksiyon henüz boşken ızgara yerine karşılama ekranı çıkar: ne işe
yaradığını bir cümleyle anlatır, "İlk ojeyi ekle" düğmesini ve
"Yedekten yükle" seçeneğini gösterir — ikincisi telefon değiştiren
kullanıcının aradığı ilk şeydir.

Üstte filtre şeridi:

- Arama kutusu (marka, isim ve notta arar)
- Duruma göre filtre
- Markaya göre filtre (mevcut kayıtlardan türetilir)
- Renk ailesine göre filtre
- Sıralama: son eklenen (varsayılan), alım tarihi, marka, renk tonu

Filtre sonucu boşsa neyin filtrelendiğini söyleyen ve filtreyi
temizlemeyi öneren bir mesaj gösterilir.

### 2. Detay / düzenleme

Kutucuğa dokununca açılır. Tüm alanlar düzenlenebilir. Fotoğraf
telefon kamerasından çekilebilir veya galeriden seçilebilir. Silme
işlemi onay ister.

Durum `bitti` veya `atildi` seçildiğinde bitiş tarihi alanı görünür
olur; başka durumlarda gizlenir.

### 3. Yeni oje ekleme

Detay ekranının boş hali. Yalnız renk zorunludur — kullanıcı
markasını hatırlamıyorsa bile kaydı oluşturup sonra tamamlayabilir.

### 4. Özet

- Toplam oje sayısı
- Toplam harcama (fiyatı girilmiş kayıtlar üzerinden; kaç kaydın
  fiyatsız olduğu belirtilir)
- Duruma göre dağılım
- En çok sahip olunan markalar
- "6 aydır açılmamış" listesi
- Biten ojeler için ortalama dayanma süresi

## Barkod ve otomatik doldurma

Amaç, yazmayı en aza indirmek. Barkod okuma tek başına ürün adını
getirmez — barkod yalnız bir numaradır ve Türkiye'deki oje markaları
açık ürün veritabanlarında çoğunlukla kayıtlı değildir. Bu yüzden
barkodun değeri başka yerlerdedir:

**Mağaza sorusu — "bu bende var mı?".** Ana ekrandaki tarama düğmesi
kamerayı açar. Okunan barkod koleksiyonda varsa o kaydı gösterir:
adı, durumu, ne zaman alındığı, üzerinden ne kadar geçtiği ve notu.
Yoksa bunu söyler ve tek dokunuşla eklemeyi önerir. Aynı ojeden bir
tane daha alınmış olabileceği için "yine de yeni kayıt ekle" yolu açık
bırakılır.

**Marka öğrenme.** Barkodun ilk yedi hanesi üreticiyi belirler. Kayıt
kaydedilirken bu önek ile marka eşleştirilip saklanır; sonraki
taramalarda aynı önek görülürse marka alanı kendiliğinden dolar ve
tahmin olduğu kullanıcıya söylenir. Eşleşme tablosu yedeğe dahildir.

**Ürün numarası öğrenme.** Bazı markalar ürün numarasını barkoda gömer:
Pastel 461 → 869064490**461**5, Pastel 457 → 869064490**457**8. Kullanıcı
saf sayıdan oluşan bir isim (3–5 hane) yazıp kaydettiğinde, o sayının
barkod içindeki yeri önekle birlikte saklanır; aynı önekli sonraki
barkodlarda numara oradan çıkarılıp önerilir. Desen bulunamazsa hiçbir
şey öğrenilmez — yanlış tahmin üretmektense sessiz kalmak yeğdir.

**Google'da arama.** Açık veritabanları Google kadar geniş değil: Pastel
461 kayıtlı, Pastel 28 değil. Bu yüzden hem sonuç ekranında hem kayıt
formunda barkodu Google'da aratan bir bağlantı durur. Kullanıcının zaten
elle yaptığı işi tek dokunuşa indirir; sonucu kendisi okuyup yazar.

Google'ın kendi verisini uygulamaya çekmek mümkün değil: Lens'in API'si
halka açık değil, arama sonuçlarını programla okumak da tarayıcı
güvenliği ve kullanım şartları nedeniyle yapılamaz. Ama Lens de bilgiyi
etiketten okuyor — aynısı yerelde yapılabilir.

## Etiketten bilgi doldurma

Kayıt formunun başında "Bilgileri kendi doldursun" bölümü iki yol sunar;
ikisi de aynı çözümleyiciden geçer, dolu alanların üzerine hiç yazılmaz.

**Fotoğraftan okuma (OCR).** Şişe etiketinin fotoğrafı çekilir, yazılar
okunup marka, numara, hacim, üretim ve son kullanma tarihi çıkarılır.
Okuma motoru (tesseract.js) sayfaya gömülmez, yalnız bu düğmeye
basılınca dışarıdan yüklenir — dosyayı şişirmemek için. Motor
yüklenemezse (internet yok) özellik kendini kapatır ve kullanıcı
yapıştırma yoluna yönlendirilir. Fotoğraf okumadan önce büyütülüp griye
çevrilir ve kontrastı açılır; küçük etiket yazılarında fark ediyor.

Telefon fotoğrafları 12 megapiksel gelir. İlk sürümde ölçekleme
`max(1, hedef/enBüyükKenar)` yazıldığı için büyük fotoğraflar hiç
küçültülmüyor, okuyucuya ham hâlleriyle gidiyor ve sonuç boş dönüyordu.
Sentetik test görüntüleri küçük olduğundan hata testlerde görünmemişti.
Uzun kenar artık hedefe çekilir (küçültme de büyütme de).

Tek geçiş yerine birkaç ayar denenir (düz metin bloğu, kontrastı açılmış
seyrek metin, daha küçük ölçek) ve sonuçlar birleştirilir; gerçek
fotoğrafta hangisinin tutacağı önceden bilinemiyor. İlk geçiş zaten
doyurucuysa kullanıcı bekletilmez.

OCR satır başlarına çöp bırakır ("_ 190", "om Coffee Bean"). Çözümleyici
satır kenarlarındaki harf/rakam olmayanları atar ve renk adından yalnız
büyük harfle başlayan sözcükleri alır. Numara ile ad hem alt alta hem
aynı satırda aranır; forma "190 Coffee Bean" biçiminde birleşik yazılır.

**Okunan yazı gösterilir.** Çıkarım başarısız olsa bile ham metin
katlanabilir bir alanda görünür: kullanıcı neyin okunduğunu görür ve
gerekirse bilgiyi kendisi alır. Sessiz başarısızlık teşhis edilemiyordu.

Sınır: etiket üzerinde kutu içine alınmış izole ürün numarası (Pastel'in
"28"i gibi) ve dikey basılmış barkod rakamları okunmuyor. Bu kabul
edildi, çünkü aynı bilgi başka yollardan gelebiliyor: barkod taraması,
barkod deseni ve Google'dan yapıştırma.

**Google'dan yapıştırma.** Lens çıktısı ("Marka: Pastel / Renk Numarası:
28 / Miktar: 13 ml / Üretim Tarihi (Prd): 01/2020 …") yapıştırılır,
alanlar dolar. OCR'ın tutmadığı durumlarda kesin çalışan yol budur.

**Alan açılmayan bilgiler nota yazılır.** Hacim ve tarihler için ayrı
alan açılmadı; "13 ml · Üretim 01/2020 · Son kullanma 01/2025 (süresi
geçmiş)" biçiminde nota eklenir. Süresi geçmiş olma durumu hesaplanıp
yazılır.

Çözümleyici tuzaklara karşı korunmuştur: "13 ml" satırı "775 Leafy
Green" kalıbına benzediği için ölçü birimleri ve çok kısa sözcükler
elenir; yıl gibi görünen dört haneli sayılar ürün numarası sayılmaz.

**İnternetten ad sorma.** Barkod okunduğunda iki açık ürün
veritabanı sırayla denenir (kozmetik, sonra genel). Türk oje markalarının
orada kayıtlı olmayacağı varsayılmıştı; gerçekte kayıtlılar — örneğin
Pastel 461 tam adıyla dönüyor. Bu yüzden arama hem "koleksiyona ekle"
formunda hem de "bu oje sende yok" ekranında çalışır ve sonucu
görünür şekilde bildirir: bulundu, kayıtlı değil, ya da internet yok.
Sessiz başarısızlık kullanıcıya arama hiç yapılmıyormuş gibi geliyordu.

Gelen ad genellikle "Pastel Nail Polish Oje No: 461" biçimindedir;
marka adı ve genel ürün sözcükleri ayıklanarak "461"e indirgenir.
Yalnız boş alanlar doldurulur; kullanıcının yazdığının üzerine yazılmaz.

**Fotoğraftan renk.** Fotoğraf eklendiğinde şişenin ortasına bakılıp
baskın renk bulunur ve renk alanına yazılır. Cam parlaması, beyaz zemin
ve etiket elenir. Renksiz ojelerde (siyah, beyaz, gri) en sık tekrar
eden ton seçilir — burada ortanca parlaklık yanıltıcıdır, beyaz bir
şişede etiket yazısı sonucu siyaha çeker. Kullanıcı rengi kendisi
seçtiyse fotoğraf onu ezmez.

**Okuma yöntemi.** Kareler video akışından kendimiz alınır: nişan
çerçevesine karşılık gelen yatay şerit bir canvas'a kırpılıp okunur.
Kütüphanenin kendi akış yönetimi (`decodeFromStream`) iPhone'da
çalışmıyordu; ayrıca sarmalayıcının canvas alan yöntemleri bu sürümde
ya yok (`decodeFromCanvas`) ya da canvas kabul etmiyor (`decode`). Bu
yüzden ZXing'in çekirdek API'si kullanılır:
`HTMLCanvasElementLuminanceSource` → `HybridBinarizer` → `BinaryBitmap`
→ `MultiFormatReader.decode`. Kırpma hem hızlandırır hem isabeti artırır.

**Yedek yol: fotoğraftan okuma.** Canlı tarama tutmazsa kullanıcı tek
kare fotoğraf çeker ve aynı çözücüden geçirilir. Kamera ekranında bu
seçenek ile "numarayı yaz" seçeneği her zaman görünür durur.

**Tarayıcı desteği.** Önce tarayıcının yerleşik barkod okuyucusu
denenir (Android Chrome'da mevcut ve hızlıdır); yoksa dosyaya gömülü
ZXing devreye girer. Böylece iPhone dahil her telefonda ve internetsiz
çalışır. Kamera açılamazsa (izin yok, kamera yok veya sayfa `file://`
üzerinden açılmış) sebebi Türkçe olarak söylenir ve numarayı elle yazma
yolu sunulur — tarama hiçbir zaman tek yol değildir.

## Fotoğraf işleme

Seçilen görsel, kaydedilmeden önce tarayıcıda yeniden boyutlandırılır:
uzun kenar en fazla 800 piksel, JPEG olarak sıkıştırılır. Amaç hem
telefonda yer kaplamamak hem de yedek dosyasını makul boyutta tutmak.
100 kayıt bu ayarla yaklaşık 5–8 MB'lık bir yedek dosyası üretir.

## Hata durumları

| Durum | Davranış |
|---|---|
| IndexedDB açılamıyor (gizli sekme, izin yok) | Uygulama açılır ama üstte kalıcı uyarı: veriler kaydedilemiyor, yapılanlar kaybolacak |
| Depolama alanı doldu | Kayıt işlemi durur, Türkçe uyarı çıkar ve kullanıcı hemen yedek almaya yönlendirilir; sessiz kayıp olmaz |
| Yedek dosyası bozuk veya farklı biçimde | İçeri alınmaz, mevcut koleksiyona dokunulmaz, hata açıkça söylenir |
| Fotoğraf okunamıyor | Kayıt fotoğrafsız kaydedilir, kullanıcı bilgilendirilir |

Yedekten yükleme mevcut koleksiyonun üzerine yazar; bu nedenle işlem
öncesi ne olacağını söyleyen bir onay istenir.

## Test

Tarayıcıda gerçek akışlar denenecek:

1. Boş durumdan oje ekleme
2. Fotoğraflı kayıt ekleme ve fotoğrafın küçültüldüğünün doğrulanması
3. Arama, her filtre türü ve her sıralama seçeneği
4. Durum değiştirme ve bitiş tarihi alanının görünüp kaybolması
5. Sayfa yenilendikten sonra verinin durduğunun doğrulanması
6. Yedek alma, verinin temizlenmesi, yedekten geri yükleme
7. Bozuk yedek dosyasının reddedildiğinin doğrulanması
8. Telefon genişliğinde görünüm

## Kapsam dışı

Bu sürümde yapılmayacaklar: çoklu kullanıcı, cihazlar arası
senkronizasyon, alışveriş listesi/istek listesi, barkod okuma, renk
eşleştirme önerisi, sürülmüş hâlin denenmesi (swatch) takvimi.

## Yayın

Uygulama https://sozatici.github.io/oje-defteri/ adresinde yayında.
Kaynak: github.com/sozatici/oje-defteri (herkese açık depo — GitHub'ın
ücretsiz planında Pages yalnız açık depolardan yayınlanır; uygulama kodu
görünür, kullanıcı verisi depoda değil telefonda durur).

`site/` klasörü her değiştiğinde GitHub Actions iş akışı
(`.github/workflows/pages.yml`) siteyi kendiliğinden yeniden yayınlar.
Yani sürüm çıkarmak için `python build.py` çalıştırıp commit'lemek yeterli.

Yayınlanmış sürüm güvenli adres (`https://`) üzerinden açıldığı için
kamera erişimi mümkündür; barkod tarama yalnız burada çalışır. Telefona
kopyalanan tek dosya sürümünde tarama yerine numara elle yazılır.
