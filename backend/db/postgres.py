import databases
import sqlalchemy
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# databases library gives us async DB access
database = databases.Database(
    DATABASE_URL,
    statement_cache_size=0
)

# SQLAlchemy for schema definition only (not ORM)
metadata = sqlalchemy.MetaData()

tasks_table = sqlalchemy.Table(
    "tasks",
    metadata,
    sqlalchemy.Column("task_id", sqlalchemy.String, primary_key=True),
    sqlalchemy.Column("task_type", sqlalchemy.String, nullable=False),
    sqlalchemy.Column("payload", sqlalchemy.JSON, nullable=False),
    sqlalchemy.Column("status", sqlalchemy.String, default="PENDING"),
    sqlalchemy.Column("priority", sqlalchemy.Integer, default=5),
    sqlalchemy.Column("max_retries", sqlalchemy.Integer, default=3),
    sqlalchemy.Column("retry_count", sqlalchemy.Integer, default=0),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime),
    sqlalchemy.Column("started_at", sqlalchemy.DateTime, nullable=True),
    sqlalchemy.Column("completed_at", sqlalchemy.DateTime, nullable=True),
    sqlalchemy.Column("result", sqlalchemy.JSON, nullable=True),
    sqlalchemy.Column("error", sqlalchemy.Text, nullable=True),
)

engine = sqlalchemy.create_engine(DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://"))


async def connect_db():
    await database.connect()
    print("✅ PostgreSQL connected")


async def disconnect_db():
    await database.disconnect()


def create_tables():
    """Run once to create tables in Supabase"""
    metadata.create_all(engine)
    print("✅ Tables created")


# ─── CRUD Operations ──────────────────────────────────────────

async def insert_task(task_data: dict):
    query = tasks_table.insert().values(**task_data)
    await database.execute(query)


async def get_task(task_id: str):
    query = tasks_table.select().where(tasks_table.c.task_id == task_id)
    return await database.fetch_one(query)


async def get_all_tasks(limit: int = 50):
    query = tasks_table.select().order_by(
        tasks_table.c.created_at.desc()
    ).limit(limit)
    return await database.fetch_all(query)


async def update_task_status(task_id: str, updates: dict):
    query = tasks_table.update().where(
        tasks_table.c.task_id == task_id
    ).values(**updates)
    await database.execute(query)


async def get_tasks_by_status(status: str):
    query = tasks_table.select().where(tasks_table.c.status == status)
    return await database.fetch_all(query)


async def get_metrics():
    """Returns count of tasks grouped by status"""
    query = sqlalchemy.text("""
        SELECT status, COUNT(*) as count 
        FROM tasks 
        GROUP BY status
    """)
    return await database.fetch_all(query)