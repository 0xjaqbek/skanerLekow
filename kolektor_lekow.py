# kolektor_lekow.py
import requests
import time
import json
import sqlite3
from datetime import datetime

# TWOJ KLUCZ API
API_KEY = "cvlcXy_mnJGxwHimNLrgJ_Akot-oKvYjxEx3cMbkvew"

# Lista substancji do zebrania
SUBSTANCJE = [
    "Adenozyna", "Adrenalina", "Amiodaron", "Atropina", "Budezonid",
    "Deksametazon", "Diazepam", "Drotaweryna", "Fentanyl", "Flumazenil",
    "Furosemid", "Glukagon", "Glukoza", "Heparyna", "Hydrokortyzon",
    "Hydroksyetyloskrobia", "Hydroksyzyna", "Ibuprofen", "Izosorbid monoazotanu",
    "Kaptopryl", "Ketoprofen", "Klemastyna", "Klonazepam", "Klopidogrel",
    "Kwas acetylosalicylowy", "Kwas traneksamowy", "Lidokaina", "Magnez",
    "Mannitol", "Metamizol", "Metoklopramid", "Metoprolol", "Midazolam",
    "Morfina", "Nalokson", "Nitrogliceryna", "Noradrenalina", "Papaweryna",
    "Paracetamol", "Prasugrel", "Salbutamol", "Thiethylperazinum",
    "Tikagrelor", "Tlen medyczny", "Urapidyl", "Wodorowęglan sodu",
    "Zelatyna modyfikowana", "Plyn fizjologiczny", "Roztwor Ringera"
]

def pobierz_leki_dla_substancji(substancja, klucz_api, strona=0, rozmiar=100):
    """Pobiera leki dla danej substancji"""
    
    url = f"https://drugsapi.miniporadnia.pl/v1/drugs/by-subst-page/{substancja}"
    params = {"page": strona, "size": rozmiar}
    headers = {"X-API-Key": klucz_api}
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print(f"  Limit RPS - czekam 5 sekund...")
            time.sleep(5)
            return pobierz_leki_dla_substancji(substancja, klucz_api, strona, rozmiar)
        else:
            print(f"  Blad {response.status_code}: {response.text}")
            return []
    except Exception as e:
        print(f"  Blad: {e}")
        return []

def stworz_baze():
    """Tworzy baze SQLite"""
    conn = sqlite3.connect('leki_ratownika.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS leki (
            id INTEGER PRIMARY KEY,
            nazwa TEXT,
            substancja_czynna TEXT,
            dawka TEXT,
            postac TEXT,
            ean TEXT,
            kod_atc TEXT,
            dostepnosc TEXT,
            refundowany INTEGER,
            cena_detaliczna REAL,
            podmiot TEXT,
            wielkosc_opakowania TEXT,
            substancja_szukana TEXT,
            data_pobrania TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_ean ON leki(ean)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_nazwa ON leki(nazwa)')
    
    conn.commit()
    return conn

def zapisz_lek(conn, lek, substancja_szukana):
    """Zapisuje lek do bazy"""
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT OR REPLACE INTO leki 
            (id, nazwa, substancja_czynna, dawka, postac, ean, kod_atc, 
             dostepnosc, refundowany, cena_detaliczna, podmiot, 
             wielkosc_opakowania, substancja_szukana)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            lek.get('id'),
            lek.get('nazwa'),
            lek.get('substCzynna'),
            lek.get('dawka'),
            lek.get('postac'),
            lek.get('ean'),
            lek.get('kodAtc'),
            lek.get('katDostOpak'),
            1 if lek.get('refund') else 0,
            lek.get('cenaDetal'),
            lek.get('podmOdpow'),
            lek.get('wielkoscOpak'),
            substancja_szukana
        ))
        conn.commit()
        return True
    except Exception as e:
        print(f"    Blad zapisu: {e}")
        return False

def main():
    print("=" * 70)
    print("KOLEKTOR LEKOW DLA RATOWNIKOW MEDYCZNYCH")
    print("=" * 70)
    
    # Sprawdz polaczenie
    print("\n1. Sprawdzanie polaczenia z API...")
    test_url = "https://drugsapi.miniporadnia.pl/v1/usage"
    headers = {"X-API-Key": API_KEY}
    
    try:
        test = requests.get(test_url, headers=headers, timeout=10)
        if test.status_code == 200:
            usage = test.json()
            print(f"   ✅ Polaczenie OK!")
            print(f"   Plan: {usage.get('planCode')}")
            print(f"   Wazny do: {usage.get('validTo')}")
            print(f"   Pozostalo zapytan: {usage.get('requestLimit', 0) - usage.get('requestsUsed', 0)}")
        else:
            print(f"   ❌ Blad autoryzacji! Status: {test.status_code}")
            return
    except Exception as e:
        print(f"   ❌ Blad polaczenia: {e}")
        return
    
    # Stworz baze
    print("\n2. Tworzenie bazy danych...")
    conn = stworz_baze()
    print("   ✅ Baza utworzona: leki_ratownika.db")
    
    # Zbieraj dane
    print(f"\n3. Rozpoczecie zbierania danych dla {len(SUBSTANCJE)} substancji...")
    print("   (UWAGA: Z powodu limitu RPS=1, proces potrwa ok. 30-40 minut)\n")
    
    wszystkie_leki = 0
    
    for i, substancja in enumerate(SUBSTANCJE, 1):
        print(f"[{i}/{len(SUBSTANCJE)}] {substancja}...")
        
        strona = 0
        liczba_lekow = 0
        
        while True:
            # Czekaj 1 sekunde (RPS=1)
            if strona > 0 or i > 1:
                time.sleep(1)
            
            dane = pobierz_leki_dla_substancji(substancja, API_KEY, strona, 100)
            
            if not dane or len(dane) == 0:
                break
            
            for lek in dane:
                if zapisz_lek(conn, lek, substancja):
                    liczba_lekow += 1
                    wszystkie_leki += 1
                    if lek.get('ean'):
                        print(f"    ✓ {lek.get('nazwa')} - {lek.get('dawka')}")
            
            if len(dane) < 100:
                break
                
            strona += 1
        
        print(f"    -> Znaleziono {liczba_lekow} lekow dla {substancja}")
        
        # Dodatkowa przerwa miedzy substancjami
        if i < len(SUBSTANCJE):
            time.sleep(2)
    
    # Podsumowanie
    print("\n" + "=" * 70)
    print("PODSUMOWANIE:")
    print(f"✅ Zebrano {wszystkie_leki} lekow")
    
    # Sprawdz statystyki
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(DISTINCT substancja_szukana) FROM leki')
    unikalne = cursor.fetchone()[0]
    print(f"✅ Substancji z danymi: {unikalne}/{len(SUBSTANCJE)}")
    
    cursor.execute('SELECT COUNT(*) FROM leki WHERE ean IS NOT NULL AND ean != ""')
    z_ean = cursor.fetchone()[0]
    print(f"✅ Lekow z kodem EAN: {z_ean}")
    
    # Zamknij baze
    conn.close()
    print("\n✅ BAZA GOTOWA! Mozesz teraz uzyc skanera.")
    print("📁 Plik bazy: leki_ratownika.db")

if __name__ == "__main__":
    main()