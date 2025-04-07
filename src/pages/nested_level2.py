# In src/pages/nested_level2.py
from pages.base_page import BasePage
import streamlit as st

class NestedLevel2Page(BasePage):
    def show_page(self):
        st.title("Nested Level 2")
        st.write("This is a deeply nested submenu item at level 2.")

    def label(self):
        return "Nested Level 2"

    def icon(self):
        return "diagram-3"

    def order(self):
        return 112

    def parent(self):
        return "nested_level1"