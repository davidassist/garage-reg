# System Architecture

## Overview

GarageReg is a modern, scalable garage gate management system built with a microservices architecture and containerized deployment.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Mobile App    │    │   Web Admin     │    │   Public API    │
│   (Flutter)     │    │   (Next.js)     │    │   (External)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │     Traefik     │
                    │  (Load Balancer) │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Celery        │    │   WebSocket     │
│   (REST API)    │    │   (Workers)     │    │   (Real-time)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │      Redis      │
                    │ (Cache/Broker)  │
                    └─────────────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │      MinIO      │    │    Mailhog      │
│   (Database)    │    │   (Storage)     │    │    (Email)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Technology Stack

### Frontend
- **Web Admin**: Next.js 14, React 18, TypeScript, Tailwind CSS
- **Mobile**: Flutter 3.16+, Dart 3.2+, BLoC pattern
- **UI Components**: shadcn/ui, Radix UI, Lucide Icons

### Backend
- **API Framework**: FastAPI (Python 3.11+)
- **Task Queue**: Celery with Redis
- **Authentication**: JWT with Argon2id password hashing
- **API Documentation**: Swagger/OpenAPI 3.0

### Database & Storage
- **Primary Database**: PostgreSQL 15
- **Cache & Message Broker**: Redis 7
- **Object Storage**: MinIO (S3-compatible)
- **Search**: PostgreSQL Full-Text Search

### Infrastructure
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Traefik v3
- **Monitoring**: Prometheus, Grafana, Flower
- **CI/CD**: GitHub Actions

### Security
- **Authentication**: JWT with RS256 signing
- **Password Hashing**: Argon2id
- **API Security**: Rate limiting, CORS, CSRF protection
- **Transport**: HTTPS/TLS 1.3

## Service Architecture

### API Gateway (Traefik)
- Load balancing and routing
- SSL termination
- Rate limiting
- Health checks

### Core API (FastAPI)
- RESTful API endpoints
- Authentication & authorization
- Input validation & sanitization
- Business logic orchestration

### Background Workers (Celery)
- Maintenance scheduling
- Report generation
- Email notifications
- Data processing tasks

### Database Layer
- PostgreSQL for transactional data
- Redis for caching and sessions
- MinIO for file storage

## Data Flow

### User Authentication Flow
```
Mobile/Web → Traefik → FastAPI → PostgreSQL
                  ↓
               JWT Token
                  ↓
            Subsequent Requests
```

### Gate Operation Flow
```
Mobile App → FastAPI → Gate Controller → Hardware
     ↓           ↓
WebSocket ← Redis ← Status Updates
     ↓
Real-time UI
```

### Maintenance Workflow
```
Scheduled Task → Celery Worker → Database
                      ↓
               Email Notification
                      ↓
              Mobile/Web Alert
```

## Scalability Considerations

### Horizontal Scaling
- Stateless API design
- Load balancer distribution
- Database read replicas
- Redis clustering

### Performance Optimization
- API response caching
- Database query optimization
- Asset CDN distribution
- Image optimization

### High Availability
- Multi-container deployment
- Health check monitoring
- Automatic failover
- Backup strategies

## Security Architecture

### Authentication & Authorization
- JWT-based stateless authentication
- Role-based access control (RBAC)
- API key management for external services
- Biometric authentication for mobile

### Data Protection
- Encryption at rest and in transit
- PII data masking in logs
- Secure secret management
- Regular security audits

### Network Security
- HTTPS enforcement
- CORS configuration
- Rate limiting per endpoint
- DDoS protection

## Monitoring & Observability

### Application Monitoring
- Health check endpoints
- Performance metrics
- Error tracking with Sentry
- User activity analytics

### Infrastructure Monitoring
- Container resource usage
- Database performance
- Network latency
- Storage utilization

### Logging Strategy
- Structured JSON logging
- Centralized log aggregation
- Log retention policies
- Audit trail maintenance

## Deployment Architecture

### Development Environment
- Docker Compose stack
- Local development databases
- Hot reload capabilities
- Debug tooling integration

### Staging Environment
- Production-like configuration
- Automated testing deployment
- Performance testing setup
- Security scanning integration

### Production Environment
- Kubernetes orchestration
- Auto-scaling policies
- Blue-green deployments
- Disaster recovery setup

## Future Architecture Considerations

### Microservices Evolution
- Service decomposition strategy
- API gateway enhancement
- Event-driven architecture
- Message queue implementation

### Cloud Migration Path
- Container orchestration (Kubernetes)
- Managed database services
- CDN integration
- Multi-region deployment

### IoT Integration
- MQTT broker integration
- Device management platform
- Edge computing capabilities
- Real-time data processing