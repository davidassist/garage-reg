# Engineering Handbook

## Verzió és Frissítés
- **Verzió**: 1.0.0
- **Utolsó frissítés**: 2025-10-01
- **Következő felülvizsgálat**: 2025-12-01

## Tartalomjegyzék

1. [Kódstílus és Fejlesztési Konvenciók](#1-kódstílus-és-fejlesztési-konvenciók)
2. [Commit Konvenciók](#2-commit-konvenciók)
3. [Monorepo Könyvtárstruktúra](#3-monorepo-könyvtárstruktúra)
4. [Branch Stratégia](#4-branch-stratégia)
5. [CI/CD Alapelvek](#5-cicd-alapelvek)
6. [Biztonsági Alapelvek](#6-biztonsági-alapelvek)
7. [Adatvédelem és GDPR](#7-adatvédelem-és-gdpr)
8. [Domain Szótár](#8-domain-szótár)
9. [Szabványok és Referenciák](#9-szabványok-és-referenciák)
10. [Checklistek és Sablonok](#10-checklistek-és-sablonok)

---

## 1. Kódstílus és Fejlesztési Konvenciók

### 1.1 Általános Elvek
- **DRY (Don't Repeat Yourself)**: Ismétlődő kód elkerülése
- **SOLID elvek** betartása
- **Clean Code** elvek követése
- Konzisztens kódformázás minden projektben

### 1.2 Nyelvspecifikus Konvenciók

#### TypeScript/JavaScript
```typescript
// Interfészek nagy I-vel kezdődnek
interface IGateController {
  id: string;
  status: GateStatus;
  lastMaintenance: Date;
}

// Enum-ok PascalCase
enum GateStatus {
  OPEN = 'open',
  CLOSED = 'closed',
  MOVING = 'moving',
  ERROR = 'error'
}

// Függvények camelCase
const validateGateOperation = (gateId: string): boolean => {
  // Implementáció
};
```

#### C# (.NET)
```csharp
// Publikus tulajdonságok PascalCase
public class GateController
{
    public string Id { get; set; }
    public GateStatus Status { get; set; }
    
    // Privát mezők underscore előtaggal
    private readonly ILogger _logger;
    
    // Metódusok PascalCase
    public async Task<bool> ValidateOperationAsync(string gateId)
    {
        // Implementáció
    }
}
```

### 1.3 Dokumentáció
- **JSDoc/XMLDoc** használata minden publikus API-hoz
- README.md minden projekt gyökerében
- Inline kommentek csak bonyolult logikánál

---

## 2. Commit Konvenciók

### 2.1 Conventional Commits Format
```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

### 2.2 Típusok
- **feat**: Új funkció
- **fix**: Hibjavítás
- **docs**: Dokumentáció változás
- **style**: Formázás, whitespace
- **refactor**: Kód átstrukturálás
- **test**: Tesztek hozzáadása/módosítása
- **chore**: Build, dependency frissítések

### 2.3 Scope-ok (kapukarbantartás specifikus)
- **gate**: Kapu vezérlés
- **maintenance**: Karbantartási funkciók
- **safety**: Biztonsági rendszerek
- **auth**: Authentikáció/Authorizáció
- **api**: API változások
- **db**: Adatbázis változások

### 2.4 Példák
```
feat(gate): add emergency stop functionality
fix(safety): resolve photocell detection issue
docs(maintenance): update service checklist template
refactor(api): restructure gate controller endpoints
```

---

## 3. Monorepo Könyvtárstruktúra

```
garagereg/
├── apps/                           # Alkalmazások
│   ├── web-client/                 # Frontend React app
│   ├── mobile-app/                 # React Native app
│   └── admin-panel/                # Admin interface
├── services/                       # Backend szolgáltatások
│   ├── api-gateway/                # API Gateway
│   ├── gate-service/               # Kapu vezérlés
│   ├── maintenance-service/        # Karbantartás
│   ├── auth-service/               # Authentikáció
│   └── notification-service/       # Értesítések
├── packages/                       # Shared könyvtárak
│   ├── shared-types/               # Közös TypeScript típusok
│   ├── ui-components/              # UI komponensek
│   ├── utils/                      # Segédfüggvények
│   └── constants/                  # Konstansok
├── infrastructure/                 # Infrastruktúra kód
│   ├── docker/                     # Docker fájlok
│   ├── k8s/                        # Kubernetes manifests
│   └── terraform/                  # Infrastructure as Code
├── docs/                          # Dokumentáció
│   ├── api/                       # API dokumentáció
│   ├── architecture/              # Architektúra diagramok
│   └── deployment/                # Deployment útmutatók
├── tools/                         # Fejlesztői eszközök
│   ├── scripts/                   # Build/deploy scriptek
│   └── generators/                # Kód generátorok
└── tests/                         # E2E és integrációs tesztek
    ├── e2e/                       # End-to-end tesztek
    └── integration/               # Integrációs tesztek
```

---

## 4. Branch Stratégia

### 4.1 Trunk-based Development
- **main**: Production-ready kód
- **feature/***: Új funkciók fejlesztése
- **hotfix/***: Sürgős production javítások
- **release/***: Release előkészítés (opcionális)

### 4.2 Branch Naming Convention
```
feature/gate-emergency-stop
feature/maintenance-scheduling
hotfix/safety-sensor-timeout
release/v2.1.0
```

### 4.3 Pull Request (PR) Folyamat
1. **Branch létrehozása** main-ből
2. **Fejlesztés** kis, atomi commit-okkal
3. **PR készítése** template alapján
4. **Code Review** minimum 2 reviewer
5. **CI/CD pipeline** sikeres lefutása
6. **Merge** squash commit-tal

### 4.4 PR Template
```markdown
## Változások leírása
<!-- Rövid leírás a változásokról -->

## Típus
- [ ] Bugfix
- [ ] Új funkció
- [ ] Breaking change
- [ ] Dokumentáció

## Tesztelés
- [ ] Unit tesztek frissítve
- [ ] Integration tesztek futtatva
- [ ] Manuális tesztelés elvégezve

## Checklist
- [ ] Kód megfelel a style guide-nak
- [ ] Self-review elvégezve
- [ ] Dokumentáció frissítve
```

---

## 5. CI/CD Alapelvek

### 5.1 Pipeline Szakaszok
1. **Validate**: Linting, formázás ellenőrzés
2. **Test**: Unit, integration tesztek
3. **Build**: Alkalmazások build-elése
4. **Security**: Vulnerability scan, SAST/DAST
5. **Deploy**: Staging/Production deployment

### 5.2 Deployment Stratégia
- **Blue-Green Deployment** production környezetben
- **Feature Flags** új funkciók fokozatos bevezetéséhez
- **Canary Releases** kritikus változásokhoz
- **Rollback** automatikus sikertelen deployment esetén

### 5.3 Monitoring és Alerting
- **Health Checks** minden service-hez
- **Metrics Collection** (Prometheus/Grafana)
- **Log Aggregation** (ELK Stack)
- **Alert Rules** kritikus hibákra

---

## 6. Biztonsági Alapelvek

### 6.1 Authentication és Authorization

#### 6.1.1 Argon2id Paraméterek
```typescript
const ARGON2_CONFIG = {
  type: argon2.argon2id,
  memoryCost: 65536,      // 64 MiB
  timeCost: 3,            // 3 iterations
  parallelism: 4,         // 4 threads
  hashLength: 32          // 32 bytes output
};
```

#### 6.1.2 JWT Konfiguráció
```typescript
const JWT_CONFIG = {
  accessTokenTTL: '15m',      // 15 perc
  refreshTokenTTL: '7d',      // 7 nap
  issuer: 'garagereg-api',
  audience: 'garagereg-client',
  algorithm: 'RS256'          // RSA256 aláírás
};
```

### 6.2 CSRF Védelem
- **SameSite cookies** strict módban
- **CSRF tokens** minden state-changing művelethez
- **Double Submit Cookie** pattern használata

### 6.3 Rate Limiting
```typescript
const RATE_LIMITS = {
  authentication: {
    windowMs: 15 * 60 * 1000,  // 15 perc
    max: 5                      // Max 5 próbálkozás
  },
  api: {
    windowMs: 60 * 1000,       // 1 perc
    max: 100                   // Max 100 kérés
  },
  gateOperation: {
    windowMs: 60 * 1000,       // 1 perc
    max: 10                    // Max 10 kapu művelet
  }
};
```

### 6.4 Input Validáció
- **Zod/Joi** schema validáció minden input-ra
- **Sanitization** XSS védelem
- **Parameter validation** minden endpoint-on
- **File upload** restrictions és virus scan

### 6.5 Audit Logging
```typescript
interface AuditLogEntry {
  timestamp: Date;
  userId: string;
  action: string;
  resource: string;
  resourceId?: string;
  ipAddress: string;
  userAgent: string;
  result: 'success' | 'failure';
  metadata?: Record<string, any>;
}
```

### 6.6 Security Headers
```typescript
const SECURITY_HEADERS = {
  'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
  'X-Content-Type-Options': 'nosniff',
  'X-Frame-Options': 'DENY',
  'X-XSS-Protection': '1; mode=block',
  'Content-Security-Policy': "default-src 'self'",
  'Referrer-Policy': 'strict-origin-when-cross-origin'
};
```

---

## 7. Adatvédelem és GDPR

### 7.1 PII (Personally Identifiable Information) Kategóriák

#### 7.1.1 Magas Kockázat
- **Teljes név**
- **Email cím**
- **Telefonszám**
- **Fizikai cím**
- **IP cím** (session context-ben)

#### 7.1.2 Közepes Kockázat
- **Felhasználói ID**
- **Device ID**
- **Munkaszám**

### 7.2 Log Retention Szabályok
```typescript
const LOG_RETENTION = {
  audit: '7 years',           // Audit logok
  application: '1 year',      // Alkalmazás logok
  security: '3 years',        // Biztonsági logok
  performance: '90 days',     // Teljesítmény metrikák
  debug: '30 days'            // Debug információk
};
```

### 7.3 Adatmaszkolás Szabályok
```typescript
const DATA_MASKING = {
  email: (email: string) => {
    const [local, domain] = email.split('@');
    return `${local.charAt(0)}***@${domain}`;
  },
  
  phone: (phone: string) => {
    return phone.replace(/(\d{2})(\d{3})(\d{4})/, '$1***$3');
  },
  
  address: (address: string) => {
    // Csak város és irányítószám megjelenítése
    return address.replace(/^.*(?=\d{4}\s+\w+)/, '*** ');
  }
};
```

### 7.4 GDPR Jogok Implementáció

#### 7.4.1 Adathordozhatóság (Data Portability)
```typescript
interface DataExportRequest {
  userId: string;
  requestDate: Date;
  format: 'json' | 'xml' | 'csv';
  includeHistorical: boolean;
}
```

#### 7.4.2 Törlési Jog (Right to Erasure)
```typescript
interface DataDeletionRequest {
  userId: string;
  requestDate: Date;
  retainAuditTrail: boolean;
  anonymizeData: boolean;
}
```

---

## 8. Domain Szótár

### 8.1 Kapurendszer Komponensek

| Magyar | English | Leírás |
|--------|---------|--------|
| Kapu | Gate | Főbejárati/garázs kapu |
| Vezérlő | Controller | Kapu vezérlő egység |
| Motor | Motor/Drive | Kapu hajtómotor |
| Élvédelem | Edge Protection | Biztonsági élvédelem |
| Fotocella | Photocell | Optikai biztonsági érzékelő |
| Vészleállító | Emergency Stop | Vészhelyzeti leállító gomb |
| Távvezérlő | Remote Control | Rádiós távvezérlő |
| Indukciós hurok | Induction Loop | Járműérzékelő hurok |
| Korlát | Barrier | Sorompó típusú kapu |
| Szárny | Wing/Leaf | Kapu szárny |

### 8.2 Karbantartási Terminológia

| Magyar | English | Leírás |
|--------|---------|--------|
| Munkalap | Work Order | Karbantartási munkalap |
| Jegyzőkönyv | Protocol/Report | Karbantartási jegyzőkönyv |
| Ellenőrzés | Inspection | Rendszeres ellenőrzés |
| Javítás | Repair | Hibák javítása |
| Megelőző karbantartás | Preventive Maintenance | Ütemezett karbantartás |
| Hibaelhárítás | Troubleshooting | Hibakeresés és elhárítás |
| Alkatrészcsere | Parts Replacement | Alkatrészek cseréje |
| Beállítás | Adjustment | Rendszer beállításai |
| Kalibrálás | Calibration | Érzékelők kalibrálása |
| Teszt | Test | Működési próbák |

### 8.3 Biztonsági Fogalmak

| Magyar | English | Leírás |
|--------|---------|--------|
| Biztonsági kategória | Safety Category | EN 954-1 szerinti kategóriák |
| Teljesítményszint | Performance Level | EN ISO 13849-1 PLa-PLe |
| Biztonsági integritási szint | Safety Integrity Level | IEC 61508 SIL1-SIL4 |
| Veszélyhelyzet | Hazardous Situation | Potenciálisan veszélyes állapot |
| Kockázatelemzés | Risk Assessment | Biztonsági kockázatok felmérése |
| Védőberendezés | Safety Device | Biztonsági védőeszközök |

### 8.4 Állapotok és Működési Módok

| Magyar | English | Kód | Leírás |
|--------|---------|-----|--------|
| Zárt | Closed | CLS | Kapu teljesen zárt |
| Nyitott | Open | OPN | Kapu teljesen nyitott |
| Nyitás | Opening | OPG | Nyitási folyamat |
| Zárás | Closing | CLG | Zárási folyamat |
| Megállt | Stopped | STP | Mozgás leállítva |
| Hiba | Error | ERR | Hibás működés |
| Karbantartás | Maintenance | MNT | Karbantartási mód |
| Vészhelyzet | Emergency | EMG | Vészhelyzeti állapot |

---

## 9. Szabványok és Referenciák

### 9.1 Európai Szabványok

#### 9.1.1 EN 13241 - Ipari, kereskedelmi és garázs kapuk és ajtók
**Hivatkozás**: EN 13241-1:2003+A2:2016 - Termékszabvány - 1. rész: Biztonsági követelmények nélküli termékek

**Főbb követelmények**:
- Mechanikai szilárdság és stabilitás
- Tűzbiztonság
- Higiénia, egészség és környezetvédelem
- Használat biztonsága
- Zajvédelem
- Energiatakarékosság és hőmegtartás

**TODO**: Frissíteni a legújabb 2023-as verzióra

#### 9.1.2 EN 12453:2017+A1:2021 - Ipari és kereskedelmi kapuk biztonsága
**Hivatkozás**: EN 12453:2017+A1:2021 - Használat biztonsága - Követelmények

**Biztonsági kategóriák**:
```
Kategória A: Korlátozott hozzáférés szakképzett személyzet számára
Kategória B: Korlátozott hozzáférés ismert személyzet számára  
Kategória C: Korlátlan hozzáférés nyilvános használatra
```

**Aktiválási típusok**:
- Típus 1: Ember által működtetett vezérlés (tartós nyomás)
- Típus 2: Ember által működtetett vezérlés (impulzus)
- Típus 3: Automatikus működtetés

#### 9.1.3 EN 12604:2017+A1:2020 - Mechanikus szempontok
**Hivatkozás**: EN 12604:2017+A1:2020 - Mechanikus szempontok - Követelmények

**Főbb területek**:
- Mechanikus vezérlés és működtetés
- Kézi erő alkalmazás követelményei
- Tartalék működtetési rendszerek
- Mechanikus biztonsági berendezések

### 9.2 Nemzetközi Szabványok

#### 9.2.1 ISO 13849-1 - Biztonsági vezérlőrendszerek
**Teljesítményszintek (Performance Levels)**:
- **PLa**: Alacsony kockázat
- **PLb**: Kis kockázat  
- **PLc**: Közepes kockázat
- **PLd**: Nagy kockázat
- **PLe**: Nagyon nagy kockázat

#### 9.2.2 IEC 61508 - Funkcionális biztonság
**SIL Szintek**:
- **SIL 1**: 10⁻¹ - 10⁻² hibaarány
- **SIL 2**: 10⁻² - 10⁻³ hibaarány
- **SIL 3**: 10⁻³ - 10⁻⁴ hibaarány
- **SIL 4**: 10⁻⁴ - 10⁻⁵ hibaarány

### 9.3 Magyar Szabványok

#### 9.3.1 MSZ EN 12453
**Státusz**: Nemzeti átvétel az EN 12453:2017+A1:2021 alapján
**Hatályba lépés**: 2022-04-01

---

## 10. Checklistek és Sablonok

### 10.1 Karbantartási Checklist Sablon

```markdown
# Karbantartási Checklist - {{GATE_TYPE}}

**Kapu azonosító**: {{GATE_ID}}
**Dátum**: {{DATE}}
**Technikus**: {{TECHNICIAN_NAME}}
**Típus**: {{MAINTENANCE_TYPE}}

## Vizuális Ellenőrzés
- [ ] Kapu szerkezet állapota
- [ ] Vezetősínek tisztasága
- [ ] Kábelezés épségének ellenőrzése
- [ ] Biztonsági matricák olvashatósága

## Mechanikus Elemek
- [ ] Motor működése ({{MOTOR_TYPE}})
- [ ] Hajtáslánc/fogaskerék ellenőrzése
- [ ] Kenés szükségessége
- [ ] Csapágyak állapota

## Biztonsági Rendszerek
- [ ] Fotocellák működése (TX/RX párok)
- [ ] Élvédelem tesztje
- [ ] Vészleállító gomb működése
- [ ] Indukciós hurok kalibrálása

## Elektronikus Rendszerek  
- [ ] Vezérlő panel működése
- [ ] Távirányítók tesztje ({{REMOTE_COUNT}} db)
- [ ] Pozíció érzékelők
- [ ] Kapcsolati erő mérése

## Beállítások
- [ ] Nyitási/zárási idők
- [ ] Erőhatárok beállítása
- [ ] Fotocella késleltetések
- [ ] Automatikus zárás időzítése

## Tesztek
- [ ] Teljes ciklus teszt (5x)
- [ ] Biztonsági funkciók tesztje
- [ ] Vészhelyzeti működés
- [ ] Kézi override teszt

## Megjegyzések
{{NOTES}}

## Következő Karbantartás
**Tervezett dátum**: {{NEXT_MAINTENANCE}}
**Speciális figyelem**: {{SPECIAL_ATTENTION}}

---
**Technikus aláírás**: ________________
**Ügyfél aláírás**: ________________
```

### 10.2 Hibabejelentés Sablon

```markdown
# Hibabejelentés - {{INCIDENT_ID}}

## Alapadatok
- **Bejelentés dátuma**: {{REPORT_DATE}}
- **Kapu azonosító**: {{GATE_ID}}
- **Helyszín**: {{LOCATION}}
- **Bejelentő**: {{REPORTER_NAME}}

## Hiba Leírása
**Tünetek**: {{SYMPTOMS}}

**Hibaüzenet**: {{ERROR_MESSAGE}}

**Körülmények**: {{CIRCUMSTANCES}}

## Sürgősségi Kategória
- [ ] Kritikus (teljes leállás)
- [ ] Magas (biztonsági kockázat)
- [ ] Közepes (funkcionalitás korlátozás)
- [ ] Alacsony (kisebb kellemetlenség)

## Első Intézkedések
{{IMMEDIATE_ACTIONS}}

## Eszkaláció
- [ ] Helyszíni technikus
- [ ] Ügyeletes mérnök
- [ ] Gyártó támogatás
- [ ] Külső szakértő

---
**Státusz**: {{STATUS}}
**Hozzárendelt technikus**: {{ASSIGNED_TECHNICIAN}}
**Becsült javítási idő**: {{ESTIMATED_REPAIR_TIME}}
```

### 10.3 Code Review Checklist

```markdown
# Code Review Checklist

## Funkcionalitás
- [ ] Kód megfelel a követelményeknek
- [ ] Edge case-ek kezelve
- [ ] Error handling megfelelő
- [ ] Performance optimális

## Biztonság
- [ ] Input validáció implementálva
- [ ] SQL injection védelem
- [ ] XSS védelem
- [ ] Authentication/Authorization ellenőrzés

## Kódminőség
- [ ] DRY elv betartása
- [ ] SOLID elvek követése
- [ ] Érthető névadás
- [ ] Megfelelő kommentezés

## Tesztek
- [ ] Unit tesztek írva
- [ ] Integration tesztek frissítve
- [ ] Test coverage megfelelő (>80%)
- [ ] Happy path és edge case-ek tesztelve

## Dokumentáció
- [ ] API dokumentáció frissítve
- [ ] README.md aktualizálva
- [ ] Changelog bejegyzés
- [ ] Migration scriptek (ha szükséges)
```

---

## TODO Lista

### Magas Prioritás
- [ ] **Biztonsági audit** elvégzése külső céggel
- [ ] **Penetration testing** webalkalmazásra
- [ ] **GDPR compliance audit** jogi szakértővel
- [ ] **Disaster Recovery Plan** kidolgozása

### Közepes Prioritás  
- [ ] **Performance benchmark** minden service-re
- [ ] **Monitoring dashboard** fejlesztése
- [ ] **Automated testing** pipeline bővítése
- [ ] **Documentation review** negyedévente

### Alacsony Prioritás
- [ ] **Developer onboarding** process dokumentálása
- [ ] **Architecture decision records** (ADR) bevezetése
- [ ] **Code quality metrics** bevezetése
- [ ] **Technical debt** tracking implementálása

---

## Kapcsolattartás és Felelősök

### Dokumentum Karbantartás
- **Felelős**: Engineering Lead
- **Review ciklus**: Negyedévente
- **Jóváhagyás**: CTO

### Biztonsági Kérdések
- **CISO**: security@garagereg.com
- **Security Team**: security-team@garagereg.com
- **Incidensbejelentés**: incidents@garagereg.com

### Szabványok és Compliance
- **Quality Assurance**: qa@garagereg.com
- **Compliance Officer**: compliance@garagereg.com

---

**Dokumentum verzió**: 1.0.0  
**Utolsó módosítás**: 2025-10-01  
**Következő felülvizsgálat**: 2025-12-01  
**Jóváhagyta**: Engineering Team