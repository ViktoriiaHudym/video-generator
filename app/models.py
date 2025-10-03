from typing import List, Dict
from pydantic import BaseModel, HttpUrl

class VoiceItem(BaseModel):
    text: List[str]
    voice: str

class TaskPayload(BaseModel):
    task_name: str
    video_blocks: Dict[str, List[HttpUrl]]
    audio_blocks: Dict[str, List[HttpUrl]]
    voice_blocks: Dict[str, List[VoiceItem]]
    