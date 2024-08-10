import os
from pathlib import Path

from scripts.text_generation.create_all import create_full_story
from scripts.sounds_and_music.sound_scraper import scrape_sounds
from scripts.text_to_speech.text_to_speech import create_recordings
from scripts.image_generation.generate_story_images import add_story_images
from scripts.video_editing.story_to_video import create_video


def create_story(story_prompt, story_title=None):
    if story_title is None:
        story_folder = create_full_story(story_prompt)
    else:
        story_folder = Path() / 'stories' / story_title
    add_story_images(story_folder)
    scrape_sounds(story_folder)
    create_recordings(story_folder)
    create_video(story_folder)


if __name__ == '__main__':
    prompt = ("write me a very short story about a hospital named 'the vally' in afula, israel. "
              "the hospital decided to add a gym to the hospital employees, it was very good. add to the story about the benefits of a gym in a workplace")
    create_story(prompt, 'The Valley’s Transformation')
