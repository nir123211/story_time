import os
import requests
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from misc import keys
from gtts import gTTS
from tqdm import tqdm


def generate_speech(text, file_path, pbar=None):
    tts = gTTS(text, 'com')
    tts.save(file_path)
    if pbar:
        pbar.update(1)


def create_recordings(story_dir):
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    pbar = tqdm(total=len(line_folders))
    processes = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for line_folder in tqdm(line_folders, desc='Creating voice recordings'):
            if (line_folder / 'line.txt').exists() and not (line_folder / 'line.mp3').exists():
                line_text = (line_folder / 'line.txt').read_text()
                # tts_elevenlabs(line_text, os.path.join(line_folder, 'line.mp3'), pbar)
                processes.append(pool.submit(generate_speech, line_text, os.path.join(line_folder, 'line.mp3'), pbar))
    [process.result() for process in processes]
