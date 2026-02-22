from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from db.postgres import connect_db, disconnect_db, create_tables
from routes.tasks import router as tasks_router
from routes.metrics import router as metrics_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    create_tables()       # creates tables in Supabase if they don't exist
    await connect_db()
    yield
    # Shutdown
    await disconnect_db()


app = FastAPI(
    title="Distributed Task Queue",
    description="A production-grade task queue system",
    version="1.0.0",
    lifespan=lifespan
)

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(tasks_router)
app.include_router(metrics_router)


@app.get("/")
async def root():
    return {"message": "Task Queue API is running", "docs": "/docs"}


@app.get("/health")
async def health():
    return {"status": "healthy"}