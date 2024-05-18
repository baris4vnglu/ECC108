import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkinter import Spinbox
from tkinter import PhotoImage
from datetime import datetime
import random
import subprocess

class Proje:
    def __init__(self, ad, tarih=None, durum="İşlemde"):
        self.ad = ad
        self.tarih = tarih if tarih else datetime.now()
        self.durum = durum
        self.notlar = []

        

    def durumu_degistir(self, durum):
        self.durum = durum

    def not_ekle(self, not_metni):
        self.notlar.append(not_metni)

    def not_sil(self, index):
        del self.notlar[index]

    def kalan_sure(self):
        simdiki_zaman = datetime.now()
        kalan_zaman = self.tarih - simdiki_zaman
        if kalan_zaman.total_seconds() < 0:
            return f"Project Overdue"
        else:
            günler = kalan_zaman.days
            saatler, saniyeler = divmod(kalan_zaman.seconds, 3600)
            dakikalar, saniyeler = divmod(saniyeler, 60)
            return f"{günler} day {saatler} hour {dakikalar} minute left"

    def __str__(self):
        return f"{self.ad} - {self.tarih} - {self.durum}"


class ProjeEklePenceresi(tk.Toplevel):
    def __init__(self, parent, onay_callback):
        super().__init__(parent)
        self.parent = parent
        self.onay_callback = onay_callback

        self.title("add project")

        self.proje_adi_label = tk.Label(self, text="Project name:")
        self.proje_adi_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.proje_adi_giris = tk.Entry(self)
        self.proje_adi_giris.grid(row=0, column=1, padx=10, pady=5)

        self.proje_tarih_label = tk.Label(self, text="project day (day/mounth/year):")
        self.proje_tarih_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.proje_gun_giris = Spinbox(self, from_=1, to=31, width=5)
        self.proje_gun_giris.grid(row=1, column=1, padx=5, pady=5)
        self.proje_ay_giris = Spinbox(self, from_=1, to=12, width=5)
        self.proje_ay_giris.grid(row=1, column=2, padx=5, pady=5)
        self.proje_yil_giris = Spinbox(self, from_=1900, to=2200, width=8)
        self.proje_yil_giris.grid(row=1, column=3, padx=5, pady=5)

        self.onay_button = tk.Button(self, text="Approve", command=self.onayla)
        self.onay_button.grid(row=2, columnspan=4, padx=10, pady=10)

    def onayla(self):
        proje_adi = self.proje_adi_giris.get()
        gun = self.proje_gun_giris.get()
        ay = self.proje_ay_giris.get()
        yil = self.proje_yil_giris.get()
        
        if proje_adi and gun and ay and yil:
            try:
                proje_tarih = datetime(int(yil), int(ay), int(gun))
                self.onay_callback(proje_adi, proje_tarih)
                self.destroy()  # Pencereyi kapat
            except ValueError:
                messagebox.showerror("error", "Please enter a valid date.")        
        else:
            messagebox.showerror("error", "Please fill in all fields.")


class ProjeDurumDegistirPenceresi(tk.Toplevel):
    def __init__(self, parent, proje):
        super().__init__(parent)
        self.parent = parent
        self.proje = proje

        self.title("Change Project Status")

        self.durum_label = tk.Label(self, text="Select New Status:")
        self.durum_label.pack()

        self.yeni_durum = tk.StringVar(self)
        self.yeni_durum.set("in process")
        self.durum_secim = tk.OptionMenu(self, self.yeni_durum, "in process", "Completed", "Continues", "In development")
        self.durum_secim.pack()

        self.onay_button = tk.Button(self, text="Approve", command=self.durumu_degistir)
        self.onay_button.pack()

    def durumu_degistir(self):
        yeni_durum = self.yeni_durum.get()
        self.proje.durumu_degistir(yeni_durum)
        self.parent.listele_projeler()
        self.destroy()


