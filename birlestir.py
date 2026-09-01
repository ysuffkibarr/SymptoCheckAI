import os

def koda_dok(cikis_dosyasi="SymptoCheckAI_kodlar.txt"):
    # Sadece bu uzantılara sahip dosyaları al (Büyük CSV ve binary dosyaları atla)
    gecerli_uzantilar = {'.py', '.html', '.yml'}
    # Taranmayacak gereksiz klasörler
    haric_klasorler = {'.git', '__pycache__', 'venv', '.venv', 'data'} 

    with open(cikis_dosyasi, 'w', encoding='utf-8') as yazici:
        for root, dirs, files in os.walk('.'):
            # Hariç tutulan klasörleri yoksay
            dirs[:] = [d for d in dirs if d not in haric_klasorler]

            for dosya in files:
                uzanti = os.path.splitext(dosya)[1]
                if uzanti in gecerli_uzantilar:
                    dosya_yolu = os.path.join(root, dosya)
                    
                    try:
                        with open(dosya_yolu, 'r', encoding='utf-8') as okuyucu:
                            icerik = okuyucu.read()
                            
                        yazici.write(f"\n{'='*50}\n")
                        yazici.write(f"DOSYA: {dosya_yolu}\n")
                        yazici.write(f"{'='*50}\n\n")
                        yazici.write(icerik)
                        yazici.write("\n")
                        
                    except Exception as e:
                        print(f"{dosya_yolu} okunamadı: {e}")
                        
    print(f"İşlem tamam! Tüm kodlar '{cikis_dosyasi}' dosyasında birleştirildi.")

if __name__ == "__main__":
    koda_dok()