# uzupelnij_brakujace.py
import requests
import time
import sqlite3
import json
from datetime import datetime

# TWOJ KLUCZ API
API_KEY = "cvlcXy_mnJGxwHimNLrgJ_Akot-oKvYjxEx3cMbkvew"

# Oryginalna lista substancji
ORIGINALNE_SUBSTANCJE = [
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

# Alternatywne nazwy dla substancji (zgodne z API)
ALTERNATYWNE_NAZWY = {
    "Adenozyna": ["Adenosine", "Adenosinum"],
    "Adrenalina": ["Epinephrine", "Adrenaline", "Adrenalini hydrochloridum"],
    "Amiodaron": ["Amiodarone", "Amiodaroni hydrochloridum"],
    "Atropina": ["Atropine", "Atropini sulfas"],
    "Budezonid": ["Budesonide", "Budetonide"],
    "Deksametazon": ["Dexamethasone", "Dexamethasonum"],
    "Diazepam": ["Diazepamum"],
    "Drotaweryna": ["Drotaverine", "Drotaverini hydrochloridum"],
    "Fentanyl": ["Fentanyl", "Fentanylum"],
    "Flumazenil": ["Flumazenilum"],
    "Furosemid": ["Furosemide", "Furosemidum"],
    "Glukagon": ["Glucagon", "Glucagonum"],
    "Glukoza": ["Glucose", "Glucosum", "Dextrose"],
    "Heparyna": ["Heparin", "Heparinum", "Heparin sodium"],
    "Hydrokortyzon": ["Hydrocortisone", "Hydrocortisonum"],
    "Hydroksyetyloskrobia": ["Hydroxyethyl starch", "HES", "Hydroxyethylamylum"],
    "Hydroksyzyna": ["Hydroxyzine", "Hydroxyzinum"],
    "Ibuprofen": ["Ibuprofenum", "Ibuprofen"],
    "Izosorbid monoazotanu": ["Isosorbide mononitrate", "Isosorbidi mononitras"],
    "Kaptopryl": ["Captopril", "Captoprilum"],
    "Ketoprofen": ["Ketoprofenum", "Ketoprofen"],
    "Klemastyna": ["Clemastine", "Clemastini hydrofumaras"],
    "Klonazepam": ["Clonazepam", "Clonazepamum"],
    "Klopidogrel": ["Clopidogrel", "Clopidogrelum"],
    "Kwas acetylosalicylowy": ["Acetylsalicylic acid", "Acidum acetylsalicylicum", "Aspirin"],
    "Kwas traneksamowy": ["Tranexamic acid", "Acidum tranexamicum"],
    "Lidokaina": ["Lidocaine", "Lidocainum", "Lidocaini hydrochloridum"],
    "Magnez": ["Magnesium", "Magnesium sulfate", "Magnesii sulfas"],
    "Mannitol": ["Mannitolum"],
    "Metamizol": ["Metamizole", "Metamizolum", "Metamizole sodium"],
    "Metoklopramid": ["Metoclopramide", "Metoclopramidum"],
    "Metoprolol": ["Metoprololum", "Metoprolol"],
    "Midazolam": ["Midazolamum"],
    "Morfina": ["Morphine", "Morphinum", "Morphini sulfas"],
    "Nalokson": ["Naloxone", "Naloxonum"],
    "Nitrogliceryna": ["Nitroglycerin", "Glyceryl trinitrate", "Nitroglycerinum"],
    "Noradrenalina": ["Norepinephrine", "Noradrenaline", "Norepinephrinum"],
    "Papaweryna": ["Papaverine", "Papaverinum"],
    "Paracetamol": ["Paracetamolum", "Acetaminophen"],
    "Prasugrel": ["Prasugrelum"],
    "Salbutamol": ["Salbutamolum", "Albuterol"],
    "Thiethylperazinum": ["Thiethylperazine", "Torecan"],
    "Tikagrelor": ["Ticagrelor", "Ticagrelorum"],
    "Tlen medyczny": ["Oxygen", "Oxygenium"],
    "Urapidyl": ["Urapidil", "Urapidilum"],
    "Wodorowęglan sodu": ["Sodium bicarbonate", "Natrii hydrogenocarbonas"],
    "Zelatyna modyfikowana": ["Gelatin", "Modified gelatin", "Succinylated gelatin"],
    "Plyn fizjologiczny": ["Sodium chloride", "Saline", "Natrii chloridum"],
    "Roztwor Ringera": ["Ringer solution", "Ringer's solution", "Ringer"]
}

def sprawdz_co_brakuje(db_path="leki_ratownika.db"):
    """Sprawdza które substancje z oryginalnej listy nie zostały znalezione"""
    
    print("=" * 70)
    print("ANALIZA BRAKUJĄCYCH SUBSTANCJI")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Pobierz substancje które są w bazie
    cursor.execute("SELECT DISTINCT substancja_szukana FROM leki WHERE substancja_szukana IS NOT NULL")
    znalezione = set([row[0] for row in cursor.fetchall()])
    
    # Znajdź brakujące
    brakujace = []
    for substancja in ORIGINALNE_SUBSTANCJE:
        if substancja not in znalezione:
            brakujace.append(substancja)
    
    # Pokaż wyniki
    print(f"\n📊 STATYSTYKI:")
    print(f"   ✅ Znaleziono: {len(znalezione)}/{len(ORIGINALNE_SUBSTANCJE)} substancji")
    print(f"   ❌ Brakuje: {len(brakujace)} substancji")
    
    if brakujace:
        print(f"\n❌ BRAKUJĄCE SUBSTANCJE:")
        for i, subst in enumerate(brakujace, 1):
            print(f"   {i:2d}. {subst}")
            # Pokaż proponowane alternatywy
            if subst in ALTERNATYWNE_NAZWY:
                alternatywy = ALTERNATYWNE_NAZWY[subst]
                print(f"       💡 Spróbuj: {', '.join(alternatywy[:3])}")
    
    conn.close()
    return brakujace

def testuj_wyszukiwanie(substancja, alternatywy):
    """Testuje różne nazwy dla danej substancji"""
    
    headers = {"X-API-Key": API_KEY}
    wyniki = {}
    
    print(f"\n🔍 Testowanie: {substancja}")
    
    # Testuj oryginalną nazwę
    url = f"https://drugsapi.miniporadnia.pl/v1/drugs/by-subst-page/{substancja}"
    try:
        response = requests.get(url, headers=headers, params={"page": 0, "size": 5}, timeout=10)
        if response.status_code == 200:
            dane = response.json()
            wyniki[substancja] = len(dane)
            print(f"   📝 '{substancja}': {len(dane)} leków")
        else:
            wyniki[substancja] = 0
            print(f"   ❌ '{substancja}': brak wyników")
    except:
        wyniki[substancja] = 0
        print(f"   ❌ '{substancja}': błąd zapytania")
    
    time.sleep(1)  # RPS=1
    
    # Testuj alternatywne nazwy
    for alt in alternatywy:
        url = f"https://drugsapi.miniporadnia.pl/v1/drugs/by-subst-page/{alt}"
        try:
            response = requests.get(url, headers=headers, params={"page": 0, "size": 5}, timeout=10)
            if response.status_code == 200:
                dane = response.json()
                wyniki[alt] = len(dane)
                if len(dane) > 0:
                    print(f"   ✅ '{alt}': {len(dane)} leków")
                else:
                    print(f"   ❌ '{alt}': brak wyników")
            else:
                wyniki[alt] = 0
        except:
            wyniki[alt] = 0
        
        time.sleep(1)  # RPS=1
    
    return wyniki

def pobierz_brakujace_substancje(brakujace, db_path="leki_ratownika.db"):
    """Pobiera brakujące substancje używając alternatywnych nazw"""
    
    print("\n" + "=" * 70)
    print("PONOWNE WYSZUKIWANIE BRAKUJĄCYCH SUBSTANCJI")
    print("=" * 70)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    nowe_leki = 0
    
    for substancja in brakujace:
        print(f"\n📌 Przetwarzanie: {substancja}")
        
        # Pobierz alternatywne nazwy
        alternatywy = ALTERNATYWNE_NAZWY.get(substancja, [])
        
        if not alternatywy:
            print(f"   ⚠️ Brak alternatywnych nazw dla {substancja}")
            continue
        
        # Testuj każdą alternatywę
        for alt in alternatywy:
            print(f"   🔄 Próba: {alt}")
            
            url = f"https://drugsapi.miniporadnia.pl/v1/drugs/by-subst-page/{alt}"
            page = 0
            size = 100
            
            while True:
                time.sleep(1)  # RPS=1
                
                try:
                    response = requests.get(
                        url, 
                        headers={"X-API-Key": API_KEY},
                        params={"page": page, "size": size},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        dane = response.json()
                        if not dane or len(dane) == 0:
                            break
                        
                        for lek in dane:
                            # Sprawdź czy lek już istnieje
                            cursor.execute("SELECT id FROM leki WHERE id = ?", (lek.get('id'),))
                            if not cursor.fetchone():
                                # Zapisz nowy lek
                                cursor.execute('''
                                    INSERT INTO leki 
                                    (id, nazwa, substancja_czynna, dawka, postac, ean, kod_atc,
                                     dostepnosc, refundowany, cena_detaliczna, podmiot,
                                     wielkosc_opakowania, substancja_szukana, data_pobrania)
                                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                                    substancja,
                                    datetime.now()
                                ))
                                nowe_leki += 1
                                print(f"       ✓ Dodano: {lek.get('nazwa')}")
                        
                        if len(dane) < size:
                            break
                        page += 1
                    
                    elif response.status_code == 429:
                        print(f"       ⏰ Limit RPS, czekam 5s...")
                        time.sleep(5)
                        continue
                    else:
                        break
                        
                except Exception as e:
                    print(f"       ❌ Błąd: {e}")
                    break
            
            # Jeśli znaleziono leki dla tej alternatywy, przejdź do następnej substancji
            cursor.execute("SELECT COUNT(*) FROM leki WHERE substancja_szukana = ?", (substancja,))
            if cursor.fetchone()[0] > 0:
                print(f"   ✅ Znaleziono leki dla {substancja} (używając '{alt}')")
                break
        
        conn.commit()
    
    conn.close()
    print(f"\n✅ Dodano {nowe_leki} nowych leków do bazy")
    return nowe_leki

def zapisz_raport(brakujace, wyniki_testow=None, filename="raport_brakujacych.json"):
    """Zapisuje raport brakujących substancji"""
    
    raport = {
        "data_generowania": datetime.now().isoformat(),
        "suma_substancji": len(ORIGINALNE_SUBSTANCJE),
        "brakujace_substancje": brakujace,
        "alternatywne_nazwy": {subst: ALTERNATYWNE_NAZWY.get(subst, []) for subst in brakujace}
    }
    
    if wyniki_testow:
        raport["wyniki_testow"] = wyniki_testow
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(raport, f, ensure_ascii=False, indent=2)
    
    print(f"\n📄 Raport zapisany jako: {filename}")

def main():
    """Główna funkcja"""
    
    print("\n" + "=" * 70)
    print("NARZĘDZIE DO UZUPEŁNIANIA BRAKUJĄCYCH LEKÓW")
    print("=" * 70)
    
    # Sprawdź co brakuje
    brakujace = sprawdz_co_brakuje()
    
    if not brakujace:
        print("\n✅ Wszystkie substancje zostały znalezione!")
        return
    
    print(f"\n🔧 Liczba brakujących substancji: {len(brakujace)}")
    
    # Opcje
    print("\nCo chcesz zrobić?")
    print("1. Tylko wyświetl raport brakujących substancji")
    print("2. Testuj alternatywne nazwy (bez zapisywania)")
    print("3. Spróbuj automatycznie uzupełnić brakujące dane")
    print("4. Pokaż szczegółowe propozycje dla każdej brakującej substancji")
    
    wybor = input("\nTwój wybór (1-4): ").strip()
    
    if wybor == "1":
        zapisz_raport(brakujace)
        
    elif wybor == "2":
        wyniki = {}
        for subst in brakujace[:5]:  # Tylko pierwsze 5 dla testu
            alternatywy = ALTERNATYWNE_NAZWY.get(subst, [])
            if alternatywy:
                wyniki[subst] = testuj_wyszukiwanie(subst, alternatywy)
            time.sleep(2)
        zapisz_raport(brakujace, wyniki)
        
    elif wybor == "3":
        print("\n⚠️ UWAGA: To może zająć kilka minut...")
        potwierdzenie = input("Czy na pewno chcesz kontynuować? (t/n): ").strip().lower()
        if potwierdzenie == 't':
            nowe = pobierz_brakujace_substancje(brakujace)
            print(f"\n✅ Uzupełniono bazę o {nowe} leków")
            
            # Pokaż aktualne statystyki
            conn = sqlite3.connect("leki_ratownika.db")
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(DISTINCT substancja_szukana) FROM leki")
            znalezione = cursor.fetchone()[0]
            print(f"📊 Aktualnie znaleziono: {znalezione}/{len(ORIGINALNE_SUBSTANCJE)} substancji")
            conn.close()
        else:
            print("Anulowano.")
            
    elif wybor == "4":
        print("\n📋 SZCZEGÓŁOWE PROPOZYCJE:")
        for subst in brakujace:
            print(f"\n🔹 {subst}")
            if subst in ALTERNATYWNE_NAZWY:
                print(f"   Proponowane nazwy do wyszukania:")
                for alt in ALTERNATYWNE_NAZWY[subst]:
                    print(f"   • {alt}")
            else:
                print(f"   ⚠️ Brak propozycji - sprawdź ręcznie w dokumentacji")
    
    else:
        print("❌ Nieprawidłowy wybór")

if __name__ == "__main__":
    main()