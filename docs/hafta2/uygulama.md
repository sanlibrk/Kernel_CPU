# İkinci hafta uygulamasının teknik açıklaması

Bu belge, CPU yönetimi ve süreç zamanlama çalışmasının ilk uygulamasındaki
programları, veri biçimlerini, deney düzenini ve doğrulama sınırlarını açıklar.
Kodda uygulanmış davranışlar ile ileride çekirdek entegrasyonu gerektiren
özellikler birbirinden ayrılır.

## 1. Kapsam ve bileşenler

Uygulama iki bağımsız C programı ve bunları doğrulayan Python araçlarından oluşur.

| Bileşen | Kaynak | İşlev |
|---|---|---|
| Zamanlama modeli | [`src/scheduler_sim.c`](../../src/scheduler_sim.c) | Tek CPU üzerinde RR referansı ile etkileşimli tercih politikasını karşılaştırır. |
| Linux başlangıç ölçümü | [`src/linux_baseline.c`](../../src/linux_baseline.c) | Mevcut Linux zamanlayıcısı altında periyodik kısa işlerin gecikmesini ölçer. |
| Otomatik testler | [`tests/test_scheduling.py`](../../tests/test_scheduling.py) | Bilinen zamanlama örneklerini, girdi doğrulamasını ve gerçek süreç ölçümünün temel özelliklerini sınar. |
| Deney yürütücüsü | [`scripts/run_experiments.py`](../../scripts/run_experiments.py) | Derleme, test ve deney çıktılarını aynı sonuç dizininde toplar. |
| Sunum üreticisi | [`scripts/build_week2_presentation.py`](../../scripts/build_week2_presentation.py) | Arşivlenmiş verilerden grafikleri ve 18 slaytlık PDF'i üretir. |
| Derleme giriş noktası | [`Makefile`](../../Makefile) | Derleme, test, deney ve derleme çıktısı temizleme hedeflerini tanımlar. |

`scheduler_sim` bir Linux çekirdek zamanlayıcısı değildir. Modelin `rr` seçeneği
de Linux'un varsayılan adil zamanlayıcısının uygulaması veya taklidi değildir.
`linux_baseline` gerçek Linux süreçleri kullanır; ancak özel politikayı sisteme
yüklemez. Bu aşamada model karşılaştırması ile gerçek Linux başlangıç ölçümü
farklı deneylerdir.

## 2. Derleme ve çalıştırma

Derleme için C11 destekli GCC, GNU Make; testler ve deney yürütücüsü için Linux
üzerinde Python 3.10 veya üzeri gerekir. Python tarafında standart kütüphane
kullanılır. Windows üzerinde gerçek süreç ölçümünün çalıştırılması WSL/Linux
ortamı gerektirir.

```bash
make
make test
make experiment
```

Derleme seçenekleri `-std=c11 -O2 -g -Wall -Wextra -Werror -pedantic` biçimindedir.
`-O2` optimizasyonu, `-g` hata ayıklama bilgisini etkinleştirir. Uyarılar hata
olarak değerlendirilir. Çalıştırılabilir dosyalar `build/` dizinine yazılır.

| Hedef | Yaptığı işlem |
|---|---|
| `make` / `make all` | İki C programını derler; güncel dosyaları yeniden derlemez. |
| `make test` | Derlemeden sonra `unittest` testlerini ayrıntılı çıktı ile yürütür. |
| `make experiment` | Deney betiğini çalıştırır; betik de derlemeyi ve testleri doğrular. |
| `make presentation` | İsteğe bağlı sunum bağımlılıklarıyla mevcut arşivden PDF ve grafikleri üretir; yeni deney yapmaz. |
| `make clean` | Yalnızca `build/` dizinini siler; deney sonuçlarını silmez. |

## 3. Zamanlama modelinin varsayımları

Modelde tek bir CPU ve tam sayı milisaniyelik bir zaman ekseni vardır. Her görev
bir kez sisteme gelir ve tek bir CPU çalışma ihtiyacını tamamlar. I/O bekleme,
uyku/uyanma döngüleri, CPU göçü, çok çekirdekli yerleşim ve bağlam değiştirme
maliyeti modellenmez. Bir model adımı, seçilen görevin 1 ms CPU işi yapmasıdır;
programın gerçek bilgisayarda 1 ms boyunca çalışması anlamına gelmez.

`interactive` sınıfı girdi dosyasında açıkça belirtilir. Model görev davranışından
otomatik sınıflandırma yapmaz ve bir görevin etkileşimli olduğunu işletim
sisteminden keşfetmez. Başlangıç parametreleri araştırılacak politika yönünü
temsil eder; en iyi parametreler olarak kabul edilmez.

