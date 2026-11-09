# CPU yönetimi ve süreç zamanlama

**Burak Şanlı · Harran Üniversitesi · Bilgisayar Mühendisliği Bitirme Projesi**
**Danışman:** Prof. Dr. Dursun Akaslan

Bu proje, Linux tabanlı bir sistemde CPU yoğun arka plan işleriyle birlikte çalışan
kısa ve etkileşimli görevlerin bekleme sürelerini incelemektedir. Amaç, uzun işlerin
ilerlemesini koruyarak kısa görevlerin yanıt süresini azaltabilecek bir zamanlama
politikası geliştirmek ve sınırlarını karşılaştırmalı deneylerle değerlendirmektir.

## Haftalık çalışmalar

| Hafta | Kapsam | Belgeler |
|---|---|---|
| 1 | Konu seçimi, problem tanımı ve geliştirme yaklaşımı | [Hafta 1](docs/hafta1/README.md) · [Özgün PDF](docs/hafta1/Burak_Sanli_210504018_BitirmeProjesi_1_KonuSecimi.pdf) |
| 2 | C tabanlı politika prototipi, Linux başlangıç ölçümü ve otomatik kontroller | [Hafta 2](docs/hafta2/README.md) · [Uygulama ayrıntıları](docs/hafta2/uygulama.md) · [Deney sonuçları](docs/hafta2/deney_sonuclari.md) · [PDF sunumu](docs/hafta2/Burak_Sanli_Hafta2_CPU_Zamanlama.pdf) |

Haftalık teknik belgeler ve mevcut PDF sunumları [belge dizininde](docs/README.md)
listelenmektedir. Yeni haftalar tamamlandıkça aynı dizine eklenir.

## Mevcut uygulama

| Bileşen | İşlev |
|---|---|
| [`scheduler_sim`](src/scheduler_sim.c) | Tek CPU ve 1 ms adımlı modelde Round Robin ile bütçe/yaşlandırma tabanlı politika prototipini karşılaştırır. |
| [`linux_baseline`](src/linux_baseline.c) | Gerçek Linux süreçleriyle mevcut zamanlayıcı altında uyanma ve tamamlanma gecikmesini ölçer. |
| [Deney çalıştırıcısı](scripts/run_experiments.py) | Testleri, model senaryolarını ve gerçek Linux koşularını çalıştırıp ham sonuçları ve ortam bilgilerini kaydeder. |
| [Otomatik testler](tests/test_scheduling.py) | Bilinen zamanlama örneklerini, süre muhasebesini, girdi doğrulamasını ve gerçek ölçüm programını kontrol eder. |

İkinci haftada politika kuralları model düzeyinde uygulanmıştır. Linux çekirdeğine
özel zamanlama politikası henüz yüklenmemiştir. Modeldeki Round Robin referansı,
Linux'un varsayılan adil zamanlayıcısının taklidi değildir; model karşılaştırması
Linux üzerinde performans artışı kanıtı olarak yorumlanmamalıdır.

## Gereksinimler ve çalıştırma

- Linux; Windows üzerinde WSL/Ubuntu kullanılabilir.
- C11 destekli GCC, GNU Make, Python 3.10+ ve saat dilimi verisi.
- Derleme ve deneyler için ek Python paketi, yönetici yetkisi veya çekirdek modülü gerekmez.

Komutlar deponun kök dizininde çalıştırılır:

```bash
make
make test
make experiment
```

VS Code ile proje klasörü veya `Kernel_CPU.code-workspace` açılabilir.
Windows üzerinde Linux ölçüm programının derleme ve çalıştırma adımları WSL
terminalinde yürütülmelidir.

```bash
./build/scheduler_sim --policy rr workloads/mixed.csv
./build/scheduler_sim --policy interactive workloads/mixed.csv
./build/linux_baseline --workers 0 --samples 40
./build/linux_baseline --workers 2 --samples 40
```

`make experiment`, testlerden sonra altı model ve altı gerçek Linux koşusu üretir.
Her gerçek koşuda 40 örnek kaydedilir; toplam 240 örnek toplanır. Çıktılar
`results/week2-.../` dizinine yazılır. `results/latest.json` yalnızca başarılı bir
deney grubundan sonra güncellenir. `build/` ve yeni `results/` çıktıları Git'e
dahil edilmez. Değerlendirme için arşivlenmiş ilk veri grubu
[`experiments/hafta2/2026-11-05`](experiments/hafta2/2026-11-05) altındadır.

## Doğrulama ve sınırlar

İlk deney grubunda 13 test başarılı olmuş, üç model iş yükü iki politikayla
çalıştırılmış ve gerçek Linux başlangıç ölçümleri tamamlanmıştır. Ortam,
parametreler, tüm tekrarlar ve yorumlama sınırları [deney raporunda](docs/hafta2/deney_sonuclari.md)
yer almaktadır. Modelde I/O, çok çekirdek yerleşimi ve bağlam değiştirme maliyeti
bulunmamaktadır. Gerçek ölçümler konteyner kotası, sanallaştırma ve sistem yükünden
etkilenebilir; sonuçlar genel performans veya kesin gecikme garantisi değildir.

Sonraki geliştirme aşaması, ekip çekirdeğini belirlemek ve ayrı bir test sanal
makinesinde `sched_ext`/BTF desteği ile güvenli yükleme/geri dönüş sürecini
doğrulamaktır. Ardından politika kuralları çekirdeğe uyarlanarak aynı deney
düzeninde mevcut Linux davranışıyla karşılaştırılacaktır.

## İkinci hafta değerlendirmesi ve sunumu

[Değerlendirme ve sonraki adımlar](docs/hafta2/degerlendirme_ve_sonraki_adimlar.md),
tamamlanan çıktıları, olumlu ve gerileyen ölçütleri ve çekirdek entegrasyonuna geçiş
ölçütlerini bir araya getirir. [18 slaytlık PDF](docs/hafta2/Burak_Sanli_Hafta2_CPU_Zamanlama.pdf)
ve [grafikleri](docs/hafta2/grafikler) arşivlenmiş ilk deney grubundan üretilmiştir.
PDF'i okumak için geliştirme ortamı veya ek paket kurulumu gerekmez.

Sunumu yeniden üretmek için isteğe bağlı Python bağımlılıkları kullanılır:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-presentation.txt
make presentation
```

Linux dağıtımında sanal ortam desteği yoksa `python3-venv` paketinin kurulması
gerekebilir. Bu bağımlılıklar C programlarını derlemek veya test etmek için
gerekli değildir. Sunum hedefi yeni deney yapmaz; sürümlendirilmiş veri grubunu kullanır.

## Araştırma desteği başvurusu

[2209-A 2026 araştırma önerisi ve başvuru belgeleri](docs/basvuru/2209a/README.md),
bireysel CPU zamanlama projesinin ayrıntılı altı aylık planını, güncel Word/PDF
dosyalarını, teknik kaynakları ve TYBS aktarım rehberini içerir. Belgelerin
hazırlanması, resmî başvurunun gönderildiği veya desteğin kabul edildiği anlamına gelmez.
