# Çalıştırma komutları ve canlı gösterim

Bu belge Windows/PowerShell ekranından başlayarak tam Linux iş akışını ve
Windows'ta yalnız zamanlama modelinin çalıştırılmasını açıklar. Komut bloklarının
üstünde hangi terminalde çalıştırılacakları belirtilmiştir. Bütün komutlar aynı
terminale topluca yapıştırılmamalıdır.

## 1. GitHub güncellemesi — PowerShell

Ekran görüntüsündeki proje konumu:

```powershell
cd "C:\Users\sanli\Masaüstü\Kernel_CPU"
git status --short
git pull --ff-only
```

`git status`, yerel değişiklikleri gösterir. Ekrandaki `.vscode` ve
`src/scheduler_sim.exe` gibi dosyalar kişisel ayar/derleme çıktısı olabilir.
`git pull` yerel değişikliklerle çakışırsa burada durup hata incelenmelidir;
değişiklikleri silmek için `reset --hard` veya `clean` kullanılmamalıdır.
Başarılı güncellemeden sonra devam edilir.

## 2. Tam projeyi çalıştırmak için WSL/Ubuntu'ya geçiş — PowerShell

```powershell
wsl --list --verbose
```

Listede Ubuntu varsa aşağıdaki komuta geçilir:

```powershell
wsl -d Ubuntu
```

Dağıtım adı, listelenen adla aynı olmalıdır.
Örneğin listede `Ubuntu-24.04` varsa `wsl -d Ubuntu-24.04` kullanılır.
`PS C:\...>` yerine Linux kabuk istemi görünmelidir.

Liste “yüklü dağıtım yok” diyorsa veya WSL kurulu değilse aşağıdaki komut
**yönetici PowerShell** penceresinde çalıştırılır:

```powershell
wsl --install -d Ubuntu
```

“Değişiklikler sistem yeniden önyükleninceye kadar etkili olmayacak” mesajı
alınırsa burada durulur: dosyalar kaydedilip **Başlat → Güç → Yeniden başlat**
seçilir. Hızlı Başlatma açıkken kapatıp açmak aynı tam yeniden başlatmayı
yapmayabilir. Bilgisayar açıldıktan sonra dağıtım listesi kontrol edilir;
Ubuntu hâlâ yoksa kurulum komutu yeniden çalıştırılarak dağıtım kurulumu tamamlanır.
Ubuntu ilk açılışta yerel kullanıcı adı ve parola isteyebilir.

PowerShell'de `wsl -d Ubuntu` başarısız olduysa sonraki Linux komutlarına
geçilmez. `PS C:\...>` istemi hâlâ Windows terminalidir; burada `/mnt/c/...`
yolu ve Linux `make` komutları kullanılmaz. Windows modeli için 10. bölüm
WSL kurulumu beklenirken de kullanılabilir.

## 3. Proje klasörü ve bir kerelik araç kurulumu — Ubuntu terminali

```bash
cd '/mnt/c/Users/sanli/Masaüstü/Kernel_CPU'
pwd
ls
sudo apt update
sudo apt install -y build-essential python3 python3-venv git tzdata
gcc --version
make --version
python3 --version
```

Bu yol, ekranda görülen Windows klasörünün WSL karşılığıdır. Klasör farklı
yerdeyse yol buna göre değiştirilir. Python 3.10 veya üzeri kullanılmalıdır.
`sudo` parolası Ubuntu kullanıcısının parolasıdır; yazılırken karakter görünmemesi
normaldir. Paket kurulumu ilk hazırlıktır, her sunumda tekrarlanmaz.

## 4. Derleme ve otomatik testler — Ubuntu terminali

```bash
make
make test
```

`make`, `build/scheduler_sim` ve `build/linux_baseline` üretir. Mevcut pakette
13 test yöntemi vardır. Başarı çıktısı `Ran 13 tests` ve `OK` içerir.
Derleme veya test hatası varsa sonraki adımları başarılı olmuş gibi sunmadan
önce hata çözülmelidir. Kodu çalıştırmak için `sudo` gerekmez.

## 5. Model karşılaştırması — Ubuntu terminali

Karışık iş yükünü ve iki politikanın görev bazındaki çıktısını gösterir:

```bash
cat workloads/mixed.csv
./build/scheduler_sim --policy rr workloads/mixed.csv
./build/scheduler_sim --policy interactive workloads/mixed.csv
```

