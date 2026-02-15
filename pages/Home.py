import asyncio
import os
import nest_asyncio
import streamlit as st
from dotenv import load_dotenv
from config import config
from agno.team import Team
from agno.utils.log import logger

# TeamRunEvent is not needed as an import - using string constants for event types
from agno.media import Image
from halo import HaloConfig, create_halo
from utils import (
    about,
    add_message,
    display_tool_calls,
    example_inputs,
    knowledge_widget,
    selected_agents,
    selected_model,
    selected_tools,
    session_selector,
    show_user_memories,
    utilities_widget,
)
from agno.utils.log import log_debug

load_dotenv(override=True)

# Must precede any llm module imports
# from langtrace_python_sdk import langtrace
# from langtrace_python_sdk.utils.with_root_span import with_langtrace_root_span
# langtrace.init()

# from langfuse import get_client

# langfuse = get_client()

# Verify connection
# if langfuse.auth_check():
#    print("Langfuse client is authenticated and ready!")
# else:
#    print("Authentication failed. Please check your credentials and host.")


nest_asyncio.apply()
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon=config.APP_ICON,
    layout="wide",
    # initial_sidebar_state="collapsed",
    menu_items=config.MENU_ITEMS,
)

with open("styles.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Logo in sidebar
st.logo(config.LOGO_TEXT_PATH, size="large", icon_image=config.LOGO_ICON_PATH)


async def header():
    one_cola = st.columns([1])[0]
    with one_cola:
        col1a, col2a = st.columns([1, 5])

        with col1a:
            # image_path = os.path.join(config.ASSETS_DIR, "masteragent.png")
            image_path = config.MASTER_AGENT_ICON
            st.image(image_path, width=200)
        with col2a:
            st.markdown(f"<h1>{config.APP_NAME}</h1>", unsafe_allow_html=True)
            st.markdown(
                f"<p>{config.APP_DESCRIPTION}</p>",
                unsafe_allow_html=True,
            )


async def body() -> None:
    ####################################################################
    # Initialize User and Session State
    ####################################################################
    # Get Windows username automatically

    windows_username = "Ava"  # Default fallback
    try:
        windows_username = os.getlogin()
    except Exception:
        pass

    # Initialize persistent tool calls storage if not already present
    if "persistent_tool_calls" not in st.session_state:
        st.session_state["persistent_tool_calls"] = {}

    # Clean, lean User ID widget
    user_id = st.sidebar.text_input(
        "👤 User ID", value=windows_username, help="Your username for this session"
    )

    ####################################################################
    # Select Model
    ####################################################################
    model_id = await selected_model()

    ####################################################################
    # Select Tools
    ####################################################################
    tools = await selected_tools()

    ####################################################################
    # Select Team Members
    ####################################################################
    agents = await selected_agents()

    ####################################################################
    # Generate or retrieve session ID
    ####################################################################
    try:
        logger.info("---*--- Managing HALO session ---*---")
        # Generate session ID if not already present
        if (
            "session_id" not in st.session_state
            or st.session_state["session_id"] is None
        ):
            import uuid

            session_id = str(uuid.uuid4())
            st.session_state["session_id"] = session_id
            logger.info(f"Generated new session ID: {session_id}")
        else:
            session_id = st.session_state["session_id"]
            logger.info(f"Using existing session ID: {session_id}")
    except Exception as e:
        st.warning(f"Could not manage HALO session: {str(e)}")
        return

    ####################################################################
    # Create HALO
    ####################################################################
    halo_config = HaloConfig(
        user_id=user_id, model_id=model_id, tools=tools, agents=agents
    )

    # Check if HALO instance should be recreated
    recreate_halo = (
        "halo" not in st.session_state
        or st.session_state.get("halo") is None
        or st.session_state.get("halo_config") != halo_config
    )

    # Create HALO instance if it doesn't exist or configuration has changed
    halo: Team
    if recreate_halo:
        logger.info("---*--- Creating HALO instance ---*---")
        halo = create_halo(halo_config, session_id=session_id)
        st.session_state["halo"] = halo
        st.session_state["halo_config"] = halo_config
        logger.info("---*--- HALO instance created ---*---")
    else:
        halo = st.session_state["halo"]
        logger.info("---*--- HALO instance exists ---*---")

    logger.info(f"---*--- HALO session: {st.session_state.get('session_id')} ---*---")

    ####################################################################
    # Load agent runs (i.e. chat history) from memory if messages is not empty
    ####################################################################
    try:
        # Initialize messages list if it doesn't exist
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

        # Only load chat history if messages list is empty (first load)
        if len(st.session_state["messages"]) == 0:
            if hasattr(halo, "get_chat_history"):
                try:
                    chat_history = halo.get_chat_history()
                except Exception as inner_e:
                    if "session not found" in str(inner_e).lower():
                        chat_history = []
                    else:
                        raise
            else:
                chat_history = []
            if len(chat_history) > 0:
                logger.info("Loading chat history from database")
                # Loop through the runs and add the messages to the messages list
                for message in chat_history:
                    try:
                        if message.role == "user":
                            await add_message(message.role, str(message.content))
                        if message.role == "assistant":
                            # Check if tool_calls attribute exists
                            tool_calls = getattr(message, "tool_calls", None)
                            await add_message(
                                "assistant", str(message.content), tool_calls
                            )
                    except Exception as e:
                        logger.warning(f"Error processing message: {e}")
                        continue
    except Exception as e:
        if "session not found" in str(e).lower():
            logger.info("No chat history found for this session")
        else:
            logger.warning(f"Failed to load chat history: {e}")
        # Initialize empty messages list if it doesn't exist
        if "messages" not in st.session_state:
            st.session_state["messages"] = []

    ####################################################################
    # Get user input
    ####################################################################
    # if prompt := st.chat_input("✨ How can I help you?"):
    #    await add_message("user", prompt)

    prompt = st.chat_input(
        "✨ How can I help you?", accept_file=True, file_type=["jpg", "jpeg", "png"]
    )
    if prompt:
        images = []
        # images = [r"file://C:\Users\Computer\OneDrive\Desktop\de_giw\godsinwhite\generated_images\0c059aca-7fd2-45e9-be9c-1cae5f6ca688.png"]

        # Check if files are uploaded
        if hasattr(prompt, "files") and prompt.files:
            # Handle file input with optional text
            import datetime

            # Create uploads directory if it doesn't exist
            uploads_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"
            )
            # log_debug(f"uploads_dir: {uploads_dir}")
            os.makedirs(uploads_dir, exist_ok=True)

            uploaded_filenames = []
            # Process ALL uploaded files
            for uploaded_file in prompt.files:
                # Create unique filename to prevent overwriting
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                os.path.splitext(uploaded_file.name)[1]
                unique_filename = f"{timestamp}_{uploaded_file.name}"
                file_path = os.path.join(uploads_dir, unique_filename)

                # Save file to persistent storage
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.getvalue())

                uploaded_filenames.append(uploaded_file.name)

                # Create Agno Image object for ALL images
                agno_image = Image(filepath=file_path)
                images.append(agno_image)

                # Don't display image here - it will be shown in chat history

            # Create descriptive text content that references ALL uploaded images
            base_text = getattr(prompt, "text", "") or ""
            if base_text.strip():
                # User provided text with images
                if len(uploaded_filenames) == 1:
                    text_content = f"{base_text} (Analyzing uploaded image: {uploaded_filenames[0]})"
                else:
                    text_content = f"{base_text} (Analyzing {len(uploaded_filenames)} uploaded images: {', '.join(uploaded_filenames)})"
            else:
                # No text provided, create default message for image analysis
                if len(uploaded_filenames) == 1:
                    text_content = (
                        f"Please analyze this uploaded image: {uploaded_filenames[0]}"
                    )
                else:
                    text_content = f"Please analyze these {len(uploaded_filenames)} uploaded images: {', '.join(uploaded_filenames)}"

            # Store ALL images in session state for this message
            if "current_images" not in st.session_state:
                st.session_state["current_images"] = []
            st.session_state["current_images"] = images

            await add_message("user", text_content, images=images)

        elif hasattr(prompt, "text") and prompt.text:
            # Handle text-only input
            await add_message("user", prompt.text)
        elif isinstance(prompt, str):
            # Fallback for simple string input
            await add_message("user", prompt)

    ####################################################################
    # Show example inputs
    ####################################################################
    await example_inputs()

    ####################################################################
    # Show user memories
    ####################################################################
    await show_user_memories(halo, user_id)

    ####################################################################
    # Display agent messages
    ####################################################################
    for message in st.session_state["messages"]:
        avatar = None
        if message["role"] == "user":
            avatar = "👤"
        elif message["role"] == "assistant":
            avatar = "🤖"
        if message["role"] in ["user", "assistant"]:
            _content = message["content"]
            # if _content is not None:
            # Skip messages with None or empty content
            # Handle both string content and ChatInputValue objects
            content_str = str(_content) if _content is not None else ""
            # content_str += "Das ist ein Bild: file://C:\\Users\\Computer\\OneDrive\\Desktop\\de_giw\\godsinwhite\\generated_images\\0c059aca-7fd2-45e9-be9c-1cae5f6ca688.png"
            # log_debug(f"content_str: {content_str}")

            if (
                content_str
                and content_str.strip() != ""
                and content_str.strip().lower() != "none"
            ):
                with st.chat_message(message["role"], avatar=avatar):
                    # Generate a unique key for this message based on its content and role
                    message_key = f"{message['role']}_{hash(message['content'])}"
                    # log_debug(f"message_key: {message_key}")

                    # Store tool calls in persistent session state if they exist
                    if "tool_calls" in message and message["tool_calls"]:
                        # Store the tool calls in the persistent storage
                        st.session_state["persistent_tool_calls"][message_key] = (
                            message["tool_calls"]
                        )

                    # Display tool calls if they exist in the persistent storage
                    if message_key in st.session_state["persistent_tool_calls"]:
                        # Create a dedicated container with a stable key
                        with st.container():
                            # Display the tool calls from the persistent storage
                            display_tool_calls(
                                st.empty(),
                                st.session_state["persistent_tool_calls"][message_key],
                            )

                    # Check for image links in the content
                    import re
                    from PIL import Image as PILImage

                    # from PIL import Image

                    # Display the message content
                    st.markdown(content_str)
                    # log_debug(f"content_str: {content_str}")

                    # Display uploaded images if they exist in the message (50% size)
                    if "images" in message and message["images"]:
                        # st.write("**Uploaded Images:**")
                        # Create two columns for 50% width display
                        col1, col2 = st.columns([1, 1])
                        for idx, image in enumerate(message["images"]):
                            # log_debug(f"image huu: {image}")
                            image_filepath = image.get("filepath", image.get("url"))
                            # st.write(f"image huu: {image_filepath}")

                            # Alternate between columns for multiple images
                            current_col = col1 if idx % 2 == 0 else col2
                            with current_col:
                                try:
                                    # st.write("**Uploaded Images:**")
                                    # Check if image is located in the uploads folder
                                    uploads_dir = os.path.join(
                                        os.path.dirname(
                                            os.path.dirname(os.path.abspath(__file__))
                                        ),
                                        "uploads",
                                    )
                                    # log_debug(f"uploads_dir 1: {uploads_dir}")
                                    image_name = os.path.basename(image_filepath)
                                    # log_debug(f"image_name 1: {image_name}")
                                    image_pfad = os.path.join(uploads_dir, image_name)
                                    # log_debug(f"image_pfad 1: {image_pfad}")

                                    if os.path.isfile(image_pfad):
                                        st.write("**Uploaded Images:**")
                                        st.image(
                                            image_pfad,
                                            caption=f"Image {idx+1}: {image_name}",
                                            width=None,
                                        )

                                    # Display image from filepath at 50% size
                                    # if hasattr(image, 'filepath') and image.filepath:
                                    #    st.image(str(image.filepath), caption=f"Image {idx+1}", width=None)
                                    # elif hasattr(image, 'url') and image.url:
                                    #    st.write("**Uploaded Images 2:**")
                                    #    st.image(image.url, caption=f"Image {idx+1}", width=None)
                                except Exception as e:
                                    st.error(f"Error displaying image {idx+1}: {e}")
                    else:

                        # Check for sandbox image links (UUID-style filenames that might be referenced incorrectly)
                        # These are typically UUID filenames that should be in generated_images directory
                        sandbox_pattern = r"\[.*?\]\(sandbox:/mnt/data/([a-f0-9\-]+\.(?:png|jpg|jpeg|gif))\)"
                        sandbox_matches = re.findall(sandbox_pattern, content_str)
                        log_debug(f"sandbox_matches: {sandbox_matches}")

                        # Check for dashboard_charts and other chart directory links
                        chart_pattern = r"\[.*?\]\(.*?(dashboard_charts|business_charts|charts)[/\\]([^)]+)\)"
                        # search for the chart name and the file extension
                        # chart_pattern = r'\[.*?\]\(.*?(dashboard_charts|business_charts|charts)[/\\]([^)]+\.(?:png|jpg|jpeg|gif|bmp|webp|svg))\)'
                        chart_matches = re.findall(chart_pattern, content_str)
                        log_debug(f"chart_matches: {chart_matches}")

                        for chart_dir, img_filename in chart_matches:
                            # log_debug(f"img_filename: {img_filename}")
                            # Search for the image file in the chart directory
                            chart_dir_path = os.path.join(
                                os.path.dirname(
                                    os.path.dirname(os.path.abspath(__file__))
                                ),
                                chart_dir,
                            )
                            if os.path.exists(chart_dir_path):
                                # Look for files that match the filename pattern
                                for file in os.listdir(chart_dir_path):
                                    if file.startswith(img_filename.split(".")[0]):
                                        img_path = os.path.join(chart_dir_path, file)
                                        # log_debug(f"Found matching file: {img_path}")
                                        break
                                else:
                                    # If no matching file found, use the original path
                                    img_path = os.path.join(
                                        chart_dir_path, img_filename
                                    )
                            else:
                                img_path = os.path.join(
                                    os.path.dirname(
                                        os.path.dirname(os.path.abspath(__file__))
                                    ),
                                    chart_dir,
                                    img_filename,
                                )

                            # img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), chart_dir, img_filename)
                            # img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), chart_dir, img_filename)
                            log_debug(f"img_path: {img_path}")
                            if os.path.exists(img_path):
                                try:
                                    img = PILImage.open(img_path)
                                    # Calculate 50% of the container width
                                    col1, col2 = st.columns([1, 1])
                                    with col1:
                                        st.image(
                                            img,
                                            caption=f"Chart: {img_filename}",
                                            width="stretch",
                                        )
                                        break
                                except Exception as e:
                                    st.error(f"Error displaying chart: {e}")

                        # Check for local file image links
                        file_pattern = r"\[.*?\]\(file:///(.*?\.(?:png|jpg|jpeg|gif))\)"
                        file_matches = re.findall(file_pattern, content_str)
                        log_debug(f"file_matches: {file_matches}")

                        # Check for relative path image links (./path/image.png)
                        relative_pattern = (
                            r"\[.*?\]\(\.?/?([^)]*\.(?:png|jpg|jpeg|gif))\)"
                        )
                        relative_matches = re.findall(relative_pattern, content_str)
                        log_debug(f"relative_matches: {relative_matches}")

                        # Display sandbox images if found (map sandbox references to generated_images directory)
                        # for img_filename in sandbox_matches or generated_matches or file_matches:
                        #    #log_debug(f"img_filename: {img_filename}")
                        #    # Map sandbox references to the actual generated_images directory
                        #    #img_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "generated_images", img_filename)
                        #    img_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "generated_images", img_filename)
                        #
                        #    if os.path.exists(img_path):
                        #        try:
                        #            #img = Image.open(img_path)
                        #            img = PILImage.open(img_path)
                        #            # Calculate 50% of the container width
                        #            col1, col2 = st.columns([1, 1])
                        #            with col1:
                        #                st.image(img, caption=f"Generated Image: {img_filename}", width="stretch")
                        #        except Exception as e:
                        #            st.error(f"Error displaying sandbox image: {e}")
                        #    else:
                        #        # If not found, show a helpful error message
                        #        st.warning(f"Image not found: {img_filename}. Please check if the file exists in the generated_images directory.")

                        # Display relative path images
                        for img_filename in relative_matches:
                            log_debug(f"img_filename: {img_filename}")
                            # Try different base paths
                            possible_paths = [
                                os.path.join(
                                    os.path.dirname(os.path.abspath(__file__)),
                                    img_filename,
                                ),
                                os.path.join(os.getcwd(), img_filename),
                                img_filename,  # Try absolute path as-is
                            ]

                            for full_path in possible_paths:
                                if os.path.exists(full_path):
                                    try:
                                        img = PILImage.open(full_path)
                                        # Calculate 50% of the container width
                                        col1, col2 = st.columns([1, 1])
                                        with col1:
                                            st.image(
                                                img,
                                                caption=f"Image: {os.path.basename(full_path)}",
                                                width="stretch",
                                            )
                                            break  # Stop trying other paths once we find the image
                                    except Exception:
                                        continue  # Try next path

    ####################################################################
    # Generate response for user message
    ####################################################################
    last_message = (
        st.session_state["messages"][-1] if st.session_state["messages"] else None
    )
    if last_message and last_message.get("role") == "user":
        user_message = last_message["content"]
        message_images = last_message.get("images", [])
        logger.info(f"Responding to message: {user_message}")
        if message_images:
            logger.info(f"Message includes {len(message_images)} images")

        with st.chat_message("assistant", avatar="🤖"):
            # Create container for tool calls
            tool_calls_container = st.empty()

            response = ""
            try:
                # Initialize streaming state
                if "streaming_response" not in st.session_state:
                    st.session_state["streaming_response"] = ""
                if "streaming_active" not in st.session_state:
                    st.session_state["streaming_active"] = False

                # Start streaming if not already active
                if not st.session_state["streaming_active"]:
                    st.session_state["streaming_active"] = True
                    st.session_state["streaming_response"] = ""

                    # Create status indicator
                    with st.status("Thinking...", expanded=False) as status:
                        # Run the agent and collect response
                        if message_images:
                            # Pass images directly as parameter to arun method
                            run_response = halo.arun(
                                user_message,
                                images=message_images,
                                stream=True,
                                stream_intermediate_steps=True,
                            )
                        else:
                            run_response = halo.arun(
                                user_message,
                                stream=True,
                                stream_intermediate_steps=True,
                            )

                        status.update(label="Processing...", state="running")

                        async for resp_chunk in run_response:
                            # Debug: Log all events to understand what's happening
                            if hasattr(resp_chunk, "event"):
                                logger.debug(f"Received event: {resp_chunk.event}")

                            # Handle tool call started events
                            if (
                                resp_chunk.event == "TeamToolCallStarted"
                                and hasattr(resp_chunk, "tool")
                                and resp_chunk.tool
                            ):
                                if "current_tool_calls" not in st.session_state:
                                    st.session_state["current_tool_calls"] = []

                                tool_id = getattr(
                                    resp_chunk.tool, "tool_name", None
                                ) or getattr(resp_chunk.tool, "name", None)
                                is_duplicate = any(
                                    getattr(t, "tool_name", None) == tool_id
                                    or getattr(t, "name", None) == tool_id
                                    for t in st.session_state["current_tool_calls"]
                                )

                                if tool_id and not is_duplicate:
                                    st.session_state["current_tool_calls"].append(
                                        resp_chunk.tool
                                    )
                                    display_tool_calls(
                                        tool_calls_container,
                                        st.session_state["current_tool_calls"],
                                    )

                            # Handle tool calls from tools array
                            elif (
                                hasattr(resp_chunk, "tools")
                                and resp_chunk.tools
                                and len(resp_chunk.tools) > 0
                            ):
                                if "current_tool_calls" not in st.session_state:
                                    st.session_state["current_tool_calls"] = []

                                for tool in resp_chunk.tools:
                                    tool_id = None
                                    if hasattr(tool, "get"):
                                        tool_id = tool.get("name") or tool.get(
                                            "tool_name"
                                        )
                                    else:
                                        tool_id = getattr(
                                            tool, "name", None
                                        ) or getattr(tool, "tool_name", None)

                                    is_duplicate = False
                                    for t in st.session_state["current_tool_calls"]:
                                        existing_tool_id = None
                                        if hasattr(t, "get"):
                                            existing_tool_id = t.get("name") or t.get(
                                                "tool_name"
                                            )
                                        else:
                                            existing_tool_id = getattr(
                                                t, "name", None
                                            ) or getattr(t, "tool_name", None)

                                        if existing_tool_id == tool_id:
                                            is_duplicate = True
                                            break

                                    if tool_id and not is_duplicate:
                                        st.session_state["current_tool_calls"].append(
                                            tool
                                        )

                                display_tool_calls(
                                    tool_calls_container,
                                    st.session_state["current_tool_calls"],
                                )

                            # Accumulate response content - try multiple event types
                            if (
                                resp_chunk.event == "TeamRunResponseContent"
                                or resp_chunk.event == "TeamRunContent"
                                or resp_chunk.event == "run_content"
                                or resp_chunk.event == "content"
                            ) and resp_chunk.content is not None:
                                response += resp_chunk.content
                                st.session_state["streaming_response"] = response
                                logger.debug(
                                    f"Accumulated response length: {len(response)}"
                                )

                            # Also check if there's a response attribute directly
                            elif (
                                hasattr(resp_chunk, "response")
                                and resp_chunk.response is not None
                            ):
                                response += str(resp_chunk.response)
                                st.session_state["streaming_response"] = response
                                logger.debug(
                                    f"Accumulated response from response attr: {len(response)}"
                                )

                    # Reset streaming state
                    st.session_state["streaming_active"] = False

                    # Display the accumulated response after status completion
                    if st.session_state["streaming_response"]:
                        response = st.session_state["streaming_response"]
                        st.markdown(response)
                    else:
                        # If no response was captured through streaming, show a message
                        response = "No response received from the agent."
                        st.markdown(response)

                    # Add the response to the messages with the accumulated tool calls
                    message_key = f"assistant_{hash(response)}"

                    # Add the response to the messages with the accumulated tool calls
                    tool_calls_to_use = None
                    if (
                        "current_tool_calls" in st.session_state
                        and st.session_state["current_tool_calls"]
                    ):
                        # Use the accumulated tool calls from the session state
                        tool_calls_to_use = st.session_state["current_tool_calls"]
                        # Store in persistent storage
                        st.session_state["persistent_tool_calls"][
                            message_key
                        ] = tool_calls_to_use
                        # Add the message with tool calls
                        await add_message("assistant", response, tool_calls_to_use)
                        # Clear the current tool calls for the next response
                        st.session_state["current_tool_calls"] = []
                    else:
                        # No tool calls to add
                        await add_message("assistant", response)
            except Exception as e:
                logger.error(f"Error during agent run: {str(e)}", exc_info=True)
                error_message = f"Sorry, I encountered an error: {str(e)}"
                await add_message("assistant", error_message)
                st.error(error_message)

    ####################################################################
    # Knowledge widget
    ####################################################################
    await knowledge_widget(halo)

    ####################################################################
    # Session selector
    ####################################################################
    await session_selector(halo, halo_config)

    ####################################################################
    # About section
    ####################################################################
    await utilities_widget(halo)


def main():
    """Main function using synchronous Streamlit pattern with streaming fragments"""
    # Initialize session state synchronously
    if "halo" not in st.session_state:
        st.session_state["halo"] = None
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # Run header and body synchronously
    asyncio.run(header())
    asyncio.run(body())
    asyncio.run(about())


# Apply nest_asyncio for compatibility
nest_asyncio.apply()

# Execute main function
main()
