# FastAPI Backend for GarageReg

## Development Setup

1. **Create virtual environment**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**:
   ```bash
   alembic upgrade head
   ```

4. **Start development server**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database setup
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── api/                 # API routes
│   ├── services/            # Business logic
│   ├── auth/                # Authentication
│   ├── utils/               # Utilities
│   └── worker.py            # Celery worker
├── alembic/                 # Database migrations
├── tests/                   # Test suite
├── requirements.txt         # Python dependencies
└── Dockerfile              # Docker configuration
```

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_gates.py
```

## API Endpoints

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `POST /api/v1/auth/logout` - Logout

### Gates
- `GET /api/v1/gates/` - List gates
- `POST /api/v1/gates/` - Create gate
- `GET /api/v1/gates/{id}` - Get gate
- `PUT /api/v1/gates/{id}` - Update gate
- `DELETE /api/v1/gates/{id}` - Delete gate

### Maintenance
- `GET /api/v1/maintenance/` - List maintenance records
- `POST /api/v1/maintenance/` - Create maintenance record
- `GET /api/v1/maintenance/{id}` - Get maintenance record

### Health Check
- `GET /healthz` - Health check endpoint