import random
from itertools import chain, product
from typing import Dict, Iterator, List

import ffmpeg
from google.cloud import storage

from app.config import get_logger
from app.models import TaskPayload, VoiceItem

logger = get_logger(__name__)


class Combination:
    """Represents a single combination of video, audio, and voice."""
    def __init__(self, video_blocks: List[str], audio_url: str, voice_item: VoiceItem):
        self.video_blocks = video_blocks
        self.audio_url = audio_url
        self.voice_item = voice_item

class CombinationBuilder:
    """
    Generates unique combinations of video, audio, and voice assets.
    """
    def __init__(self, payload: TaskPayload):
        self.payload = payload

    def _get_all_video_combinations(self) -> Iterator[tuple[str, ...]]:
        video_groups = self.payload.video_blocks.values()
        if not video_groups:
            return iter([])
        return product(*video_groups)

    def build_combinations(self) -> Iterator[Combination]:
        """
        Builds and yields unique combinations from the provided task payload.

        Yields:
            An iterator of Combination objects.

        Raises:
            ValueError: If audio or voice blocks are empty.
        """
        all_audios = self._flatten_dict_values(self.payload.audio_blocks)
        all_voices = self._flatten_dict_values(self.payload.voice_blocks)

        if not all_audios or not all_voices:
            raise ValueError("Audio and voice blocks cannot be empty.")

        for video_combo_tuple in self._get_all_video_combinations():
            random_audio = random.choice(all_audios)
            random_voice = random.choice(all_voices)
            yield Combination(
                video_blocks=list(video_combo_tuple),
                audio_url=random_audio,
                voice_item=random_voice,
            )

    @staticmethod
    def _flatten_dict_values(data: Dict[str, List]) -> List:
        """Flattens a dictionary's list values into a single list."""
        if not data:
            return []
        return list(chain.from_iterable(data.values()))


class VideoCombinationsService:
    def __init__(self, storage_service: storage):
        self.storage_service = storage_service

    def generate_and_upload_combinations(self, task_payload: TaskPayload, task_id: str) -> List[str]:
        """
        Generates combinations, processes metadata, and uploads to storage.

        Args:
            task_payload: The input data defining the task.
            task_id: A unique identifier for the task.

        Returns:
            A list of GCS URLs for the generated metadata files.
        """
        builder = CombinationBuilder(task_payload)
        combinations = builder.build_combinations()
        gcs_urls = []

        for i, combination in enumerate(combinations):
            final_json = self._process_single_combination(combination)
            remote_path = f"{task_id}/{i + 1}.json"
            gcs_url = self.storage_service.upload_json(final_json, remote_path)
            gcs_urls.append(gcs_url)

        return gcs_urls

    def _process_single_combination(self, combination: Combination) -> Dict:
        """Processes a single combination to generate its final metadata JSON."""
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
        
        return {
            "total_duration_seconds": round(total_duration, 2),
            "background_audio_url": combination.audio_url,
            "selected_voice_block": combination.voice_item.model_dump(),
            "video_segments": video_segments
        }

    @staticmethod
    def get_video_metadata(url: str) -> Dict:
        """
        Probes a video URL to extract metadata like duration and resolution.
        """
        try:
            probe = ffmpeg.probe(url)
            video_stream = next(
                (s for s in probe["streams"] if s["codec_type"] == "video"), None
            )
            if not video_stream:
                logger.warning("No video stream found for URL: %s" % url)
                return {"error": "No video stream found"}
            
            return {
                "duration": float(video_stream.get('duration', 0)),
                "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}"
            }
        except ffmpeg.Error as e:
            error_message = e.stderr.decode("utf-8", errors="ignore")
            logger.error("FFmpeg error for URL %s: %s", url, error_message)
            return {"error": f"FFmpeg error: {error_message}"}
        