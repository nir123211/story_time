import requests
from misc import keys


def init_model(story_dir):
    return (story_dir / "voice.txt").read_text()


def generate_speech(voice_id, text, output_path, prev_text, next_text, pbar=None):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
      "Accept": "audio/mpeg",
      "Content-Type": "application/json",
      "xi-api-key": keys.eleven_key
    }

    data = {
      "text": text,
      "model_id": "eleven_monolingual_v1",
      "voice_settings": {
        "stability": 0.8,
        "similarity_boost": 0.5
      }

    }

    response = requests.post(url, json=data, headers=headers)
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
    if pbar:
        pbar.update(1)

