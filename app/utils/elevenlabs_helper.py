from elevenlabs.client import ElevenLabs

from app.config import ELEVENLABS_API_KEY


def get_elevenlabs_client():
    if not ELEVENLABS_API_KEY:
        return None
    return ElevenLabs(api_key=ELEVENLABS_API_KEY)


def generate_voice_from_11labs_api(text: str, voice_id: str = "JBFqnCBsd6RMkjVDRZzb", model: str = 'eleven_turbo_v2'):
    client = get_elevenlabs_client()
    if not client:
        raise ConnectionError("ElevenLabs API key is not configured.")

    audio_stream = client.text_to_speech.convert(
        voice_id=voice_id,
        text=text,
        model_id=model,
        output_format="mp3_44100_128",
    )
    
    chunks = [chunk for chunk in audio_stream if isinstance(chunk, bytes)]
    
    return b''.join(chunks)
