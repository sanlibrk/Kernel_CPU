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

- [Çalıştırma komutları ve canlı gösterim](calistirma_ve_canli_gosterim.md)
- [18 slaytın konuşma metni ve soru-cevap notları](sunum_metni.md)
- [Konuşma metni — Word](Burak_Sanli_Hafta2_Sunum_Metni.docx)
- [Konuşma metni — PDF](Burak_Sanli_Hafta2_Sunum_Metni.pdf)
- [Uygulama mimarisi ve algoritma ayrıntıları](uygulama.md)
- [Deney yöntemi, tüm koşular ve sonuçların değerlendirilmesi](deney_sonuclari.md)
- [Aşama değerlendirmesi ve sonraki adımlar](degerlendirme_ve_sonraki_adimlar.md)
- [PDF sunumu — 18 slayt](Burak_Sanli_Hafta2_CPU_Zamanlama.pdf)
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

## PDF sunumu ve grafikler

18 slaytlık sunum; problem tanımını, kaynak bileşenlerini, algoritma kurallarını,
kontrollü zamanlama örneğini, model sonuçlarını, gerçek Linux başlangıç ölçümünü,
testleri, sınırlılıkları ve sonraki aşamanın ölçütlerini içerir. Sayısal veriler
ilk deney arşivinden alınmıştır; yerel Ubuntu/WSL kurulumu veya yerel performans
doğrulanmış bir deney sonucu olarak sunulmaz.

- [Sunumu aç](Burak_Sanli_Hafta2_CPU_Zamanlama.pdf)
- [Karışık model iş yükü grafiği](grafikler/mixed.png)
- [Yoğun etkileşimli model iş yükü grafiği](grafikler/interactive_pressure.png)
- [Gerçek Linux P95 grafiği](grafikler/linux_p95.png)

Sunumu ve grafikleri yeniden üretme adımları [ana sayfada](../../README.md)
açıklanmıştır. Üretici: [`scripts/build_week2_presentation.py`](../../scripts/build_week2_presentation.py).
Bu komut arşivi değiştirmez ve yeni performans deneyi çalıştırmaz.
