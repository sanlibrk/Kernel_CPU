# Belge biçimlerinin kaynakları

## Araştırma önerisi çalışma şablonu

[2209A_Arastirma_Onerisi_Formati.docx](2209A_Arastirma_Onerisi_Formati.docx),
yürütücünün paylaştığı iki doldurulmuş araştırma önerisi örneğinin kapak,
bölüm ve tablo düzeninden türetilmiştir. Bir örnek 2026'ya, diğeri 2024'e aittir.
Yıl ve bilimsel nitelik başlıkları 2026 bilgi notuyla eşleştirilmiştir.

Başka projelerin bilimsel metinleri, kimlikleri, kaynakçaları, bütçeleri ve
grafikleri çalışma şablonunda bulunmaz. Orijinal doldurulmuş örnekler depoda
yayımlanmamıştır. Biçimin teknik kaydı ve dosya özetleri
[buradadır](arastirma_onerisi_bicim_kaydi.json).

- Kapakta paylaşılan program logosu ve araştırma önerisi formu düzeni bulunur.
- Gövde Arial 9'dur; içerik alanları çerçevelidir.
- İş-zaman çizelgesi beş, risk tablosu üç sütunludur.
- Araştırma olanakları, yaygın etki ve bütçe çizelgeleri ayrı doldurulur.
- Word formundaki bütçe bölümü nedeniyle son bölüm numaraları çevrim içi 2026
  bilgi notundan farklı olabilir; aktarım başlığın adına ve içeriğine göre yapılır.

[Üretici](../../../../scripts/build_2209_application.py) bu şablonun kopyasını
ana Markdown kaynağından doldurur. Uzun yöntem alanında sayfa akışını korumak
üzere iç satırlar bölünebilir; çerçeve ve tek sütunlu alan görünümü korunur.
Kapak bilgileri, şekiller ve kaynakça projeye göre eklenir. Örneklerdeki 20 sayfa
üst sınırı kontrol edilir; asgari sayfa sayısı hedeflenmez.

## Ayrı sonuç raporu şablonu

[2209-a_sonuc_raporu_formati.docx](2209-a_sonuc_raporu_formati.docx),
yürütücünün daha önce paylaştığı 16.008 baytlık dosyanın değiştirilmemiş kopyasıdır.
SHA-256: `8401f2ae6e0e8d081bf0122ee3a7660d8763d5285a78af8c5e258c73dc3aaf7b`.

Bu ayrı şablonda çerçeveli VML kapak, genel bilgi tablosu, beş numaralı içerik
bölümü, yürütücü/danışman imza tablosu ve tarih alanı vardır.
[Sonuç biçimli rapor üreticisi](../../../../scripts/build_2209_report.py)
şablonu ayrı bir kopyada doldurur; özgün dosyanın baytlarını değiştirmez.
Mevcut durum raporu, başvuru araştırma önerisinin yerine kullanılmaz.
