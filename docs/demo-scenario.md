# GarageReg Demo Forgatókönyv - "Golden Path"

## Áttekintés

Ez a dokumentum bemutatja a GarageReg rendszer teljes munkafolyamatát egy valós üzleti forgatókönyv szerint. A demo forgatókönyv egy "golden path" alapján mutatja be a rendszer főbb funkcióit: ügyfél kezeléstől a kapu ellenőrzéseken keresztül a hibajegy feldolgozásáig és munkalap generálásáig.

## Demo Adatok Struktúrája

### 1. Ügyfél (1 db)
**TechPark Business Center Kft.**
- Cím: 1117 Budapest, InfoPark sétány 1.
- Adószám: 12345678-2-41
- Cégjegyzékszám: 01-09-876543
- Kapcsolattartó: Kovács László (vezető)
- Telefon: +36 1 999 8877
- E-mail: kovacs.laszlo@techpark.hu

### 2. Telephelyek (2 db)

#### A) TechPark Északi Campus
- Cím: 1117 Budapest, InfoPark sétány 1/A
- Terület: 15,000 m²
- Koordináták: 47.4736° N, 19.0511° E
- Típus: Irodapark + gyártás

#### B) TechPark Déli Campus  
- Cím: 1117 Budapest, InfoPark sétány 1/B
- Terület: 8,500 m²
- Koordináták: 47.4720° N, 19.0515° E
- Típus: Logisztikai központ

### 3. Épületek (3 db)

#### Északi Campus:
- **Alfa Épület**: 4 szintes irodaház, 120 irodaegység
- **Béta Épület**: 2 szintes gyártócsarnok, 8 gyártóegység

#### Déli Campus:
- **Gamma Épület**: 1 szintes logisztikai csarnok, 25 raktárégység

### 4. Kapuk (10 db)

#### Alfa Épület (4 kapu):
1. **MAIN-ALF-001** - Főbejárat (automatikus üvegajtó)
2. **PARK-ALF-002** - Parkolóház bejárat (sorompó)  
3. **FIRE-ALF-003** - Tűzjelző kijárat (push bar ajtó)
4. **SERV-ALF-004** - Szerviz bejárat (kulcsos ajtó)

#### Béta Épület (3 kapu):
5. **PROD-BET-005** - Gyártócsarnok főbejárat (automatikus tolókapu)
6. **LOAD-BET-006** - Rakodó kapu (kézi emelőkapu) 
7. **EMRG-BET-007** - Vészhelyzeti kijárat (emergency exit)

#### Gamma Épület (3 kapu):
8. **DOCK-GAM-008** - Dokkoló kapu #1 (hydraulikus emelőkapu)
9. **DOCK-GAM-009** - Dokkoló kapu #2 (hydraulikus emelőkapu)
10. **YARD-GAM-010** - Udvar kapu (kétszárnyú tolókapu)

### 5. Ellenőrzések (2 db)

#### A) Havi Biztonsági Ellenőrzés
- **Kapu**: MAIN-ALF-001 (Alfa épület főbejárat)
- **Dátum**: 2024.10.04 09:00
- **Ellenőr**: Szabó Péter (jogosítvány: ELL-2024-0156)
- **Típus**: Rendszeres biztonsági ellenőrzés
- **Eredmény**: Kisebb hiba észlelve (kopott tömítés)

#### B) Negyedéves Karbantartási Ellenőrzés  
- **Kapu**: PROD-BET-005 (Béta épület gyártócsarnok)
- **Dátum**: 2024.10.04 14:30
- **Ellenőr**: Nagy Anna (jogosítvány: ELL-2024-0089)
- **Típus**: Megelőző karbantartási ellenőrzés
- **Eredmény**: Súlyos hiba (motor túlmelegedés)

### 6. Hibajegy → Munkalap Folyamat (1 db)

A Béta épület gyártócsarnok ellenőrzése során észlelt motor túlmelegedés probléma alapján:

#### Hibajegy
- **ID**: TICKET-2024-001
- **Prioritás**: Magas (üzemzavar)
- **Kategória**: Elektromos hiba
- **Leírás**: Automatikus tolókapu motorjánál túlmelegedés észlelhető. A kapu lassabban reagál, időnként megáll.
- **Helyszín**: TechPark Déli Campus, Béta épület, PROD-BET-005 kapu
- **Bejelentő**: Nagy Anna (ellenőr)
- **Státusz**: Aktív → Munkarendelés létrehozva

#### Munkalap (Work Order)
- **ID**: WO-2024-001  
- **Cím**: Motor túlmelegedés javítása - PROD-BET-005
- **Típus**: Javítás/csere
- **Technikus**: Molnár Gábor (jogosítvány: TECH-2024-0234)
- **Becsült időtartam**: 4 óra
- **Státusz**: Befejezve
- **Elvégzett munka**: 
  - Motor hűtőventillátor csere
  - Hő-szenzor kalibrálás
  - Működési teszt
