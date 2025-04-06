# ============================================================================
# -*- coding: utf-8 -*-
#
# Module:       application_utilities.py
# Description:  Contains utility functions for loading modules dynamically,
#               managing configurations, and applying theme settings.
#               Custom configuration settings are stored in a separate
#               app_config.toml file to avoid conflicts with Streamlit's
#               internal configuration handling.
# History:
# 2024-05-18    urot Created
# 2024-07-29    urot Moved app_config.toml into the .config/ directory
# 2025-01-11    urot Allow macOS style path with spaces as db path
# ============================================================================

import os
from time import sleep
import streamlit as st
from streamlit_option_menu import option_menu
import toml
import importlib
from pages.base_page import BasePage

# File paths for the configurations
STREAMLIT_CONFIG_PATH = ".streamlit/config.toml"
APP_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                               '.config', 'app_config.toml')
#@st.cache_resource
# In application_utilities.py, modify the load_modules() function:

def load_modules():
    with st.spinner('Loading modules...'):
        pages_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "pages")
        modules = []
        failed_modules = []

        for filename in os.listdir(pages_path):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module_path = f"pages.{module_name}"

                try:
                    module = importlib.import_module(module_path)

                    # Find all classes that inherit from BasePage
                    page_classes = []
                    for name, obj in module.__dict__.items():
                        if isinstance(obj, type) and issubclass(obj, BasePage) and obj is not BasePage:
                            page_classes.append(obj)

                    # Sort by inheritance depth (most derived classes first)
                    page_classes.sort(key=lambda cls: len(cls.__mro__), reverse=True)

                    # Use the most derived class (the one with the longest inheritance chain)
                    if page_classes:
                        modules.append((module_name, page_classes[0]()))

                except Exception as e:
                    failed_modules.append((module_name, str(e)))

        # Sort modules by their order
        modules.sort(key=lambda x: x[1].order())

        # Set default page
        if modules:
            st.session_state.default_page = modules[0][1].label()
        else:
            st.session_state.default_page = "Error"  # If no modules exist, set a default error page

        # Report failed modules
        if failed_modules:
            st.warning("Some modules failed to load:")
            for module, error in failed_modules:
                st.error(f"Failed to load {module}: {error}")

    return modules

# Default themes
default_light_theme = {
    "theme": {
        "base": "light",
        "primaryColor": "#F63366",
        "backgroundColor": "#FFFFFF",
        "secondaryBackgroundColor": "#F0F2F6",
        "textColor": "#262730",
        "font": "sans serif"
    }
}

default_dark_theme = {
    "theme": {
        "base": "dark",
        "primaryColor": "#F63366",
        "backgroundColor": "#262730",
        "secondaryBackgroundColor": "#1A1A1A",
        "textColor": "#FFFFFF",
        "font": "sans serif"
    }
}

# Determine theme status
def determine_theme_status(theme):
    if theme == default_dark_theme["theme"]:
        return "dark"
    elif theme == default_light_theme["theme"]:
        return "light"
    else:
        return "custom"

# Create default config files if they don't exist
def create_default_configs():
    default_streamlit_config = {
        "theme": default_dark_theme["theme"],  # Default to dark theme
    }
    os.makedirs(os.path.dirname(STREAMLIT_CONFIG_PATH), exist_ok=True)
    with open(STREAMLIT_CONFIG_PATH, "w") as f:
        toml.dump(default_streamlit_config, f)

    default_app_config = {
        "streamlit-option-menu": {
            "orientation": "vertical",  # Default orientation
            "wide_mode": False  # Default to not wide mode
        },
        "database": {
            "db_file_path": "",
            "eod_api_key": ""
        },
        "LLM": {
            "openai_api_key": ""
        }
    }
    # Create .config directory if it doesn't exist
    os.makedirs(os.path.dirname(APP_CONFIG_PATH), exist_ok=True)
    with open(APP_CONFIG_PATH, "w") as f:
        toml.dump(default_app_config, f)

# Apply theme settings immediately
def apply_theme_settings(theme):
    st.config.set_option('theme.base', theme.get('base', 'light'))
    st.config.set_option('theme.primaryColor', theme.get('primaryColor', '#F63366'))
    st.config.set_option('theme.backgroundColor', theme.get('backgroundColor', '#FFFFFF'))
    st.config.set_option('theme.secondaryBackgroundColor', theme.get('secondaryBackgroundColor', '#F0F2F6'))
    st.config.set_option('theme.textColor', theme.get('textColor', '#262730'))
    # Apply custom font via CSS
    font_css = f"""
    <style>
    body {{
        font-family: {theme.get('font', 'sans serif')}, sans-serif;
    }}
    </style>
    """
    st.markdown(font_css, unsafe_allow_html=True)

# Load current config values from configuration files if they exist
def load_config():
    if not os.path.exists(STREAMLIT_CONFIG_PATH) or not os.path.exists(APP_CONFIG_PATH):
        create_default_configs()

    config = toml.load(STREAMLIT_CONFIG_PATH)
    theme = config.get("theme", {})
    base = theme.get("base", "light")
    defaults = default_dark_theme if base == "dark" else default_light_theme
    for key, value in defaults["theme"].items():
        theme.setdefault(key, value)

    app_config = toml.load(APP_CONFIG_PATH)
    extras = app_config.get("streamlit-option-menu", {})
    orientation = extras.get("orientation", "vertical")
    wide_mode = extras.get("wide_mode", False)

    # Store everything in a dictionary instead of directly in session state
    config_data = {
        "theme": theme,
        "theme_status": determine_theme_status(theme),
        "orientation": orientation,
        "wide_mode": wide_mode
    }

    # Add app settings to the config_data
    app_settings = read_api_settings()
    config_data.update(app_settings)

    # Add research_assistant configuration
    research_assistant_config = app_config.get("research_assistant", {})
    config_data["research_assistant"] = research_assistant_config

    return config_data