### 3.1. Görev yapısı

`Task` yapısının alanları şöyledir:

| Alan | Anlamı |
|---|---|
| `id` | Girdi içindeki benzersiz görev numarası; Linux süreç kimliği değildir. |
| `interactive` | Etkileşimli sınıf için 1, arka plan sınıfı için 0. |
| `arrival` | Görevin hazır duruma geldiği model zamanı. |
| `burst` | Toplam CPU çalışma ihtiyacı. |
| `remaining` | Henüz tamamlanmamış CPU ihtiyacı. |
| `start` | İlk CPU çalışmasının zamanı; başlamamış görevde −1. |
| `finish` | CPU ihtiyacının tamamlandığı zaman. |
| `ready_since` | Son kez beklemeye başladığı an; başlangıçta varış zamanı. |
| `ticket` | Kuyruk sırasını belirleyen artan sıra numarası; henüz kabul edilmemiş görevde 0. |

Görevler sabit boyutlu bir dizide tutulur. Kuyruk sırası gerçek bir bağlı liste
yerine `ticket` alanlarıyla temsil edilir. Seçim, uygun görevlerin taranmasıyla
yapılır. Bu yapı anlaşılabilir bir referans uygulama sağlar; çekirdek için
ölçeklenebilir veri yapısı veya maliyet optimizasyonu iddiası içermez.

### 3.2. Girdi dosyasının biçimi ve sınırları

CSV başlığı tam olarak şu biçimdedir:

```csv
id,class,arrival_ms,burst_ms
1,background,0,120
2,interactive,5,2
```

| Alan | Kabul edilen değer |
|---|---|
| `id` | 1–1.000.000 arasında benzersiz tam sayı. |
| `class` | Tam olarak `background` veya `interactive`. |
| `arrival_ms` | 0–1.000.000 arasında tam sayı. |
| `burst_ms` | 1–1.000.000 arasında tam sayı. |

En fazla 256 görev kabul edilir. Bütün görevlerin CPU ihtiyaçlarının toplamı
1.000.000 ms'yi aşamaz. Bu sınır, son tamamlanma zamanının mutlaka 1.000.000 ms
olduğu anlamına gelmez; geç varışlar toplam model süresini uzatabilir.

Ayrıştırıcı dört alanlı basit CSV kullanır: tırnaklı alan, yorum satırı veya
alan içinde virgül desteği yoktur. Boş satırlar atlanır, Windows satır sonları
işlenir. Sınıf etiketlerindeki ek boşluklar kabul edilmez. Satır tamponu 256
bayttır; uzun satırlar reddedilir. Dosyanın okunamaması, yanlış başlık, eksik/fazla
alan, bilinmeyen sınıf, yinelenen numara, geçersiz sayı ve aşılmış sınırlar hata
ile sonuçlanır. Kaynak dosyadaki satır sırası görev önceliği değildir.

### 3.3. Komut satırı seçenekleri

```bash
./build/scheduler_sim --policy interactive --quantum 4 --window 20 --budget 8 --aging 20 workloads/mixed.csv
```

| Seçenek | Varsayılan | Açıklama |
|---|---:|---|
| `--policy` | `interactive` | `rr` veya `interactive`. |
| `--quantum` | 4 | Bir seçimde kullanılabilecek zaman dilimi, ms. |
| `--window` | 20 | Tercih bütçesinin yenilendiği sabit pencere, ms. |
| `--budget` | 8 | Pencere başındaki etkileşimli tercih bütçesi, ms. |
| `--aging` | 20 | Yaşlandırma seçimine uygun bekleme eşiği, ms. |

Bütün sayısal seçenekler 1–1.000.000 aralığındadır. Bütçe pencereyi aşamaz;
sıfır bütçe veya sıfır yaşlandırma değeri kabul edilmez. İş yükü yolu zorunludur.
Karşılaştırmada politika açıkça belirtilmelidir; seçenek verilmezse özel
politika çalışır. RR seçilse bile ortak komut satırı doğrulaması pencere/bütçe
değerlerini kontrol eder; bu parametreler RR'nin görev seçimini değiştirmez.

### 3.4. Fonksiyonlar

