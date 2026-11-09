# 2209-A 2026 — Gönderim öncesi kontrol

## Belge kontrolünün kapsamı

Araştırma önerisi, yürütücünün sağladığı 2026 çağrı duyurusu ve Başvuru İçeriği
Bilgi Notu temel alınarak düzenlenmiştir. Güncel Word/PDF, tek ana Markdown
metninden üretilir. Gerçek belge üzerinde hesaplanan kelime/karakter sayıları,
takvim ağırlıkları ve atıf eşleşmeleri [doğrulama kaydındadır](uygunluk_kontrolu.json).
Bu kayıt resmî sistem onayı veya destek kararı değildir.

| İçerik şartı | Son revizyonun karşılığı |
|---|---|
| Özet 25–450 kelime; bilimsel nitelik, yöntem, yönetim ve etki | Dört unsur özette var; gerçek Word üzerinden sınır kontrolü yapılır. |
| Bilimsel nitelik, hedef ve yöntem bölümleri en az 350 karakter | Üç alan ayrı ölçülür. |
| Araştırma sorusu ve gerekçeli yöntem | CFS/EEVDF/sched_ext karşılaştırması, hipotez ve sabit sürüm birincil kaynak atıfları. |
| Ölçülebilir hedefler ve takvim | Beş teknik adım, planlanan altı ay, katkı ağırlıkları toplamı yüzde 100. |
| Literatür, rapor, paylaşım, satın almanın ayrı adım olmaması | Bu işler ilgili teknik adımlara dahil. |
| Bağımlı/bağımsız değişkenler, analiz ve ön çalışma | İş yükü hücreleri ve ölçütleri ayrılmış; önceki veriler gelecekteki deney sayılmıyor. |
| B planında yöntem değişikliğinin açıklanması | Karar haftası, yapılandırılmış konuk ve yazılımsal emülasyon, kiplerin ayrılması ve takvim etkisi açık. |
| Mevcut araştırma olanakları | Kullanıcının doğruladığı işlemci/RAM ve başarılı yerel test; hedef VM tahsisi plan olarak ayrılmış. |
| Yaygın etki | Somut teknik/eğitim/açık araştırma çıktıları kategori tablosunda. |
| Kaynakların metinde kullanılması | Dört kaynak da metin içi atıflarla eşleşiyor. |
| Görsellerin uygun türü | İki PNG ayrıca indirilip sisteme yüklenebilir. |

Ulusal strateji öncelik eşleştirmesi veya ek puan avantajı talep edilmiş bir
sonuç olarak sunulmamaktadır. İlgili alan/beyan sistemde seçilecekse 12. Kalkınma
Planı ve 2030 stratejisiyle ilişkinin gerekçesi ayrıca doğrulanmalıdır.

## Araştırma kaynağı doğrulaması

Mevcut kaynak: yürütücünün bildirdiği i7-12650H işlemci, yaklaşık 15,7 GiB RAM
ve Ubuntu/WSL geliştirme ortamı. Paylaşılan yerel çıktı, C derlemesinin ve 13 test
metodunun tamamlandığını göstermektedir. Kaynakta belirtilmeyen disk kapasitesi,
misafir çekirdek desteği, iç içe hızlandırma veya kurum laboratuvarı varsayılmamıştır.
Bunlar ilk teknik iş adımındaki uygulanabilirlik kontrolleridir.

İlk Debian ortamındaki deney kayıtları ve yeni yerel test birbirinden ayrılmıştır.
Yerel testin geçmesi, çekirdeğe özel politika yüklendiğini veya performans
kazancı elde edildiğini kanıtlamaz.

## Kaynakça ve editör kontrolü

Kaynak sürümleri, okunan belgeler ve erişim tarihleri [kaynak kaydında](kaynak_dogrulama.md)
bulunur. İncelenen teknik kaynaklarda sunulmayan DOI numarası uydurulmamıştır.
TÜBİTAK'ın bağlantılı bibliyografik düzenleme sayfasına erişim engeli vardır;
o sayfanın güncel gösterimi bağımsız doğrulanmış sayılmaz. TYBS'nin kaynakça
adımında istenen biçim ve alanlar son gönderimden önce karşılaştırılmalıdır.

Metin, tablolar, listeler ve görseller [aktarım rehberine](tybs_aktarim_rehberi.md)
göre aktarılmalı; son ön izlemede alanların boşalmadığı, tabloların taşmadığı,
özel karakterlerin ve görsellerin doğru çıktığı kontrol edilmelidir.

## Bütçe ve uygunluk beyanları

Yürütücü mevcut olanaklarla çalışmayı tercih etmiştir; yeni gider öngörüsü 0 TL'dir.
Bu tercih, programın/sistemin sıfır bütçeli başvuruyu kabul ettiği anlamına gelmez.
Bu idari uygunluk kontrolü henüz doğrulanmamıştır. Gereksiz maliyet kalemi
oluşturulmaz. Bütçe üst sınırı çağrı PDF'inde tutar olarak verilmemiştir;
program sayfasındaki güncel bilgi esas alınır. Çağrıya göre bütçe kapanıştan
sonra değiştirilemez; konferans katılımı, yayın ve patent giderleri bütçeye alınmaz.

Aşağıdaki kişisel/kurumsal beyanlar belge hazırlayarak doğrulanmış olmaz:

- Uygun ve kayıtlı öğrenci statüsü, ARBİS kaydının tamamlanması/güncelliği.
- Aynı dönemde başka başvuru veya devam eden 2209-A/B projesi kısıtları.
- Aynı proje için önceki TÜBİTAK desteği bulunmaması.
- Danışmanın güncel YÖK/ARBİS bilgileri, danışmanlığı kabulü ve çağrıdaki en fazla
  beş proje sınırına uygunluğu.
- Gerekli görülürse kurum/etik izin veya muafiyet süreçleri.

## ÜYZ kullanımı ve sorumluluk

Çağrı 8.4–8.5 hükümlerine göre üretken yapay zekâ kullanım rehberi, doğru kullanım
beyanı ve danışman kontrolü esas alınmalıdır. Bu projede metin düzenleme, kod
önerileri, deney otomasyonu ve grafik üretiminde ÜYZ destekli araçlardan
yararlanılmıştır. Yürütücü ve danışman kaynakları, hesaplamaları ve içeriği gözden
geçirmelidir. Güncel rehberin bütün hükümlerinin okunduğu veya bu insan kontrolünün
zaten tamamlandığı varsayılmaz; sistemin beyan adımı buna göre doğru doldurulur.

## Resmî işlemin tamamlanma ölçütü

TYBS'de son ön izleme → yürütücünün doğruluk/yükümlülük onayı → akademik danışman
onayı → kuruluş yetkilisinin e-imzası → sistemde geçerli başvuru durumunun kontrolü.
Çağrı 4.3.4.2'ye göre kuruluş yetkilisi imzası sonrasında başvuru geçerli kabul edilir.
Bu işlemlerden hiçbiri burada yapılmış olarak raporlanmamaktadır.

Çağrı metni son gün 17.30 kapanışını belirtir; gün/ay program sayfasına
bırakılmıştır. Bu dosyada doğrulanmamış yeni bir son tarih verilmemiştir.
Paylaşılan sonuç raporu şablonu ise proje sonundaki rapora aittir; araştırma
önerisinin yerine doldurulmuş veya gelecekteki sonuçlarla tamamlanmış gösterilmemiştir.
