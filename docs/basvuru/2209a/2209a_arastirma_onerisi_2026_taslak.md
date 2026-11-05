# Başvuru bilgileri ve metnin durumu

Proje başlığı: Etkileşimli Görevlerde Yanıt Süresini İyileştirmeye Yönelik Bütçe ve Yaşlandırma Tabanlı CPU Zamanlama Politikasının Geliştirilmesi
Yürütücü: Burak Şanlı
Üniversite / bölüm: Harran Üniversitesi, Bilgisayar Mühendisliği
Akademik danışman: Prof. Dr. Dursun Akaslan — başvuruya özgü kabul/onay henüz tamamlanmış değildir.
Başvuru türü: Bireysel; başka öğrenci proje ortağı bulunmamaktadır.
Önerilen proje süresi: 6 ay / 24 haftalık çalışma planı. Başlangıç tarihi resmî yürürlük tarihi ve danışman değerlendirmesiyle kesinleştirilecektir.

Bu metin, paylaşılan 2026 çağrı duyurusu ve Başvuru İçeriği Bilgi Notu başlıklarına göre hazırlanmış başvuru taslağıdır. TYBS'de doldurulmuş veya gönderilmiş bir başvuru değildir. Proje kapsamı yalnızca yürütücünün CPU zamanlama çalışmasıdır. Gelecek faaliyetler plan, mevcut kod ve ölçümler ön çalışma olarak belirtilmiştir. Kaynakça, bütçe, mevcut donanım ve başvuru sahibinin uygunluk beyanları son kontrolden geçmelidir.


# ÖZET

CPU yoğun arka plan işleriyle birlikte çalışan kısa ve etkileşimli görevlerin gecikmesi, kaynak paylaşımı ile kullanıcı etkileşimi arasında önemli bir denge oluşturmaktadır. Bu projenin amacı, kısa görevlerin yanıt süresini destekleyen sınırlı bir tercih bütçesi ile uzun bekleyen görevleri koruyan yaşlandırma kurallarını birleştiren CPU zamanlama politikasını geliştirmek ve hangi yük koşullarında yararlı olduğunu deneysel olarak belirlemektir. Katkı, bütün işletim sisteminin yeniden yazılması veya evrensel bir hızlanma iddiası değil, tanımlı bir kaynak paylaşımı politikasının uygulanması ve ölçülebilir sınırlarının ortaya konulmasıdır.

Çalışma altı aylık plan içinde referans modelin genişletilmesi, yalıtılmış test ortamının doğrulanması, uygun açık kaynak çekirdek altyapısında politika entegrasyonu ve karşılaştırmalı deneylerden oluşmaktadır. Ön çalışmada C tabanlı tek CPU modeli, gerçek süreç ölçüm aracı ve 13 başarılı test hazırlanmıştır. Modeldeki olumlu ilk yanıt bulgusunun yanında yoğun etkileşimli yükte toplam beklemenin arttığı da görülmüştür; bu nedenle kısa görev gecikmesi, arka plan ilerlemesi ve uygulama maliyeti birlikte değerlendirilecektir.

Yöntemde varsayılan ve özel politika aynı iş yükleri ve kaynak koşullarında, sırası dengelenmiş ve rastgeleleştirilmiş eşleştirilmiş tekrarlarla karşılaştırılacaktır. Öncelikli ölçüt P95 uyanma gecikmesi; koruyucu ölçütler uzun işlerin tamamlanma süresi, ilerleme kaybı ve politika maliyetidir. Gecikme deneyi ile sabit iş miktarı üzerinden işlem hacmi deneyi ayrı yürütülecektir. Sanallaştırma, timer davranışı ve bellek baskısı gibi etkenler kayıt altına alınacaktır.

Proje yönetimi beş ölçülebilir iş adımı, kaynak doğrulaması ve geri dönüş planına dayanmaktadır. Beklenen çıktılar; test edilmiş politika prototipi, uygun çekirdek üzerinde uygulama, sürümlendirilmiş iş yükleri, deney verileri ve yeniden üretim belgeleridir. Sonuçlar olumlu ve olumsuz koşulları birlikte raporlayarak sistem programlama eğitimi ve kaynak yönetimi araştırmaları için paylaşılabilir bir değerlendirme altyapısı sağlayacaktır.