| Fonksiyon | Sorumluluk |
|---|---|
| `fail` | Hata iletisini standart hata akışına yazar ve başarısız çıkış yapar. |
| `number` | Sayısal metni dönüştürür; aralık dışı veya tamamı ayrıştırılamayan değeri reddeder. |
| `load` | CSV'yi okur, sınırları doğrular ve görevlerin ilk durumlarını kurar. |
| `ready` | Varış zamanı gelmiş ve CPU ihtiyacı bitmemiş görevleri belirler. |
| `admit` | Henüz sıra numarası almamış hazır görevleri varış zamanı, sonra görev numarası sırasıyla kabul eder. |
| `choose` | Politika, yaşlandırma, bütçe ve kuyruk sırasına göre sıradaki görevi döndürür. |
| `main` | Seçenekleri işler, zaman döngüsünü yürütür ve görev bazında CSV üretir. |

### 3.5. Bir model adımındaki işlem sırası

Her `now` zamanında şu sıra uygulanır:

1. `now`, pencere uzunluğunun tam katıysa bütçe başlangıç değerine yenilenir.
2. Zamanı gelen yeni görevler `admit` ile kuyruğa alınır.
3. Hazır bir arka plan görevi olup olmadığı belirlenir.
4. Çalışan görevin zaman dilimi bitmişse veya bütçe nedeniyle kesilmesi gerekiyorsa
   göreve yeni bir kuyruk numarası verilir; `ready_since = now` yapılır.
5. Çalışan görev yoksa `choose` çağrılır ve yeni zaman dilimi başlatılır.
6. Hiç hazır görev yoksa zaman 1 ms ilerler.
7. Bir görev seçilmişse kalan CPU ihtiyacı ve zaman dilimi 1 ms azaltılır.
   Etkileşimli görev çalışıyorsa ve bütçe pozitifse bütçe de 1 ms azalır.
8. Zaman 1 ms ilerletilir; görevin kalan ihtiyacı sıfırsa tamamlanma zamanı yazılır.

Bu sıra bazı sınır durumlarını belirler. Örneğin zaman diliminin bittiği anda
gelen yeni görevler, süresi dolan görev yeniden kuyruğa konmadan önce kabul
edilir. Pencere yenilenmesi ise tek başına çalışan görevi kesmez. Yeni bir
etkileşimli görevin gelmesi de tek başına kesme nedeni değildir.

### 3.6. Round Robin referansı

RR, hazır görevler arasından en küçük `ticket` değerini seçer. Görev tamamlanmazsa
zaman dilimi sonunda yeni bir sıra numarası alarak kuyruğun sonuna geçer.
Sınıf etiketi RR seçimini etkilemez. Hazır görev bulunmadığında CPU modelde boş
kalır; bir görev hazırken yapay boşluk oluşturulmaz.

İki görev de 0. ms'de gelir ve 5 ms CPU isterse, 2 ms zaman diliminde çalışma
aralıkları şöyledir:

| Aralık, ms | Görev |
|---|---:|
| 0–2 | 1 |
| 2–4 | 2 |
| 4–6 | 1 |
| 6–8 | 2 |
| 8–9 | 1 |
| 9–10 | 2 |

İlk görev 9. ms'de, ikinci görev 10. ms'de tamamlanır. Bu takvim otomatik testte
kontrol edilen analitik örneklerden biridir.

### 3.7. Etkileşimli tercih politikası

`choose` önce hazır görevleri tarar. Varsayılan kuyruk adayı en küçük `ticket`
değeridir. Yaşlandırma eşiğine ulaşan görevler varsa, en eski `ready_since`
değerine sahip görev seçilir; eşitlikte kuyruk numarası kullanılır. Yaşlandırma
her iki sınıfa da uygulanır ve bütçe tercihinden önce değerlendirilir.

Yaşlandırılmış görev yoksa sınıf seçimi şöyledir:

- Bütçe pozitifse etkileşimli sınıf tercih edilir.
- Bütçe sıfırsa ve arka plan görevi hazırsa arka plan sınıfı tercih edilir.
- Hazır arka plan görevi yoksa etkileşimli görevlerin çalışmasına devam edilir.
- Tercih edilen sınıfta hazır görev bulunamazsa genel kuyruk adayı kullanılır.

Seçilen sınıf içinde en küçük kuyruk numarası kullanılır. Bir etkileşimli görevin
çalışması sırasında bütçe tükenirse, hazır arka plan işi bulunduğu koşulda sonraki
1 ms adımının başında zaman dilimi bitmeden yeniden seçim yapılabilir.

Bütçe ve yaşlandırmanın birlikte kullanımında aşağıdaki ayrımlar önemlidir:

- Bütçe sabit zaman pencerelerine bağlıdır; kayan pencere değildir. Kullanılmayan
  bütçe sonraki pencereye taşınmaz.
- Yaşlandırma, görevin ilk varışından beri geçen toplam süreye veya toplam
  bekleme metriğine dayanmaz. Görev çalıştıktan sonra yeniden kuyruğa girdiğinde
  bekleme başlangıcı yenilenir.
