import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Data.database import Database

class ClassroomWindow:
    def __init__(self, department_id=1):
        self.root = tk.Toplevel()
        self.root.title("Derslik Yönetimi")
        self.root.geometry("1000x600")
        self.root.configure(bg="#f0f0f0")
        self.department_id = department_id
        self.selected_classroom = None
        
        self.create_widgets()
        self.load_classrooms()
    
    def show(self):
        self.root.mainloop()
        
    def create_widgets(self):
        # BAŞLIK
        title_label = tk.Label(
            self.root,
            text="Derslik Yönetimi",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # ANA FRAME
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # SOL TARAF - DERSLİK FORMU
        left_frame = tk.LabelFrame(
            main_frame,
            text="Derslik Bilgileri",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        
        # Derslik Kodu
        tk.Label(left_frame, text="Derslik Kodu:", font=("Arial", 10), bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=5)
        self.code_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.code_entry.grid(row=0, column=1, pady=5, padx=5)
        
        # Derslik Adı
        tk.Label(left_frame, text="Derslik Adı:", font=("Arial", 10), bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.name_entry.grid(row=1, column=1, pady=5, padx=5)
        
        # Kapasite
        tk.Label(left_frame, text="Kapasite:", font=("Arial", 10), bg="#f0f0f0").grid(row=2, column=0, sticky="w", pady=5)
        self.capacity_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.capacity_entry.grid(row=2, column=1, pady=5, padx=5)
        
        # Sıra Sayısı
        tk.Label(left_frame, text="Sıra Sayısı:", font=("Arial", 10), bg="#f0f0f0").grid(row=3, column=0, sticky="w", pady=5)
        self.rows_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.rows_entry.grid(row=3, column=1, pady=5, padx=5)
        
        # Sütun Sayısı
        tk.Label(left_frame, text="Sütun Sayısı:", font=("Arial", 10), bg="#f0f0f0").grid(row=4, column=0, sticky="w", pady=5)
        self.columns_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.columns_entry.grid(row=4, column=1, pady=5, padx=5)
        
        # Sıra Tipi
        tk.Label(left_frame, text="Sıra Tipi:", font=("Arial", 10), bg="#f0f0f0").grid(row=5, column=0, sticky="w", pady=5)
        self.seat_type_combo = ttk.Combobox(left_frame, values=["2'li", "3'lü", "Tekli"], width=17)
        self.seat_type_combo.grid(row=5, column=1, pady=5, padx=5)
        self.seat_type_combo.set("2'li")
        
        # BUTONLAR
        button_frame = tk.Frame(left_frame, bg="#f0f0f0")
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)
        
        add_btn = tk.Button(
            button_frame,
            text="Ekle",
            font=("Arial", 10, "bold"),
            bg="#2ecc71",
            fg="white",
            width=8,
            command=self.add_classroom
        )
        add_btn.pack(side="left", padx=5)
        
        update_btn = tk.Button(
            button_frame,
            text="Güncelle",
            font=("Arial", 10, "bold"),
            bg="#3498db",
            fg="white",
            width=8,
            command=self.update_classroom
        )
        update_btn.pack(side="left", padx=5)
        
        delete_btn = tk.Button(
            button_frame,
            text="Sil",
            font=("Arial", 10, "bold"),
            bg="#e74c3c",
            fg="white",
            width=8,
            command=self.delete_classroom
        )
        delete_btn.pack(side="left", padx=5)
        
        clear_btn = tk.Button(
            button_frame,
            text="Temizle",
            font=("Arial", 10),
            bg="#95a5a6",
            fg="white",
            width=8,
            command=self.clear_form
        )
        clear_btn.pack(side="left", padx=5)
        
        # SAĞ TARAF - DERSLİK LİSTESİ
        right_frame = tk.LabelFrame(
            main_frame,
            text="Derslik Listesi",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        right_frame.pack(side="right", fill="both", expand=True)
        
        # Treeview
        self.tree = ttk.Treeview(
            right_frame,
            columns=("ID", "Kod", "Ad", "Kapasite", "Sıra", "Sütun", "Tip"),
            show="headings",
            height=20
        )
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Kod", text="Derslik Kodu")
        self.tree.heading("Ad", text="Derslik Adı")
        self.tree.heading("Kapasite", text="Kapasite")
        self.tree.heading("Sıra", text="Sıra Sayısı")
        self.tree.heading("Sütun", text="Sütun Sayısı")
        self.tree.heading("Tip", text="Sıra Tipi")
        
        self.tree.column("ID", width=40)
        self.tree.column("Kod", width=80)
        self.tree.column("Ad", width=120)
        self.tree.column("Kapasite", width=60)
        self.tree.column("Sıra", width=60)
        self.tree.column("Sütun", width=60)
        self.tree.column("Tip", width=60)
        
        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Event binding
        self.tree.bind("<<TreeviewSelect>>", self.on_classroom_select)
    
    def load_classrooms(self):
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, code, name, capacity, rows, columns, seat_type 
                FROM classrooms 
                WHERE department_id = ?
                ORDER BY code
            ''', (self.department_id,))
            
            classrooms = cursor.fetchall()
            
            # Treeview'ı temizle
            for item in self.tree.get_children():
                self.tree.delete(item)
            
            # Derslikleri ekle
            for classroom in classrooms:
                self.tree.insert("", "end", values=classroom)
            
            conn.close()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Derslikler yüklenirken hata: {str(e)}")
    
    def on_classroom_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        
        item = selected[0]
        values = self.tree.item(item, "values")
        
        self.selected_classroom = values[0]  # ID
        self.code_entry.delete(0, tk.END)
        self.code_entry.insert(0, values[1])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[2])
        self.capacity_entry.delete(0, tk.END)
        self.capacity_entry.insert(0, values[3])
        self.rows_entry.delete(0, tk.END)
        self.rows_entry.insert(0, values[4])
        self.columns_entry.delete(0, tk.END)
        self.columns_entry.insert(0, values[5])
        self.seat_type_combo.set(values[6])
    
    def add_classroom(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        capacity = self.capacity_entry.get().strip()
        rows = self.rows_entry.get().strip()
        columns = self.columns_entry.get().strip()
        seat_type = self.seat_type_combo.get()
        
        if not all([code, name, capacity, rows, columns]):
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
            return
        
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO classrooms 
                (code, name, capacity, rows, columns, seat_type, department_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, int(capacity), int(rows), int(columns), seat_type, self.department_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarılı", "Derslik başarıyla eklendi!")
            self.clear_form()
            self.load_classrooms()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Derslik eklenirken hata: {str(e)}")
    
    def update_classroom(self):
        if not self.selected_classroom:
            messagebox.showwarning("Uyarı", "Lütfen güncellemek için bir derslik seçin!")
            return
        
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        capacity = self.capacity_entry.get().strip()
        rows = self.rows_entry.get().strip()
        columns = self.columns_entry.get().strip()
        seat_type = self.seat_type_combo.get()
        
        if not all([code, name, capacity, rows, columns]):
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
            return
        
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE classrooms 
                SET code = ?, name = ?, capacity = ?, rows = ?, columns = ?, seat_type = ?
                WHERE id = ? AND department_id = ?
            ''', (code, name, int(capacity), int(rows), int(columns), seat_type, self.selected_classroom, self.department_id))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarılı", "Derslik başarıyla güncellendi!")
            self.clear_form()
            self.load_classrooms()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Derslik güncellenirken hata: {str(e)}")
    
    def delete_classroom(self):
        if not self.selected_classroom:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir derslik seçin!")
            return
        
        result = messagebox.askyesno("Onay", "Bu dersliği silmek istediğinizden emin misiniz?")
        if not result:
            return
        
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM classrooms WHERE id = ?', (self.selected_classroom,))
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Başarılı", "Derslik başarıyla silindi!")
            self.clear_form()
            self.load_classrooms()
            
        except Exception as e:
            messagebox.showerror("Hata", f"Derslik silinirken hata: {str(e)}")
    
    def clear_form(self):
        self.selected_classroom = None
        self.code_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.capacity_entry.delete(0, tk.END)
        self.rows_entry.delete(0, tk.END)
        self.columns_entry.delete(0, tk.END)
        self.seat_type_combo.set("2'li")

if __name__ == "__main__":
    app = ClassroomWindow()
    app.show()