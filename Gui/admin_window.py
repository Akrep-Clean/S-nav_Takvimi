import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
import traceback


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)



try:
    import excel_upload_window
    import student_list_window
    import course_list_window
    import exam_schedule_window
    import classroom_window
    import login_window
except ImportError as e:
    messagebox.showerror("Import Hatası", f"Gerekli modüller yüklenemedi: {e}\nLütfen dosya yapısını kontrol edin.")
    sys.exit(1)


class AdminWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sınav Takvim Sistemi - Admin Paneli")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        self.create_widgets()
        
    def show(self):
        self.root.mainloop()
        
    def create_widgets(self):

        title_label = tk.Label(
            self.root,
            text="Admin Paneli",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        

        desc_label = tk.Label(
            self.root,
            text="Tüm bölümlere erişim, her işlemi yapabilme yetkisi",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        desc_label.pack(pady=10)
        

        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=30)
        

        classroom_btn = tk.Button(
            button_frame,
            text="Derslik Yönetimi",
            font=("Arial", 12, "bold"),
            bg="#f39c12", # Turuncu
            fg="white",
            width=20,
            height=3,
            command=self.manage_classrooms
        )
        classroom_btn.grid(row=0, column=0, padx=10, pady=10) 
        
        
        excel_upload_btn = tk.Button(
            button_frame,
            text="Excel ile Veri Yükle",
            font=("Arial", 12, "bold"),
            bg="#8e44ad", # Mor
            fg="white",
            width=20,
            height=3,
            command=self.excel_upload
        )
        excel_upload_btn.grid(row=0, column=1, padx=10, pady=10)

       
        exam_schedule_btn = tk.Button(
            button_frame,
            text="Sınav Programı Oluştur",
            font=("Arial", 12, "bold"),
            bg="#e74c3c", # Kırmızı
            fg="white",
            width=20,
            height=3,
            command=self.show_exam_schedule
        )
        exam_schedule_btn.grid(row=0, column=2, padx=10, pady=10) 
        
      
        student_list_btn = tk.Button(
            button_frame,
            text="Öğrenci Listesi",
            font=("Arial", 12, "bold"),
            bg="#1abc9c", # Turkuaz
            fg="white",
            width=20,
            height=3,
            command=self.show_student_list
        )
        student_list_btn.grid(row=1, column=0, padx=10, pady=10)

        
        course_list_btn = tk.Button(
            button_frame,
            text="Ders Listesi", 
            font=("Arial", 12, "bold"),
            bg="#e67e22", # Turuncu 2
            fg="white",
            width=20,
            height=3,
            command=self.show_course_list
        )
        course_list_btn.grid(row=1, column=1, padx=10, pady=10)

        
        logout_btn = tk.Button(
            self.root,
            text="Çıkış Yap",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            width=15,
            command=self.logout
        )
        logout_btn.pack(pady=20)
    

    
    def excel_upload(self):
        try:

            print(f"🎯 Admin Excel Upload - Varsayılan Department ID: {1}")
            excel_app = excel_upload_window.ExcelUploadWindow(department_id=1)
            excel_app.show()
        except Exception as e:
            messagebox.showerror("Hata", f"Excel penceresi açılamadı: {str(e)}")
            traceback.print_exc()
            
    def show_student_list(self):
        try:

            print(f"🎯 Admin Student List - Varsayılan Department ID: {1}")
            student_list_window.StudentListWindow(department_id=1).show()
        except Exception as e:
            messagebox.showerror("Hata", f"Öğrenci listesi açılamadı: {str(e)}")
            traceback.print_exc()

    def show_exam_schedule(self):
        try:
            
            exam_schedule_window.ExamScheduleWindow(department_id=1).show()
        except Exception as e:
            messagebox.showerror("Hata", f"Sınav programı penceresi açılamadı: {str(e)}")
            traceback.print_exc()

    def show_course_list(self):
        try:
            
            print(f"🎯 Admin Course List - Varsayılan Department ID: {1}")
            course_list_window.CourseListWindow(department_id=1).show()
        except Exception as e:
            messagebox.showerror("Hata", f"Ders listesi açılamadı: {str(e)}")
            traceback.print_exc()
            
    def manage_classrooms(self):
        try:
            
            classroom_window.ClassroomWindow(department_id=1).show()
        except Exception as e:
            messagebox.showerror("Hata", f"Derslik yönetimi açılamadı: {str(e)}")
            traceback.print_exc()

    def logout(self):
        self.root.destroy()
        
        login_app = login_window.LoginWindow()
        login_app.show()

if __name__ == "__main__":
    app = AdminWindow()
    app.show()
