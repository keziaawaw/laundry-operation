from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from auth.jwt_handler import get_current_user

router = APIRouter()


class Customer(BaseModel):
    id: Optional[str] = None
    name: str
    email: EmailStr
    phone: str
    address: str
    city: str
    postal_code: str


class Worker(BaseModel):
    id: Optional[str] = None
    name: str
    role: str
    phone: str
    status: str = "available"


class LaundryMachine(BaseModel):
    id: Optional[str] = None
    machine_type: str
    capacity_kg: float
    status: str = "available"
    location: str


@router.post("/customers")
def create_customer(customer: Customer, current_user: dict = Depends(get_current_user)):
    customer_data = customer.model_dump() if hasattr(customer, "model_dump") else customer.dict()
    return {"id": "cust_123", **customer_data, "status": "active", "message": "Pelanggan berhasil dibuat"}


@router.get("/customers/{customer_id}")
def get_customer(customer_id: str, current_user: dict = Depends(get_current_user)):
    return {
        "id": customer_id,
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+62812345678",
        "address": "Jl. Merdeka No. 1",
        "city": "Jakarta",
        "postal_code": "12345",
        "status": "active",
    }


@router.post("/workers")
def create_worker(worker: Worker, current_user: dict = Depends(get_current_user)):
    worker_data = worker.model_dump() if hasattr(worker, "model_dump") else worker.dict()
    return {"id": "worker_123", **worker_data, "message": "Pekerja berhasil ditambahkan"}


@router.get("/workers")
def list_workers(current_user: dict = Depends(get_current_user)):
    return {
        "workers": [
            {"id": "worker_1", "name": "Budi", "role": "washer", "status": "available"},
            {"id": "worker_2", "name": "Ahmad", "role": "ironer", "status": "busy"},
        ]
    }


@router.post("/machines")
def create_machine(machine: LaundryMachine, current_user: dict = Depends(get_current_user)):
    machine_data = machine.model_dump() if hasattr(machine, "model_dump") else machine.dict()
    return {"id": "machine_123", **machine_data, "message": "Mesin berhasil ditambahkan"}


@router.get("/machines")
def list_machines(current_user: dict = Depends(get_current_user)):
    return {
        "machines": [
            {"id": "m_1", "machine_type": "washer", "capacity_kg": 10, "status": "available"},
            {"id": "m_2", "machine_type": "dryer", "capacity_kg": 8, "status": "busy"},
        ]
    }
