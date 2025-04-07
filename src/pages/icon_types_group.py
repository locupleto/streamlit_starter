# In src/pages/icon_types_group.py
from pages.base_page import BasePage
import streamlit as st

class IconTypesGroupPage(BasePage):
    def show_page(self):
        st.title("Icon Types Group")
        st.write("This is a group header that contains different icon type examples.")

    def label(self):
        return "Icon Types"

    def icon(self):
        return "palette2"

    def order(self):
        return 100

    def group_type(self):
        return "group"  # Make this a group header