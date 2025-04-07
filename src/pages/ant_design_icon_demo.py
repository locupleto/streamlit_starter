# In src/pages/ant_design_icon_demo.py
from pages.base_page import BasePage
import streamlit as st

class AntDesignIconDemoPage(BasePage):
    def show_page(self):
        st.title("Ant Design Icons")
        st.write("This page demonstrates Ant Design icons with the 'ad-' prefix.")
        st.markdown("""
        Ant Design icons need the 'ad-' prefix in the `icon_type()` method.

        Example: `return "ad-"`
        """)

    def label(self):
        return "Ant Design Icons"

    def icon(self):
        return "AppstoreOutlined"

    def order(self):
        return 102

    def parent(self):
        return "icon_types_group"

    def icon_type(self):
        return "ad-"  # Use Ant Design icons