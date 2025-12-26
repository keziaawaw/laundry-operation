import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI
from fastapi.security import OAuth2PasswordBearer

app = FastAPI(
    title="Laundry Management API",
    description="API untuk mengelola laundry, login, billing, logistics, dan resources.",
    version="1.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json",
)

try:
    from auth.api import router as auth_router
    app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
except ImportError as e:
    print(f"Warning: Could not import auth router: {e}")

try:
    from billing.api import router as billing_router
    app.include_router(billing_router, prefix="/billing", tags=["Billing & Payment"])
except ImportError as e:
    print(f"Warning: Could not import billing router: {e}")

try:
    from customers.api import router as customers_router
    app.include_router(customers_router, prefix="/customers", tags=["Customer & Resources"])
except ImportError as e:
    print(f"Warning: Could not import customers router: {e}")

try:
    from laundryoperation.api import router as laundry_router
    app.include_router(laundry_router, prefix="/laundry", tags=["Laundry Operation"])
except ImportError as e:
    print(f"Warning: Could not import laundry router: {e}")

try:
    from logistics.api import router as logistics_router
    app.include_router(logistics_router, prefix="/logistics", tags=["Logistics & Notification"])
except ImportError as e:
    print(f"Warning: Could not import logistics router: {e}")


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
