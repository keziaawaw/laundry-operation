from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.jwt_handler import get_current_user

router = APIRouter()


class CourierSchedule(BaseModel):
    order_id: str
    pickup_address: str
    delivery_address: str
    scheduled_time: datetime
    courier_name: Optional[str] = None
    status: str = "pending"


class NotificationRequest(BaseModel):
    order_id: str
    customer_phone: str
    message_type: str
    message_content: str


@router.post("/schedule-pickup")
def schedule_pickup(schedule: CourierSchedule, current_user: dict = Depends(get_current_user)):
    return {
        "order_id": schedule.order_id,
        "status": "scheduled",
        "pickup_address": schedule.pickup_address,
        "scheduled_time": schedule.scheduled_time,
        "message": "Pickup berhasil dijadwalkan",
    }


@router.post("/schedule-delivery")
def schedule_delivery(schedule: CourierSchedule, current_user: dict = Depends(get_current_user)):
    return {
        "order_id": schedule.order_id,
        "status": "scheduled",
        "delivery_address": schedule.delivery_address,
        "scheduled_time": schedule.scheduled_time,
        "message": "Delivery berhasil dijadwalkan",
    }


@router.post("/send-notification")
def send_notification(notif: NotificationRequest, current_user: dict = Depends(get_current_user)):
    return {
        "order_id": notif.order_id,
        "message_type": notif.message_type,
        "status": "sent",
        "timestamp": datetime.now(),
        "message": "Notifikasi berhasil dikirim",
    }


@router.get("/courier-location/{order_id}")
def get_courier_location(order_id: str, current_user: dict = Depends(get_current_user)):
    return {
        "order_id": order_id,
        "courier_name": "John Doe",
        "latitude": -6.2088,
        "longitude": 106.8456,
        "status": "on_the_way",
        "eta_minutes": 15,
    }
