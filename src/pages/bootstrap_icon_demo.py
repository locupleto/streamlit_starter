# In src/pages/bootstrap_icon_demo.py
from pages.base_page import BasePage
import streamlit as st

class BootstrapIconDemoPage(BasePage):
    def show_page(self):
        st.title("Bootstrap Icons")
        st.write("This page demonstrates Bootstrap icons (default icon type).")
        st.markdown("""
        Bootstrap icons don't need a prefix in the `icon_type()` method.

        Example: `return "heart-fill"`
        """)
        st.markdown("See: [Bootstrap Icons](https://icons.getbootstrap.com/)")

    def label(self):
        return "Bootstrap Icons"

    def icon(self):
        return "heart-fill"

    def order(self):
        return 101

    def parent(self):
        return "icon_types_group"