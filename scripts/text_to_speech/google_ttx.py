from pathlib import Path
import os
from gtts import gTTS

from tqdm import tqdm

def init_model():
    return


def text_to_speech(text, output_path, pbar=None):
    tts = gTTS(text, 'com')
    tts.save(output_path)
    if pbar:
        pbar.update(1)

def add_narrations(story_dir, force=False, workers=3):
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    pbar = tqdm(total=len(line_folders), desc='Creating voice recordings')
    for index, line_folder in enumerate(line_folders):
        if ((line_folder / 'line.txt').exists() and not (line_folder / 'line.mp3').exists()) or force:
            line_text = (line_folder / 'line.txt').read_text()
            text_to_speech(line_text, line_folder /'line.mp3', pbar)


if __name__ == '__main__':
    story_dir_ = Path("stories/Whiskers in the Morning Star")
    add_narrations(story_dir_, force=True)