- Eşik, yalnızca seçim anında değerlendirilir. Çalışan bir görevin zaman dilimini
  sırf başka görev eşiğe ulaştı diye kesmez.
- Sıfır bütçeli bir etkileşimli görev yaşlandırmayla seçilebilir. Bu görev 1 ms
  çalışır; arka plan işi hazırsa sonraki adımda bütçe nedeniyle yeniden seçim olur.
- Başka sınıfta hazır görev bulunmaması veya yaşlandırma kararı bütçenin üzerinde
  etkileşimli çalışma oluşturabilir. Dolayısıyla bütçe katı CPU kotası değildir.
- Bu kurallar bütün iş yüklerinde kesin bir bekleme üst sınırı veya genel
  açlık-önleme ispatı sağlamaz.

### 3.8. Model çıktısı ve metrikler

Çıktı standart çıktı akışına CSV olarak yazılır. Görev satırları çalışma sırasına
göre değil, giriş dosyasındaki sırayla verilir.

| Alan | Tanım |
|---|---|
| `id`, `class`, `arrival_ms`, `burst_ms` | Görevin giriş bilgileri. |
| `start_ms` | İlk kez CPU üzerinde çalışmaya başladığı zaman. |
| `finish_ms` | CPU ihtiyacının tamamlandığı zaman. |
| `response_ms` | `start_ms - arrival_ms`. |
| `turnaround_ms` | `finish_ms - arrival_ms`. |
| `waiting_ms` | `turnaround_ms - burst_ms`; bütün kuyruk beklemelerinin toplamı. |

Modelde I/O olmadığı için dönüş süresi yalnızca CPU çalışması ile kuyruk
beklemelerinden oluşur. İlk yanıt süresi, sonraki zaman dilimleri arasındaki
beklemeleri içermez. Toplam bekleme ile ilk yanıt bu nedenle farklı metriklerdir.

## 4. Gerçek Linux başlangıç ölçümü

Bu programın amacı, özel politika uygulanmadan önce gerçek Linux ortamındaki
gecikme davranışını kaydetmektir. Aynı CPU üzerinde periyodik bir kısa iş ve
isteğe bağlı CPU yoğun arka plan işçileri oluşturulur. Kısa işler, ana sürecin
tekrarlanan CPU patlamalarıdır; her örnek için ayrı süreç oluşturulmaz.

### 4.1. Komut satırı seçenekleri

```bash
./build/linux_baseline --workers 2 --samples 40 --period-ms 20 --burst-us 500 --worker-ms 800
```

| Seçenek | Varsayılan | Aralık | Anlamı |
|---|---:|---:|---|
| `--workers` | 2 | 0–8 | CPU yoğun arka plan süreçlerinin sayısı. |
| `--samples` | 40 | 1–2.000 | Ana süreçte ölçülecek periyodik kısa iş sayısı. |
| `--period-ms` | 20 | 1–1.000 | Planlanan kısa işler arasındaki süre, ms. |
| `--burst-us` | 500 | 1–100.000 | Her kısa iş için hedef süreç CPU süresi, µs. |
| `--worker-ms` | 800 | 1–60.000 | Her arka plan işçisinin hedef süreç CPU süresi, ms. |

Bilinmeyen seçenek, eksik seçenek değeri veya aralık dışı sayı hata ile
sonuçlanır. `--workers 0` durumunda yalnızca ana süreç ölçülür. Bu durum, barındıran
sistemde hiç başka yük olmadığı anlamına gelmez.

### 4.2. Fonksiyonlar ve veri yapıları

| Bileşen | Sorumluluk |
|---|---|
| `children`, `child_count` | Oluşturulan arka plan süreçlerini izler. |
| `cleanup` | Normal çıkış veya `exit` üzerinden hata çıkışında izlenen çocuk süreçleri sonlandırır ve toplar. |
| `fail` | Açıklama ve mevcut sistem hata metnini yazıp başarısız çıkış yapar. |
| `number` | Seçenek değerlerinin sayısal aralıklarını doğrular. |
| `ns` | Verilen saat kaynağını nanosaniye cinsinden okur. |
| `burn` | Hedef süreç CPU süresine ulaşıncaya kadar hesaplama döngüsü çalıştırır. |
| `transfer` | Boru üzerinden istenen miktarda veri okur/yazar; kesilen çağrıları tekrarlar. |
| `compare` | Yüzdelik hesabında gecikme örneklerini sıralamak için kullanılır. |
| `Worker` | Bir işçinin numarası, duvar saati süresi ve harcanan CPU süresini taşır. |
| `main` | Ortam seçimi, süreçler, ölçüm döngüsü, bekleme ve JSON çıktısını yönetir. |

