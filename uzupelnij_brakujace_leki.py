# uzupelnij_brakujace_leki.py
import json
import requests
import time
from datetime import datetime

# TWOJ KLUCZ API
API_KEY = "cvlcXy_mnJGxwHimNLrgJ_Akot-oKvYjxEx3cMbkvew"

# Alternatywne nazwy dla substancji (jak szukać w API)
ALTERNATYWNE_NAZWY = {
    "Adenozyna": ["Adenosine", "Adenosinum", "Adenocor"],
    "Adrenalina": ["Epinephrine", "Adrenaline", "Adrenalini hydrochloridum", "Adrenalina WZF"],
    "Atropina": ["Atropine", "Atropini sulfas", "Atropinum sulfuricum", "Atropina"],
    "Budezonid": ["Budesonide", "Budetonide", "Pulmicort"],
    "Deksametazon": ["Dexamethasone", "Dexamethasonum", "Dexaven"],
    "Drotaweryna": ["Drotaverine", "Drotaverini hydrochloridum", "No-Spa"],
    "Glukagon": ["Glucagon", "Glucagonum", "GlucaGen"],
    "Heparyna": ["Heparin", "Heparinum", "Heparin sodium", "Heparyna WZF"],
    "Hydrokortyzon": ["Hydrocortisone", "Hydrocortisonum", "Solu-Cortef"],
    "Hydroksyetyloskrobia": ["Hydroxyethyl starch", "HES", "Voluven", "Venofundin"],
    "Hydroksyzyna": ["Hydroxyzine", "Hydroxyzinum", "Atarax"],
    "Izosorbid monoazotanu": ["Isosorbide mononitrate", "Isosorbidi mononitras", "Isomak"],
    "Kaptopryl": ["Captopril", "Captoprilum"],
    "Klemastyna": ["Clemastine", "Clemastini hydrofumaras", "Tavegyl"],
    "Klonazepam": ["Clonazepam", "Clonazepamum", "Rivotril"],
    "Klopidogrel": ["Clopidogrel", "Clopidogrelum", "Plavix"],
    "Kwas traneksamowy": ["Tranexamic acid", "Acidum tranexamicum", "Exacyl"],
    "Lidokaina": ["Lidocaine", "Lidocainum", "Lidocaini hydrochloridum", "Lignocaine"],
    "Magnez": ["Magnesium", "Magnesium sulfate", "Magnesii sulfas"],
    "Metoklopramid": ["Metoclopramide", "Metoclopramidum"],
    "Morfina": ["Morphine", "Morphinum", "Morphini sulfas"],
    "Nalokson": ["Naloxone", "Naloxonum"],
    "Nitrogliceryna": ["Nitroglycerin", "Glyceryl trinitrate", "Nitroglycerinum"],
    "Noradrenalina": ["Norepinephrine", "Noradrenaline", "Norepinephrinum"],
    "Papaweryna": ["Papaverine", "Papaverinum"],
    "Plyn fizjologiczny": ["Sodium chloride", "Saline", "Natrii chloridum", "NaCl"],
    "Roztwor Ringera": ["Ringer solution", "Ringer's solution", "Ringer"],
    "Thiethylperazinum": ["Thiethylperazine", "Torecan"],
    "Tikagrelor": ["Ticagrelor", "Ticagrelorum", "Brilique"],
    "Tlen medyczny": ["Oxygen", "Oxygenium", "Medical oxygen"],
    "Urapidyl": ["Urapidil", "Urapidilum", "Ebrantil"],
    "Wodorowęglan sodu": ["Sodium bicarbonate", "Natrii hydrogenocarbonas"],
    "Zelatyna modyfikowana": ["Gelatin", "Modified gelatin", "Succinylated gelatin", "Geloplasma"]
}

def pobierz_leki_dla_substancji(substancja, alternatywy):
    """Próbuje pobrać leki dla substancji używając alternatywnych nazw"""
    
    headers = {"X-API-Key": API_KEY}
    wszystkie_leki = []
    
    print(f"\n🔍 Szukam: {substancja}")
    
    for alt in alternatywy[:3]:  # Sprawdź max 3 alternatywy
        print(f"   Próba: '{alt}'...")
        
        url = f"https://drugsapi.miniporadnia.pl/v1/drugs/by-subst-page/{alt}"
        page = 0
        size = 100
        
        while True:
            time.sleep(1)  # RPS=1
            
            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params={"page": page, "size": size},
                    timeout=30
                )
                
                if response.status_code == 200:
                    dane = response.json()
                    if not dane or len(dane) == 0:
                        break
                    
                    for lek in dane:
                        # Sprawdź czy to lek dla ludzi (nie weterynaryjny)
                        if lek.get('rodzajPrep') == 'ludzki':
                            wszystkie_leki.append(lek)
                            print(f"      ✓ {lek.get('nazwa')} - {lek.get('dawka')} (EAN: {lek.get('ean')})")
                    
                    if len(dane) < size:
                        break
                    page += 1
                    
                elif response.status_code == 429:
                    print(f"      ⏰ Limit RPS, czekam 5s...")
                    time.sleep(5)
                    continue
                else:
                    break
                    
            except Exception as e:
                print(f"      ❌ Błąd: {e}")
                break
        
        if wszystkie_leki:
            print(f"   ✅ Znaleziono {len(wszystkie_leki)} leków dla {substancja}")
            break
    
    return wszystkie_leki

