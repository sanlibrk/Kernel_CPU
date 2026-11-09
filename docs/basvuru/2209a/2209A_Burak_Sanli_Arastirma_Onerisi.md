# ARAŞTIRMA ÖNERİSİ

## GENEL BİLGİLER

| Alan | Bilgi |
|---|---|
| Proje başlığı | Etkileşimli Görevlerde Yanıt Süresini İyileştirmeye Yönelik Bütçe ve Yaşlandırma Tabanlı CPU Zamanlama Politikasının Geliştirilmesi |
| Proje yürütücüsü | Burak Şanlı |
| Üniversite / bölüm | Harran Üniversitesi / Bilgisayar Mühendisliği |
| Akademik danışman | Prof. Dr. Dursun Akaslan |
| Başvuru türü | Bireysel |
| Proje süresi | 6 ay |



# ÖZET

CPU yoğun arka plan işleriyle birlikte çalışan kısa görevlerin yanıt süresi, uzun işlerin ilerlemesi ve zamanlama maliyeti birlikte değerlendirilmesi gereken bir kaynak paylaşımı problemidir. Bu projenin amacı, sabit pencereye bağlı sınırlı etkileşimli tercih bütçesiyle yaşlandırmayı birleştiren CPU zamanlama politikasını geliştirmek ve hangi yüklerde yararlı veya yetersiz olduğunu belirlemektir. Katkı, mevcut adil zamanlama altyapısını bütünüyle değiştirme iddiasından ziyade açık görev sınıfları için gecikme–ilerleme dengesinin uygulanması ve kontrollü ölçümüdür.

Altı aylık çalışma; test ortamının doğrulanması, referans modelin genişletilmesi, uygun çekirdek altyapısında politika uygulaması ve tekrarlanabilir karşılaştırmalardan oluşmaktadır. Ön çalışmada C modeli, gerçek süreç ölçüm aracı ve 13 başarılı test yöntemi hazırlanmıştır. Modelde karışık yükün ilk yanıtı iyileşirken yoğun etkileşimli yükün toplam beklemesi artmıştır. Özel politika henüz çekirdeğe yüklenmemiştir; ön bulgular gerçek Linux performans artışı olarak sunulmamaktadır.

Ana deney tasarımında üç yük ailesi iki yoğunluk düzeyinde incelenecektir. Varsayılan ve özel politika, hücre başına en az 10 eşleştirilmiş blokla toplam en az 120 koşuda karşılaştırılacaktır. Kısa görev içeren dört hücredeki 80 koşuda en az 1.000'er kısa görev gözlemi toplanacak; saf arka planın iki hücresindeki 40 koşuda sabit iş miktarının tamamlanması ve işlem hacmi ölçülecektir. Gecikme koşularında arka plan yükü bütün gözlem penceresi boyunca sürdürülecektir. P95 gecikme, ilerleme ve maliyet birlikte analiz edilecek; koşul sırası kontrol edilerek belirsizlik ve olumsuz sonuçlar raporlanacaktır.

Proje yönetimi beş ölçülebilir iş adımı ve doğrulanabilir geri dönüş planına dayanmaktadır. Mevcut kişisel bilgisayar ve açık kaynak araçları kullanılacak; ek ekipman veya ücretli hizmet alımı planlanmayacaktır. Beklenen çıktılar, test edilmiş politika prototipi, sürümlendirilmiş iş yükleri ve deney kayıtları, bileşen etkilerini açıklayan karşılaştırmalar ve yeniden üretim belgeleridir. Sonuçların sistem programlama eğitimi ve sonraki kaynak yönetimi araştırmaları için kullanılabilir bir değerlendirme altyapısı sağlaması hedeflenmektedir.

Anahtar kelimeler: CPU zamanlama, etkileşimli görev, yaşlandırma, kaynak paylaşımı, deneysel değerlendirme.

# 1. ARAŞTIRMA ÖNERİSİNİN BİLİMSEL NİTELİĞİ

## 1.1. Konunun Önemi ve Araştırma Önerisinin Bilimsel Niteliği

CPU zamanlama, etkileşimli görevlerin kısa sürede yanıt vermesiyle uzun hesaplama işlerinin ilerlemesini birlikte etkiler. İlk yanıt, toplam bekleme, tamamlanma süresi, kaynak paylaşımının adaleti ve zamanlama maliyeti aynı ölçüt değildir. Bu araştırma, mevcut sistemlerin kısa görevlere hiç destek vermediği veya adalet mekanizmasının bulunmadığı iddiasına dayanmamaktadır.

CFS tasarımı görev ağırlıklarını ve sanal çalışma zamanını temel alarak adil paylaşımı ele alır (Linux Kernel Community, 2024a). EEVDF, uygunluk ve sanal son teslim zamanı üzerinden adil sınıfta görev seçimini düzenler (Linux Kernel Community, 2024b). sched_ext ise başlı başına yeni bir zamanlama algoritması değil, BPF programlarıyla politika geliştirilebilen bir çekirdek altyapısıdır (Linux Kernel Community, 2024c; 2024d). İncelenen scx_simple örneğinin varsayılan davranışı ağırlıklı sanal zaman seçimidir; FIFO kipi ayrıca etkinleştirilir. Aynı örneğin kaynak açıklaması, CPU yoğun görevlerin FIFO kipinde etkileşimli görevleri geride bırakabildiğini belirtmektedir (Linux Kernel Community, 2024c; 2024d). Bu ayrım, karşılaştırmada hem politika kurallarının hem kullanılan çerçevenin açıkça tanımlanmasını gerektirir.

