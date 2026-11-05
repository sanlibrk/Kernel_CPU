# CPU yönetimi ve süreç zamanlama — ikinci hafta

Burak Şanlı · Harran Üniversitesi Bilgisayar Mühendisliği

## VS Code'da açma

Proje klasörünü açın veya `Kernel_CPU.code-workspace` dosyasına çift tıklayın.
İlk incelenecek dosya `src/scheduler_sim.c`; gerçek Linux ölçüm programı
`src/linux_baseline.c`, testler `tests/test_scheduling.py` içindedir.

## Çalıştırma

Gerekenler: Linux, GCC (C11), GNU Make ve Python 3.10+.
Windows'ta kodları doğrudan inceleyebilirsiniz; gerçek süreç ölçümünü WSL/Linux'ta
çalıştırın. Ek Python paketi, root veya çekirdek modülü gerekmiyor.
Bulut görevleri zaten yalıtılmıştır; mevcut checkout'u kullanın, yeni worktree gerekmez.

```bash
make
make test
make experiment
```

`make experiment`, testlerden sonra altı model ve altı gerçek Linux koşusu yapar.
Çıktılar `results/week2-.../` dizinindedir; ham CSV/JSON, test günlüğü ve özet
saklanır. Her başarılı deney `results/latest.json` işaretçisini günceller.
`build/` ve `results/` üretilen çıktılardır; Git'e dahil edilmez.

## İki programın farkı

**scheduler_sim:** C ile yazılmış tek CPU, 1 ms adımlı zamanlama modeli.
Round Robin referansı ile bütçe/yaşlandırma içeren politika prototipini karşılaştırır.
Bu program Linux zamanlayıcısını değiştirmez. RR, Linux'un varsayılan adil
zamanlayıcısının modeli değildir.

**linux_baseline:** Gerçek Linux süreçlerini aynı izinli CPU'ya sabitler.
Periyodik kısa CPU işi ile CPU yoğun arka plan işçilerini çalıştırır.
Uyanma ve tamamlanma gecikmesini, arka plan işçilerinin CPU/duvar saati sürelerini
kaydeder. Özel politika bu ölçümde uygulanmaz; mevcut Linux davranışı ölçülür.

```bash
./build/scheduler_sim --policy rr workloads/mixed.csv
./build/scheduler_sim --policy interactive workloads/mixed.csv
./build/linux_baseline --workers 0 --samples 40
./build/linux_baseline --workers 2 --samples 40
```

## Politika prototipi

- 4 ms zaman dilimi; girişte açıkça belirtilen etkileşimli/arka plan görev sınıfları.
- Sabit 20 ms pencerede 8 ms etkileşimli tercih bütçesi; kullanılmayan bütçe taşınmaz.
- Arka plan işi hazırsa bütçe tükendiğinde ona sıra verilir.
- Seçim anında en az 20 ms bekleyen görevlere yaşlandırma önceliği tanınır.
- Sınıf içinde FIFO/Round Robin; başka hazır iş yoksa CPU boş bırakılmaz.

Bütçe katı CPU kotası değildir: yaşlandırma veya başka sınıfta hazır iş olmaması
bütçeyi aşabilir. Sıfır bütçeyle yaşlandırma üzerinden seçilen etkileşimli görev
1 ms çalışabilir; arka plan işi hazırsa sonraki adımda yeniden seçim yapılır.
Yeni görev gelişi tek başına çalışan görevi kesmez, zaman dilimi beklenir.
Modelde I/O, çok çekirdek ve bağlam değiştirme maliyeti yoktur. Yaşlandırma tüm
yüklerde kesin bir bekleme üst sınırı garantisi değildir.

Model yanıt süresi = ilk başlama − varış; toplam bekleme = tamamlanma − varış − CPU ihtiyacı.
Gerçek programda uyanma gecikmesi = çalışmaya dönüş − planlanan uyanma anı.
Bu, saf çekirdek kuyruk gecikmesi değildir; timer, sanallaştırma ve ortam yükü de etkiler.
Tamamlanma gecikmesi kısa CPU işini de kapsar. P95 sıralı örneklerde
`ceil(0.95 * n)` sırasıdır; örnek sayısı ve tekrarlar sonuçlarla birlikte belirtilir.

**Modeldeki sonuçlar Linux performans artışı kanıtlamaz.** Gerçek Linux programı
yalnızca başlangıç çizgisidir. Henüz çekirdeğe politika yüklenmedi.

## Mevcut ortam ve sonraki adım

İlk ortam: Debian 13, Linux 6.18.57, GCC 14.2. Çekirdek numarası tek başına
`sched_ext` desteğini garanti etmez. Bu oturumda sched_ext sysfs ve çekirdek BTF
arayüzleri görünmüyor; süreçte yönetim/BPF yetkileri yok.

Sonraki aşama: ekip çekirdeğini belirlemek, ayrı test VM'inde `sched_ext`/BTF
desteğini doğrulamak, örnek politika ve güvenli geri dönüşü denemek. Ardından bu
kuralları çekirdeğe taşıyıp aynı iş yüklerinde gerçek karşılaştırma yapmak.
PDF sunumu kullanıcıyla içerik netleştirildikten sonra ayrıca hazırlanacak.

Açıklamalı dosya rehberi: [docs/kod_rehberi.md](docs/kod_rehberi.md).
