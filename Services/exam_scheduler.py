import sqlite3
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random
from Data.database import Database

class ExamScheduler:
    def __init__(self, department_id=1):
        self.department_id = department_id
        self.db = Database()
        
    def get_student_course_conflicts(self):
        """
        Öğrenci bazlı ders çakışma matrisini oluştur
        Hangi dersler hangi öğrencileri paylaşıyor?
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Öğrenci-Ders ilişkilerini al
        cursor.execute('''
            SELECT s.id as student_id, c.id as course_id, c.code, c.name
            FROM students s
            JOIN student_courses sc ON s.id = sc.student_id
            JOIN courses c ON sc.course_id = c.id
            WHERE s.department_id = ?
        ''', (self.department_id,))
        
        student_courses = cursor.fetchall()
        
        # Çakışma matrisi: {course_id: set_of_conflicting_course_ids}
        conflict_matrix = defaultdict(set)
        
        # Öğrenci bazlı ders gruplarını oluştur
        student_course_map = defaultdict(list)
        for student_id, course_id, code, name in student_courses:
            student_course_map[student_id].append(course_id)
        
        # Her öğrenci için, aldığı tüm dersler birbiriyle çakışır
        for student_id, course_list in student_course_map.items():
            for i in range(len(course_list)):
                for j in range(i + 1, len(course_list)):
                    conflict_matrix[course_list[i]].add(course_list[j])
                    conflict_matrix[course_list[j]].add(course_list[i])
        
        conn.close()
        return conflict_matrix
    
    def get_course_student_counts(self):
        """Her dersin kaç öğrencisi olduğunu hesapla"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT c.id, c.code, c.name, COUNT(sc.student_id) as student_count
            FROM courses c
            LEFT JOIN student_courses sc ON c.id = sc.course_id
            WHERE c.department_id = ?
            GROUP BY c.id
            ORDER BY student_count DESC
        ''', (self.department_id,))
        
        course_counts = cursor.fetchall()
        conn.close()
        
        return {course_id: (code, name, count) for course_id, code, name, count in course_counts}
    
    def graph_coloring_schedule(self, conflict_matrix, course_student_counts):
        """
        Graph coloring algoritması ile sınav programı oluştur
        """
        # Dersleri öğrenci sayısına göre sırala (en zor olanlar önce)
        courses_sorted = sorted(course_student_counts.keys(), 
                              key=lambda x: course_student_counts[x][2], 
                              reverse=True)
        
        # Zaman slotlarına atama
        time_slots = {}  # {course_id: time_slot}
        slot_courses = defaultdict(list)  # {time_slot: [course_ids]}
        
        # Mevcut zaman slotu
        current_slot = 0
        
        for course_id in courses_sorted:
            # Bu ders için uygun zaman slotunu bul
            suitable_slot = None
            
            for slot in range(current_slot + 1):
                # Bu slottaki derslerle çakışma kontrolü
                conflict_found = False
                for scheduled_course in slot_courses[slot]:
                    if scheduled_course in conflict_matrix[course_id]:
                        conflict_found = True
                        break
                
                if not conflict_found:
                    suitable_slot = slot
                    break
            
            if suitable_slot is None:
                # Yeni zaman slotu oluştur
                current_slot += 1
                suitable_slot = current_slot
            
            time_slots[course_id] = suitable_slot
            slot_courses[suitable_slot].append(course_id)
        
        return time_slots, slot_courses
    
    def assign_classrooms(self, slot_courses, course_student_counts, date_range):
        """
        Derslik atamalarını yap ve tarih/saat belirle
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Mevcut derslikleri al
        cursor.execute('''
            SELECT id, code, name, capacity FROM classrooms 
            WHERE department_id = ?
            ORDER BY capacity DESC
        ''', (self.department_id,))
        
        classrooms = cursor.fetchall()
        
        # Tarih aralığını işle
        start_date, end_date = date_range
        current_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Günlük zaman slotları (09:00, 11:00, 14:00, 16:00)
        daily_slots = ['09:00', '11:00', '14:00', '16:00']
        
        exam_schedule = []
        slot_index = 0
        
        # Her zaman slotu için derslik ataması yap
        for time_slot, course_ids in slot_courses.items():
            if slot_index >= len(daily_slots):
                # Yeni güne geç
                current_date += timedelta(days=1)
                slot_index = 0
                
                # Haftasonu kontrolü
                while current_date.weekday() >= 5:  # 5: Cumartesi, 6: Pazar
                    current_date += timedelta(days=1)
            
            if current_date > end_date:
                raise Exception("Tarih aralığı yetersiz! Daha fazla güne ihtiyaç var.")
            
            exam_time = daily_slots[slot_index]
            available_classrooms = classrooms.copy()
            
            # Bu slot'taki dersleri dersliklere yerleştir
            for course_id in course_ids:
                code, name, student_count = course_student_counts[course_id]
                
                # Yeterli kapasiteli derslik bul
                classroom_assigned = None
                for i, (class_id, class_code, class_name, capacity) in enumerate(available_classrooms):
                    if capacity >= student_count:
                        classroom_assigned = (class_id, class_code, class_name, capacity)
                        available_classrooms.pop(i)
                        break
                
                if classroom_assigned:
                    class_id, class_code, class_name, capacity = classroom_assigned
                    exam_schedule.append({
                        'course_id': course_id,
                        'course_code': code,
                        'course_name': name,
                        'student_count': student_count,
                        'date': current_date.strftime('%Y-%m-%d'),
                        'time': exam_time,
                        'classroom_id': class_id,
                        'classroom_code': class_code,
                        'classroom_name': class_name,
                        'capacity': capacity
                    })
                else:
                    # Derslik bulunamadı - hata veya bölme gerekli
                    print(f"⚠️ Derslik bulunamadı: {code} ({student_count} öğrenci)")
            
            slot_index += 1
        
        conn.close()
        return exam_schedule
    
    def generate_exam_schedule(self, start_date, end_date, exam_type="Vize"):
        """
        Tüm sınav programını oluştur
        """
        try:
            print("🔍 Çakışma matrisi oluşturuluyor...")
            conflict_matrix = self.get_student_course_conflicts()
            
            print("📊 Ders-öğrenci sayıları hesaplanıyor...")
            course_student_counts = self.get_course_student_counts()
            
            print("🎨 Graph coloring ile zaman planlaması yapılıyor...")
            time_slots, slot_courses = self.graph_coloring_schedule(conflict_matrix, course_student_counts)
            
            print("🏫 Derslik atamaları yapılıyor...")
            exam_schedule = self.assign_classrooms(slot_courses, course_student_counts, (start_date, end_date))
            
            print(f"✅ Sınav programı oluşturuldu!")
            print(f"   📅 Toplam {len(slot_courses)} zaman slotu")
            print(f"   📚 Toplam {len(exam_schedule)} sınav")
            print(f"   🗓️  Tarih aralığı: {start_date} - {end_date}")
            
            return exam_schedule
            
        except Exception as e:
            print(f"❌ Hata: {e}")
            return None

# Test için
if __name__ == "__main__":
    scheduler = ExamScheduler(department_id=1)
    schedule = scheduler.generate_exam_schedule("2024-01-15", "2024-01-30", "Vize")
    
    if schedule:
        print("\n📋 OLUŞTURULAN SINAV PROGRAMI:")
        for exam in schedule[:5]:  # İlk 5'i göster
            print(f"   {exam['course_code']} - {exam['date']} {exam['time']} - {exam['classroom_code']} ({exam['student_count']} öğr.)")