Anahtar kelimeler: CPU zamanlama, etkileşimli görev, yaşlandırma, kaynak paylaşımı, deneysel değerlendirme.


# 1. ARAŞTIRMA ÖNERİSİNİN BİLİMSEL NİTELİĞİ

## 1.1. Konunun Önemi ve Araştırma Önerisinin Bilimsel Niteliği

İşlemci zamanının çalışmaya hazır görevler arasında paylaşılması; etkileşimli görevlerin yanıtını, uzun işlerin tamamlanmasını ve kaynak kullanımının adaletini birlikte etkilemektedir. Klasik işletim sistemi kaynakları bu hedeflerin farklı zamanlama tercihleri doğurabildiğini açıklamaktadır [1]. Adil zamanlama altyapıları, sanal çalışma zamanı veya uygunluk ve sanal son teslim zamanı gibi mekanizmalarla bu dengeyi ele almaktadır [2,3]. Dolayısıyla araştırma, mevcut sistemlerin kaynak paylaşımını hiç çözmediği iddiasına dayanmamaktadır.

Araştırmanın ele aldığı somut problem, uzun CPU işleriyle kısa periyodik görevlerin aynı kaynağı paylaştığı koşullarda kısa görev gecikmesinin azaltılması ve bu tercihin uzun işlere getirdiği maliyetin birlikte belirlenmesidir. İlk sürüm açıkça işaretlenen iki görev sınıfıyla ve tek mantıksal CPU'da başlayacak; çok çekirdek kapsamı yalnızca çekirdek politikasının doğruluğu ve kaynak uygunluğu sağlandıktan sonra ek deney olarak değerlendirilecektir. Bellek yönetimi, fan kontrolü ve bütün bir işletim sisteminin yeniden tasarlanması kapsam dışındadır.

Araştırma sorusu şudur: Sabit pencereye bağlı sınırlı etkileşimli tercih bütçesi ile son beklemeye girişe dayalı yaşlandırma birleştirildiğinde, kısa görevlerin P95 uyanma gecikmesi uzun işlerin ilerlemesi kabul edilebilir sınırda korunarak azaltılabilir mi? Hipotez, tanımlı karma iş yüklerinin bir bölümünde bu dengenin sağlanabileceğidir; bütün yüklerde üstünlük varsayılmamaktadır.

Beklenen bilimsel katkı, bu kural bileşiminin belirli yüklerdeki davranışının açık tanımı, uygulanması ve kontrollü karşılaştırmasıdır. Literatürde ilk algoritma olduğu iddia edilmemektedir. Mevcut zamanlama yaklaşımları ve sched_ext örnekleriyle farklar geliştirme sırasında sistematik olarak karşılaştırılacaktır [2–4]. Ön çalışmada yoğun etkileşimli model yükünde ilk yanıt iyileşirken toplam beklemenin artması, araştırmanın hangi koşullarda başarısız olduğunu da incelemesini gerektiren somut bir karşı örnektir.

Araştırma sistem yazılımı ve kaynak yönetimiyle ilişkilidir. Ulusal strateji belgelerinin belirli kritik alanlarına ilişkin puan avantajı veya resmî uyum iddiası, ilgili metinlerle doğrulanmadan kurulmamıştır.

## 1.2. Amaç ve Hedefler

Amaç, açıkça tanımlanmış bir CPU zamanlama politikasını modelden gerçek çekirdek deneyine taşıyarak gecikme, ilerleme ve maliyet dengesini açıklamaktır. Altı aylık planın ölçülebilir hedefleri şunlardır:

