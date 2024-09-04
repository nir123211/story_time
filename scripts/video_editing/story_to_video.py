import os
import random
import cv2 as cv
import numpy as np
from moviepy.editor import (VideoClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip,
                            AudioClip, concatenate_audioclips, VideoFileClip, ImageClip)
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_normalize import audio_normalize
import textwrap
import ffmpeg
from pathlib import Path


def display_text(image, text):
    font = cv.FONT_HERSHEY_SIMPLEX

    wrapped_text = textwrap.wrap(text, width=60)
    font_size = 1
    font_thickness = 1

    for i, line in enumerate(wrapped_text):
        textsize = cv.getTextSize(line, font, font_size, font_thickness)[0]
        gap = textsize[1] + 15
        y = int(850+textsize[1]) + i * gap
        x = int((image.shape[1] - textsize[0]) / 2)

        text_w, text_h = textsize
        cv.rectangle(image, (x - 3, y+8), (x+3+text_w, y-text_h-6), (0, 0, 0), -1)
        cv.putText(image, line, (x, y), font,
                   font_size,
                   (255, 255, 255),
                   font_thickness,
                   lineType=cv.LINE_AA)


def create_line_video(line_dir: Path, force=False):
    if (line_dir / 'line.mp4').exists() and not force:
        return
    if not (line_dir / 'image.png').exists():
        raise ValueError("No image in folder")

    image = cv.imread(str(line_dir / 'image.png'))
    image = cv.cvtColor(image, cv.COLOR_BGR2RGB)

    line_text = (line_dir / 'line.txt').read_text()
    random_location = (random.randrange(300, 800), random.randrange(300, 800))

    def make_frame(t):
        zoom_amount = float(t / 100)
        frame = cv.resize(image[int(random_location[1] * zoom_amount):
                                int(1024 - (1024 - random_location[1]) * zoom_amount),
                          int(random_location[0] * zoom_amount):
                          int(1024 - (1024 - random_location[0]) * zoom_amount)],
                          (1024, 1024))
        display_text(frame, line_text)
        return frame

    dub = (AudioFileClip(str(line_dir / 'line.mp3')).fx(audio_normalize).fx(audio_fadeout, 0.5).
           fx(volumex, 0.8))

    sounds = dub
    if (line_dir / 'sound.mp3').exists():
        try:
            effect = ((AudioFileClip(str(line_dir / 'sound.mp3')).fx(audio_normalize).fx(volumex, 0.2))
                      .fx(audio_fadeout, 1))
        except ZeroDivisionError:
            effect = ((AudioFileClip(str(line_dir / 'sound.mp3')).fx(volumex, 0.2)).fx(audio_fadeout, 1))

        if effect.duration < dub.duration:
            silence_clip = AudioClip(lambda t: [0], duration=dub.duration)
            effect = concatenate_audioclips([effect, silence_clip]).fx(audio_fadein, 3).fx(audio_fadeout, 1)
        sounds = CompositeAudioClip([effect, dub]).set_duration(t=dub.duration)

    sounds = concatenate_audioclips([sounds, AudioClip(lambda t: [0], duration=1)])
    clip = VideoClip(make_frame, duration=sounds.duration).set_audio(sounds)
    clip.write_videofile(str(line_dir / 'line.mp4'), fps=25)


def create_video_lines(story_dir):
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]
    for line in line_folders:
        create_line_video(line)

def merge_video_chunks(story_dir):
    lines = [line for line in os.listdir(story_dir) if os.path.isdir(os.path.join(story_dir, line))
             and 'tmp' not in line]
    lines = sorted(lines, key=lambda line: int(line.replace('line', '')))
    os.makedirs(os.path.join(story_dir, 'tmp'), exist_ok=True)
    index = 1
    clip = None
    music_clip = None
    for line in lines:
        line_path = os.path.join(story_dir, line)
        if 'music.mp3' in os.listdir(line_path):
            if clip is not None:
                if music_clip is not None:
                    new_audio_clip = CompositeAudioClip([clip.audio, music_clip]).set_duration(clip.duration)
                    clip = clip.set_audio(new_audio_clip).fx(audio_fadeout, 1)
                clip.write_videofile(os.path.join(story_dir, 'tmp', f'clip{index}.mp4'), fps=25, bitrate='1500k')
                index += 1
            clip = VideoFileClip(os.path.join(line_path, 'line.mp4'))
            music_clip = AudioFileClip(os.path.join(line_path, 'music.mp3')).fx(audio_normalize).fx(volumex, 0.2)
        elif line == 'line0':
            clip = VideoFileClip(os.path.join(line_path, 'line.mp4'))
        else:
            clip_to_add = VideoFileClip(os.path.join(line_path, 'line.mp4'))
            clip = concatenate_videoclips([clip, clip_to_add])
    new_audio_clip = CompositeAudioClip([clip.audio, music_clip]).set_duration(clip.duration)
    clip = clip.set_audio(new_audio_clip).fx(audio_fadeout, 1)
    clip.write_videofile(os.path.join(story_dir, 'tmp', f'clip{index}.mp4'), fps=25)


def finalize_video(story_dir):
    story_name = story_dir.stem
    tmp_folder = story_dir / 'tmp'
    clips = [clip for clip in os.listdir(tmp_folder)]
    clips = sorted(clips, key=lambda filename: int(filename.replace('clip', '').replace('.mp4', '')))
    video = None
    for index, clip in enumerate(clips):
        if index == 0:
            video = VideoFileClip(os.path.join(tmp_folder, clip))
        else:
            video = concatenate_videoclips([video, VideoFileClip(os.path.join(tmp_folder, clip))])
    video = (concatenate_videoclips([video,
                                     ImageClip(np.zeros([1024, 1024, 3]), duration=100)]).set_duration(video.duration))
    video.write_videofile(os.path.join(story_dir, f'{story_name}.mp4'), fps=24, audio_bitrate='128k', codec='libx264')
    input_opts = {
        'format': 'mp4',
    }
    output_opts = {
        'format': 'matroska',
    }
    (ffmpeg.input(os.path.join(story_dir, f'{story_name}.mp4'), **input_opts).
     output(os.path.join(story_dir, f'{story_name}.mkv'), **output_opts).run())
    os.remove(os.path.join(story_dir, f'{story_name}.mp4'))
    input_opts = {
        'format': 'matroska',
    }
    output_opts = {
        'format': 'mp4',
    }
    (ffmpeg.input(os.path.join(story_dir, f'{story_name}.mkv'), **input_opts).
     output(os.path.join(story_dir, f'{story_name}.mp4'), **output_opts).run())


def create_video(story_dir):
    create_video_chunks(story_dir)
    merge_video_chunks(story_dir)
    finalize_video(story_dir)


if __name__ == '__main__':
    story_dire = r'C:\programing\python_projects\StoryTime\stories\The Hilarious Hassle on the Hellenic Seas'
