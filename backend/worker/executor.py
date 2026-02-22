import asyncio
import random


async def execute_task(task_type: str, payload: dict) -> dict:
    """
    Routes task_type to the correct handler.
    Returns result dict on success, raises exception on failure.
    """
    handlers = {
        "send_email": handle_send_email,
        "generate_report": handle_generate_report,
        "process_data": handle_process_data,
        "send_sms": handle_send_sms,
    }

    handler = handlers.get(task_type)
    if not handler:
        raise ValueError(f"Unknown task type: {task_type}")

    return await handler(payload)


async def handle_send_email(payload: dict) -> dict:
    """Simulate sending an email"""
    await asyncio.sleep(1)  # simulate network call

    # Simulate 20% failure rate to test retry logic
    if random.random() < 0.2:
        raise ConnectionError("Email server timeout")

    return {
        "status": "sent",
        "to": payload.get("to"),
        "subject": payload.get("subject", "No subject"),
        "message_id": f"msg_{random.randint(1000, 9999)}"
    }


async def handle_generate_report(payload: dict) -> dict:
    """Simulate generating a report"""
    await asyncio.sleep(2)  # simulate heavy computation
    return {
        "status": "generated",
        "report_id": f"rpt_{random.randint(1000, 9999)}",
        "rows_processed": random.randint(100, 10000)
    }


async def handle_process_data(payload: dict) -> dict:
    """Simulate data processing"""
    await asyncio.sleep(0.5)
    return {
        "status": "processed",
        "records": payload.get("records", 0),
        "output_file": f"output_{random.randint(1000, 9999)}.csv"
    }


async def handle_send_sms(payload: dict) -> dict:
    """Simulate sending SMS"""
    await asyncio.sleep(0.3)
    if random.random() < 0.1:
        raise ConnectionError("SMS gateway unavailable")
    return {
        "status": "sent",
        "phone": payload.get("phone"),
        "message_id": f"sms_{random.randint(1000, 9999)}"
    }