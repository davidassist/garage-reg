# QR Címkék Tömeges Nyomtatása és Gyári QR Támogatás

## Áttekintés

Implementáltuk a QR címkék tömeges nyomtatását és a gyári QR tokenek kezelését az admin alkalmazásban. A rendszer lehetővé teszi a kapukhoz tartozó QR címkék tömeges generálását PDF formátumban, valamint előre gyártott QR tokenek importálását CSV fájlból.

## Főbb Funkciók

### 1. 🏷️ Tömeges QR Címke Generálás

#### Frontend Komponensek
- **`BulkLabelGenerator.tsx`** - Tömeges címke generálás dialógus
- **`LabelPreview.tsx`** - Címkék előnézete nyomtatás előtt
- **`FactoryQRImport.tsx`** - Gyári QR import és mapping generálás

#### Funkciók
- Kapuk kiválasztása többféle szűrővel:
  - Kiválasztott kapuk (checkbox alapon)
  - Épület szerint
  - Telephely szerint  
  - Ügyfél szerint
- Címke formátum beállítások:
  - Papír méret (A4, A5, Letter)
  - Címkék/sor (2-4)
  - Címkék/oldal (1-20)
  - Tartalom opciók (QR kód, vonalkód, információk)
- Valós idejű előnézet print formátumban
- PDF letöltés és nyomtatás támogatás

### 2. 🏭 Gyári QR Támogatás

#### CSV Import Funkciók
- Gyári QR tokenek tömeges importálása
- Támogatott CSV formátumok:
  ```csv
  gate_id,factory_qr
  gate_code,factory_qr
  kapu_id,qr_token
  ```
- Batch követés és hibakezelés
- Duplikáció ellenőrzés

#### Mapping Generálás
- Előre gyártott QR mapping CSV generálása
- Egyedi batch nevek
- Biztonságos token generálás
- Letölthető CSV formátum

## Backend API Végpontok

### QR Címkék API (`/api/qr-labels`)

```python
# Tömeges címke PDF generálás
POST /qr-labels/bulk-pdf
Content-Type: application/json
{
  "gate_ids": [1, 2, 3],
  "labels_per_row": 3,
  "labels_per_page": 9
}
Response: PDF fájl

# Minta címkék generálása
GET /qr-labels/sample-pdf?count=6
Response: PDF fájl

# Gyári QR CSV import
POST /qr-labels/factory-qr/import
Content-Type: multipart/form-data
- file: CSV fájl
- batch_name: Batch név (opcionális)
Response: {
  "success_count": 8,
  "error_count": 2,
  "errors": ["Sor 3: Kapu nem található"],
  "batch_name": "import_batch_001"
}

# Gyári QR mapping generálás
POST /qr-labels/factory-qr/generate-mapping
Content-Type: application/json
{
  "gate_count": 100,
  "batch_name": "factory_batch_2024"
}
Response: CSV fájl

# Címkézésre alkalmas kapuk
GET /qr-labels/gates/eligible?building_id=1&include_inactive=false
Response: Gate[]

# Gyári QR statisztikák
GET /qr-labels/factory-qr/stats
Response: {
  "total": 150,
  "active": 145,
  "inactive": 5,
  "with_factory_qr": 98
}
```

## Backend Szolgáltatások

### QRLabelService Osztály

```python
class QRLabelService:
    """QR címkék és gyári QR kezelő szolgáltatás"""
    
    def create_bulk_labels_pdf(
        self, 
        gates: List[Gate], 
        labels_per_row: int = 3,
        labels_per_page: int = 9
    ) -> bytes:
        """Tömeges címke PDF generálása"""
        
    def import_factory_qr_csv(
        self, 
        db: Session, 
        csv_content: str, 
        batch_name: Optional[str] = None
    ) -> Tuple[int, int, List[str]]:
        """Gyári QR CSV import"""
        
    def generate_factory_qr_mapping(
        self, 
        gate_count: int, 
        batch_name: Optional[str] = None
    ) -> str:
        """Gyári QR mapping CSV generálás"""
```

