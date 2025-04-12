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