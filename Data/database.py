import sqlite3
import os

class Database:
    def __init__(self, db_name="app.db"):
        db_path = os.path.join(os.path.dirname(__file__), db_name)
        self.db_path = db_path
        self._create_tables()
        self._insert_initial_data()

    def _create_tables(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'coordinator')),
                department_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS classrooms (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                capacity INTEGER NOT NULL,
                rows INTEGER NOT NULL,
                columns INTEGER NOT NULL,
                seat_type TEXT,
                department_id INTEGER NOT NULL,
                UNIQUE(code, department_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT NOT NULL,
                name TEXT NOT NULL,
                instructor TEXT,
                type TEXT,
                department_id INTEGER NOT NULL,
                UNIQUE(code, department_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_number TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                class TEXT,
                department_id INTEGER NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_courses (
                student_id INTEGER NOT NULL,
                course_id INTEGER NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
                PRIMARY KEY (student_id, course_id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def _insert_initial_data(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT OR IGNORE INTO users (email, password, role, department_id) VALUES (?, ?, ?, ?)",
                           ('admin', 'admin', 'admin', 1))
        except sqlite3.IntegrityError:
            pass 

        departments = [
            (1, 'Bilgisayar Mühendisliği'),
            (2, 'Yazılım Mühendisliği'),
            (3, 'Elektrik Mühendisliği'),
            (4, 'Elektronik Mühendisliği'),
            (5, 'İnşaat Mühendisliği')
        ]
        
        try:
            cursor.executemany("INSERT OR IGNORE INTO departments (id, name) VALUES (?, ?)", departments)
        except sqlite3.IntegrityError:
            pass

        conn.commit()
        conn.close()

if __name__ == "__main__":
    print("Veritabanı başlatılıyor...")
    db = Database()
    print(f"Veritabanı dosyası '{db.db_path}' oluşturuldu/kontrol edildi.")