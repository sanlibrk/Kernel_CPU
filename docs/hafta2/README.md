# Hafta 2 — Politika prototipi ve başlangıç ölçümleri

## Çalışmanın kapsamı

Bu aşama, CPU zamanlama kurallarının C tabanlı bir modelde prototiplenmesini ve
gerçek Linux süreçleri üzerinde başlangıç ölçümlerinin toplanmasını kapsamaktadır.
Özel politikanın Linux çekirdeğine entegrasyonu sonraki geliştirme aşamasıdır.

| Tamamlanan bileşen | Kapsam |
|---|---|
| Zamanlama modeli | Round Robin referansı, sınırlı etkileşimli tercih bütçesi, yaşlandırma ve görev bazında ölçütler. |
| Gerçek Linux ölçüm programı | Aynı CPU'daki periyodik kısa iş ve arka plan süreçleri; uyanma, tamamlanma ve işçi süreleri. |
| Otomatik kontroller | 13 test yöntemi; analitik örnekler, girdi denetimi, süre muhasebesi ve gerçek süreç kontrolleri. |
| Deney çalıştırıcısı | Üç model senaryosu × iki politika; iki gerçek yük koşulu × üç tekrar. |
| İlk sonuç arşivi | Altı model CSV'si, altı Linux JSON'u, test günlüğü ve ortam/parametre özeti. |

## Teknik belgeler

- [Uygulama mimarisi ve algoritma ayrıntıları](uygulama.md)
- [Deney yöntemi, tüm koşular ve sonuçların değerlendirilmesi](deney_sonuclari.md)
- [Arşivlenmiş ham veriler](../../experiments/hafta2/2026-11-05)

Uygulama belgesi, veri yapıları ve fonksiyonları, seçim kurallarını, komut satırı
seçeneklerini, giriş/çıkış biçimlerini, ölçütleri ve test kapsamını açıklar.
Deney belgesi, sayısal sonuçları kaynak kayıtlarıyla birlikte verir; model
karşılaştırmasını gerçek Linux başlangıç ölçümünden ayrı değerlendirir.

## Kaynak dosyaları

| Dosya | İşlev |
|---|---|
| [`src/scheduler_sim.c`](../../src/scheduler_sim.c) | Tek CPU zamanlama modeli. |
| [`src/linux_baseline.c`](../../src/linux_baseline.c) | Gerçek Linux süreçleri üzerinde ölçüm. |
| [`tests/test_scheduling.py`](../../tests/test_scheduling.py) | Otomatik kontroller. |
| [`scripts/run_experiments.py`](../../scripts/run_experiments.py) | Deneylerin yürütülmesi ve arşivleme. |
| [`workloads/`](../../workloads) | Karışık, yalnız arka plan ve yoğun etkileşimli senaryolar. |
| [`Makefile`](../../Makefile) | Derleme, test, deney ve temizlik hedefleri. |

## İlk değerlendirme ve açık işler

Karışık model iş yükünde etkileşimli görevlerin ortalama ilk yanıt süresi RR için
11 ms, prototip için 3 ms ölçülmüştür. Bununla birlikte yoğun etkileşimli model
senaryosunda ilk yanıt iyileşirken toplam bekleme süresi artmıştır. Bu nedenle
sonuçlar tek bir ölçüte dayanarak genel iyileşme olarak sunulmamaktadır.

Gerçek Linux koşularında yalnızca mevcut `SCHED_OTHER` davranışı ölçülmüştür.
Politika henüz çekirdekte çalışmadığından Linux'a karşı kazanç ölçümü yoktur.
Çekirdek/dağıtım seçimi, `sched_ext` ve BTF desteği, ayrı test sanal makinesi,
yükleme/geri dönüş deneyi ve gerçek politika karşılaştırması açık işlerdir.

İkinci haftanın PDF sunumu henüz hazırlanmamıştır.
