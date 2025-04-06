# ============================================================================
# -*- coding: utf-8 -*-
#
# Module:       Theme Settings Page
# Description:  Implements the ThemeSettingsPage class that inherits from 
#               BasePage and defines the content and properties for the theme 
#               settings page. This page allows users to customize the 
#               application theme, including primary color, background color, 
#               secondary background color, text color, font, menu orientation 
#               and display mode (wide or not).
# Useful Links:
#   https://icons.getbootstrap.com/
#
# History:
# 2024-05-18    urot  Created
# ============================================================================

import streamlit as st
from pages.base_page import BasePage
from utilities.application_utilities import save_config, default_light_theme, default_dark_theme

class ThemeSettingsPage(BasePage):

    def show_page(self):
        st.title("Theme Settings")

        # Ensure theme status is correctly determined
        if "theme_status" not in st.session_state:
            st.session_state.theme_status = "light" if st.session_state.theme == default_light_theme["theme"] else "dark"

        # Use st.form to group input elements
        with st.form(key="theme_settings_form"):
            # Theme selection
            theme_status = st.selectbox(
                "Select Theme",
                options=["light", "dark", "custom"],
                index=["light", "dark", "custom"].index(st.session_state.get("theme_status", "light"))
            )

            # Menu orientation selection
            orientation = st.selectbox(
                "Select Menu Orientation",
                options=["vertical", "horizontal"],
                index=0 if st.session_state.get("orientation", "vertical") == "vertical" else 1
            )

            # Display mode selection
            display_mode = st.checkbox("Wide Mode", value=st.session_state.get("wide_mode", False))

            # Disable color and font pickers if the theme is not custom
            is_custom_theme = theme_status == "custom"

            primaryColor = st.color_picker("Primary Color", st.session_state.theme["primaryColor"], disabled=not is_custom_theme)
            backgroundColor = st.color_picker("Background Color", st.session_state.theme["backgroundColor"], disabled=not is_custom_theme)
            secondaryBackgroundColor = st.color_picker("Secondary Background Color", st.session_state.theme["secondaryBackgroundColor"], disabled=not is_custom_theme)
            textColor = st.color_picker("Text Color", st.session_state.theme["textColor"], disabled=not is_custom_theme)
            font = st.selectbox(
                "Select Font",
                options=["sans serif", "serif", "monospace"],
                index=["sans serif", "serif", "monospace"].index(st.session_state.theme["font"]),
                disabled=not is_custom_theme
            )

            # Submit button for the form
            submit_button = st.form_submit_button(label="Apply Settings")

        if submit_button:
            if theme_status == "dark":
                theme = default_dark_theme["theme"]
            elif theme_status == "light":
                theme = default_light_theme["theme"]
            else:
                theme = {
                    "base": st.session_state.theme["base"],
                    "primaryColor": primaryColor,
                    "backgroundColor": backgroundColor,
                    "secondaryBackgroundColor": secondaryBackgroundColor,
                    "textColor": textColor,
                    "font": font
                }

            st.session_state.wide_mode = display_mode
            st.session_state.orientation = orientation
            st.session_state.theme_status = theme_status
            save_config(theme, orientation, display_mode)
            st.experimental_rerun()

    def label(self):
        return "Theme Settings"

    def icon(self):
        return "palette"

    def order(self):
        return 3
