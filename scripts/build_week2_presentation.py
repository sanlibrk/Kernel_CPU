#!/usr/bin/env python3
"""Create the week-two presentation from the archived, measured data group."""
from html import escape
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "experiments/hafta2/2026-11-05"
OUT = ROOT / "docs/hafta2"
FIGURES = OUT / "grafikler"
PDF = OUT / "Burak_Sanli_Hafta2_CPU_Zamanlama.pdf"
BG = "#0B1728"
PANEL = "#11253B"
TEXT = "#E5EDF7"
MUTED = "#ACBDCF"
TEAL = "#2BD0C3"
BLUE = "#69AFFF"
ORANGE = "#F9B66B"
REPO = "https://github.com/sanlibrk/Kernel_CPU/tree/main/docs/hafta2"
W, H = 960, 540


def figures(data):
    FIGURES.mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 11,
                         "text.color": TEXT, "axes.labelcolor": MUTED,
                         "xtick.color": TEXT, "ytick.color": MUTED,
                         "axes.edgecolor": "#40536A", "axes.facecolor": BG,
                         "figure.facecolor": BG, "savefig.facecolor": BG})

    def bars(ax, values, title, ylabel, labels=("RR", "Prototip")):
        ax.bar(labels, values, color=[BLUE, TEAL], width=.53)
        ax.set_title(title, color=TEXT, pad=16, fontsize=13)
        ax.set_ylabel(ylabel)
        ax.set_ylim(0, max(values) * 1.35)
        ax.spines[["top", "right"]].set_visible(False)
        ax.grid(axis="y", alpha=.12)
        ax.set_axisbelow(True)
        for i, value in enumerate(values):
            label = f"{value:.3f}".rstrip("0").rstrip(".")
            ax.text(i, value + max(values) * .045, label, ha="center", fontsize=13)

    mixed = data["model"]["mixed"]
    pressure = data["model"]["interactive_pressure"]
    for name, model in (("mixed", mixed), ("interactive_pressure", pressure)):
        fig, axes = plt.subplots(1, 2, figsize=(11, 3.15), layout="constrained")
        bars(axes[0], [model[p]["interactive"]["response_mean_ms"]
                      for p in ("rr", "interactive")],
             "Etkileşimli görev: ortalama ilk yanıt", "Süre (ms)")
        if name == "mixed":
            bars(axes[1], [model[p]["background"]["turnaround_mean_ms"]
                          for p in ("rr", "interactive")],
                 "Arka plan: ortalama dönüş süresi", "Süre (ms)")
        else:
            bars(axes[1], [model[p]["interactive"]["waiting_mean_ms"]
                          for p in ("rr", "interactive")],
                 "Etkileşimli görev: toplam bekleme", "Ortalama süre (ms)")
        fig.savefig(FIGURES / f"{name}.png", dpi=170)
        plt.close(fig)

    fig, ax = plt.subplots(figsize=(11, 3.15), layout="constrained")
    rows = data["linux_baseline"]
    for offset, workers, color, label in ((-.18, 0, BLUE, "0 arka plan işçisi"),
                                         (.18, 2, TEAL, "2 arka plan işçisi")):
        selected = [r for r in rows if r["workers"] == workers]
        x = [r["repetition"] + offset for r in selected]
        values = [r["wake_p95_ms"] for r in selected]
        ax.bar(x, values, width=.32, color=color, label=label)
        for xx, value in zip(x, values):
            ax.text(xx, value + .065, f"{value:.3f}", ha="center", fontsize=11)
    ax.set_xticks([1, 2, 3], ["Tekrar 1", "Tekrar 2", "Tekrar 3"])
    ax.set_ylabel("P95 uyanma gecikmesi (ms)")
    ax.set_ylim(0, 3.8)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left", labelcolor=TEXT)
    ax.grid(axis="y", alpha=.12)
    ax.set_axisbelow(True)
    fig.savefig(FIGURES / "linux_p95.png", dpi=170)
    plt.close(fig)


