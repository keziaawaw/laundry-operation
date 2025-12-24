from fastapi import APIRouter, Depends
from auth.jwt_handler import get_current_user

router = APIRouter()


@router.get("/tasks")
def get_tasks(current_user=Depends(get_current_user)):
    return {"tasks": [{"id": 1, "name": "Cuci Baju"}, {"id": 2, "name": "Setrika Pakaian"}], "user": current_user}


@router.get("/tasks/{task_id}")
def get_task(task_id: int, current_user=Depends(get_current_user)):
    return {"task_id": task_id, "name": f"Task {task_id}", "user": current_user}
