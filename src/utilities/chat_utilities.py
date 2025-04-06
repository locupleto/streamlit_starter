# ============================================================================
# -*- coding: utf-8 -*-
#
# Module:      chat_utilities.py
# Description: Common utility functions for managing chat sessions, including
#              creation, saving, loading, and displaying chat histories.
#              Supports multiple assistant types and integrates with the
#              Streamlit-based user interface.
#
# History:
# 2024-07-17   urot Created
# 2025-03-01   urot Added support for d2 diagram visualizations in chats
# 2025-03-01   urot Added support for Mermaid diagram visualizations in chats
# 2025-04-06   urot Added directory creation and improved error handling
# ============================================================================

import os
import json
from datetime import datetime
import uuid
import streamlit as st
import re
import subprocess
import tempfile
import logging

# Configure logging
logger = logging.getLogger(__name__)

def create_new_chat():
    """
    Create a new chat session for an assistant.

    Returns:
        tuple: (chat_id, filename)
    """
    chat_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{chat_id}.json"
    return chat_id, filename

def get_chat_directory(assistant_name):
    """
    Get the chat directory for the specified assistant and create it if it doesn't exist.

    Args:
        assistant_name (str): Name of the assistant

    Returns:
        str: Path to the chat directory
    """
    chat_dir = f"{assistant_name}_chat_history"

    # Create the directory if it doesn't exist
    if not os.path.exists(chat_dir):
        try:
            os.makedirs(chat_dir)
            logger.info(f"Created chat history directory: {chat_dir}")
        except Exception as e:
            logger.error(f"Error creating chat directory {chat_dir}: {str(e)}")

    return chat_dir

def save_chat(assistant_name, chat_id, messages):
    """
    Save chat messages to a file.

    Args:
        assistant_name (str): Name of the assistant
        chat_id (str): Unique identifier for the chat
        messages (list): List of message dictionaries

    Returns:
        bool: True if successful, False otherwise
    """
    if not messages:  # Don't save empty chat histories
        return False

    folder = get_chat_directory(assistant_name)

    try:
        # Find the existing file for this chat_id
        existing_files = [f for f in os.listdir(folder) if chat_id in f and f.endswith('.json')]

        # Generate new filename with current timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{timestamp}_{chat_id}.json"
        new_file_path = os.path.join(folder, new_filename)

        # If an existing file is found, rename it
        if existing_files:
            old_file_path = os.path.join(folder, existing_files[0])
            os.rename(old_file_path, new_file_path)

        # Save the updated chat content
        with open(new_file_path, 'w') as f:
            json.dump(messages, f)
        return True
    except Exception as e:
        logger.error(f"Error saving chat: {str(e)}")
        return False

