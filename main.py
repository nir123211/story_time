from pathlib import Path

from scripts.text_generation.character_descriptions import add_characters
from scripts.text_generation.story import create_story
from scripts.text_generation.sound_prompts import add_sound_prompts
from scripts.text_generation.image_prompts import add_image_prompts
from scripts.sounds_and_music.elevenlabs_sound_generator import add_music, add_sounds_mp3
from scripts.video_editing.story_to_video import create_video_lines, merge_video_chunks, finalize_video
from scripts.text_to_speech.google_ttx import add_narrations
from scripts.text_to_speech.elevenlabs_api import add_narrations
from scripts.image_generation.flux_schnell import generate_story_images


def make_story(prompt, story_dir=None):
    if prompt:
        story_dir = create_story(prompt)
    add_characters(story_dir)
    add_image_prompts(story_dir)
    add_sound_prompts(story_dir)
    add_sounds_mp3(story_dir)
    add_music(story_dir)
    add_narrations(story_dir)
    generate_story_images(story_dir)
    create_video_lines(story_dir)
    merge_video_chunks(story_dir)
    finalize_video(story_dir)


if __name__ == '__main__':
    my_prompt = ""
    my_dir = Path("stories\\The Shirtless Saga of Moriah Battalion's Communications Unit")
    make_story(my_prompt, my_dir)