class Presentation:
    def __init__(self):
        fonts = Path(matplotlib.get_data_path()) / "fonts/ttf"
        for name, filename in (("Body", "DejaVuSans.ttf"),
                               ("Bold", "DejaVuSans-Bold.ttf"),
                               ("Mono", "DejaVuSansMono.ttf")):
            pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
        self.c = canvas.Canvas(str(PDF), pagesize=(W, H), invariant=1)
        self.c.setTitle("CPU yönetimi ve süreç zamanlama — Hafta 2")
        self.c.setAuthor("Burak Şanlı")
        self.c.setSubject("C politika prototipi, Linux başlangıç ölçümleri ve ikinci hafta değerlendirmesi")
        self.page = 0

    def text(self, value, x, y, width=880, size=16, color=TEXT, font="Body"):
        style = ParagraphStyle("slide", fontName=font, fontSize=size,
                               leading=size * 1.4, textColor=colors.HexColor(color))
        paragraph = Paragraph(escape(value).replace("\n", "<br/>"), style)
        _, height = paragraph.wrap(width, 1000)
        assert y - height >= 0, f"Text outside page {self.page}: {value}"
        paragraph.drawOn(self.c, x, y - height)
        return y - height

    def start(self, title, subtitle, note):
        if self.page:
            self.c.showPage()
        self.page += 1
        c = self.c
        c.setFillColor(colors.HexColor(BG))
        c.rect(0, 0, W, H, fill=1, stroke=0)
        c.setFillColor(colors.HexColor(TEAL))
        c.rect(40, 496, 40, 4, fill=1, stroke=0)
        self.text(title, 40, 474, size=25, font="Bold")
        self.text(subtitle, 40, 425, size=14, color=TEAL)
        c.setStrokeColor(colors.HexColor("#31455D"))
        c.line(40, 126, 920, 126)
        self.text(note, 48, 113, width=864, size=10.4, color=MUTED)
        self.text("Burak Şanlı • CPU Zamanlaması • Hafta 2", 40, 31, size=8.5, color=MUTED)
        self.text(f"{self.page:02d} / 18", 863, 31, width=70, size=8.5, color=MUTED)
        c.linkURL(REPO, (40, 16, 380, 36), relative=0, thickness=0)

    def bullets(self, values, y=380, size=16):
        for value in values:
            self.c.setFillColor(colors.HexColor(TEAL))
            self.c.circle(45, y - 11, 2.7, fill=1, stroke=0)
            y = self.text(value, 61, y, width=850, size=size) - 18
        assert y >= 135, f"Body overlaps footer on slide {self.page}"

    def table(self, headers, rows, widths, y=382, row_height=38, size=12):
        c = self.c
        x = 40
        for i, row in enumerate([headers, *rows]):
            c.setFillColor(colors.HexColor(PANEL if i % 2 == 0 else BG))
            c.rect(40, y - row_height, 880, row_height, fill=1, stroke=0)
            x = 49
            for value, width in zip(row, widths):
                bottom = self.text(str(value), x, y - 7, width=width - 18,
                                   size=size, color=TEAL if i == 0 else TEXT,
                                   font="Bold" if i == 0 else "Body")
                assert bottom >= y - row_height + 2, f"Table row overflow on slide {self.page}"
                x += width
            y -= row_height
        assert y >= 136, f"Table overlaps footer on slide {self.page}"

    def code(self, lines, y=380):
        c = self.c
        height = 28 * len(lines) + 22
        c.setFillColor(colors.HexColor(PANEL))
        c.roundRect(40, y - height, 880, height, 6, fill=1, stroke=0)
        for i, line in enumerate(lines):
            self.text(line, 58, y - 12 - i * 28, size=14, color=TEAL, font="Mono")
        assert y - height >= 140

    def chart(self, name):
        self.c.drawImage(ImageReader(str(FIGURES / name)), 40, 154,
                         width=880, height=252, mask="auto")

    def save(self):
        assert self.page == 18
        self.c.save()


