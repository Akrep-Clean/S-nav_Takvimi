import sqlite3
from datetime import datetime, timedelta, time
from collections import defaultdict, deque
import random
import itertools
import os
import sys
import traceback

# --- Veritabanı importu için sys.path ayarı ---
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)
# --- Bitiş ---

from Data.database import Database

class ExamScheduler:
    def __init__(self, department_id=1):
        self.department_id = department_id
        self.db = Database()

    # --- Sınıf Seviyesi Fonksiyonu ---
    def get_course_class_levels(self):
        """
        Her dersin ağırlıklı olarak hangi sınıf seviyesindeki öğrenciler tarafından alındığını belirler.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sc.course_id, s.class, COUNT(s.id) as count
            FROM student_courses sc
            JOIN students s ON sc.student_id = s.id
            WHERE s.department_id = ?
            GROUP BY sc.course_id, s.class
            ORDER BY sc.course_id, count DESC
        ''', (self.department_id,))
        rows = cursor.fetchall()
        conn.close()

        course_class_map = {}
        for course_id, class_level, count in rows:
            if course_id not in course_class_map:
                course_class_map[course_id] = class_level
        return course_class_map

    # --- Çakışma Matrisi Fonksiyonu ---
    def get_student_course_conflicts(self):
        """
        Öğrenci bazlı ders çakışma matrisini oluşturur.
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.id as student_id, sc.course_id
            FROM students s
            JOIN student_courses sc ON s.id = sc.student_id
            WHERE s.department_id = ?
        ''', (self.department_id,))
        student_courses_raw = cursor.fetchall()
        conn.close()

        conflict_matrix = defaultdict(set)
        student_course_map = defaultdict(list)
        for student_id, course_id in student_courses_raw:
            student_course_map[student_id].append(course_id)

        for student_id, course_list in student_course_map.items():
            for i in range(len(course_list)):
                for j in range(i + 1, len(course_list)):
                    c1, c2 = course_list[i], course_list[j]
                    conflict_matrix[c1].add(c2)
                    conflict_matrix[c2].add(c1)
        return conflict_matrix

    # --- Ders Detayları (Öğrenci Sayısı, Hoca) Fonksiyonu ---
    def get_course_details(self):
        """
        Her dersin öğrenci sayısını ve diğer bilgilerini alır.
        Dönüş: {course_id: {'code': ..., 'name': ..., 'count': ..., 'instructor': ...}}
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT c.id, c.code, c.name, c.instructor, COUNT(sc.student_id) as student_count
            FROM courses c
            LEFT JOIN student_courses sc ON c.id = sc.course_id
            WHERE c.department_id = ?
            GROUP BY c.id
            ORDER BY student_count DESC
        ''', (self.department_id,))
        course_counts_raw = cursor.fetchall()
        conn.close()

        return {
            course_id: {
                'code': code, 'name': name, 'count': count, 'instructor': instructor
            }
            for course_id, code, name, instructor, count in course_counts_raw
        }

    # --- Graph Coloring (Slot Oluşturma) Fonksiyonu ---
    def create_exam_slots(self, conflict_matrix, course_details, course_class_levels):
        """
        Dersleri çakışmayacak ve sınıf seviyelerini dağıtacak şekilde soyut slotlara atar.
        """
        courses_sorted = sorted(course_details.keys(),
                              key=lambda cid: (
                                  -course_details[cid]['count'], # Önce en kalabalık
                                  course_class_levels.get(cid, "Bilinmiyor") # Sonra sınıfa göre grupla
                              ),
                              reverse=False)

        slot_courses_map = defaultdict(list)
        slot_class_levels = defaultdict(set)
        course_to_slot_map = {}
        
        current_slot = 0

        for course_id in courses_sorted:
            course_level = course_class_levels.get(course_id, "Bilinmiyor")
            suitable_slot = -1

            conflicting_slots = set()
            for conflicting_course_id in conflict_matrix.get(course_id, set()):
                if conflicting_course_id in course_to_slot_map:
                    conflicting_slots.add(course_to_slot_map[conflicting_course_id])

            preferred_slot = -1 # Sınıf çakışması olmayan
            fallback_slot = -1 # Sınıf çakışması olan

            for slot in range(current_slot + 1):
                if slot in conflicting_slots:
                    continue 

                if course_level != "Bilinmiyor" and course_level in slot_class_levels[slot]:
                    if fallback_slot == -1: # İlk bulduğumuz sınıf çakışmalı slot
                        fallback_slot = slot
                else:
                    preferred_slot = slot # Sınıf çakışması yok, bu en iyisi
                    break # En iyi slotu bulduk, aramayı durdur.

            if preferred_slot != -1:
                suitable_slot = preferred_slot
            elif fallback_slot != -1: # Sınıf çakışmasız slot yoksa, çakışmalı olana ata
                suitable_slot = fallback_slot
            else: # Hiç uygun slot yoksa (veya ilk dersse)
                current_slot += 1
                suitable_slot = current_slot
            
            course_to_slot_map[course_id] = suitable_slot
            slot_courses_map[suitable_slot].append(course_id)
            if course_level != "Bilinmiyor":
                slot_class_levels[suitable_slot].add(course_level)

        print(f"   -> Graph Coloring Sonucu: {len(slot_courses_map)} slot oluşturuldu.")
        return slot_courses_map

    # --- Derslik Uygunluk Fonksiyonu ---
    def is_classroom_available(self, calendar, date_str, start_dt, end_dt, classroom_id):
        """Dersliğin verilen zaman aralığında boş olup olmadığını kontrol eder."""
        if date_str not in calendar or classroom_id not in calendar[date_str]:
            return True 

        classroom_schedule = calendar[date_str].get(classroom_id, [])
        for scheduled_start, scheduled_end in classroom_schedule:
            if start_dt < scheduled_end and end_dt > scheduled_start:
                return False
        return True

    # --- GÜNCELLENMİŞ: Sınav Bölme Mantığı Aktif ---
    def assign_classrooms_and_times(self, slot_courses_map, course_details,
                                     start_date_str, end_date_str,
                                     default_duration=75, break_time=15,
                                     excluded_days=[],
                                     special_durations={},
                                     day_start_time_str="09:00", day_end_time_str="17:00"):
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        # Derslikleri BÜYÜKTEN KÜÇÜĞE sırala (Sınav bölme için)
        cursor.execute('''
            SELECT id, code, name, capacity FROM classrooms
            WHERE department_id = ?
            ORDER BY capacity DESC 
        ''', (self.department_id,))
        all_classrooms = cursor.fetchall()
        conn.close()

        if not all_classrooms:
            raise ValueError("Sınav yapılacak uygun derslik bulunamadı!")
        
        print(f"   -> {len(all_classrooms)} derslik bulundu (En büyük kapasite: {all_classrooms[0][3]})")

        try:
            current_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            day_start_time = datetime.strptime(day_start_time_str, '%H:%M').time()
            day_end_time = datetime.strptime(day_end_time_str, '%H:%M').time()
        except ValueError:
             raise ValueError("Tarih/Saat formatı hatalı (YYYY-MM-DD veya HH:MM).")

        calendar = defaultdict(lambda: defaultdict(list))
        exam_schedule = []
        unassigned_exams = []
        sorted_slots = sorted(slot_courses_map.keys())
        processed_slots = 0

        while current_date <= end_date and processed_slots < len(sorted_slots):
            day_name = current_date.strftime('%A').lower()
            if current_date.weekday() >= 5 or day_name in [d.lower() for d in excluded_days]:
                 print(f"   -> Gün atlandı (hariç/hafta sonu): {current_date}")
                 current_date += timedelta(days=1)
                 continue

            print(f"-> Gün işleniyor: {current_date}")
            current_slot_time_dt = datetime.combine(current_date, day_start_time)
            
            # O gün yerleştirebildiğimiz kadar slot yerleştirelim
            while processed_slots < len(sorted_slots):
                slot_key = sorted_slots[processed_slots]
                courses_in_slot = slot_courses_map[slot_key]
                courses_in_slot.sort(key=lambda cid: course_details[cid]['count'], reverse=True)

                possible_start_time_dt = current_slot_time_dt
                slot_successfully_placed = False

                while possible_start_time_dt.time() < day_end_time:
                    current_date_str = current_date.strftime('%Y-%m-%d')
                    print(f"   -> Slot {slot_key} için saat deneniyor: {possible_start_time_dt.strftime('%H:%M')}")
                    
                    all_courses_in_slot_assigned = True
                    day_ended_for_this_slot_duration = False
                    temp_unavailable_classrooms_for_this_try = set()
                    temp_assignments_for_slot = []

                    for course_id in courses_in_slot:
                        details = course_details[course_id]
                        student_count = details['count']
                        duration = special_durations.get(details['code'], default_duration)
                        exam_end_time_dt = possible_start_time_dt + timedelta(minutes=duration)

                        if exam_end_time_dt.time() > day_end_time or exam_end_time_dt.date() != current_date:
                            if exam_end_time_dt.time() <= time(0, 0): # Gece yarısını geçtiyse (örn: 23:00 + 75dk)
                                print(f"      -> Sınav gün sonunu (gece yarısı) aşıyor ({details['code']})")
                            else:
                                print(f"      -> Sınav gün bitiş saatini ({day_end_time_str}) aşıyor ({details['code']})")
                            day_ended_for_this_slot_duration = True
                            all_courses_in_slot_assigned = False
                            break 

                        # --- SINAV BÖLME MANTIĞI ---
                        needed_capacity = student_count
                        assigned_classrooms_for_this_course = []
                        
                        for (c_id, c_code, c_name, c_cap) in all_classrooms:
                            if needed_capacity <= 0:
                                break
                            
                            if c_id not in temp_unavailable_classrooms_for_this_try and \
                               self.is_classroom_available(calendar, current_date_str, possible_start_time_dt, exam_end_time_dt, c_id):
                                
                                assigned_classrooms_for_this_course.append({
                                    'classroom_id': c_id, 'classroom_code': c_code,
                                    'classroom_name': c_name, 'capacity': c_cap
                                })
                                needed_capacity -= c_cap
                                temp_unavailable_classrooms_for_this_try.add(c_id)
                        
                        if needed_capacity > 0:
                            print(f"      -> {details['code']} ({student_count} öğr.) için YETERLİ KAPASİTE ({student_count - needed_capacity} bulundu) bulunamadı {possible_start_time_dt.strftime('%H:%M')}.")
                            all_courses_in_slot_assigned = False
                            break
                        else:
                            print(f"      -> Geçici atama: {details['code']} ({len(assigned_classrooms_for_this_course)} dersliğe bölündü)")
                            temp_assignments_for_slot.append({
                                'course_id': course_id, 'details': details, 'duration': duration,
                                'start_dt': possible_start_time_dt, 'end_dt': exam_end_time_dt,
                                'assigned_classrooms': assigned_classrooms_for_this_course
                            })
                        # --- SINAV BÖLME SONU ---

                    if day_ended_for_this_slot_duration:
                        # Bu saat dilimi gün sonunu aştı, bu gün için daha fazla deneme
                        print(f"   -> Gün sonuna ulaşıldı, {current_date_str} için başka atama denenmeyecek.")
                        break # Saat arama döngüsünden (Inner Loop 2) çık

                    if all_courses_in_slot_assigned:
                        latest_end_time_in_slot = possible_start_time_dt
                        
                        for assignment in temp_assignments_for_slot:
                            course_id = assignment['course_id']
                            details = assignment['details']
                            
                            classroom_codes = []
                            classroom_ids = []
                            total_capacity = 0
                            
                            for room in assignment['assigned_classrooms']:
                                classroom_id = room['classroom_id']
                                classroom_codes.append(room['classroom_code'])
                                classroom_ids.append(str(classroom_id)) # Stringe çevir
                                total_capacity += room['capacity']
                                
                                calendar[current_date_str][classroom_id].append((assignment['start_dt'], assignment['end_dt']))
                                calendar[current_date_str][classroom_id].sort()

                            if assignment['end_dt'] > latest_end_time_in_slot:
                                latest_end_time_in_slot = assignment['end_dt']

                            exam_schedule.append({
                                'course_id': course_id,
                                'course_code': details['code'],
                                'course_name': details['name'],
                                'instructor': details.get('instructor', 'N/A'),
                                'student_count': details['count'],
                                'date': current_date_str,
                                'time': assignment['start_dt'].strftime('%H:%M'),
                                'duration': assignment['duration'],
                                'classroom_id': ','.join(classroom_ids), # ID'leri birleştir
                                'classroom_code': ','.join(classroom_codes), # Kodları birleştir
                                'capacity': total_capacity # Toplam kapasite
                            })

                        print(f"   => Slot {slot_key} atandı: {current_date_str} {possible_start_time_dt.strftime('%H:%M')}")
                        slot_successfully_placed = True
                        processed_slots += 1
                        current_slot_time_dt = latest_end_time_in_slot + timedelta(minutes=break_time)
                        break # Saat arama döngüsünden (Inner Loop 2) çık
                    
                    else:
                         possible_start_time_dt += timedelta(minutes=break_time) 

                if not slot_successfully_placed:
                    print(f"   -> Slot {slot_key} bugüne sığmadı.")
                    break 

            current_date += timedelta(days=1)


        if processed_slots < len(sorted_slots):
            print(f"❌ Tarih aralığı {start_date_str} - {end_date_str} yetersiz!")
            for slot_key in sorted_slots[processed_slots:]:
                 for course_id in slot_courses_map[slot_key]:
                      details = course_details[course_id]
                      unassigned_exams.append({'course_code': details['code'], 'course_name': details['name'], 'reason': 'Tarih aralığı yetersiz/Kapasite doldu'})

        print(f"✅ Zaman/Derslik atama tamamlandı. {len(exam_schedule)} sınav atandı.")
        if unassigned_exams:
             print(f"⚠️ Atanamayan Sınavlar ({len(unassigned_exams)}): {[e['course_code'] for e in unassigned_exams]}")

        return exam_schedule, unassigned_exams

    # --- Ana Fonksiyon (Güncellendi) ---
    def generate_exam_schedule(self, start_date, end_date, exam_type="Vize",
                               default_duration=75, break_time=15, excluded_days=[]):
        """
        Tüm sınav programını oluşturur.
        """
        exam_schedule = []
        unassigned_exams = []
        try:
            print(f"\n--- Sınav Programı Oluşturma Başladı ({exam_type}) ---")
            print(f"Tarih Aralığı: {start_date} - {end_date}, Süre: {default_duration} dk, Mola: {break_time} dk, Hariç: {excluded_days}")

            print("1. Ders Detayları (Öğrenci Sayısı, Hoca) Alınıyor...")
            course_details = self.get_course_details()
            if not course_details:
                 raise ValueError("Veritabanında planlanacak ders bulunamadı (Excel yüklendi mi?).")
            
            # 0 öğrencili dersleri filtrele
            courses_with_students = {cid: det for cid, det in course_details.items() if det['count'] > 0}
            if not courses_with_students:
                 raise ValueError("Planlanacak (öğrencisi olan) ders bulunamadı.")
            print(f"   -> {len(courses_with_students)} öğrencisi olan ders planlanacak.")

            print("2. Öğrenci-Ders Çakışmaları Hesaplanıyor...")
            conflict_matrix = self.get_student_course_conflicts()
            print(f"   -> {len(conflict_matrix)} ders için çakışma bilgisi bulundu.")

            print("3. Derslerin Sınıf Seviyeleri Belirleniyor...")
            course_class_levels = self.get_course_class_levels()
            print(f"   -> {len(course_class_levels)} ders için sınıf seviyesi belirlendi.")

            print("4. Graph Coloring ile Çakışmayacak Slotlar Oluşturuluyor (Sınıf dağılımı dikkate alınarak)...")
            slot_courses_map = self.create_exam_slots(
                conflict_matrix, courses_with_students, course_class_levels
            )
            if not slot_courses_map:
                 raise ValueError("Graph coloring başarısız, slot oluşturulamadı.")

            print("5. Zaman ve Derslik Atamaları Yapılıyor (SINAV BÖLME AKTİF)...")
            exam_schedule, unassigned_exams = self.assign_classrooms_and_times(
                slot_courses_map, courses_with_students, start_date, end_date,
                default_duration, break_time, excluded_days
            )

            total_assigned = len(exam_schedule)
            total_courses = len(courses_with_students)
            print(f"\n--- Sınav Programı Oluşturma Tamamlandı ---")
            print(f"   -> Toplam {total_courses} dersten {total_assigned} tanesi için sınav atandı.")
            if unassigned_exams:
                 print(f"   -> Atanamayan {len(unassigned_exams)} sınav:")
                 for exam in unassigned_exams: print(f"      - {exam['course_code']} ({exam['course_name']})")
            print(f"--------------------------------------------")

        except ValueError as ve:
             print(f"❌ Veri/Yapılandırma Hatası: {ve}")
        except Exception as e:
            print(f"❌ Beklenmedik Hata: {e}")
            traceback.print_exc()

        return exam_schedule, unassigned_exams


# --- Test Bloğu ---
if __name__ == "__main__":
    scheduler = ExamScheduler(department_id=1) 

    start = "2025-10-27"
    end = "2025-11-07"
    exam_type = "Vize"
    excluded = ["Saturday", "Sunday"]

    schedule, unassigned = scheduler.generate_exam_schedule(start, end, exam_type, excluded_days=excluded)

    if schedule:
        print("\n📋 OLUŞTURULAN SINAV PROGRAMI (İlk 20):")
        schedule.sort(key=lambda x: (x['date'], x['time']))
        for exam in schedule[:20]:
            print(f"   {exam['date']} {exam['time']} ({exam['duration']} dk) - {exam['course_code']} ({exam['student_count']} öğr.) -> {exam['classroom_code']} (Toplam Kap: {exam['capacity']})")
    else:
        print("\n❌ Sınav programı oluşturulamadı veya boş döndü.")

    if unassigned:
        print("\n⚠️ ATANAMAYAN SINAVLAR:")
        for exam in unassigned:
             print(f"   - {exam['course_code']} ({exam['course_name']}): {exam.get('reason', 'Atanamadı')}")