def load_chat(assistant_name, chat_id):
    """
    Load a specific chat session.

    Args:
        assistant_name (str): Name of the assistant
        chat_id (str or tuple): Unique identifier for the chat session

    Returns:
        list: List of message dictionaries, or empty list if not found
    """
    folder = get_chat_directory(assistant_name)

    try:
        # Extract chat_id if it's part of a tuple
        if isinstance(chat_id, tuple):
            chat_id = chat_id[0]

        # Find files that contain the chat_id and end with .json
        matching_files = [f for f in os.listdir(folder) if chat_id in f and f.endswith('.json')]

        if not matching_files:
            logger.info(f"No file found for chat_id {chat_id} in folder {folder}")
            return []

        if len(matching_files) > 1:
            logger.warning(f"Multiple files found for chat_id {chat_id}. Using the most recent one.")
            matching_files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)

        filename = matching_files[0]
        file_path = os.path.join(folder, filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
            if not content:  # Ignore empty files
                logger.info(f"Ignoring empty chat file: {filename}")
                return []
            return content

    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON in file for chat_id {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Unexpected error loading chat {chat_id}: {e}")

    return []

def get_recent_chats(assistant_name, limit=5):
    """
    Retrieve the most recent chat sessions.

    Args:
        assistant_name (str): Name of the assistant
        limit (int): Maximum number of recent chats to retrieve

    Returns:
        list: List of tuples containing (chat_id, chat_title)
    """
    folder = get_chat_directory(assistant_name)

    try:
        if not os.path.exists(folder):
            return []

        files = [f for f in os.listdir(folder) if f.endswith('.json')]
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)), reverse=True)

        recent_chats = []
        for file in files:
            if len(recent_chats) >= limit:
                break
            chat_id = file.split('_')[2].split('.')[0]
            file_path = os.path.join(folder, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    chat_content = json.load(f)
                    if chat_content:  # Only add non-empty chats
                        chat_title = chat_content[0]['content'][:30] + "..."
                        recent_chats.append((chat_id, chat_title))
            except Exception as e:
                logger.error(f"Error reading chat file {file_path}: {e}")
                continue

        return recent_chats
    except Exception as e:
        logger.error(f"Error retrieving recent chats: {e}")
        return []

def display_sidebar_chat_history(assistant_name, session_state, rerun_function):
    """
    Display the sidebar chat history for a given assistant with expanded buttons.

    This function shows recent chats, and allows creating a new chat. 
    It also handles loading chats clicked.

    Args:
        assistant_name (str): The name of the assistant (e.g., 'developer', 'trading')
        session_state (streamlit.SessionState): Streamlit's session state object
        rerun_function (callable): Function to rerun the Streamlit app
    """
    st.sidebar.write("Recent Chats")

    button_container = st.sidebar.container()
    recent_chats = get_recent_chats(assistant_name)

    for chat_id, chat_title in recent_chats:
        if button_container.button(chat_title, key=f"btn_{chat_id}", use_container_width=True):
            loaded_chat = load_chat(assistant_name, chat_id)
            if loaded_chat:
                session_state[f"{assistant_name}_current_chat_id"] = chat_id
                session_state[f"{assistant_name}_messages"] = loaded_chat
                rerun_function()
            else:
                st.sidebar.error(f"Failed to load chat with ID: {chat_id}")

    # Get the total number of chats
    all_chats = get_all_chats(assistant_name)
    total_chats = len(all_chats)

    st.sidebar.markdown("---")

    if st.sidebar.button("New Chat :heavy_plus_sign:", use_container_width=True, type="secondary"):
        new_chat_id, _ = create_new_chat()
        session_state[f"{assistant_name}_current_chat_id"] = new_chat_id
        session_state[f"{assistant_name}_messages"] = []
        rerun_function()

def get_all_chats(assistant_name):
    """
    Retrieve all chat histories for a given assistant.

    This function reads all JSON files in the assistant's chat history folder
    and returns a dictionary containing information about each chat session.

    Args:
        assistant_name (str): The name of the assistant (e.g., 'developer', 'trading')

    Returns:
        dict: A dictionary where keys are chat_ids and values are dictionaries
              containing 'timestamp' and 'title' for each chat.
    """
    folder = get_chat_directory(assistant_name)
    all_chats = {}

    try:
        if not os.path.exists(folder):
            return {}

        for filename in os.listdir(folder):
            if filename.endswith('.json'):
                try:
                    parts = filename.split('_')
                    if len(parts) < 3:
                        continue

                    chat_id = parts[2].split('.')[0]
                    timestamp = parts[0]

                    # Try to parse the timestamp and format it
                    try:
                        if len(timestamp) == 8:  # YYYYMMDD
                            dt = datetime.strptime(timestamp, "%Y%m%d")
                        elif len(timestamp) == 14:  # YYYYMMDDHHMMSS
                            dt = datetime.strptime(timestamp, "%Y%m%d%H%M%S")
                        else:
                            dt = datetime.now()  # Fallback if parsing fails
                        formatted_time = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        formatted_time = timestamp  # Use original string if parsing fails

                    with open(os.path.join(folder, filename), 'r') as f:
                        chat_content = json.load(f)
                        chat_title = chat_content[0]['content'][:30] + "..." if chat_content else f"Chat {chat_id[:8]}..."
                    all_chats[chat_id] = {'timestamp': formatted_time, 'title': chat_title}
                except Exception as e:
                    logger.error(f"Error processing chat file {filename}: {e}")
                    continue
    except Exception as e:
        logger.error(f"Error retrieving all chats: {e}")

    return all_chats

def initialize_or_load_chat_session(assistant_name):
    """
    Initialize a new chat session or load an existing one.

    Args:
        assistant_name (str): Name of the assistant

    Returns:
        tuple: (chat_id, messages)
    """
    messages_key = f"{assistant_name}_messages"
    current_chat_id_key = f"{assistant_name}_current_chat_id"

    # If both chat ID and messages are already in session state, return them
    if st.session_state.get(current_chat_id_key) and st.session_state.get(messages_key):
        return st.session_state[current_chat_id_key], st.session_state[messages_key]

    # Initialize session state if not already done
    if messages_key not in st.session_state:
        st.session_state[messages_key] = []
    if current_chat_id_key not in st.session_state:
        st.session_state[current_chat_id_key] = None

    current_chat_id = st.session_state[current_chat_id_key]
    messages = st.session_state[messages_key]

    # If no current chat ID, try to load the most recent chat
    if current_chat_id is None:
        recent_chats = get_recent_chats(assistant_name)
        if recent_chats:
            current_chat_id = recent_chats[0][0]
            loaded_chat = load_chat(assistant_name, current_chat_id)
            if loaded_chat:
                messages = loaded_chat
            else:
                logger.info(f"Failed to load recent chat {current_chat_id}")
                current_chat_id = None

    # Only create a new chat if there's no current chat ID and no messages
    if current_chat_id is None and not messages:
        current_chat_id, _ = create_new_chat()
        messages = []

    # Update session state
    st.session_state[current_chat_id_key] = current_chat_id
    st.session_state[messages_key] = messages

    return current_chat_id, messages

def cleanup_empty_chats(assistant_name):
    """
    Remove empty chat files for the given assistant.

    Args:
        assistant_name (str): Name of the assistant
    """
    folder = get_chat_directory(assistant_name)

    try:
        if not os.path.exists(folder):
            return

        for filename in os.listdir(folder):
            if filename.endswith('.json'):
                file_path = os.path.join(folder, filename)
                try:
                    with open(file_path, 'r') as f:
                        content = json.load(f)
                        if not content:
                            os.remove(file_path)
                            logger.info(f"Removed empty chat file: {filename}")
                except Exception as e:
                    logger.error(f"Error during cleanup of file {filename}: {e}")
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")

def visualize_any_d2_diagram(latest_query, ai_response, show_image_expanded=True):
    """
    Generate and display a diagram using the `d2` tool if the latest query requests it.

    This method performs the following steps:
      1. Converts the provided query and AI response to strings.
      2. Checks whether the query contains "d2" or "diagram" (case-insensitive).
      3. If the condition is met:
         - Creates a temporary directory to hold temporary files.
         - Writes the full AI response to a temporary file.
         - Extracts the first code block (delimited by triple backticks) from the AI response.
         - Writes the extracted code block to another temporary file.
         - Invokes the command-line tool `d2` (with the `--sketch` option) to generate an image from the code block.
         - Displays the resulting image using Streamlit.
      4. If the query does not request a diagram, displays an informational message.

    Parameters:
        latest_query (str or any): The user's latest query. This will be converted to a string.
        ai_response (str or any): The AI's complete response. This will be converted to a string.
        show_image_expanded (bool): Whether to show the image expanded by default. Default is True.

    Returns:
        bool: True if a diagram was generated and displayed, False otherwise.
    """
    # Convert inputs to strings in case they're not already.
    latest_query_str = str(latest_query)
    ai_response_str = str(ai_response)

    # Check if the query contains "d2" or "diagram" (ignoring case)
    if (
        "d2" in latest_query_str.lower() and 
        ("diagram" in latest_query_str.lower() or "sketch" in latest_query_str.lower()) and
        "mermaid" not in latest_query_str.lower()
    ) or (
        "d2" in ai_response_str.lower() and 
        ("diagram" in ai_response_str.lower() or "sketch" in ai_response_str.lower()) and
        "mermaid" not in ai_response_str.lower()
    ):
        code_block_matches = re.findall(r"```(?:\w*\n)?(.*?)```", ai_response_str, re.DOTALL)

        # Early return if no code block is found
        if not code_block_matches:
            st.warning("No diagram code was found in the response. The AI assistant may need to provide the diagram code first.")
            return False

        code_block = code_block_matches[0]

        # Early return if code block is empty
        if not code_block.strip():
            st.warning("Empty diagram code block found. The AI assistant may need to provide valid diagram code.")
            return False

        # Basic d2 syntax validation
        def appears_to_be_d2_code(code):
            # Common d2 syntax patterns
            d2_patterns = [
                r'->', # Arrows
                r'-->', # Different arrow styles
                r'<->', # Bidirectional arrows
                r'\.+', # Connections using dots
                r'shape:', # Shape definitions
                r'style:', # Style definitions
                r'direction:', # Direction specifications
                r'\{.*?\}', # Block definitions
                r'label:', # Label definitions
            ]

            # Check if the code contains at least one d2-like pattern
            return any(re.search(pattern, code) for pattern in d2_patterns)

        if not appears_to_be_d2_code(code_block):
            return False

        # Use a temporary directory for our temporary files.
        with tempfile.TemporaryDirectory() as tmpdirname:
            raw_answer_path = os.path.join(tmpdirname, "raw_ai_answer.txt")
            raw_block_path = os.path.join(tmpdirname, "raw_block.txt")
            output_img_path = os.path.join(tmpdirname, "output.svg")

            # Write the full AI response to a temporary file.
            with open(raw_answer_path, "w") as f:
                f.write(ai_response_str)

            # Write the extracted code block to a temporary file.
            with open(raw_block_path, "w") as f:
                f.write(code_block)

            # Call the d2 command on the temporary raw_block file.
            command = [
                "d2",
                "--sketch",
                raw_block_path,
                output_img_path
            ]
            with st.spinner('Processing your request...'):
                result = subprocess.run(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

            # Check for errors in the d2 command execution
            if not re.match(r"^success: ", result.stderr):
                with st.expander("Show stderr output", expanded=False):
                    st.write("d2 stderr:", result.stderr)

            # Display the image if the output file exists.
            if os.path.exists(output_img_path):
                with st.expander("Show generated diagram:", expanded=show_image_expanded):
                    st.image(output_img_path, caption="Generated Diagram", use_container_width=True)
                return True
            else:
                st.error("Failed to generate the diagram using d2.")
                return False
    return False

def check_and_visualize_d2_diagrams_in_chat_history(messages, index, show_image_expanded=False):
    """
    Check if a message pair in chat history contains a d2 diagram request and visualize it.

    Parameters:
        messages (list): List of message dictionaries with 'role' and 'content' keys
        index (int): Current index in the message list
        show_image_expanded (bool): Whether to show the image expanded by default. Default is False.

    Returns:
        bool: True if a diagram was generated and displayed, False otherwise.
    """
    # Check if this is an assistant message and there's a previous user message
    if (index > 0 and 
        messages[index]["role"] == "assistant" and 
        messages[index-1]["role"] == "user"):

        # Get the previous user message to check for diagram requests
        previous_user_message = messages[index-1]["content"]
        current_assistant_message = messages[index]["content"]

        # Visualize diagram if needed
        return visualize_any_d2_diagram(
            previous_user_message, 
            current_assistant_message, 
            show_image_expanded=show_image_expanded
        )

    return False

def visualize_any_mermaid_diagram(latest_query, ai_response,
                                  show_image_expanded=True):
    """
    Generate and display a mermaid diagram using the `mmdc` tool if the
    latest query requests it.

    This method performs the following steps:
      1. Converts the query and AI response to strings.
      2. Checks whether the query contains "mermaid" or "diagram"
         (case-insensitive).
      3. If the condition is met:
         - Creates a temporary directory for holding temporary files.
         - Writes the full AI response to a temporary file.
         - Extracts the first code block (delimited by triple backticks)
           from the AI response.
         - Writes the extracted code block to another temporary file.
         - Invokes the command-line tool `mmdc` to generate an image from
           the code block.
         - Displays the resulting image using Streamlit.
      4. If the query does not request a diagram, displays an
         informational message.

    Parameters:
        latest_query (str or any): The user's latest query.
        ai_response (str or any): The AI's complete response.
        show_image_expanded (bool): Whether to show the image expanded by
            default. Default is True.

    Returns:
        bool: True if a diagram was generated and displayed, False otherwise.
    """
    # Convert inputs to strings in case they're not already
    latest_query_str = str(latest_query)
    ai_response_str = str(ai_response)

    # Check if the query explicitly requests a mermaid diagram
    lq = latest_query_str.lower()
    ar = ai_response_str.lower()

    if (
        "mermaid" in lq and ("diagram" in lq or "sketch" in lq) and "d2" not in lq
    ) or (
        "mermaid" in ar and ("diagram" in ar or "sketch" in ar) and "d2" not in ar
    ):
        code_block_matches = re.findall(
            r"```(?:\w*\n)?(.*?)```", ai_response_str, re.DOTALL
        )

        # Early return if no code block is found
        if not code_block_matches:
            st.warning("No diagram code was found in the response. The AI assistant may need to provide the diagram code first.")
            return False

        code_block = code_block_matches[0]

        # Early return if code block is empty
        if not code_block.strip():
            st.warning("Empty diagram code block found. The AI assistant may need to provide valid diagram code.")
            return False

        # Basic Mermaid syntax validation
        def appears_to_be_mermaid_code(code):
            # Common Mermaid syntax patterns
            mermaid_patterns = [
                r'graph\s+[TBLR]?[DRLR]?', # Graph declarations
                r'sequenceDiagram', # Sequence diagrams
                r'classDiagram', # Class diagrams
                r'stateDiagram-v2', # State diagrams
                r'erDiagram', # Entity Relationship diagrams
                r'pie\s*title', # Pie charts
                r'gantt', # Gantt charts
                r'flowchart\s+[TBLR]?[DRLR]?', # Flowcharts
                r'-->|--[x]|==>', # Various arrow types
                r'subgraph', # Subgraph declarations
                r'participant', # Sequence diagram participants
                r'class\s+\w+', # Class definitions
                r'state\s+\w+', # State definitions
            ]

            # Check if the code contains at least one Mermaid-like pattern
            # and doesn't contain obvious non-Mermaid patterns
            return (any(re.search(pattern, code, re.IGNORECASE) for pattern in mermaid_patterns) and
                   not re.search(r'import\s+|def\s+|class\s*:', code))  # Not Python code

        if not appears_to_be_mermaid_code(code_block):
            st.warning("The code block doesn't appear to contain valid Mermaid diagram syntax. The AI assistant may need to provide correct Mermaid code.")
            return False

        # Use a temporary directory for our temporary files
        with tempfile.TemporaryDirectory() as tmpdirname:
            raw_answer_path = os.path.join(tmpdirname, "raw_ai_answer.txt")
            raw_block_path = os.path.join(tmpdirname, "raw_block.txt")
            output_img_path = os.path.join(tmpdirname, "output.svg")

            # Write the full AI response to a temporary file
            with open(raw_answer_path, "w") as f:
                f.write(ai_response_str)

            # Write the extracted code block to a temporary file
            with open(raw_block_path, "w") as f:
                f.write(code_block)

            # Call the mmdc command on the temporary raw_block file
            command = [
                "mmdc",
                "-q",  # Quiet mode
                "-i", raw_block_path,
                "-o", output_img_path,
            ]

            with st.spinner('Processing your request...'):
                try:
                    result = subprocess.run(
                        command,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                        timeout=30  # Add timeout to prevent hanging
                    )

                    # Check for errors in the mmdc command execution
                    if result.returncode != 0:
                        with st.expander("Show stderr output", expanded=False):
                            st.write("mmdc stderr:", result.stderr)
                            st.write("mmdc stdout:", result.stdout)
                        st.error("Failed to generate the diagram using mmdc.")
                        return False

                except subprocess.TimeoutExpired:
                    st.error("Diagram generation timed out. The diagram might be too complex.")
                    return False
                except Exception as e:
                    st.error(f"An error occurred while generating the diagram: {str(e)}")
                    return False

            # Display the image if the output file exists
            if os.path.exists(output_img_path):
                try:
                    with st.expander("Show generated diagram:", expanded=show_image_expanded):
                        st.image(output_img_path, caption="Generated Diagram", use_container_width=True)
                    return True
                except Exception as e:
                    st.error(f"Failed to display the generated diagram: {str(e)}")
                    return False
            else:
                st.error("Failed to generate the diagram using mmdc.")
                return False
    return False

def check_and_visualize_mermaid_diagrams_in_chat_history(
    messages, index, show_image_expanded=False
):
    """
    Check if a message pair in chat history contains a mermaid diagram
    request and visualize it.

    Parameters:
        messages (list): List of message dictionaries with 'role' and
            'content' keys.
        index (int): Current index in the message list.
        show_image_expanded (bool): Whether to show the image expanded by
            default. Default is False.

    Returns:
        bool: True if a diagram was generated and displayed, False otherwise.
    """
    if (
        index > 0
        and messages[index]["role"] == "assistant"
        and messages[index - 1]["role"] == "user"
    ):
        previous_user_message = messages[index - 1]["content"]
        current_assistant_message = messages[index]["content"]

        return visualize_any_mermaid_diagram(
            previous_user_message,
            current_assistant_message,
            show_image_expanded=show_image_expanded,
        )
    return False