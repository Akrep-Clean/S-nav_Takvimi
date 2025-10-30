import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from Data.database import Database

class ClassroomWindow:
    def __init__(self, department_id=1):
        self.root = tk.Toplevel()
        self.root.title("Derslik Yönetimi")
        # Pencere boyutunu görselleştirme için genişletelim
        self.root.geometry("1200x700") # Genişlik ve yükseklik artırıldı
        self.root.configure(bg="#f0f0f0")
        self.department_id = department_id
        self.selected_classroom = None

        # Görselleştirme için Canvas nesnesini tutacak değişken
        self.canvas = None
        # Görselleştirme çerçevesini tutacak değişken
        self.visualization_frame = None

        self.create_widgets()
        self.load_classrooms()

    def show(self):
        self.root.mainloop()

    def create_widgets(self):
        # BAŞLIK
        title_label = tk.Label(
            self.root,
            text="Derslik Yönetimi",
            font=("Arial", 16, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=15) # Biraz padding azaltıldı

        # ANA FRAME
        main_frame = tk.Frame(self.root, bg="#f0f0f0")
        # fill="both", expand=True ile ana pencereye yayılmasını sağla
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # SOL TARAF - DERSLİK FORMU (Aynı kalıyor)
        left_frame = tk.LabelFrame(
            main_frame,
            text="Derslik Bilgileri",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        # Sadece dikeyde yayılsın (fill="y") ve sola yaslansın
        left_frame.pack(side="left", fill="y", padx=(0, 10))

        # --- Form elemanları (Entry, Label, Button) aynı kalıyor ---
        # Derslik Kodu
        tk.Label(left_frame, text="Derslik Kodu:", font=("Arial", 10), bg="#f0f0f0").grid(row=0, column=0, sticky="w", pady=5)
        self.code_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.code_entry.grid(row=0, column=1, pady=5, padx=5)
        # Derslik Adı
        tk.Label(left_frame, text="Derslik Adı:", font=("Arial", 10), bg="#f0f0f0").grid(row=1, column=0, sticky="w", pady=5)
        self.name_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.name_entry.grid(row=1, column=1, pady=5, padx=5)
        # Kapasite
        tk.Label(left_frame, text="Kapasite:", font=("Arial", 10), bg="#f0f0f0").grid(row=2, column=0, sticky="w", pady=5)
        self.capacity_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.capacity_entry.grid(row=2, column=1, pady=5, padx=5)
        # Sıra Sayısı (Boyuna)
        tk.Label(left_frame, text="Boyuna Sıra Sayısı (Satır):", font=("Arial", 10), bg="#f0f0f0").grid(row=3, column=0, sticky="w", pady=5)
        self.rows_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.rows_entry.grid(row=3, column=1, pady=5, padx=5)
        # Sütun Sayısı (Enine)
        tk.Label(left_frame, text="Enine Sıra Sayısı (Sütun):", font=("Arial", 10), bg="#f0f0f0").grid(row=4, column=0, sticky="w", pady=5)
        self.columns_entry = tk.Entry(left_frame, font=("Arial", 10), width=20)
        self.columns_entry.grid(row=4, column=1, pady=5, padx=5)
        # Sıra Tipi
        tk.Label(left_frame, text="Sıra Tipi:", font=("Arial", 10), bg="#f0f0f0").grid(row=5, column=0, sticky="w", pady=5)
        self.seat_type_combo = ttk.Combobox(left_frame, values=["2'li", "3'lü", "Tekli"], width=17, state="readonly") # readonly ekledik
        self.seat_type_combo.grid(row=5, column=1, pady=5, padx=5)
        self.seat_type_combo.set("2'li")
        # BUTONLAR
        button_frame = tk.Frame(left_frame, bg="#f0f0f0")
        button_frame.grid(row=6, column=0, columnspan=2, pady=15)
        add_btn = tk.Button(button_frame, text="Ekle", font=("Arial", 10, "bold"), bg="#2ecc71", fg="white", width=8, command=self.add_classroom)
        add_btn.pack(side="left", padx=5)
        update_btn = tk.Button(button_frame, text="Güncelle", font=("Arial", 10, "bold"), bg="#3498db", fg="white", width=8, command=self.update_classroom)
        update_btn.pack(side="left", padx=5)
        delete_btn = tk.Button(button_frame, text="Sil", font=("Arial", 10, "bold"), bg="#e74c3c", fg="white", width=8, command=self.delete_classroom)
        delete_btn.pack(side="left", padx=5)
        clear_btn = tk.Button(button_frame, text="Temizle", font=("Arial", 10), bg="#95a5a6", fg="white", width=8, command=self.clear_form)
        clear_btn.pack(side="left", padx=5)
        # --- Form elemanları sonu ---


        # ORTA TARAF - DERSLİK LİSTESİ
        middle_frame = tk.LabelFrame( # Değişiklik: right_frame -> middle_frame
            main_frame,
            text="Derslik Listesi",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        # Hem yatayda hem dikeyde yayılsın (fill="both", expand=True)
        middle_frame.pack(side="left", fill="both", expand=True, padx=10) # side="left" yaptık

        # Treeview (Aynı kalıyor)
        self.tree = ttk.Treeview(
            middle_frame,
            columns=("ID", "Kod", "Ad", "Kapasite", "Sıra", "Sütun", "Tip"),
            show="headings",
            height=20 # Yüksekliği ayarlayabilirsin
        )
        self.tree.heading("ID", text="ID")
        self.tree.heading("Kod", text="Derslik Kodu")
        self.tree.heading("Ad", text="Derslik Adı")
        self.tree.heading("Kapasite", text="Kapasite")
        self.tree.heading("Sıra", text="Boyuna(Satır)") # İsmi netleştirdik
        self.tree.heading("Sütun", text="Enine(Sütun)") # İsmi netleştirdik
        self.tree.heading("Tip", text="Sıra Tipi")
        self.tree.column("ID", width=40, anchor='center')
        self.tree.column("Kod", width=80, anchor='center')
        self.tree.column("Ad", width=120)
        self.tree.column("Kapasite", width=60, anchor='center')
        self.tree.column("Sıra", width=90, anchor='center') # Genişlettik
        self.tree.column("Sütun", width=90, anchor='center') # Genişlettik
        self.tree.column("Tip", width=70, anchor='center')
        scrollbar = ttk.Scrollbar(middle_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self.on_classroom_select)


        # SAĞ TARAF - GÖRSELLEŞTİRME ALANI (Yeni Eklendi)
        self.visualization_frame = tk.LabelFrame( # Yeni LabelFrame
            main_frame,
            text="Oturma Düzeni Önizleme",
            font=("Arial", 12, "bold"),
            bg="#f0f0f0",
            padx=10,
            pady=10
        )
        # Sadece dikeyde yayılsın ve sağa yaslansın
        self.visualization_frame.pack(side="right", fill="y", padx=(10, 0))

        # Canvas widget'ı oluştur
        # Genişlik ve yüksekliği ayarlayabilirsin
        self.canvas = tk.Canvas(self.visualization_frame, width=400, height=500, bg="white", relief="sunken", borderwidth=1)
        self.canvas.pack(fill="both", expand=True)


    # --- Diğer Fonksiyonlar (load_classrooms, add_, update_, delete_, clear_) ---
    # Bu fonksiyonlar genellikle aynı kalır, ama on_classroom_select güncellenecek

    def load_classrooms(self):
        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id, code, name, capacity, rows, columns, seat_type
                FROM classrooms
                WHERE department_id = ?
                ORDER BY code
            ''', (self.department_id,))

            classrooms = cursor.fetchall()

            for item in self.tree.get_children():
                self.tree.delete(item)

            for classroom in classrooms:
                self.tree.insert("", "end", values=classroom)

            conn.close()

            # İlk açılışta görselleştirmeyi temizle
            self.clear_visualization()

        except Exception as e:
            messagebox.showerror("Hata", f"Derslikler yüklenirken hata: {str(e)}")


    def on_classroom_select(self, event):
        selected = self.tree.selection()
        if not selected:
            # Seçim kalkarsa görselleştirmeyi temizle
            self.clear_visualization()
            self.selected_classroom = None # Seçili ID'yi de temizle
            return

        item = selected[0]
        values = self.tree.item(item, "values")

        # Formu doldur
        self.selected_classroom = values[0]  # ID
        self.code_entry.delete(0, tk.END)
        self.code_entry.insert(0, values[1]) # Kod
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, values[2]) # Ad
        self.capacity_entry.delete(0, tk.END)
        self.capacity_entry.insert(0, values[3]) # Kapasite
        self.rows_entry.delete(0, tk.END)
        self.rows_entry.insert(0, values[4]) # Boyuna Sıra (Satır)
        self.columns_entry.delete(0, tk.END)
        self.columns_entry.insert(0, values[5]) # Enine Sıra (Sütun)
        self.seat_type_combo.set(values[6]) # Sıra Tipi

        # Oturma düzenini çizdir (Yeni eklendi)
        try:
            rows = int(values[4])
            cols = int(values[5])
            seat_type = values[6]
            self.draw_seating_layout(rows, cols, seat_type)
        except (ValueError, IndexError):
            messagebox.showerror("Hata", "Seçili dersliğin sıra/sütun bilgileri geçersiz.")
            self.clear_visualization()


    def add_classroom(self):
        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        capacity = self.capacity_entry.get().strip()
        rows = self.rows_entry.get().strip()
        columns = self.columns_entry.get().strip()
        seat_type = self.seat_type_combo.get()

        if not all([code, name, capacity, rows, columns]):
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
            return

        try:
            # Sayısal değerleri kontrol et
            capacity_int = int(capacity)
            rows_int = int(rows)
            columns_int = int(columns)

            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO classrooms
                (code, name, capacity, rows, columns, seat_type, department_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (code, name, capacity_int, rows_int, columns_int, seat_type, self.department_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Derslik başarıyla eklendi!")
            self.clear_form() # Formu ve görselleştirmeyi temizle
            self.load_classrooms() # Listeyi yenile

        except ValueError:
             messagebox.showerror("Hata", "Kapasite, Sıra Sayısı ve Sütun Sayısı sayısal değer olmalıdır.")
        except Exception as e:
            messagebox.showerror("Hata", f"Derslik eklenirken hata: {str(e)}")


    def update_classroom(self):
        if not self.selected_classroom:
            messagebox.showwarning("Uyarı", "Lütfen güncellemek için bir derslik seçin!")
            return

        code = self.code_entry.get().strip()
        name = self.name_entry.get().strip()
        capacity = self.capacity_entry.get().strip()
        rows = self.rows_entry.get().strip()
        columns = self.columns_entry.get().strip()
        seat_type = self.seat_type_combo.get()

        if not all([code, name, capacity, rows, columns]):
            messagebox.showwarning("Uyarı", "Lütfen tüm alanları doldurun!")
            return

        try:
            # Sayısal değerleri kontrol et
            capacity_int = int(capacity)
            rows_int = int(rows)
            columns_int = int(columns)

            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE classrooms
                SET code = ?, name = ?, capacity = ?, rows = ?, columns = ?, seat_type = ?
                WHERE id = ? AND department_id = ?
            ''', (code, name, capacity_int, rows_int, columns_int, seat_type, self.selected_classroom, self.department_id))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Derslik başarıyla güncellendi!")
            self.clear_form()
            self.load_classrooms() # Listeyi ve potansiyel görselleştirmeyi yenile

        except ValueError:
             messagebox.showerror("Hata", "Kapasite, Sıra Sayısı ve Sütun Sayısı sayısal değer olmalıdır.")
        except Exception as e:
            messagebox.showerror("Hata", f"Derslik güncellenirken hata: {str(e)}")


    def delete_classroom(self):
        if not self.selected_classroom:
            messagebox.showwarning("Uyarı", "Lütfen silmek için bir derslik seçin!")
            return

        result = messagebox.askyesno("Onay", "Bu dersliği silmek istediğinizden emin misiniz?\n(Bu dersliğe atanmış sınavlar varsa sorun çıkabilir!)")
        if not result:
            return

        try:
            db = Database()
            conn = db.get_connection()
            cursor = conn.cursor()

            cursor.execute('DELETE FROM classrooms WHERE id = ?', (self.selected_classroom,))

            conn.commit()
            conn.close()

            messagebox.showinfo("Başarılı", "Derslik başarıyla silindi!")
            self.clear_form() # Formu ve görselleştirmeyi temizle
            self.load_classrooms() # Listeyi yenile

        except Exception as e:
            messagebox.showerror("Hata", f"Derslik silinirken hata: {str(e)}")


    def clear_form(self):
        self.selected_classroom = None
        self.code_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.capacity_entry.delete(0, tk.END)
        self.rows_entry.delete(0, tk.END)
        self.columns_entry.delete(0, tk.END)
        self.seat_type_combo.set("2'li")
        # Form temizlenince görselleştirmeyi de temizle
        self.clear_visualization()


    # --- Yeni Görselleştirme Fonksiyonları ---
    def clear_visualization(self):
        """Canvas üzerindeki tüm çizimleri temizler."""
        if self.canvas:
            self.canvas.delete("all")
            # İsteğe bağlı: Temizlendiğini belirten bir yazı eklenebilir
            # self.canvas.create_text(200, 250, text="Önizleme için listeden derslik seçin.", fill="gray")

    def draw_seating_layout(self, rows, cols, seat_type):
        """Verilen bilgilere göre Canvas üzerine oturma düzenini çizer."""
        self.clear_visualization() # Önce eski çizimi temizle

        if not rows or not cols or not self.canvas:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Padding (kenar boşlukları)
        padding = 20
        # Çizim alanı
        draw_width = canvas_width - 2 * padding
        draw_height = canvas_height - 2 * padding

        # Koltuk boyutları ve aralıkları
        # Koltukları sığdırmak için boyutları dinamik hesapla
        # Aralıkları da hesaba katalım (örneğin koltuk genişliğinin %20'si kadar)
        total_horizontal_space = cols # Her sütun için 1 birim
        if seat_type == "2'li":
            total_horizontal_space = cols * 2 + (cols - 1) * 0.5 # 2 koltuk + yarım koltukluk koridor
        elif seat_type == "3'lü":
            total_horizontal_space = cols * 3 + (cols - 1) * 0.5 # 3 koltuk + yarım koltukluk koridor
        # else "Tekli" için cols yeterli

        # Her bir koltuğun yaklaşık genişliği
        seat_width = draw_width / (total_horizontal_space * 1.2) # %20 aralık payı
        h_gap = seat_width * 0.2 # Yatay aralık

        # Sıra (row) yüksekliği
        seat_height = draw_height / (rows * 1.3) # %30 dikey aralık payı
        v_gap = seat_height * 0.3 # Dikey aralık

        # Boyutları minimum/maksimum ile sınırla (çok küçük veya çok büyük olmasın)
        seat_width = max(10, min(seat_width, 40))
        seat_height = max(10, min(seat_height, 40))
        h_gap = max(2, h_gap)
        v_gap = max(4, v_gap)

        # Sıra tipi (grup boyutu)
        seats_per_group = 1
        if seat_type == "2'li":
            seats_per_group = 2
        elif seat_type == "3'lü":
            seats_per_group = 3

        # Koridor genişliği (koltuk grubu arasına konulacak) - yarım koltuk genişliği gibi
        corridor_width = seat_width * 0.5

        # Çizime başla
        current_y = padding
        for r in range(rows):
            current_x = padding
            for c in range(cols):
                # Koltuk grubunu çiz
                for i in range(seats_per_group):
                    x1 = current_x
                    y1 = current_y
                    x2 = current_x + seat_width
                    y2 = current_y + seat_height
                    # Dikdörtgen çiz (fill: dolgu rengi, outline: kenar rengi)
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill="lightblue", outline="black")
                    # Opsiyonel: Koltuk numarasını yazdır (r+1, c+1, i+1 gibi)
                    # self.canvas.create_text(x1 + seat_width/2, y1 + seat_height/2, text=f"{r+1}-{c+1}-{i+1}", font=("Arial", 6))
                    current_x += seat_width + h_gap # Bir sonraki koltuk için x'i ilerlet

                # Gruplar arasına koridor ekle (son sütun hariç)
                if c < cols - 1:
                    current_x += corridor_width # Koridor boşluğu ekle

            current_y += seat_height + v_gap # Bir sonraki sıra için y'yi ilerlet

# --- Ana Çalıştırma Bloğu (Test için) ---
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw() # Ana test penceresini gizle
    # Örnek departman ID'si ile pencereyi aç
    app = ClassroomWindow(department_id=1)
    # add_sample_classrooms() # Eğer test verisi yoksa, örnek derslikleri ekle
    root.mainloop()