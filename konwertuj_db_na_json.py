# konwertuj_db_na_json.py
import sqlite3
import json
from datetime import datetime

def konwertuj_db_na_json(db_path="leki_ratownika.db", json_path="leki_ratownika.json"):
    """
    Konwertuje bazę SQLite na plik JSON
    
    Args:
        db_path: ścieżka do pliku bazy SQLite
        json_path: ścieżka do pliku wyjściowego JSON
    """
    
    print("=" * 60)
    print("KONWERTER DB -> JSON")
    print("=" * 60)
    
    try:
        # Połącz z bazą
        print(f"\n1. Łączenie z bazą: {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # Umożliwia dostęp po nazwach kolumn
        cursor = conn.cursor()
        print("   ✅ Połączono")
        
        # Sprawdź ile jest rekordów
        cursor.execute("SELECT COUNT(*) FROM leki")
        liczba_rekordow = cursor.fetchone()[0]
        print(f"   📊 Znaleziono {liczba_rekordow} rekordów")
        
        # Pobierz wszystkie dane
        print("\n2. Pobieranie danych...")
        cursor.execute("""
            SELECT 
                id, nazwa, substancja_czynna, dawka, postac, ean, kod_atc,
                dostepnosc, refundowany, cena_detaliczna, podmiot,
                wielkosc_opakowania, substancja_szukana, data_pobrania
            FROM leki 
            ORDER BY substancja_szukana, nazwa
        """)
        
        wszystkie_leki = cursor.fetchall()
        print(f"   ✅ Pobrano {len(wszystkie_leki)} rekordów")
        
        # Konwertuj na listę słowników
        print("\n3. Konwersja na JSON...")
        leki_lista = []
        
        for lek in wszystkie_leki:
            lek_dict = {
                "id": lek["id"],
                "nazwa": lek["nazwa"],
                "substancja_czynna": lek["substancja_czynna"],
                "dawka": lek["dawka"],
                "postac": lek["postac"],
                "ean": lek["ean"],
                "kod_atc": lek["kod_atc"],
                "dostepnosc": lek["dostepnosc"],
                "refundowany": bool(lek["refundowany"]) if lek["refundowany"] is not None else False,
                "cena_detaliczna": float(lek["cena_detaliczna"]) if lek["cena_detaliczna"] else None,
                "podmiot": lek["podmiot"],
                "wielkosc_opakowania": lek["wielkosc_opakowania"],
                "substancja_szukana": lek["substancja_szukana"],
                "data_pobrania": lek["data_pobrania"]
            }
            leki_lista.append(lek_dict)
        
        # Zapisz do JSON
        print(f"\n4. Zapis do pliku: {json_path}")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(leki_lista, f, ensure_ascii=False, indent=2)
        
        # Sprawdź rozmiar pliku
        import os
        rozmiar = os.path.getsize(json_path) / 1024  # w KB
        
        print(f"   ✅ Zapisano {len(leki_lista)} leków")
        print(f"   📦 Rozmiar pliku: {rozmiar:.2f} KB")
        
        # Podsumowanie
        print("\n" + "=" * 60)
        print("PODSUMOWANIE:")
        print(f"✅ Plik JSON: {json_path}")
        print(f"✅ Liczba leków: {len(leki_lista)}")
        
        # Dodatkowe statystyki
        cursor.execute("SELECT COUNT(DISTINCT substancja_szukana) FROM leki")
        substancje = cursor.fetchone()[0]
        print(f"✅ Unikalnych substancji: {substancje}")
        
        cursor.execute("SELECT COUNT(*) FROM leki WHERE ean IS NOT NULL AND ean != ''")
        z_ean = cursor.fetchone()[0]
        print(f"✅ Leki z kodem EAN: {z_ean}")
        
        # Zamknij połączenie
        conn.close()
        
        return leki_lista
        
    except FileNotFoundError:
        print(f"\n❌ BŁĄD: Nie znaleziono pliku {db_path}")
        print("   Najpierw uruchom kolektor_lekow.py aby zebrać dane")
        return None
    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        return None

def konwertuj_z_podzialem_na_substancje(db_path="leki_ratownika.db", json_path="leki_ratownika_grupowany.json"):
    """
    Konwertuje bazę na JSON, grupując leki według substancji
    """
    
    print("=" * 60)
    print("KONWERTER DB -> JSON (grupowany według substancji)")
    print("=" * 60)
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        print(f"\n1. Łączenie z bazą: {db_path}")
        cursor.execute("SELECT COUNT(*) FROM leki")
        liczba_rekordow = cursor.fetchone()[0]
        print(f"   📊 Znaleziono {liczba_rekordow} rekordów")
        
        # Pobierz wszystkie dane
        cursor.execute("""
            SELECT 
                id, nazwa, substancja_czynna, dawka, postac, ean, kod_atc,
                dostepnosc, refundowany, cena_detaliczna, podmiot,
                wielkosc_opakowania, substancja_szukana, data_pobrania
            FROM leki 
            ORDER BY substancja_szukana, nazwa
        """)
        
        # Grupuj według substancji
        print("\n2. Grupowanie według substancji...")
        leki_grupowane = {}
        
        for lek in cursor.fetchall():
            substancja = lek["substancja_szukana"]
            
            if substancja not in leki_grupowane:
                leki_grupowane[substancja] = []
            
            lek_dict = {
                "id": lek["id"],
                "nazwa": lek["nazwa"],
                "dawka": lek["dawka"],
                "postac": lek["postac"],
                "ean": lek["ean"],
                "kod_atc": lek["kod_atc"],
                "dostepnosc": lek["dostepnosc"],
                "refundowany": bool(lek["refundowany"]) if lek["refundowany"] is not None else False,
                "cena_detaliczna": float(lek["cena_detaliczna"]) if lek["cena_detaliczna"] else None,
                "podmiot": lek["podmiot"],
                "wielkosc_opakowania": lek["wielkosc_opakowania"]
            }
            leki_grupowane[substancja].append(lek_dict)
        
        # Zapisz do JSON
        print(f"\n3. Zapis do pliku: {json_path}")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(leki_grupowane, f, ensure_ascii=False, indent=2)
        
        import os
        rozmiar = os.path.getsize(json_path) / 1024
        
        print(f"   ✅ Zapisano {len(leki_grupowane)} grup substancji")
        print(f"   📦 Rozmiar pliku: {rozmiar:.2f} KB")
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("PODSUMOWANIE:")
        print(f"✅ Plik JSON: {json_path}")
        print(f"✅ Liczba substancji: {len(leki_grupowane)}")
        
        # Pokaż kilka przykładowych substancji
        print("\n📋 Przykładowe substancje w pliku:")
        for i, substancja in enumerate(list(leki_grupowane.keys())[:10], 1):
            liczba = len(leki_grupowane[substancja])
            print(f"   {i}. {substancja} - {liczba} leków")
        
        return leki_grupowane
        
    except FileNotFoundError:
        print(f"\n❌ BŁĄD: Nie znaleziono pliku {db_path}")
        return None
    except Exception as e:
        print(f"\n❌ BŁĄD: {e}")
        return None

def main():
    """Główna funkcja - wybór opcji konwersji"""
    
    print("\n" + "=" * 60)
    print("KONWERTER BAZY LEKÓW")
    print("=" * 60)
    print("\nWybierz format eksportu:")
    print("1. JSON - lista wszystkich leków")
    print("2. JSON - pogrupowany według substancji (zalecany)")
    print("3. Oba formaty")
    
    wybor = input("\nTwój wybór (1/2/3): ").strip()
    
    if wybor == "1":
        konwertuj_db_na_json()
    elif wybor == "2":
        konwertuj_z_podzialem_na_substancje()
    elif wybor == "3":
        konwertuj_db_na_json()
        print("\n")
        konwertuj_z_podzialem_na_substancje()
    else:
        print("❌ Nieprawidłowy wybór")
        return
    
    print("\n✅ Konwersja zakończona!")
    print("\n📁 Pliki zostały zapisane w bieżącym folderze.")

if __name__ == "__main__":
    main()