Bu projenin ele aldığı somut sorun, açıkça belirtilen kısa/periyodik görevlerle CPU yoğun uzun görevlerin aynı işlemciyi paylaştığı koşullarda, kısa görevlere verilen tercihin ne zaman yararlı olduğu ve bunun uzun görevlerin ilerlemesine hangi maliyeti getirdiğidir. Önerilen politika, sabit zaman penceresi içindeki sınırlı etkileşimli tercih bütçesini son bekleme başlangıcına dayalı yaşlandırmayla birleştirir. Mevcut adil zamanlayıcının genel kaynak paylaşımı hedefini yeniden tanımlamak yerine, iki görev sınıfı için açık bir gecikme–ilerleme denge kuralını araştırır. Bütçe ve yaşlandırmanın tek tek etkileri, aynı altyapıda bu bileşenlerin kaldırıldığı ek kontrol sürümleriyle incelenecektir.

Araştırma sorusu şöyledir: Sınırlı tercih bütçesi ve yaşlandırma kullanan politika, tanımlı karma yüklerde kısa görevlerin P95 uyanma gecikmesini azaltırken arka plan ilerlemesini ve tamamlanmasını önceden belirlenen sınırlar içinde koruyabilir mi? Araştırma hipotezi, bunun bazı karma yük koşullarında sağlanabileceği; yoğun talepte ise bütçe, ilk yanıt ve toplam bekleme arasında ölçülebilir ödünleşimler oluşacağıdır. Evrensel üstünlük veya literatürde ilk algoritma olma iddiası kurulmamaktadır.

Ön çalışmadaki modelde karışık yükün ortalama ilk yanıtı 11 ms'den 3 ms'ye inerken, yoğun etkileşimli yükte toplam ortalama bekleme 252,667 ms'den 303,833 ms'ye yükselmiştir. Bu karşı örnek, birinci çalışmaya erişim ile bütün işin bitişini birlikte inceleme gereğini somutlaştırmaktadır. Bilimsel katkı; kural bileşiminin gerçek çekirdekte uygulanması, varsayılan davranışla eşleştirilmiş ölçümü, tekil bileşen kontrolleri ve yararlı/zararlı yük koşullarının açıklanmasıdır. İlk sürüm açık görev sınıfları ve tek ölçüm CPU'suyla sınırlıdır; otomatik sınıflandırma, genel çok çekirdek yerleşimi, bellek ve termal yönetim temel hedef değildir.

## 1.2. Amaç ve Hedefler

Amaç, bütçe ve yaşlandırma tabanlı politika kurallarını denetlenebilir referans modelden gerçek çekirdek deneyine taşıyarak gecikme, ilerleme ve uygulama maliyeti arasındaki dengeyi belirlemektir. Altı aylık çalışmanın ölçülebilir hedefleri şunlardır:

1. Birinci iş adımında hedef çekirdeğin tam sürümünü ve yapılandırmasını, BPF/BTF araçlarını, yükleme yetkilerini ve geri yüklenebilir test ortamını kaydetmek; örnek politikanın yüklenmesi, kaldırılması ve varsayılan zamanlamaya dönüşünü üç ardışık denemede doğrulamak.
2. İkinci adımda görev kabulü, kuyruk sırası, bütçe yenilenmesi, yaşlandırma ve istisnaları tanımlanmış modeli genişletmek; üç iş yükü ailesini ve sınır/karşı örnekleri oluşturmak.
3. Üçüncü adımda aynı kuralları uygun sched_ext altyapısında uygulamak; görev bitişi, sayaç tutarlılığı, sınıf kabulü, bütçe muhasebesi ve güvenli geri dönüş dahil toplam en az 25 test yöntemi veya ayrı kayıtlı doğrulama senaryosu hazırlamak. Mevcut 13 test bu hedefin ön çalışma kısmıdır; kalan testler yapılmış kabul edilmez.
4. Dördüncü adımda üç aile ve iki yoğunluk düzeyinden oluşan altı hücrede en az 10 eşleştirilmiş blok yürütmek: varsayılan ve özel politika için toplam en az 120 ana koşu. Bunların 80'i kısa görev içeren gecikme koşusu, 40'ı saf arka plan koşusudur. Yalnız 80 gecikme koşusunun her birinde en az 1.000 kısa iş gözlemi toplanacaktır.
5. Beşinci adımda seçili karma yüklerde FIFO referansı ve bütçesiz/yaşlandırmasız sürümlerle ek kontroller yapmak; bütün ana hücrelerde olumlu ve olumsuz bulguları, belirsizliği, ilerleme kaybını ve maliyeti birlikte raporlamak.

Öncelikli gecikme ölçütü, kısa görev içeren koşulardaki P95 uyanma gecikmesidir. Saf arka plan koşularında kısa görev bulunmadığından bu ölçüt hesaplanmaz. Bu hücrelerde sabit iş miktarının tamamlanma süresi ve işlem hacmi kullanılır. Başlangıç mühendislik hedefi, önceden seçilmiş karma yükte P95 gecikmenin en az yüzde 20 azalması ve uzun işlerde koruyucu ilerleme/tamamlanma ölçütünün yüzde 10'dan fazla bozulmamasıdır. Bu oranlar ölçülmüş kazanç değildir. Birincil hücre 20 ms periyotlu, iki arka plan işçili karma koşuldur; ilerleme koruması aynı koşuldaki doğrulanmış hesaplama parçalarının saniyedeki sayısına dayanır. Ana deneyler başlamadan örnekleme, dışlama ve analiz kuralları kayda alınacaktır. Geliştirme adımlarının başarıyla bitmesi hipotezin mutlaka doğrulanmasını gerektirmez; hedef karşılanmazsa etki ve geçerlilik sınırları raporlanacaktır.

# 2. YÖNTEM

