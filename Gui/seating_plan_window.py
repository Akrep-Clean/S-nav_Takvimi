import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sys
import os
from fpdf import FPDF # PDF oluşturmak için
from collections import defaultdict # Import edildi
import traceback # Hata ayıklama için

# Veritabanı ve diğer modüllere ulaşmak için sys.path güncellemesi
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Data.database import Database

class SeatingPlanWindow:
    def __init__(self, parent, exam_details, department_id):
        self.root = tk.Toplevel(parent) # Ana pencereye bağlı Toplevel
        self.root.title("Oturma Planı Oluştur")
        self.root.geometry("800x650") # Boyut artırıldı
        self.root.configure(bg="#f0f0f0")

        self.exam_details = exam_details 
        self.department_id = department_id
        self.db = Database()
        
        self.seating_plan_by_classroom = defaultdict(list) # {classroom_code: [öğrenci listesi]}
        self.classroom_info_map = {} # {classroom_code: (rows, cols, capacity, seat_type)}
        self.all_students = [] # Dersteki tüm öğrenciler
        
        # Gelen birleştirilmiş derslik kodlarını ayır
        self.classroom_codes_list = exam_details.get('classroom_code', '').split(',')
        self.classroom_codes_list = [code.strip() for code in self.classroom_codes_list if code.strip()]
        
        if not self.classroom_codes_list:
            messagebox.showerror("Hata", "Sınav için atanmış derslik kodu bulunamadı.")
            self.root.destroy()
            return
        
        self.canvas = None
        self.classroom_select_combo = None # Derslik seçimi için combobox

        self.create_widgets()
        
        # Pencere açılır açılmaz oturma planını oluştur
        self.generate_seating_plan()

    def create_widgets(self):
        # BAŞLIK
        title_label = tk.Label(
            self.root,
            text="Sınav Oturma Planı",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=10)

        # SINAV BİLGİLERİ GÖSTERİMİ
        info_frame = tk.Frame(self.root, bg="#f0f0f0", pady=5)
        info_frame.pack(fill="x", padx=20)
        tk.Label(info_frame, text=f"Ders: {self.exam_details['course_code']} - {self.exam_details['course_name']}",
                 font=("Arial", 10), bg="#f0f0f0", anchor='w').pack(fill="x")
        tk.Label(info_frame, text=f"Tarih/Saat: {self.exam_details['date']} {self.exam_details['time']}",
                 font=("Arial", 10), bg="#f0f0f0", anchor='w').pack(fill="x")
        tk.Label(info_frame, text=f"Derslikler: {self.exam_details['classroom_code']}", 
                 font=("Arial", 10, "bold"), bg="#f0f0f0", anchor='w').pack(fill="x")
        tk.Label(info_frame, text=f"Öğrenci Sayısı: {self.exam_details['student_count']}",
                 font=("Arial", 10), bg="#f0f0f0", anchor='w').pack(fill="x")

        # GÖRSELLEŞTİRME ALANI
        visualization_frame = tk.LabelFrame(
            self.root,
            text="Oturma Düzeni Önizleme",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        visualization_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Derslik Seçim Çerçevesi
        preview_select_frame = tk.Frame(visualization_frame, bg="#f0f0f0")
        preview_select_frame.pack(fill="x", pady=(0, 5))
        
        tk.Label(preview_select_frame, text="Önizlenecek Derslik:", font=("Arial", 10), bg="#f0f0f0").pack(side="left")
        
        self.classroom_select_combo = ttk.Combobox(
            preview_select_frame,
            values=self.classroom_codes_list,
            state="readonly",
            width=15
        )
        self.classroom_select_combo.pack(side="left", padx=5)
        self.classroom_select_combo.bind("<<ComboboxSelected>>", self.update_canvas_preview)

        # Canvas widget'ı
        self.canvas = tk.Canvas(visualization_frame, bg="white", relief="sunken", borderwidth=1)
        self.canvas.pack(fill="both", expand=True)

        # PDF İNDİRME BUTONU
        generate_pdf_btn = tk.Button(
            self.root,
            text="Oturma Planı PDF İndir",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            width=30,
            command=self.export_to_pdf
        )
        generate_pdf_btn.pack(pady=15)

    def generate_seating_plan(self):
        """
        Sınav planını (öğrencilerin dersliklere dağılımını) hesaplar.
        """
        try:
            # 1. Öğrencileri Çek
            conn = self.db.get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT s.student_number, s.name
                FROM students s
                JOIN student_courses sc ON s.id = sc.student_id
                JOIN courses c ON sc.course_id = c.id
                WHERE c.code = ? AND s.department_id = ?
                ORDER BY s.student_number -- Numaraya göre sırala
            ''', (self.exam_details['course_code'], self.department_id))
            self.all_students = cursor.fetchall()
            
            # Gelen öğrenci sayısı ile veritabanından çekilen öğrenci sayısını karşılaştır
            db_student_count = len(self.all_students)
            exam_student_count = 0
            try:
                # 'student_count' string gelebilir, int'e çevir
                exam_student_count = int(self.exam_details['student_count'])
            except ValueError:
                pass

            if db_student_count == 0:
                messagebox.showwarning("Uyarı", "Bu derse kayıtlı öğrenci veritabanında bulunamadı.")
                conn.close()
                return
            
            # Eğer scheduler'ın bulduğu sayı ile DB'den gelen sayı farklıysa (genelde aynı olmalı)
            if db_student_count != exam_student_count:
                print(f"Uyarı: Scheduler {exam_student_count} öğrenci bekliyordu, DB'den {db_student_count} öğrenci bulundu.")
                # Biz DB'den geleni (self.all_students) baz alacağız.

            # 2. Tüm Dersliklerin Bilgilerini Çek
            self.classroom_info_map = {}
            total_available_capacity = 0
            for code in self.classroom_codes_list:
                code = code.strip() 
                if not code: continue
                
                cursor.execute('''
                    SELECT rows, columns, capacity, seat_type FROM classrooms
                    WHERE code = ? AND department_id = ?
                ''', (code, self.department_id))
                classroom_info = cursor.fetchone()
                
                if classroom_info:
                    self.classroom_info_map[code] = classroom_info
                    total_available_capacity += int(classroom_info[2]) # Kapasiteyi topla
                else:
                    messagebox.showerror("Hata", f"'{code}' kodlu derslik bilgisi veritabanında bulunamadı!")
                    conn.close()
                    return
            conn.close() 

            # 3. Oturma Planı Oluştur (Öğrencileri dersliklere dağıt)
            self.seating_plan_by_classroom.clear()
            student_index = 0
            
            for code in self.classroom_codes_list:
                code = code.strip()
                if student_index >= len(self.all_students):
                    break # Tüm öğrenciler yerleşti
                
                if code not in self.classroom_info_map: continue
                
                rows, cols, capacity, seat_type = self.classroom_info_map[code]
                rows, cols, capacity = int(rows), int(cols), int(capacity)
                
                seats_filled_in_this_room = 0
                
                # Dersliğin kapasitesi (10x5=50) veya (öğrenci sayısı-kapasite) kadar yerleştir
                for r in range(1, rows + 1):
                    for c in range(1, cols + 1):
                        # Öğrenci bittiyse VEYA bu dersliğin kapasitesi dolduysa dur
                        if student_index >= len(self.all_students) or seats_filled_in_this_room >= capacity:
                            break
                            
                        student_no, student_name = self.all_students[student_index]
                        self.seating_plan_by_classroom[code].append({
                            'student_number': student_no,
                            'name': student_name,
                            'row': r,
                            'col': c
                        })
                        student_index += 1
                        seats_filled_in_this_room += 1
                    
                    if student_index >= len(self.all_students) or seats_filled_in_this_room >= capacity:
                        break 
            
            total_placed_students = student_index
            
            if self.classroom_codes_list:
                self.classroom_select_combo.set(self.classroom_codes_list[0])
                self.update_canvas_preview(None) 

            # DÜZELTİLMİŞ UYARI: Toplam öğrenci sayısı, yerleştirilen öğrenci sayısından fazlaysa
            if total_placed_students < len(self.all_students):
                 messagebox.showwarning("Kapasite Aşıldı", 
                                       f"Toplam derslik kapasitesi ({total_available_capacity}) yetersiz!\n\n"
                                       f"{len(self.all_students)} öğrenciden {total_placed_students} tanesi yerleştirilebildi.\n"
                                       f"{len(self.all_students) - total_placed_students} öğrenci açıkta kaldı.")
            else:
                print(f"Oturma planı: {total_placed_students} öğrencinin tamamı yerleştirildi.")

        except Exception as e:
            messagebox.showerror("Hata", f"Oturma planı oluşturulurken hata: {str(e)}")
            traceback.print_exc()

    def update_canvas_preview(self, event):
        """Combobox'tan seçilen dersliğin önizlemesini çizer."""
        selected_code = self.classroom_select_combo.get()
        if not selected_code or selected_code not in self.classroom_info_map:
            if self.canvas: self.canvas.delete("all")
            return

        rows, cols, capacity, seat_type = self.classroom_info_map[selected_code]
        rows, cols, capacity = int(rows), int(cols), int(capacity)
        
        students_in_this_room = self.seating_plan_by_classroom.get(selected_code, [])

        self.draw_seating_plan_on_canvas(rows, cols, seat_type, students_in_this_room, capacity)


    # --- GÜNCELLENDİ: "Çince" hatasını düzeltmek için font değiştirildi ---
    def draw_seating_plan_on_canvas(self, rows, cols, seat_type, students_assigned, capacity):
        """Verilen bilgilere göre Canvas üzerine çizim yapar."""
        if not self.canvas: return
        self.canvas.delete("all") 

        self.canvas.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        padding = 20
        draw_width = canvas_width - 2 * padding
        draw_height = canvas_height - 2 * padding

        if rows <= 0 or cols <= 0: return

        # Basit (r, c) grid hesaplaması
        total_cell_width = draw_width / cols
        total_cell_height = draw_height / rows
        
        seat_width = total_cell_width * 0.8 # Aralığı artır
        seat_height = total_cell_height * 0.8
        
        h_gap = total_cell_width * 0.1 # %10 soldan %10 sağdan
        v_gap = total_cell_height * 0.1

        # FONT DÜZELTMESİ: "Çince" hatası için Arial kullan
        font_size = min(9, int(seat_height / 3.5)) # Max 9
        seat_font = ("Arial", font_size, "bold") # Kalın Arial dene

        seat_map = { (seat['row'], seat['col']): seat['student_number'] for seat in students_assigned }
        
        seat_counter = 0
        for r in range(1, rows + 1):
            for c in range(1, cols + 1):
                if seat_counter >= capacity: # Dersliğin fiziksel kapasitesini aşma
                    break

                x1 = padding + (c - 1) * total_cell_width + h_gap
                y1 = padding + (r - 1) * total_cell_height + v_gap
                x2 = x1 + seat_width
                y2 = y1 + seat_height

                student_no = seat_map.get((r, c))
                
                fill_color = "lightblue" if student_no else "#E0E0E0" # Boş koltuklar açık gri
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill_color, outline="black")

                if student_no:
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    short_no = str(student_no)[-4:] # Son 4 hane
                    try:
                        self.canvas.create_text(cx, cy, text=short_no, font=seat_font, anchor="center")
                    except Exception as e:
                        print(f"Canvas text çizim hatası (muhtemelen font): {e}")
                        # Font hatası olursa dikdörtgeni yine de çizsin ama text'i çizmesin
                
                seat_counter += 1
            if seat_counter >= capacity:
                break


    # --- GÜNCELLENDİ: PDF (Her derslik için ayrı sayfa oluşturur) ---
    def export_to_pdf(self):
        if not self.seating_plan_by_classroom:
            messagebox.showerror("Hata", "Oluşturulmuş bir oturma planı bulunamadı.")
            return

        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF Dosyası", "*.pdf"), ("Tüm Dosyalar", "*.*")],
                title="Oturma Planını PDF Olarak Kaydet",
                initialfile=f"OturmaPlani_{self.exam_details['course_code']}_{self.exam_details['date']}.pdf"
            )
            if not file_path: return

            pdf = FPDF()
            line_height = 8
            col_widths = [35, 85, 20, 20] # No, Ad, Sıra, Sütun

            # --- Font Ekleme Bloğu (DejaVu veya Arial Fallback) ---
            pdf_font = 'Arial' # Varsayılan olarak Arial
            try:
                current_dir_font = os.path.dirname(os.path.abspath(__file__))
                parent_dir_font = os.path.dirname(current_dir_font)
                font_path_regular = os.path.join(parent_dir_font, "fonts", "DejaVuSansCondensed.ttf")
                font_path_bold = os.path.join(parent_dir_font, "fonts", "DejaVuSansCondensed-Bold.ttf")
                
                if not os.path.exists(font_path_regular) or not os.path.exists(font_path_bold):
                    raise FileNotFoundError("DejaVu font dosyaları 'fonts' klasöründe bulunamadı.")
                    
                pdf.add_font('DejaVu', '', font_path_regular, uni=True)
                pdf.add_font('DejaVu', 'B', font_path_bold, uni=True)
                pdf_font = 'DejaVu' # Başarılı olursa Dejavu kullan
                print("DejaVu fontları PDF için yüklendi.")
            except Exception as font_error:
                 print(f"Font Hatası: {font_error}. Standart font (Arial) kullanılacak.")
                 # Arial zaten FPDF'in içinde tanımlı
            # --- Font Ekleme Bloğu Sonu ---

            # --- Başlık Fonksiyonu ---
            def draw_pdf_header(classroom_code):
                pdf.set_font(pdf_font, 'B', 14)
                # Türkçe karakterleri elle düzelt (Arial için)
                title_text = f"{self.exam_details['course_code']} - {self.exam_details['course_name']} Oturma Plani"
                if pdf_font == 'Arial':
                    title_text = title_text.encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 10, title_text, ln=True, align='C')
                
                pdf.set_font(pdf_font, 'B', 12)
                derslik_text = f"Derslik: {classroom_code}"
                if pdf_font == 'Arial':
                    derslik_text = derslik_text.encode('latin-1', 'replace').decode('latin-1')
                pdf.cell(0, 8, derslik_text, ln=True, align='C')
                
                pdf.set_font(pdf_font, '', 10)
                pdf.cell(0, 6, f"Tarih/Saat: {self.exam_details['date']} {self.exam_details['time']}", ln=True, align='C')
                pdf.ln(5)
                # Tablo Başlıkları
                pdf.set_font(pdf_font, 'B', 10)
                pdf.cell(col_widths[0], line_height, 'Ogrenci No', border=1, align='C')
                pdf.cell(col_widths[1], line_height, 'Ad Soyad', border=1, align='C')
                pdf.cell(col_widths[2], line_height, 'Sira', border=1, align='C')
                pdf.cell(col_widths[3], line_height, 'Sutun', border=1, align='C')
                pdf.ln()
            # --- Başlık Fonksiyonu Sonu ---

            # Her derslik için bir sayfa oluştur
            for classroom_code in self.classroom_codes_list:
                classroom_code = classroom_code.strip()
                students_in_this_room = self.seating_plan_by_classroom.get(classroom_code, [])
                
                if not students_in_this_room:
                    continue 

                pdf.add_page()
                draw_pdf_header(classroom_code)
                pdf.set_font(pdf_font, '', 9)

                for student_seat in students_in_this_room:
                    if pdf.get_y() + line_height > pdf.page_break_trigger:
                        pdf.add_page()
                        draw_pdf_header(classroom_code)
                        pdf.set_font(pdf_font, '', 9)

                    no = str(student_seat['student_number'])
                    name = str(student_seat['name'])
                    row_num = str(student_seat['row'])
                    col_num = str(student_seat['col'])

                    if pdf_font == 'Arial':
                        name = name.encode('latin-1', 'replace').decode('latin-1')
                        
                    pdf.cell(col_widths[0], line_height, no, border=1)
                    pdf.cell(col_widths[1], line_height, name, border=1)
                    pdf.cell(col_widths[2], line_height, row_num, border=1, align='C')
                    pdf.cell(col_widths[3], line_height, col_num, border=1, align='C')
                    pdf.ln()

            pdf.output(file_path)
            messagebox.showinfo("Başarılı", f"Oturma planı ({len(self.classroom_codes_list)} derslik için) PDF olarak kaydedildi:\n{file_path}")

        except Exception as e:
            messagebox.showerror("PDF Hatası", f"PDF oluşturulurken hata: {str(e)}")
            traceback.print_exc() # Konsola detaylı hata


# Test bloğu
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() 
    sample_exam = {
        'date': '2024-01-15', 'time': '09:00', 'course_code': 'YDB117',
        'course_name': 'İngilizce I', 'student_count': 150, 
        'classroom_code': '3001,3002,3003,3004', 
        'capacity': 162, 
        'instructor': 'Öğr. Gör. Ali SEZER'
    }
    app = SeatingPlanWindow(root, sample_exam, department_id=1)
    root.mainloop()

