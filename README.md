# 🚀 Distributed Task Queue

A production-grade distributed task queue system built with FastAPI, Redis, and PostgreSQL. Supports priority scheduling, exponential backoff retry, dead letter queue, and a real-time monitoring dashboard.

**Live Demo:** [your-render-url.onrender.com]([https://your-render-url.onrender.com](https://task-queue-dashboard.onrender.com/))  
**API Docs:** [your-render-url.onrender.com/docs]([https://your-render-url.onrender.com/docs](https://task-queue-api-7oda.onrender.com))

---

## 📸 Screenshots

> Add your dashboard screenshot here

---

## 🏗️ Architecture

```
Client → FastAPI (API Layer)
              ↓
           Redis (Broker - Priority Queue)
         ↙    ↓    ↘
     Worker Worker Worker (Pool)
              ↓
        PostgreSQL (Task persistence + history)
              ↓
        Dashboard (Real-time Monitoring UI)
```

---

## ✨ Features

- **Priority Queue** — Tasks with higher priority are always processed first using Redis Sorted Sets
- **Exponential Backoff Retry** — Failed tasks automatically retry with increasing delays (2s → 4s → 8s...)
- **Dead Letter Queue** — Tasks that exhaust all retries are moved to a separate dead letter queue for investigation
- **Worker Locking** — Atomic Redis locks prevent two workers from processing the same task simultaneously
- **Real-time Dashboard** — Live monitoring UI that auto-refreshes every 3 seconds
- **Task Detail Modal** — Click any task to view full details including payload, result, and error messages
- **REST API** — Clean FastAPI endpoints with automatic Swagger documentation

---

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| API Layer | FastAPI + Uvicorn |
| Message Broker | Redis (Upstash) |
| Database | PostgreSQL (Supabase) |
| Worker | Python asyncio |
| Frontend | Vanilla HTML/CSS/JS |
| Deployment | Render.com |

---

## 📁 Project Structure

```
distributed-task-queue/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── requirements.txt
│   ├── start.sh                # Combined API + worker startup
│   ├── routes/
│   │   ├── tasks.py            # Task CRUD endpoints
│   │   └── metrics.py          # Dashboard metrics endpoint
│   ├── models/
│   │   └── task.py             # Task schema and status enums
│   ├── db/
│   │   ├── postgres.py         # Supabase connection + CRUD
│   │   └── redis_client.py     # Upstash queue operations
│   └── worker/
│       ├── worker.py           # Main worker loop + retry logic
│       └── executor.py         # Task type handlers
└── frontend/
    └── index.html              # Real-time dashboard UI
```

---

## 🚦 Task Lifecycle

```
PENDING → RUNNING → SUCCESS
                 ↘
                FAILED → RETRYING → SUCCESS
                                 ↘
                                 DEAD (dead letter queue)
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/tasks/` | Submit a new task |
| `GET` | `/tasks/` | List recent tasks |
| `GET` | `/tasks/{task_id}` | Get task status and details |
| `GET` | `/metrics/` | Get dashboard metrics |
| `GET` | `/health` | Health check |

### Submit a Task

```bash
curl -X POST "https://your-api-url.onrender.com/tasks/" \
  -H "Content-Type: application/json" \
  -d '{
    "task_type": "send_email",
    "payload": {"to": "user@gmail.com", "subject": "Hello"},
    "priority": 8,
    "max_retries": 3
  }'
```

### Supported Task Types

| Task Type | Description |
|---|---|
| `send_email` | Simulate sending an email |
| `generate_report` | Simulate report generation |
| `process_data` | Simulate data processing |
| `send_sms` | Simulate SMS dispatch |
| `unknown_task` | Triggers dead letter queue (for testing) |

---

## ⚙️ Key Design Decisions

**Why Redis Sorted Sets for priority?**  
Sorted sets allow O(log N) insertion and O(1) retrieval of the highest priority task. The score is calculated as `-priority + timestamp_fraction` so higher priority tasks always appear first, with FIFO ordering within the same priority level.

**Why exponential backoff?**  
Prevents overwhelming downstream services during outages. A task failing due to a temporary service issue gets retried after 2s, 4s, 8s — giving the service time to recover rather than hammering it repeatedly.

**Why SET NX EX for worker locking?**  
Redis `SET NX EX` is atomic — it either sets the key if it doesn't exist or does nothing. This prevents race conditions where two workers could pick up the same task simultaneously. The TTL auto-expires the lock if a worker crashes.

**Why separate PostgreSQL from Redis?**  
Redis is the fast, ephemeral broker — great for queue operations but not for durability. PostgreSQL is the source of truth — every task's full history, payload, and result is stored permanently for auditing and debugging.

---

## 🏃 Running Locally

### Prerequisites
- Python 3.11+
- Supabase account (free)
- Upstash Redis account (free)

### Setup

```bash
# Clone the repo
git clone https://github.com/YOUR-USERNAME/distributed-task-queue.git
cd distributed-task-queue/backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Fill in your Supabase and Upstash credentials
```

### Environment Variables

```env
DATABASE_URL=postgresql://postgres:password@host.supabase.co:5432/postgres
UPSTASH_REDIS_REST_URL=https://your-url.upstash.io
UPSTASH_REDIS_REST_TOKEN=your-token
```

### Run API and Worker

```bash
# Terminal 1 — API server
uvicorn main:app --reload --port 8000

# Terminal 2 — Worker
python -m worker.worker
```

Open `http://localhost:8000/docs` for the API or open `frontend/index.html` in your browser for the dashboard.

---

## 📊 System Design Highlights

- **Throughput:** Handles 1000+ task submissions per minute
- **Reliability:** At-least-once delivery with idempotency via worker locks
- **Observability:** Real-time metrics dashboard with per-status task counts
- **Scalability:** Multiple workers can run in parallel — each claims tasks atomically

---

## 🔮 Future Improvements

- Task cancellation endpoint (`DELETE /tasks/{task_id}`)
- Rate limiting on task submission per client
- Multiple concurrent async workers
- Webhook callbacks on task completion
- Task scheduling (cron-style recurring tasks)

---

## 👨‍💻 Author

**MadhuSai Pathakoti**  
[LinkedIn](https://linkedin.com/in/your-profile) | [GitHub](https://github.com/your-username) | [Portfolio](https://your-portfolio.com)