1. Görev kabulü, bütçe yenilenmesi, yeniden kuyruğa giriş ve yaşlandırma istisnaları belgelenmiş referans modeli genişletmek; en az üç yük ailesi ve sınır koşullarını test etmek.
2. Geri yüklenebilir ayrı sanal makinede özellik/araç/yetki kontrollerini tamamlamak; örnek politikanın yükleme-kaldırma ve varsayılana dönüşünü üç ardışık denemede doğrulamak.
3. Bütçe ve yaşlandırma kurallarını uygun çekirdek altyapısında uygulamak; geçerli girdiler, görev bitişleri ve geri dönüş denemeleri dahil en az 25 test yöntemi veya belgelenmiş kontrol senaryosu hazırlamak.
4. Üç yük ailesi ve iki yoğunluk düzeyinde, her hücre için en az 10 eşleştirilmiş blokla varsayılan/özel politika karşılaştırması yapmak; ham kayıtları ve parametreleri saklamak.
5. P95 gecikmenin yanında uzun işlerin tamamlanması, ilerleme ve politika maliyetini raporlamak; olumlu ve olumsuz koşulları aynı değerlendirmede açıklamak.

Geliştirme hedeflerinin tamamlanması, hipotezin mutlaka doğrulanması anlamına gelmez. Pilot sonrası ve ana deneylerden önce sayısal başarı eşikleri sabitlenecektir. Başlangıç mühendislik hedefi, seçilen karma yüklerde en az yüzde 20 P95 gecikme azalması ile uzun iş tamamlanma süresindeki artışın yüzde 10'u aşmamasının birlikte sağlanmasıdır. Bu oranlar ölçülmüş sonuç veya literatürden türetilmiş evrensel sınır değil, danışmanla gerekçelendirilip ana deneylerden önce kayda alınacak önerilen kabul eşikleridir.


# 2. YÖNTEM

Araştırma, tek CPU referans modelinin işlevsel incelemesi ile gerçek çekirdek üzerinde eşleştirilmiş karşılaştırmalı deneyleri birleştirmektedir. Modelde Round Robin, kural etkilerini açıklamak için kullanılır; gerçek Linux adil zamanlayıcısının modeli değildir. Gerçek deneyde karşılaştırma, aynı çekirdek ve kaynak yapılandırmasında varsayılan zamanlama ile özel politika arasında yapılacaktır [2–4].

Ön çalışmada C modeli, süreç ölçüm programı ve deney yürütücüsü geliştirilmiş; 13 test yöntemi başarılı olmuştur. Üç model senaryosu iki politikayla yürütülmüş, mevcut SCHED_OTHER altında altı koşuda toplam 240 kısa iş örneği toplanmıştır. Karışık model yükünde etkileşimli ortalama ilk yanıt 11 ms'den 3 ms'ye inerken, yoğun etkileşimli yükte toplam ortalama bekleme 252,667 ms'den 303,833 ms'ye yükselmiştir. Bunlar model bulgularıdır; özel politika henüz çekirdeğe yüklenmemiştir ve Linux üzerinde performans artışı gösterilmemiştir.

İlk iş adımında geri yüklenebilir test sanal makinesi, çekirdek yapılandırması, BPF/BTF desteği, derleyici hedefi ve yükleme yetkileri doğrulanacaktır. Öncelikli yol sched_ext/BPF altyapısıdır [4]. Bir örnek politikanın etkinliği, kaldırılması ve görevlerin varsayılan zamanlamada ilerlemesi test edilmeden yeni kurallar aktarılmayacaktır. Ana bilgisayardaki kurulum, test VM'inin destek ve yetki koşullarını otomatik sağlamış kabul edilmeyecektir.

İkinci adımda görev sınıfları açıkça belirtilecek; zaman dilimi, sabit pencere, etkileşimli tercih bütçesi ve son bekleme başlangıcını kullanan yaşlandırma tanımlanacaktır. Mevcut 4 ms zaman dilimi, 20 ms pencere, 8 ms bütçe ve 20 ms yaşlandırma eşiği başlangıç değerleridir. Bütçenin katı kota olmadığı, yaşlandırmanın seçim anında değerlendirildiği ve bütün yüklerde gecikme garantisi sağlamadığı testlerle ve açıklamalarla korunacaktır. Model karşı örnekleri gerçek uygulamaya aktarımdan önce kullanılacaktır.

