import os

from scripts.text_generation.create_story import create_story
from scripts.text_generation.create_characters import create_characters
from scripts.text_generation.create_image_prompts import add_image_prompts
from scripts.text_generation.create_sounds import add_sounds


def create_full_story(prompt):
    story_dir = create_story(prompt)
    create_characters(story_dir)
    add_image_prompts(story_dir)
    add_sounds(story_dir)
    return story_dir


if __name__ == '__main__':
    os.chdir("../..")
    create_full_story("a very short story about a brave pig")