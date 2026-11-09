# Araştırma önerisinin şekilleri

| Şekil | Dosyalar | İçerik / kaynak |
|---|---|---|
| 1 | [PNG](ek3_politika_akisi.png), [SVG](ek3_politika_akisi.svg), [DOT çizim kaynağı](ek3_politika_akisi.dot) | Mevcut C modelinin 1 ms adımı ve seçim kuralları. Gerçek çekirdek programı değildir. |
| 2 | [Karışık model PNG](ek1_karisik_model.png) | Ortalama ilk yanıt ve arka plan dönüş süresi; 5 Kasım 2026 model arşivi. |
| 3 | [Yoğun etkileşimli model PNG](ek2_yogun_etkilesimli_model.png) | İlk yanıt iyileşmesi ile toplam bekleme artışını birlikte gösteren karşı örnek. |

Üç şekil de [araştırma önerisinin](../2209A_Burak_Sanli_Arastirma_Onerisi.md)
Word/PDF kopyasında, numarası ve açıklamasıyla yer alır. İki model grafiği ayrıca
ayrı [mevcut durum raporunda](../2209A_Burak_Sanli_Proje_Raporu.md) kullanılır.
Grafiklerdeki model kazancı gerçek Linux politika kazancı olarak yorumlanmaz.

TYBS aktarımında bilgi notunun **Resim Yükle** aracı ve PNG dosyaları kullanılır;
boyut ve okunurluk sistem ön izlemesinde denetlenir. SVG ve DOT dosyaları çizimin
yeniden üretilmesi için saklanır, editörün bunları kabul ettiği varsayılmaz.

Akış görselini kurulu Graphviz ile yeniden üretmek için depo kökünde:

```bash
dot -Tsvg docs/basvuru/2209a/ekler/ek3_politika_akisi.dot -o docs/basvuru/2209a/ekler/ek3_politika_akisi.svg
dot -Tpng -Gdpi=170 docs/basvuru/2209a/ekler/ek3_politika_akisi.dot -o docs/basvuru/2209a/ekler/ek3_politika_akisi.png
```
