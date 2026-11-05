# Hafta 1 — Konu seçimi ve problem tanımı

**Konu:** CPU yönetimi içinde süreç zamanlama
**Öğrenci:** Burak Şanlı
**Bölüm:** Harran Üniversitesi Bilgisayar Mühendisliği
**Danışman:** Prof. Dr. Dursun Akaslan

## Kapsam

İlk hafta, CPU yoğun arka plan işleriyle kısa ve etkileşimli görevlerin birlikte
çalıştığı bir kullanım senaryosu tanımlanmıştır. Araştırma sorusu, kısa görevlerin
bekleme süresinin uzun işlerin ilerlemesi korunarak azaltılıp azaltılamayacağıdır.

Önerilen geliştirme yönü, mevcut Linux altyapısı üzerinde sınırlı bir zamanlama
politikası oluşturmaktır. İlk tasarımda açık görev sınıfları, sınırlı etkileşimli
CPU bütçesi ve uzun bekleyen görevleri koruyan yaşlandırma benzeri kurallar yer
almaktadır. `sched_ext`/BPF ve doğrudan çekirdek zamanlayıcısı değişikliği, teknik
uygunluğu daha sonra değerlendirilecek uygulama seçenekleridir.

Bu aşamada uygulama geliştirilmemiş ve performans deneyi yürütülmemiştir.
Ubuntu'nun geliştirme dağıtımı olarak rolü, Linux çekirdeğinin sağladığı altyapı
ve projede geliştirilmesi planlanan bileşen özgün sunumda ayrı açıklanmıştır.

## PDF sunumu

[CPU yönetimi ve süreç zamanlama — özgün konu seçimi PDF'i](Burak_Sanli_210504018_BitirmeProjesi_1_KonuSecimi.pdf)

18 sayfalık özgün belge, içerik veya biçim değişikliği yapılmadan arşivlenmiştir.
Uygulama aşamasının kayıtları [ikinci hafta](../hafta2/README.md) altında yer alır.
