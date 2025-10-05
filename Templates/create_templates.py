import pandas as pd
import os

def create_course_template():
    """Ders listesi şablonu oluştur"""
    data = {
        'Ders Kodu': ['CSE101', 'CSE102', 'MATH101'],
        'Ders Adı': ['Programlama', 'Veri Yapıları', 'Matematik'],
        'Hoca': ['Dr. Ali Yılmaz', 'Dr. Ayşe Demir', 'Dr. Mehmet Kaya'],
        'Tip': ['Zorunlu', 'Zorunlu', 'Zorunlu']
    }
    
    df = pd.DataFrame(data)
    df.to_excel('templates/ders_listesi_sablonu.xlsx', index=False)
    print("✅ Ders listesi şablonu oluşturuldu!")

def create_student_template():
    """Öğrenci listesi şablonu oluştur"""
    data = {
        'Öğrenci No': ['260201001', '260201002', '260201003'],
        'Ad-Soyad': ['Ahmet Yılmaz', 'Ayşe Demir', 'Mehmet Kaya'],
        'Sınıf': ['1. Sınıf', '1. Sınıf', '1. Sınıf'],
        'Ders Kodu': ['CSE101', 'CSE101', 'CSE101']
    }
    
    df = pd.DataFrame(data)
    df.to_excel('templates/ogrenci_listesi_sablonu.xlsx', index=False)
    print("✅ Öğrenci listesi şablonu oluşturuldu!")

if __name__ == "__main__":
    # Templates klasörünü oluştur
    os.makedirs('templates', exist_ok=True)
    
    create_course_template()
    create_student_template()
    print("🎉 Tüm şablonlar hazır!")