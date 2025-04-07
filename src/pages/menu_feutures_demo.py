# In src/pages/menu_features_demo.py
from pages.base_page import BasePage
import streamlit as st

class MenuFeaturesDemoPage(BasePage):
    def show_page(self):
        st.title("Menu Features Demo")
        st.write("This page demonstrates various features of the Ant Design Menu component.")

        st.markdown("""
        ## Features Demonstrated in the Menu

        - **Group Headers**: The "Icon Types" section is a group header
        - **Dividers**: Notice the divider before the "Advanced Features" section
        - **Icon Types**: 
          - Bootstrap icons (default)
          - Ant Design icons (prefixed with "ad-")
          - FontAwesome icons (prefixed with "fa-")
        - **Nested Submenus**: The "Advanced Features" section has multiple levels
        """)

    def label(self):
        return "Menu Features"

    def icon(self):
        return "palette"

    def order(self):
        return 95

    def divider_before(self):
        return True  # Add a divider before this item