`response_ms`, ilk çalışmaya kadar geçen süre; `waiting_ms` bütün kuyruk
beklemelerinin toplamı; `turnaround_ms` varıştan tamamlanmaya kadar geçen süredir.
`interactive` satırlarına bakılır. Bu girdide RR ilk yanıtı 11 ms, prototip
3 ms üretir. Bunlar **model zamanlarıdır**, terminalin gerçek çalışma süresi değildir.

Diğer iki senaryo:

```bash
./build/scheduler_sim --policy rr workloads/cpu_only.csv
./build/scheduler_sim --policy interactive workloads/cpu_only.csv
./build/scheduler_sim --policy rr workloads/interactive_pressure.csv
./build/scheduler_sim --policy interactive workloads/interactive_pressure.csv
```

Yoğun etkileşimli senaryoda ilk yanıt iyileşirken toplam bekleme artabilir.
Bu nedenle yalnız ilk yanıt sütunu üzerinden genel başarı sonucu çıkarılmaz.

Parametreleri açıkça belirterek aynı varsayılan deneyi çalıştırma:

```bash
./build/scheduler_sim --policy interactive --quantum 4 --window 20 --budget 8 --aging 20 workloads/mixed.csv
```

## 6. Model sonuçlarını kaydetme ve okunur özet — Ubuntu terminali

```bash
mkdir -p results/demo
./build/scheduler_sim --policy rr workloads/mixed.csv > results/demo/mixed-rr.csv
./build/scheduler_sim --policy interactive workloads/mixed.csv > results/demo/mixed-interactive.csv
python3 - <<'PY'
import csv
import statistics
for policy in ('rr', 'interactive'):
    with open(f'results/demo/mixed-{policy}.csv') as f:
        rows = list(csv.DictReader(f))
    short = [r for r in rows if r['class'] == 'interactive']
    long = [r for r in rows if r['class'] == 'background']
    print(policy)
    print('  Etkilesimli ortalama ilk yanit (ms):',
          statistics.mean(int(r['response_ms']) for r in short))
    print('  Arka plan ortalama donus (ms):',
          statistics.mean(int(r['turnaround_ms']) for r in long))
    print('  Son bitis (ms):', max(int(r['finish_ms']) for r in rows))
PY
```

Bu özetin değerleri RR/prototip için sırasıyla 11/3, 372/372 ve 376/376'dır.

## 7. Gerçek Linux başlangıç ölçümü — Ubuntu terminali

```bash
mkdir -p results/demo
./build/linux_baseline --workers 0 --samples 40 --period-ms 20 --burst-us 500 --worker-ms 800 > results/demo/linux-workers0.json
./build/linux_baseline --workers 2 --samples 40 --period-ms 20 --burst-us 500 --worker-ms 800 > results/demo/linux-workers2.json
python3 - <<'PY'
import json
for workers in (0, 2):
    with open(f'results/demo/linux-workers{workers}.json') as f:
        data = json.load(f)
    print('Arka plan iscisi:', data['workers'])
    print('  Ornek sayisi:', data['sample_count'])
    print('  Secilen CPU:', data['cpu'])
    print('  P50 uyanma gecikmesi (ms):', data['wake_p50_ms'])
    print('  P95 uyanma gecikmesi (ms):', data['wake_p95_ms'])
    print('  En buyuk gecikme (ms):', data['wake_max_ms'])
    for worker in data['background']:
        print('  Isci', worker['id'], 'CPU/duvar saati (ms):',
              worker['cpu_ms'], worker['wall_ms'])
PY
```

Bu kısım gerçek süreçler çalıştırır ve normal `SCHED_OTHER` davranışını ölçer.
Özel politikayı çekirdeğe yüklemez. Canlı sonuçların PDF'teki sayılarla aynı olması
beklenmez: PDF, 5 Kasım 2026 tarihli Debian/Linux deney arşivini gösterir;
yerel WSL ortamı ve o anki sistem yükü farklıdır. İki işçili ölçümün her koşuda
daha yüksek çıkacağı garanti edilmez. Ölçüm programı görevlerini tamamlayıp kapanır.

## 8. Tam deney grubu — Ubuntu terminali

```bash
make experiment
```

Bu komut testleri, üç senaryo × iki model politikası ve üç tekrar × iki Linux
yük koşulunu çalıştırır. Gerçek koşularda toplam 240 örnek alınır. Yeni sonuç
dizininin yerini ve kısa özeti görmek için:

