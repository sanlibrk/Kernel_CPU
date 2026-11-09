# 2209-A 2026 — Gecikme Odaklı CPU Zamanlama

**Yürütücü:** Burak Şanlı
**Kurum:** Harran Üniversitesi · Bilgisayar Mühendisliği
**Akademik danışman:** Prof. Dr. Dursun Akaslan
**Kapsam:** Bireysel araştırma önerisi · Altı aylık geliştirme ve deney planı

Proje, kısa etkileşimli görevlerle CPU yoğun arka plan işlerinin birlikte
çalıştığı koşullarda gecikme ve ilerleme dengesini araştırır. Başvuru için etkin
belge, bilimsel gerekçeyi, akademik literatür karşılaştırmasını, politika
tasarımını ve deney yöntemini sunan **araştırma önerisidir**. Mevcut çalışma
durumunu sonuç raporu şablonunda açıklayan ayrı rapor aşağıda korunur.

## Başvuru için etkin araştırma önerisi

| Belge | Kullanım |
|---|---|
| [Araştırma önerisini Word olarak indir](https://raw.githubusercontent.com/sanlibrk/Kernel_CPU/main/docs/basvuru/2209a/2209A_Burak_Sanli_Arastirma_Onerisi.docx) | Düzenlenebilir başvuru belgesi. |
| [Araştırma önerisini PDF olarak aç](2209A_Burak_Sanli_Arastirma_Onerisi.pdf) | Sayfa düzeni korunmuş inceleme kopyası. |
| [Araştırma önerisi metnini oku](2209A_Burak_Sanli_Arastirma_Onerisi.md) | Word ve PDF'in üretildiği ana metin. |
| [Araştırma önerisinin uygunluk kontrolleri](uygunluk_kontrolu.json) | Belge üzerinde hesaplanan içerik ve biçim kontrolleri. |
| [Kullanılan araştırma önerisi biçim şablonu](sablon/2209A_Arastirma_Onerisi_Formati.docx) | Paylaşılan örneklerden kimlik ve proje içerikleri çıkarılarak türetilmiş kapak ve boş tablolar. |

Başvuru dosyası, paylaşılan örneklerin kapak ve çerçeveli içerik düzenine
aktarılmıştır. Arial 9 gövde yazısı, beş sütunlu iş-zaman çizelgesi, üç sütunlu
risk tablosu, araştırma olanakları, yaygın etki ve bütçe çizelgeleri kullanılır.
Çok yazarlı akademik kaynağa metin içinde **Goel vd. (2002)** biçiminde atıf
yapılır; kaynakçada yazarlar tam listelenir. Kurumsal yazarlı çekirdek
belgelerinde kurum adı korunur.

Etkin başvuru dosyaları `2209A_Burak_Sanli_Arastirma_Onerisi` adıyla tutulur.
Bilimsel katkı belirli bir kural bileşiminin uygulanması ve değerlendirilmesidir;
literatürde ilk algoritma, doğrulanmış genel performans kazancı veya tamamlanmış
çekirdek entegrasyonu iddiası kurulmaz.

## Bilimsel içerik ve ön çalışma

Öneri; mevcut yaklaşımlarla karşılaştırmayı, bütçe ve yaşlandırma parametrelerinin
gerekçesini, politika sözde kodunu ve karar akışını birlikte açıklar. Araştırma
sorusu, ölçülebilir hedefler, kontrol sürümleri ve değerlendirme ölçütleri bu
tasarıma bağlanır. Gerçekleşen ön çalışmalar şunlardır:

- C tabanlı zamanlama modeli ve gerçek Linux başlangıç ölçüm programı geliştirilmiştir.
- İlk deney grubunda 13 test yöntemi, altı model koşusu ve toplam 240 kısa iş
  gözlemi içeren altı gerçek Linux koşusu tamamlanmıştır.
- 5 Kasım 2026 tarihli Debian/Linux deneyleriyle Ubuntu/WSL üzerinde doğrulanan
  yerel C derlemesi ve 13 test birbirinden ayrılır.
- Haftalık belgeler, teknik açıklamalar, deney arşivi ve sunum materyalleri hazırlanmıştır.
- Özel zamanlama politikası henüz çekirdeğe yüklenmemiştir; model bulguları
  Linux üzerinde politika kazancı olarak sunulmaz.

## Altı aylık geliştirme ve değerlendirme planı

| Aşama | Planlanan kapsam | Ölçüt |
|---|---|---|
| Ana gecikme deneyleri | 4 hücre × 10 eşleştirilmiş blok × 2 politika = 80 koşu | Koşu başına en az 1.000 kısa görev; P95 gecikme, sürekli arka plan ilerlemesi ve maliyet. |
| Ana saf arka plan deneyleri | 2 hücre × 10 blok × 2 politika = 40 koşu | Aynı sabit hesaplama işinin bitişi, işlem hacmi ve bireysel ilerleme; kısa görev/P95 şartı uygulanmaz. |
| Mekanizma kontrolleri | 2 karma yük × 3 ek kontrol × 5 blok × 2 koşu = 60 koşu | FIFO referansı, yaşlandırmasız sürüm ve bütçe sınırı kaldırılmış sürüm. |
| Pilot ve işlevsel doğrulama | Ana verilerden ayrı | Ortam, güvenli geri dönüş, kayıt ve izleme kalibrasyonu. |

Planlanan araştırma **120 ana + 60 ikincil deney koşusundan** oluşur; pilot ve
kod doğrulama çalışmaları bu sayının dışındadır. İlk iki haftanın mevcut
13 test/240 başlangıç gözlemi bu gelecekteki deneylerle karıştırılmaz.
Parametre pilotunda yedi ayar için 21 deterministik model çalıştırması ve en
fazla 56 gerçek koşu planlanır. Bu pilotlar henüz yapılmış sonuç değildir ve
180 ana/ikincil koşuya dahil edilmez.

## Altyapı ve uygulanabilirlik

Yürütücünün doğruladığı kişisel bilgisayar i7-12650H işlemci ve yaklaşık
15,7 GiB RAM içerir. Ubuntu/WSL üzerinde C derlemesi ve 13 test başarılıdır.
Hedef test misafirine 2 sanal CPU ve 4 GiB RAM ayrılması planlanır; bu, kurulmuş
misafir veya doğrulanmış çekirdek desteği olarak sunulmaz. Yapılandırılmış ayrı
çekirdek ve gerektiğinde yazılımsal emülasyon B planıdır. Yürütme kipleri aynı
karşılaştırma veri grubunda karıştırılmaz.

## Kaynaklar ve başvuruya aktarım

- [Araştırma önerisi için TYBS aktarım rehberi](tybs_aktarim_rehberi.md)
- [Başvuru öncesi resmî işlem kontrol listesi](basvuru_kontrol_listesi_2026.md)
- [Doğrulanan kaynaklar ve erişim kaydı](kaynak_dogrulama.md)
- [Araştırma önerisinin ayrı PNG ekleri](ekler/README.md)

Kaynaklar, okunan Time-Sensitive Linux makalesi ve resmî çekirdek deposunun
sabit sürüm belgeleridir. SCHED_DEADLINE/EDF/CBS karşılaştırması, tercih
bütçesinin gerçek zaman rezervasyonu sayılmamasını açıklar. İncelenen metinlerde
sunulmayan DOI numaraları üretilmemiştir.
TÜBİTAK'ın bağlantılı kaynakça web sayfasına erişim kısıtı bulunduğu için o
sayfanın güncel biçiminin bağımsız kontrol edildiği iddia edilmez.

**Resmî işlem durumu:** Belge düzenlemesi, TYBS'ye gönderim veya onay anlamına
gelmez. Sistem ön izlemesi, uygunluk beyanları, bütçe girişinin kabulü, danışman
onayı ve kuruluş yetkilisi e-imzası ilgili sistemlerde doğrulanmalıdır.
Bu idari kontroller, bilimsel içeriğin belge üzerinde doğrulanmasından ayrıdır.

9 Kasım'da paylaşılan [yerel WSL terminal kaydı](../../../experiments/hafta2/2026-11-09-wsl/README.md)
da ön çalışma olarak eklenmiştir. Tam otomatik grubun ham dosyaları henüz
paylaşılmadığı için terminalde görünen başarı bilgisi ile bağımsız olarak
yeniden hesaplanmış ham veri ayrımı korunur.

## Ayrı belge: mevcut çalışma durumu raporu

9 Kasım 2026 tarihli rapor, sağlanan sonuç raporu şablonunun kapak, iki özgün
tablo ve imza alanlarını kullanarak gerçekleşen çalışmaları ve kalan planı
açıklar. Bu belge başvuru araştırma önerisinin yerine geçmez; tamamlanmış bir
projenin resmî kapanış bildirimi değildir.

| Belge | Kullanım |
|---|---|
| [Mevcut durum raporu — Word](https://raw.githubusercontent.com/sanlibrk/Kernel_CPU/main/docs/basvuru/2209a/2209A_Burak_Sanli_Proje_Raporu.docx) | Özgün sonuç raporu şablonunda doldurulan ayrı rapor. |
| [Mevcut durum raporu — PDF](2209A_Burak_Sanli_Proje_Raporu.pdf) | Mevcut çalışma aşamasının okuma kopyası. |
| [Mevcut durum raporu metni](2209A_Burak_Sanli_Proje_Raporu.md) | Gerçekleşen çalışmalar, çıktılar, harcamalar ve kalan plan. |
| [Özgün sonuç raporu şablonu](sablon/2209-a_sonuc_raporu_formati.docx) | Raporun temel aldığı, ayrı saklanan Word şablonu. |
| [Mevcut durum raporunun kontrolleri](rapor_kontrolu.json) | Şablon, içerik ve üretilen dosyalara ilişkin kontroller. |

Yürütücünün beyanına göre rapor tarihine kadar gerçekleşen proje gideri 0 TL'dir.
Resmî proje başlangıç/bitiş tarihleri ve imza tarihi kesinleşmiş olarak girilmez;
imza alanları imzalanmış gösterilmez. Bu gider beyanı, destek bütçesinin program
veya sistem tarafından kabul edildiği anlamına gelmez.

## Belgeleri yeniden üretme

İki belge setinin üreticileri ve kontrol kayıtları ayrıdır. İlgili ana metin
değiştiğinde o belgenin Word ve PDF dosyaları birlikte yeniden üretilir.
C programlarının çalışması bu belge bağımlılığına bağlı değildir.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-documents.txt
```

Araştırma önerisini Word ve PDF olarak üretmek için:

```bash
python3 scripts/build_2209_application.py --pdf
```

Özgün sonuç raporu şablonundan mevcut durum raporunu üretmek için:

```bash
python3 scripts/build_2209_report.py --pdf
```

PDF üretimi ayrıca kurulu LibreOffice gerektirir. Üreticiler resmî sisteme
bağlanmaz ve yeni deney yürütmez. Araştırma önerisinin kontrolleri
`uygunluk_kontrolu.json`, mevcut durum raporunun kontrolleri `rapor_kontrolu.json`
dosyasındadır. Sonuç raporu şablonunun kullanılması, araştırma önerisi ve resmî
başvuru gereklerini değiştirmez.
