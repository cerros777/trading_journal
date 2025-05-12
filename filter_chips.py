from streamlit_pills import pills
import streamlit as st
from filters import apply_date_filter

def render_filter_chips(session_key, default="Last Day"):
    filter_options = ["Last Day", "Last week", "Last month", "All Time"]

    # Default
    if session_key not in st.session_state:
        st.session_state[session_key] = default

    unique_key = f"pills_{session_key}"

    selected_value = pills(
        label="",  # Hide label
        options=filter_options,
        index=filter_options.index(st.session_state[session_key]),
        label_visibility="collapsed",
        backgroundColor="#262730",
        key=unique_key
    )

    if st.session_state[session_key] != selected_value:
        st.session_state[session_key] = selected_value
        st.rerun()

    return selected_value

