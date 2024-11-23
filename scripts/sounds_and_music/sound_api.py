from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
from elevenlabs import ElevenLabs
from misc.keys import eleven_key

client = ElevenLabs(api_key=eleven_key)


def generate_sound(prompt, output_path):
    data = client.text_to_sound_effects.convert(
        text=prompt,
        duration_seconds=6)

    with open(output_path, "wb") as f:
        for chunk in data:
            f.write(chunk)


def add_sounds_mp3(story_dir):
    print('Adding sounds:')
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    with ThreadPoolExecutor(max_workers=2) as process_pool:
        for line_folder in tqdm(line_folders, desc='Getting sounds and music'):
            if (line_folder / 'sound.txt').exists() and not (line_folder / 'sound.mp3').exists():
                effect_query = (line_folder / 'sound.txt').read_text()
                print(f'Adding effect: {effect_query}')
                process_pool.submit(generate_sound, effect_query, os.path.join(line_folder, 'sound.mp3'))