def main():
    data = json.loads((ARCHIVE / "summary.json").read_text())
    assert data["tests"] == {"passed": 13, "failed": 0, "skipped": 0}
    assert len(data["linux_baseline"]) == 6
    assert sum(row["sample_count"] for row in data["linux_baseline"]) == 240
    # Prevent a presentation from silently mixing data from another experiment.
    for row in data["linux_baseline"]:
        raw = json.loads((ARCHIVE / row["file"]).read_text())
        assert raw["wake_p95_ms"] == row["wake_p95_ms"]
        assert len(raw["samples"]) == row["sample_count"]
    figures(data)
    p = Presentation()
    p.start("CPU yönetimi ve süreç zamanlama", "Hafta 2 — C prototipi ve ilk deneyler",
            "Bu sunum, 5 Kasım 2026 tarihinde kaydedilen deney grubuna dayanır. Özel politika henüz Linux çekirdeğine yüklenmemiştir.")
    p.text("HARRAN ÜNİVERSİTESİ", 40, 365, size=20, font="Bold")
    p.text("Bilgisayar Mühendisliği • Bitirme Projesi", 40, 322, size=17, color=MUTED)
    p.text("Burak Şanlı\nÖğrenci Numarası: 210504018", 40, 260, size=18)
    p.text("Danışman: Prof. Dr. Dursun Akaslan", 40, 185, size=16, color=TEAL)

    p.start("Araştırma sorusu ve bu haftanın kapsamı", "Kısa görevlerin yanıtı ile uzun işlerin ilerlemesini birlikte değerlendirmek",
            "İlk hafta problem ve teknik seçenekler tanımlandı. İkinci hafta model uygulaması, ölçüm aracı ve ilk doğrulamalar tamamlandı.")
    p.bullets(["CPU yoğun arka plan işleri varken kısa ve etkileşimli görevlerin beklemesi incelenmektedir.",
               "Politika kuralları, denetlenebilir bir C modelinde uygulanmıştır.",
               "Gerçek Linux için mevcut davranışı kaydeden ayrı bir başlangıç ölçüm programı geliştirilmiştir."])

    p.start("Geliştirilen bileşenler", "Kaynak kod, deney yürütme ve doğrulama ayrı sorumluluklara sahiptir.",
            "Kaynak kodlar, teknik belgeler ve seçilmiş ham veriler GitHub üzerinde sürümlendirilmiştir.")
    p.table(["Bileşen", "Sorumluluk"], [
        ["src/scheduler_sim.c", "Tek CPU modeli; RR ve tercih politikası"],
        ["src/linux_baseline.c", "Gerçek süreçlerle gecikme ve işçi süreleri"],
        ["tests/test_scheduling.py", "13 test yöntemi ve alt testler"],
        ["scripts/run_experiments.py", "Test, 6 model ve 6 Linux koşusu"],
        ["experiments/hafta2/2026-11-05", "Özgün kayıtlar ve bütünlük özetleri"]], [340, 540], size=12)

    p.start("Derleme ve deneylerin tekrarlanması", "Linux • GCC/C11 • GNU Make • Python 3.10+",
            "Komutlar depo kökünde yürütülür. Gerçek zaman ölçümleri ortam yüküyle değişebilir; model aynı girdilerde deterministiktir.")
    p.code(["make", "make test", "make experiment"])
    p.text("Yeni koşular results/ altında ayrı bir dizine yazılır.\n"
           "Son başarılı deney, latest.json işaretçisiyle bulunur.", 48, 237, size=15)

    p.start("Görev girdisi ve süre ölçütleri", "Modelde her görev tek CPU patlamasına sahiptir; sınıf girişte tanımlanır.",
            "Model görev numarası Linux süreç kimliği değildir. Toplam bekleme, ilk yanıt süresinden farklı bir ölçüttür.")
    p.table(["Alan / ölçüt", "Tanım"], [
        ["id, class", "Benzersiz görev numarası; background / interactive"],
        ["arrival_ms, burst_ms", "Hazır olma anı ve toplam CPU ihtiyacı"],
        ["response_ms", "İlk başlama − varış"],
        ["waiting_ms", "Tamamlanma − varış − CPU ihtiyacı"],
        ["turnaround_ms", "Tamamlanma − varış"]], [285, 595], size=12)

    p.start("Politikanın başlangıç kuralları", "Sınırlı tercih bütçesi ve uzun bekleyen görevlere yaşlandırma",
            "Parametreler başlangıç tasarımıdır. Bütçe, yaşlandırma ve tek sınıflı yük istisnaları nedeniyle katı CPU kotası değildir.")
    p.bullets(["Zaman dilimi 4 ms; sabit 20 ms pencerede 8 ms etkileşimli tercih bütçesi.",
               "Bütçe tükenince hazır arka plan görevlerine sıra verilir.",
               "Seçim anında en az 20 ms bekleyen görevler yaşlandırma önceliği alır.",
               "Sınıf içinde kuyruk sırası korunur; hazır iş varken CPU boş bırakılmaz."], size=15)

    p.start("Bir model adımındaki karar sırası", "1 ms adımlar; çalışan görev zaman dilimi veya bütçe koşuluyla yeniden seçilir.",
            "Yaşlandırma son yeniden kuyruğa girişten beri beklemeyi kullanır. Yeni görev gelişi veya pencere yenilenmesi tek başına kesme oluşturmaz.")
    p.bullets(["Pencere sınırında bütçeyi yenile; zamanı gelen görevleri kuyruğa al.",
               "Gerekirse çalışan görevi yeniden kuyruğa koy; önce yaşlandırmayı değerlendir.",
               "Yaşlandırılmış görev yoksa bütçeye göre sınıfı, sonra kuyruk adayını seç.",
               "1 ms CPU ihtiyacını tüket; kalan süreyi, bütçeyi ve bitişi güncelle."], size=15)

    p.start("Kontrollü örnekte ilk yanıt", "Görev 1 ve 2: varış 0, CPU 20 ms; görev 3: varış 1, CPU 1 ms",
            "Bu küçük örnek otomatik testte kontrol edilir. Görev 3 için ilk yanıt RR'de 7 ms, prototipte 3 ms'dir; gerçek Linux sonucu değildir.")
    p.table(["Politika", "0–4 ms", "4–5 ms", "5–8 ms", "8–9 ms"], [
        ["RR", "Görev 1", "Görev 2", "Görev 2", "Görev 3"],
        ["Prototip", "Görev 1", "Görev 3", "Görev 2", "Görev 2"]],
        [180, 175, 175, 175, 175], row_height=48, size=13)
    p.text("İlk yanıtın erken verilmesi, görevin sonraki beklemelerinin\n"
           "ve bütün işlerin tamamlanmasının ayrıca ölçülmesini gerektirir.", 48, 203, size=16)

    p.start("Karşılaştırılan model senaryoları", "Aynı görevler ve aynı parametrelerle iki politika karşılaştırılır.",
            "Modelde I/O, CPU göçü, çok çekirdek ve bağlam değiştirme maliyeti yoktur. RR, Linux'un adil zamanlayıcısının modeli değildir.")
    p.table(["Senaryo", "Arka plan", "Etkileşimli", "Toplam iş"], [
        ["cpu_only", "3 × 120 ms", "Yok", "360 ms"],
        ["mixed", "3 × 120 ms", "8 × 2 ms", "376 ms"],
        ["interactive_pressure", "3 × 80 ms", "12 × 20 ms", "480 ms"]],
        [290, 190, 220, 180], row_height=48, size=13)

    p.start("Karışık model iş yükünün sonucu", "8 kısa etkileşimli görev ve 3 uzun arka plan görevi",
            "Ortalama ilk yanıt 11 ms'den 3 ms'ye iner. Arka plan ortalama dönüşü 372 ms, son bitiş 376 ms olarak kalır. Sonuç modelle sınırlıdır.")
    p.chart("mixed.png")

    p.start("Yoğun yükte ölçütler farklılaşabiliyor", "İlk yanıt iyileşirken toplam bekleme artabiliyor.",
            "İlk yanıt: 31,333 → 19,333 ms. Toplam bekleme: 252,667 → 303,833 ms. Genel başarı tek bir gecikme ölçütüne indirgenemez.")
    p.chart("interactive_pressure.png")

    p.start("Gerçek Linux ölçümünün düzeni", "Mevcut SCHED_OTHER davranışının başlangıç çizgisi",
            "İlk doğrulama ortamı: Debian 13, Linux 6.18.57. Ortak CPU özel olarak yalıtılmamıştır; timer ve sanallaştırma etkileri ölçüme katılabilir.")
    p.bullets(["Ana süreç ve 0 veya 2 arka plan işçisi aynı izinli mantıksal CPU'ya sabitlenir.",
               "40 kısa iş: 20 ms periyot, hedef 500 µs CPU süresi; işçi başına 800 ms CPU bütçesi.",
               "Mutlak monoton saatle hedefler, süreç CPU saatiyle iş bütçesi ölçülür.",
               "Üç tekrar; her tekrarda önce 0, sonra 2 işçi. Toplam 240 kısa iş örneği."], size=15)

    p.start("Gerçek Linux: P95 uyanma gecikmesi", "Her sütun 40 örnekli ayrı bir koşunun en yakın sıra P95 değeridir.",
            "Arka plan yüküyle daha yüksek gecikme gözlenmiştir. Özel politika bu koşularda uygulanmadı; grafik Linux'a karşı politika kazancı değildir.")
    p.chart("linux_p95.png")

    p.start("Arka plan işlerinin tamamlanması", "İşçiler kendi CPU ve duvar saati sürelerini kaydetmektedir.",
            "İş yükü CPU zamanı bütçesiyle sınırlıdır; sabit sayıda hesaplama işlemi yapan bir işlem hacmi veya hızlanma testi değildir.")
    rows = [r for r in data["linux_baseline"] if r["workers"] == 2]
    p.table(["Tekrar", "İşçi 0 duvar saati", "İşçi 1 duvar saati", "CPU hedefi"],
            [[r["repetition"], f"{r['background_wall_ms'][0]:.3f} ms",
              f"{r['background_wall_ms'][1]:.3f} ms", "800 ms / işçi"] for r in rows],
            [130, 260, 260, 230], row_height=45, size=12)
    p.text("Bütün arka plan işçileri tamamlanmıştır. İşçi bitişi,\n"
           "ana sürecin beklemeden dönüş anıyla karıştırılmamıştır.", 48, 183, size=15)

    p.start("Otomatik doğrulamanın sonucu", "13 başarılı test yöntemi • 0 başarısız • 0 atlanan",
            "Testler seçili örnekleri doğrular. Tüm iş yüklerinde adalet, açlık oluşmaması veya çekirdek entegrasyonunun doğruluğu için ispat değildir.")
    p.bullets(["Analitik RR takvimi, boş CPU, giriş sırası, bütçe ve yaşlandırma örnekleri.",
               "20 sabit tohumlu iş yükü × 2 politika: görev bitişleri ve süre muhasebesi.",
               "Geçersiz girdilerin reddi; 0 ve 2 gerçek işçiyle çıktı ve tamamlanma kontrolleri.",
               "Test günlüğü, ham CSV/JSON ve kaynak özetleri deney arşivinde korunmaktadır."], size=15)

    p.start("Sınırlılıklar ve yorum sınırı", "Gözlenen sonuç ile henüz doğrulanmamış özellikler ayrı değerlendirilir.",
            "Yerel Ubuntu kurulumu veya bu bilgisayardaki performans, bu arşivlenmiş deneylerin doğruladığı bir sonuç olarak sunulmamıştır.")
    p.bullets(["Model tek CPU ve tek patlamalı görevlerle sınırlı; otomatik sınıflandırma yok.",
               "Bütçe ve yaşlandırma kesin gecikme üst sınırı sağlamıyor.",
               "Gerçek ölçüm üç tekrar; koşul sırası sabit, ortam yükü bütünüyle kontrol edilmiyor.",
               "Özel politika henüz çekirdekte çalışmıyor; Linux'a karşı iyileşme iddiası yok."], size=15)

    p.start("İkinci haftanın somut çıktıları", "Konu seçiminden çalıştırılabilir ve izlenebilir bir ilk uygulamaya geçiş",
            "Deney tabloları ve grafikler ilk deney arşivine, kontrollü örnek otomatik testteki görev tanımına dayanır. Teknik belgeler GitHub'dadır.")
    p.bullets(["C politika prototipi ve bağımsız gerçek Linux başlangıç ölçüm programı.",
               "Üç model senaryosu, altı model koşusu ve altı gerçek Linux koşusu.",
               "Başarılı test günlüğü, kaynak özetleri ve özgün ham ölçüm kayıtları.",
               "Haftalık belgeler, uygulama açıklaması, sonuç değerlendirmesi ve PDF sunumu."], size=15)

    p.start("Sonraki aşama ve geçiş ölçütleri", "Önce uygun test ortamı ve güvenli yükleme, ardından politika entegrasyonu",
            "Bu başlıklar gelecek geliştirme hedefleridir; tamamlanmış uygulama veya deney sonucu olarak sunulmamaktadır.")
    p.bullets(["Ekip çekirdeğini ve ayrı test VM'ini belirle; sched_ext/BTF, araç zinciri ve yetkileri doğrula.",
               "Örnek politikanın yüklenmesi, kaldırılması ve varsayılan zamanlayıcıya dönüşünü test et.",
               "Bütçe ve yaşlandırma kurallarını çekirdeğe taşı; aynı gerçek iş yüklerinde karşılaştır.",
               "Daha çok tekrar, uzun işlerin ilerlemesi, adalet ve politika maliyetini birlikte değerlendir."], size=15)
    p.save()
    print(f"Created {PDF} (18 slides) from archived data; no new experiment was run.")


if __name__ == "__main__":
    main()
