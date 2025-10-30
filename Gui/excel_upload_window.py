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
        # Department ID'yi al, eğer yoksa varsayılan 1 (Admin) olsun
        self.department_id = department_id if department_id else 1
        print(f"ExcelUploadWindow açıldı - Department ID: {self.department_id}")
        
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
            # Açıklama güncellendi
            text="PDF'teki formata benzer ('1. Sınıf', 'SEÇMELİ DERS' vb. ara başlıkları olan) dosyayı yükleyin.",
            font=("Arial", 9), # Font küçültüldü
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
            text="Basit Şablon İndir", # İsim değişti
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
        
        # --- GÜNCELLENDİ: Öğrenci şablonu açıklaması (Uzun Format) ---
        student_desc = tk.Label(
            student_frame,
            text="Excel formatı: 'Öğrenci No', 'Ad Soyad', 'Sınıf', 'Ders'",
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
            # Bu şablon basit, başlıklı format. PDF'teki ara-başlıklı değil.
            data = {
                'DERS KODU': ['CSE101', 'CSE102', 'MATH101'],
                'DERSİN ADI': ['Programlama', 'Veri Yapıları', 'Matematik'],
                'DERSİ VEREN ÖĞR. ELEMANI': ['Dr. Ali Yılmaz', 'Dr. Ayşe Demir', 'Dr. Mehmet Kaya'],
                'Tip': ['Zorunlu', 'Zorunlu', 'Zorunlu'] 
            }
            df = pd.DataFrame(data)
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            template_path = os.path.join(desktop_path, "ders_listesi_BASIT_sablon.xlsx")
            df.to_excel(template_path, index=False)
            messagebox.showinfo("Başarılı", f"Basit ders listesi şablonu masaüstünüze kaydedildi!\n\nYol: {template_path}")
        except Exception as e:
            messagebox.showerror("Hata", f"Şablon oluşturulamadı: {str(e)}")
        
    # --- GÜNCELLENDİ: Öğrenci şablonu (Uzun Format) ---
    def download_student_template(self):
        try:
            # Uzun formata göre güncellendi
            data = {
                'Öğrenci No': ['260201001', '260201001', '260201002'],
                'Ad Soyad': ['Ahmet Yılmaz', 'Ahmet Yılmaz', 'Ayşe Demir'],
                'Sınıf': ['1. Sınıf', '1. Sınıf', '1. Sınıf'],
                'Ders': ['BLM101', 'FEF115', 'BLM101'] # Her satır 1 ders
            }
            
            df = pd.DataFrame(data)
            
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            template_path = os.path.join(desktop_path, "ogrenci_listesi_sablonu.xlsx")
            df.to_excel(template_path, index=False)
            
            messagebox.showinfo("Başarılı", f"Öğrenci listesi şablonu masaüstünüze kaydedildi!\n\nYol: {template_path}")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Şablon oluşturulamadı: {str(e)}")
    
    # --- upload_courses (ARA BAŞLIKLI FORMATI OKUR - DOKUNMA) ---
    def upload_courses(self):
        file_path = self.course_file_path.get()
        if not file_path:
            messagebox.showerror("Hata", "Lütfen önce bir ders dosyası seçin!")
            return
        
        try:
            self.progress['value'] = 0
            self.status_label.config(text="Excel dosyası okunuyor...")
            self.root.update_idletasks()
            
            # Başlıksız (header=None) oku
            df = pd.read_excel(file_path, header=None)
            
            print("📋 Excel (başlıksız) ders verisi okundu:")
            print(df.head(10))

            self.progress['value'] = 30
            self.status_label.config(text="Dersler veritabanına kaydediliyor (format analiz ediliyor)...")
            
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            success_count = 0
            error_rows = []
            
            current_type = "Zorunlu"
            
            total_rows = len(df)
            for index, row in df.iterrows():
                try:
                    row_num = index + 1 
                    
                    if row.isnull().all():
                        continue

                    first_cell = str(row[0]).strip().lower()

                    if "seçmeli" in first_cell or "seçimlik" in first_cell:
                        current_type = "Seçmeli"
                        print(f"   -> Satır {row_num}: Ders tipi 'Seçmeli' olarak değişti.")
                        continue 

                    if "ders kodu" in first_cell or "sınıf" in first_cell:
                        print(f"   -> Satır {row_num}: Başlık satırı atlandı.")
                        continue 
                    
                    if pd.notna(row[0]) and pd.notna(row[1]) and pd.notna(row[2]):
                        ders_kodu = str(row[0]).strip()
                        ders_adi = str(row[1]).strip()
                        ogretmen = str(row[2]).strip()
                        ders_tipi = current_type 

                        if len(ders_kodu) < 3 or ' ' in ders_kodu:
                            print(f"❌ Satır {row_num} atlandı - Geçersiz ders kodu: '{ders_kodu}'")
                            error_rows.append(row_num)
                            continue
                            
                        cursor.execute('''
                            INSERT OR REPLACE INTO courses 
                            (code, name, instructor, type, department_id)
                            VALUES (?, ?, ?, ?, ?)
                        ''', (ders_kodu, ders_adi, ogretmen, ders_tipi, self.department_id))
                        
                        print(f"   ✅ Satır {row_num} eklendi: {ders_kodu} ({ders_tipi})")
                        success_count += 1
                    
                    else:
                         print(f"   -> Satır {row_num} atlandı (Eksik bilgi veya format dışı).")

                except Exception as e:
                    print(f"❌ Satır {row_num} işlenirken ciddi hata: {e}")
                    error_rows.append(row_num)
                
                if total_rows > 0:
                    self.progress['value'] = 30 + int(70 * (index + 1) / total_rows)
                    self.root.update_idletasks()

            
            conn.commit()
            conn.close()
            self.progress['value'] = 100
            
            if success_count == 0:
                messagebox.showwarning("Başarısız", 
                                    f"Hiç ders yüklenemedi!\n"
                                    f"Dosya formatı beklenenden farklı olabilir.")
            elif error_rows:
                messagebox.showwarning("Kısmen Başarılı", 
                                    f"Yükleme tamamlandı!\n"
                                    f"Başarılı: {success_count} ders\n"
                                    f"Hatalı satırlar: {len(error_rows)} ({', '.join(map(str, error_rows[:5]))}{'...' if len(error_rows) > 5 else ''})")
            else:
                messagebox.showinfo("Başarılı", 
                                f"Tüm dersler (Zorunlu/Seçmeli) başarıyla yüklendi!\nToplam: {success_count} kayıt.")
            
            self.status_label.config(text=f"Ders yükleme tamamlandı - {success_count} kayıt eklendi")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okuma/işleme hatası: {str(e)}")
            self.status_label.config(text="Hata oluştu!")
            self.progress['value'] = 0

    # --- BU FONKSİYON TAMAMEN DEĞİŞTİ (YENİ UZUN FORMATA GÖRE) ---
    def upload_students(self):
        file_path = self.student_file_path.get()
        if not file_path:
            messagebox.showerror("Hata", "Lütfen önce bir öğrenci dosyası seçin!")
            return
        
        # Kontrol: Dersler yüklendi mi?
        db_check = Database()
        conn_check = db_check.get_connection()
        cursor_check = conn_check.cursor()
        cursor_check.execute("SELECT COUNT(*) FROM courses WHERE department_id = ?", (self.department_id,))
        course_count = cursor_check.fetchone()[0]
        conn_check.close()
        
        if course_count == 0:
            messagebox.showerror("Hata", "Öğrenci yüklemeden önce dersleri yüklemelisiniz!\n'courses' tablosu boş.")
            return

        try:
            self.progress['value'] = 0
            self.status_label.config(text="Öğrenci Excel dosyası okunuyor...")
            self.root.update_idletasks()
            
            # Excel'i oku (ilk satır başlık)
            df = pd.read_excel(file_path)
            
            print("📋 Öğrenci Excel sütunları:", list(df.columns))
            
            # Gerekli temel sütunları kontrol et (YENİ FORMATA GÖRE)
            required_cols = ['Öğrenci No', 'Ad Soyad', 'Sınıf', 'Ders']
            if not all(col in df.columns for col in required_cols):
                messagebox.showerror("Hata", 
                                    f"Excel formatı yanlış!\n\nBeklenen sütunlar: {required_cols}\n\nBulunan sütunlar: {list(df.columns)}")
                self.status_label.config(text="Hata: Sütun isimleri yanlış.")
                self.progress['value'] = 0
                return

            self.progress['value'] = 30
            self.status_label.config(text="Öğrenciler ve ders atamaları kaydediliyor...")
            
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Hızlı işleme için ders kodlarını önbelleğe al (HashMap)
            cursor.execute('SELECT code, id FROM courses WHERE department_id = ?', (self.department_id,))
            course_code_to_id_map = {code: course_id for code, course_id in cursor.fetchall()}
            print(f"   -> {len(course_code_to_id_map)} ders kodu önbelleğe alındı.")
            
            # Hızlı işleme için öğrencileri önbelleğe al (HashMap)
            cursor.execute('SELECT student_number, id FROM students WHERE department_id = ?', (self.department_id,))
            student_no_to_id_map = {student_no: student_id for student_no, student_id in cursor.fetchall()}
            print(f"   -> {len(student_no_to_id_map)} mevcut öğrenci önbelleğe alındı.")
            
            success_student_inserts = 0 # Yeni eklenen öğrenci sayısı
            success_course_links = 0 # Yeni eklenen ders-öğrenci bağlantısı
            error_rows = []
            unknown_courses = set() # Bilinmeyen ders kodlarını bir kez göstermek için

            total_rows = len(df)
            for index, row in df.iterrows():
                try:
                    row_num = index + 2 
                    
                    student_no = str(row['Öğrenci No']).strip()
                    name = str(row['Ad Soyad']).strip()
                    class_name = str(row['Sınıf']).strip()
                    course_code = str(row['Ders']).strip() # Sütun adı 'Ders'

                    if not student_no or not name or not course_code:
                        print(f"❌ Satır {row_num} atlandı - Öğrenci No, Ad veya Ders Kodu boş.")
                        error_rows.append(row_num)
                        continue

                    # 1. Öğrenciyi Ekle/Al
                    student_id = student_no_to_id_map.get(student_no)
                    if not student_id:
                        # Öğrenci yok, ekle
                        cursor.execute('''
                            INSERT OR IGNORE INTO students 
                            (student_number, name, class, department_id)
                            VALUES (?, ?, ?, ?)
                        ''', (student_no, name, class_name, self.department_id))
                        # Yeni ID'yi al
                        cursor.execute('SELECT id FROM students WHERE student_number = ?', (student_no,))
                        student_id_result = cursor.fetchone()
                        if not student_id_result:
                            print(f"❌ Satır {row_num} - Öğrenci oluşturulamadı: {student_no}")
                            error_rows.append(row_num)
                            continue
                        student_id = student_id_result[0]
                        student_no_to_id_map[student_no] = student_id # Önbelleğe ekle
                        success_student_inserts += 1

                    # 2. Ders ID'sini Bul
                    course_id = course_code_to_id_map.get(course_code)
                    
                    if course_id:
                        # 3. Öğrenci-Ders İlişkisini Ekle
                        cursor.execute('''
                            INSERT OR IGNORE INTO student_courses 
                            (student_id, course_id)
                            VALUES (?, ?)
                        ''', (student_id, course_id))
                        
                        if cursor.rowcount > 0:
                            success_course_links += 1
                    else:
                        # Ders bulunamadı
                        if course_code not in unknown_courses:
                            print(f"   -> Uyarı: Satır {row_num} - Ders kodu '{course_code}' 'courses' tablosunda (Dept ID: {self.department_id}) bulunamadı.")
                            unknown_courses.add(course_code)
                        error_rows.append(row_num)
                    
                except Exception as e:
                    print(f"❌ Satır {row_num} işlenirken hata: {e}")
                    error_rows.append(row_num)
                
                self.progress['value'] = 30 + int(70 * (index + 1) / total_rows)
                self.root.update_idletasks()
            
            conn.commit()
            conn.close()
            self.progress['value'] = 100
            
            messagebox.showinfo("Başarılı", 
                            f"✅ Öğrenci yükleme tamamlandı!\n"
                            f"👥 Yeni eklenen öğrenci: {success_student_inserts}\n"
                            f"📚 Toplam {success_course_links} yeni ders ataması yapıldı.\n"
                            f"❌ Hatalı/Atlanmış satır sayısı: {len(error_rows)}\n"
                            f"❓ Bulunamayan Dersler: {len(unknown_courses)}")
            
            self.status_label.config(text=f"Öğrenci yükleme tamamlandı - {success_course_links} atama yapıldı.")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dosya okuma/işleme hatası: {str(e)}")
            self.status_label.config(text="Hata oluştu!")
            self.progress['value'] = 0

if __name__ == "__main__":
    # Test için
    root = tk.Tk()
    root.withdraw() # Ana test penceresini gizle
    app = ExcelUploadWindow(department_id=1)
    app.show()
    root.mainloop()