### Araştırma tasarımı ve ön çalışma

Çalışma iki katmandan oluşur: modelde kuralların işlevsel doğrulanması ve gerçek çekirdekte eşleştirilmiş karşılaştırma. Modeldeki Round Robin, kuralları açıklamak için referanstır; varsayılan adil zamanlayıcının taklidi değildir. Gerçek ana deney, aynı çekirdek ve sanal makine kaynaklarında varsayılan zamanlama ile özel politika arasında yapılacaktır (Linux Kernel Community, 2024a; 2024b; 2024c; 2024d).

Ön çalışmada C modeli, gerçek süreç ölçüm programı ve deney betiği hazırlanmış; 13 test yöntemi başarılı olmuştur. Üç model senaryosu iki politikayla çalıştırılmış, mevcut SCHED_OTHER altında altı koşuda toplam 240 kısa iş gözlemi kaydedilmiştir. Özel politika henüz çekirdeğe yüklenmemiştir. Modeldeki 11→3 ms ilk yanıt değişimi ve yoğun yükteki bekleme gerilemesi, tasarımın uygulanabilirliğini ve araştırılacak ödünleşimi göstermektedir; Linux üzerinde performans artışını kanıtlamaz.

### Hedef ortam ve sürüm kontrolü — iş adımı 1

Geliştirme ana bilgisayardan ayrı, geri yüklenebilir bir test sanal makinesinde yürütülecektir. Tek bir çekirdek kaynak etiketi/commit'i, yapılandırma, derleyici ve yükleyici sürümleri seçilip sabitlenecektir. Linux v6.12 upstream belgeleri ve aynı sürümün scx_simple kaynağı teknik başlangıç noktasıdır; nihai seçilen sürümün API'leri ilk adımda doğrulanacaktır (Linux Kernel Community, 2024c; 2024d). Sürüm numarası veya bir dosyanın görünmesi tek başına destek ve yetki kanıtı sayılmayacaktır.

CONFIG_SCHED_CLASS_EXT, BPF sistem çağrısı, BPF derleme desteği, BTF verisi ve kullanıcı alanı yükleyicisinin örnek programı derleyip yükleyebilmesi ayrı kontrollerdir. Durum dosyası, etkin politika adı, yükleyici çıkışı ve görev ilerlemesi kayda alınacaktır. Örnek politikanın kontrollü sonlandırılması, varsayılan zamanlamaya dönüş ve sanal makine görüntüsünden geri yükleme denenecektir. Yükleme ve geri dönüş sağlanmadan özel politika geliştirmesine geçilmeyecektir.

Doğrulanmış kişisel donanım ve mevcut yazılım envanteri 3.3 bölümündedir; kullanılabilir disk ve hedef misafir kaynakları ilk adımda ayrıca ölçülecektir. Kurum tahsisi varsayılmamaktadır. QEMU tabanlı ayrı test misafiri başlangıç seçeneğidir; donanım hızlandırma mevcut değilse TCG yazılımsal emülasyon yolu pilotta denenecektir. Konuk görüntüsü ve yürütme kipi her karşılaştırma çiftinde aynı tutulacak, emülasyon sonuçları yerel fiziksel sistem kazancı olarak genellenmeyecektir. Ölçümde kullanılan sanal CPU/bellek tahsisi, yürütme arka ucu, izinli CPU kümesi ve nice/cgroup durumu bütün eşleştirilmiş koşullarda aynı tutulacaktır. Çekirdek deneylerinin başarı ölçütü WSL içinde politika yüklemek değildir; WSL derleme ve kullanıcı alanı testleri için kullanılabilir, politika destekli ayrı misafir sistem gereksinimi bağımsız doğrulanır.

### Politika durumu ve çekirdeğe aktarım — iş adımları 2 ve 3

İlk sürümde sınıflar otomatik çıkarılmayacaktır. Deney yükleyicisi kısa/periyodik ve arka plan görevlerini oluşturacak; görev kimliği ve sınıfı açıkça kaydedecektir. Seçilen sürümün kısmi katılım desteğiyle yalnız deney görevlerinin özel politikaya alınması hedeflenir; kullanılan katılım kapsamı, varsayılan karşılaştırmada aynı görev kümesi ve CPU yerleşimiyle eşleştirilir. PID yeniden kullanımı, görev çıkışı ve sınıflandırılmamış görev davranışı doğruluk senaryolarında sınanacaktır. Deney süreçleri başlangıç bariyerinde bekletilecek; sınıf ve katılım kayıtları tamamlandıktan sonra serbest bırakılacaktır. Sınıf seçimini atlayabilen doğrudan yerel dispatch optimizasyonları ilk sürümde kullanılmayacaktır.

Görev başına sınıf, son hazır kuyruğa giriş zamanı, kuyruk sıra numarası ve çalışma muhasebesi tutulacaktır. İlk sürüm, ön çalışmayla uyumlu olarak en fazla 256 eşzamanlı görev kaydıyla sınırlandırılacak; kapasite aşımı test edilecektir. İki sınıf FIFO kuyruğu ve hazır görev sayacı kullanılacak; yaşlandırma için kuyruk başlarındaki en eski bekleme karşılaştırılacaktır. İşlemler BPF doğrulayıcısının kabul edeceği sınırlı yapılarla gerçekleştirilecek; kullanıcı alanına her seçimde gidilmeyecektir. Görev çıkışı veya geçersiz kayıtların temizlenmesi sınırlı adımlı olacak; kayıt kapasitesinin aşılması sessiz görev kaybı yerine görünür hata ve güvenli geri dönüşle ele alınacaktır.

