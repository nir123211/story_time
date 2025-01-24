import os
import random
import cv2 as cv
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import (VideoClip, AudioFileClip, concatenate_videoclips, CompositeAudioClip,
                            AudioClip, concatenate_audioclips, VideoFileClip, ImageClip)
from moviepy.audio.fx.volumex import volumex
from moviepy.audio.fx.audio_fadein import audio_fadein
from moviepy.audio.fx.audio_fadeout import audio_fadeout
from moviepy.audio.fx.audio_normalize import audio_normalize
import textwrap
import ffmpeg
from pathlib import Path


def wrap_text(text, font, max_width, draw):
    """
    Wraps text into multiple lines if it exceeds the max width.
    """
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        text_bbox = draw.textbbox((0, 0), test_line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    # Add the last line
    if current_line:
        lines.append(current_line)

    return lines


def add_subtitle_to_existing_image(image_array, text):
    # Convert the image array to a Pillow Image
    image = Image.fromarray(image_array).convert("RGBA")

    # Create an overlay for drawing text
    overlay = Image.new("RGBA", image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)

    # Load a font
    font_size = int(image.size[1] * 0.03)  # Adjust font size relative to image height
    font = ImageFont.truetype("arial.ttf", font_size)  # Replace with a valid font file

    # Maximum width for the text
    max_width = int(image.size[0] * 0.9)  # 90% of the image width

    # Wrap text to fit within the max width
    lines = wrap_text(text, font, max_width, draw)

    # Calculate total text height (including line spacing)
    line_spacing = 10
    total_text_height = sum(draw.textbbox((0, 0), line, font=font)[3] for line in lines) + (len(lines) - 1) * line_spacing

    # Starting Y position to center the text block vertically near the bottom
    y = image.size[1] - total_text_height - 30

    # Add a semi-transparent background rectangle for the text block
    background_margin = 10
    draw.rectangle(
        [(0, y - background_margin), (image.size[0], y + total_text_height + background_margin)],
        fill=(0, 0, 0, 150),  # Semi-transparent black
    )

    # Draw each line of text
    for line in lines:
        text_bbox = draw.textbbox((0, 0), line, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (image.size[0] - text_width) // 2
        draw.text((x, y), line, font=font, fill="white")
        y += text_height + line_spacing

    # Combine the image and overlay
    combined = Image.alpha_composite(image, overlay)

    # Write the modified image back to the existing image array
    modified_image = np.array(combined.convert("RGB"))
    image_array[:, :, :] = modified_image


def create_line_video(line_dir: Path, force=False):
    if (line_dir / 'line.mp4').exists() and not force:
        return
    if not (line_dir / 'image.png').exists():
        raise ValueError(f"No image in folder {line_dir}")

    print("papa")
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
        add_subtitle_to_existing_image(frame, line_text)
        return frame

    dub = (AudioFileClip(str(line_dir / 'line.mp3')).fx(audio_normalize).fx(audio_fadeout, 0.5).
           fx(volumex, 0.8))

    sounds = dub
    if (line_dir / 'sound.mp3').exists():
        try:
            effect = ((AudioFileClip(str(line_dir / 'sound.mp3')).fx(audio_normalize).fx(volumex, 0.2))
                      .fx(audio_fadeout, 1))
        except ZeroDivisionError:
            effect = ((AudioFileClip(str(line_dir / 'sound.mp3')).fx(volumex, 0.2)).fx(audio_fadeout, 1.5))

        if effect.duration < dub.duration:
            silence_clip = AudioClip(lambda t: [0], duration=dub.duration)
            effect = concatenate_audioclips([effect, silence_clip]).fx(audio_fadein, 3).fx(audio_fadeout, 1)
        sounds = CompositeAudioClip([effect, dub]).set_duration(t=dub.duration)

    sounds = concatenate_audioclips([sounds, AudioClip(lambda t: [0], duration=1)])
    clip = VideoClip(make_frame, duration=sounds.duration).set_audio(sounds)
    clip.write_videofile(str(line_dir / 'line.mp4'), fps=25)


def create_video_lines(story_dir, force=False):
    lines = [line for line in os.listdir(story_dir) if (story_dir / line).is_dir() and 'line' in line]
    lines = sorted(lines, key=lambda folder: int(folder.replace('line', '')))
    line_folders: [Path] = [(story_dir / line) for line in lines if (story_dir / line).is_dir()]
    for line in line_folders:
        create_line_video(line, force)


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
                try:
                    clip.write_videofile(os.path.join(story_dir, 'tmp', f'clip{index}.mp4'), fps=25, bitrate='1500k')
                except IndexError:
                    ...
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


if __name__ == '__main__':
    lala = Path("../../stories/A Lifetime of Laughter")
    create_video_lines(lala, force=True)
    merge_video_chunks(lala)
    finalize_video(lala)