
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/auth/login")
async def login():
    return {
        "access_token": "test_token_123",
        "token_type": "bearer", 
        "user": {"id": 1, "username": "admin", "email": "admin@test.com"}
    }

@app.get("/api/auth/me")
async def me():
    return {"id": 1, "username": "admin", "email": "admin@test.com"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "timestamp": "2025-10-04T10:00:00Z"}

@app.get("/api/users")
async def users():
    return [
        {"id": 1, "username": "admin", "email": "admin@test.com", "role": "admin"},
        {"id": 2, "username": "operator", "email": "operator@test.com", "role": "operator"}
    ]

@app.get("/api/organizations")
async def organizations():
    return [
        {"id": 1, "name": "Test Organization", "description": "Test org for E2E"}
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