Politika 4 ms başlangıç zaman dilimi, 20 ms sabit duvar zamanı penceresi, 8 ms etkileşimli çalışma bütçesi ve 20 ms yaşlandırma eşiğiyle başlayacaktır. Bunlar optimum olduğu gösterilmiş değerler değildir. Duvar saati pencere sınırını belirler; bütçe ise görevin CPU üzerinde gerçekten çalıştığı süreyle tüketilir. Bekleme süresi bütçeden düşülmez. CPU muhasebesi için sabitlenmiş çekirdekte doğrulanabilir görev çalışma sayacı kullanılacak; çalışma başlangıç/bitiş geri çağrılarında fark alınarak sayaç tutarlılığı analitik yüklerle kontrol edilecektir. Kalan dilime dayalı muhasebe kullanılırsa gönüllü yield'in dilimi sıfırlayabildiği durum ayrıca ele alınacak, otomatik olarak bütün dilim tüketilmiş sayılmayacaktır (Linux Kernel Community, 2024c; 2024d).

Enqueue, dispatch ve çalışma/durma olaylarında durum güncellenecektir. Çekirdek uygulaması her milisaniyede kullanıcı alanında dönen bir simülasyon döngüsü olmayacaktır. Önce yaşlandırma eşiğini geçen aday; aksi halde bütçeye göre sınıf ve FIFO sıra numarası seçilecektir. Yaşlandırma son beklemeye girişten itibaren değerlendirilir; kesin gecikme üst sınırı oluşturmaz. Başka sınıfta iş yoksa CPU boş bırakılmaz; bütçenin katı kota olmadığı ve yaşlandırma istisnaları açıkça tanımlanır. Gerçek dilim sonlandırma ve bütçe/pencere sınırı davranışının modelden ayrıldığı noktalar önce modele eklenip test edilecek, eşdeğer davranış varsayılmayacaktır. Her seçimin maliyeti ve sayaç/izleme etkisi ölçüm kapsamındadır.

### İş yükleri, gözlem penceresi ve örnekleme — iş adımı 4

Ana deney üç ailede iki yoğunluk düzeyinden oluşur:

| Aile | Yoğunluk düzeyleri | İş tanımı | Ölçüt ve gözlem kuralı |
|---|---|---|---|
| Saf arka plan | Aynı ölçüm CPU'sunda 2 ve 4 uzun görev | Her görevde önceden belirlenmiş sabit hesaplama işi; girdiler ve doğrulama özeti eşit | Tamamlanma süresi, işlem hacmi ve görevler arası dağılım; kısa iş örneği ve uyanma P95'i yoktur |
| Seyrek etkileşimli karma | 20 ve 10 ms kısa iş periyodu; 2 arka plan işçisi | Her kısa iş için başlangıçta 500 µs süreç CPU hedefi; arka plan işçileri bütün ölçüm penceresi boyunca sürer | Her koşuda en az 1.000 kısa iş; P50/P95 uyanma ve tamamlanma gecikmesi, arka plan ilerlemesi |
| Yoğun etkileşimli karma | 5 ve 2 ms kısa iş periyodu; 2 arka plan işçisi | Aynı kısa iş hedefi; daha sık geliş; bütün pencere boyunca süren arka plan işi | Her koşuda en az 1.000 kısa iş; aynı gecikme ve ilerleme ölçütleri |

Bu değerler ana deneyden önce pilotta uygulanabilirliği sınanacak başlangıç düzenidir; son tanımlar ve değiştirme gerekçeleri ana veri toplanmadan sabitlenir. Gecikme koşularında 1.000 gözlem, 20 ms periyotta yaklaşık 20 saniyelik ölçüm gerektirir. Ön çalışmadaki 800 ms işçi CPU bütçesi bu pencereye doğrudan taşınmayacaktır. Yeni arka plan işçileri ısınma ve bütün ölçüm penceresi boyunca çalışacak; sabit büyüklükte doğrulanabilir hesaplama parçaları üzerinden ilerleme sayaçları üretilecektir. Kısa iş örnekleri bitince durdurma işareti verilip devam eden hesaplama parçasının bitişi ve süreç çıkışı kaydedilecektir. Uzun bir görev erken bittiği için pencerenin sessizce yüksüz hâle gelmesine izin verilmeyecektir.

Gecikme deneyinde arka plan ilerlemesi, birim duvar zamanında tamamlanan eşit hesaplama parçaları ve en uzun gözlenen ilerlememe aralığıyla ölçülür. Bu işçilerde programı durdurduğumuz süre bir sabit iş tamamlanma kazancı sayılmaz. Uzun iş tamamlanması/işlem hacmi, ayrı saf arka plan ailesinde aynı sabit toplam hesaplama işiyle değerlendirilir. İlerleme ve tamamlanma için kullanılan koruyucu ölçütlerin hangi aileye ait olduğu tablolarda açık tutulacaktır.

Kısa iş uyanma hedefleri CLOCK_MONOTONIC üzerinde mutlak olarak, kısa iş CPU bütçesi süreç CPU saatiyle ölçülecektir. Geç kalınan periyotlar atlanmayacak; birikmiş gecikme kaydedilecektir. Uyanma ölçümü timer, kesme ve sanallaştırma etkilerini kapsar; saf çekirdek kuyruk gecikmesi olarak adlandırılmayacaktır. Görev başlangıç/bitiriş, CPU ve duvar süreleri ayrı alanlardır. Saf arka plan işinde aynı girdi ve işlem sayısıyla çıktı doğrulama özeti kontrol edilecek; CPU zamanı bütçeli döngü sabit iş hacmi ölçümü yerine kullanılmayacaktır.

### Karşılaştırma, sıralama ve ek kontrol sürümleri

