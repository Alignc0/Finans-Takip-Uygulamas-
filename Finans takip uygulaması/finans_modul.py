import csv
import os
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt

class RENK:
    HEADER = ''
    MAVI = ''
    YESIL = ''
    UYARI = ''
    HATA = ''
    ENDC = ''
    BOLD = ''
    UNDERLINE = ''

KAYIT_DOSYASI = "finans_kayitlari.csv"
GELIR_DOSYASI = "gelir.txt"
KATEGORILER = ["Market", "Fatura", "Ulaşım", "Eğlence", "Giyim", "Sağlık", "Yatırım", "Borç", "Diğer"]

def verileri_oku(ay_filtresi=None):
    if not os.path.exists(KAYIT_DOSYASI):
        return []

    giderler = []
    with open(KAYIT_DOSYASI, mode="r", newline="", encoding="utf-8") as dosya:
        okuyucu = csv.DictReader(dosya)
        for satir in okuyucu:
            try:
                if satir["Tür"] == "Gider":
                    if ay_filtresi is None or satir["Tarih"].startswith(ay_filtresi):
                        satir["Miktar"] = float(satir["Miktar"])
                        giderler.append(satir)
            except (ValueError, KeyError):
                continue
    return giderler

def gelir_getir():
    try:
        with open(GELIR_DOSYASI, "r", encoding="utf-8") as f:
            gelir = float(f.read().strip())
            return gelir
    except (FileNotFoundError, ValueError):
        return None

def gelir_kaydet(gelir):
    with open(GELIR_DOSYASI, "w", encoding="utf-8") as f:
        f.write(str(gelir))

def kayit_ekle(kategori, aciklama, miktar):
    tarih = datetime.now().strftime("%Y-%m-%d")
    kayit = [tarih, "Gider", kategori, aciklama, miktar]
    dosya_yeni_mi = not os.path.exists(KAYIT_DOSYASI)
    with open(KAYIT_DOSYASI, mode="a", newline="", encoding="utf-8") as dosya:
        yazici = csv.writer(dosya)
        if dosya_yeni_mi:
            yazici.writerow(["Tarih", "Tür", "Kategori", "Açıklama", "Miktar"])
        yazici.writerow(kayit)

def kategori_grafik(gider_verileri, ay_str):
    if not gider_verileri:
        return None

    giderler = defaultdict(float)
    for satir in gider_verileri:
        giderler[satir["Kategori"]] += satir["Miktar"]

    kategoriler = list(giderler.keys())
    miktarlar = list(giderler.values())

    plt.figure(figsize=(8, 8))
    plt.pie(miktarlar, labels=kategoriler, autopct="%1.1f%%", startangle=140,
            wedgeprops={'edgecolor': 'white', 'linewidth': 1})
    plt.title(f"{ay_str} Ayı Gider Dağılımı", fontweight='bold')
    plt.axis("equal")
    plt.tight_layout()
    return plt

def aylik_harcama_verileri():
    tum_giderler = verileri_oku()
    if not tum_giderler:
        return None, None

    aylik_toplam = defaultdict(float)
    for satir in tum_giderler:
        ay = satir["Tarih"][:7]
        aylik_toplam[ay] += satir["Miktar"]

    sirali_aylar = sorted(aylik_toplam.keys())
    harcamalar = [aylik_toplam[ay] for ay in sirali_aylar]
    return sirali_aylar, harcamalar

def finans_mentoru_raporu(gider_verileri, ay_str):
    gelir = gelir_getir()
    if gelir is None:
        return None

    if not gider_verileri:
        return f"{ay_str} ayı için gider kaydı bulunamadı."

    gider_kategorileri = defaultdict(float)
    toplam_gider = 0
    for satir in gider_verileri:
        toplam_gider += satir["Miktar"]
        gider_kategorileri[satir["Kategori"]] += satir["Miktar"]

    bakiye = gelir - toplam_gider

    rapor = []
    rapor.append(f"Finansal Mentor Raporu ({ay_str})")
    rapor.append(f"Toplam Gelir: {gelir:.2f} ₺")
    rapor.append(f"Toplam Gider: {toplam_gider:.2f} ₺")
    rapor.append(f"Kalan Bakiye: {bakiye:.2f} ₺")
    rapor.append("")
    rapor.append("Kategori Harcama Oranları (Gelire Göre):")
    for kategori, miktar in sorted(gider_kategorileri.items(), key=lambda item: item[1], reverse=True):
        oran = (miktar / gelir) * 100
        rapor.append(f"  - {kategori}: %{oran:.1f}")

    rapor.append("\nTavsiyeler:")
    if toplam_gider > gelir:
        rapor.append("  Giderleriniz gelirinizi aşıyor! Harcamalarınızı acilen gözden geçirin.")
    elif bakiye < gelir * 0.15:
        rapor.append("  Tasarruf oranınız çok düşük. Gelirin en az %15'ini ayırmaya çalışın.")
    else:
        rapor.append("  Finansal dengeniz sağlıklı görünüyor. Tasarruf veya yatırım yapabilirsiniz.")

    if gider_kategorileri["Yatırım"] < gelir * 0.1 and bakiye > 0:
        rapor.append("  Yatırıma daha fazla pay ayırmanız uzun vadede faydalı olur.")

    if gider_kategorileri["Market"] > gelir * 0.3:
        rapor.append("  Market harcamalarınızı azaltmaya çalışın.")

    return "\n".join(rapor)