```bash
python3 - <<'PY'
import json
from pathlib import Path
directory = Path(json.loads(Path('results/latest.json').read_text())['directory'])
data = json.loads((directory / 'summary.json').read_text())
print('Sonuc dizini:', directory)
print('Testler:', data['tests'])
for name, policies in data['model'].items():
    print('Model:', name)
    for policy, summary in policies.items():
        print(' ', policy, 'etkilesimli:', summary['interactive'],
              'arka plan:', summary['background'])
for run in data['linux_baseline']:
    print('Linux tekrar', run['repetition'], 'isci', run['workers'],
          'P95(ms)', run['wake_p95_ms'])
PY
```

Sunumdaki tarihsel verilerin bütünlüğünü kontrol etme:

```bash
(cd experiments/hafta2/2026-11-05 && sha256sum -c sha256sums.txt)
```

## 9. PDF ve konuşma metnini açma — PowerShell

Ubuntu kabuğundan PowerShell'e dönmek için önce `exit` yazılır. Ardından:

```powershell
Start-Process '.\docs\hafta2\Burak_Sanli_Hafta2_CPU_Zamanlama.pdf'
Start-Process '.\docs\hafta2\Burak_Sanli_Hafta2_Sunum_Metni.docx'
```

Mevcut sunumu açmak için tekrar PDF üretmek gerekmez. Yalnız sunumu arşivden
yeniden üretmek istenirse **Ubuntu terminalinde**, bir kez kurulan isteğe bağlı
paketlerle:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements-presentation.txt
make presentation
deactivate
```

`make presentation` tarihsel arşivi kullanır, yeni ölçümlerini grafiğe otomatik
aktarmış olmaz. Asıl sunum dosyasını paylaşmadan önce yerel değişiklikler
`git status --short` ile incelenir.

## 10. WSL olmadan yalnız modeli gösterme — PowerShell

Windows GCC kuruluysa model Linux olmadan derlenebilir. Ekran görüntüsündeki
eski `src/scheduler_sim.exe` yerine aşağıdaki komut güncel kaynak koddan çıktı üretir:

```powershell
cd "C:\Users\sanli\Masaüstü\Kernel_CPU"
gcc --version
New-Item -ItemType Directory -Force build | Out-Null
gcc -std=c11 -O2 -Wall -Wextra -Werror -pedantic .\src\scheduler_sim.c -o .\build\scheduler_sim.exe
.\build\scheduler_sim.exe --policy rr .\workloads\mixed.csv
.\build\scheduler_sim.exe --policy interactive .\workloads\mixed.csv
```

Tablo görünümü için:

```powershell
.\build\scheduler_sim.exe --policy rr .\workloads\mixed.csv | ConvertFrom-Csv | Format-Table -AutoSize
.\build\scheduler_sim.exe --policy interactive .\workloads\mixed.csv | ConvertFrom-Csv | Format-Table -AutoSize
```

`gcc` bulunamıyorsa bu alternatif uygulanamaz; tam Linux akışı kullanılabilir.
`linux_baseline.c`, `make test` ve `make experiment` için bu Windows komutlarının
yeterli olduğu düşünülmemelidir; bunları WSL/Linux'ta çalıştırmak gerekir.

## 11. Sunum günü kısa akış

Kurulum, güncelleme ve prova sunumdan önce tamamlanır. Canlı gösterimde sırayla:

```bash
make
make test
cat workloads/mixed.csv
./build/scheduler_sim --policy rr workloads/mixed.csv
./build/scheduler_sim --policy interactive workloads/mixed.csv
```

Sonra 7. bölümdeki iki gerçek Linux ölçümü ve kısa özet gösterilebilir.
PDF'teki grafikleri göstermek için bütün deneyi yeniden çalıştırmak zorunlu değildir.
Yoğun etkileşimli senaryodaki gerilemeyi de anlatmak değerlendirmeyi tamamlar.

## 12. GitHub ile güncel çalışma

Başlarken `git status --short` ve `git pull --ff-only`; bitirirken önce
değişiklikleri inceleme, sonra yalnız paylaşılacak dosyaları seçerek commit/push:

```bash
git status --short
git diff
git add docs/hafta2/sunum_metni.md
git commit -m "Update presentation narration"
git push origin HEAD:main
```

Bu örnek yalnız ilgili metin dosyasını seçer. Dosya değişmediyse yeni commit
yapılmaz. `build/` ve `results/` çıktıları mevcut kurala göre Git dışında kalır;
her dosyayı seçmek için `git add .` kullanmak yerel ayar ve `.exe` dosyalarını da
yanlışlıkla paylaşabilir. Paylaşılacak yeni deney arşivi ayrıca incelenerek seçilir.
Gerçek ölçümlerin kaybolmaması için `make experiment` çıktısı olan dizin saklanır.