Altı ana hücrenin her birinde varsayılan ve özel politika için en az 10 eşleştirilmiş blok vardır: 60 çift, toplam en az 120 ana koşu. Kısa iş içeren dört hücre 80 gecikme koşusu ve koşu başına en az 1.000 kısa gözlem; saf arka planın iki hücresi 40 tamamlanma/işlem hacmi koşusu üretir. Koşul sırası blok içinde rastgeleleştirilir veya dengelenir; tohum ve sıra kaydedilir. Donanım kaynakları, çekirdek, derleme seçenekleri, nice/cgroup ayarları, CPU affinity ve iş girdileri çiftler arasında aynı tutulur. Isınma süresi ve koşular arası bekleme, pilot değişkenliğine göre ana deneyden önce belirlenir. Kaynak kısıtlaması, sanal makine yeniden başlatma veya kayıt eksikliği gibi geçersizlik nedenleri önceden tanımlanır; kötü performans tek başına dışlama nedeni olmaz.

Beşinci iş adımında sınırlı bir seçili karma yük kümesinde üç ek kontrol uygulanacaktır: aynı sched_ext altyapısında açıkça FIFO kipine alınmış scx_simple referansı, yaşlandırmanın kapatıldığı sürüm ve tercih bütçesinin üst sınırının kaldırıldığı sürüm (bu sürümde bütçe sıfırlanmaz; hazır etkileşimli görevlere yaşlandırma kuralı saklı kalmak üzere sınırsız sınıf tercihi tanınır). scx_simple'ın varsayılanı FIFO olmadığından kullanılan kip ve dilim ayrıca kaydedilir (Linux Kernel Community, 2024c; 2024d). Ek kontroller, 20 ms seyrek ve 2 ms yoğun karma koşullarda yürütülecektir. Her ek kontrol sürümü, aynı yükte tam politika ile 5 eşleştirilmiş blokta karşılaştırılır: 2 yük × 3 kontrol × 5 blok × 2 koşu = 60 ek koşu. Böylece ana deney 120, ikincil mekanizma deneyi 60, toplam plan 180 koşudur; pilot ve işlevsel testler bu sayıya dahil değildir. Birincil hipotez 120 ana koşuda değerlendirilecek, ek koşular mekanizma incelemesi olarak raporlanacaktır. FIFO referansı çerçeve/politika etkisini ayırt etmeye yardımcı olur; varsayılan zamanlayıcıyla farklı seçim semantiği kullandığından saf çerçeve maliyetini tek başına kesin olarak ayırdığı iddia edilmez. Bileşen kapatma deneyleri, bütçe ve yaşlandırmanın hangi etkiye katkıda bulunduğunu sınar.

### İlerleme, adalet ve maliyetin işlemsel tanımı

Karma koşullarda arka plan ilerlemesi, her işçinin aynı sayıda işlem içeren hesaplama parçalarından saniyede tamamladığı parça sayısıyla ölçülecektir. İşçilerin sayaçları ayrı kaydedilecek, toplam ilerleme ve en düşük bireysel ilerleme birlikte raporlanacaktır. İlerlememe aralığı, bir işçinin ardışık iki doğrulanmış parça bitişi arasındaki en uzun gözlenen duvar zamanı olarak tanımlanacaktır; parça boyutunun çözünürlük etkisi pilotta kaydedilecektir. Saf arka planda eşit toplam hesaplama işi ve doğrulanmış çıktı özeti kullanılacak; son görevin bitişi, görev bazında bitişler ve birim zamanda tamamlanan iş ölçülecektir. Birincil karma hücrede P95'in en az yüzde 20 düşmesi, toplam arka plan ilerlemesinin yüzde 10'dan fazla azalmaması ve hiçbir işçinin deney penceresi boyunca tamamen ilerlemesiz kalmaması birlikte mühendislik hedefidir. Saf arka plan hücrelerinde yüzde 10'dan büyük tamamlanma bozulması ayrıca raporlanacaktır; bir hücredeki kazanç başka hücrenin kaybını gizlemek için ortalanmayacaktır.

Adalet değerlendirmesi aynı sınıfta eşit iş isteyen iki veya dört arka plan görevinin bireysel CPU zamanları ve ilerleme dağılımıyla sınırlı tutulacaktır; farklı talepler gerekçesiz tek bir adalet sayısına indirgenmeyecektir. Süreç CPU zamanı, duvar zamanı ve mevcutsa bağlam değiştirme sayıları kaydedilecektir. Politika olay sayaçları, yükleyici CPU zamanı ve aynı seçili yükte pilot kalibrasyonu olarak yürütülen izleme açık/kapalı kontrollerinin farkı ek maliyet göstergeleri olacaktır. Bu kalibrasyon koşuları 180 deney koşusuna dahil değildir; ana ve ikincil deneylerin tümünde önceden belirlenmiş aynı izleme durumu kullanılacaktır. Doğrulanmış çekirdek izleme olanağı yoksa yalnız bu kullanıcı alanı göstergelerinden kesin BPF çalışma süresi çıkarılmayacaktır. Ek FIFO referansı ve bileşen çıkarma koşuları karar kurallarını açıklamaya yardımcı olur; farklı seçim semantiği nedeniyle yalnız FIFO–varsayılan farkı saf altyapı maliyeti sayılmaz.

### Analiz, kabul ölçütleri ve tekrar üretim

Kısa iş içeren koşularda ortalama, P50, P95 ve örnek sayıları raporlanır. P99 yalnız kuyruk örnekleme belirsizliğiyle birlikte ek ölçüt olabilir. En büyük gözlem en kötü durum garantisi değildir. Aynı koşunun ardışık 1.000 örneği bağımsız deney tekrarı sayılmaz; ana karşılaştırmanın deney birimi eşleştirilmiş koşu/bloktur.