`cleanup`, `atexit` ile kaydedilir. Bu mekanizma bütün sinyaller veya zorla
sonlandırma koşulları için genel bir temizlik garantisi değildir; programda ayrı
bir sinyal işleyicisi bulunmaz.

### 4.3. CPU seçimi ve süreçler

`sched_getaffinity`, sürecin kullanmasına izin verilen mantıksal CPU kümesini
okur. Kümedeki en düşük numaralı CPU seçilir ve `sched_setaffinity` ile ana süreç
ona sabitlenir. `fork` ile oluşturulan işçiler bu seçimi miras alır.

Bu düzenek aynı mantıksal CPU'da rekabet oluşturur. CPU'yu diğer sistem
süreçlerinden ayırmaz, fiziksel çekirdek üzerinde özel kullanım sağlamaz ve
SMT/hiper iş parçacığı etkilerini ortadan kaldırmaz. Sanal makine, konteyner
veya WSL ortamında barındıran sistemin etkileri sürebilir.

Program mevcut zamanlama sınıfının `SCHED_OTHER` olduğunu doğrular. Farklı
sınıfta başlatılmışsa hata verir; kendisi gerçek zaman sınıfına geçmez.
`SCHED_OTHER` adı çekirdeğin tam iç algoritmasını veya nice değerini tanımlamaz.
Program nice ve cgroup ayarlarını değiştirmez; ana süreçten miras alınan ortamda
çalışır. CPU sabitleme veya gerekli sistem çağrıları ortam tarafından
engelleniyorsa ölçüm de hata verir.

### 4.4. Borular, başlangıç ve işçilerin tamamlanması

Başlangıç için kullanılan `gate` borusu her işçiye bir baytlık serbest bırakma
işareti iletir. Sonuç borusu `output`, tamamlanan işçilerin `Worker` kayıtlarını
ana sürece taşır. Kayıtlar borunun atomik yazma sınırından küçüktür.

İşçilere başlangıç işaretleri sırayla verilir; süreçlerin tam olarak aynı anda
başlaması garanti edilmez. Ana süreç, işçiler serbest bırakıldıktan sonra ilk
örnek için yaklaşık 20 ms ileride bir hedef zaman oluşturur. Bu ek süre
`--period-ms` seçeneğinden bağımsızdır.

Her işçi kendi CPU bütçesini tüketip CPU ve duvar saati sürelerini yazar.
Ana süreç ölçümleri bitirdikten sonra `waitpid` ile işçilerin başarıyla
sonlandığını doğrular ve sonuç kayıtlarını okur. Dolayısıyla programın toplam
çalışma süresi yalnızca kısa işlerin ölçüm penceresi değildir; arka plan
işçilerinin tamamlanması da beklenir. Küçük işçi bütçeleri seçilirse işçiler
kısa iş örneklerinin tamamından önce bitebilir.

### 4.5. Saat kaynakları ve hesaplama işi

`CLOCK_PROCESS_CPUTIME_ID`, sürecin CPU üzerinde gerçekten harcadığı zamanı
ölçer. Süreç kuyrukta beklerken bu saat aynı biçimde ilerlemez.
`CLOCK_MONOTONIC` ise uyanma hedeflerini ve duvar saati sürelerini ölçer.

`burn`, `volatile` bir değişken üzerinde tam sayı işlemleri yapar ve süreç CPU
saatini denetler. Hedef süre alt sınırdır; bir döngünün ve saat okumasının
maliyeti nedeniyle ölçülen süre hedefi biraz aşabilir. Bu, sabit sayıda işlem
yapan bir hız testi değildir: farklı işlemci hızlarında hedef CPU süresi
korunurken yapılan döngü sayısı değişebilir. CPU saati kontrolünün işlem maliyeti
de çalışma yükünün parçasıdır.

### 4.6. Periyodik kısa iş döngüsü

Örnek `i` için hedef zaman `epoch + i × period` olarak hesaplanır.
`clock_nanosleep`, `CLOCK_MONOTONIC` ve `TIMER_ABSTIME` ile bu mutlak zamana
bekler. Böylece her periyot önceki örneğin gerçek bitişinden türetilmez.

Uykudan döner dönmez uyanma gecikmesi kaydedilir; ardından kısa CPU işi
çalıştırılır ve tamamlanma gecikmesi ölçülür. Önceki iş geç bitmişse sıradaki
mutlak hedef geçmişte kalabilir. Örnekler atlanmaz ve hedefler ileri taşınmaz;
biriken gecikme sonraki örneklerde de görülebilir.

