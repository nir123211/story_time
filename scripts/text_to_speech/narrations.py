import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from scripts.text_to_speech.local import google_ttx
from scripts.text_to_speech.api import elevenlabs_api

local_models = {"gtts": google_ttx}
api_models = {"elevenlabs": elevenlabs_api}
all_models = {"local": local_models, "api": api_models}


def create_recordings(story_dir, model_script, force=False):
    model = model_script.init_model(story_dir)

    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    processes = []
    pbar = tqdm(total=len(line_folders), desc='Creating voice recordings')
    with ThreadPoolExecutor(max_workers=3) as pool:
        for index, line_folder in enumerate(line_folders):
            if ((line_folder / 'line.txt').exists() and not (line_folder / 'line.mp3').exists()) or force:
                prev_line = ""
                if index > 0:
                    prev_line = (line_folders[index-1] / 'line.txt').read_text()
                next_line = ""
                if index < len(line_folders):
                    next_line = (line_folders[index-1] / 'line.txt').read_text()
                line_text = (line_folder / 'line.txt').read_text()
                processes.append(pool.submit(model_script.generate_speech, model, line_text,
                                             line_folder/'line.mp3', prev_line, next_line, pbar))
    [process.result() for process in processes]


if __name__ == '__main__':
    story_dir = Path("../../stories/A Lifetime of Laughter")
    create_recordings(story_dir, elevenlabs_api, force=True)