Her ana hücre için P95'in eşleştirilmiş mutlak/göreli değişimi veya o hücrede geçerli tamamlanma/işlem hacmi değişimi hesaplanır. Payda sıfırsa göreli oran yerine mutlak fark verilir. Koşu/blok yapısını koruyan yeniden örneklemeyle yaklaşık yüzde 95 belirsizlik aralığı hesaplanabilir; en az 10 blok küçük bir örneklemdir ve aralığın kesinliği sınırlı olabilir. Birincil hücre, 20 ms periyotlu ve iki arka plan işçili seyrek etkileşimli koşuldur. Pilot, kayıt bütünlüğü ve uygulanabilirliği sınar; bu koşul değiştirilecekse neden ve yeni hücre ana veriler toplanmadan kayda alınır. Diğer ana hücreler ikincil olarak etiketlenir. Birden çok hücre için doğrulayıcı anlamlılık iddiası kurulursa çoklu karşılaştırma düzeltmesi ve kullanılan karar kuralı önceden kaydedilir. Parametre seçiminde kullanılan pilot girdileriyle son değerlendirme girdileri ayrılır.

Başarı yalnız ilk yanıt düşüşüne bağlı olmayacaktır: gecikme kazancı yanında aynı karma koşulda arka plan ilerleme kaybı ve ayrı sabit iş koşullarında uzun iş tamamlanma maliyeti değerlendirilir. Başlangıçta önerilen yüzde 20 gecikme azalışı ve yüzde 10 koruyucu bozulma sınırı, hedef niteliktedir; elde edilmiş sonuç veya evrensel eşik değildir. Pilot sonrası kesin hesaplama, hücre ve karar kuralları ana deneyden önce sabitlenir. Olumsuz sonuçlar, başarısız koşular ve politika yükleme sorunları da kayıt altına alınır.

Kaynak commit'i, çekirdek yapılandırması, araç sürümleri, tohumlar, sınıf kayıtları, ham örnekler ve dosya bütünlük özetleri saklanacaktır. Birinci iş adımı ortam/geri dönüşü, ikinci ve üçüncü adım model/çekirdek doğruluğunu, dördüncü ana karşılaştırmayı, beşinci bileşen ve sağlamlık kontrollerini karşılar. Sonlu deneylerde bütün işlerin ilerlemesi, bütün yüklerde açlık oluşmamasının ispatı olarak sunulmaz.

# 3. PROJE YÖNETİMİ

## 3.1. Çalışma Takvimi

Çalışma altı aylık sürede yürütülecektir. Aylar projenin yürürlüğe girmesinden itibaren göreli olarak tanımlanmıştır; 24 haftalık aktif çalışma bu altı aylık dönem içinde planlanmıştır. Literatür incelemesi, raporlama ve paylaşım ilgili teknik faaliyetlerin içinde yürütülecek, ayrı iş adımı olarak gösterilmeyecektir.

| Dönem | Faaliyet | Sorumlu | Başarı ölçütü | Başarıya katkı (%) |
|---|---|---|---|---|
| Ay 1 / hafta 1–4 | Deney ortamı ve örnek politika doğrulaması | Burak Şanlı | Özellik/araç/yetki kayıtları; geri yüklenebilir VM; üç başarılı yükleme-kaldırma ve dönüş denemesi | 15 |
| Ay 2 / hafta 5–8 | Politika/model genişletme ve sınır koşullarının incelenmesi | Burak Şanlı | En az üç yük ailesi; kural ve istisnaların belgelenmesi; analitik ve karşı örnek kayıtları | 20 |
| Ay 3–ilk yarı Ay 4 / hafta 9–14 | Çekirdek politika uygulaması ve işlevsel doğrulama | Burak Şanlı | Uygun çekirdekte çalışır politika; toplam en az 25 test/kontrol senaryosu; görev ilerlemesi ve geri dönüş kayıtları | 25 |
| İkinci yarı Ay 4–Ay 5 / hafta 15–20 | Pilot ve kontrollü karşılaştırmalı deneyler | Burak Şanlı | Altı hücrede 60 çift/120 ana koşu: 80 gecikme ve 40 saf arka plan; gecikme koşusu başına en az 1.000 örnek; kayıt ve dışlama gerekçeleri tam | 25 |
| Ay 6 / hafta 21–24 | Sağlamlık, maliyet ve başarısız yük koşullarının doğrulanması | Burak Şanlı | İki karma yükte üç ek kontrol için 30 çift/60 ek koşu; bileşen, maliyet ve olumsuz sonuç tabloları; tekrar üretim kontrolü | 15 |

Katkı ağırlıkları toplamı yüzde 100'dür. Akademik danışman bütün iş adımlarında bilimsel değerlendirme ve rehberlik sağlayacaktır.

## 3.2. Risk Yönetimi

