# Gecikme Odaklı CPU Zamanlama

**Burak Şanlı · Harran Üniversitesi · Bilgisayar Mühendisliği**
**Danışman:** Prof. Dr. Dursun Akaslan

CPU yoğun arka plan işleriyle birlikte çalışan kısa ve etkileşimli görevler için
gecikme–ilerleme dengesini inceleyen bireysel bitirme projesidir. Çalışma,
sınırlı tercih bütçesi ve bekleme süresine dayalı görev seçimini kontrollü
zamanlama deneyleriyle değerlendirmektedir.

## Başvuru ve sunumlar

| Belge | Dosyalar |
|---|---|
| TÜBİTAK 2209-A araştırma önerisi | [Word](https://raw.githubusercontent.com/sanlibrk/Kernel_CPU/main/docs/basvuru/2209a/2209A_Burak_Sanli_Arastirma_Onerisi.docx) · [PDF](docs/basvuru/2209a/2209A_Burak_Sanli_Arastirma_Onerisi.pdf) |
| Hafta 1 — Konu seçimi | [PDF](docs/hafta1/Burak_Sanli_210504018_BitirmeProjesi_1_KonuSecimi.pdf) |
| Hafta 2 — Prototip ve başlangıç ölçümleri | [PDF](docs/hafta2/Burak_Sanli_Hafta2_CPU_Zamanlama.pdf) |

## Uygulama

| Bileşen | İşlev |
|---|---|
| [scheduler_sim.c](src/scheduler_sim.c) | Tek CPU modelinde Round Robin ve bütçe/yaşlandırma politikasının karşılaştırılması. |
| [linux_baseline.c](src/linux_baseline.c) | Mevcut Linux zamanlayıcısı altında periyodik kısa işlerin uyanma gecikmesinin ölçülmesi. |
| [run_experiments.py](scripts/run_experiments.py) | Testlerin ve deneylerin çalıştırılması; ham sonuçların ve ortam bilgilerinin kaydedilmesi. |
| [test_scheduling.py](tests/test_scheduling.py) | Zamanlama davranışı, süre muhasebesi, girdi doğrulaması ve Linux ölçüm kontrolleri. |

Mevcut prototip 13 testle doğrulanmıştır. Model karşılaştırmaları ve gerçek Linux
başlangıç ölçümleri tamamlanmıştır. Özel politikanın `sched_ext` üzerinden çekirdek
entegrasyonu sonraki geliştirme aşamasıdır.

## Çalıştırma

Linux veya Windows üzerinde Ubuntu/WSL; C11 destekli GCC, GNU Make ve Python
3.10+ gereklidir. Komutlar proje kökünde çalıştırılır:

```bash
make
make test
make experiment
```

`make experiment`, altı model ve altı Linux koşusu üretir; Linux koşularında toplam
240 gözlem toplanır. Yeni sonuçlar `results/` altında saklanır.

## Teknik belgeler

- [Kod rehberi](docs/kod_rehberi.md)
- [Deney yöntemi ve sonuçları](docs/hafta2/deney_sonuclari.md)
- [Çalıştırma ve canlı gösterim](docs/hafta2/calistirma_ve_canli_gosterim.md)
- [Haftalık belgeler](docs/README.md)
- [Arşivlenmiş deney verileri](experiments/hafta2/2026-11-05)
- [Yerel Ubuntu/WSL doğrulaması](experiments/hafta2/2026-11-09-wsl)
