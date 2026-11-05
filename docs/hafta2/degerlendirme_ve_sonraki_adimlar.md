# Hafta 2 — Değerlendirme ve sonraki adımlar

## 1. İkinci haftanın çıktıları

İkinci hafta, konu seçimindeki CPU zamanlama fikrini çalıştırılabilir bir
referans uygulamaya ve tekrarlanabilir bir başlangıç ölçüm düzenine dönüştürmüştür.
Bu aşamanın somut çıktıları aşağıda özetlenmiştir.

| Çıktı | Doğrulanan kapsam |
|---|---|
| C tabanlı zamanlama modeli | Tek CPU'da RR referansı ve bütçe/yaşlandırma içeren politika prototipi. |
| Gerçek Linux ölçüm programı | Aynı CPU'daki periyodik kısa iş ile arka plan işçilerinin gecikme ve tamamlanma kayıtları. |
| Otomatik testler | 13 test yöntemi; analitik örnekler, girdi denetimi, süre muhasebesi ve gerçek süreç kontrolleri. |
| Deney yürütücüsü | Üç model senaryosunun iki politikayla, iki Linux yük koşulunun üçer tekrarla çalıştırılması. |
| Arşiv ve teknik belgeler | Ham CSV/JSON dosyaları, test günlüğü, ortam/parametre özeti ve uygulama açıklamaları. |

[Uygulama ayrıntıları](uygulama.md), [deney yöntemi ve sonuçlar](deney_sonuclari.md)
ile [ham veri arşivi](../../experiments/hafta2/2026-11-05) bu değerlendirmeyi destekler.
Kayıtlı doğrulama ortamı Debian 13 ve Linux 6.18.57'dir. Yerel Ubuntu/WSL
kurulumunun tamamlanması ve aynı kontrollerin orada yürütülmesi bu deney arşivinde
doğrulanmış gözlemler değildir; farklı ortamlar için ayrıca kayıt tutulmalıdır.

## 2. Testlerin gösterdiği ve göstermediği özellikler

Kayıtlı koşuda 13 test yöntemi başarılı, başarısız ve atlanan test sayıları sıfırdır.
Bilinen iki görevli RR takvimi ve başlangıçta boş CPU örneği doğru sonuç vermiştir.
Seçilen örneklerde bütçe sonrası arka plan ilerlemesi, yaşlandırma önceliği ve
yalnız etkileşimli görevlerde yapay CPU boşluğu oluşmaması doğrulanmıştır.
Sabit tohumlu 20 iş yükü her iki politikada tamamlanmış; görev bazındaki süre
eşitlikleri ve boşluksuz örneklerde toplam CPU ihtiyacı kontrol edilmiştir.
Gerçek Linux kontrolleri de örnek/işçi sayıları, süre alanları ve süreçlerin
başarıyla tamamlanması bakımından tutarlı çıktı üretmiştir.

Bu testler sonlu, seçilmiş girdilerin işlevsel doğrulamasıdır. Bütün iş yüklerinde
adalet, sonsuz görev akışında açlık oluşmaması veya kesin bir gecikme üst sınırı
kanıtlanmamıştır. Testler Linux çekirdeğine politika yüklemesini sınamaz;
parametrelerin en iyi olduğunu veya sistemin genel olarak hızlandığını göstermez.

## 3. Model sonuçlarının değerlendirilmesi

Karışık iş yükünde etkileşimli görevlerin ortalama ve P95 ilk yanıtı RR'de 11 ms,
prototipte 3 ms'dir. Aynı sonlu görev kümesinde arka plan ortalama dönüş süresi
372 ms, son görev bitişi 376 ms olarak iki politikada da aynı kalmıştır.
Bu gözlem, seçilen kısa görev senaryosunda ilk yanıt hedefinin desteklendiğini
göstermektedir. Bununla birlikte arka plan ortalama ilk yanıtı 4 ms'den yaklaşık
4,667 ms'ye çıkmıştır; bütün ölçütler aynı yönde iyileşmemiştir.

Yoğun etkileşimli senaryo daha belirgin bir ödünleşim içermektedir:

| Etkileşimli görev ölçütü | RR | Prototip |
|---|---:|---:|
| Ortalama ilk yanıt | 31,333 ms | 19,333 ms |
| P95 ilk yanıt | 54 ms | 33 ms |
| Ortalama toplam bekleme | 252,667 ms | 303,833 ms |
| Ortalama dönüş | 272,667 ms | 323,833 ms |

