from fastapi import APIRouter
from db.postgres import get_metrics
from db.redis_client import get_queue_depth, get_dead_letter_count

router = APIRouter(prefix="/metrics", tags=["Metrics"])


@router.get("/")
async def get_dashboard_metrics():
    """Returns all stats needed for the dashboard"""

    db_metrics = await get_metrics()

    # Convert to a clean dict {status: count}
    status_counts = {row["status"]: row["count"] for row in db_metrics}

    return {
        "queue_depth": get_queue_depth(),
        "dead_letter_count": get_dead_letter_count(),
        "pending": status_counts.get("PENDING", 0),
        "running": status_counts.get("RUNNING", 0),
        "success": status_counts.get("SUCCESS", 0),
        "failed": status_counts.get("FAILED", 0),
        "retrying": status_counts.get("RETRYING", 0),
        "dead": status_counts.get("DEAD", 0),
        "total": sum(status_counts.values()),
    }