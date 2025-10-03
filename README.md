<<<<<<< HEAD
# garage-reg
=======
# GarageReg - Garage Gate Management System

A comprehensive garage gate management and maintenance system built with modern technologies.

## 🏗️ Architecture

This is a monorepo containing:

- **Backend Services**: FastAPI-based API and Celery workers
- **Web Admin Panel**: Next.js React application  
- **Mobile App**: Flutter cross-platform application
- **Infrastructure**: Docker Compose development environment

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local web development)
- Flutter SDK (for mobile development)
- Python 3.11+ (for local backend development)

### Development Setup

1. **Clone and setup environment**:
   ```bash
   git clone <repository-url>
   cd garagereg
   cp .env.example .env
   ```

2. **Start all services**:
   ```bash
   docker compose up -d
   ```

3. **Verify health**:
   ```bash
   curl http://localhost/api/healthz
   ```

### Service URLs

- **API**: http://localhost/api
- **Web Admin**: http://localhost:3000
- **Traefik Dashboard**: http://localhost:8080
- **MinIO Console**: http://localhost:9001
- **Mailhog**: http://localhost:8025
- **Redis Commander**: http://localhost:8081

## 📁 Project Structure

```
garagereg/
├── backend/                    # FastAPI backend services
│   ├── api/                    # REST API service
│   └── worker/                 # Celery worker service
├── web-admin/                  # Next.js admin panel
├── mobile/                     # Flutter mobile app
├── infra/                      # Infrastructure & Docker
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
└── .github/                    # GitHub Actions CI/CD
```

## 🧪 Testing

```bash
# Backend tests
cd backend && python -m pytest

# Frontend tests  
cd web-admin && npm test

# Mobile tests
cd mobile && flutter test

# E2E tests
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 🚢 Deployment

```bash
# Build production images
docker compose -f docker-compose.prod.yml build

# Deploy to staging
./scripts/deploy-staging.sh

# Deploy to production
./scripts/deploy-production.sh
```

## 📚 Documentation

- [Engineering Handbook](./docs/engineering-handbook.md)
- [API Documentation](./docs/api/)
- [Architecture Overview](./docs/architecture/)
- [Deployment Guide](./docs/deployment/)

## 🤝 Contributing

1. Read the [Engineering Handbook](./docs/engineering-handbook.md)
2. Follow our [Git workflow](./docs/engineering-handbook.md#4-branch-stratégia)
3. Ensure all tests pass and code follows our standards
4. Submit a Pull Request with proper description

## 📄 License

See [LICENSE](./LICENSE) file for details.

## 🆘 Support

- **Issues**: GitHub Issues
- **Security**: security@garagereg.com
- **Documentation**: [Engineering Handbook](./docs/engineering-handbook.md)
>>>>>>> 11e701d (feat: Add Gates and Sites pages with basic structure and content)
