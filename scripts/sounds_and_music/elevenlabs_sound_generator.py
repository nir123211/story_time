from pathlib import Path
import os
import shutil
from concurrent.futures import ThreadPoolExecutor

from elevenlabs import ElevenLabs
from tqdm import tqdm

client = ElevenLabs(api_key=os.environ["ELEVEN_KEY"])


def generate_sound(prompt, output_path, pbar):
    data = client.text_to_sound_effects.convert(
        text=prompt,
        duration_seconds=6)

    with open(output_path, "wb") as f:
        for chunk in data:
            f.write(chunk)
    if pbar:
        pbar.update(1)


def add_sounds_mp3(story_dir):
    print('Adding sounds:')
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]
    pbar = tqdm(total=len(lines), desc="generating sound effects")
    processes = []
    with ThreadPoolExecutor(max_workers=3) as process_pool:
        for line_folder in tqdm(line_folders, desc='Getting sounds and music'):
            if (line_folder / 'sound.txt').exists() and not (line_folder / 'sound.mp3').exists():
                effect_query = (line_folder / 'sound.txt').read_text()
                print(f'Adding effect: {effect_query}')
                processes.append(process_pool.submit(generate_sound, effect_query, os.path.join(line_folder, 'sound.mp3'), pbar))
            else:
                pbar.update(1)
    processes = [process.result() for process in processes]


def add_music(story_dir):
    music_folder = Path.cwd()/"scripts"/"sounds_and_music"/"music"
    print('Adding sounds:')
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    for line_folder in tqdm(line_folders, desc='Getting sounds and music'):
        if (line_folder / 'music.txt').exists() and not (line_folder / 'music.mp3').exists():
            music_query = (line_folder / 'music.txt').read_text()
            print(f'Adding music: {music_query}')
            shutil.copyfile(music_folder/music_query, line_folder/"music.mp3")