Görevler ilk kez CPU'ya daha erken ulaşmış, ancak toplam bekleme ve tamamlanma
süreleri artmıştır. İlk yanıt ile işin bitişini aynı başarı ölçütü olarak ele
almak bu gerilemeyi gizler. Arka plan ortalama ilk yanıtı da 4 ms'den 12 ms'ye
çıkmıştır. Son bitişin 480 ms olarak aynı kalması, sıfır bağlam değiştirme
maliyetli modelde aynı CPU ihtiyacının boşluksuz yürütülmesiyle ilişkilidir;
gerçek sistemde işlem hacmi kazancı veya genel adalet kanıtı değildir.

## 4. Gerçek Linux başlangıç ölçümünün rolü

Üç tekrardaki 0 ve 2 işçili koşular toplam 240 kısa iş gözlemi sağlamıştır.
İki arka plan işçisi varken gözlenen uyanma gecikmeleri daha yüksektir.
Ancak koşul sırası rastgeleleştirilmemiş, tekrar sayısı sınırlı kalmış ve
barındıran sistemin tüm yükü kontrol edilmemiştir. Ölçülen değerler timer,
uyandırma, zamanlama ve sanallaştırma etkilerini birlikte içerebilir.

Bu koşular mevcut `SCHED_OTHER` davranışının başlangıç kaydıdır. Prototip politika
Linux'ta çalışmadığı için onun çekirdek üzerindeki başarısı ölçülmemiştir.
Modeldeki ilk yanıt ile Linux programındaki uyanma gecikmesi farklı tanımlardır;
bu iki veri grubundan doğrudan bir Linux performans artışı hesaplanamaz.

## 5. Üçüncü hafta için aşamalar ve kabul ölçütleri

| Aşama | Tamamlanma ölçütü |
|---|---|
| Çekirdek ve test ortamı seçimi | Ekip çekirdeğinin sürümü/yapılandırması, ayrı test sanal makinesi ve geri yüklenebilir başlangıç durumu kayıtlıdır. |
| Özellik ve araç zinciri doğrulaması | sched_ext, BPF ve BTF desteği; gerekli LLVM/Clang, bpftool/libbpf bileşenleri ve yükleme yetkileri seçilen sürümle doğrulanmıştır. |
| Örnek politika deneyi | Küçük bir örnek politika derlenir, test VM'ine yüklenir, etkinliği gözlenir ve kaldırılır. |
| Güvenli geri dönüş | Politika sonlandırıldığında varsayılan zamanlamaya dönüş ve görevlerin ilerlemesi doğrulanır; hata halinde VM geri yükleme yolu denenmiştir. |
| Politika aktarımı | Önceki aşamalar tamamlandıktan sonra bütçe, görev seçimi ve yaşlandırma kuralları çekirdek altyapısına uyarlanır. |
| Karşılaştırmalı değerlendirme | Varsayılan ve özel politika aynı iş yükleri, CPU yerleşimi, parametreler ve kayıt yöntemiyle karşılaştırılır. |

Özellik kontrolünde `CONFIG_SCHED_CLASS_EXT`, `CONFIG_BPF_SYSCALL` ve ilgili BTF
yapılandırması seçilen çekirdeğin belgeleriyle birlikte incelenmelidir.
Çekirdek sürüm numarası veya `/sys/kernel/btf/vmlinux` dosyasının görünmesi tek
başına yeterli değildir. Araç zincirinin BPF hedefini derleyebilmesi ve gerekli
sistem çağrılarının seçilen ortamda yetkilendirilmesi de doğrulanmalıdır.

Yükleme, kaldırma ve geri dönüş doğrulanmadan prototipin kuralları aktarılmamalıdır.
Karşılaştırmada ilk yanıt/uyanma gecikmesine ek olarak toplam bekleme, kısa ve
uzun işlerin tamamlanması, görev ilerlemesi ve politika maliyeti incelenmelidir.
Daha fazla tekrar, koşul sırasının kontrolü ve önceden belirlenmiş değerlendirme
ölçütleri, tek bir olumlu örneğe dayanma riskini azaltacaktır.

## 6. Aşama sonucu

İkinci hafta, algoritma fikrinin test edilebilir bir modele ve gerçek süreçlerle
çalışan bir ölçüm temeline dönüştürülmesini tamamlamıştır. Sonuçlar ilk yanıt
hedefi için kontrollü bir olumlu örnek ve yoğun yükte dikkate alınması gereken
bir bekleme gerilemesi ortaya koymaktadır. Çekirdek entegrasyonu ve gerçek
politika karşılaştırması sonraki aşamanın doğrulanacak çalışma konularıdır.
