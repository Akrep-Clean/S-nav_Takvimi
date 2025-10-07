import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import datetime, timedelta

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Services.exam_scheduler import ExamScheduler

class ExamScheduleWindow:
    def __init__(self, department_id=1):
        self.root = tk.Toplevel()
        self.root.title("Sınav Programı Oluştur")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        self.department_id = department_id
        self.scheduler = ExamScheduler(department_id)
        
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
        title_label.pack(pady=20)
        
        # AYARLAR FRAME
        settings_frame = tk.LabelFrame(
            self.root,
            text="Sınav Ayarları",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        settings_frame.pack(pady=10, padx=20, fill="x")
        
        # Tarih aralığı
        date_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        date_frame.pack(fill="x", pady=5)
        
        tk.Label(date_frame, text="Başlangıç Tarihi:", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5)
        self.start_date_entry = tk.Entry(date_frame, font=("Arial", 10), width=12)
        self.start_date_entry.pack(side="left", padx=5)
        self.start_date_entry.insert(0, "2024-01-15")
        
        tk.Label(date_frame, text="Bitiş Tarihi:", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5)
        self.end_date_entry = tk.Entry(date_frame, font=("Arial", 10), width=12)
        self.end_date_entry.pack(side="left", padx=5)
        self.end_date_entry.insert(0, "2024-01-30")
        
        # Sınav tipi
        type_frame = tk.Frame(settings_frame, bg="#f0f0f0")
        type_frame.pack(fill="x", pady=5)
        
        tk.Label(type_frame, text="Sınav Tipi:", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5)
        self.exam_type_combo = ttk.Combobox(type_frame, values=["Vize", "Final", "Bütünleme"], width=15)
        self.exam_type_combo.pack(side="left", padx=5)
        self.exam_type_combo.set("Vize")
        
        # OLUŞTUR BUTONU
        generate_btn = tk.Button(
            settings_frame,
            text="Sınav Programını Oluştur",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=20,
            command=self.generate_schedule
        )
        generate_btn.pack(pady=10)
        
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
        
        # Treeview
        self.tree = ttk.Treeview(
            results_frame,
            columns=("Tarih", "Saat", "Ders Kodu", "Ders Adı", "Öğrenci Sayısı", "Derslik", "Kapasite"),
            show="headings",
            height=20
        )
        
        # Kolon başlıkları
        self.tree.heading("Tarih", text="Tarih")
        self.tree.heading("Saat", text="Saat")
        self.tree.heading("Ders Kodu", text="Ders Kodu")
        self.tree.heading("Ders Adı", text="Ders Adı")
        self.tree.heading("Öğrenci Sayısı", text="Öğrenci Sayısı")
        self.tree.heading("Derslik", text="Derslik")
        self.tree.heading("Kapasite", text="Kapasite")
        
        # Kolon genişlikleri
        self.tree.column("Tarih", width=80)
        self.tree.column("Saat", width=60)
        self.tree.column("Ders Kodu", width=80)
        self.tree.column("Ders Adı", width=200)
        self.tree.column("Öğrenci Sayısı", width=100)
        self.tree.column("Derslik", width=80)
        self.tree.column("Kapasite", width=70)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def generate_schedule(self):
        start_date = self.start_date_entry.get().strip()
        end_date = self.end_date_entry.get().strip()
        exam_type = self.exam_type_combo.get()
        
        if not start_date or not end_date:
            messagebox.showerror("Hata", "Lütfen tarih aralığını girin!")
            return
        
        try:
            # Tarih formatı kontrolü
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Hata", "Tarih formatı yanlış! YYYY-MM-DD formatında girin.")
            return
        
        # Treeview'ı temizle
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Progress bar göster
        progress = ttk.Progressbar(self.root, orient="horizontal", length=400, mode='indeterminate')
        progress.pack(pady=10)
        progress.start()
        
        self.root.update_idletasks()
        
        try:
            # Sınav programını oluştur
            schedule = self.scheduler.generate_exam_schedule(start_date, end_date, exam_type)
            
            progress.stop()
            progress.destroy()
            
            if schedule:
                # Treeview'a ekle
                for exam in schedule:
                    self.tree.insert("", "end", values=(
                        exam['date'],
                        exam['time'],
                        exam['course_code'],
                        exam['course_name'],
                        exam['student_count'],
                        exam['classroom_code'],
                        exam['capacity']
                    ))
                
                messagebox.showinfo("Başarılı", 
                                  f"Sınav programı oluşturuldu!\n"
                                  f"Toplam {len(schedule)} sınav planlandı.")
            else:
                messagebox.showerror("Hata", "Sınav programı oluşturulamadı!")
                
        except Exception as e:
            progress.stop()
            progress.destroy()
            messagebox.showerror("Hata", f"Sınav programı oluşturulurken hata: {str(e)}")

if __name__ == "__main__":
    app = ExamScheduleWindow()
    app.show()