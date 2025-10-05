import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import sys
import os

# Database import
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Data.database import Database

class ExcelUploadWindow:
    def __init__(self, department_id=None):
        self.root = tk.Toplevel()
        self.root.title("Excel Yükleme - Ders ve Öğrenci Listeleri")
        self.root.geometry("700x500")
        self.root.configure(bg="#f0f0f0")
        self.department_id = department_id
        
        self.create_widgets()
        
    def create_widgets(self):
        # BAŞLIK
        title_label = tk.Label(
            self.root,
            text="Excel Dosyalarını Yükle",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # DERS LİSTESİ BÖLÜMÜ
        course_frame = tk.LabelFrame(
            self.root,
            text="Ders Listesi Yükleme",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        course_frame.pack(pady=10, padx=20, fill="x")
        
        course_desc = tk.Label(
            course_frame,
            text="Excel formatı: Ders Kodu, Ders Adı, Hoca, Tip (Zorunlu/Seçmeli)",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        course_desc.pack(pady=5)
        
        self.course_file_path = tk.StringVar()
        course_file_entry = tk.Entry(
            course_frame,
            textvariable=self.course_file_path,
            width=50,
            font=("Arial", 10),
            state="readonly"
        )
        course_file_entry.pack(side=tk.LEFT, padx=5)
        
        course_browse_btn = tk.Button(
            course_frame,
            text="Dosya Seç",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self.browse_course_file
        )
        course_browse_btn.pack(side=tk.LEFT, padx=5)
        
        course_upload_btn = tk.Button(
            course_frame,
            text="Dersleri Yükle",
            font=("Arial", 10, "bold"),
            bg="#2ecc71",
            fg="white",
            command=self.upload_courses
        )
        course_upload_btn.pack(side=tk.LEFT, padx=5)
        
        template_course_btn = tk.Button(
            course_frame,
            text="Şablon İndir",
            font=("Arial", 10),
            bg="#f39c12",
            fg="white",
            command=self.download_course_template
        )
        template_course_btn.pack(side=tk.LEFT, padx=5)
        
        # ÖĞRENCİ LİSTESİ BÖLÜMÜ
        student_frame = tk.LabelFrame(
            self.root,
            text="Öğrenci Listesi Yükleme",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        student_frame.pack(pady=10, padx=20, fill="x")
        
        student_desc = tk.Label(
            student_frame,
            text="Excel formatı: Öğrenci No, Ad-Soyad, Sınıf, Ders Kodu",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        student_desc.pack(pady=5)
        
        self.student_file_path = tk.StringVar()
        student_file_entry = tk.Entry(
            student_frame,
            textvariable=self.student_file_path,
            width=50,
            font=("Arial", 10),
            state="readonly"
        )
        student_file_entry.pack(side=tk.LEFT, padx=5)
        
        student_browse_btn = tk.Button(
            student_frame,
            text="Dosya Seç",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self.browse_student_file
        )
        student_browse_btn.pack(side=tk.LEFT, padx=5)
        
        student_upload_btn = tk.Button(
            student_frame,
            text="Öğrencileri Yükle",
            font=("Arial", 10, "bold"),
            bg="#2ecc71",
            fg="white",
            command=self.upload_students
        )
        student_upload_btn.pack(side=tk.LEFT, padx=5)
        
        template_student_btn = tk.Button(
            student_frame,
            text="Şablon İndir",
            font=("Arial", 10),
            bg="#f39c12",
            fg="white",
            command=self.download_student_template
        )
        template_student_btn.pack(side=tk.LEFT, padx=5)
        
        # PROGRESS BAR
        self.progress = ttk.Progressbar(
            self.root,
            orient=tk.HORIZONTAL,
            length=400,
            mode='determinate'
        )
        self.progress.pack(pady=20)
        
        # DURUM MESAJI
        self.status_label = tk.Label(
            self.root,
            text="Dosya seçin ve yükleyin...",
            font=("Arial", 10),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        self.status_label.pack(pady=10)
        
        # ÇIKIŞ BUTONU
        close_btn = tk.Button(
            self.root,
            text="Kapat",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            width=15,
            command=self.root.destroy
        )
        close_btn.pack(pady=10)
    
    def browse_course_file(self):
        file_path = filedialog.askopenfilename(
            title="Ders Listesi Excel Dosyasını Seçin",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.course_file_path.set(file_path)
            self.status_label.config(text="Ders dosyası seçildi: " + os.path.basename(file_path))
    
    def browse_student_file(self):
        file_path = filedialog.askopenfilename(
            title="Öğrenci Listesi Excel Dosyasını Seçin",
            filetypes=[("Excel files", "*.xlsx *.xls")]
        )
        if file_path:
            self.student_file_path.set(file_path)
            self.status_label.config(text="Öğrenci dosyası seçildi: " + os.path.basename(file_path))
    
    def download_course_template(self):
        try:
            # Ders listesi şablonu oluştur
            data = {
                'Ders Kodu': ['CSE101', 'CSE102', 'MATH101'],
                'Ders Adı': ['Programlama', 'Veri Yapıları', 'Matematik'],
                'Hoca': ['Dr. Ali Yılmaz', 'Dr. Ayşe Demir', 'Dr. Mehmet Kaya'],
                'Tip': ['Zorunlu', 'Zorunlu', 'Zorunlu']
            }
            
            df = pd.DataFrame(data)
            
            # Kullanıcının masaüstüne kaydet
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            template_path = os.path.join(desktop_path, "ders_listesi_sablonu.xlsx")
            df.to_excel(template_path, index=False)
            
            messagebox.showinfo("Başarılı", f"Ders listesi şablonu masaüstünüze kaydedildi!\n\nYol: {template_path}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Şablon oluşturulamadı: {str(e)}")
    
    def download_student_template(self):
        try:
            # Öğrenci listesi şablonu oluştur
            data = {
                'Öğrenci No': ['260201001', '260201002', '260201003'],
                'Ad-Soyad': ['Ahmet Yılmaz', 'Ayşe Demir', 'Mehmet Kaya'],
                'Sınıf': ['1. Sınıf', '1. Sınıf', '1. Sınıf'],
                'Ders Kodu': ['CSE101', 'CSE101', 'CSE101']
            }
            
            df = pd.DataFrame(data)
            
            # Kullanıcının masaüstüne kaydet
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            template_path = os.path.join(desktop_path, "ogrenci_listesi_sablonu.xlsx")
            df.to_excel(template_path, index=False)
            
            messagebox.showinfo("Başarılı", f"Öğrenci listesi şablonu masaüstünüze kaydedildi!\n\nYol: {template_path}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Şablon oluşturulamadı: {str(e)}")
    
    def upload_courses(self):
        if not self.course_file_path.get():
            messagebox.showerror("Hata", "Lütfen önce bir dosya seçin!")
            return
        
        try:
            self.progress['value'] = 0
            self.status_label.config(text="Excel dosyası okunuyor...")
            self.root.update_idletasks()
            
            # Excel'i oku
            df = pd.read_excel(self.course_file_path.get())
            self.progress['value'] = 30
            self.status_label.config(text="Veritabanına kaydediliyor...")
            
            # Gerekli sütunları kontrol et
            required_columns = ['Ders Kodu', 'Ders Adı', 'Hoca', 'Tip']
            for col in required_columns:
                if col not in df.columns:
                    messagebox.showerror("Hata", f"Eksik sütun: {col}\n\nLütfen şablonu kullanın!")
                    return
            
            # Database'e kaydet
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            success_count = 0
            error_rows = []
            
            for index, row in df.iterrows():
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO courses 
                        (code, name, instructor, type, department_id)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        str(row['Ders Kodu']), 
                        str(row['Ders Adı']), 
                        str(row['Hoca']), 
                        str(row['Tip']), 
                        self.department_id
                    ))
                    success_count += 1
                    
                except Exception as e:
                    error_rows.append(index + 2)  # +2 because Excel rows start from 1 + header
                    print(f"Satır {index+2} hatası: {e}")
            
            conn.commit()
            conn.close()
            self.progress['value'] = 100
            
            if error_rows:
                messagebox.showwarning("Kısmen Başarılı", 
                                      f"Yükleme tamamlandı!\nBaşarılı: {success_count}\nHatalı satırlar: {error_rows}")
            else:
                messagebox.showinfo("Başarılı", 
                                   f"Tüm dersler başarıyla yüklendi!\nToplam: {success_count} kayıt")
            
            self.status_label.config(text=f"Ders yükleme tamamlandı - {success_count} kayıt eklendi")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okuma hatası: {str(e)}")
            self.status_label.config(text="Hata oluştu!")
    
    def upload_students(self):
        if not self.student_file_path.get():
            messagebox.showerror("Hata", "Lütfen önce bir dosya seçin!")
            return
        
        try:
            self.progress['value'] = 0
            self.status_label.config(text="Excel dosyası okunuyor...")
            self.root.update_idletasks()
            
            # Excel'i oku
            df = pd.read_excel(self.student_file_path.get())
            self.progress['value'] = 30
            self.status_label.config(text="Veritabanına kaydediliyor...")
            
            # Gerekli sütunları kontrol et
            required_columns = ['Öğrenci No', 'Ad-Soyad', 'Sınıf', 'Ders Kodu']
            for col in required_columns:
                if col not in df.columns:
                    messagebox.showerror("Hata", f"Eksik sütun: {col}\n\nLütfen şablonu kullanın!")
                    return
            
            # Database'e kaydet
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            success_count = 0
            error_rows = []
            
            for index, row in df.iterrows():
                try:
                    # Öğrenciyi ekle
                    cursor.execute('''
                        INSERT OR REPLACE INTO students 
                        (student_number, name, class, department_id)
                        VALUES (?, ?, ?, ?)
                    ''', (
                        str(row['Öğrenci No']), 
                        str(row['Ad-Soyad']), 
                        str(row['Sınıf']), 
                        self.department_id
                    ))
                    
                    success_count += 1
                    
                except Exception as e:
                    error_rows.append(index + 2)
                    print(f"Satır {index+2} hatası: {e}")
            
            conn.commit()
            conn.close()
            self.progress['value'] = 100
            
            if error_rows:
                messagebox.showwarning("Kısmen Başarılı", 
                                      f"Yükleme tamamlandı!\nBaşarılı: {success_count}\nHatalı satırlar: {error_rows}")
            else:
                messagebox.showinfo("Başarılı", 
                                   f"Tüm öğrenciler başarıyla yüklendi!\nToplam: {success_count} kayıt")
            
            self.status_label.config(text=f"Öğrenci yükleme tamamlandı - {success_count} kayıt eklendi")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okuma hatası: {str(e)}")
            self.status_label.config(text="Hata oluştu!")

if __name__ == "__main__":
    app = ExcelUploadWindow()
    app.root.mainloop()