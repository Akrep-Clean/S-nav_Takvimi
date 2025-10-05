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

# Dersleri ve department_id'lerini kontrol et
cursor.execute("SELECT code, name, department_id FROM courses")
courses = cursor.fetchall()

print("📋 Veritabanındaki dersler:")
for course in courses:
    print(f"  {course[0]} - {course[1]} - Department ID: {course[2]}")

conn.close()