def usun_puste_rekordy(json_path="leki_ratownika_grupowany.json"):
    """Usuwa puste rekordy (placeholdery z nullami)"""
    
    print("=" * 70)
    print("KROK 1: Usuwanie pustych rekordów")
    print("=" * 70)
    
    with open(json_path, 'r', encoding='utf-8') as f:
        dane = json.load(f)
    
    usuniete = 0
    czyste_dane = {}
    
    for substancja, leki in dane.items():
        # Filtruj tylko leki które mają nazwę (nie są null)
        dobre_leki = [lek for lek in leki if lek.get('nazwa') and lek.get('nazwa') != 'null']
        
        if dobre_leki:
            czyste_dane[substancja] = dobre_leki
        else:
            print(f"   ❌ {substancja}: usunięto {len(leki)} pustych rekordów")
            usuniete += len(leki)
    
    # Zapisz oczyszczone dane
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(czyste_dane, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Usunięto {usuniete} pustych rekordów")
    return czyste_dane

def uzupelnij_brakujace(json_path="leki_ratownika_grupowany.json"):
    """Uzupełnia brakujące substancje"""
    
    print("\n" + "=" * 70)
    print("KROK 2: Uzupełnianie brakujących substancji")
    print("=" * 70)
    
    # Wczytaj istniejące dane
    with open(json_path, 'r', encoding='utf-8') as f:
        dane = json.load(f)
    
    # Znajdź brakujące substancje
    brakujace = [s for s in ALTERNATYWNE_NAZWY.keys() if s not in dane or not dane[s]]
    
    print(f"\n📊 Brakuje {len(brakujace)} substancji:")
    for i, sub in enumerate(brakujace, 1):
        print(f"   {i:2d}. {sub}")
    
    if not brakujace:
        print("\n✅ Wszystkie substancje są już w bazie!")
        return dane
    
    # Pobierz dane dla brakujących
    nowe_dane = {}
    
    for substancja in brakujace:
        alternatywy = ALTERNATYWNE_NAZWY.get(substancja, [substancja])
        leki = pobierz_leki_dla_substancji(substancja, alternatywy)
        
        if leki:
            # Konwertuj na format zgodny z JSON
            leki_format = []
            for lek in leki:
                leki_format.append({
                    "id": lek.get('id'),
                    "nazwa": lek.get('nazwa'),
                    "dawka": lek.get('dawka'),
                    "postac": lek.get('postac'),
                    "ean": lek.get('ean'),
                    "kod_atc": lek.get('kodAtc'),
                    "dostepnosc": lek.get('katDostOpak'),
                    "refundowany": bool(lek.get('refund', 0)),
                    "cena_detaliczna": lek.get('cenaDetal'),
                    "podmiot": lek.get('podmOdpow'),
                    "wielkosc_opakowania": lek.get('wielkoscOpak')
                })
            nowe_dane[substancja] = leki_format
            print(f"\n✅ {substancja}: dodano {len(leki)} leków")
        else:
            print(f"\n⚠️ {substancja}: NIE znaleziono leków")
            nowe_dane[substancja] = []
        
        # Dodatkowa przerwa między substancjami
        if substancja != brakujace[-1]:
            print("   Czekam 2 sekundy...")
            time.sleep(2)
    
    # Połącz stare i nowe dane
    for substancja, leki in nowe_dane.items():
        if leki:  # tylko jeśli znaleziono leki
            dane[substancja] = leki
    
    # Zapisz zaktualizowane dane
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(dane, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 70)
    print("PODSUMOWANIE:")
    print(f"✅ Zaktualizowano plik: {json_path}")
    
    # Statystyki - poprawiona wersja (bez zagnieżdżonego with)
    with open(json_path, 'r', encoding='utf-8') as f:
        finalne = json.load(f)
    
    substancje_z_danymi = sum(1 for s, l in finalne.items() if l)
    print(f"✅ Substancje z danymi: {substancje_z_danymi}/50")
    
    return dane

def main():
    print("\n" + "=" * 70)
    print("NARZĘDZIE DO UZUPEŁNIANIA BRAKUJĄCYCH LEKÓW")
    print("=" * 70)
    
    print("\nTo narzędzie:")
    print("1. Usunie puste rekordy (placeholdery)")
    print("2. Pobierze prawdziwe dane dla brakujących substancji")
    print("3. Użyje alternatywnych nazw (np. 'Epinephrine' zamiast 'Adrenalina')")
    print("\n⚠️ UWAGA: Ze względu na limit RPS=1 proces może potrwać ~15-20 minut")
    
    potwierdzenie = input("\nCzy kontynuować? (t/n): ").strip().lower()
    if potwierdzenie != 't':
        print("Anulowano.")
        return
    
    # Krok 1: Usuń puste rekordy
    usun_puste_rekordy()
    
    # Krok 2: Uzupełnij brakujące
    uzupelnij_brakujace()
    
    print("\n✅ ZAKOŃCZONO!")
    print("Plik leki_ratownika_grupowany.json został zaktualizowany.")

if __name__ == "__main__":
    main()