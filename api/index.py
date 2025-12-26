import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

try:
    from auth.api import router as auth_router
    from billing.api import router as billing_router
    from customers.api import router as customers_router
    from laundryoperation.api import router as laundry_router
    from logistics.api import router as logistics_router
except ImportError as e:
    print(f"Import error: {e}")
    raise

app = FastAPI(
    title="Laundry Management API",
    description="API untuk mengelola laundry, login, billing, logistics, dan resources.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(laundry_router, prefix="/laundry", tags=["Laundry Operation"])
app.include_router(billing_router, prefix="/billing", tags=["Billing & Payment"])
app.include_router(logistics_router, prefix="/logistics", tags=["Logistics & Notification"])
app.include_router(customers_router, prefix="/customers", tags=["Customer & Resources"])


@app.get("/")
def root():
    return {
        "message": "Laundry Management API",
        "version": "1.0.0",
        "bounded_contexts": [
            "Order & Laundry Operation",
            "Billing & Payment",
            "Logistics & Notification",
            "Customer & Resources",
        ],
        "docs": "http://localhost:8000/docs",
    }