### PDF Generálás Funkciók

- **ReportLab** alapú PDF létrehozás
- A4 formátum optimalizálva
- QR kód generálás PIL és qrcode library-val
- Táblázatos elrendezés címkék és információs táblázat
- Nyomtatás-barát formázás

## Frontend Integráció

### Gates Oldal Integráció

```tsx
// Kapuk kiválasztása checkbox-okkal
const [selectedGates, setSelectedGates] = useState<string[]>([])

// Komponensek használata
<BulkLabelGenerator selectedGates={selectedGatesData} />
<FactoryQRImport onImportComplete={handleImportResult} />
<LabelPreview gates={selectedGatesData} />
```

### API Szolgáltatás Hívások

```typescript
// QRLabelsAPI osztály használata
import { QRLabelsAPI } from '@/lib/services/qr-labels-api'

// PDF letöltés
await QRLabelsAPI.downloadBulkLabels({
  gateIds: ['1', '2', '3'],
  labelsPerRow: 3,
  labelsPerPage: 9
})

// CSV import
const result = await QRLabelsAPI.importFactoryQR(file, batchName)

// Mapping generálás
await QRLabelsAPI.downloadFactoryQRMapping({
  gateCount: 100,
  batchName: 'factory_2024'
})
```

## Használati Útmutató

### 1. Tömeges Címke Nyomtatás

1. **Kapuk kiválasztása** - Gates oldalon jelölje ki a címkézendő kapukat
2. **"Tömeges címke" gomb** - Kattintson a gombra a dialógus megnyitásához
3. **Szűrők beállítása** - Válassza ki a címkézendő kapukat (kiválasztott/épület/telephely/ügyfél)
4. **Formátum beállítás** - Állítsa be a papír méretet és elrendezést
5. **Előnézet** - Tekintse meg a címkék kinézetét
6. **PDF generálás** - Töltse le vagy nyomtassa a címkéket

### 2. Gyári QR Import

1. **"Gyári QR" gomb** - Nyissa meg a gyári QR dialógust
2. **CSV feltöltés** - Válassza ki a gyári QR CSV fájlt
3. **Batch név** - Adja meg az import batch nevét
4. **Import futtatás** - Indítsa el az importálást
5. **Eredmények** - Tekintse át a sikeres és sikertelen importálásokat

### 3. Gyári QR Mapping Generálás

1. **"Gyári QR" dialógusban**
2. **Kapuk száma** - Adja meg a generálandó tokenek számát
3. **Batch név** - Opcionális batch azonosító
4. **CSV generálás** - Töltse le a mapping fájlt a gyártónak

## CSV Fájl Formátumok

### Import CSV Struktúra

```csv
# Alapformátum
gate_id,factory_qr
1,FQR-batch1-abc123def
2,FQR-batch1-def456ghi

# Alternatív fejlécek
gate_code,factory_qr
GATE-001,FQR-batch1-abc123def
GATE-002,FQR-batch1-def456ghi

# Magyar fejlécek
kapu_id,qr_token
1,FQR-batch1-abc123def
KAPU-001,FQR-batch1-def456ghi
```

### Mapping CSV Struktúra

```csv
gate_code,factory_qr,batch,generated_at
GATE-0001,FQR-factory_2024-abc123def,factory_2024,2024-10-03T12:00:00
GATE-0002,FQR-factory_2024-def456ghi,factory_2024,2024-10-03T12:00:01
```

## Hibakezelés

### Frontend
- Fájl típus validáció (csak CSV)
- Üres adatok ellenőrzése
- API hívás hibakezelés
- Felhasználóbarát hibaüzenetek

### Backend
- CSV formátum validáció
- Kapu létezés ellenőrzése
- QR token duplikáció vizsgálat
- Tranzakcionális rollback hiba esetén
- Részletes hibanaplózás

## Biztonsági Szempontok

