# ============================================================================
# -*- coding: utf-8 -*-
#
# Module: Home Page
# Description: Implements the HomePage class that inherits from BasePage
#              and defines the content and properties for the home page.
#
# Useful Links:
#   https://icons.getbootstrap.com/
#
# History:
# 2024-05-18    urot  Created
# ============================================================================

import streamlit as st
from pages.base_page import BasePage

class HomePage(BasePage):

    def show_page(self):
        st.title("Home Page")
        st.write("Welcome to the Home Page. This is the main dashboard of the application.")

    def label(self):
        return "Home"

    def icon(self):
        return "house"

    def order(self):
        return 1

