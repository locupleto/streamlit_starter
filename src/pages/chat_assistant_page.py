# ============================================================================
# -*- coding: utf-8 -*-
#
# Module:       chat_assistant_page.py
# Description:  Implements the WebAssistantPage class.
#
# History:
# 2024-07-14    urot    Created
# 2024-07-29    urot    Moved config files into .config/ directory
# ============================================================================

import streamlit as st
from datetime import datetime
import os
from pages.base_page import BasePage
from utilities.application_utilities import validate_session_state
from utilities.chat_utilities import (save_chat,   
                initialize_or_load_chat_session, display_sidebar_chat_history)
from utilities.styling_utilities import set_background_images
from models.llms import get_large_llm_model, BaseLLMModel
from avatars.assistant_avatars import USER_AVATAR, CHATBOT_AVATAR
from typing import Dict, Any
import logging

# Custom Page background
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATIC_DIR = os.path.join(BASE_DIR, 'images')
MAIN_CONTAINER_BKG_IMAGE = os.path.join(STATIC_DIR, 'green-paper.png')
PROMPT_CONTAINER_BKG_IMAGE = os.path.join(STATIC_DIR, 'green-paper-prompt.png')
ASSISTANT_NAME = "chat"

HELPFUL_ASSISTANT_TEMPLATE =\
"""
<system_message>
    <role>Helpful AI Assistant for answering questions and having a dialog</role>
    <description>
        You are an expert AI assistant specializing in answering user queries. 
    </description>
    <current_datetime>{}</current_datetime>
    <instruction>
        ALWAYS Answer the user question as best you can in a style and manner true to you character!
    </instruction>
</system_message>
"""

IRONIC_COMEDIAN_ASSISTANT_TEMPLATE =\
"""
<system_message>
    <role>Lazy and ironic comedian</role>
    <description>
        You are a very lazy and ironic assistant that recents having yo answer the users questions and make fun of him or her. 
    </description>
    <current_datetime>{}</current_datetime>
    <instruction>
        ALWAYS Answer the user question as best you can in a style and manner true to you character!
    </instruction>
</system_message>
"""

# Choose which template to use as the default
SYSTEM_PROMPT_TEMPLATE = IRONIC_COMEDIAN_ASSISTANT_TEMPLATE

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatAssistantPage(BasePage):
    def __init__(self):
        if 'chat_current_chat_id' not in st.session_state:
            st.session_state.chat_current_chat_id = None

    def validate_page_session_state(self):
        validate_session_state()

        if "openai_api_key" not in st.session_state:
            st.error("OpenAI API key is not set. Please set it in the settings page.")
            return
        if "anthropic_api_key" not in st.session_state:
            st.error("Anthropic API key is not set. Please set it in the settings page.")
            return
        st.session_state.chat_current_chat_id, st.session_state.chat_messages = initialize_or_load_chat_session(ASSISTANT_NAME)

    def prepare_messages(self):
        messages = []
        last_role = None
        for message in st.session_state.chat_messages:
            if isinstance(message["content"], dict) and "type" in message["content"]:
                continue # Skip non-text messages like quotes

            # Ensure roles alternate
            if last_role == message["role"] == "user":
                messages.append({"role": "assistant", "content": "I understand."})

            messages.append({"role": message["role"], "content": message["content"]})
            last_role = message["role"]

        # Ensure the last message is from the user
        if last_role != "user":
            messages.append({"role": "user", "content": "Please continue."})
        return messages
    
    def show_page(self):
        self.validate_page_session_state()

        # Display chat history in the sidebar
        display_sidebar_chat_history("chat", st.session_state, st.rerun)

        # Display background image
        set_background_images(MAIN_CONTAINER_BKG_IMAGE, PROMPT_CONTAINER_BKG_IMAGE)

        # Display chat history
        for message in st.session_state.chat_messages:
            avatar = USER_AVATAR if message["role"] == "user" else CHATBOT_AVATAR
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

        # User Query...
        enable_attatchments = False # "multiple"
        model_signature = BaseLLMModel.large_model_name()
        if prompt := st.chat_input(f"{model_signature}: What can I help you with?",
                                   accept_file=enable_attatchments,
                                   file_type=['txt','png','jpg','jpeg']):
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            with st.chat_message("user", avatar=USER_AVATAR):
                if prompt and enable_attatchments:
                    if prompt["files"]:
                        for uploaded_file in prompt["files"]:
                            file_id = uploaded_file.file_id
                            name = uploaded_file.name
                            type = uploaded_file.type
                            size = uploaded_file.size

                            st.write(f"📄 **{name}**")
                            st.write(f"• Type: `{type}`")
                            st.write(f"• Size: `{size}` bytes")

                            # To read file as bytes:
                            urls = uploaded_file._file_urls
                            bytes_data = uploaded_file.getvalue()
                            st.write(bytes_data)
                    #ChatInputValue
                    st.write(prompt['text'])
                    pass
                    #st.image(prompt["files"][0])                            
                else:
                    st.markdown(prompt)

            # Assistant (streaming) response...
            with st.chat_message("assistant", avatar=CHATBOT_AVATAR):
                response = self.generate_response()
                if response.strip():  # Check if response is not empty
                    st.session_state.chat_messages.append({"role": "assistant", "content": response})

                    # Save chat history after each interaction
                    try:
                        save_chat("chat", st.session_state.chat_current_chat_id, st.session_state.chat_messages)
                    except Exception as e:
                        st.error(f"An error occurred while saving the chat: {str(e)}")

    def generate_response(self):
        messages = self.prepare_messages()
        ai_response = ""

        # Get current time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Format the template with the current time
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(current_time)
        
        try:
            model = get_large_llm_model(system_message=system_prompt, temperature=0)
            ai_response = model.stream_response(messages)
        except Exception as e:
            error_message = f"I'm very sorry but an error occurred:  \n\n{str(e)}"
            st.error(error_message)
            ai_response = error_message
        return ai_response

    def icon(self):
        return "chat-right-dots"

    def order(self):
        return 83
    
    def label(self):
        return "Chat Assistant"