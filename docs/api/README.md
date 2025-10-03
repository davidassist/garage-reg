# API Documentation

## Overview

GarageReg REST API provides endpoints for managing garage gates, maintenance schedules, and user authentication.

## Base URL

- **Development**: `http://localhost/api/v1`
- **Production**: `https://api.garagereg.com/v1`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

### Login
```http
POST /auth/login
Content-Type: application/json

{
  "username": "your-username",
  "password": "your-password"
}
```

### Response
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 900
}
```

## Endpoints

### Health Check
- `GET /healthz` - Basic health check
- `GET /health/detailed` - Detailed health information

### Authentication
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - User logout

### Users
- `GET /users/` - List users (admin only)
- `GET /users/{id}` - Get user details
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user

### Gates
- `GET /gates/` - List all gates
- `POST /gates/` - Create new gate
- `GET /gates/{id}` - Get gate details
- `PUT /gates/{id}` - Update gate
- `DELETE /gates/{id}` - Delete gate
- `POST /gates/{id}/open` - Open gate
- `POST /gates/{id}/close` - Close gate
- `POST /gates/{id}/stop` - Emergency stop
- `GET /gates/{id}/status` - Get gate status

### Maintenance
- `GET /maintenance/` - List maintenance records
- `POST /maintenance/` - Create maintenance record
- `GET /maintenance/{id}` - Get maintenance details
- `PUT /maintenance/{id}` - Update maintenance record
- `DELETE /maintenance/{id}` - Delete maintenance record
- `GET /maintenance/gates/{gate_id}` - Get gate maintenance history
- `POST /maintenance/schedule` - Schedule maintenance
- `GET /maintenance/overdue` - List overdue maintenance

## Error Responses

The API uses standard HTTP status codes:

- `200 OK` - Success
- `201 Created` - Resource created
- `400 Bad Request` - Invalid request
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Access denied
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Error Format
```json
{
  "detail": "Error message",
  "error_code": "SPECIFIC_ERROR_CODE",
  "timestamp": "2025-01-01T12:00:00Z"
}
```

## Rate Limiting

API endpoints are rate limited:
- Authentication: 5 requests per 15 minutes
- General API: 100 requests per minute
- Gate operations: 10 requests per minute

## Pagination

List endpoints support pagination:

```http
GET /gates/?page=1&size=20&sort=created_at&order=desc
```

### Response Format
```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "size": 20,
  "pages": 5
}
```

## WebSocket Events

Real-time updates via WebSocket connection:

```javascript
const ws = new WebSocket('ws://localhost/api/ws');

ws.onmessage = function(event) {
  const data = JSON.parse(event.data);
  // Handle gate status updates, maintenance alerts, etc.
};
```

## SDKs and Tools

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`
- **OpenAPI Schema**: `/openapi.json`
- **Postman Collection**: Available in `/docs/api/postman/`