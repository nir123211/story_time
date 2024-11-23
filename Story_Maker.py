import streamlit as st
from streamlit_utils import (create_first_story, show_story, show_characters, load_lines, show_lines, edit_line,
                             finish_video, show_video)


if st.session_state.setdefault('status', 'create_story') == 'create_story':
    create_first_story()
elif st.session_state['status'] == 'edit_story':
    show_story()
elif st.session_state['status'] == 'characters':
    show_characters()
elif st.session_state['status'] == 'generate_lines':
    load_lines()
elif st.session_state['status'] == 'lines':
    show_lines()
elif st.session_state['status'] == 'edit_line':
    edit_line()
elif st.session_state['status'] == 'finish_video':
    finish_video()
elif st.session_state['status'] == 'show_video':
    show_video()
else:
    st.header(st.session_state['status'])
