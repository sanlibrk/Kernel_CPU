# 9 Kasım 2026 — Yerel Ubuntu/WSL doğrulaması

Bu kayıt, yürütücünün paylaştığı [terminal çıktısına](terminal_log.txt) dayanır.
[Yapılandırılmış özet](record.json), yalnız bu çıktıda görülen sonuçları ve
daha önce bildirilen kişisel donanım envanterini içerir. Yerel WSL çekirdek
sürümü bu kayıtta bulunmadığından eski bulut çekirdeği sürümü kullanılmamıştır.

- C programları önceden derlenmiştir; `make` güncel hedef bulunduğunu bildirmiştir.
- Ayrı test çalıştırmasında 13 test geçmiştir.
- Karışık modelde kısa görevlerin ilk yanıtı RR için 11 ms, prototip için 3 ms'dir.
- Ayrı gerçek ölçümlerde 0 ve 2 arka plan çalışanıyla 40'ar gözlem alınmıştır.
- `make experiment` çıktısı 13 test, altı model ve altı Linux koşusu / 240 gözlem
  için başarı bildirmiştir. Sonuç dizini `results/week2-20261109-190318-856835` olarak
  görünmektedir. Bu dizindeki ham CSV/JSON dosyaları paylaşılmadığından burada
  yeniden hesaplanmış bir tam deney özeti bulunmamaktadır.

| Ayrı ölçüm | Ortalama uyanma gecikmesi (ms) | P95 (ms) | En yüksek (ms) |
|---|---:|---:|---:|
| 0 arka plan çalışanı, 40 gözlem | 0,301670 | 0,571509 | 0,670742 |
| 2 arka plan çalışanı, 40 gözlem | 1,130421 | 3,984890 | 5,537544 |

Bu iki ölçüm, tam otomatik gruptaki altı koşuyla aynı sayısal sonuçlarmış gibi
sunulmaz. Linux'ta özel politika kullanılmamıştır. Değerler tek makinedeki
başlangıç gözlemleridir; önceki Debian bulut deneyleriyle birleştirilmez.