### 4.7. JSON alanları

Program başarılı koşunun sonunda tek JSON nesnesi üretir.

| Alan | Açıklama |
|---|---|
| `kind` | Çıktı türü: `linux_baseline`. |
| `kernel` | Çalışan Linux çekirdeğinin sürüm metni. |
| `cpu` | Seçilen mantıksal CPU numarası. |
| `scheduler` | Doğrulanmış `SCHED_OTHER` sınıfı. |
| `workers`, `sample_count` | İşçi ve kısa iş örneği sayıları. |
| `period_ms`, `burst_us`, `worker_cpu_budget_ms` | Koşunun istenen iş yükü parametreleri. |
| `wake_mean_ms` | Örnek uyanma gecikmelerinin aritmetik ortalaması. |
| `wake_p50_ms`, `wake_p95_ms` | Uyanma gecikmelerinin en yakın sıra yöntemiyle yüzdelikleri. |
| `wake_max_ms` | Koşudaki en yüksek uyanma gecikmesi. |
| `samples` | Her kısa iş örneğinin ayrıntıları. |
| `background` | Tamamlanan arka plan işçilerinin süreleri; sıfır işçide boş liste. |

`samples` içindeki alanlar:

| Alan | Açıklama |
|---|---|
| `index` | Sıfırdan başlayan örnek numarası. |
| `release_offset_ms` | İlk örneğin hedefinden itibaren planlanan ofset; `index × period_ms`. |
| `wake_lateness_ms` | Uykudan dönüşte okunan zaman − planlanan uyanma zamanı. |
| `completion_latency_ms` | Kısa CPU işi bittikten sonraki zaman − planlanan uyanma zamanı. |
| `cpu_ms` | Kısa işte gerçekten harcanan süreç CPU süresi. |

`background` kayıtları `id`, `wall_ms` ve `cpu_ms` içerir. `wall_ms`, işçinin
hesaplamaya başlamasından hesaplamayı bitirmesine kadar geçen kendi duvar saati
süresidir; ortak örnek başlangıcından veya `fork` anından ölçülmez.

Uyanma gecikmesi saf çekirdek çalışma kuyruğu gecikmesi değildir. Timer
çözünürlüğü, zamanlayıcı davranışı, kesmeler, sanallaştırma ve ortam yükü ölçüme
katkıda bulunabilir. Tamamlanma gecikmesi bunlara kısa CPU işinin yürütülmesini
de ekler. Modeldeki `response_ms` ile bu alanlar doğrudan aynı ölçüm değildir.

### 4.8. Yüzdelikler

Yüzdelikler örnekleri küçükten büyüğe sıralayıp `ceil(p × n / 100)` sırasındaki
değeri seçer. Sıra burada 1'den başlar. Örneğin 40 örnekte P95, 38. sıradaki
değerdir. P50, çift sayıda örnekte ortadaki iki değerin ortalamasını almak zorunda
değildir; yine aynı en yakın sıra tanımı kullanılır.

P95 değeri bir gözlem özetidir. Tek başına güven aralığı, bütün olası en kötü
durumların sınırı veya genel bir gecikme garantisi değildir.

## 5. Otomatik testlerin kapsamı

Test paketi 11 model ve 2 gerçek Linux test yöntemi içerir. Bazı yöntemler farklı
girdiler üzerinde alt testler yürütür; bunlar ayrı üst seviye test sayısı değildir.

| Test | Kontrol edilen özellik |
|---|---|
| `test_single_task_and_initial_idle` | Geç gelen tek görevin boş CPU'da hemen başlaması ve doğru bitmesi. |
| `test_known_round_robin` | İki görev için analitik RR başlangıç/bitiş takvimi. |
| `test_input_order_does_not_choose_priority` | Aynı iş yükünde CSV satırlarını ters çevirmenin görev sonuçlarını değiştirmemesi. |
| `test_interactive_preference_in_controlled_case` | Seçili küçük örnekte etkileşimli ilk yanıtın RR'ye göre erkene gelmesi. |
| `test_budget_gives_background_cpu_under_interactive_pressure` | Seçili örnekte bütçe sonrası arka plan işinin başlaması ve ilerlemesi. |
| `test_aging_bypasses_large_interactive_budget` | Seçili örnekte yaşlandırmanın sınıf tercihinden önce devreye girmesi. |
| `test_no_artificial_idle_when_only_interactive_tasks` | Tek sınıflı örnekte bütçe tükenmesinin yapay boşluk oluşturmaması. |
| `test_background_only_matches_rr` | Seçili yalnız arka plan iş yükünde iki politikanın aynı sonucu vermesi. |
| `test_randomized_accounting_and_all_tasks_complete` | Sabit tohumla üretilen 20 yükte iki politika için tamamlanma ve süre muhasebesi. |
| `test_invalid_workloads_rejected` | Seçili bozuk CSV, sınıf, sayı, tekrar ve CPU ihtiyacı girdilerinin reddi. |
| `test_invalid_options_rejected` | Seçili geçersiz model seçeneklerinin reddi. |
| `test_real_measurements_with_and_without_workers` | 0 ve 2 işçiyle dört örnekli gerçek koşuların başarılı bitmesi, JSON sayıları ve süre özellikleri. |
| `test_invalid_measurement_options_rejected` | Seçili geçersiz Linux ölçüm seçeneklerinin reddi. |

