# Streamlit Starter Project

**A robust foundation for building LLM-powered multi-page Streamlit applications with a clean, modular architecture.**

## Overview

This project provides a structured framework for rapidly developing Streamlit applications that leverage Large Language Models (LLMs). It features a modular page system, theme customization, chat interfaces with history management, and support for multiple LLM providers.

![Screenshot](https://github.com/locupleto/streamlit_starter/raw/main/Screenshot.png)

## Key Features

- **Modular Page Architecture:** Easily add new pages by extending the `BasePage` class
- **Dynamic Navigation:** Automatic sidebar menu generation from page modules
- **Theme Customization:** Light/dark mode and custom theme support
- **LLM Integration:** Support for OpenAI, Anthropic Claude, and Google Gemini models
- **Chat Interface:** Ready-to-use chat assistant with persistent history
- **Diagram Support:** Built-in visualization for Mermaid and D2 diagrams in chat

## Project Structure

```
streamlit_starter/
├── src/
│   ├── pages/
│   │   ├── base_page.py              # Abstract base class for all pages
│   │   ├── app_settings.py           # API key management
│   │   ├── chat_assistant_page.py    # Chat interface implementation
│   │   └── theme_settings.py         # Theme customization
│   ├── models/
│   │   └── llms.py                   # LLM provider wrappers
│   ├── utilities/
│   │   ├── application_utilities.py  # Core app functions
│   │   └── chat_utilities.py         # Chat history management
│   └── app.py                        # Main application entry point
├── .config/
│   └── app_config.toml               # API keys and app settings (local only)
└── .streamlit/
    └── config.toml                   # Streamlit configuration (local only)
```

## Getting Started

1. **Clone this repository**

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run src/app.py
   ```

## Configuration

### Critical Settings Files

- **`.config/app_config.toml`:** Contains API keys and application settings
  - Managed through the **API Settings** page
  - Should be kept local (added to `.gitignore`)

- **`.streamlit/config.toml`:** Contains Streamlit configuration
  - Managed through the **Theme Settings** page
  - Must include this setting for proper sidebar display:

  ```toml
  [client]
  showSidebarNavigation = false
  ```

## Adding New Pages

- Create a new Python file in the `src/pages` directory.
- Extend the `BasePage` class and implement required methods:

```python
from pages.base_page import BasePage

class MyNewPage(BasePage):
    def show_page(self):
        # Page content implementation
        pass

    def label(self):
        return "My New Page"  # Menu label

    def icon(self):
        return "star"  # Bootstrap icon name

    def order(self):
        return 10  # Menu position
```

## Hierarchical Menus

The application supports hierarchical menus (parent-child relationships) with a simplified approach:

### Creating Parent-Child Relationships

1. **For Child Pages**: Simply specify the parent module name in the `parent()` method:

   ```python
   def parent(self):
       # This must match the module name of the parent page
       return "menu_demo"
   ```

2. **For Parent Pages**: No need to explicitly list children! The menu structure is built automatically by detecting which pages have declared this page as their parent.

   However, if you want to explicitly control the children or their order, you can still override the `children()` method:

   ```python
   def children(self):
       # Optional - only needed if you want to explicitly control children
       return ["menu_demo_child1", "menu_demo_child2"]
   ```

3. **Menu Groups**: To create a menu group (a parent item that can be expanded), set the appropriate group type:

   ```python
   def group_type(self):
       return "group"  # Creates an expandable menu group
   ```

### How It Works

The system automatically:

- Identifies parent-child relationships by checking each page's `parent()` method
- Builds a mapping of parent pages to their children
- Prioritizes explicitly defined children (via `children()`) but falls back to auto-detected children
- Sorts children by their `order()` value

This approach eliminates redundancy and makes maintaining menu structures much easier.

## LLM Integration

The application supports multiple LLM providers through a unified interface:

- **OpenAI** (GPT models)
- **Anthropic** (Claude models)
- **Google** (Gemini models)

Configure API keys on the **App Settings** page.

## License

[MIT License](LICENSE)

## Starting point

This project is designed as a starting point for LLM-powered Streamlit applications. Fork and customize it to fit your specific needs and go from there.

An alternate way to create a new project is this:

1. **Clone this repository**

2. **Create a new project <new-projectname> on GitHub**
   
3. **Duplicate and rename a local copy of the Starter project**

4. **Re-initialise git:**
   ```bash
   rm -rf .git
   git init
   git add .
   git commit -m "Initial commit for <new-projectname>"
   git remote add origin \
   https://github.com:YOURUSERNAME/new-projectname.git
   git branch -M main
   git push -u origin main
   ```

5. **Run the application:**
   ```bash
   streamlit run src/app.py
   ```
