# ============================================================================
# -*- coding: utf-8 -*-
#
# Project:      Streamlit Application with Dynamic Page Loading
# Description:  This Streamlit application dynamically loads and displays
#               pages defined in the app_pages package. Each page must 
#               implement the BasePage abstract base class.
#
# Usage:        Run with 'streamlit run app.py' from the terminal.
#
# Virtual Environment Setup:
#   python3 -m venv venv
#   source venv/bin/activate
#   pip install --upgrade pip
#   pip install -r requirements.txt
#
# Required Packages:
#   altair==4.1.0
#   streamlit
#   watchdog
#   streamlit-js-eval
#   streamlit-option-menu
#
# VSCode Notes: Run with 'streamlit run app.py' from the terminal or press
#               Cmd+Shift+D to bring up the debugging interface.
#
# Important!!!
#   Make sure to have this setting in the .streamlit/config-toml to avoid 
#   seeing all modules in the sidebar.
#
#   [client]
#   showSidebarNavigation = false
#
# Useful Links:
#   https://icons.getbootstrap.com/
#
# History:
# 2024-05-18    urot  Created
# ============================================================================

import streamlit as st
import os
from utilities.application_utilities import validate_session_state, dynamic_streamlit_menu
from utilities.application_utilities import load_config, apply_config
from utilities.styling_utilities import *

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, 'images')

# Set the page configuration (default wide)
st.set_page_config(layout="wide" if st.session_state.get("wide_mode", True) else "centered")

# Load the configuration at the start
config_data = load_config()

# Now apply the loaded configuration
apply_config(config_data)

# Debug function to print all session state variables
def debug_session_state():
    st.sidebar.subheader("Debug Info")
    for key, value in st.session_state.items():
        st.sidebar.write(f"{key}: {value}")

# Main application logic
def event_handler():

    # Initialize necessary session state variables
    validate_session_state()

    # Style and slightly tweak the sidebar header
    st.logo(os.path.join(STATIC_DIR, 'logo_image.png'), 
            link="http://localhost:8501", 
            icon_image=os.path.join(STATIC_DIR, 'logo_icon.png'))
    tweak_logo_position_and_padding()

    # Always hide the sidebar header if in horizontal orientation
    if st.session_state.get("orientation", "vertical") == 'horizontal':
        hide_sidebar_header()

    # Hide the streamlit std burger menu, reduce the vertical padding accordingly
    hide_streamlit_header_menu_and_footer()
    reduce_vertical_main_padding()

    selected_page, page_dict = dynamic_streamlit_menu(
        st.session_state.get("orientation", "vertical")
    )

    page_dict[selected_page].show_page()

if __name__ == "__main__":
    event_handler()