- **Felhasznált alkatrészek**:
  - Hűtőventillátor (CAME-FAN-200W)
  - Hőmérséklet szenzor (TEMP-SENS-A1)

## Golden Path Forgatókönyv

### 1. Szakasz: Rendszer Felkészítés
```
Admin bejelentkezés → Demo adatok inicializálás → Dashboard áttekintés
```

### 2. Szakasz: Ügyfél és Infrastruktúra Kezelés  
```
Clients → TechPark létrehozás → Sites → Északi/Déli Campus → 
Buildings → Alfa/Béta/Gamma épületek → Gates → 10 kapu regisztrálás
```

### 3. Szakasz: Ellenőrzési Folyamat
```
Inspection Manager → Template kiválasztás → Kapu hozzárendelés →
Ellenőrzés végrehajtás → Problémák dokumentálás → Befejezés
```

### 4. Szakasz: Hibakezelés és Munkarendelés
```
Ticket Management → Új hibajegy → Prioritás beállítás → 
Work Order létrehozás → Technikus hozzárendelés → Munka végrehajtás
```

### 5. Szakasz: Dokumentum Generálás
```
PDF Reports → 3 dokumentum generálás:
1. Ellenőrzési jegyzőkönyv (Inspection Report) 
2. Munkalap (Work Order)
3. Befejezési riport (Completion Report)
```

## UI Navigációs Útvonal

### Főbb Képernyők és Átmenetek:

1. **Dashboard** (`/dashboard`)
   - Rendszer áttekintés
   - Aktív ellenőrzések
   - Nyitott hibajegyek

2. **Ügyfél Kezelés** (`/clients`)
   - TechPark ügyfél létrehozás
   - Kapcsolattartói adatok

3. **Telephely Kezelés** (`/sites`) 
   - Északi/Déli Campus létrehozás
   - Koordináták, címek

4. **Épület Kezelés** (`/buildings`)
   - Alfa, Béta, Gamma épületek
   - Szint és egység információk

5. **Kapu Kezelés** (`/gates`)
   - 10 kapu regisztrálás
   - QR kód generálás
   - Műszaki paraméterek

6. **Ellenőrzés Demo** (`/inspection-demo`)
   - Template alapú ellenőrzés
   - Valós idejű kitöltés
   - Automatikus mentés

7. **Hibajegy Rendszer** (`/tickets`)
   - Ticket létrehozás
   - Work Order generálás
   - Státusz követés

## Generálandó PDF Dokumentumok

### 1. Ellenőrzési Jegyzőkönyv (Inspection Report)
**Fájlnév**: `inspection-report-MAIN-ALF-001-20241004.pdf`

**Tartalom**:
- Kapu azonosító és műszaki adatok
- Ellenőrzés típusa és dátuma
- Ellenőr adatai és jogosítványa
- Checklist eredmények
- Észlelt problémák
- Fotó dokumentáció
- Javaslatok és következő lépések

### 2. Munkalap (Work Order Document)  
**Fájlnév**: `work-order-WO-2024-001.pdf`

**Tartalom**:
- Munkarendelés adatok
- Hibabejelentés részletei  
- Tervezett vs. tényleges munkaidő
- Technikus adatai
- Elvégzett munkálatok listája
- Felhasznált alkatrészek
- Minőségbiztosítási jóváhagyás

### 3. Befejezési Riport (Completion Report)
**Fájlnév**: `completion-report-WO-2024-001.pdf`

**Tartalom**:
- Projekt összefoglaló
- Problémamegoldás dokumentáció
- Költségkimutatás
- Tesztelési eredmények
- Garanciális információk
- Ügyfél visszajelzés
- Lezárási jóváhagyás

## Elfogadási Kritériumok

### ✅ Demo Végigjátszhatóság UI-ból
- [ ] Teljes navigációs útvonal követhető
- [ ] Minden demo adat megjelenik
- [ ] Nincsenek hibák vagy megszakítások
- [ ] Responsiv design minden képernyőn

### ✅ 3 PDF Dokumentum Generálás  
- [ ] Inspection Report PDF generálás sikeres
- [ ] Work Order PDF generálás sikeres
- [ ] Completion Report PDF generálás sikeres
- [ ] Minden PDF tartalma teljes és formázott
- [ ] PDF fájlok letölthetők és megnyithatók

### ✅ Funkcionális Teljeskörűség
- [ ] Teljes adatmodell reprezentálva
- [ ] Munkafoly szakadások nélkül
- [ ] Hibakezelés működik
- [ ] Audit trail rögzítés

## Következő Lépések

1. **Demo Adatok Generálás**: `demo_scenario_data.py` script létrehozása
2. **UI Komponensek**: Hiányzó oldal implementálás  
3. **PDF Szolgáltatások**: Template és generátor finomhangolás
4. **E2E Tesztelés**: Teljes forgatókönyv automatizálása
5. **Dokumentáció**: Felhasználói útmutató készítés

---

*Dokumentum verzió: 1.0*  
*Utolsó frissítés: 2024.10.04*  
*Szerző: GarageReg Development Team*