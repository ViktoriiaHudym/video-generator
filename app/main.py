import uuid

from fastapi import FastAPI, HTTPException

from app.models import TaskPayload
from app.utils.composing_helper import CombinationBuilder, MetadataComposer
from app.utils.gcs_client_helper import get_gcs_client

app = FastAPI()

gcs_client = get_gcs_client()


@app.post("/generate")
async def generate_video_combinations(task_details: TaskPayload):
    if not get_gcs_client:
        raise HTTPException(status_code=500, detail='GCS client is not availiable')

    task_id = str(uuid.uuid4())

    composer = MetadataComposer(gcs_client)
    builder = CombinationBuilder(task_details)

    gcs_urls = []

    try:
        combinations = builder.build_combinations()
        
        for i, combination in enumerate(combinations):    
            video_metadata = composer.process_combination(combination)
            
            gcs_url = composer.upload_to_gcs(video_metadata, remote_path=f'{task_id}/{i+1}.json')
            gcs_urls.append(gcs_url)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'An unexpected error occured: {e}')
    
    return {
        'task_id': task_id,
        'task_name': task_details.task_name,
        'message': f'Combinations for the task generated successfully. See them in GCS',
        'gcs_urls': gcs_urls,
        'status': 'success'
    }
