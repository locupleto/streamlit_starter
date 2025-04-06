# Streamlit Starter Project

**A robust foundation for building LLM-powered multi-page Streamlit applications with a clean, modular architecture.**

## Overview

This project provides a structured framework for rapidly developing Streamlit applications that leverage Large Language Models (LLMs). It features a modular page system, theme customization, chat interfaces with history management, and support for multiple LLM providers.

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

## LLM Integration

The application supports multiple LLM providers through a unified interface:

- **OpenAI** (GPT models)
- **Anthropic** (Claude models)
- **Google** (Gemini models)

Configure API keys on the **App Settings** page.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

> **Note:** This project is designed as a starting point for your own LLM-powered Streamlit applications. Customize it to fit your specific needs.

