# 2209-A 2026 — CPU Zamanlama Araştırma Önerisi

**Yürütücü:** Burak Şanlı
**Kurum:** Harran Üniversitesi · Bilgisayar Mühendisliği
**Akademik danışman:** Prof. Dr. Dursun Akaslan
**Kapsam:** Bireysel bitirme projesi · Planlanan süre: 6 ay

Proje, kısa etkileşimli görevlerle CPU yoğun arka plan işlerinin birlikte
çalıştığı koşullarda gecikme ve ilerleme dengesini araştırır. Sınırlı tercih
bütçesi ve yaşlandırma kuralları, referans modelden uygun çekirdek altyapısına
aktarılacak; varsayılan zamanlama ile karşılaştırılacaktır.

## Güncel başvuru belgeleri

| Belge | Kullanım |
|---|---|
| [Word dosyasını indir](https://raw.githubusercontent.com/sanlibrk/Kernel_CPU/main/docs/basvuru/2209a/2209A_Burak_Sanli_Arastirma_Onerisi.docx) | Düzenlenebilir araştırma önerisi. |
| [PDF dosyasını aç](2209A_Burak_Sanli_Arastirma_Onerisi.pdf) | Sayfa düzeni korunmuş okuma ve inceleme kopyası. |
| [Başvuru metnini oku](2209A_Burak_Sanli_Arastirma_Onerisi.md) | Word ve PDF'in üretildiği tek ana metin. |

Bu dizinde tek bir güncel belge seti tutulur. Önceki sürümler Git geçmişindedir.

## Deney tasarımı

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

## Kurallar, kaynaklar ve aktarım

- [Belge üzerinde hesaplanan uygunluk kontrolleri](uygunluk_kontrolu.json)
- [TYBS aktarım rehberi ve alan eşleştirmesi](tybs_aktarim_rehberi.md)
- [Gönderim öncesi resmî işlem kontrol listesi](basvuru_kontrol_listesi_2026.md)
- [Doğrulanan kaynaklar ve erişim kaydı](kaynak_dogrulama.md)
- [Ayrı PNG ekleri](ekler/README.md)

Bölüm düzeninde yürütücünün sağladığı 2026 Başvuru İçeriği Bilgi Notu esas
alınmıştır. Kaynaklar resmî çekirdek deposunun sabit sürüm belgelerinden
okunmuş ve metindeki atıflarla eşleştirilmiştir. İncelenen kaynaklarda sunulmayan
DOI numaraları üretilmemiştir. TÜBİTAK'ın bağlantılı kaynakça web sayfasına erişim
kısıtı bulunduğu için o sayfanın güncel biçiminin bağımsız kontrol edildiği iddia edilmez.

**Resmî işlem durumu:** Belge düzenlemesi, TYBS'ye gönderim veya onay anlamına
gelmez. Sistem ön izlemesi, uygunluk beyanları, bütçe girişinin kabulü, danışman
onayı ve kuruluş yetkilisi e-imzası ilgili sistemlerde doğrulanmalıdır.
Mevcut olanaklarla ek harcama planlanmadığı için gider öngörüsü 0 TL'dir;
programın/sistemin bu bütçe tercihini kabulü ayrıca kontrol edilir.

## Belgeleri yeniden üretme

Ana metin değiştirilirse Word ve PDF birlikte yeniden üretilir. C programlarının
çalışması bu ek belge bağımlılığına bağlı değildir.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-documents.txt
python3 scripts/build_2209_application.py
```

PDF üretimi için ayrıca kurulu LibreOffice gerekir:

```bash
python3 scripts/build_2209_application.py --pdf
```

Üretici resmî sisteme bağlanmaz; yeni deney yürütmez. Kelime/karakter sınırları,
takvim ve atıf eşleşmeleri son Word dosyasından yeniden hesaplanır.
