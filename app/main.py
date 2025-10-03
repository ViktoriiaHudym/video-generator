from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import utils
import uuid
from models import TaskPayload, VoiceItem

app = FastAPI()


@app.post("/generate")
async def generate_videos(task: TaskPayload, background_tasks: BackgroundTasks = None):
    
    task_id = str(uuid.uuid4())
    # background_tasks.add_task()

    return {
        "status": "success",
        "message": f"Task '{task.task_name}' successfully created.",
        "task_id": task_id
    }


