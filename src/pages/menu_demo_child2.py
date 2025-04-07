# In src/pages/menu_demo_child2.py
from pages.base_page import BasePage
import streamlit as st

class MenuDemoChild2Page(BasePage):
    def show_page(self):
        st.title("Child Page 2")
        st.write("This is another child page in the hierarchical menu.")

    def label(self):
        return "Child Page 2"

    def icon(self):
        return "2-circle"

    def order(self):
        return 92

    def parent(self):
        # This must match the module name of the parent page
        return "menu_demo"