Bağımsız değişkenler politika, kısa/uzun iş oranı, görev geliş yoğunluğu, CPU ihtiyacı ve politika parametreleridir. Bağımlı değişkenler P50/P95 uyanma gecikmesi, tamamlanma süresi, görev ilerlemesi ve politika maliyetidir. CPU yerleşimi, çekirdek tabanı, sanal makine kaynakları ve iş yükü tanımları eşleştirilmiş koşullarda sabit tutulacaktır. Çok çekirdek genişletmesi çekirdek doğrulamasına bağlı ek deneydir; temel başarı koşulu tek CPU deneyidir.

Gecikme deneyinde, aynı mantıksal CPU'daki periyodik kısa CPU patlamaları ve arka plan işleri kullanılacaktır. CLOCK_MONOTONIC ile mutlak uyanma hedefleri, süreç CPU saatiyle iş bütçeleri ölçülecektir. Bu uyanma ölçümü saf çekirdek kuyruk gecikmesi değildir; timer, kesme ve sanallaştırma etkilerini kapsar. İşlem hacmi için ayrıca doğrulanabilir sabit sayıda hesaplama işlemi yapan uzun görevler kullanılacaktır; CPU zamanı bütçeli ilk programın bitiş süresi tek başına hızlanma göstergesi sayılmayacaktır.

Üç yük ailesi yalnız arka plan, seyrek kısa görevli karma yük ve yoğun etkileşimli yükten oluşacaktır. Her aile iki yoğunluk düzeyinde değerlendirilecektir. Her hücrede en az 10 eşleştirilmiş blok, toplam en az 60 çift/120 koşu planlanmaktadır. Her koşuda en az 1.000 kısa iş gözlemi hedeflenir; nihai tekrar sayısı pilot değişkenliğine göre artırılabilir. Aynı koşudaki gözlemler bağımsız deney tekrarı sayılmayacaktır. Koşul sırası her blokta dengelenecek/rastgeleleştirilecek, tohumlar ve ısınma/dışlama kuralları ana deneyden önce kaydedilecektir.

Analizde koşu/blok düzeyindeki eşleştirilmiş P95 farkları ve göreli değişimler özetlenecektir. Uygun olduğunda blok yapısını koruyan yeniden örnekleme ile yüzde 95 belirsizlik aralıkları hesaplanacaktır. Parametre seçimi için kullanılan pilot yükleri, son değerlendirme yüklerinden ayrılacaktır. P99 yalnızca yeterli veri ve kuyruk belirsizliği açıklanarak ek ölçüt olarak verilecek; en büyük gözlem kesin en kötü durum sınırı sayılmayacaktır. Arka plan tamamlanma süresi, en uzun gözlenen ilerlememe aralığı ve maliyetin bozulduğu durumlar olumlu gecikme sonucu yanında raporlanacaktır.

Model genişletme, çekirdek doğrulama ve uygulama ilk üç iş adımıyla; tekrarlı deneyler dördüncü adımla; karşı örnekler ve sağlamlık incelemesi beşinci adımla ilişkilidir. Kaynak sürümü, yapılandırma, ham kayıtlar ve dosya özetleri saklanacaktır. Sonlu deneylerde bütün işlerin tamamlanması genel bir açlık önleme ispatı olarak sunulmayacaktır.


# 3. PROJE YÖNETİMİ

## 3.1. Çalışma Takvimi

Önerilen süre altı aydır. Aylar projenin yürürlüğe girmesinden itibaren göreli olarak gösterilmiştir; kesin takvim danışman ve resmî başlangıç durumuna göre işlenecektir. Beş iş adımı ardışık toplam altı ayı kapsar. Literatür incelemesi, satın alma, rapor hazırlama ve paylaşım faaliyetleri gerekli adımlara dahil edilmiştir; ayrı iş adımı olarak gösterilmemiştir.

