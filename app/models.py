from typing import Dict, List

from pydantic import BaseModel


class VoiceItem(BaseModel):
    """Defines the structure for a voice block item."""
    text: List[str]
    voice: str

class TaskPayload(BaseModel):
    """Defines the input payload for the video generation task."""
    task_name: str
    video_blocks: Dict[str, List[str]]
    audio_blocks: Dict[str, List[str]]
    voice_blocks: Dict[str, List[VoiceItem]]

class GenerateResponse(BaseModel):
    """Defines the successful response structure for the generation endpoint."""
    task_id: str
    task_name: str
    message: str
    gcs_urls: List[str]
    status: str = "success"
