from pages.base_page import BasePage
import streamlit as st

class MenuDemoChild1Page(BasePage):
    def show_page(self):
        st.title("Child Page 1")
        st.write("This is a child page in the hierarchical menu.")

    def label(self):
        return "Child Page 1"

    def icon(self):
        return "1-circle"

    def order(self):
        return 91

    def parent(self):
        # This must match the module name of the parent page
        return "menu_demo"