Rastgele testlerde aynı tohum kullanılır; girdiler tekrar üretilebilir. İlk görev
0. ms'de hazırdır ve 80 ms CPU ihtiyacı vardır; bütün görevler de ilk 15 ms içinde
gelir. Bu örneklerde CPU boşluğu yoktur; son bitişin toplam CPU ihtiyacına eşitliği
bu koşul altında kontrol edilir.

Gerçek Linux testleri performansın belirli bir eşikten iyi olmasını veya yük
arttığında gecikmenin mutlaka artmasını şart koşmaz. Sonuçların sonlu olması,
örnek/işçi sayıları, süre alt sınırları ve yüzdelik sıralaması gibi temel
özellikler doğrulanır. Bunlar çekirdek politikasının doğru uygulandığını,
parametrelerin en iyi olduğunu veya bütün iş yüklerinde açlık olmayacağını
kanıtlamaz. Girdi uzayının tamamı ve bütün hata/sinyal durumları test edilmez.

## 6. Deney yürütücüsü ve sonuçların izlenebilirliği

### 6.1. Yürütme sırası

`run_experiments.py` şu adımları uygular:

1. İstanbul saat diliminde zaman damgalı yeni bir sonuç dizini oluşturur.
2. `make all` ile derlemeyi doğrular.
3. Test paketini çalıştırır; çıktı ve hata akışlarını `tests.txt` içinde saklar.
4. Başarısız, sıfır testli veya atlanan test bildiren koşuda ilerlemeyi durdurur.
5. `workloads/` içindeki CSV dosyalarını sıralı biçimde her iki politika ile yürütür.
6. Üç tekrarın her birinde önce sıfır, sonra iki işçili gerçek Linux koşusu yapar.
7. Ortam, parametreler, dosya adları, metrik özetleri ve kaynak özetlerini
   `summary.json` dosyasına yazar.
8. Yalnızca bütün adımlar başarılı olduğunda `results/latest.json` işaretçisini
   geçici dosya üzerinden atomik olarak değiştirir.

Depodaki mevcut üç iş yüküyle altı model koşusu yapılır. Yeni CSV dosyaları
eklenirse betik onları da işleme alır. Gerçek ölçüm düzeninde altı koşu ve koşu
başına 40 örnek bulunur: toplam 240 kısa iş gözlemi. Koşu sırası rastgeleleştirilmez;
bu ilk düzenekte zamanla değişen ortam etkileri bütünüyle dengelenmiş değildir.

Model koşularının parametreleri `quantum=4`, `window=20`, `budget=8`, `aging=20`
olarak açıkça verilir. Gerçek koşularda `period_ms=20`, `burst_us=500` ve
işçi başına `worker_ms=800` kullanılır.

### 6.2. Özet alanları

`summary.json` içindeki temel bölümler şöyledir:

- `created_at`: saat dilimi bilgisi içeren deney başlangıç zaman damgası.
- `environment`: çekirdek, mimari, dağıtım adı, izinli CPU kümesi ve görünür
  sched_ext/BTF dosyalarına ilişkin gözlemler. Varsa cgroup CPU/bellek dosyaları
  da okunur; bunlar deney öncesindeki anlık ortam bilgileridir.
- `tests`: mevcut test paketinin başarı, hata ve atlama sayıları.
- `policy_parameters`: modelin açıkça kullanılan parametreleri.
- `model`: iş yükü ve politika bazında özet metrikler ile ham CSV dosyası adı.
- `linux_baseline`: tekrar/işçi sayıları, koşu metrikleri, ham JSON dosyası adı ve
  arka plan işçilerinin duvar saati süreleri.
- `source_sha256`: seçili kaynak ve belge dosyalarının SHA-256 içerik özetleri.

