# In src/pages/nested_level1.py
from pages.base_page import BasePage
import streamlit as st

class NestedLevel1Page(BasePage):
    def show_page(self):
        st.title("Nested Level 1")
        st.write("This is a nested submenu item at level 1.")

    def label(self):
        return "Nested Level 1"

    def icon(self):
        return "diagram-2"

    def order(self):
        return 111

    def parent(self):
        return "advanced_features"

    def children(self):
        return ["nested_level2"]