| Dönem | Faaliyet | Sorumlu | Başarı ölçütü | Başarıya katkı (%) |
|---|---|---|---|---|
| Ay 1 / hafta 1–4 | Deney ortamı ve örnek politika doğrulaması | Burak Şanlı | Özellik/araç/yetki kayıtları; geri yüklenebilir VM; üç başarılı yükleme-kaldırma ve dönüş denemesi | 15 |
| Ay 2 / hafta 5–8 | Politika/model genişletme ve sınır koşullarının incelenmesi | Burak Şanlı | En az üç yük ailesi; kural ve istisnaların belgelenmesi; analitik ve karşı örnek kayıtları | 20 |
| Ay 3–ilk yarı Ay 4 / hafta 9–14 | Çekirdek politika uygulaması ve işlevsel doğrulama | Burak Şanlı | Uygun çekirdekte çalışır politika; toplam en az 25 test/kontrol senaryosu; görev ilerlemesi ve geri dönüş kayıtları | 25 |
| İkinci yarı Ay 4–Ay 5 / hafta 15–20 | Pilot ve kontrollü karşılaştırmalı deneyler | Burak Şanlı | Altı deney hücresinde en az 10 eşleştirilmiş blok; en az 120 koşu; parametreler, ham veriler ve dışlama gerekçeleri kayıtlı | 25 |
| Ay 6 / hafta 21–24 | Sağlamlık, maliyet ve başarısız yük koşullarının doğrulanması | Burak Şanlı | Bağımsız doğrulama koşulları; gecikme/ilerleme/maliyet tabloları; karşı örnekler ve tekrar üretim kontrolü | 15 |

Katkı ağırlıkları toplamı yüzde 100'dür. Akademik danışman tüm adımlarda bilimsel değerlendirme ve rehberlik sağlayacaktır; ilgili resmî kabul/onay işlemi ayrıca tamamlanmalıdır.

## 3.2. Risk Yönetimi

| Risk | B Planı ve yöntem etkisi |
|---|---|
| sched_ext/BTF veya yetki desteğinin bulunmaması | İlk ay içinde destekli ayrı test VM'i/çekirdek seçilir. Sağlanamazsa aynı araştırma sorusunu koruyan doğrudan çekirdek değişikliği danışmanla fizibiliteye alınır; yöntem ve takvim etkisi açıkça revize edilir. Yalnız model sonucu çekirdek hedefi tamamlanmış gibi gösterilmez. |
| Politika hatasıyla sistemin durması | Yalıtılmış VM, geri yüklenebilir görüntü ve önceden denenmiş kaldırma/geri dönüş yolu kullanılır; güvenilir sürüme dönülüp hata senaryosu kaydedilir. |
| Kısa görev kazancının uzun işleri bozması | Bütçe/yaşlandırma parametreleri pilotta gözden geçirilir; ana deney eşikleri sonuç görüldükten sonra değiştirilmez. Yarar sağlanmayan yükler araştırma sonucu olarak raporlanır. |
| Ortam gürültüsü veya yetersiz tekrar | Eşleştirme, bloklama ve sıralama kontrolü uygulanır; pilotta değişkenlik yüksekse tekrar artırılır veya geçerlilik alanı daraltılarak belirsizlik raporlanır. |
| Takvim veya kaynak yetersizliği | Otomatik sınıflandırma ve çok çekirdek genişletmesi ertelenir; temel hedef olan tek CPU'da gerçek politika karşılaştırması korunur. |

## 3.3. Araştırma Olanakları

Mevcut ön çalışmada C/Python kaynakları, testler, deney betikleri ve arşivlenmiş ölçümler hazırlanmıştır. Bu yazılım birikimi proje başlangıç girdisidir. Ön çalışma ortamı Debian 13 ve Linux 6.18.57'dir; mevcut bulut ortamının proje süresi boyunca kesintisiz tahsis edileceği varsayılmamaktadır.

Geliştirmede yürütücünün bilgisayarı, açık kaynak derleyici/izleme araçları ve ayrı test VM'i kullanılması planlanmaktadır. Kişisel bilgisayarın işlemci, RAM, disk ve sanallaştırma desteği ile üniversitenin ek olanakları henüz doğrulanmadığından laboratuvar adı, kapasite veya kurum tahsis taahhüdü uydurulmamıştır. TYBS'ye son aktarım öncesi bu alan gerçek donanım bilgileri ve danışmanın doğruladığı olanaklarla tamamlanacaktır.


