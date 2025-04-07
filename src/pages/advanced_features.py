# In src/pages/advanced_features.py
from pages.base_page import BasePage
import streamlit as st

class AdvancedFeaturesPage(BasePage):
    def show_page(self):
        st.title("Advanced Features")
        st.write("This demonstrates a deeper menu hierarchy with multiple levels.")

    def label(self):
        return "Advanced Features"

    def icon(self):
        return "gear-wide-connected"

    def order(self):
        return 110

    def divider_before(self):
        return True  # Add a divider before this item

    def children(self):
        return ["nested_level1"]