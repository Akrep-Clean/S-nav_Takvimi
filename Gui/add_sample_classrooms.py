import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

# Veritabanına ulaşmak için sys.path ayarı
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)


from Data.database import Database

def add_all_sample_classrooms():
    db = Database()
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # (code, name, capacity, rows (boyuna), columns (enine), seat_type, department_id)
    sample_classrooms = [
        # --- Bölüm 1: Bilgisayar Mühendisliği (PDF'e göre) ---
        # PDF'teki sıra/sütun isimleri formdakiyle (rows=boyuna, cols=enine) eşleşecek şekilde girildi
        # Kapasite = rows * cols * seat_type_multiplier (1, 2, or 3)
        
        # 3001, 301, 42 kap., 7 boyuna, 3 enine. (7*3=21 yuva. 42/21 = 2). PDF'teki "Sıra Yapısı 3" yerine "2'li" olmalı.
        ("3001", "301", 42, 7, 3, "2'li", 1),
        
        # 3002, Büyük Amfi, 48 kap., 8 boyuna, 3 enine. (8*3=24 yuva. 48/24 = 2). PDF'teki "Sıra Yapısı 4" yerine "2'li" olmalı.
        ("3002", "Büyük Amfi", 48, 8, 3, "2'li", 1),
        
        # 3003, 303, 42 kap., 3 boyuna, 7 enine. (3*7=21 yuva. 42/21 = 2). PDF'teki "Sıra Yapısı 3" yerine "2'li" olmalı.
        ("3003", "303", 42, 3, 7, "2'li", 1),
        
        # 3004, EDA, 30 kap., 6 boyuna, 5 enine. (6*5=30 yuva. 30/30 = 1). PDF'teki "Sıra Yapısı 12" yerine "Tekli" olmalı.
        ("3004", "EDA", 30, 6, 5, "Tekli", 1),
        
        # 3005, 305, 42 kap., 3 boyuna, 7 enine. (3*7=21 yuva. 42/21 = 2). PDF'teki "Sıra Yapısı 3" yerine "2'li" olmalı.
        ("3005", "305", 42, 3, 7, "2'li", 1),
        
        # --- Diğer Bölümler için Örnekler (PDF'e göre eklenebilir) ---
        
        # --- Bölüm 2: Yazılım Mühendisliği ---
        ("S101", "Yazılım Lab 1", 50, 10, 5, "Tekli", 2),
        ("S102", "Yazılım Amfi", 100, 10, 10, "Tekli", 2),
        ("S103", "Yazılım Sınıf", 60, 6, 5, "2'li", 2),
        
        # --- Bölüm 3: Elektrik Mühendisliği ---
        ("E101", "Elektrik Amfi", 120, 10, 6, "2'li", 3),
        ("E102", "Devre Lab", 40, 8, 5, "Tekli", 3),
        
        # --- Bölüm 4: Elektronik Mühendisliği ---
        ("EL101", "Elektronik Amfi", 120, 10, 6, "2'li", 4),
        ("EL102", "Sinyal Lab", 40, 8, 5, "Tekli", 4),
        
        # --- Bölüm 5: İnşaat Mühendisliği ---
        ("I101", "İnşaat Amfi", 150, 15, 5, "2'li", 5),
        ("I102", "Çizim Stüdyosu", 60, 10, 6, "Tekli", 5),
    ]
    
    insert_count = 0
    for classroom in sample_classrooms:
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO classrooms 
                (code, name, capacity, rows, columns, seat_type, department_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', classroom)
            if cursor.rowcount > 0:
                insert_count += 1
        except Exception as e:
            print(f"Hata: {classroom[0]} eklenemedi - {e}")
    
    conn.commit()
    conn.close()
    print(f"✅ {insert_count} adet örnek derslik veritabanına eklendi!")

if __name__ == "__main__":
    # Bu scripti çalıştırmadan önce database.py'nin çalışıp
    # boş app.db dosyasını oluşturduğundan emin olun.
    add_all_sample_classrooms()
