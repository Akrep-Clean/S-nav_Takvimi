import tkinter as tk
from tkinter import messagebox
import sqlite3
import hashlib
import sys
import os
import admin_window

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Data.database import Database

class LoginWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login Ekranı")
        self.root.geometry("600x300")
        self.root.configure(bg="#9C9191")
        self.create_widgets()
        
    def show(self):
        self.root.mainloop()       
        
    def create_widgets(self):
        title_label = tk.Label(
            self.root, 
            text="Sınav Takvim Sistemi",
            font=("Arial", 16, "bold"),
            bg="#62B5C4"
        )
        title_label.pack(pady=20)
        
        email_label = tk.Label(
            self.root, 
            text="E-mail:",
            font=("Arial", 12, "bold"),
            bg="#3B4E6B"
        )
        email_label.pack(pady=5)
        self.email_entry = tk.Entry(self.root, font=("Arial", 12))
        self.email_entry.pack(pady=5)

        password_label = tk.Label(
            self.root,
            text="Şifre:",
            font=("Arial", 12, "bold"),
            bg="#3B4E6B"
        )
        password_label.pack(pady=5)
        self.password_entry = tk.Entry(self.root, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5)
        
        login_button = tk.Button(
            self.root,
            text="Giriş Yap",
            font=("Arial", 12, "bold"),
            bg="#3B4E6B",
            fg="white",
            command=self.login
        )
        login_button.pack(pady=20)

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        
        if not email or not password:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return
        
        # VERİTABANI İLE GİRİŞ KONTROLÜ
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            # Şifreyi hash'le
            hashed_password = hashlib.md5(password.encode()).hexdigest()
            
            # Kullanıcıyı veritabanında ara
            cursor.execute('''
                SELECT * FROM users WHERE email = ? AND password = ?
            ''', (email, hashed_password))
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                user_id, user_email, user_password, role, department_id, created_at = user
                messagebox.showinfo("Başarılı", f"{role} olarak giriş yapıldı!")
                self.root.destroy()
                
                # Rol'e göre yönlendirme
                if role == "admin":
                    # Önce admin_window dosyasını oluşturmamız lazım
                    messagebox.showinfo("Yönlendirme", "Admin paneline yönlendiriliyor...")
                    
                    admin_window.AdminWindow().show()
                elif role == "coordinator":
                    # import coordinator_window
                    # coordinator_window.CoordinatorWindow(department_id).show()
                    messagebox.showinfo("Yönlendirme", "Koordinatör paneline yönlendiriliyor...")
            else:
                messagebox.showerror("Hata", "Geçersiz e-mail veya şifre.")
                
        except Exception as e:
            messagebox.showerror("Hata", f"Veritabanı hatası: {str(e)}")

if __name__ == "__main__":
    login_app = LoginWindow()
    login_app.show()