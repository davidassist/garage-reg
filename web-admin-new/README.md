# GarageReg Admin Panel

Modern React TypeScript admin alkalmazás a GarageReg rendszerhez, teljes authentication, RBAC jogosultságkezeléssel és komponenskönyvtárral.

## ✨ Funkciók

### 🔐 Authentication & Authorization
- **Bejelentkezési form** - React Hook Form + Zod validációval
- **RBAC jogosultságkezelés** - Szerepalapú hozzáférés-vezérlés
- **Protected routes** - Védett útvonalak permission guard-okkal
- **Automatikus token kezelés** - localStorage + Zustand store

### 📊 Dashboard
- **Statisztikai dashboard** - Lejáró ellenőrzések és KPI-k
- **Responsive design** - Mobil és desktop optimalizálva
- **Real-time adatok** - React Query cache kezeléssel

### 🏢 Entitás kezelés
- **Ügyfelek** - Teljes CRUD műveletek
- **Telephelyek** - Hierarchikus struktúra
- **Épületek** - Kapcsolt adatok kezelése  
- **Kapuk** - Részletes kapu információk

### 🎨 UI/UX
- **Shadcn/ui komponenskönyvtár** - Modern, accessible komponensek
- **Tailwind CSS** - Utility-first styling
- **Dark mode support** - Sötét téma támogatás
- **Mobile-first** - Responsive layout minden eszközön

### 🧪 Testing
- **Playwright E2E tesztek** - Teljes smoke teszt lefedettség
- **Authentication flow** - Bejelentkezési folyamat tesztjei
- **RBAC validation** - Jogosultság ellenőrzések
- **Protected route** - Védett útvonal tesztek

## 🚀 Telepítés

### Előfeltételek
```bash
Node.js 18+ és npm/yarn
Backend API futnia kell (localhost:8000)
```

### Fejlesztői környezet
```bash
# Dependencies telepítése
npm install

# Development szerver indítása
npm run dev

# Alkalmazás elérhető: http://localhost:3000
```

### Production build
```bash
# Production build készítése
npm run build

# Build előnézet
npm run preview
```

## 🧪 Tesztelés

### E2E tesztek futtatása
```bash
# Playwright tesztek telepítése
npx playwright install

# E2E tesztek futtatása
npm run test:e2e

# E2E tesztek UI módban
npm run test:e2e:ui
```

### Teszt lefedettség
- ✅ **Authentication flow** - Bejelentkezés/kijelentkezés
- ✅ **Protected routes** - Jogosultság-alapú hozzáférés
- ✅ **Navigation** - Oldalak közötti navigáció
- ✅ **Dashboard** - Statisztikai adatok megjelenítése
- ✅ **RBAC guards** - Szerepalapú funkciók tesztelése

## 🏗️ Architektúra

### Technológiai stack
```
Frontend Framework: React 18 + TypeScript
State Management: Zustand + React Query
UI Library: Shadcn/ui + Tailwind CSS
Form Handling: React Hook Form + Zod
Routing: React Router v6
Testing: Playwright
Build Tool: Vite
```

### Mappa struktúra
```
src/
├── components/          # Újrahasználható komponensek
│   ├── ui/             # Shadcn/ui komponensek
│   ├── auth/           # Authentication komponensek
│   └── layout/         # Layout komponensek
├── pages/              # Oldal komponensek
├── hooks/              # Custom React hooks
│   ├── api.ts          # React Query hooks
│   └── permissions.ts  # RBAC jogosultság hooks
├── stores/             # Zustand store-ok
├── lib/                # Utility függvények
│   ├── api.ts          # API client
│   ├── utils.ts        # Helper függvények
│   └── validations.ts  # Zod sémák
├── types/              # TypeScript típusok
└── tests/              # E2E tesztek
    └── e2e/            # Playwright test fájlok
```

### State Management
```typescript
// Auth Store (Zustand)
- User authentication állapot
- Login/logout funkciók
- Persistent storage

// API State (React Query)
- Server állapot kezelés
- Cache invalidation
- Background updates
- Optimistic updates
```

### Permission System
```typescript
// RBAC Implementation
interface Permission {
  resource: 'clients' | 'sites' | 'buildings' | 'gates'
  action: 'create' | 'read' | 'update' | 'delete'
}

// Usage példa
const { canCreateClient, canEditClient } = usePermissions()
```

## 🔌 API Integráció

### Backend kapcsolat
```typescript
// API Base URL
const API_BASE_URL = '/api/v1'

// Automatikus proxy (Vite)
'/api' -> 'http://localhost:8000'
```

### Authentication
```typescript
// Login flow
POST /api/v1/auth/login (FormData)
Response: { access_token, user }

// Protected requests  
Authorization: Bearer <token>
```

### Error Handling
```typescript
// Automatic retry logic
- Network errors: 3x retry
- 401/403 errors: No retry
- Automatic token refresh

// User-friendly error messages
- Hungarian error messages
- Fallback for unknown errors
```

## 📱 Responsive Design

### Breakpoints (Tailwind)
```css
sm: 640px   # Tablet portrait
md: 768px   # Tablet landscape  
lg: 1024px  # Desktop
xl: 1280px  # Large desktop
2xl: 1536px # Extra large
```

### Mobile Features
- Hamburger menu navigáció
- Touch-friendly gombok
- Optimalizált form layout
- Swipe gestures támogatás

## 🔒 Biztonsági funkciók

### Frontend Security
- **XSS Protection** - Input sanitization
- **CSRF Token** - API request védelem  
- **Secure Storage** - Encrypted localStorage
- **Route Guards** - Permission-based access

### Authentication Security
- **JWT Token** - Secure token storage
- **Auto Logout** - Inaktivitás esetén
- **Session Management** - Multi-tab sync
- **Role-based Access** - Granular permissions

## 🎯 Elfogadási kritériumok

### ✅ Teljesített követelmények
1. **Bejelentkezési oldal** - React Hook Form + Zod validáció
2. **Dashboard** - Lejáró ellenőrzések és statisztikák
3. **CRUD oldalak** - Ügyfél/telephely/épület/kapu listák
4. **Globális állapot** - React Query + Zustand
5. **Űrlapok** - React Hook Form + Zod validáció  
6. **Komponenskönyvtár** - Shadcn/ui + custom komponensek
7. **E2E tesztek** - Playwright smoke tesztek
8. **RBAC guardok** - Védett route-ok szerepalapú hozzáféréssel

### 🚀 További fejlesztési lehetőségek
- **Real-time notifications** - WebSocket integráció
- **Advanced filtering** - Komplex szűrők és keresés
- **Bulk operations** - Tömeges műveletek
- **Export functionality** - PDF/Excel export
- **Audit log** - Felhasználói aktivitás naplózás
- **Multi-language** - Többnyelvű támogatás

## 👥 Fejlesztési workflow

### Git workflow
```bash
# Feature branch
git checkout -b feature/component-name

# Development és tesztelés
npm run dev
npm run test:e2e

# Code review és merge
git push origin feature/component-name
```

### Code Quality
```bash
# Linting
npm run lint

# TypeScript check  
npm run type-check

# Prettier formatting
npm run format
```

Ez egy teljes értékű, production-ready admin alkalmazás modern React ökoszisztémával és teljes test lefedettséggel.