Model özetinde `task_count` ve en büyük `finish_ms` değerinden hesaplanan
`makespan_ms` vardır. Bu son değer zaman ekseninin başlangıcından itibaren
ölçülür; ilk görev geç geliyorsa başlangıç boşluğu da sayılır. Her görev sınıfı
için sayı, ortalama/P95 ilk yanıt, ortalama toplam bekleme ve ortalama dönüş süresi
hesaplanır. Bir sınıfta görev yoksa o sınıf için yalnızca sıfır sayısı yazılır.

SHA-256 değerleri, koşuyla ilişkilendirilmiş dosya içeriklerinin sonradan
karşılaştırılmasını sağlar. Bu kayıt bir dijital imza, güvenilir zaman damgası
veya donanım/ortamın değişmediğine dair garanti değildir. Betik özetleri koşular
bittikten sonra alır; aynı anda kaynak düzenlemekten kaçınılmalıdır.

`sched_ext_visible` ve `btf_visible` yalnızca ilgili dosya yollarının varlığını
bildirir. Dosyanın görünmesi tek başına yükleme yetkisini veya politika
uyumluluğunu doğrulamaz; görünmemesi de tek başına bütün çekirdek yapılandırması
hakkında kesin hüküm vermez.

### 6.3. Sonuç dosyalarının saklanması

Örnek sonuç dizini yapısı:

```text
results/
  latest.json
  week2-.../
    tests.txt
    summary.json
    model-mixed-rr.csv
    model-mixed-interactive.csv
    model-cpu_only-rr.csv
    model-cpu_only-interactive.csv
    model-interactive_pressure-rr.csv
    model-interactive_pressure-interactive.csv
    linux-workers0-run1.json
    linux-workers2-run1.json
    ...
```

Başarısız koşudan kalan kısmi dosyalar kendi dizininde kalabilir; son başarılı
koşu işaretçisi bunlara yönlendirilmez. `build/` ve `results/`, `.gitignore`
tarafından dışlanır. Bu nedenle yerelde üretilen bütün ham sonuçlar otomatik
olarak GitHub deposuna eklenmez. Kalıcı olarak paylaşılacak deney kayıtları
ilgili araştırma raporuyla birlikte ayrıca seçilip sürümlendirilmelidir.

### 6.4. PDF ve grafiklerin yeniden üretilmesi

`make presentation`, sürümlendirilmiş ilk deney grubunu okuyarak üç PNG grafiği
ve 18 slaytlık PDF sunumu üretir. Yeni deney çalıştırmaz ve tarihsel arşivi
değiştirmez. Grafikler model karşılaştırmasını gerçek Linux başlangıç ölçümünden
ayrı gösterir. Kontrollü zaman çizelgesi, otomatik testte kullanılan görev
tanımından türetilmiştir.

Bu hedef için isteğe bağlı ReportLab 4.4.9 ve Matplotlib 3.10.8 kullanılır;
bağımlılıklar `requirements-presentation.txt` içinde belirtilmiştir. Fontlar
Matplotlib ile gelen DejaVu ailesinden alınır. Yalnızca PDF'i okumak veya C
uygulamasını derleyip test etmek için bu ek bağımlılıklar gerekli değildir.
Kurulum ve yeniden üretim komutları [ana sayfada](../../README.md) yer almaktadır.

Üretici, test/örnek sayısı ve kullanılan JSON kayıtlarının bazı alanları için
tutarlılık kontrolleri yapar. Bu kontroller arşivin bütünlük dosyasının yerini
almaz; ham veri bütünlüğü ayrıca `sha256sums.txt` üzerinden denetlenebilir.
Sabit girdilerle PDF ve grafiklerin byte düzeyinde yeniden üretilebilirliği
ilk sunum hazırlanırken kontrol edilmiştir.

## 7. Sonuçların yorumlanması ve sonraki aşama

Model, tanımlanan görevler altında politika kurallarının etkisini incelemeye ve
algoritmayı denetlenebilir örneklerle geliştirmeye yarar. Linux başlangıç
ölçümü ise mevcut ortamda gerçek süreçlerin davranışını kaydeder. İki programın
çıktısı birbirinin yerine kullanılamaz.

Linux'a karşı bir iyileşme değerlendirmesi, özel politikanın uygun çekirdek ve
yetkilerle ayrı bir test ortamına yüklenmesini; aynı iş yüklerinin varsayılan
ve özel politikada tekrarlanmasını gerektirir. Kısa görevlerin gecikmesiyle
birlikte uzun işlerin tamamlanması, adalet ve uygulama maliyeti de incelenmelidir.
Bu aşamadaki az örnekli, tek CPU'lu ölçümler genel performans veya çok çekirdek
davranışı için sonuç üretmez.
