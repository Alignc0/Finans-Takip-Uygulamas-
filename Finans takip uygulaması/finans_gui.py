import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QComboBox, QLineEdit, QMessageBox,
    QTextEdit, QInputDialog, QDialog, QFormLayout
)
from PyQt5.QtCore import QDate
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import finans_modul as fm
from datetime import datetime

class GrafikPenceresi(QDialog):
    def __init__(self, plt_obj, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Grafik")
        self.fig = plt_obj.gcf()
        self.canvas = FigureCanvas(self.fig)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.resize(600, 600)

class FinansApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Kişisel Finans Takip Sistemi (PyQt5)")
        self.setGeometry(300, 100, 700, 500)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QVBoxLayout()

        gelir_hb = QHBoxLayout()
        self.gelir_label = QLabel("Aylık Gelir: --- ₺")
        self.gelir_guncelle_btn = QPushButton("Geliri Belirle / Güncelle")
        self.gelir_guncelle_btn.clicked.connect(self.gelir_guncelle)
        gelir_hb.addWidget(self.gelir_label)
        gelir_hb.addWidget(self.gelir_guncelle_btn)
        layout.addLayout(gelir_hb)

        layout.addWidget(QLabel("Yeni Gider Kaydı Ekle"))
        form_layout = QFormLayout()
        self.kategori_combo = QComboBox()
        self.kategori_combo.addItems(fm.KATEGORILER)
        self.aciklama_input = QLineEdit()
        self.miktar_input = QLineEdit()
        form_layout.addRow("Kategori:", self.kategori_combo)
        form_layout.addRow("Açıklama:", self.aciklama_input)
        form_layout.addRow("Miktar (₺):", self.miktar_input)
        layout.addLayout(form_layout)
        self.gider_ekle_btn = QPushButton("Gideri Kaydet")
        self.gider_ekle_btn.clicked.connect(self.gider_ekle)
        layout.addWidget(self.gider_ekle_btn)

        ay_hb = QHBoxLayout()
        ay_hb.addWidget(QLabel("Analiz için Ay Seç:"))
        self.ay_input = QLineEdit()
        self.ay_input.setPlaceholderText("YYYY-AA (Boşsa güncel ay)")
        ay_hb.addWidget(self.ay_input)
        layout.addLayout(ay_hb)

        btn_hb = QHBoxLayout()
        self.ozet_btn = QPushButton("Aylık Finansal Özet Göster")
        self.ozet_btn.clicked.connect(self.finans_ozet)
        btn_hb.addWidget(self.ozet_btn)

        self.grafik_btn = QPushButton("Kategori Harcama Grafiği")
        self.grafik_btn.clicked.connect(self.kategori_grafik_goster)
        btn_hb.addWidget(self.grafik_btn)

        self.harcama_btn = QPushButton("Tüm Zamanlar Harcama Grafiği")
        self.harcama_btn.clicked.connect(self.tum_zamanlar_grafik)
        btn_hb.addWidget(self.harcama_btn)

        self.mentor_btn = QPushButton("Finansal Mentor Raporu")
        self.mentor_btn.clicked.connect(self.finans_mentor)
        btn_hb.addWidget(self.mentor_btn)

        layout.addLayout(btn_hb)

        self.rapor_metni = QTextEdit()
        self.rapor_metni.setReadOnly(True)
        layout.addWidget(self.rapor_metni)

        self.central_widget.setLayout(layout)

        self.gelir_goster()

    def gelir_goster(self):
        gelir = fm.gelir_getir()
        if gelir is None:
            self.gelir_label.setText("Aylık Gelir: Belirtilmemiş")
        else:
            self.gelir_label.setText(f"Aylık Gelir: {gelir:.2f} ₺")

    def gelir_guncelle(self):
        gelir, ok = QInputDialog.getDouble(self, "Gelir Belirle", "Aylık net gelirinizi girin (₺):", decimals=2, min=0)
        if ok:
            fm.gelir_kaydet(gelir)
            self.gelir_goster()
            QMessageBox.information(self, "Başarılı", "Gelir başarıyla kaydedildi.")

    def gider_ekle(self):
        kategori = self.kategori_combo.currentText()
        aciklama = self.aciklama_input.text().strip()
        try:
            miktar = float(self.miktar_input.text())
        except ValueError:
            QMessageBox.warning(self, "Hata", "Miktar geçersiz. Lütfen sayı girin.")
            return

        if miktar <= 0:
            QMessageBox.warning(self, "Hata", "Miktar pozitif olmalı.")
            return

        fm.kayit_ekle(kategori, aciklama, miktar)
        QMessageBox.information(self, "Başarılı", "Gider kaydı başarıyla eklendi.")
        self.aciklama_input.clear()
        self.miktar_input.clear()

    def ay_getir(self):
        ay_str = self.ay_input.text().strip()
        if not ay_str:
            ay_str = datetime.now().strftime("%Y-%m")
        try:
            datetime.strptime(ay_str, "%Y-%m")
            return ay_str
        except ValueError:
            QMessageBox.warning(self, "Hata", "Ay formatı yanlış. 'YYYY-AA' formatında olmalı.")
            return None

    def finans_ozet(self):
        ay_str = self.ay_getir()
        if ay_str is None:
            return
        gider_verileri = fm.verileri_oku(ay_str)
        gelir = fm.gelir_getir()
        if gelir is None:
            QMessageBox.warning(self, "Hata", "Önce aylık gelirinizi belirleyin.")
            return

        toplam_gider = sum(k["Miktar"] for k in gider_verileri)
        bakiye = gelir - toplam_gider
        metin = (
            f"Finansal Özet ({ay_str}):\n\n"
            f"Gelir: {gelir:.2f} ₺\n"
            f"Gider: {toplam_gider:.2f} ₺\n"
            f"Kalan Bakiye: {bakiye:.2f} ₺"
        )
        self.rapor_metni.setPlainText(metin)

    def kategori_grafik_goster(self):
        ay_str = self.ay_getir()
        if ay_str is None:
            return
        gider_verileri = fm.verileri_oku(ay_str)
        if not gider_verileri:
            QMessageBox.information(self, "Bilgi", f"{ay_str} için gider kaydı bulunmuyor.")
            return
        plt_obj = fm.kategori_grafik(gider_verileri, ay_str)
        if plt_obj is None:
            QMessageBox.information(self, "Bilgi", "Grafik için veri bulunamadı.")
            return
        dialog = GrafikPenceresi(plt_obj, self)
        dialog.exec_()
        plt.close()

    def tum_zamanlar_grafik(self):
        aylar, harcamalar = fm.aylik_harcama_verileri()
        if aylar is None or harcamalar is None:
            QMessageBox.information(self, "Bilgi", "Henüz gider kaydı bulunmuyor.")
            return

        plt.figure(figsize=(10, 6))
        plt.bar(aylar, harcamalar, color="skyblue")
        plt.title("Aylık Gider Değişimi", fontweight='bold')
        plt.xlabel("Ay")
        plt.ylabel("Toplam Gider (₺)")
        plt.xticks(rotation=45)
        plt.grid(axis="y", linestyle='--', alpha=0.7)
        plt.tight_layout()

        dialog = GrafikPenceresi(plt, self)
        dialog.exec_()
        plt.close()

    def finans_mentor(self):
        ay_str = self.ay_getir()
        if ay_str is None:
            return
        gider_verileri = fm.verileri_oku(ay_str)
        rapor = fm.finans_mentoru_raporu(gider_verileri, ay_str)
        if rapor is None:
            QMessageBox.warning(self, "Hata", "Önce aylık gelirinizi belirleyin.")
            return
        self.rapor_metni.setPlainText(rapor)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pencere = FinansApp()
    pencere.show()
    sys.exit(app.exec_())