# İlk deney grubu — 5 Kasım 2026

Bu dizin, ikinci hafta deneylerinin özgün çıktılarını içerir. Kayıtlar sonraki
belge düzenlemelerinde yeniden üretilmemiş veya sayısal olarak değiştirilmemiştir.

| Dosyalar | İçerik |
|---|---|
| `model-*.csv` | Üç iş yükünün RR ve prototip politikasıyla görev bazındaki altı sonucu. |
| `linux-workers0-run*.json` | Arka plan işçisi olmadan üç gerçek Linux koşusu; her dosyada 40 örnek. |
| `linux-workers2-run*.json` | İki arka plan işçisiyle üç koşu; her dosyada 40 örnek ve iki işçi kaydı. |
| `summary.json` | Ortam, parametreler, test sayıları, koşu özetleri ve deney anındaki kaynak SHA-256 özetleri. |
| `tests.txt` | Deney grubuna ait başarılı test çalıştırmasının günlüğü. |
| `sha256sums.txt` | Bu arşivde listelenen dosyaların SHA-256 özetleri. |

Ölçülen uygulama kaynakları ilk prototip commit'indeki içerikle aynıdır.
`summary.json` içindeki belge özetleri deney anına aittir; daha sonra düzenlenmiş
belgelerin güncel içerikleriyle eşleşmeleri beklenmez.

Yöntem, sayısal tablolar ve sınırlılıklar
[Hafta 2 deney raporunda](../../../docs/hafta2/deney_sonuclari.md) açıklanmıştır.

## Bütünlük kontrolü

Bu dizinde:

```bash
sha256sum -c sha256sums.txt
```

Yeni bir deney `make experiment` ile deponun kökünde çalıştırılır ve `results/`
altında ayrı bir dizin oluşturur. Bu tarihsel arşivin üzerine yazılmaz.
