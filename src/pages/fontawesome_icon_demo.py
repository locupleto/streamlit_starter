# In src/pages/fontawesome_icon_demo.py
from pages.base_page import BasePage
import streamlit as st

class FontAwesomeIconDemoPage(BasePage):
    def show_page(self):
        st.title("FontAwesome Icons")
        st.write("This page demonstrates FontAwesome icons with the 'fa-' prefix.")
        st.markdown("""
        FontAwesome icons need the 'fa-' prefix in the `icon_type()` method.

        Example: `return "fa-"`
        """)

    def label(self):
        return "FontAwesome Icons"

    def icon(self):
        return "coffee"

    def order(self):
        return 103

    def parent(self):
        return "icon_types_group"

    def icon_type(self):
        return "fa-"  # Use FontAwesome icons