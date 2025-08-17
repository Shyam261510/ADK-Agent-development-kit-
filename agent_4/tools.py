from pymongo import MongoClient
from datetime import datetime, timedelta

client = MongoClient(
    "mongodb+srv://plug_api:shyam261510@cluster0.izdmd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
db = client["task_manager"]
tasks_collection = db["tasks"]


def addTask(description: str, due_date: str) -> dict:
    """Add a task with description and due_date (YYYY-MM-DD HH:MM)."""

    task = {
        "description": description,
        "due_date": due_date,
        "status": "Pending",
        "created_at": datetime.now(),
    }

    tasks_collection._insert_one(task)

    return {"message": f"Task '{description}' added successfully!"}


def remind_task(min_ahead: int = 60) -> dict:
    """Get tasks due in the next X minutes."""
    now = datetime.now()
    future_time = now + timedelta(minutes=min_ahead)

    tasks = list(
        tasks_collection.find(
            {"due_date": {"$gte": now, "$lte": future_time}, "status": "Pending"}
        )
    )

    return {
        "upcoming_task": [
            {"description": task["description"], "due_date": str(task["due_date"])}
            for task in tasks
        ]
    }
