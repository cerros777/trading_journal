from streamlit_pills import pills
import streamlit as st
from filters import apply_date_filter

def render_filter_chips(df, session_key="filter_selection"):
    filter_options = ["Last Day", "Last week", "Last month", "All Time"]

    # Initialize
    if session_key not in st.session_state:
        st.session_state[session_key] = "Last Day"

    selected = pills(
        label="",  # Hide label
        options=filter_options,
        index=filter_options.index(st.session_state[session_key]),
        label_visibility="collapsed",
        backgroundColor="gray"
    )

    st.session_state[session_key] = selected
    return apply_date_filter(df, selected), selected

