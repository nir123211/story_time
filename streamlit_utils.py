from pathlib import Path

import streamlit as st
from scripts.text_generation.create_story import create_story, change_story
from scripts.text_generation.create_all import create_characters, add_sounds, add_image_prompts
from scripts.sounds_and_music.sound_scraper import scrape_sounds
from scripts.text_to_speech.text_to_speech import create_recordings
from scripts.image_generation.generate_story_images import add_story_images
from scripts.video_editing.story_to_video import create_video



def show_sidebar_section():
    st.sidebar.title("Select story component")
    story_button = st.button("story")