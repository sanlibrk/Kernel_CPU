# Kaynak ve atıf kaydı

**Proje:** Gecikme Odaklı CPU Zamanlama. Erişim tarihi: 9 Kasım 2026.
Kaynaklar, başvuru metnindeki iddialarla aşağıdaki kapsamda eşleştirilmiştir.
Başka projelerin bitki bilimi kaynakları bu araştırmaya aktarılmamıştır.

| Metin içi atıf | Okunan kaynak | Desteklediği bilgi / sınır |
|---|---|---|
| Goel vd., 2002 | *Supporting Time-Sensitive Applications on a Commodity OS*, tam makale; [erişilen kopya](https://raw.githubusercontent.com/Yodaquette/CS6210_AdvOS_Papers/master/part03_RecoveryAndInternetScaleComputing/02_RealtimeAndMultimedia/01_TimeSensitiveApps.pdf) | Timer hassasiyeti, çekirdek kesilebilirliği ve zamanlamanın birlikte değerlendirilmesi; gecikme ile işlem hacmi maliyetinin ayrılması. Eski TSL sonuçları bizim politikamızın güncel kazancı değildir. |
| Linux Kernel Community, 2024a | [CFS Scheduler, v6.12](https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-design-CFS.rst) | Ağırlıklar ve sanal çalışma zamanı üzerinden adil paylaşım. |
| Linux Kernel Community, 2024b | [EEVDF Scheduler, v6.12](https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-eevdf.rst) | Uygunluk, lag ve sanal son teslim zamanı üzerinden seçim. |
| Linux Kernel Community, 2024c | [Extensible Scheduler Class, v6.12](https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-ext.rst) | BPF politika altyapısı, yapılandırma ve geri dönüş davranışı. |
| Linux Kernel Community, 2024d | [scx_simple.bpf.c, v6.12](https://github.com/torvalds/linux/blob/v6.12/tools/sched_ext/scx_simple.bpf.c) | Örneğin ağırlıklı sanal zaman / ayrıca açılan FIFO seçenekleri. |
| Linux Kernel Community, 2024e | [Deadline Task Scheduling, v6.12](https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-deadline.rst) | EDF/CBS, runtime/period/deadline ve kabul kontrolü. Bizim tercih bütçemiz aynı gerçek zaman garantisini vermez. |

## Gösterim ve erişim kapsamı

Üç ve daha fazla yazarı bulunan makaleye metin içinde **Goel vd. (2002)** veya
**(Goel vd., 2002)** biçiminde atıf yapılır. Kaynakçada beş yazar da tam yazılır.
Kurumsal yazarlı Linux belgelerinde yazar adı `Linux Kernel Community` olarak
korunur; kuruma gerekçesiz “vd.” eklenmez. Aynı yılın belgeleri a–e ile ayrılır.

Tam metin dosyalarının SHA-256 değerleri ve erişim adresleri
[kaynak kaydında](kaynak_kaydi.json) saklanır. Akademik makalenin erişilen PDF'i
başlık ve yazarları içerir; canlı yayıncı metadata/DOI sayfası bu ortamda ayrıca
kontrol edilememiştir. Okunan PDF'te DOI bulunmadığından DOI uydurulmamıştır.
Linux kaynaklarının sabit sürümü v6.12'dir; sürümün yayımlanma tarihi önceki
kaynak kontrolünde 17 Kasım 2024 olarak doğrulanmıştır.

USENIX/Stanford yayıncı adresleri ve TÜBİTAK'ın bibliyografik düzenleme sayfası
bu ortamda erişim kısıtına takılmıştır. Bu sayfaların güncel kurallarının veya
metadata alanlarının bağımsız canlı doğrulandığı iddia edilmez. Gönderim öncesi
TYBS kaynakça adımının istenen gösterimi ve varsa DOI bilgileri kontrol edilir.

Kaynak sayısı kapsamlı veya sistematik literatür taraması yapıldığı anlamına
gelmez. Yenilik iddiası “ilk algoritma” değildir; tanımlı görev sınıflarında
kural bileşimini uygulamak ve katkılarını kontrollü deneylerle açıklamaktır.
