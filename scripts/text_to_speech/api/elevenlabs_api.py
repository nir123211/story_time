from pathlib import Path
from elevenlabs import ElevenLabs
from elevenlabs import VoiceSettings
from misc import keys


def init_model(story_dir):
    return (story_dir / "voice.txt").read_text()


def generate_speech(voice_id, text, output_path, prev_text, next_text, pbar=None):

    client = ElevenLabs(
        api_key=keys.eleven_key,
    )
    response = client.text_to_speech.convert(
        voice_id=voice_id,
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        previous_text=prev_text,
        next_text=next_text,
        # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.5,
            style=0.5,
            use_speaker_boost=False,
        ),
    )
    with open(output_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)

