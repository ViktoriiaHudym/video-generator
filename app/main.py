import uuid

from fastapi import FastAPI, HTTPException, status

from app.models import GenerateResponse, TaskPayload
from app.utils.composing_helper import VideoCombinationsService
from app.utils.gcs_client_helper import get_storage_service

app = FastAPI()

storage_service = get_storage_service()


@app.post("/generate", response_model=GenerateResponse)
def generate_video_combinations(task_details: TaskPayload):
    """
    Endpoint to generate video combinations based on a task payload.
    """
    task_id = str(uuid.uuid4())

    try:
        video_service = VideoCombinationsService(storage_service)
        
        gcs_urls = video_service.generate_and_upload_combinations(
            task_payload=task_details, task_id=task_id
        )

        return GenerateResponse(
            task_id=task_id,
            task_name=task_details.task_name,
            message="Combinations for the task generated successfully.",
            gcs_urls=gcs_urls,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"External service error: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {e}",
        )
    
