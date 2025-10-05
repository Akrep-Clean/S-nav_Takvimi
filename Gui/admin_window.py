import tkinter as tk
from tkinter import ttk, messagebox
import excel_upload_window
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
        # BAŞLIK
        title_label = tk.Label(
            self.root,
            text="Admin Paneli",
            font=("Arial", 20, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # AÇIKLAMA
        desc_label = tk.Label(
            self.root,
            text="Tüm bölümlere erişim, her işlemi yapabilme yetkisi",
            font=("Arial", 12),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        desc_label.pack(pady=10)
        
        # BUTON FRAME
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(pady=30)
        
        # BÖLÜM YÖNETİMİ BUTONU
        departments_btn = tk.Button(
            button_frame,
            text="Bölüm Yönetimi",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=20,
            height=3,
            command=self.manage_departments
        )
        departments_btn.grid(row=0, column=0, padx=10, pady=10)
        
        # KULLANICI YÖNETİMİ BUTONU
        users_btn = tk.Button(
            button_frame,
            text="Kullanıcı Yönetimi",
            font=("Arial", 12, "bold"),
            bg="#e74c3c", 
            fg="white",
            width=20,
            height=3,
            command=self.manage_users
        )
        users_btn.grid(row=0, column=1, padx=10, pady=10)
        
        # TÜM SINAV PROGRAMLARI BUTONU
        all_exams_btn = tk.Button(
            button_frame,
            text="Tüm Sınav Programları",
            font=("Arial", 12, "bold"),
            bg="#2ecc71",
            fg="white", 
            width=20,
            height=3,
            command=self.view_all_exams
        )
        all_exams_btn.grid(row=1, column=0, padx=10, pady=10)
        
        # RAPORLAR BUTONU
        reports_btn = tk.Button(
            button_frame,
            text="Raporlar",
            font=("Arial", 12, "bold"),
            bg="#f39c12",
            fg="white",
            width=20,
            height=3,
            command=self.generate_reports
        )
        reports_btn.grid(row=1, column=1, padx=10, pady=10)
        excel_upload_btn = tk.Button(
            button_frame,
            text="Excel ile Veri Yükle",
            font=("Arial", 12, "bold"),
            bg="#8e44ad",
            fg="white",
            width=20,
            height=3,
            command=self.excel_upload
        )
        excel_upload_btn.grid(row=3, column=0, padx=10, pady=10)
        # Öğrenci Listesi Butonu
        student_list_btn = tk.Button(
            button_frame,
            text="Öğrenci Listesi",
            font=("Arial", 12, "bold"),
            bg="#1abc9c",
            fg="white",
            width=20,
            height=3,
            command=self.show_student_list
        )
        student_list_btn.grid(row=2, column=0, padx=10, pady=10)

        # Ders Listesi Butonu
        course_list_btn = tk.Button(
            button_frame,
            text="Ders Listesi", 
            font=("Arial", 12, "bold"),
            bg="#e67e22",
            fg="white",
            width=20,
            height=3,
            command=self.show_course_list
        )
        course_list_btn.grid(row=2, column=1, padx=10, pady=10)
        # ÇIKIŞ BUTONU
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
    
    def manage_departments(self):
        messagebox.showinfo("Bölüm Yönetimi", "Bölüm yönetimi ekranı açılacak...")
        # Burada bölüm ekleme/silme/güncelleme işlemleri yapılacak
    
    def manage_users(self):
        messagebox.showinfo("Kullanıcı Yönetimi", "Kullanıcı yönetimi ekranı açılacak...")
        # Burada kullanıcı ekleme/rol atama işlemleri yapılacak
    
    def view_all_exams(self):
        messagebox.showinfo("Tüm Sınavlar", "Tüm bölümlerin sınav programları görüntülenecek...")
        # Burada tüm sınav programları listelenecek
    
    def generate_reports(self):
        messagebox.showinfo("Raporlar", "Sistem raporları oluşturulacak...")
        # Burada PDF/Excel raporları oluşturulacak
    def excel_upload(self):
        try:
            import excel_upload_window
            
            # DEBUG: Department ID'yi göster
            print(f"🎯 Admin Excel Upload - Department ID: {1}")  # Admin için 1 numaralı department
            
            # Department ID'yi geç - Admin için Bilgisayar Müh. (id=1)
            excel_app = excel_upload_window.ExcelUploadWindow(department_id=1)
            excel_app.show()
        except Exception as e:
            messagebox.showerror("Hata", f"Excel penceresi açılamadı: {str(e)}")   
    def show_student_list(self):
        try:
            import student_list_window
            
            # DEBUG: Department ID'yi göster
            print(f"🎯 Admin Student List - Department ID: {1}")
            
            # Department ID'yi geç - Admin için Bilgisayar Müh. (id=1)
            student_list_window.StudentListWindow(department_id=1).show()
        except Exception as e:
            messagebox.showerror("Hata", f"Öğrenci listesi açılamadı: {str(e)}")

    def show_course_list(self):
        try:
            import course_list_window
            print(f"🎯 Admin Course List - Department ID: {1}")
            
            # Department ID'yi geç - Admin için Bilgisayar Müh. (id=1)
            course_list_window.CourseListWindow(department_id=1).show()
        except Exception as e:
            messagebox.showerror("Hata", f"Ders listesi açılamadı: {str(e)}")
    def logout(self):
        self.root.destroy()
        # Giriş ekranına dön
        from login_window import LoginWindow
        LoginWindow().show()

if __name__ == "__main__":
    app = AdminWindow()
    app.show()