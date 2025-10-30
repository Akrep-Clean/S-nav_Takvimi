import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import seating_plan_window # Bu importun da sys.path'den sonra olması iyi olur

# --- BU KOD BLOĞU KESİNLİKLE OLMALI ---
# Database ve Services importları için ana dizini ekle
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
# --- BİTİŞ ---

from Services.exam_scheduler import ExamScheduler
from Data.database import Database


class ExamScheduleWindow:
    def __init__(self, department_id=1):
        self.root = tk.Toplevel()
        self.root.title("Sınav Programı Oluştur")
        # Kısıtlar için pencereyi biraz büyütelim
        self.root.geometry("1100x750") 
        self.root.configure(bg="#f0f0f0")
        self.department_id = department_id
        self.scheduler = ExamScheduler(department_id)
        self.schedule_data = None
        self.db = Database()

        self.create_widgets()

    def show(self):
        self.root.mainloop()

    def create_widgets(self):
        # BAŞLIK
        title_label = tk.Label(
            self.root,
            text="Sınav Programı Oluştur",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=10)

        # AYARLAR FRAME (Kısıtlar için güncellendi)
        settings_frame = tk.LabelFrame(
            self.root,
            text="Sınav Ayarları ve Kısıtlar (PDF)",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        settings_frame.pack(pady=5, padx=20, fill="x")

        # Ayarları 2 sütunlu yapmak için ana frame'ler
        left_settings_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        left_settings_frame.pack(side="left", fill="x", expand=True, padx=5)
        right_settings_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        right_settings_frame.pack(side="right", fill="x", expand=True, padx=5)

        # --- SOL TARAF (Tarih ve Tip) ---
        # Tarih aralığı
        date_frame = tk.Frame(left_settings_frame, bg="#f0f0f0")
        date_frame.pack(fill="x", pady=2)
        tk.Label(date_frame, text="Başlangıç Tarihi:", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5)
        self.start_date_entry = tk.Entry(date_frame, font=("Arial", 10), width=12)
        self.start_date_entry.pack(side="left", padx=5)
        self.start_date_entry.insert(0, "2025-10-27") # PDF tarihine uygun örnek

        date_frame_end = tk.Frame(left_settings_frame, bg="#f0f0f0")
        date_frame_end.pack(fill="x", pady=2)
        tk.Label(date_frame_end, text="Bitiş Tarihi:    ", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5) # Hizalama için boşluk
        self.end_date_entry = tk.Entry(date_frame_end, font=("Arial", 10), width=12)
        self.end_date_entry.pack(side="left", padx=5)
        self.end_date_entry.insert(0, "2025-11-07") # PDF tarihine uygun örnek

        # Sınav tipi
        type_frame = tk.Frame(left_settings_frame, bg="#f0f0f0")
        type_frame.pack(fill="x", pady=2)
        tk.Label(type_frame, text="Sınav Tipi:     ", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5) # Hizalama için boşluk
        self.exam_type_combo = ttk.Combobox(type_frame, values=["Vize", "Final", "Bütünleme"], width=15, state="readonly")
        self.exam_type_combo.pack(side="left", padx=5)
        self.exam_type_combo.set("Vize")

        # --- SAĞ TARAF (PDF Kısıtları - YENİ EKLENDİ) ---
        # Varsayılan Sınav Süresi
        duration_frame = tk.Frame(right_settings_frame, bg="#f0f0f0")
        duration_frame.pack(fill="x", pady=2)
        tk.Label(duration_frame, text="Varsayılan Süre (dk):", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5)
        self.duration_entry = tk.Entry(duration_frame, font=("Arial", 10), width=10)
        self.duration_entry.pack(side="left", padx=5)
        self.duration_entry.insert(0, "75") # PDF'teki varsayılan

        # Sınav Arası Bekleme Süresi
        break_frame = tk.Frame(right_settings_frame, bg="#f0f0f0")
        break_frame.pack(fill="x", pady=2)
        tk.Label(break_frame, text="Bekleme Süresi (dk): ", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5)
        self.break_entry = tk.Entry(break_frame, font=("Arial", 10), width=10)
        self.break_entry.pack(side="left", padx=5)
        self.break_entry.insert(0, "15") # PDF'teki varsayılan

        # Hariç Günler
        excluded_frame = tk.Frame(right_settings_frame, bg="#f0f0f0")
        excluded_frame.pack(fill="x", pady=2)
        tk.Label(excluded_frame, text="Hariç Günler:          ", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5) # Hizalama
        self.sat_check_var = tk.BooleanVar(value=True) # Cumartesi varsayılan hariç
        self.sun_check_var = tk.BooleanVar(value=True) # Pazar varsayılan hariç
        tk.Checkbutton(excluded_frame, text="Cmt", variable=self.sat_check_var, bg="#f0f0f0").pack(side="left")
        tk.Checkbutton(excluded_frame, text="Pzr", variable=self.sun_check_var, bg="#f0f0f0").pack(side="left")
        
        # OLUŞTUR BUTONU
        generate_btn = tk.Button(
            self.root, # Ayarlar frame'inin dışına aldık
            text="Sınav Programını Oluştur",
            font=("Arial", 12, "bold"), 
            bg="#3498db",
            fg="white",
            width=30, # Genişlik artırıldı
            command=self.generate_schedule
        )
        generate_btn.pack(pady=10) # Padding ayarlandı

        # SONUÇLAR FRAME
        results_frame = tk.LabelFrame(
            self.root,
            text="Oluşturulan Sınav Programı",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        results_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Treeview (YENİ: "Süre" kolonu eklendi)
        self.tree = ttk.Treeview(
            results_frame,
            columns=("Tarih", "Saat", "Süre", "Ders Kodu", "Ders Adı", "Hoca", "Öğrenci Sayısı", "Derslik", "Kapasite"),
            show="headings",
            height=15 # Yükseklik ayarlandı
        )
        self.tree.bind("<Double-1>", self.show_seating_plan)

        # Kolon başlıkları
        self.tree.heading("Tarih", text="Tarih")
        self.tree.heading("Saat", text="Saat")
        self.tree.heading("Süre", text="Süre (dk)") # YENİ
        self.tree.heading("Ders Kodu", text="Ders Kodu")
        self.tree.heading("Ders Adı", text="Ders Adı")
        self.tree.heading("Hoca", text="Öğretim Elemanı")
        self.tree.heading("Öğrenci Sayısı", text="Öğr. Sayısı")
        self.tree.heading("Derslik", text="Derslik")
        self.tree.heading("Kapasite", text="Kapasite")

        # Kolon genişlikleri
        self.tree.column("Tarih", width=80, anchor='center')
        self.tree.column("Saat", width=60, anchor='center')
        self.tree.column("Süre", width=70, anchor='center') # YENİ
        self.tree.column("Ders Kodu", width=80, anchor='center')
        self.tree.column("Ders Adı", width=160) # Daraltıldı
        self.tree.column("Hoca", width=140)
        self.tree.column("Öğrenci Sayısı", width=80, anchor='center')
        self.tree.column("Derslik", width=80, anchor='center')
        self.tree.column("Kapasite", width=70, anchor='center')

        # Scrollbar (Aynı)
        scrollbar_y = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(results_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        self.tree.pack(side="top", fill="both", expand=True)
        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")

        # Excel'e Aktar Butonu (Aynı)
        export_btn = tk.Button(
            self.root, 
            text="Excel'e Aktar",
            font=("Arial", 10, "bold"),
            bg="#27ae60", 
            fg="white",
            width=15,
            command=self.export_schedule_to_excel
        )
        export_btn.pack(pady=10)

    # --- Hoca Map Fonksiyonu (Aynı) ---
    def get_instructor_map(self):
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT code, instructor FROM courses WHERE department_id = ?", (self.department_id,))
        instructors = cursor.fetchall()
        conn.close()
        return {code: instructor for code, instructor in instructors}

    # --- Oturma Planı Göster (Aynı, YENİ: Süre bilgisini de alalım) ---
    def show_seating_plan(self, event):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        item = selected_items[0]
        values = self.tree.item(item, "values")

        try:
            exam_details = {
                'date': values[0],
                'time': values[1],
                'duration': values[2], # Süreyi de gönderelim (opsiyonel)
                'course_code': values[3],
                'course_name': values[4],
                'instructor': values[5],
                'student_count': values[6],
                'classroom_code': values[7],
                'capacity': values[8]
            }
            student_count = int(exam_details['student_count'])
            if student_count <= 0:
                 messagebox.showinfo("Bilgi", "Bu sınava kayıtlı öğrenci bulunmamaktadır. Oturma planı oluşturulamaz.")
                 return
        except (ValueError, IndexError):
             messagebox.showerror("Hata", "Seçilen sınav bilgileri geçersiz.")
             return

        seating_plan_app = seating_plan_window.SeatingPlanWindow(self.root, exam_details, self.department_id)

    # --- GÜNCELLENDİ: generate_schedule (Yeni kısıtları okur ve yeni scheduler'ı çağırır) ---
    def generate_schedule(self):
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        exam_type = self.exam_type_combo.get()

        # Yeni kısıtları oku
        try:
            default_duration_val = int(self.duration_entry.get().strip())
            break_time_val = int(self.break_entry.get().strip())
        except ValueError:
            messagebox.showerror("Hata", "Süre ve Mola alanları sayısal değer olmalıdır!")
            return

        excluded_days_val = []
        if self.sat_check_var.get():
            excluded_days_val.append("Saturday")
        if self.sun_check_var.get():
            excluded_days_val.append("Sunday")

        # Tarih format kontrolü
        if not start_date or not end_date:
            messagebox.showerror("Hata", "Lütfen tarih aralığını girin!")
            return
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Hata", "Tarih formatı yanlış! YYYY-MM-DD formatında girin.")
            return

        # Treeview'ı temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.schedule_data = None

        progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode='indeterminate')
        progress.pack(pady=5)
        progress.start()
        self.root.update_idletasks() # Progress bar'ı göstermek için
        print(f"Scheduler çağrılıyor: {start_date}, {end_date}, {exam_type}, {default_duration_val}, {break_time_val}, {excluded_days_val}")

        try:
            # Hoca bilgilerini önceden çek (scheduler'dan gelmiyorsa diye)
            instructor_map = self.get_instructor_map()

            # --- GÜNCELLENMİŞ ÇAĞRI ---
            # Gelişmiş scheduler artık (schedule, unassigned_exams) tuple'ı döndürüyor
            schedule, unassigned_exams = self.scheduler.generate_exam_schedule(
                start_date,
                end_date,
                exam_type,
                default_duration_val,
                break_time_val,
                excluded_days_val
            )
            # --- ÇAĞRI SONU ---
            
            progress.stop()
            progress.destroy()

            # schedule None değilse ve içinde veri varsa
            if schedule:
                self.schedule_data = schedule # Veriyi sakla
                # Treeview'a ekle (Hoca ve Süre bilgisiyle birlikte)
                for exam in schedule:
                    # Hoca adını al (scheduler döndürmüyorsa map'ten al)
                    instructor = exam.get('instructor') or instructor_map.get(exam['course_code'], 'N/A')
                    # Süreyi al
                    duration = exam.get('duration', default_duration_val)
                    
                    self.tree.insert("", "end", values=(
                        exam['date'],
                        exam['time'],
                        duration, # YENİ
                        exam['course_code'],
                        exam['course_name'],
                        instructor,
                        exam['student_count'],
                        exam['classroom_code'],
                        exam['capacity']
                    ))
                
                # Başarı mesajını atanamayanları içerecek şekilde güncelle
                total_assigned = len(schedule)
                total_unassigned = len(unassigned_exams)
                message = f"Sınav programı oluşturuldu!\n"
                message += f"Toplam {total_assigned} sınav planlandı.\n"
                if total_unassigned > 0:
                     message += f"UYARI: {total_unassigned} sınav atanamadı (Tarih aralığı yetersiz veya uygun derslik bulunamadı)."
                     # Atanamayanları konsola yazdır
                     print("--- ATANAMAYAN SINAVLAR ---")
                     for u_exam in unassigned_exams:
                         print(f" - {u_exam['course_code']} ({u_exam['course_name']}): {u_exam.get('reason', 'Atanamadı')}")
                
                messagebox.showinfo("Başarılı", message)

            else:
                # schedule listesi boş geldiyse
                if unassigned_exams:
                     messagebox.showerror("Hata", f"Sınav programı oluşturulamadı!\n{len(unassigned_exams)} ders için uygun yer veya zaman bulunamadı.")
                else:
                     messagebox.showerror("Hata", "Sınav programı oluşturulamadı! (Veritabanında ders/öğrenci olmayabilir veya bilinmeyen hata)")

        except Exception as e:
            progress.stop()
            progress.destroy()
            messagebox.showerror("Kritik Hata", f"Sınav programı oluşturulurken beklenmedik bir hata oluştu:\n{str(e)}")
            import traceback
            traceback.print_exc() # Detaylı hata için konsola yaz
            self.schedule_data = None

    # --- Excel'e Aktarma Fonksiyonu (GÜNCELLENDİ: Süre kolonunu ekle) ---
    def export_schedule_to_excel(self):
        if not self.schedule_data:
            messagebox.showwarning("Uyarı", "Excel'e aktarılacak bir sınav programı bulunamadı.")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel Dosyası", "*.xlsx"), ("Tüm Dosyalar", "*.*")],
                title="Sınav Programını Excel Olarak Kaydet"
            )

            if not file_path:
                return

            instructor_map = self.get_instructor_map()
            export_data = []
            
            default_duration_val = int(self.duration_entry.get().strip()) # Varsayılanı al

            for exam in self.schedule_data:
                 instructor = exam.get('instructor') or instructor_map.get(exam['course_code'], 'N/A')
                 duration = exam.get('duration', default_duration_val)
                 
                 export_data.append({
                    'Tarih': exam['date'],
                    'Saat': exam['time'],
                    'Süre (dk)': duration, # YENİ
                    'Ders Kodu': exam['course_code'],
                    'Ders Adı': exam['course_name'],
                    'Öğretim Elemanı': instructor,
                    'Öğrenci Sayısı': exam['student_count'],
                    'Derslik': exam['classroom_code'],
                    'Kapasite': exam['capacity']
                 })

            df = pd.DataFrame(export_data)
            # Sütun sırasını belirleyelim
            column_order = ['Tarih', 'Saat', 'Süre (dk)', 'Ders Kodu', 'Ders Adı', 'Öğretim Elemanı', 'Öğrenci Sayısı', 'Derslik', 'Kapasite']
            df = df[column_order]

            df.to_excel(file_path, index=False)
            messagebox.showinfo("Başarılı", f"Sınav programı başarıyla '{os.path.basename(file_path)}' olarak kaydedildi!")

        except Exception as e:
            messagebox.showerror("Hata", f"Excel dosyasına aktarılırken bir hata oluştu:\n{str(e)}")


if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    app = ExamScheduleWindow(department_id=1) 
    app.show()
    root.mainloop()