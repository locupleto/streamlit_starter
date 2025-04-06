# ============================================================================
# -*- coding: utf-8 -*-
#
# Module:       styling_utilities.py
# Description:  Contains utility functions for managing and tweaking the 
#               streamlit app by e.g. tweaking some CSS styles to fit my 
#               visual preferences.
# History:
# 2024-05-18    urot  Created
# ============================================================================

import streamlit as st
import base64

# Function to hide the sidebar header in horizontal mode
def hide_sidebar_header():
    hide_sidebar_header_style = """
                <style>
                [data-testid="stSidebarHeader"] {
                    display: none;
                }
                </style>
                """
    hide_logo_icon_style = """
                <style>
                [data-testid="collapsedControl"] {
                    display: none;
                }
                </style>              
                """
    st.html(hide_sidebar_header_style)
    st.html(hide_logo_icon_style)

# Function to show the sidebar header with an image
def hide_streamlit_header_menu_and_footer():
    # Hide made by streamlit
    hide_st_style = """
                <style>
                #MainMenu {visibility: hidden;}
                footer {visibility: hidden;}
                header {visibility: hidden;}
                </style>
                """
    st.html(hide_st_style)

def reduce_vertical_main_padding():
    # Custom CSS to reduce padding and margin above the headline
    adjust_padding_margin_style = """
                <style>
                [data-testid="stAppViewBlockContainer"]
                {
                    padding-top: 0px;     /* Reduce padding above the content */
                    padding-bottom: 0px;  /* Adjust padding below the content if needed */
                    margin-top: 0px;      /* Reduce margin above the content */
                }
                </style>
                """
    st.html(adjust_padding_margin_style)
    
def tweak_logo_position_and_padding():
    # Custom CSS to reduce padding and margin above the headline
    adjust_sidebar_bottom_padding_style = """
                <style>
                [data-testid="stLogo"] {
                    /* width: 550px;   Adjust the width as needed */
                    /* height: auto;  Maintain aspect ratio */
                }

                [data-testid="stSidebarHeader"]
                {
                    padding-left:   2.0rem;
                    padding-bottom: 10px;   /* Adjust padding below the content if needed */
                }
                </style>
                """
    st.html(adjust_sidebar_bottom_padding_style)

# Define a function to style the DataFrame
def style_dataframe(df):
    # Apply styles to the DataFrame
    styled_df = df.style.set_properties(**{
        'background-color': 'black',
        'color': 'lawngreen',
        'border': '1px solid lawngreen',
        'border-color': 'lawngreen'
    }).set_table_styles([
        {'selector': 'th', 'props': [('background-color', 'black'), ('color', 'lawngreen'), ('border', '2px solid lawngreen')]}
    ])
    return styled_df

def set_background_images(img_path_1: str, img_path_2: str) -> None:
    """
    Sets background images for the Streamlit app container and bottom block.
    This is useful as it gives us an option to use different backgrounds for 
    different pages in a multipage app.

    Args:
    img_path_1 (str): Path to the image for the main app container.
    img_path_2 (str): Path to the image for the bottom block container.

    Returns:
    None: This function applies the styling directly using st.markdown.
    """

    def get_base64_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()

    img_base64_1 = get_base64_image(img_path_1)
    img_base64_2 = get_base64_image(img_path_2)

    page_bg_img = f"""
    <style>
    [data-testid="stAppViewContainer"], [data-testid="stBottomBlockContainer"] {{
    background-image: url("data:image/png;base64,{img_base64_1}");
    background-size: cover;
    }}

    [data-testid="stBottomBlockContainer"] {{
    background-image: url("data:image/png;base64,{img_base64_2}");
    background-size: cover;
    }}
    </style>
    """
    st.html(page_bg_img)

def render_chat_message(message, user_avatar=None, assistant_avatar=None, custom_render_func=None):
    """
    Renders a chat message in a Streamlit app with appropriate styling and avatar.
    This function is designed to be flexible and usable across different types of assistants.

    Args:
    message (dict): A dictionary containing the chat message information.
                    Expected to have at least a 'role' key ('user' or 'assistant')
                    and a 'content' key with the message content.
    user_avatar (str, optional): HTML string for the user's avatar. Defaults to None.
    assistant_avatar (str, optional): HTML string for the assistant's avatar. Defaults to None.
    custom_render_func (callable, optional): A function that defines custom rendering logic
                                             for specific message types. This function should
                                             accept the message content as its argument.
                                             Defaults to None.

    Returns:
    None: This function renders the chat message directly in the Streamlit app.

    Note:
    If no custom_render_func is provided, the function defaults to rendering
    the message content as markdown. The custom_render_func allows for
    handling of complex message types (e.g., charts, tables) specific to
    different assistants.
    """
    avatar = None
    if message["role"] == "user" and user_avatar:
        avatar = user_avatar
    elif message["role"] == "assistant" and assistant_avatar:
        avatar = assistant_avatar

    with st.chat_message(message["role"], avatar=avatar):
        if custom_render_func and callable(custom_render_func):
            custom_render_func(message["content"])
        else:
            st.markdown(str(message["content"]))

def apply_custom_table_style():
    custom_table_style = """
    <style>
    .custom-table {
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 1rem;
    }
    .custom-table th, .custom-table td {
        border: 2px solid #4CAF50;
        padding: 8px;
        text-align: left;
    }
    .custom-table th {
        background-color: #4CAF50;
        color: white;
    }
    .custom-table tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    </style>
    """
    st.html(custom_table_style)