import asyncio
import uuid
from datetime import datetime
from worker.executor import execute_task
from db.postgres import (
    connect_db, disconnect_db,
    get_task, update_task_status
)
from db.redis_client import (
    dequeue_task, requeue_task_with_delay,
    move_to_dead_letter, acquire_lock, release_lock
)

WORKER_ID = str(uuid.uuid4())[:8]  # short unique id for this worker
POLL_INTERVAL = 2  # seconds to wait when queue is empty


def calculate_backoff(retry_count: int) -> float:
    """
    Exponential backoff: 2s, 4s, 8s, 16s...
    Capped at 60 seconds.
    """
    delay = 2 ** (retry_count + 1)
    return min(delay, 60)


async def process_task(task_id: str):
    """Process a single task end to end"""

    # 1. Acquire lock — prevent other workers from grabbing same task
    lock_acquired = acquire_lock(task_id, WORKER_ID, ttl=60)
    if not lock_acquired:
        print(f"⚠️  Worker {WORKER_ID}: Task {task_id} already locked, skipping")
        return

    try:
        # 2. Fetch task details from PostgreSQL
        task = await get_task(task_id)
        if not task:
            print(f"❌ Worker {WORKER_ID}: Task {task_id} not found in DB")
            return

        task = dict(task)

        # Skip if already processed (safety check)
        if task["status"] in ("SUCCESS", "DEAD"):
            print(f"⏭️  Worker {WORKER_ID}: Task {task_id} already {task['status']}, skipping")
            return

        print(f"🔄 Worker {WORKER_ID}: Starting task {task_id} [{task['task_type']}]")

        # 3. Mark as RUNNING
        await update_task_status(task_id, {
            "status": "RUNNING",
            "started_at": datetime.utcnow()
        })

        # 4. Execute the task
        result = await execute_task(task["task_type"], task["payload"])

        # 5. Mark as SUCCESS
        await update_task_status(task_id, {
            "status": "SUCCESS",
            "completed_at": datetime.utcnow(),
            "result": result,
            "error": None
        })

        print(f"✅ Worker {WORKER_ID}: Task {task_id} completed successfully")

    except Exception as e:
        error_message = str(e)
        print(f"❌ Worker {WORKER_ID}: Task {task_id} failed — {error_message}")

        task = dict(await get_task(task_id))
        retry_count = task["retry_count"] + 1
        max_retries = task["max_retries"]

        if retry_count <= max_retries:
            # Retry with exponential backoff
            delay = calculate_backoff(retry_count)
            print(f"🔁 Worker {WORKER_ID}: Retrying task {task_id} in {delay}s (attempt {retry_count}/{max_retries})")

            await update_task_status(task_id, {
                "status": "RETRYING",
                "retry_count": retry_count,
                "error": error_message
            })

            requeue_task_with_delay(task_id, delay)

        else:
            # Exhausted all retries — move to dead letter
            print(f"💀 Worker {WORKER_ID}: Task {task_id} exhausted all retries, moving to dead letter")

            await update_task_status(task_id, {
                "status": "DEAD",
                "completed_at": datetime.utcnow(),
                "retry_count": retry_count,
                "error": error_message
            })

            move_to_dead_letter(task_id)

    finally:
        # Always release lock
        release_lock(task_id)


async def run_worker():
    """Main worker loop — runs forever"""
    print(f"🚀 Worker {WORKER_ID} started, waiting for tasks...")

    await connect_db()

    try:
        while True:
            task_id = dequeue_task()

            if task_id:
                await process_task(task_id)
            else:
                # Queue empty — wait before polling again
                await asyncio.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        print(f"\n🛑 Worker {WORKER_ID} shutting down gracefully...")

    finally:
        await disconnect_db()


if __name__ == "__main__":
    asyncio.run(run_worker())