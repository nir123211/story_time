from pathlib import Path

import streamlit as st
from scripts.text_generation.create_story import create_story, change_story
from scripts.text_generation.create_all import create_characters, add_sounds, add_image_prompts
from scripts.sounds_and_music.sound_scraper import scrape_sounds
from scripts.text_to_speech.text_to_speech import create_recordings
from scripts.image_generation.generate_story_images import add_story_images
from scripts.video_editing.story_to_video import create_video


st.header('Movie Generator!')


def story_creation_area():
    prompt_area = st.empty()
    col1, col2 = prompt_area.columns([6, 2])
    with col1:
        story_prompt = st.text_area('what story do you want to create?', height=5)
    with col2:
        story_length = st.selectbox("Story length:", ['very short', 'short', 'normal', 'long'])
    if st.button('Create Story!'):
        if story_length != 'normal':
            story_prompt = f'A {story_length} story about: {story_prompt}'
        st.session_state['story_prompt'] = story_prompt
        with st.spinner('Generating Story...'):
            st.session_state['story_dir']: Path = create_story(story_prompt)
    story_dir = st.session_state.get('story_dir')
    if story_dir:
        story_text = (story_dir / "story_lines.txt").read_text()
        st.write(story_text)
        if st.session_state.get('edit_story'):
            new_story = st.text_area('Edit the story here', value=story_text, height=10)
            col1, col2, col3 = st.columns([1, 1, 1])
            with col1:
                if st.button('Save Edit'):
                    change_story(story_dir, new_story)
                    st.session_state.pop('edit_story')
                    st.rerun()
            with col2:
                if st.button('Cancel'):
                    st.session_state.pop('edit_story')
                    st.rerun()
        else:
            col1, col2, col3 = st.columns([1, 1, 1])
            if col1.button('Turn It To A Movie!'):
                col1.subheader("please wait...")
                # with col1.status('casting characters', expanded=True):
                #     create_characters(story_dir)
                # with col1.status('thinking about the right sounds...', expanded=True):
                #     add_sounds(story_dir)
                # with col1.status('thinking about the right images...'):
                #     add_image_prompts(story_dir)
                # with col1.status('getting sounds...'):
                #     scrape_sounds(story_dir)
                # with col1.status('creating images...'):
                #     add_story_images(story_dir, "open_dall_e")
                with col1.status('narrating...'):
                    create_recordings(story_dir)
                with col1.status('finishing up...'):
                    create_video(story_dir)
            st.video(str(story_dir / f'{story_dir.stem}.mp4'))

            with col2:
                if st.button('edit_story'):
                    st.session_state['edit_story'] = True
                    st.rerun()
            with col3:
                if st.button('Retry'):
                    st.session_state.pop('story')
                    st.rerun()


if st.session_state.setdefault('story_creation', True):
    story_creation_area()
else:
    st.subheader("please wait...")
    with st.status('thinking about the right sounds...', expanded=True):
        st.session_state['story'].add_sound_prompts()
    with st.status('thinking about the right images...'):
        st.session_state['story'].add_images_prompts()
    st.session_state['story'].parse_story_lines()
    with st.status('getting sounds...'):
        st.session_state['story'].add_sounds()
    with st.status('creating images...'):
        st.session_state['story'].generate_images()

st.header("hello!")