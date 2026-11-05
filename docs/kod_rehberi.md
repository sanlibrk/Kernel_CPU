# İkinci hafta kod rehberi

## Hocaya tek cümleyle

“Politikamın ilk kurallarını C ile çalışır bir modelde uyguladım; gerçek Linux
üzerinde sonraki karşılaştırmalar için başlangıç ölçüm aracı hazırladım.
Henüz Linux çekirdeğine özel politika yüklemedim.”

## Zamanlama modeli: src/scheduler_sim.c

- `load`: CSV'den görev numarası, sınıfı, varış anı ve CPU ihtiyacını okur;
  bozuk girişleri ve yinelenen numaraları reddeder.
- `admit`: zamanı gelen görevleri varış/numara sırasıyla kuyruğa alır.
- `choose`: sıradaki görevi RR veya bütçe/yaşlandırma kurallarıyla seçer.
- `main`: 1 ms adımlarla görevi yürütür, bütçeyi ve kalan CPU ihtiyacını günceller.
- Sonuç: ilk başlama, tamamlanma, yanıt, bekleme ve dönüş süreleri.

Örneğin `1,background,0,120`: 0. ms'de hazır olan, 120 ms CPU işi isteyen arka
plan görevidir. Model numarası gerçek bir Linux süreç kimliği değildir.

## Gerçek ölçüm: src/linux_baseline.c

- `sched_getaffinity` izin verilen CPU'ları bulur, `sched_setaffinity` birini seçer.
- `fork` ile oluşturulan işçiler aynı CPU seçimini miras alır.
- Başlangıç borusu işçileri serbest bırakır; ana süreç periyodik kısa işi yürütür.
- `burn`: `CLOCK_PROCESS_CPUTIME_ID` ile gerçekten harcanan CPU işini sınırlar.
- `CLOCK_MONOTONIC`: duvar saati ölçümü ve mutlak uyanma hedefi içindir.
- `waitpid` ve işçi sonuçları arka plan işlerinin tamamlandığını doğrular.

Kısa işler, tek ana sürecin periyodik CPU patlamalarıdır; her örnekte yeni süreç
oluşturulmaz. `nice`, cgroup veya çekirdek zamanlayıcısı değiştirilmez.
İş yetişmezse sonraki örneğin biriken gecikmesi de kaydedilir; örnek atlanmaz.

## Deney ve testler

- `workloads/mixed.csv`: 3 uzun arka plan işi ve 8 kısa etkileşimli iş.
- `workloads/cpu_only.csv`: yalnızca 3 uzun iş.
- `workloads/interactive_pressure.csv`: daha yoğun etkileşimli talep.
- `tests/test_scheduling.py`: bilinen RR takvimi, boş CPU, bütçe, yaşlandırma,
  hatalı girdi, tekrarlanabilir rastgele iş yüklerinde süre muhasebesi ve gerçek
  Linux ölçümünün çıktı/bitiş kontrolleri.
- `scripts/run_experiments.py`: test günlüğü, kaynak SHA-256 özetleri, model CSV,
  gerçek Linux JSON ve ortam bilgilerini aynı deney dizininde toplar.

Gerçek deneyde 0 ve 2 arka plan işçisiyle üçer tekrar, her tekrarda 40 örnek,
20 ms periyot, 500 µs kısa CPU işi ve işçi başına 800 ms CPU bütçesi kullanılır.
Tüm süreçler aynı izinli CPU'da ve normal `SCHED_OTHER` politikasıyla çalışır.

## Sunumda korunacak ayrımlar

Modelde RR ile kıyaslama Linux'un varsayılan zamanlayıcısıyla kıyaslama değildir.
Modeldeki ilk yanıt ile gerçek süreçteki uyanma gecikmesi farklı ölçümlerdir.
Tek CPU ve az örnekli ilk deney, çok çekirdek veya genel performans sonucu değildir.
Konteyner kotası, barındıran makinenin yükü ve timer davranışı ölçümleri etkiler.
Parametreler başlangıç tasarımıdır; en iyi parametreleri bulduğumuz söylenemez.

## Canlı demo

```bash
make test
./build/scheduler_sim --policy rr workloads/mixed.csv
./build/scheduler_sim --policy interactive workloads/mixed.csv
./build/linux_baseline --workers 2 --samples 10 --worker-ms 200
```

Modelde `response_ms` sütununu, gerçek ölçümde `wake_p95_ms` ve arka plan
`wall_ms` alanlarını açıklayın. Bunları farklı deneyler olarak gösterin.
