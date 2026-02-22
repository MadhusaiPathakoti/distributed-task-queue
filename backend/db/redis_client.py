from upstash_redis import Redis
from dotenv import load_dotenv
import os
import json
import time

load_dotenv()

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

QUEUE_KEY = "task_queue"          # main priority queue
DEAD_LETTER_KEY = "dead_letter"   # failed tasks go here
LOCK_PREFIX = "lock:task:"        # worker locks


# ─── Queue Operations ─────────────────────────────────────────

def enqueue_task(task_id: str, priority: int):
    """
    Add task to Redis sorted set.
    Score = negative priority so highest priority is picked first.
    We subtract current timestamp fraction to preserve FIFO within same priority.
    """
    score = -priority + (time.time() / 1e12)  # tiny timestamp offset
    redis.zadd(QUEUE_KEY, {task_id: score})
    print(f"📥 Task {task_id} enqueued with priority {priority}")


def dequeue_task():
    """
    Pop the highest priority task (lowest score = highest priority).
    Returns task_id string or None.
    """
    result = redis.zpopmin(QUEUE_KEY, count=1)
    if result:
        task_id = result[0][0]  # zpopmin returns [(member, score), ...]
        return task_id
    return None


def requeue_task_with_delay(task_id: str, delay_seconds: float):
    """
    Put a failed task back in queue after a delay.
    Score = future timestamp so it won't be picked up until then.
    """
    future_score = time.time() + delay_seconds
    redis.zadd(QUEUE_KEY, {task_id: future_score})
    print(f"🔄 Task {task_id} requeued with {delay_seconds}s delay")


def move_to_dead_letter(task_id: str):
    """Tasks that exhausted all retries go here"""
    redis.lpush(DEAD_LETTER_KEY, task_id)
    print(f"💀 Task {task_id} moved to dead letter queue")


def get_queue_depth():
    return redis.zcard(QUEUE_KEY)


def get_dead_letter_count():
    return redis.llen(DEAD_LETTER_KEY)


# ─── Worker Lock ──────────────────────────────────────────────

def acquire_lock(task_id: str, worker_id: str, ttl: int = 60) -> bool:
    """
    Atomic lock — only one worker can process a task at a time.
    SET NX EX = set only if not exists, with expiry.
    Returns True if lock acquired, False if another worker has it.
    """
    result = redis.set(
        f"{LOCK_PREFIX}{task_id}",
        worker_id,
        nx=True,
        ex=ttl
    )
    return result is not None


def release_lock(task_id: str):
    redis.delete(f"{LOCK_PREFIX}{task_id}")