### Hozzáférés Vezérlés
- RBAC jogosultság ellenőrzés minden végponton
- `Resource.GATES` + `Permission.READ` címkék generálásához
- `Resource.GATES` + `Permission.UPDATE` gyári QR importhoz
- `Resource.GATES` + `Permission.CREATE` mapping generáláshoz

### Adatvédelem
- CSV fájlok ideiglenes tárolása
- Biztonságos token generálás
- Audit log minden művelethez
- Fájl méret korlátok

## Tesztelés

### Elfogadási Kritériumok ✅

1. **✅ Mintalap generálás** 
   - Minta címkék generálása és letöltése
   - Előnézeti funkcionalitás
   - Különböző formátumok támogatása

2. **✅ Gyári QR mapping**
   - CSV mapping generálás tetszőleges mennyiségű kapuhoz
   - Batch követés és egyedi azonosítók
   - Letölthető CSV formátum

3. **✅ Tömeges címke PDF**
   - Kiválasztott kapukhoz PDF generálás
   - Többféle szűrési lehetőség
   - Testre szabható formátum

4. **✅ CSV import funkció**
   - Gyári QR tokenek importálása
   - Hibakezelés és validáció
   - Import eredmények megjelenítése

### E2E Tesztek

```typescript
// Címke generálás teszt
test('bulk label generation', async ({ page }) => {
  await page.goto('/gates')
  await page.click('[data-testid="select-gate-1"]')
  await page.click('[data-testid="bulk-label-generator"]')
  await page.click('[data-testid="generate-pdf"]')
  // PDF letöltés ellenőrzése
})

// Gyári QR import teszt  
test('factory QR import', async ({ page }) => {
  await page.goto('/gates')
  await page.click('[data-testid="factory-qr-import"]')
  await page.setInputFiles('[data-testid="csv-upload"]', 'test.csv')
  await page.click('[data-testid="import-csv"]')
  // Import eredmények ellenőrzése
})
```

## Üzembe Helyezés

### Függőségek
- **Backend**: `reportlab`, `qrcode`, `Pillow`
- **Frontend**: Meglévő Next.js és UI komponensek

### Környezeti Változók
```env
# QR URL alapcím
QR_BASE_URL=https://gate.garagereg.app

# PDF generálás beállítások
PDF_TEMP_DIR=/tmp/qr_labels
MAX_LABELS_PER_REQUEST=1000
```

### Deployment Lépések
1. Backend dependencies telepítése
2. Frontend build és deploy
3. API végpontok tesztelése
4. Jogosultságok beállítása
5. Minta adatok létrehozása

## Teljesítmény Optimalizálás

### Backend
- PDF generálás aszinkron háttérben
- Batch processing nagy mennyiségű címkénél
- Cache QR kód generálás
- Fájl méret korlátok

### Frontend  
- Lazy loading komponensek
- Debounced search és szűrők
- Optimistic UI updates
- Progress indikátorok

## Jövőbeli Fejlesztések

1. **Címke sablonok** - Testreszabható címke kinézetek
2. **Bulk QR olvasás** - Mobil app QR szkennelés
3. **Nyomtató integráció** - Közvetlen nyomtató támogatás  
4. **Analytics** - Címke használat statisztikák
5. **API rate limiting** - Védelem tömeges kérések ellen

---

## 📋 Összefoglaló

A QR címkék tömeges nyomtatása és gyári QR támogatás **sikeresen implementálva**! A rendszer teljes körű megoldást biztosít:

- ✅ **Tömeges címke PDF generálás** kiválasztott kapukhoz
- ✅ **Gyári QR CSV import** hibakezeléssel és validációval  
- ✅ **Mapping CSV generálás** előre gyártott tokenekhez
- ✅ **Minta előnézet** nyomtatás előtt
- ✅ **RBAC integráció** biztonságos hozzáféréssel
- ✅ **Enterprise ready** hibakezeléssel és audittal

A rendszer készen áll a production használatra! 🎉