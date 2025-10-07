import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


from Data.database import Database

def add_sample_classrooms():
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    sample_classrooms = [
        # (code, name, capacity, rows, columns, seat_type, department_id)
        ("A101", "Amfi 1", 150, 15, 10, "2'li", 1),
        ("A102", "Amfi 2", 120, 12, 10, "2'li", 1),
        ("B201", "Sınıf 201", 50, 10, 5, "2'li", 1),
        ("B202", "Sınıf 202", 60, 12, 5, "2'li", 1),
        ("LAB1", "Bilgisayar Lab 1", 40, 8, 5, "Tekli", 1),
        ("LAB2", "Bilgisayar Lab 2", 30, 6, 5, "Tekli", 1),
        ("C301", "Büyük Sınıf", 200, 20, 10, "3'lü", 1),
        ("C302", "Orta Sınıf", 80, 10, 8, "2'li", 1)
    ]
    
    for classroom in sample_classrooms:
        cursor.execute('''
            INSERT OR IGNORE INTO classrooms 
            (code, name, capacity, rows, columns, seat_type, department_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', classroom)
    
    conn.commit()
    conn.close()
    print("✅ Örnek derslikler eklendi!")

if __name__ == "__main__":
    add_sample_classrooms()