# 4. ARAŞTIRMA ÖNERİSİNİN YAYGIN ETKİSİ

| Kategori | Ölçülebilir ve gerçekçi beklenen çıktı |
|---|---|
| Bilimsel / teknik | Bir politika tanımı ve uygun çekirdekte prototip; üç yük ailesini ve altı hücreyi kapsayan karşılaştırma veri grubu; gecikme, arka plan ilerlemesi ve maliyetin birlikte değerlendirildiği bir teknik rapor. |
| Eğitim / insan kaynağı | Sistem programlama, çekirdek araçları ve deney tasarımını açıklayan yeniden üretim yönergeleri; test ve iş yükü örneklerinin en az bir bölüm içi teknik sunumla paylaşılması. |
| Açık araştırma ve yeniden kullanım | Uygun lisans ve kurum koşulları gözetilerek sürümlendirilmiş kod, seçilmiş kişisel veri içermeyen ham ölçümler ve veri şemalarının paylaşılması. |
| Sonraki araştırmalar | Otomatik sınıflandırma veya çok çekirdek gibi genişletmeler için açık kısıt ve karşı örnek listesi; lisansüstü araştırmaya başlangıç sağlayabilecek yöntemsel birikim. |

Yayın kabulü, patent, ticari ürün veya belirli performans kazancı kesin çıktı olarak vaat edilmemektedir. Eğitim ve yeniden kullanım hedefleri, teknik belgeler ve doğrulanabilir kod/veri çıktılarıyla değerlendirilecektir.


# 5. BELİRTMEK İSTEDİĞİNİZ DİĞER KONULAR

Ön çalışma verileri, uygulanabilirlik ve ölçüm altyapısı bakımından destekleyici niteliktedir. Karışık modelde ilk yanıtın 11 ms'den 3 ms'ye düşmesi ile yoğun etkileşimli modelde toplam beklemenin artması birlikte sunulacaktır. Mevcut gerçek Linux veri grubu, özel politika başarısının kanıtı olarak kullanılmayacaktır. Kaynak kod ve tarihsel veri arşivi: https://github.com/sanlibrk/Kernel_CPU

# 6. EKLER

Başvuru değerlendirmesine katkı sağladığı ve sistem izin verdiği ölçüde politika akış şeması, küçük analitik zamanlama örneği ve ön çalışma karşılaştırma grafikleri eklenebilir. Haftalık sunum PDF'i araştırma önerisinin zorunlu bir yerine geçen belge olarak varsayılmamıştır. Katılımcı anketi veya ölçek kullanılmadığı için böyle bir ek oluşturulmamıştır. Paylaşılan sonuç raporu şablonu proje sonunda kullanılacak belgedir; şimdi tamamlanmış sonuçlar ve imzalarla doldurulmamıştır.


# KAYNAKLAR — son bibliyografik kontrol taslağı

[1] Silberschatz, A., Galvin, P. B. ve Gagne, G. 2018. Operating System Concepts, 10. baskı. Wiley.
[2] The Linux Kernel Documentation. “CFS Scheduler”. https://docs.kernel.org/scheduler/sched-design-CFS.html
[3] The Linux Kernel Documentation. “EEVDF Scheduler”. https://docs.kernel.org/scheduler/sched-eevdf.html
[4] The Linux Kernel Documentation. “Extensible Scheduler Class”. https://docs.kernel.org/scheduler/sched-ext.html

Metin içi atıflar [1]–[4] ile eşleştirilmiştir. Çevrim içi kaynakların içerikleri bu oturumda yeniden açılamamıştır; hedef çekirdek sürümüyle uyumları, bibliyografik yazım ve erişim tarihleri son kontrolde doğrulanmalıdır. DOI uydurulmamıştır; DOI'si bulunan kaynaklar için DOI eklenmesi bilgi notunun gereğidir. İlgili hakemli çalışmalarla karşılaştırma, kaynak doğrulaması tamamlanmadan bitirilmiş bir literatür taraması sayılmamalıdır.
