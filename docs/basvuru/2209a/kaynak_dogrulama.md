# Kaynak doğrulama kaydı

Başvuru metnindeki teknik karşılaştırmalar, Linux çekirdeğinin resmî kaynak deposunda `v6.12` etiketi altında bulunan aşağıdaki birincil kaynaklara dayanmaktadır. Belgeler 9 Kasım 2026 tarihinde okunmuştur. Sürüm etiketinin yayımlanma tarihi kaynak sayfasında 17 Kasım 2024 olarak doğrulanmıştır.

| Atıf | Kaynak ve sabit sürüm bağlantısı | Metinde desteklediği bilgi |
|---|---|---|
| Linux Kernel Community, 2024a | [CFS Scheduler](https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-design-CFS.rst) | Sanal çalışma zamanı ve adil paylaşım yaklaşımı. |
| Linux Kernel Community, 2024b | [EEVDF Scheduler](https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-eevdf.rst) | Uygunluk, lag ve sanal son teslim zamanı ile görev seçimi. |
| Linux Kernel Community, 2024c | [Extensible Scheduler Class](https://github.com/torvalds/linux/blob/v6.12/Documentation/scheduler/sched-ext.rst) | BPF ile zamanlama arayüzü; çekirdek yapılandırması, örnekler ve geri dönüş davranışı. |
| Linux Kernel Community, 2024d | [scx_simple.bpf.c](https://github.com/torvalds/linux/blob/v6.12/tools/sched_ext/scx_simple.bpf.c) | Örnek politikanın ağırlıklı sanal-zaman/FIFO seçenekleri; kuyruk ve sayaç yapıları. |

## Kaynakça yaklaşımı

Başvuru metninde yazar–yıl atıfları ile kaynakça kayıtları eşleştirilmiştir. Kaynaklar resmî teknik dokümantasyon ve kaynak dosyalarıdır. İncelenen kayıtlarda DOI numarası sunulmadığından DOI uydurulmamıştır. Başvuruya sonradan DOI içeren bir yayın eklenirse DOI kaynakça kaydına da eklenmelidir.

TÜBİTAK bilgi notunun bağlantı verdiği bibliyografik düzenleme sayfasına bu çalışma ortamının ağ kısıtı nedeniyle erişilememiştir. Bu nedenle o sayfanın güncel kurallarına yönelik bağımsız çevrim içi doğrulama yapıldığı iddia edilmez. TYBS kaynakça adımındaki alanlar ve gösterim, gönderimden önce kontrol edilmelidir.

## İnternet araştırmasının kapsamı

GitHub üzerinden erişilebilen üçüncü taraf bir başvuru aracı dizini de incelenmiştir; bu kaynakta kabul edilmiş örnek başvurular bulunmadığı belirtildiği için bilimsel kanıt veya resmî şablon olarak kullanılmamıştır. Başka projelerin metinleri başvuruya kopyalanmamıştır. Bölüm düzeninde yürütücünün sağladığı 2026 bilgi notu esas alınmıştır.
