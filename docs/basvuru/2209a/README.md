# 2209-A — CPU Zamanlama Proje Raporu

**Yürütücü:** Burak Şanlı
**Kurum:** Harran Üniversitesi · Bilgisayar Mühendisliği
**Akademik danışman:** Prof. Dr. Dursun Akaslan
**Rapor tarihi:** 9 Kasım 2026
**Kapsam:** Mevcut çalışma aşaması · Bireysel bitirme projesi · Altı aylık plan

Proje, kısa etkileşimli görevlerle CPU yoğun arka plan işlerinin birlikte
çalıştığı koşullarda gecikme ve ilerleme dengesini araştırır. Güncel rapor,
sağlanan **2209-A sonuç raporu şablonu** üzerinde hazırlanır; özgün kapak,
iki tablo ve imza alanları korunur. Tamamlanan ön çalışmalar ile planlanan
çekirdek entegrasyonu ve karşılaştırmalar açıkça ayrılır.

Bu belge mevcut çalışma durumunu raporlar; bütün projenin tamamlandığı veya
resmî sonuç raporunun gönderilip onaylandığı iddiasını içermez.

## Güncel proje raporu

| Belge | Kullanım |
|---|---|
| [Word raporunu indir](https://raw.githubusercontent.com/sanlibrk/Kernel_CPU/main/docs/basvuru/2209a/2209A_Burak_Sanli_Proje_Raporu.docx) | Özgün şablon üzerinde doldurulan düzenlenebilir proje raporu. |
| [PDF raporunu aç](2209A_Burak_Sanli_Proje_Raporu.pdf) | Sayfa düzeni korunmuş okuma ve inceleme kopyası. |
| [Rapor metnini oku](2209A_Burak_Sanli_Proje_Raporu.md) | Güncel çalışmaları, bulguları, çıktıları ve planı açıklayan metin. |
| [Özgün Word şablonunu indir](sablon/2209-a_sonuc_raporu_formati.docx) | Raporun temel alındığı, ayrı saklanan sonuç raporu şablonu. |
| [Rapor doğrulama kaydı](rapor_kontrolu.json) | Şablon, içerik ve üretilen rapor dosyalarına ilişkin kontroller. |

Etkin rapor dosyaları `2209A_Burak_Sanli_Proje_Raporu` adıyla tutulur. Önceden
hazırlanan araştırma önerisi farklı amacını korur ve aşağıdaki başvuru
referansları bölümünde listelenir.

## Gerçekleşen çalışmalar ve rapor kapsamı

- C tabanlı zamanlama modeli ve gerçek Linux başlangıç ölçüm programı geliştirilmiştir.
- İlk deney grubunda 13 test yöntemi, altı model koşusu ve toplam 240 kısa iş
  gözlemi içeren altı gerçek Linux koşusu tamamlanmıştır.
- 5 Kasım 2026 tarihli Debian/Linux deneyleriyle Ubuntu/WSL üzerinde doğrulanan
  yerel C derlemesi ve 13 test birbirinden ayrılır.
- Haftalık belgeler, teknik açıklamalar, deney arşivi ve sunum materyalleri hazırlanmıştır.
- Özel zamanlama politikası henüz çekirdeğe yüklenmemiştir; model bulguları
  Linux üzerinde politika kazancı olarak sunulmaz.

Şablonun giriş, proje konusu, dönem çalışmaları, sonuç, çıktılar ve harcama
başlıkları kullanılır. **Yürütücünün beyanına göre rapor tarihine kadar
gerçekleşen proje gideri 0 TL'dir.** Resmî proje başlangıç/bitiş tarihleri ve
imzalama tarihi kesinleşmiş bilgiler olarak girilmez; imza alanları imzalanmış
olarak gösterilmez.

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

## Altyapı ve uygulanabilirlik

Yürütücünün doğruladığı kişisel bilgisayar i7-12650H işlemci ve yaklaşık
15,7 GiB RAM içerir. Ubuntu/WSL üzerinde C derlemesi ve 13 test başarılıdır.
Hedef test misafirine 2 sanal CPU ve 4 GiB RAM ayrılması planlanır; bu, kurulmuş
misafir veya doğrulanmış çekirdek desteği olarak sunulmaz. Yapılandırılmış ayrı
çekirdek ve gerektiğinde yazılımsal emülasyon B planıdır. Yürütme kipleri aynı
karşılaştırma veri grubunda karıştırılmaz.

## Araştırma önerisi ve başvuru referansları

Araştırma önerisi, 2026 Başvuru İçeriği Bilgi Notu'ndaki alanlara göre hazırlanmış
ayrı bir belge setidir. Sonuç raporu şablonunun kullanılması, önerinin ve resmî
başvuru gereklerinin yerini almaz.

- [Araştırma önerisi metni](2209A_Burak_Sanli_Arastirma_Onerisi.md)
- [Araştırma önerisi Word dosyası](https://raw.githubusercontent.com/sanlibrk/Kernel_CPU/main/docs/basvuru/2209a/2209A_Burak_Sanli_Arastirma_Onerisi.docx)
- [Araştırma önerisi PDF dosyası](2209A_Burak_Sanli_Arastirma_Onerisi.pdf)
- [Araştırma önerisinin uygunluk kontrolleri](uygunluk_kontrolu.json)
- [Araştırma önerisi için TYBS aktarım rehberi](tybs_aktarim_rehberi.md)
- [Başvuru öncesi resmî işlem kontrol listesi](basvuru_kontrol_listesi_2026.md)
- [Doğrulanan kaynaklar ve erişim kaydı](kaynak_dogrulama.md)
- [Araştırma önerisinin ayrı PNG ekleri](ekler/README.md)

Kaynaklar resmî çekirdek deposunun sabit sürüm belgelerinden okunmuş ve atıflarla
eşleştirilmiştir. İncelenen kaynaklarda sunulmayan DOI numaraları üretilmemiştir.
TÜBİTAK'ın bağlantılı kaynakça web sayfasına erişim kısıtı bulunduğu için o
sayfanın güncel biçiminin bağımsız kontrol edildiği iddia edilmez.

**Resmî işlem durumu:** Belge düzenlemesi, TYBS'ye gönderim veya onay anlamına
gelmez. Sistem ön izlemesi, uygunluk beyanları, bütçe girişinin kabulü, danışman
onayı ve kuruluş yetkilisi e-imzası ilgili sistemlerde doğrulanmalıdır.
Gerçekleşen giderin 0 TL olması, destek bütçesinin program veya sistem tarafından
onaylandığı anlamına gelmez; başvuruya özgü bu kontrol ayrı yürütülür.

## Güncel raporu yeniden üretme

Rapor üreticisi ayrı saklanan özgün Word şablonunu kullanır. Rapor metni
değiştirildiğinde Word ve PDF birlikte yeniden üretilir. C programlarının
çalışması belge üretim bağımlılığına bağlı değildir.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-documents.txt
python3 scripts/build_2209_report.py
```

PDF üretimi için ayrıca kurulu LibreOffice gerekir:

```bash
python3 scripts/build_2209_report.py --pdf
```

Üretici resmî sisteme bağlanmaz ve yeni deney yürütmez. Güncel raporun kontrol
kaydı `rapor_kontrolu.json` dosyasıdır. Başvuruya ait özet kelime/karakter ve
takvim kontrolleri ise ayrı araştırma önerisinin `uygunluk_kontrolu.json`
dosyasında korunur. Araştırma önerisini yeniden üretmek için kullanılan
`scripts/build_2209_application.py`, o belge setine aittir.
