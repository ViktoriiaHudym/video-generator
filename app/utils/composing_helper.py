import json
import random
from itertools import chain, product
from typing import Dict, Iterator, List

import ffmpeg
from google.cloud.storage import Client

from config import GCS_BUCKET_NAME, logger
from models import TaskPayload, VoiceItem


class Combination:
    def __init__(self, video_blocks: List[str], audio_url: str, voice_item: VoiceItem):
        self.video_blocks = video_blocks
        self.audio_url = audio_url
        self.voice_item = voice_item


class CombinationBuilder:
    def __init__(self, payload: TaskPayload):
        self.payload = payload

    def _get_all_video_combinations(self) -> Iterator[tuple]:
        video_groups = self.payload.video_blocks.values()
        if not video_groups:
            return iter([])
        return product(*video_groups)

    def build_combinations(self) -> Iterator[Combination]:
        all_audios = self._flatten_dict_values(self.payload.audio_blocks)
        all_voices = self._flatten_dict_values(self.payload.voice_blocks)

        if not all_audios or not all_voices:
            raise ValueError("Audio blocks and voice blocks cannot be empty.")

        for video_combo_tuple in self._get_all_video_combinations():
            random_audio = random.choice(all_audios)
            random_voice = random.choice(all_voices)
            yield Combination(
                video_blocks=list(video_combo_tuple),
                audio_url=random_audio,
                voice_item=random_voice
            )
    
    @staticmethod
    def _flatten_dict_values(dict_data: Dict) -> List:
        if not dict_data:
            return []
        return list(chain.from_iterable(dict_data.values()))


class MetadataComposer:
    def __init__(self, gcs_client: Client):
        self.gcs_client = gcs_client

    def process_combination(self, combination: Combination) -> Dict:
        video_segments = []
        total_duration = 0.0
        
        for i, video_url in enumerate(combination.video_blocks):
            metadata = self.get_video_metadata(video_url)
            segment_data = {
                "block_order": i,
                "url": video_url,
                **metadata
            }
            video_segments.append(segment_data)
            if "duration" in metadata:
                total_duration += metadata["duration"]
        
        final_json = {
            "total_duration_seconds": round(total_duration, 2),
            "background_audio_url": combination.audio_url,
            "selected_voice_block": combination.voice_item.model_dump(),
            "video_segments": video_segments
        }
        return final_json
    
    @staticmethod
    def get_video_metadata(url: str) -> Dict:
        try:
            probe = ffmpeg.probe(url)
            video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
            if video_stream is None:
                logger.warning("No video stream found for URL: %s" % url)
                return {"error": "No video stream found"}
            
            return {
                "duration": float(video_stream.get('duration', 0)),
                "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}"
            }
        except ffmpeg.Error as e:
            logger.warning("FFmpeg error: %s \nURL: %s" % (e.stderr.decode('utf8'), url))
            return {"error": f"FFmpeg error: {e.stderr.decode('utf8')}"}

    def upload_to_gcs(self, data: Dict, remote_path: str) -> str:
        bucket = self.gcs_client.bucket(GCS_BUCKET_NAME)
        blob = bucket.blob(remote_path)
        
        json_data = json.dumps(data, indent=4)
        
        blob.upload_from_string(json_data, content_type='application/json')

        logger.info("File ...%s successfully uploaded to GCS bucket" % remote_path)
        return f"https://storage.cloud.google.com/{GCS_BUCKET_NAME}/{remote_path}"
