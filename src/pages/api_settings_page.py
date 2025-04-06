# ============================================================================
# -*- coding: utf-8 -*-
#
# Module:       api_settings_page.py
# Description:  Implements the ApiSettingsPage class that inherits from 
#               BasePage and defines the content and properties for the 
#               application settings page. This page allows users to configure 
#               settings such as the database file path, EOD API key, and 
#               OpenAI API key as well as preferred small and large language 
#               models. The settings are stored in a configuration file and 
#               synchronized with the Streamlit session state.
# Useful Links:
#   https://icons.getbootstrap.com/
#
# History:
# 2024-05-24    urot Created
# 2024-07-29    urot Moved app_config.toml into the .config/ directory
# 2024-10-25    urot Updated Claude 3.5 Sonet model version
# ============================================================================

import os
import streamlit as st
from pages.base_page import BasePage
from utilities.application_utilities import validate_session_state
import toml

# Get the absolute path to the project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
APP_CONFIG_PATH = os.path.join(BASE_DIR, '.config', 'app_config.toml')

class ApiSettingsPage(BasePage):

    def responsive_padding(self):
        padding_css = """
        <style>
        .responsive-padding {
            padding: 1vh 1vw;
        }
        </style>
        """
        st.html(padding_css)

    def show_page(self):
        validate_session_state()
        st.title("API Keys")

        # Add responsive padding
        self.responsive_padding()

        # Load current app configuration
        if not os.path.exists(APP_CONFIG_PATH):
            self.create_default_app_config()

        app_config = toml.load(APP_CONFIG_PATH)

        # Load the settings from session state or default to values in the config file
        if "db_file_path" not in st.session_state:
            st.session_state["db_file_path"] = app_config.get('database', {}).get('db_file_path', '')
        if "eod_api_key" not in st.session_state:
            st.session_state["eod_api_key"] = app_config.get('database', {}).get('eod_api_key', '')
        if "openai_api_key" not in st.session_state:
            st.session_state["openai_api_key"] = app_config.get('LLM', {}).get('openai_api_key', '')
        if "langchain_api_key" not in st.session_state:
            st.session_state["langchain_api_key"] = app_config.get('LLM', {}).get('langchain_api_key', '')
        if "anthropic_api_key" not in st.session_state:
            st.session_state["anthropic_api_key"] = app_config.get('LLM', {}).get('anthropic_api_key', '')
        if "google_api_key" not in st.session_state:
            st.session_state["google_api_key"] = app_config.get('LLM', {}).get('google_api_key', '')
        if "perplexity_api_key" not in st.session_state:
            st.session_state["perplexity_api_key"] = app_config.get('search', {}).get('perplexity_api_key', '')
        if "brave_api_key" not in st.session_state:
            st.session_state["brave_api_key"] = app_config.get('search', {}).get('brave_api_key', '')
        if "large_model" not in st.session_state:
            st.session_state["large_model"] = app_config.get('LLM', {}).get('large_model', 'gpt-4o')
        if "small_model" not in st.session_state:
            st.session_state["small_model"] = app_config.get('LLM', {}).get('small_model', 'gpt-4o-mini')
        if "exa_ai_api_key" not in st.session_state:
            st.session_state["exa_ai_api_key"] = app_config.get('RAG', {}).get('exa_ai_api_key', '')

        # Use st.form to group input elements
        with st.form(key="settings_form"):
            st.html('<div class="responsive-padding">')  # Start of padded div
            # Create three columns
            col1, col2, col3 = st.columns(3)

            with col1:
                st.subheader("AI providers")
                openai_api_key = st.text_input('OpenAI API Key', value=st.session_state["openai_api_key"])
                anthropic_api_key = st.text_input('Anthropic API Key', value=st.session_state["anthropic_api_key"])     
                google_api_key = st.text_input('Google API Key', value=st.session_state["google_api_key"])
                langchain_api_key = st.text_input('Langchain API Key', value=st.session_state["langchain_api_key"])

                st.subheader("LLM Preferences")
                large_model = st.selectbox(
                    'Large Model',
                    options=["o3-mini", "o1-mini", "gpt-4o", "gpt-4o-mini-2024-07-18", "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307", "gemini-1.5-pro-latest"],
                    index=["o3-mini", "o1-mini", "gpt-4o", "gpt-4o-mini-2024-07-18", "claude-3-7-sonnet-20250219", "claude-3-5-sonnet-20241022", "claude-3-haiku-20240307", "gemini-1.5-pro-latest"].index(st.session_state["large_model"])
                )
                small_model = st.selectbox(
                    'Small Model',
                    options=["o3-mini", "gpt-4o-mini-2024-07-18", "claude-3-haiku-20240620", "gemini-1.5-flash-latest"],
                    index=["o3-mini", "gpt-4o-mini-2024-07-18", "claude-3-haiku-20240620", "gemini-1.5-flash-latest"].index(st.session_state["small_model"])
                )

            with col2:                
                st.subheader("RAG Settings")
                exa_ai_api_key = st.text_input('Exa API Key', value=st.session_state["exa_ai_api_key"])

                st.html('<div style="padding: 4px 0;"></div>')
                st.subheader("Search providers")
                perplexity_api_key = st.text_input('Perplexity API Key', value=st.session_state["perplexity_api_key"])
                brave_api_key = st.text_input('Brave API Key', value=st.session_state["brave_api_key"])

            with col3:
                st.subheader("EOD Database")
                db_file_path = st.text_input('SQLite Marketdata Db Path', value=st.session_state["db_file_path"])
                eod_api_key = st.text_input('EOD API Key', value=st.session_state["eod_api_key"])

            st.html('</div>')  # End of padded div

            # Submit button for the form
            submit_button = st.form_submit_button(label="Save Settings")

        # Save the updated configuration when the form is submitted
        if submit_button:
            trimmed_db_file_path = db_file_path.strip()
            trimmed_eod_api_key = eod_api_key.strip()
            trimmed_open_ai_key = openai_api_key.strip()
            trimmed_langchain_api_key = langchain_api_key.strip()
            trimmed_anthropic_api_key = anthropic_api_key.strip()
            trimmed_google_api_key = google_api_key.strip()
            trimmed_perplexity_api_key = perplexity_api_key.strip()
            trimmed_brave_api_key = brave_api_key.strip()
            trimmed_llamacloud_api_key = exa_ai_api_key.strip()

            # Store the trimmed values in session state
            st.session_state["db_file_path"] = trimmed_db_file_path
            st.session_state["eod_api_key"] = trimmed_eod_api_key
            st.session_state["openai_api_key"] = trimmed_open_ai_key
            st.session_state["langchain_api_key"] = trimmed_langchain_api_key
            st.session_state["anthropic_api_key"] = trimmed_anthropic_api_key
            st.session_state["google_api_key"] = trimmed_google_api_key
            st.session_state["perplexity_api_key"] = trimmed_perplexity_api_key
            st.session_state["brave_api_key"] = trimmed_brave_api_key
            st.session_state["large_model"] = large_model
            st.session_state["small_model"] = small_model
            st.session_state["exa_ai_api_key"] = trimmed_llamacloud_api_key

            # Save to app_config
            app_config['database'] = {
                'db_file_path': trimmed_db_file_path,
                'eod_api_key': trimmed_eod_api_key
            }
            app_config['LLM'] = {
                'openai_api_key': trimmed_open_ai_key,
                'langchain_api_key': trimmed_langchain_api_key,
                'anthropic_api_key': trimmed_anthropic_api_key,
                'google_api_key': trimmed_google_api_key,
                'large_model': large_model,
                'small_model': small_model
            }
            app_config['search'] = {
                'perplexity_api_key': trimmed_perplexity_api_key,
                'brave_api_key': trimmed_brave_api_key
            }
            app_config['RAG'] = {
                'exa_ai_api_key': trimmed_llamacloud_api_key
            }
            with open(APP_CONFIG_PATH, "w") as f:
                toml.dump(app_config, f)
            st.rerun()

    def create_default_app_config(self):
        default_app_config = {
            "database": {
                "db_file_path": "",
                "eod_api_key": ""
            },
            "LLM": {
                "openai_api_key": "",
                "langchain_api_key": "",
                "anthropic_api_key": "",
                "google_api_key": "",
                "large_model": "gpt-4o",
                "small_model": "gpt-4o-mini"
            },
            "search": {
                "perplexity_api_key": "",
                "brave_api_key": ""
            },
            "RAG": {
                "exa_ai_api_key": ""
            }
        }
        with open(APP_CONFIG_PATH, "w") as f:
            toml.dump(default_app_config, f)

    def label(self):
        return "API Settings"

    def icon(self):
        return "gear"

    def order(self):
        return 95