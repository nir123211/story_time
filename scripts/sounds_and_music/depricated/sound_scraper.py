import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yt_dlp
from tqdm import tqdm


def download_mp3(youtube_query, output_path, mp3_time, tries=1):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path.replace('.mp3', ''),
        'postprocessor_args': [
            '-t', str(mp3_time)  # Duration of the audio to be downloaded (10 seconds)
        ],
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        videos = ydl.extract_info(f"ytsearch{3}:{youtube_query}", download=False)['entries']
        for video in videos:
            if video.get("live_status") == "is_live":
                continue
            else:
                ydl.download(video['webpage_url'])
                break
        else:
            raise ValueError("POOPOOOO")


def scrape_sounds(story_dir):
    print('Adding music and sounds:')
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]

    with ThreadPoolExecutor(max_workers=8) as process_pool:
        for line_folder in tqdm(line_folders, desc='Getting sounds and music'):
            if (line_folder / 'music.txt').exists() and not (line_folder / 'music.mp3').exists():
                music_query = (line_folder / 'music.txt').read_text(), 'less than 1 hour'
                print(f'Adding music: {music_query}')
                process_pool.submit(download_mp3, music_query, os.path.join(line_folder, 'music.mp3'), 120, 5)
                # download_mp3(music_query, os.path.join(line_folder, 'music.mp3'), 120)
            if (line_folder / 'sound.txt').exists() and not (line_folder / 'sound.mp3').exists():
                effect_query = (line_folder / 'sound.txt').read_text(), 'sounds short'
                print(f'Adding effect: {effect_query}')
                # download_mp3(effect_query, os.path.join(line_folder, 'sound.mp3'), 10)
                process_pool.submit(download_mp3, effect_query, os.path.join(line_folder, 'sound.mp3'), 10)


if __name__ == '__main__':
    download_mp3("fireplace sounds", "laugh.mp3", 10)