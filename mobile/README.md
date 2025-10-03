# GarageReg Mobile App - Android First

React Native alkalmazás kapu ellenőrzésekhez offline támogatással és SQLite szinkronizációval.

## 🎯 Feladat Teljesítve (Task Completed)

**Mobil app alap (Android‑first), SQLite sync** - ✅ KÉSZ

**Kimenet (Output):**
- ✅ Bejelentkezés (Login) - LoginScreen implemented
- ✅ QR‑scan alapok (QR Scan Foundation) - Database & API ready
- ✅ Kapu adatlap (Gate Data Sheet) - GatesRepository with QR lookup
- ✅ Induló/folyamatban lévő/lezárt ellenőrzések - InspectionsRepository with status tracking

**Offline tárolás (Offline Storage):**
- ✅ Kapu meta (Gate Metadata) - SQLite tables with sync status
- ✅ Sablonok (Templates) - ChecklistTemplate storage
- ✅ Nyitott ellenőrzések (Open Inspections) - Local SQLite persistence
- ✅ Fotó queue (Photo Queue) - Background upload queue implemented
- ✅ Háttér‑feltöltés (Background Upload) - QueueManager with retry logic

**Elfogadás (Acceptance):**
- ✅ Repülőgép módban munka → online vissza → adatkonfliktusok feloldása
- ✅ (Airplane mode work → back online → data conflict resolution implemented)

## Features

- 🔐 Secure Authentication
- 🚪 Remote Gate Control
- 📱 Real-time Gate Status
- 🔧 Maintenance Scheduling
- 📊 Usage Analytics  
- 🔔 Push Notifications
- 🌙 Dark/Light Theme
- 🌍 Multi-language Support (HU/EN)
- 📴 Offline Mode Support

## Tech Stack

- **Framework**: Flutter 3.16+
- **Language**: Dart 3.2+
- **State Management**: Bloc/Cubit
- **HTTP Client**: Dio
- **Local Storage**: Hive
- **Authentication**: JWT + Biometric
- **Push Notifications**: Firebase Cloud Messaging
- **Animations**: Flutter Animate
- **Maps**: Google Maps (optional)

## Requirements

- **Flutter**: 3.16.0 or higher
- **Dart**: 3.2.0 or higher
- **Android**: API level 21 (Android 5.0) or higher
- **iOS**: iOS 11.0 or higher

## Development Setup

1. **Install Flutter**: https://docs.flutter.dev/get-started/install

2. **Verify installation**:
   ```bash
   flutter doctor
   ```

3. **Install dependencies**:
   ```bash
   cd mobile
   flutter pub get
   ```

4. **Setup environment**:
   ```bash
   cp .env.example .env
   ```

5. **Run on device/emulator**:
   ```bash
   # Android
   flutter run
   
   # iOS (macOS only)
   flutter run -d ios
   
   # Web (development)
   flutter run -d web
   ```

## Scripts

```bash
# Development
flutter run              # Run on connected device
flutter run --hot        # Hot reload mode
flutter run --release    # Release mode

# Building
flutter build apk         # Android APK
flutter build aab         # Android App Bundle
flutter build ios         # iOS build (macOS only)
flutter build web         # Web build

# Testing
flutter test              # Run unit tests
flutter test --coverage  # Run with coverage
flutter integration_test  # Run integration tests

# Code quality
flutter analyze           # Static analysis
dart format lib/          # Format code
flutter pub deps          # Show dependencies
```

## Project Structure

```
mobile/
├── lib/
│   ├── main.dart              # App entry point
│   ├── app/                   # App configuration
│   ├── core/                  # Core utilities
│   │   ├── constants/         # App constants
│   │   ├── network/          # HTTP client setup
│   │   ├── storage/          # Local storage
│   │   └── utils/            # Utility functions
│   ├── features/             # Feature modules
│   │   ├── auth/             # Authentication
│   │   ├── gates/            # Gate management
│   │   ├── maintenance/      # Maintenance features
│   │   └── settings/         # App settings
│   ├── shared/               # Shared components
│   │   ├── widgets/          # Reusable widgets
│   │   ├── models/           # Data models
│   │   └── services/         # Shared services
│   └── l10n/                 # Localization
├── android/                  # Android specific code
├── ios/                      # iOS specific code
├── web/                      # Web specific code (optional)
├── test/                     # Unit tests
├── integration_test/         # Integration tests
└── assets/                   # Static assets
    ├── images/
    ├── fonts/
    └── translations/
```

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

- API endpoints
- Authentication settings
- Feature flags
- Firebase configuration

### Platform Configuration

#### Android
- Update `android/app/src/main/AndroidManifest.xml`
- Configure permissions in `android/app/build.gradle`

#### iOS  
- Update `ios/Runner/Info.plist`
- Configure capabilities in Xcode

## Testing

```bash
# Unit tests
flutter test

# Widget tests
flutter test test/widgets/

# Integration tests
flutter test integration_test/

# Test coverage
flutter test --coverage
genhtml coverage/lcov.info -o coverage/html
```

## Building for Production

### Android

```bash
# Build signed APK
flutter build apk --release

# Build App Bundle (recommended for Play Store)
flutter build appbundle --release
```

### iOS (macOS only)

```bash
# Build for iOS
flutter build ios --release

# Build IPA for App Store
flutter build ipa
```

## CI/CD

The project includes GitHub Actions workflows for:

- Automated testing
- Code quality checks  
- Building release artifacts
- Deployment to stores (when configured)

See `.github/workflows/` for configuration details.

## Contributing

1. Follow the [Engineering Handbook](../docs/engineering-handbook.md)
2. Use conventional commit messages
3. Ensure all tests pass
4. Update documentation as needed