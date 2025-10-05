# data/database.py
import hashlib
import sqlite3
import os

class Database:
    def __init__(self, db_path="data/app.db"):
        self.db_path = db_path
        self.create_tables()
        self.create_default_data()  # Tablolardan SONRA veri ekle
        
    def get_connection(self):
        """Veritabanı bağlantısını oluştur"""
        return sqlite3.connect(self.db_path)
    
    def create_tables(self):
        """Tüm tabloları oluştur"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Kullanıcılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                department_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 2. Bölümler tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        # 3. CLASSROOMS tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classrooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                rows INTEGER NOT NULL,
                columns INTEGER NOT NULL,
                seat_type TEXT NOT NULL,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        ''')    
        
        # 4. COURSES tablosu - DERSLER
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                instructor TEXT NOT NULL,
                type TEXT NOT NULL,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        ''')
        
        # 5. STUDENTS tablosu - ÖĞRENCİLER
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                class TEXT NOT NULL,
                department_id INTEGER,
                FOREIGN KEY (department_id) REFERENCES departments(id)
            )
        ''')
        
        # 6. STUDENT_COURSES tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id),
                FOREIGN KEY (course_id) REFERENCES courses(id),
                UNIQUE(student_id, course_id)
            )
        ''')
        
        # 7. EXAMS tablosu - SINAVLAR
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exams (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id INTEGER NOT NULL,
                exam_date DATE NOT NULL,
                exam_time TIME NOT NULL,
                duration INTEGER NOT NULL,
                exam_type TEXT NOT NULL,
                classroom_id INTEGER,
                FOREIGN KEY (course_id) REFERENCES courses(id),
                FOREIGN KEY (classroom_id) REFERENCES classrooms(id)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✅ Tüm veritabanı tabloları oluşturuldu!")
    
    def create_default_data(self):
        """Varsayılan admin ve bölümleri ekle"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # 1. Bölümleri ekle
        departments = [
            "Bilgisayar Mühendisliği",
            "Yazılım Mühendisliği", 
            "Elektrik Mühendisliği",
            "Elektronik Mühendisliği",
            "İnşaat Mühendisliği"
        ]
        
        for dept in departments:
            cursor.execute('INSERT OR IGNORE INTO departments (name) VALUES (?)', (dept,))
        
        # 2. Admin kullanıcısını ekle
        hashed_password = hashlib.md5("admin".encode()).hexdigest()    
        cursor.execute('''
            INSERT OR IGNORE INTO users (email, password, role) 
            VALUES (?, ?, ?)
        ''', ('admin@kocaeli.edu.tr', hashed_password, 'admin'))
        
        conn.commit()
        conn.close()
        print("✅ Varsayılan veriler eklendi!")  

if __name__ == "__main__":
    db = Database()  # __init__ içinde zaten create_tables ve create_default_data çağrılıyor
    
    # Test: Verileri oku
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM departments")
    departments = cursor.fetchall()
    print("📋 Bölümler:", departments)
    
    cursor.execute("SELECT * FROM users") 
    users = cursor.fetchall()
    print("👥 Kullanıcılar:", users)

    cursor.execute("SELECT * FROM classrooms")
    classrooms = cursor.fetchall()
    print("🏫 Sınıflar:", classrooms)
    
    conn.close()