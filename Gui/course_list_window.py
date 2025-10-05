import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Data.database import Database

class CourseListWindow:
    def __init__(self, department_id=None):
        self.root = tk.Toplevel()
        self.root.title("Ders Listesi")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")
        self.department_id = department_id
        self.selected_course = None
        
        self.create_widgets()
        self.load_courses()
    
    def show(self):
        self.root.mainloop()
        
    def create_widgets(self):
        # BAŞLIK
        title_label = tk.Label(
            self.root,
            text="Ders Listesi",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # ANA FRAME
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # SOL TARAF - DERS LİSTESİ
        left_frame = tk.LabelFrame(
            main_frame,
            text="Tüm Dersler",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Ders Listesi Treeview
        self.course_tree = ttk.Treeview(
            left_frame,
            columns=("Kod", "Ad", "Hoca", "Tip"),
            show="headings",
            height=20
        )
        
        self.course_tree.heading("Kod", text="Ders Kodu")
        self.course_tree.heading("Ad", text="Ders Adı")
        self.course_tree.heading("Hoca", text="Hoca")
        self.course_tree.heading("Tip", text="Tip")
        
        self.course_tree.column("Kod", width=80)
        self.course_tree.column("Ad", width=200)
        self.course_tree.column("Hoca", width=150)
        self.course_tree.column("Tip", width=80)
        
        course_scrollbar = ttk.Scrollbar(left_frame, orient="vertical", command=self.course_tree.yview)
        self.course_tree.configure(yscrollcommand=course_scrollbar.set)
        
        self.course_tree.pack(side="left", fill="both", expand=True)
        course_scrollbar.pack(side="right", fill="y")
        
        # Sağ taraf - Öğrenci Listesi
        right_frame = tk.LabelFrame(
            main_frame,
            text="Dersi Alan Öğrenciler",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        right_frame.pack(side="right", fill="both", expand=True)
        
        self.student_tree = ttk.Treeview(
            right_frame,
            columns=("No", "Ad-Soyad", "Sınıf"),
            show="headings",
            height=20
        )
        
        self.student_tree.heading("No", text="Öğrenci No")
        self.student_tree.heading("Ad-Soyad", text="Ad-Soyad")
        self.student_tree.heading("Sınıf", text="Sınıf")
        
        self.student_tree.column("No", width=100)
        self.student_tree.column("Ad-Soyad", width=150)
        self.student_tree.column("Sınıf", width=80)
        
        student_scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=student_scrollbar.set)
        
        self.student_tree.pack(side="left", fill="both", expand=True)
        student_scrollbar.pack(side="right", fill="y")
        
        # Event binding
        self.course_tree.bind("<<TreeviewSelect>>", self.on_course_select)
    
    def load_courses(self):
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT code, name, instructor, type FROM courses 
                WHERE department_id = ?
                ORDER BY code
            ''', (self.department_id,))
            
            courses = cursor.fetchall()
            
            # Treeview'ı temizle
            for item in self.course_tree.get_children():
                self.course_tree.delete(item)
            
            # Dersleri ekle
            for course in courses:
                code, name, instructor, course_type = course
                self.course_tree.insert("", "end", values=(code, name, instructor, course_type))
            
            conn.close()
            
            messagebox.showinfo("Başarılı", f"{len(courses)} ders listelendi!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Dersler yüklenirken hata: {str(e)}")
    
    def on_course_select(self, event):
        selected = self.course_tree.selection()
        if not selected:
            return
        
        item = selected[0]
        course_code = self.course_tree.item(item, "values")[0]
        course_name = self.course_tree.item(item, "values")[1]
        self.selected_course = course_code
        
        self.load_students_for_course(course_code)
        
        # Pencere başlığını güncelle
        self.root.title(f"Ders Listesi - {course_code} {course_name}")
    
    def load_students_for_course(self, course_code):
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT s.student_number, s.name, s.class
                FROM students s
                JOIN student_courses sc ON s.id = sc.student_id
                JOIN courses c ON sc.course_id = c.id
                WHERE c.code = ? AND s.department_id = ?
                ORDER BY s.student_number
            ''', (course_code, self.department_id))
            
            students = cursor.fetchall()
            
            # Treeview'ı temizle
            for item in self.student_tree.get_children():
                self.student_tree.delete(item)
            
            # Öğrencileri ekle
            for student in students:
                student_no, name, class_name = student
                self.student_tree.insert("", "end", values=(student_no, name, class_name))
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Öğrenciler yüklenirken hata: {str(e)}")

if __name__ == "__main__":
    app = CourseListWindow()
    app.show()