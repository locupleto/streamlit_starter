# ============================================================================
# -*- coding: utf-8 -*-
#
# Module:      llms.py
# Description: Wrapper classes for LLM endpoints. 
#
# Requirements:
#              pip install colorlog
#              pip install requests
#              pip install openai langchain_openai
#              pip install anthropic langchain_anthropic
#              pip install --upgrade langchain-google-genai
#
# History:
# 2024-07-27   urot Created
# 2024-07-28   urot Refactored for unified structure
# ============================================================================

import streamlit as st
import json
import re
import logging
from typing import List, Dict, Any
from abc import ABC, abstractmethod
from utilities.application_utilities import read_api_settings
from langchain_openai import ChatOpenAI
from openai import OpenAI
from langchain_anthropic import ChatAnthropic
import anthropic
from langchain_google_genai import ChatGoogleGenerativeAI
import google.generativeai as genai
from langchain_core.messages import AIMessage
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    HarmBlockThreshold,
    HarmCategory,
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
    
class BaseLLMModel(ABC):
    """Abstract base class for LLM models."""

    def __init__(self, system_message: str, temperature: float, 
                 model: str = None, json_response: bool = False, tools = []):
        """
        Initialize the LLM model.

        Args:
            system_message (str): The system message to be used.
            temperature (float): Sampling temperature.
            model (str, optional): Model name.
            json_response (bool): Flag to indicate if the response should be JSON formatted.
        """
        self.system_message = system_message
        self.temperature = temperature
        self.model = model
        self.json_response = json_response
        self.headers = {'Content-Type': 'application/json'}

    @abstractmethod
    def invoke(self, messages: List[Dict[str, str]]) -> str:
        """Invoke the model with the given messages."""
        pass

    def stream_response(self, messages):
        """
        Stream the response from the model and handle different streaming implementations.
        """
        model_class = self.__class__.__name__

        if model_class == "OpenAIModel":
            stream = self.stream(messages)
            return st.write_stream(stream)
        elif model_class == "ClaudeModel":
            stream = self.stream(messages)
            with stream as stream:
                return st.write_stream(stream.text_stream)
        elif model_class == "GeminiModel":
            stream = self.stream(messages)
            message_placeholder = st.empty()
            full_response = ""
            for chunk in stream:
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")
            message_placeholder.markdown(full_response)
            return full_response
        else:
            return f"Error: Streaming not implemented for {model_class}"

    def _process_response(self, response_content: str) -> str:
        """Process the response content based on the json_response flag."""
        if self.json_response:
            return json.dumps(json.loads(response_content))
        return response_content

    def _handle_error(self, e: Exception) -> str:
        """Handle errors during model invocation."""
        error_message = f"Error in invoking model! {str(e)}"
        logger.error(error_message)
        return json.dumps({"error": error_message})
    
    def short_model_name(self):
        """
        Returns the model name excluding any date version part, suitable for use
        in e.g. the greeting prompt of chat-bots or assistants. 
        """
        return self.large_model_name(self.model)

    @staticmethod
    def large_model_name() -> str:
        """
        Reads the full current large model from the application settings file.
        Extracts the model name part, excluds any date version part if present,
        and capitalizes the first letter of each word between '-' signs.

        This method can be used both as an instance method and as a static 
        method.

        Args:
        model_string (str): The input model string 
        (e.g., "claude-3-5-sonnet-20240620", "gpt-4o", or "gpt-4-mini")

        Returns:
        str: The model name without the date version part, with each word capitalized
        """
        api_settings = read_api_settings()
        model_string = api_settings.get("large_model")

        # Pattern to match date formats: YYYY-MM-DD or YYYYMMDD at the end of the string
        date_pattern = r'-?(\d{4}(-?\d{2}){2})$'

        # Try to find a match
        match = re.search(date_pattern, model_string)

        if match:
            # If a date is found, remove it
            model_name = model_string[:match.start()]
            # Remove any trailing dash if present
            model_name = model_name.rstrip('-')
        else:
            # If no date is found, use the original string
            model_name = model_string

        # Capitalize each word between '-' signs
        words = model_name.split('-')
        capitalized_words = [word.capitalize() for word in words]
        capitalized_model_name = '-'.join(capitalized_words)

        return capitalized_model_name

class ClaudeModel(BaseLLMModel):
    def __init__(self, system_message: str, temperature: float, 
                 model: str = None, json_response: bool = False, 
                 tools: List[Any] = None):
        super().__init__(system_message, temperature, model, json_response, tools)
        api_settings = read_api_settings()
        self.api_key = api_settings.get("anthropic_api_key")
        self.model = self.model or api_settings.get("large_model")

        # Create the ChatAnthropic instance with tools for langgraph
        self.agentic_model = ChatAnthropic(
            model=self.model,
            temperature=self.temperature,
            anthropic_api_key=self.api_key
        )
        # Bind tools if any
        self.tools = tools
        if self.tools is not None:
            self.agentic_model.bind_tools(self.tools)

        # Create the native Anthropic client
        self.native_model = anthropic.Anthropic(api_key=self.api_key)

    def invoke(self, messages):
        """Invoke the Claude model with the given messages."""
        try:
            # Directly use the agentic ChatAnthropic instance
            response = self.agentic_model.invoke(messages)
            return response
        except Exception as e:
            return self._handle_error(e)

    def stream(self, messages: List[Dict[str, str]]):
        """Stream responses from the Claude model for use in Assistant chat."""
        completion = self.native_model.messages.stream(
            max_tokens=8192,
            #thinking={"type": "enabled", "budget_tokens": 1600},
            temperature=self.temperature,
            messages=messages,
            model=self.model,
            system=self.system_message
        )
        return completion

