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
    
    def show(self):
        self.root.mainloop()
        
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
            # Ders listesi şablonu oluştur - SENİN FORMATINDA
            data = {
                'DERS KODU': ['CSE101', 'CSE102', 'MATH101'],
                'DERSİN ADI': ['Programlama', 'Veri Yapıları', 'Matematik'],
                'DERSİ VEREN ÖĞR. ELEMANI': ['Dr. Ali Yılmaz', 'Dr. Ayşe Demir', 'Dr. Mehmet Kaya'],
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
                'Ad Soyad': ['Ahmet Yılmaz', 'Ayşe Demir', 'Mehmet Kaya'],
                'Sınıf': ['1. Sınıf', '1. Sınıf', '1. Sınıf'],
                'Ders ': ['CSE101', 'CSE101', 'CSE101']
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
            
            # Excel'i oku - header olmadan okuyalım
            df = pd.read_excel(self.course_file_path.get(), header=None)
            
            # DEBUG: Tüm veriyi göster
            print("📋 Excel verisi:")
            print(df.head(10))
            
            self.progress['value'] = 30
            self.status_label.config(text="Veriler analiz ediliyor...")
            
            # Database'e kaydet
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            success_count = 0
            error_rows = []
            
            current_type = "Zorunlu"  # Varsayılan tip
            
            # Excel formatını parse et
            for index, row in df.iterrows():
                try:
                    row_num = index + 1
                    
                    # DEBUG: Her satırı göster
                    print(f"📝 Satır {row_num}: {list(row)}")
                    
                    # Boş satırları atla
                    if row.isnull().all():
                        continue
                    
                    # Sınıf başlıklarını kontrol et (1. Sınıf, 2. Sınıf vb.)
                    first_cell = str(row[0]).strip() if pd.notna(row[0]) else ""
                    
                    if "sınıf" in first_cell.lower():
                        print(f"🎯 Sınıf değişti: {first_cell}")
                        continue
                    
                    # Seçmeli ders bölümünü kontrol et
                    if "seçmeli" in first_cell.lower() or "seçimlik" in first_cell.lower():
                        current_type = "Seçmeli"
                        print(f"🎯 Ders tipi değişti: {current_type}")
                        continue
                    
                    # Başlık satırlarını atla ("DERS KODU", "DERSİN ADI" vb.)
                    if any(keyword in first_cell.upper() for keyword in ['DERS KODU', 'DERSİN ADI', 'DERSİ VEREN']):
                        print(f"📑 Başlık satırı atlandı: {first_cell}")
                        continue
                    
                    # Veri satırlarını işle (3 sütunlu satırlar)
                    if len(row) >= 3 and pd.notna(row[0]) and pd.notna(row[1]):
                        ders_kodu = str(row[0]).strip()
                        ders_adi = str(row[1]).strip()
                        ogretmen = str(row[2]).strip() if pd.notna(row[2]) else "Belirtilmemiş"
                        
                        # Ders kodunun geçerli olduğundan emin ol (en az 3 karakter)
                        if len(ders_kodu) >= 3:
                            cursor.execute('''
                                INSERT OR REPLACE INTO courses 
                                (code, name, instructor, type, department_id)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (ders_kodu, ders_adi, ogretmen, current_type, self.department_id))
                            
                            success_count += 1
                            print(f"✅ Satır {row_num} eklendi: {ders_kodu} - {ders_adi} ({current_type})")
                        else:
                            print(f"❌ Satır {row_num} atlandı - geçersiz ders kodu: {ders_kodu}")
                    else:
                        print(f"❌ Satır {row_num} atlandı - eksik bilgi")
                        
                except Exception as e:
                    error_rows.append(row_num)
                    print(f"❌ Satır {row_num} hatası: {e}")
            
            conn.commit()
            conn.close()
            self.progress['value'] = 100
            
            if success_count == 0:
                messagebox.showwarning("Uyarı", 
                                    f"Hiç ders bulunamadı!\n\n"
                                    f"Lütfen Excel formatını kontrol edin.")
            elif error_rows:
                messagebox.showwarning("Kısmen Başarılı", 
                                    f"Yükleme tamamlandı!\nBaşarılı: {success_count}\nHatalı satırlar: {error_rows}")
            else:
                messagebox.showinfo("Başarılı", 
                                f"Tüm dersler başarıyla yüklendi!\nToplam: {success_count} kayıt\n\n"
                                f"Zorunlu/Seçmeli dersler otomatik ayarlandı!")
            
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
            
            print("📋 Öğrenci Excel sütunları:", list(df.columns))
            
            self.progress['value'] = 30
            self.status_label.config(text="Öğrenciler kaydediliyor...")
            
            # Database'e kaydet
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            success_count = 0
            error_rows = []
            total_courses_added = 0
            
            for index, row in df.iterrows():
                try:
                    row_num = index + 2  # Excel satır numarası (başlık + 1)
                    
                    # Temel öğrenci bilgilerini al
                    student_no = str(row['Öğrenci No']).strip()
                    name = str(row['Ad Soyad']).strip()
                    class_name = str(row['Sınıf']).strip()
                    
                    print(f"👤 Öğrenci {student_no} işleniyor...")
                    
                    # Öğrenciyi ekle veya güncelle
                    cursor.execute('''
                        INSERT OR REPLACE INTO students 
                        (student_number, name, class, department_id)
                        VALUES (?, ?, ?, ?)
                    ''', (student_no, name, class_name, self.department_id))
                    
                    # Öğrenci ID'sini al
                    cursor.execute('SELECT id FROM students WHERE student_number = ?', (student_no,))
                    student_id = cursor.fetchone()[0]
                    
                    # Ders sütunlarını bul (Ders1, Ders2, Ders3...)
                    course_columns = [col for col in df.columns if 'Ders' in col]
                    courses_added = 0
                    
                    print(f"  📚 Ders sütunları: {course_columns}")
                    
                    for col in course_columns:
                        if pd.notna(row[col]):
                            course_code = str(row[col]).strip()
                            
                            if course_code:  # Boş değilse
                                # Ders ID'sini bul
                                cursor.execute('SELECT id FROM courses WHERE code = ? AND department_id = ?', 
                                            (course_code, self.department_id))
                                course_result = cursor.fetchone()
                                
                                if course_result:
                                    course_id = course_result[0]
                                    
                                    # Öğrenci-ders ilişkisini ekle (çakışma olmazsa)
                                    cursor.execute('''
                                        INSERT OR IGNORE INTO student_courses 
                                        (student_id, course_id)
                                        VALUES (?, ?)
                                    ''', (student_id, course_id))
                                    
                                    if cursor.rowcount > 0:
                                        courses_added += 1
                                        total_courses_added += 1
                                        print(f"    ✅ Ders eklendi: {course_code}")
                                    else:
                                        print(f"    ⚠️ Ders zaten ekli: {course_code}")
                                else:
                                    print(f"    ❌ Ders bulunamadı: {course_code}")
                    
                    success_count += 1
                    print(f"✅ Öğrenci {student_no} tamamlandı - {courses_added} ders eklendi")
                    
                except Exception as e:
                    error_rows.append(row_num)
                    print(f"❌ Satır {row_num} hatası: {e}")
            
            conn.commit()
            conn.close()
            self.progress['value'] = 100
            
            messagebox.showinfo("Başarılı", 
                            f"✅ Öğrenciler yüklendi!\n"
                            f"👥 Toplam öğrenci: {success_count}\n"
                            f"📚 Toplam ders ilişkisi: {total_courses_added}\n"
                            f"❌ Hatalı satırlar: {len(error_rows)}")
            
            self.status_label.config(text=f"Öğrenci yükleme tamamlandı - {success_count} öğrenci")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okuma hatası: {str(e)}")
            self.status_label.config(text="Hata oluştu!")

if __name__ == "__main__":
    app = ExcelUploadWindow()
    app.show()