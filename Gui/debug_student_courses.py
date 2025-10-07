import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os


current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
from Data.database import Database

def debug_student_courses():
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    print("🔍 ÖĞRENCİ-DERS İLİŞKİLERİ DEBUG")
    print("=" * 50)
    
    # Toplam ilişki sayısı
    cursor.execute("SELECT COUNT(*) FROM student_courses")
    total_relations = cursor.fetchone()[0]
    print(f"📊 Toplam öğrenci-ders ilişkisi: {total_relations}")
    
    # İlk 10 ilişkiyi göster
    cursor.execute('''
        SELECT s.student_number, s.name, c.code, c.name
        FROM student_courses sc
        JOIN students s ON sc.student_id = s.id
        JOIN courses c ON sc.course_id = c.id
        LIMIT 10
    ''')
    
    relations = cursor.fetchall()
    print("📋 İlk 10 öğrenci-ders ilişkisi:")
    for rel in relations:
        student_no, student_name, course_code, course_name = rel
        print(f"   👤 {student_no} - {student_name} → 📚 {course_code} - {course_name}")
    
    # Her dersin öğrenci sayısı
    print("\n🎯 Derslere göre öğrenci sayıları:")
    cursor.execute('''
        SELECT c.code, c.name, COUNT(sc.student_id) as student_count
        FROM courses c
        LEFT JOIN student_courses sc ON c.id = sc.course_id
        WHERE c.department_id = 1
        GROUP BY c.code
        ORDER BY student_count DESC
    ''')
    
    course_stats = cursor.fetchall()
    for course in course_stats:
        code, name, count = course
        print(f"   📚 {code}: {count} öğrenci")
    
    conn.close()

if __name__ == "__main__":
    debug_student_courses()