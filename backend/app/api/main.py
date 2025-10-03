"""Main API router."""

from fastapi import APIRouter

from app.api.routes import auth, gates, maintenance, users, health, structure, import_routes, labels, dynamic_checklists, field_forms, qr_labels, sync, notifications, inventory, analytics, audit
from app.api import tickets, test_errors

# Create main API router
api_router = APIRouter()

# Include route modules
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(structure.router, tags=["Structure"])
api_router.include_router(import_routes.router, tags=["Import"])
api_router.include_router(labels.router, tags=["Labels"])
api_router.include_router(qr_labels.router, tags=["QR Labels"])
api_router.include_router(gates.router, prefix="/gates", tags=["Gates"])
api_router.include_router(maintenance.router, prefix="/maintenance", tags=["Maintenance"])
api_router.include_router(dynamic_checklists.router, prefix="/dynamic-checklists", tags=["Dynamic Checklists"])
api_router.include_router(field_forms.router, prefix="/field-forms", tags=["Field Forms"])
api_router.include_router(sync.router, tags=["Synchronization"])
api_router.include_router(notifications.router, tags=["Notifications"])
api_router.include_router(inventory.router, tags=["Inventory Management"])
api_router.include_router(analytics.router, tags=["Analytics & Reporting"])
api_router.include_router(audit.router, tags=["Audit & Logging"])
api_router.include_router(tickets.router, tags=["Tickets & Work Orders"])
api_router.include_router(test_errors.router, tags=["Error Testing"])