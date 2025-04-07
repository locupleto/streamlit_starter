from pages.base_page import BasePage
import streamlit as st

class MenuDemoParentPage(BasePage):
    def show_page(self):
        st.title("Menu Demo Parent")
        st.write("This is a parent page that demonstrates the hierarchical menu structure.")

    def label(self):
        return "Menu Demo"

    def icon(self):
        return "list-nested"

    def order(self):
        return 90

    def children(self):
        # Use the actual module names of the child pages
        return ["menu_demo_child1", "menu_demo_child2"]