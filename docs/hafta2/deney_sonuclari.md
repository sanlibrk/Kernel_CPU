# Hafta 2 — Deney yöntemi ve ilk sonuçlar

## Amaç ve veri kaynağı

Bu deney grubu iki ayrı soruyu ele almaktadır:

1. C tabanlı modelde bütçe ve yaşlandırma kuralları, aynı görev kümesindeki
   Round Robin referansına göre yanıt ve bekleme sürelerini nasıl değiştirmektedir?
2. Mevcut Linux zamanlayıcısı altında, aynı CPU'da arka plan yükü bulunduğunda
   periyodik kısa işin uyanma gecikmesi nasıl gözlenmektedir?

Özel politika gerçek Linux ölçümünde kullanılmamıştır. İki deneyin ölçütleri ve
referansları farklıdır; sonuçları birleştirerek Linux'a karşı performans artışı
hesaplanamaz.

Veri grubu **5 Kasım 2026, 23.11 (Türkiye saati)** tarihinde başlatılmıştır.
[Ham kayıtlar](../../experiments/hafta2/2026-11-05),
[ortam ve sonuç özeti](../../experiments/hafta2/2026-11-05/summary.json) ve
[test günlüğü](../../experiments/hafta2/2026-11-05/tests.txt) arşivlenmiştir.
Kaynak kodların bu deneyde kullanılan içeriği ilk uygulama
[commit'inde](https://github.com/sanlibrk/Kernel_CPU/commit/52ab344a5285801d61d806fcba96734222f4b4da)
bulunmaktadır. Sonraki belge düzenlemeleri uygulama kodunu değiştirmemiştir.

## Ortam ve kontroller

| Özellik | Kaydedilen değer |
|---|---|
| Dağıtım | Debian GNU/Linux 13 (trixie) |
| Çekirdek | Linux 6.18.57 |
| Mimari | x86_64 |
| Derleyici | GCC 14.2; C11, `-O2 -g -Wall -Wextra -Werror -pedantic` |
| İzinli CPU'lar | 0–4 |
| Gerçek ölçümde seçilen CPU | 0; ana süreç ve işçiler aynı CPU'ya sabitlendi |
| Konteyner CPU kotası | `cpu.max = 400000 100000`; 100 ms dönem başına 400 ms toplam CPU zamanı |
| Bellek üst sınırı | 34.359.738.368 bayt, 32 GiB |
| Zamanlama politikası | `SCHED_OTHER`; varsayılan adil sınıfın iç algoritması ayrıca izlenmedi |
| Özel zamanlayıcı yükleme durumu | Yüklenmedi; ilk doğrulama ortamında sched_ext/BTF arayüzleri görünmüyordu |

CPU kotası konteynerin toplam sınırıdır; tek CPU'ya sabitlenen bu programın dört
CPU üzerinde paralel çalıştığı anlamına gelmez. Makine paylaşımlı/sanallaştırılmış
bir ortamdır. Ana makinenin tüm yükü ve frekans yönetimi deney tarafından kontrol
edilmemektedir. `cpu.stat` kaydı deneyin başında alınmıştır; koşu boyunca
kısıtlanma yaşanmadığını kanıtlayan bir son ölçüm olarak yorumlanmamalıdır.

## Otomatik kontroller

Kaydedilen test çalıştırmasında **13 test yöntemi başarılı**, **0 başarısız**,
**0 atlanan test** vardır. Kontroller şunları kapsamaktadır:

- Tek görev, başlangıçta boş CPU ve bilinen iki görevli RR takvimi.
- Giriş satır sırasından bağımsız görev kabulü.
- Kontrollü örnekte etkileşimli tercih, bütçe sonrası arka plan ilerlemesi ve yaşlandırma.
- Yalnız etkileşimli işlerde gereksiz CPU boşluğu oluşmaması.
- Seçilen yalnız arka plan örneğinde iki politikanın aynı sonucu vermesi.
- Sabit tohumlu 20 iş yükünün iki politikayla çalıştırılması; bitiş, CPU toplamı
  ve görev bazında süre eşitliklerinin kontrolü.
- Hatalı görev/parametre girişlerinin reddi.
- 0 ve 2 gerçek Linux işçisiyle kısa fonksiyonel ölçüm; tüm örneklerin ve işçi
  bitiş kayıtlarının oluşması, CPU bütçesi ve gecikme alanlarının tutarlılığı.

Bu kontroller seçilen örnekleri doğrular; tüm olası yüklerde adalet, sonsuz görev
akışında açlık oluşmaması veya çekirdek entegrasyonunun doğruluğu için kanıt değildir.

## Model deneyleri

Ortak parametreler: 4 ms zaman dilimi, 20 ms sabit bütçe penceresi, pencere başına
8 ms etkileşimli tercih bütçesi ve 20 ms yaşlandırma eşiği. Model tek CPU üzerinde
1 ms adımlarla ilerler. Görevler tek CPU patlamasına sahiptir; I/O ve bağlam
değiştirme maliyeti yoktur. Aynı girdi ve parametreler deterministik sonuç verir.

| Senaryo | Görev kümesi | Toplam CPU ihtiyacı |
|---|---|---:|
| `cpu_only` | 0. ms'de gelen, her biri 120 ms'lik 3 arka plan görevi | 360 ms |
| `mixed` | 3 × 120 ms arka plan; 5–75 ms arasında 10 ms aralıkla gelen 8 × 2 ms etkileşimli görev | 376 ms |
| `interactive_pressure` | 3 × 80 ms arka plan; 0–22 ms arasında 2 ms aralıkla gelen 12 × 20 ms etkileşimli görev | 480 ms |

Aşağıdaki tüm zamanlar milisaniyedir. `Yanıt`, varıştan ilk çalışmaya kadar geçen
süredir. `Bekleme`, tüm hazır beklemelerin toplamıdır. Arka plan dönüş süresi,
varıştan tamamlanmaya kadar geçen süredir. `Bitiş`, modelin son görev tamamlanma
anıdır. Tablo değerleri üç ondalığa yuvarlanmıştır; CSV kayıtları tam ms değerlerini içerir.

| Senaryo | Politika | Etkileşimli ort. yanıt | Etkileşimli P95 yanıt | Etkileşimli ort. bekleme | Arka plan ort. dönüş | Bitiş |
|---|---|---:|---:|---:|---:|---:|
| `cpu_only` | RR | — | — | — | 356.000 | 360 |
| `cpu_only` | Prototip | — | — | — | 356.000 | 360 |
| `mixed` | RR | 11.000 | 11 | 11.000 | 372.000 | 376 |
| `mixed` | Prototip | 3.000 | 3 | 3.000 | 372.000 | 376 |
| `interactive_pressure` | RR | 31.333 | 54 | 252.667 | 476.000 | 480 |
| `interactive_pressure` | Prototip | 19.333 | 33 | 303.833 | 476.000 | 480 |

Karışık iş yükünde prototipin ilk yanıt süresi daha düşüktür. Ancak yoğun
etkileşimli senaryoda ilk yanıt iyileşirken toplam bekleme **artmaktadır**.
Bu fark, ilk kez CPU'ya erişmekle işin tümünü tamamlamanın ayrı hedefler olduğunu
göstermektedir. Son görev bitişinin aynı kalması bu modelde aynı toplam CPU işinin
boşluk olmadan yürütülmesiyle uyumludur; gerçek sistemde işlem hacmi kazancı değildir.

Tüm model görevleri bu sonlu örneklerde tamamlanmıştır. Bunun bütün iş yükleri
için kesin bir açlık önleme garantisi olduğu sonucuna varılamaz.

## Gerçek Linux başlangıç ölçümleri

Her tekrarda önce 0, ardından 2 arka plan işçisi koşulu çalıştırılmıştır. Üç tekrar
vardır; her koşuda aynı ana sürecin 40 periyodik kısa CPU patlaması ölçülmüştür.
Kısa iş periyodu 20 ms, hedef CPU süresi 500 µs, her arka plan işçisinin CPU
bütçesi 800 ms'dir. Süreler, sabit sayıda hesaplama işlemi yerine süreç CPU saati
ile sınırlandırılmıştır. Bu nedenle iş yükü bir sabit iş miktarı/işlem hacmi deneyi değildir.

İşçiler bir boru üzerinden serbest bırakılır; tam olarak aynı anda başladıkları
garanti edilmez. İlk kısa işin hedefi, serbest bırakmadan sonraki yaklaşık 20 ms'dir.
Uyandırma hedefleri mutlak monoton zamanla belirlenir. Ayrı bir kalibrasyon veya
atılan ısınma örnekleri yoktur; koşul sırası rastgeleleştirilmemiştir.

**Uyanma gecikmesi:** ana sürecin çalışmaya dönme anı − planlanan uyanma anı.
Bu ölçüm zamanlayıcı, timer/uyandırma maliyeti ve sanallaştırma etkilerini kapsar;
doğrudan çekirdek çalışma kuyruğu izleme ölçümü değildir.

Tüm tablo değerleri ms'dir. P50/P95, sıralı 40 örnekte `ceil(p × 40)` sırasındaki
örnektir. Her tekrar kendi içinde özetlenmiştir; tekrarların yüzdelikleri tek bir
birleşik yüzdelik olarak sunulmamıştır.

| Tekrar | Arka plan işçisi | Ort. uyanma gecikmesi | P50 | P95 | En büyük |
|---|---:|---:|---:|---:|---:|
| 1 | 0 | 0.165194 | 0.147260 | 0.289082 | 0.414238 |
| 1 | 2 | 1.095446 | 0.891242 | 2.821243 | 3.340732 |
| 2 | 0 | 0.109157 | 0.106461 | 0.129169 | 0.158034 |
| 2 | 2 | 1.122841 | 0.855589 | 2.969053 | 3.215313 |
| 3 | 0 | 0.133546 | 0.114232 | 0.165647 | 0.664773 |
| 3 | 2 | 1.099902 | 0.920860 | 2.771535 | 3.203890 |

Arka plan işçilerinin tamamlanma süreleri:

| Tekrar | İşçi 0 duvar saati | İşçi 1 duvar saati | Her işçinin CPU hedefi |
|---|---:|---:|---:|
| 1 | 1620.925871 | 1620.596351 | 800 ms |
| 2 | 1624.659203 | 1622.225022 | 800 ms |
| 3 | 1623.205389 | 1621.255906 | 800 ms |

Her işçinin gerçekleşen CPU süresi, her kısa örneğin uyanma gecikmesi, tamamlanma
gecikmesi ve CPU süresi ilgili JSON dosyasında yer almaktadır. İşçilerin kendi
ölçtüğü duvar saati süreleri kullanılmıştır; ana sürecin `waitpid` dönüş zamanı
işçi tamamlanma süresi olarak alınmamıştır.

Bu üç tekrarda arka plan yükü varken gözlenen uyanma gecikmeleri daha yüksektir.
Ancak az sayıda tekrar ve kontrol edilmeyen ortam etkileri nedeniyle sonuçlardan
genel bir oran, güven aralığı veya yalnızca zamanlayıcıya ait nedensellik çıkarılamaz.
Özel politika uygulanmadığı için bu veriler onun Linux üzerindeki başarısını ölçmez.

## Tekrarlama ve arşiv bütünlüğü

Deponun kök dizininde:

```bash
make experiment
```

Bu komut mevcut ortamda yeni veri toplar. Gerçek zaman ölçümlerinin sayısal olarak
aynı olması beklenmez; aynı model girdileri ve parametreleri aynı model sonuçlarını
üretmelidir. Komut yeni kayıtları `results/` altına yazar, yayımlanmış arşivin
üzerine yazmaz.

Arşivin `summary.json` dosyası deney anındaki kaynak dosyalarının SHA-256 özetlerini
saklar. Belge düzenlemeleri bu eski özetleri değiştirmez; güncel belgeler ile tarihsel
manifestin farklı olması uygulama kodunun değiştiği anlamına gelmez. Arşivdeki
`sha256sums.txt` listelenen veri dosyalarının bütünlüğünü kontrol etmek içindir:

```bash
cd experiments/hafta2/2026-11-05
sha256sum -c sha256sums.txt
```

## Sonraki değerlendirme aşaması

Önce ekip çekirdeği, `sched_ext`/BTF desteği ve ayrı test sanal makinesi
kesinleştirilecektir. Yükleme ve güvenli geri dönüş deneyi sonrasında özel politika
aynı gerçek iş yükleriyle karşılaştırılabilir. Daha fazla tekrar, koşul sırasının
kontrolü, CPU dışı darboğazların ayrıştırılması, uzun işlerin ilerleme ölçütleri
ve politika maliyetinin ölçülmesi sonraki deneylerin kapsamındadır.
