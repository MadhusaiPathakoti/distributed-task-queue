from fastapi import APIRouter, HTTPException
from models.task import TaskCreate, TaskResponse, TaskStatus
from db.postgres import insert_task, get_task, get_all_tasks
from db.redis_client import enqueue_task
from datetime import datetime
import uuid

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
async def submit_task(task: TaskCreate):
    """Submit a new task to the queue"""

    task_id = str(uuid.uuid4())
    now = datetime.utcnow()

    task_data = {
        "task_id": task_id,
        "task_type": task.task_type,
        "payload": task.payload,
        "status": TaskStatus.PENDING,
        "priority": task.priority,
        "max_retries": task.max_retries,
        "retry_count": 0,
        "created_at": now,
        "started_at": None,
        "completed_at": None,
        "result": None,
        "error": None,
    }

    # 1. Save to PostgreSQL first (source of truth)
    await insert_task(task_data)

    # 2. Push task_id to Redis queue
    enqueue_task(task_id, task.priority)

    return TaskResponse(**task_data)


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """Get the current status of a specific task"""
    task = await get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse(**dict(task))


@router.get("/", response_model=list[TaskResponse])
async def list_tasks(limit: int = 50):
    """Get recent tasks"""
    tasks = await get_all_tasks(limit)
    return [TaskResponse(**dict(t)) for t in tasks]