# New function to apply the loaded config
def apply_config(config_data):
    for key, value in config_data.items():
        st.session_state[key] = value
    
    apply_theme_settings(config_data["theme"])

# Helper function for read_app_settings() below
def get_ai_client_and_model(model_name):
    if model_name.startswith("gpt") or model_name.startswith("o1") or model_name.startswith("o3"):
        return "openai", model_name
    elif model_name.startswith("claude"):
        return "anthropic", model_name
    elif model_name.startswith("gemini"):
        return "google", model_name
    else:
        raise ValueError(f"Unknown model type: {model_name}")

def read_api_settings():
    settings = {}
    if os.path.exists(APP_CONFIG_PATH):
        app_config = toml.load(APP_CONFIG_PATH)

        # Get the path and clean it
        raw_path = app_config.get('database', {}).get('db_file_path', '')
        clean_path = clean_path_string(raw_path) if raw_path else ''

        settings = {
            "db_file_path": clean_path,
            "eod_api_key": app_config.get('database', {}).get('eod_api_key', ''),
            "openai_api_key": app_config.get('LLM', {}).get('openai_api_key', ''),
            "langchain_api_key": app_config.get('LLM', {}).get('langchain_api_key', ''),
            "anthropic_api_key": app_config.get('LLM', {}).get('anthropic_api_key', ''),
            "google_api_key": app_config.get('LLM', {}).get('google_api_key', ''),
            "perplexity_api_key": app_config.get('search', {}).get('perplexity_api_key', ''),
            "brave_api_key": app_config.get('search', {}).get('brave_api_key', ''),
            "large_model": app_config.get('LLM', {}).get('large_model', 'gpt-4o'),
            "small_model": app_config.get('LLM', {}).get('small_model', 'gpt-4o-mini'),
            "exa_ai_api_key": app_config.get('RAG', {}).get('exa_ai_api_key', '')
        }

        # Add AI client and model information for both large and small models
        large_model = settings["large_model"]
        settings["ai_client"], settings["ai_model"] = get_ai_client_and_model(large_model)

        small_model = settings["small_model"]
        settings["small_ai_client"], settings["small_ai_model"] = get_ai_client_and_model(small_model)

    return settings

# Ensure necessary session state variables are initialized
def validate_session_state():
    # ensure valid state and settings files
    if ('default_page' not in st.session_state or
        'previous_page' not in st.session_state or
        'orientation' not in st.session_state or
        'wide_mode' not in st.session_state):
            # figure out the page with the lowest order() = default_page
            modules = load_modules()
            st.session_state.previous_page = st.session_state.default_page

            # read all settings from the config files (or create & use defaults)
            load_config()

# Save configuration to files and update session state
def clean_path_string(path):
    """Remove excessive escaping from path string."""
    # Remove double escapes and convert escaped spaces to regular spaces
    return path.replace('\\\\', '').replace('\\ ', ' ')

def save_config(theme=None, orientation=None, wide_mode=True):
    st.session_state.theme = theme
    st.session_state.orientation = orientation
    st.session_state.wide_mode = wide_mode
    st.session_state.theme_status = determine_theme_status(theme)

    streamlit_config = {
        "theme": theme
    }

    # Always hide the auto-built sidebar navigation (until ported to 1.36)
    streamlit_config["client"] = {
        "showSidebarNavigation": False
    }

    # Load existing app config
    app_config = toml.load(APP_CONFIG_PATH)

    # Update menu settings
    app_config["streamlit-option-menu"] = {
        "orientation": orientation,
        "wide_mode": wide_mode
    }

    # Clean any path strings in the database section if they exist
    if 'database' in app_config and 'db_file_path' in app_config['database']:
        app_config['database']['db_file_path'] = clean_path_string(app_config['database']['db_file_path'])

    with open(STREAMLIT_CONFIG_PATH, "w") as f:
        toml.dump(streamlit_config, f)

    with open(APP_CONFIG_PATH, "w") as f:
        toml.dump(app_config, f)
    sleep(0.5)
    st.rerun()  # Re-run the app to apply the new config files

# Function to dynamically create menu options from loaded modules
def dynamic_streamlit_menu(orientation="vertical"):
    if 'loaded_modules' not in st.session_state:
        modules = load_modules()
        st.session_state['loaded_modules'] = modules
    else:
        modules = st.session_state['loaded_modules']
    modules.sort(key=lambda x: x[1].order())

    options = [mod[1].label() for mod in modules]
    icons = [mod[1].icon() for mod in modules]

    # Handle empty options list
    if not options:
        st.error("No modules were loaded. Please check your pages directory.")
        return None, {}

    # Ensure default_index is valid
    default_index = 0  # Always use 0 as the safe default

    if orientation == "vertical":
        with st.sidebar:
            selected = option_menu(
                menu_title=None,
                options=options,
                icons=icons,
                menu_icon="cast",
                default_index=default_index
            )
    else:
        selected = option_menu(
            menu_title=None,
            options=options,
            icons=icons,
            menu_icon="cast",
            default_index=default_index,
            orientation="horizontal"
        )

    return selected, {mod[1].label(): mod[1] for mod in modules}