| Risk ve izlenecek belirti | Önlem / B planı | Yöntem ve takvim etkisi; korunacak hedef |
|---|---|---|
| Mevcut dağıtım çekirdeğinde sched_ext/BTF bulunmaması veya örnek yüklemenin ilk iki haftada başarısız olması | Aynı araştırma sorusunu ve sched_ext yolunu koruyarak ayrı misafir sistemde uygun çekirdek kaynak etiketi seçilir; gerekli yapılandırma açılır, aynı kaynak ağacındaki örnek ve kullanıcı alanı bileşenleri derlenir. İkinci haftanın sonunda destek kararı verilir; üçüncü/dördüncü haftalar yapılandırılmış misafirin ve örnek politikanın kurulmasına ayrılır. | Çekirdeğin adil zamanlayıcısına belirsiz bir yama yazmaya geçilmez. Kaynak/araç sürümü kayda alınır; aynı misafir hem varsayılan hem özel politikada kullanılır. Birinci ayın sonunda üç yükleme-kaldırma/geri dönüş kontrolü geçmeden entegrasyon tamamlandı sayılmaz. |
| Donanım hızlandırma veya iç içe sanallaştırma bulunmaması | Önce kişisel bilgisayarda işletim sisteminin desteklediği ayrı VM arka ucu denenir. Bu mümkün değilse aynı misafir görüntüsü yazılımsal emülasyonla çalıştırılır; 1.000 gözlem penceresi korunur, duvar süresi maliyeti pilotta ölçülür. | Yürütme arka ucu aynı veri grubunda karıştırılmaz; bütün eşleştirilmiş koşullar aynı arka uçta alınır. Bulgular emülasyon ortamına koşullu açıklanır, yerel donanım genellemesi yapılmaz. Ek çok çekirdek genişletmesi çıkarılıp temel tek CPU karşılaştırması korunur. |
| Politika hatası, runnable görevlerin durması veya yükleyici çökmesi | Geri yüklenebilir misafir görüntüsü, örnek politika ile doğrulanmış sonlandırma/varsayılana dönüş ve dışarıdan misafir durdurma yolu kullanılır. Normal kapatma, yükleyicinin sonlandırılması ve kontrollü hata senaryoları üçüncü ay doğrulama paketine eklenir. | Hatalı sürüm ana ölçümde kullanılmaz. Güvenilir commit'e/görüntüye dönülür; hata kaydı, nedeni ve yeniden test sonucu saklanır. Başarısız yükleme model sonucu ile değiştirilerek çekirdek hedefi tamamlanmış gösterilmez. |
| Bütçe muhasebesinin CPU zamanı yerine beklemeyi de tüketmesi, yield veya pencere sınırında hatalı sayaç | Görev çalışma sayacı ile politika bütçesi küçük analitik CPU/uyku/yield senaryolarında karşılaştırılır; pencere sınırı ve yeniden kuyruğa giriş ayrı sınanır. API'nin sağlayamadığı davranış açıkça belgelenir ve modelde eşleştirilir. | İkinci/üçüncü adımda giderilmeden ana deney başlamaz. Eksik muhasebe ile performans kazanımı iddia edilmez; gerçek politikanın uyguladığı kural esas alınır. |
| Etkileşimli kazanç karşılığında arka plan ilerlemesinin bozulması | Bütçe ve yaşlandırma pilotta incelenir; önceden ilan edilen son deney eşikleri sonuç görüldükten sonra değiştirilmez. Ek bileşen kapatma kontrolleriyle etki araştırılır. | Hipotez kısmen veya tamamen desteklenmeyebilir; bu durum yük koşulları ve belirsizliğiyle raporlanır. Araştırma hedefi olumlu sayıyı zorlamak değil, dengeleri açıklamaktır. |
| Ön çalışmadaki kısa işçilerin ana gecikme penceresinden önce bitmesi | 800 ms ön çalışma işçisi ana deneyde tekrar kullanılmaz. Yeni sürekli işçiler ısınma ve bütün örnekleme penceresi boyunca ilerleme sayacı üretir; başlangıç/bitiriş ve yük varlığı kaydedilir. | Gözlem penceresinin bir kısmının sessizce yüksüz kalması önlenir. Gerçekten eksik/yanlış başlatılan koşu, önceden tanımlanmış işlevsel geçersizlik gerekçesiyle ayrı kaydedilip tekrarlanır. |
| Yüksek ortam gürültüsü, eksik kayıt veya VM arka ucu değişimi | Eşleştirme, sıra rastgeleleştirme, ortam kaydı ve pilot tekrar planı uygulanır. Kaynak değiştiğinde veri grubu ayrı tutulur; önceden tanımlı eksik-kayıt kuralları kullanılır. | Tekrarlama artırılabilir; yetersiz kesinlik sürerse belirsizlik ve ortamla sınırlı sonuç raporlanır. Kötü gecikme veya hipotezin desteklenmemesi dışlama nedeni değildir. |
| İş takviminin genişlemesi | Beşinci adımın ek parametre/bileşen hücreleri daraltılır; otomatik sınıflandırma ve çok çekirdek zaten temel hedef dışındadır. | Üç aile × iki yoğunluk × 10 eşleştirilmiş bloktan oluşan ana tasarım ile güvenli yükleme/geri dönüş korunur. B planı için model-only tamamlanma veya onaysız kurum donanımı varsayılmaz. |


## 3.3. Araştırma Olanakları

Proje, yürütücünün mevcut kişisel bilgisayarında ve açık kaynak geliştirme araçlarıyla yürütülecektir. Yürütücünün sağladığı sistem çıktısına göre işlemci i7-12650H modeli 12. nesil bir işlemcidir; toplam fiziksel bellek yaklaşık 15,7 GiB'dir. Bu bilgiler mevcut donanımı tanımlar; kurum laboratuvarı veya ek cihaz tahsisi varsayılmamaktadır. Windows üzerinde kurulu Ubuntu/WSL ortamında C derlemesi ve 13 test yöntemi başarıyla tamamlanmıştır. Sağlanan paket kayıtlarında GCC 15 ve Python 3.14 yer almaktadır. Bu doğrulama, hedef misafir çekirdeğin sched_ext/BTF desteğini veya iç içe donanım hızlandırmayı doğrulamamaktadır.

