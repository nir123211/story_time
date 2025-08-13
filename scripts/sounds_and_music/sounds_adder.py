from tqdm import tqdm
from pathlib import Path
import os
import shutil
from scripts.sounds_and_music.sound_api import add_sounds_mp3


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
