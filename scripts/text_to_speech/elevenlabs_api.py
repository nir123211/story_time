import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from tqdm import tqdm
from elevenlabs import ElevenLabs
from scripts.text_to_speech import voices

ELEVEN_LABS_WORKERS = 2


def text_to_speech(voice_id, text, output_path, pbar=None):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/Z3R5wn05IrDiVCyEkUrK"

    client = ElevenLabs(api_key="1effddbb452b2a49fdeebbe53189391a")
    audio = client.text_to_speech.convert(
        voice_id="Z3R5wn05IrDiVCyEkUrK",
        model_id="eleven_v3",
        text=text,
        output_format="mp3_44100_128",
    )

    with open(output_path, "wb") as f:
        for chunk in audio:
            if chunk:
                f.write(chunk)
    if pbar:
        pbar.update(1)


def add_narrations(story_dir, force=False):
    voice_id = voices.get_random_voice()
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    processes = []
    pbar = tqdm(total=len(line_folders), desc='Creating voice recordings')
    with ThreadPoolExecutor(max_workers=ELEVEN_LABS_WORKERS) as pool:
        for index, line_folder in enumerate(line_folders):
            if ((line_folder / 'line.txt').exists() and not (line_folder / 'line.mp3').exists()) or force:
                # for future use
                # prev_line = ""
                # if index > 0:
                #     prev_line = (line_folders[index-1] / 'line.txt').read_text()
                # next_line = ""
                # if index < len(line_folders):
                #     next_line = (line_folders[index-1] / 'line.txt').read_text()
                line_text = (line_folder / 'line.txt').read_text()
                if ELEVEN_LABS_WORKERS > 1:
                    processes.append(pool.submit(text_to_speech, voice_id, line_text,
                                                 line_folder /'line.mp3', pbar))
                else:
                    text_to_speech(voice_id, line_text, (line_folder /'line.mp3'), pbar)
            if ELEVEN_LABS_WORKERS > 1:
                [process.result() for process in processes]


if __name__ == '__main__':
    story_dir_ = Path("stories/Whiskers in the Morning Star")
    add_narrations(story_dir_, force=True)