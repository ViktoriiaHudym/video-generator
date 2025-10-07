from typing import Dict, List

from pydantic import BaseModel


class VoiceItem(BaseModel):
    text: List[str]
    voice: str

class TaskPayload(BaseModel):
    task_name: str
    video_blocks: Dict[str, List[str]]
    audio_blocks: Dict[str, List[str]]
    voice_blocks: Dict[str, List[VoiceItem]]