Çekirdek deneyleri için ayrı misafir sisteme başlangıçta 2 sanal CPU ve 4 GiB RAM ayrılması hedeflenmektedir. Ölçüm görevleri tek misafir CPU'ya sabitlenecek; işletim sistemi ve yönetim için diğer sanal CPU kullanılabilecektir. Bu tahsis kurulu bir kaynak olarak değil ilk iş adımında sınanacak yapılandırma olarak tanımlanmıştır. Kullanılabilir disk alanı, sanallaştırma arka ucu ve host kaynak baskısı ilk hafta kaydedilecektir. Geri yüklenebilir disk görüntüsü ve çekirdek derleme alanı için yeterli boş alan doğrulanmadan kaynak tahsisi tamamlanmış sayılmayacaktır. Konuk CPU yerleşimi, host güç modu ve eşzamanlı yük eşleştirilmiş ölçümlerde sabit/kayıtlı tutulacak; farklı yürütme arka uçları aynı veri grubunda birleştirilmeyecektir.

Hazır yazılım olanakları; C tabanlı referans model, gerçek Linux başlangıç ölçüm programı, üç iş yükü ailesi, otomatik testler, deney betiği ve özgün ham veri arşividir. 5 Kasım 2026 tarihli ilk Debian/Linux veri grubu, yerel Ubuntu test doğrulamasından ayrı tutulmaktadır. Yeni çekirdek destekli misafir sistem kurulumu, olay tabanlı politika ve uzun gözlem penceresine uygun ana deney yükleri planlanan geliştirmelerdir. Mevcut olanaklarla yürütme tercihine göre ek ekipman, ücretli hizmet, seyahat veya sarf alımı öngörülmemekte; yeni gider planı 0 TL'dir. Destek talebinin sisteme uygunluğu ve gereken idari işlemler, resmî başvuru aşamasında kontrol edilecektir.

# 4. ARAŞTIRMA ÖNERİSİNİN YAYGIN ETKİSİ

| Kategori | Ölçülebilir ve gerçekçi beklenen çıktı |
|---|---|
| Bilimsel / teknik | Bir politika tanımı ve uygun çekirdekte prototip; üç yük ailesini ve altı hücreyi kapsayan karşılaştırma veri grubu; gecikme, arka plan ilerlemesi ve maliyetin birlikte değerlendirildiği bir teknik rapor. |
| Eğitim / insan kaynağı | Sistem programlama, çekirdek araçları ve deney tasarımını açıklayan yeniden üretim yönergeleri; test ve iş yükü örneklerinin en az bir bölüm içi teknik sunumla paylaşılması. |
| Açık araştırma ve yeniden kullanım | Uygun lisans ve kurum koşulları gözetilerek sürümlendirilmiş kod, seçilmiş kişisel veri içermeyen ham ölçümler ve veri şemalarının paylaşılması. |
| Sonraki araştırmalar | Otomatik sınıflandırma veya çok çekirdek gibi genişletmeler için açık kısıt ve karşı örnek listesi; lisansüstü araştırmaya başlangıç sağlayabilecek yöntemsel birikim. |

Yayın kabulü, patent, ticari ürün veya belirli performans kazancı kesin çıktı olarak vaat edilmemektedir. Eğitim ve yeniden kullanım hedefleri, teknik belgeler ve doğrulanabilir kod/veri çıktılarıyla değerlendirilecektir.


# 5. BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR

Ön çalışma, algoritma geliştirme ve gerçek süreçlerden veri toplama altyapısının uygulanabilirliğini göstermektedir. Karışık model iş yükünde etkileşimli görevlerin ortalama ilk yanıtı 11 ms'den 3 ms'ye inmiştir. Yoğun etkileşimli senaryoda ise ortalama toplam bekleme 252,667 ms'den 303,833 ms'ye yükselmiştir. Bu karşıt bulgular, araştırmada ilk yanıtın yanında tamamlanma ve ilerleme ölçütlerinin birlikte değerlendirilmesini gerekçelendirmektedir.

Mevcut gerçek Linux deneylerinde özel politika uygulanmamıştır. Bu kayıtlar başlangıç çizgisidir; Linux üzerinde politika kazancı kanıtı olarak yorumlanmamaktadır. Kaynak kodları, test kayıtları ve özgün deney arşivi sürümlendirilmiştir: https://github.com/sanlibrk/Kernel_CPU

# 6. EKLER

Ek 1: Karışık model iş yükünde ortalama ilk yanıt ve arka plan dönüş süreleri.
Ek 2: Yoğun etkileşimli model iş yükünde ilk yanıt ve toplam bekleme karşılaştırması.

Grafikler ilk deney arşivinden üretilmiştir. Katılımcı anketi, ölçek veya kişisel veri toplama bu araştırmada planlanmamıştır.


# KAYNAKLAR

Linux Kernel Community. 2024a. “CFS Scheduler”, Linux v6.12 kaynak ağacı, Documentation/scheduler/sched-design-CFS.rst. İnternet: https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-design-CFS.rst. Son erişim: 9 Kasım 2026.

Linux Kernel Community. 2024b. “EEVDF Scheduler”, Linux v6.12 kaynak ağacı, Documentation/scheduler/sched-eevdf.rst. İnternet: https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-eevdf.rst. Son erişim: 9 Kasım 2026.

Linux Kernel Community. 2024c. “Extensible Scheduler Class”, Linux v6.12 kaynak ağacı, Documentation/scheduler/sched-ext.rst. İnternet: https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-ext.rst. Son erişim: 9 Kasım 2026.

Linux Kernel Community. 2024d. “scx_simple.bpf.c”, Linux v6.12 kaynak ağacı, tools/sched_ext/scx_simple.bpf.c. İnternet: https://github.com/torvalds/linux/blob/v6.12/tools/sched_ext/scx_simple.bpf.c. Son erişim: 9 Kasım 2026.