class GeminiModel(BaseLLMModel):
    def __init__(self, system_message: str, temperature: float, 
                 model: str = None, json_response: bool = False, 
                 tools: List[Any] = None):
        super().__init__(system_message, temperature, model, json_response, tools)
        api_settings = read_api_settings()
        self.api_key = api_settings.get("google_api_key")
        self.model = self.model or api_settings.get("large_model")

        # Configure the API
        genai.configure(api_key=self.api_key)

        # Initialize the native Google API model with system instruction
        self.native_model = genai.GenerativeModel(
            self.model,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ],
            system_instruction=system_message
        )

        # Initialize the Langchain model with safety settings
        self.agentic_model = ChatGoogleGenerativeAI(
            model=self.model,
            safety_settings={
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            temperature=self.temperature,
            google_api_key=self.api_key,
        )

        # Bind tools if any
        self.tools = tools
        if self.tools is not None:
            self.agentic_model = self.agentic_model.bind_tools(self.tools)

    def invoke(self, messages: List[Dict[str, str]]):
        try:
            # Prepare the content from messages
            formatted_messages = []
            for message in messages:
                if isinstance(message, dict):
                    role = message.get("role", "user")
                    content = message.get("content", "")
                else:
                    # Assuming message is a LangChain message object
                    role = message.type
                    content = message.content

                if role == "system":
                    # Prepend system message to the first user message
                    formatted_messages.append({"role": "user", "parts": [{"text": f"System: {content}"}]})
                elif role == "human" or role == "user":
                    formatted_messages.append({"role": "user", "parts": [{"text": content}]})
                elif role == "ai" or role == "assistant":
                    formatted_messages.append({"role": "model", "parts": [{"text": content}]})

            # Generate content using the native model
            response = self.native_model.generate_content(formatted_messages)

            # Return an AIMessage object to maintain compatibility
            return AIMessage(content=response.text)
        except Exception as e:
            return self._handle_error(e)

    def stream(self, messages: List[Dict[str, str]]):
        """Stream responses from the Gemini model."""
        try:
            # Use the same message formatting as in the invoke method
            formatted_messages = []
            for message in messages:
                if isinstance(message, dict):
                    role = message.get("role", "user")
                    content = message.get("content", "")
                else:
                    role = message.type
                    content = message.content

                if role == "system":
                    formatted_messages.append({"role": "user", "parts": [{"text": f"System: {content}"}]})
                elif role == "human" or role == "user":
                    formatted_messages.append({"role": "user", "parts": [{"text": content}]})
                elif role == "ai" or role == "assistant":
                    formatted_messages.append({"role": "model", "parts": [{"text": content}]})

            # Generate content using the native model with streaming
            response = self.native_model.generate_content(formatted_messages, stream=True)

            # Yield each chunk of the response
            for chunk in response:
                yield chunk.text

        except Exception as e:
            yield self._handle_error(e)

class OpenAIModel(BaseLLMModel):
    def __init__(self, system_message: str, temperature: float, 
                 model: str = None, json_response: bool = False, 
                 tools: List[Any] = None):
        super().__init__(system_message, temperature, model, json_response, tools)
        api_settings = read_api_settings()
        self.api_key = api_settings.get("openai_api_key")
        self.model = self.model or api_settings.get("large_model")

        # Create the ChatOpenAI instance with tools for langgraph
        self.agentic_model = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            api_key=self.api_key
        )
        if tools:
            self.agentic_model = self.agentic_model.bind_tools(tools)

        # Create the native OpenAI client
        self.native_model = OpenAI(api_key=self.api_key)

    def invoke(self, messages: List[Dict[str, str]]) -> str:
        try:
            # Prepare messages including the system message
            formatted_messages = [
                {"role": "system", "content": self.system_message},
                *messages
            ]

             # Invoke the ChatOpenAI instance
            response = self.agentic_model.invoke(formatted_messages)
            return response
        except Exception as e:
            return self._handle_error(e)

    def stream(self, messages: List[Dict[str, str]]):
        stream = self.native_model.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_message},
                *messages
            ],
            stream=True,
            temperature=self.temperature,
        )
        return stream

def get_llm_model(model_client: str, temperature: float, model: str = None, 
                  json_response: bool = False, system_message: str = None, 
                  tools: List[Any] = None, **kwargs) -> BaseLLMModel:
    """Get the appropriate LLM model based on the client type."""
    model_classes = {
        "anthropic": ClaudeModel,
        "google": GeminiModel,
        "openai": OpenAIModel
    }
    ModelClass = model_classes.get(model_client.lower())
    if not ModelClass:
        raise ValueError(f"Invalid model type: {model_client}")
    return ModelClass(system_message=system_message, temperature=temperature, 
                      model=model, json_response=json_response, tools=tools, 
                      **kwargs)

def get_large_llm_model(system_message: str = None, temperature: float = 0, 
                        tools: List[Any] = None) -> BaseLLMModel:
    api_settings = read_api_settings()
    model_client = api_settings.get("ai_client")
    large_model = api_settings.get("large_model")
    return get_llm_model(model_client=model_client, temperature=temperature, 
                         model=large_model, system_message=system_message, 
                         tools=tools)  

def get_small_llm_model(system_message: str = None, temperature: float = 0, 
                        tools: List[Any] = None) -> BaseLLMModel:
    api_settings = read_api_settings()
    model_client = api_settings.get("small_ai_client")
    small_model = api_settings.get("small_model")
    return get_llm_model(model_client=model_client, temperature=temperature, 
                         model=small_model, system_message=system_message, 
                         tools=tools)  