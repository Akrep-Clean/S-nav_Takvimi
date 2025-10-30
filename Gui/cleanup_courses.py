# test_courses.py
import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


from Data.database import Database

db = Database()
conn = db.get_connection()
cursor = conn.cursor()
# Tüm dersleri sil
cursor.execute("DELETE FROM courses")
conn.commit()

print("✅ Tüm dersler silindi!")

# Kontrol et
cursor.execute("SELECT COUNT(*) FROM courses")
remaining = cursor.fetchone()[0]
print(f"📊 Kalan ders sayısı: {remaining}")

conn.close()