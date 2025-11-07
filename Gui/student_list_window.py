import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Data.database import Database

class StudentListWindow:
    def __init__(self, department_id=None):
        self.root = tk.Toplevel()
        self.root.title("Öğrenci Listesi")
        self.root.geometry("800x500")
        self.root.configure(bg="#f0f0f0")
    
        self.department_id = department_id if department_id else 1
        
        
        print(f" StudentListWindow AÇILDI - Department ID: {self.department_id}")
        self.create_widgets()
        self.load_students()
    
    def show(self):
        self.root.mainloop()
        
    def create_widgets(self):
        
        title_label = tk.Label(
            self.root,
            text="Öğrenci Listesi",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        
        search_frame = tk.Frame(self.root, bg="#f0f0f0")
        search_frame.pack(pady=10)
        
        tk.Label(search_frame, text="Öğrenci No:", font=("Arial", 10), bg="#f0f0f0").pack(side="left", padx=5)
        self.search_entry = tk.Entry(search_frame, font=("Arial", 10), width=20)
        self.search_entry.pack(side="left", padx=5)
        
        search_btn = tk.Button(
            search_frame,
            text="Ara",
            font=("Arial", 10),
            bg="#3498db",
            fg="white",
            command=self.search_student
        )
        search_btn.pack(side="left", padx=5)
        
        
        show_all_btn = tk.Button(
            search_frame,
            text="Tümünü Göster",
            font=("Arial", 10),
            bg="#2ecc71",
            fg="white",
            command=self.load_students
        )
        show_all_btn.pack(side="left", padx=5)
        
        
        tree_frame = tk.Frame(self.root)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=("Öğrenci No", "Ad-Soyad", "Sınıf", "Dersler"),
            show="headings",
            height=15
        )
        
        self.tree.heading("Öğrenci No", text="Öğrenci No")
        self.tree.heading("Ad-Soyad", text="Ad-Soyad")
        self.tree.heading("Sınıf", text="Sınıf")
        self.tree.heading("Dersler", text="Aldığı Dersler")
        
        self.tree.column("Öğrenci No", width=100)
        self.tree.column("Ad-Soyad", width=150)
        self.tree.column("Sınıf", width=80)
        self.tree.column("Dersler", width=400)
        
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def load_students(self):
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT student_number, name, class FROM students 
                WHERE department_id = ?
                ORDER BY student_number
            ''', (self.department_id,))
            
            students = cursor.fetchall()
            
            
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            
            for student in students:
                student_no, name, class_name = student
                
                
                cursor.execute('''
                    SELECT c.code, c.name 
                    FROM student_courses sc
                    JOIN courses c ON sc.course_id = c.id
                    JOIN students s ON sc.student_id = s.id
                    WHERE s.student_number = ?
                ''', (student_no,))
                
                courses = cursor.fetchall()
                course_list = ", ".join([f"{code}" for code, name in courses])
                
                self.tree.insert("", "end", values=(student_no, name, class_name, course_list))
            
            conn.close()
            
            messagebox.showinfo("Başarılı", f"{len(students)} öğrenci listelendi!")
            
        except Exception as e:
            messagebox.showerror("Hata", f"Öğrenciler yüklenirken hata: {str(e)}")
    
    def search_student(self):
        student_no = self.search_entry.get().strip()
        if not student_no:
            messagebox.showwarning("Uyarı", "Lütfen öğrenci numarası girin!")
            return
        
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT student_number, name, class FROM students 
                WHERE student_number = ? AND department_id = ?
            ''', (student_no, self.department_id))
            
            student = cursor.fetchone()
            
            if student:
                
                for item in self.tree.get_children():
                    self.tree.delete(item)
                
                student_no, name, class_name = student
                
                
                cursor.execute('''
                    SELECT c.code, c.name 
                    FROM student_courses sc
                    JOIN courses c ON sc.course_id = c.id
                    JOIN students s ON sc.student_id = s.id
                    WHERE s.student_number = ?
                ''', (student_no,))
                
                courses = cursor.fetchall()
                course_list = ", ".join([f"{code}" for code, name in courses])
                
                self.tree.insert("", "end", values=(student_no, name, class_name, course_list))
                messagebox.showinfo("Bulundu", f"Öğrenci bulundu: {name}")
            else:
                messagebox.showinfo("Bulunamadı", "Bu numarada öğrenci bulunamadı!")
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Arama sırasında hata: {str(e)}")

if __name__ == "__main__":
    app = StudentListWindow()
    app.show()