import json
import os
from pathlib import Path

import streamlit as st

from scripts.text_generation.create_story import create_story, change_story
from scripts.text_generation.create_all import create_characters, add_sounds, add_image_prompts
from scripts.sounds_and_music.sounds_adder import add_music, add_sounds_mp3
from scripts.text_to_speech.elevenlabs import create_recordings
from scripts.image_generation.stable_diffusion_3 import generate_story_images, generate_image
from scripts.video_editing.story_to_video import (create_video_lines, create_line_video, merge_video_chunks,
                                                  finalize_video)


def create_first_story():
    st.header('Welcome To The Movie Generator! \n')
    prompt_area = st.empty()
    col1, col2 = prompt_area.columns([6, 2])
    story_prompt = col1.text_area('what story do you want to create?', height=5)
    if st.button('Create Story!'):
        story_prompt = f'A short story about: {story_prompt}'
        st.session_state['status'] = 'edit_story'
        with st.spinner('Generating Story...'):
            st.session_state['story_dir']: Path = create_story(story_prompt)
            st.rerun()


def show_story():
    st.header('Story Result: \n')
    story_dir = st.session_state['story_dir']
    story_text = (story_dir / "story_lines.txt").read_text()
    story = st.text_area('Edit the story here', value=story_text, height=500)
    col1, col2, col3 = st.columns([1, 1, 1])
    if col1.button('Bact to Story Creation'):
        st.session_state['status'] = 'create_story'
        st.rerun()
    if col3.button('Continue'):
        st.session_state['story_dir']: Path = change_story(story_dir, story)
        with col1.status('casting characters', expanded=True):
            create_characters(story_dir)
            st.session_state['status'] = 'characters'
            st.rerun()


def show_characters():
    st.header('Story Characters: \n')
    story_dir = st.session_state['story_dir']
    characters_file = story_dir / "characters.json"
    characters = json.loads(characters_file.read_text())
    index = st.session_state.setdefault('index', 0)
    character = [*characters.keys()][index]
    description = characters[character]['description']
    st.subheader(f"{character}:")
    characters[character]['description'] = st.text_area('Edit the Character here', value=description, height=500)
    col1, col2, col3 = st.columns([1, 1, 1])
    if col1.button('Previous Character'):
        if st.session_state['index'] > 0:
            st.session_state['index'] -= 1
            st.rerun()
        else:
            col1.warning('First Character Reached')
    if col2.button('Save Changes'):
        characters_file.write_text(json.dumps(characters, indent=2))
    if col3.button('Next Character'):
        if len(characters) > st.session_state['index']+1:
            st.session_state['index'] += 1
            st.rerun()
        else:
            col3.warning('Last Character Reached')
    if col1.button('Back to story'):
        st.session_state['status'] = 'edit_story'
        st.rerun()
    if col3.button('Continue'):
        st.session_state['status'] = 'generate_lines'
        st.rerun()


def load_lines():
    story_dir = st.session_state['story_dir']
    with st.status('Thinking about the right images...', expanded=True):
        add_image_prompts(story_dir)
    with st.status('Generating images...', expanded=True):
        generate_story_images(story_dir)
    with st.status('Thinking about the right sounds...', expanded=True):
        add_sounds(story_dir)
        add_music(story_dir)
        add_sounds_mp3(story_dir)
    with st.status('Narrating...', expanded=True):
        create_recordings(story_dir)
    with st.status('creating scenes...', expanded=True):
        create_video_lines(story_dir)
    st.session_state['status'] = 'lines'
    st.session_state['index'] = 1
    st.rerun()


def show_lines():
    story_dir = st.session_state['story_dir']
    index = st.session_state.setdefault('index', 0)
    line_dir = story_dir / f'line{index}'
    st.header('Story Scenes:')
    st.subheader(f"line{index}")
    st.video(str(line_dir / 'line.mp4'))
    col1, col2, col3 = st.columns([1, 1, 1])
    if col1.button('Previous Line'):
        if st.session_state['index'] > 0:
            st.session_state['index'] -= 1
            st.rerun()
        else:
            col1.warning('First Line Reached')
    if col2.button('Edit line'):
        st.session_state['status'] = 'edit_line'
        st.rerun()
    if col3.button('Next Line'):
        if f"line{st.session_state['index']+1}" in os.listdir(story_dir):
            st.session_state['index'] += 1
            st.rerun()
        else:
            col3.warning('Last Line Reached')
    if col3.button('Continue'):
        st.session_state['status'] = 'finish_video'
        st.rerun()


def edit_line():
    story_dir = st.session_state['story_dir']
    index = st.session_state.setdefault('index', 0)
    line_dir: Path = story_dir / f'line{index}'
    st.header('Story Scenes:')
    st.subheader(f"line{index}")
    st.video(str(line_dir / 'line.mp4'))
    col1, col2, col3 = st.columns([2, 2, 1])
    image_prompt = (line_dir / 'image.txt').read_text()
    image_prompt = col1.text_area('Edit the image prompt here', value=image_prompt, height=300)
    if col1.button('Change image'):
        (line_dir / 'image.txt').write_text(image_prompt)
        generate_image(image_prompt, (line_dir / 'image.png'))
        create_line_video(line_dir, force=True)
        st.rerun()
    sound_prompt = (line_dir / 'sound.txt').read_text()
    sound_prompt = col2.text_area('Edit the sound prompt here', value=sound_prompt, height=300)
    if col2.button('Change sound prompt'):
        (line_dir / 'sound.txt').write_text(sound_prompt)
        create_line_video(line_dir, force=True)
        st.rerun()
    if col3.button('Continue'):
        st.session_state['status'] = 'lines'
        st.rerun()


def finish_video():
    story_dir = st.session_state['story_dir']
    with st.status('adding_music', expanded=True):
        merge_video_chunks(story_dir)
    with st.status('Finalizing video', expanded=True):
        finalize_video(story_dir)
    st.session_state['status'] = 'show_video'
    st.rerun()


def show_video():
    st.title('Get Some Popcorn!')
    story_dir = st.session_state['story_dir']
    st.video(f"{story_dir / story_dir.stem}.mp4")