class NotEklePenceresi(tk.Toplevel):
    def __init__(self, parent, proje):
        super().__init__(parent)
        self.parent = parent
        self.proje = proje

        self.title(f"Add Note - {proje.ad}")

        self.not_metni_label = tk.Label(self, text="Note Text:")
        self.not_metni_label.pack()

        self.not_metni_giris = tk.Entry(self)
        self.not_metni_giris.pack()

        self.ekle_button = tk.Button(self, text="Add Note", command=self.not_ekle)
        self.ekle_button.pack()

    def not_ekle(self):
        not_metni = self.not_metni_giris.get()
        if not_metni:
            self.proje.not_ekle(not_metni)
            self.parent.goster_notlar(self.proje)
            self.destroy()
        else:
            messagebox.showerror("error", "Please enter note text.")


class ProjelerSayfasi(tk.Toplevel):
    def __init__(self, parent, projeler):
        super().__init__(parent)
        self.parent = parent
        self.projeler = projeler
        self.title("Projects Page")

        self.projeler_frame = tk.Frame(self)
        self.projeler_frame.pack()

        self.projeler_listesi = tk.Listbox(self.projeler_frame, height=10, width=50)
        self.projeler_listesi.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.projeler_listesi.bind("<<ListboxSelect>>", self.goster_notlar)

        self.scrollbar = tk.Scrollbar(self.projeler_frame, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.projeler_listesi.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.projeler_listesi.config(yscrollcommand=self.scrollbar.set)

        self.ekle_button = tk.Button(self.projeler_frame, text="Add Project", command=self.proje_ekle)
        self.ekle_button.pack()

        self.durum_degistir_button = tk.Button(self.projeler_frame, text="Change Project Status", command=self.proje_durum_degistir)
        self.durum_degistir_button.pack()

        self.not_ekle_button = tk.Button(self.projeler_frame, text="Add Note", command=self.not_ekle)
        self.not_ekle_button.pack()

        self.sil_button = tk.Button(self.projeler_frame, text="Delete Selected Project", command=self.proje_sil)
        self.sil_button.pack()

        self.kapat_button = tk.Button(self, text="Close Page", command=self.sayfayi_kapat)
        self.kapat_button.pack()

        self.notlar_frame = tk.Frame(self)
        self.notlar_listesi = tk.Listbox(self.notlar_frame, height=5, width=50)
        self.not_scrollbar = tk.Scrollbar(self.notlar_frame, orient=tk.VERTICAL)
        self.not_scrollbar.config(command=self.notlar_listesi.yview)
        self.not_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.notlar_listesi.config(yscrollcommand=self.not_scrollbar.set)

        self.listele_projeler()

    def proje_ekle(self):
        def onay_callback(adi, tarih):
            yeni_proje = Proje(adi, tarih)
            self.projeler.append(yeni_proje)
            self.listele_projeler()
            messagebox.showinfo("Approve", "The project has been added successfully.")

        proje_ekle_pencere = ProjeEklePenceresi(self, onay_callback)

    def proje_durum_degistir(self):
        secili = self.projeler_listesi.curselection()
        if secili:
            index = secili[0]
            proje = self.projeler[index]
            durum_degistir_pencere = ProjeDurumDegistirPenceresi(self, proje)
        else:
            messagebox.showerror("error", "Please select a project..")

    def not_ekle(self):
        secili = self.projeler_listesi.curselection()
        if secili:
            index = secili[0]
            proje = self.projeler[index]
            not_ekle_pencere = NotEklePenceresi(self, proje)
        else:
            messagebox.showerror("Error", "Please select a project.")

    def goster_notlar(self, event):
        secili = self.projeler_listesi.curselection()
        if secili:
            index = secili[0]
            proje = self.projeler[index]
            self.notlar_frame.pack()
            self.notlar_listesi.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            self.not_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            self.notlar_listesi.delete(0, tk.END)
            for not_metni in proje.notlar:
                self.notlar_listesi.insert(tk.END, not_metni)
        else:
            self.notlar_frame.pack_forget()

    def proje_sil(self):
        secili = self.projeler_listesi.curselection()
        if secili:
            index = secili[0]
            del self.projeler[index]
            self.listele_projeler()
            messagebox.showinfo("Successful", "The project has been deleted successfully.")
        else:
            messagebox.showerror("Error", "Please select a project.")

    def listele_projeler(self):
        self.projeler_listesi.delete(0, tk.END)
        for proje in self.projeler:
            kalan_zaman = proje.kalan_sure()
            self.projeler_listesi.insert(tk.END, f"{str(proje)} - {kalan_zaman}")

    def sayfayi_kapat(self):
        self.destroy()
        self.parent.deiconify()


class Ders:
    def __init__(self, ad, gun, saat_araligi):
        self.ad = ad
        self.gun = gun
        self.saat_araligi = saat_araligi

    def __str__(self):
        return f"{self.ad} - {self.gun} - {self.saat_araligi}"


class DersEklePenceresi(tk.Toplevel):
    def __init__(self, parent, onay_callback):
        super().__init__(parent)
        self.parent = parent
        self.onay_callback = onay_callback

        self.title("Add Course")

        self.ders_adi_label = tk.Label(self, text="Course Name:")
        self.ders_adi_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.ders_adi_giris = tk.Entry(self)
        self.ders_adi_giris.grid(row=0, column=1, padx=10, pady=5)

        self.ders_gun_label = tk.Label(self, text="Course Day:")
        self.ders_gun_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.ders_gun_secim = ttk.Combobox(self, values=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        self.ders_gun_secim.grid(row=1, column=1, padx=10, pady=5)

        self.saat_baslangic_label = tk.Label(self, text="Time Start:")
        self.saat_baslangic_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.saat_baslangic_giris = Spinbox(self, from_=0, to=23, width=5)
        self.saat_baslangic_giris.grid(row=2, column=1, padx=5, pady=5)

        self.saat_bitis_label = tk.Label(self, text="Finish:")
        self.saat_bitis_label.grid(row=2, column=2, padx=5, pady=5, sticky="w")

        self.saat_bitis_giris = Spinbox(self, from_=0, to=23, width=5)
        self.saat_bitis_giris.grid(row=2, column=3, padx=5, pady=5)

        self.onay_button = tk.Button(self, text="Approve", command=self.onayla)
        self.onay_button.grid(row=3, columnspan=4, padx=10, pady=10)

    def saati_kontrol_et(self, baslangic, bitis):
        baslangic_saat = int(baslangic.split(":")[0])
        bitis_saat = int(bitis.split(":")[0])
        if baslangic_saat >= bitis_saat:
            messagebox.showerror("Error", "The lesson start time cannot be greater than or equal to the end time.")
            return False
        return True

    def onayla(self):
        ders_adi = self.ders_adi_giris.get()
        ders_gun = self.ders_gun_secim.get()
        saat_baslangic = self.saat_baslangic_giris.get()
        saat_bitis = self.saat_bitis_giris.get()
        if ders_adi and ders_gun and saat_baslangic and saat_bitis:
            if self.saati_kontrol_et(saat_baslangic, saat_bitis):
                saat_araligi = f"{saat_baslangic}:00 - {saat_bitis}:00"
                self.onay_callback(ders_adi, ders_gun, saat_araligi)
                self.destroy()
        else:
            messagebox.showerror("Error", "Please fill in all fields.")



class DersSaatleriSayfasi(tk.Toplevel):
    def __init__(self, parent, dersler):
        super().__init__(parent)
        self.parent = parent
        self.dersler = dersler
        self.title("Lesson Hours Page")

        self.dersler_frame = tk.Frame(self)
        self.dersler_frame.pack()

        self.dersler_listesi = tk.Listbox(self.dersler_frame, height=10, width=50)
        self.dersler_listesi.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.dersler_frame, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.dersler_listesi.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.dersler_listesi.config(yscrollcommand=self.scrollbar.set)

        self.ekle_button = tk.Button(self.dersler_frame, text="Add Course", command=self.ders_ekle)
        self.ekle_button.pack()

        self.sil_button = tk.Button(self.dersler_frame, text="Delete Selected Lesson", command=self.ders_sil)
        self.sil_button.pack()

        self.kapat_button = tk.Button(self, text="Close Page", command=self.sayfayi_kapat)
        self.kapat_button.pack()

        self.listele_dersler()

    def ders_ekle(self):
        def onay_callback(adi, gun, saat_araligi):
            yeni_ders = Ders(adi, gun, saat_araligi)
            self.dersler.append(yeni_ders)
            self.listele_dersler()
            messagebox.showinfo("Approval", "Course Added Successfully")

        ders_ekle_pencere = DersEklePenceresi(self, onay_callback)

    def ders_sil(self):
        secili = self.dersler_listesi.curselection()
        if secili:
            index = secili[0]
            del self.dersler[index]
            self.listele_dersler()
            messagebox.showinfo("Successful", "The course has been deleted successfully.")
        else:
            messagebox.showerror("Error", "Please select a course.")

    def listele_dersler(self):
        self.dersler_listesi.delete(0, tk.END)
        for ders in self.dersler:
            self.dersler_listesi.insert(tk.END, str(ders))

    def sayfayi_kapat(self):
        self.destroy()
        self.parent.deiconify()


class Uygulama:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Uygulama")
        self.root.geometry("600x400")

        self.images = [
            r"C:\Users\EXCALIBUR\OneDrive\Masaüstü\images2.png",
            r"C:\Users\EXCALIBUR\OneDrive\Masaüstü\images3.png",
            r"C:\Users\EXCALIBUR\OneDrive\Masaüstü\images4.png",
            r"C:\Users\EXCALIBUR\OneDrive\Masaüstü\images5.png",
            r"C:\Users\EXCALIBUR\OneDrive\Masaüstü\images6.png"
        ]
        
        self.current_image_index = 0
        self.bg_image = tk.PhotoImage(file=self.images[self.current_image_index])
        self.bg_label = tk.Label(self.root, image=self.bg_image)
        self.bg_label.place(relwidth=1, relheight=1)
        
        # Arka plan resminin hafızada tutulması için referans
        


        self.duyurular = []
        self.projeler = []
        self.dersler = []

        self.root.grid_rowconfigure(0, weight=0)
        self.root.grid_columnconfigure(0, weight=1)

        self.projeler_button = tk.Button(self.root, text="Projects Page", command=self.ac_projeler, font=("Helvetica", 12))
        self.ders_saatleri_button = tk.Button(self.root, text="Lesson hours", command=self.ac_ders_saatleri, font=("Helvetica", 12))
        self.duyurular_button = tk.Button(self.root, text="Announcements", command=self.ac_duyurular, font=("Helvetica", 12))
        self.change_bg_button = tk.Button(self.root, text="Change Background", command=self.change_background, font=("Helvetica", 12))
        self.chat_buton = tk.Button(self.root,text="Chat",command=self.chat, font=("Helvetica", 12))

        self.projeler_button.grid(row=3, column=0, padx=20, pady=10)
        self.ders_saatleri_button.grid(row=2, column=0,  padx=20, pady=10)
        self.duyurular_button.grid(row=1, column=0, padx=20, pady=10)
        self.change_bg_button.grid(row=4, column=0, padx=20, pady=10)
        self.chat_buton.grid(row=5, column=0, padx=20, pady=10)

        self.root.mainloop()

    def change_background(self):
        # Rastgele bir resim seç
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.bg_image = tk.PhotoImage(file=self.images[self.current_image_index])
        self.bg_label.config(image=self.bg_image)

    def ac_duyurular(self):
        self.root.withdraw()
        self.duyurular_sayfasi = DuyurularSayfasi(self.root, self.duyurular)
        self.duyurular_sayfasi.protocol("WM_DELETE_WINDOW", self.ana_sayfayi_goster)
        self.duyurular_sayfasi.mainloop()

    def ac_ders_saatleri(self):
        self.root.withdraw()
        self.ders_saatleri_sayfasi = DersSaatleriSayfasi(self.root, self.dersler)
        self.ders_saatleri_sayfasi.protocol("WM_DELETE_WINDOW", self.ana_sayfayi_goster)
        self.ders_saatleri_sayfasi.mainloop()

    def ac_projeler(self):
        self.root.withdraw()
        self.projeler_sayfasi = ProjelerSayfasi(self.root, self.projeler)
        self.projeler_sayfasi.protocol("WM_DELETE_WINDOW", self.ana_sayfayi_goster)
        self.projeler_sayfasi.mainloop()

    def chat(self):
        subprocess.Popen(["python", "istemci_kodu.py"])

    def ana_sayfayi_goster(self):
        self.root.deiconify()


class DuyurularSayfasi(tk.Toplevel):
    def __init__(self, parent, duyurular):
        super().__init__(parent)
        self.parent = parent
        self.duyurular = duyurular
        self.title("Duyurular Sayfası")

        self.duyurular_frame = tk.Frame(self)
        self.duyurular_frame.pack()

        self.duyuru_ekle_button = tk.Button(self.duyurular_frame, text="Add Announcement", command=self.duyuru_ekle, font=("Helvetica", 12))
        self.duyuru_ekle_button.pack()

        self.duyurular_listesi = tk.Listbox(self.duyurular_frame, height=10, width=50)
        self.duyurular_listesi.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = tk.Scrollbar(self.duyurular_frame, orient=tk.VERTICAL)
        self.scrollbar.config(command=self.duyurular_listesi.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.duyurular_listesi.config(yscrollcommand=self.scrollbar.set)

        self.sil_button = tk.Button(self.duyurular_frame, text="Delete Selected Announcement", command=self.duyuru_sil, font=("Helvetica", 12))
        self.sil_button.pack()

        self.kapat_button = tk.Button(self, text="Close Page", command=self.sayfayi_kapat, font=("Helvetica", 12))
        self.kapat_button.pack()

        self.listele_duyurular()

    def duyuru_ekle(self):
        def onay_callback(duyuru_metni):
            self.duyurular.append(duyuru_metni)
            self.listele_duyurular()
            messagebox.showinfo("Approval", "Announcement added successfully.")

        duyuru_ekle_pencere = DuyuruEklePenceresi(self, onay_callback)

    def duyuru_sil(self):
        secili = self.duyurular_listesi.curselection()
        if secili:
            index = secili[0]
            del self.duyurular[index]
            self.listele_duyurular()
            messagebox.showinfo("Successful", "The announcement has been successfully deleted.")
        else:
            messagebox.showerror("Mistake", "Please select an announcement.")

    def listele_duyurular(self):
        self.duyurular_listesi.delete(0, tk.END)
        for duyuru in self.duyurular:
            self.duyurular_listesi.insert(tk.END, duyuru)

    def sayfayi_kapat(self):
        self.destroy()
        self.parent.deiconify()


class DuyuruEklePenceresi(tk.Toplevel):
    def __init__(self, parent, onay_callback):
        super().__init__(parent)
        self.parent = parent
        self.onay_callback = onay_callback

        self.title("add announcement")

        self.duyuru_metni_label = tk.Label(self, text="Announcement Text:")
        self.duyuru_metni_label.pack()

        self.duyuru_metni_giris = tk.Entry(self)
        self.duyuru_metni_giris.pack()

        self.ekle_button = tk.Button(self, text="Add Announcement", command=self.ekle)
        self.ekle_button.pack()

    def ekle(self):
        duyuru_metni = self.duyuru_metni_giris.get()
        if duyuru_metni:
            self.onay_callback(duyuru_metni)
            self.destroy()
        else:
            messagebox.showerror("Error", "Please enter the announcement text.")

uygulama = Uygulama()