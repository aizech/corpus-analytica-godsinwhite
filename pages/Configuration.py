import streamlit as st
import json
import os
import sys
import dotenv
import importlib
import inspect
import datetime
from pathlib import Path

# Add the parent directory to the path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

# Page config
st.set_page_config(
    page_title=f"{config.APP_NAME} - Configuration",
    page_icon=config.APP_ICON,
    layout="wide",
    # initial_sidebar_state="collapsed",
    menu_items=config.MENU_ITEMS,
)

# Logo in sidebar
st.logo(config.LOGO_TEXT_PATH, size="large", icon_image=config.LOGO_ICON_PATH)


# Function to dynamically discover available agents
def discover_agents():
    agents_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "agents"
    )
    agent_options = {}

    # Find all potential agent modules (files ending with _agent.py)
    for filename in os.listdir(agents_dir):
        if filename.endswith("_agent.py") and filename != "__init__.py":
            module_name = filename[:-3]  # Remove .py extension
            agent_id = module_name.replace("_agent", "")

            # Format the display name (convert snake_case to Title Case)
            display_name = " ".join(word.capitalize() for word in agent_id.split("_"))
            agent_options[display_name] = agent_id

    return agent_options


# Dynamically load available agents
AGENT_OPTIONS = discover_agents()

# Tool options (example - adjust based on your actual tools)
TOOL_OPTIONS = {
    "Web Search": "web_search",
    "File Operations": "file_ops",
}

# Preset configurations
DEFAULT_PRESETS = {"Default": {"agents": [], "tools": []}}


# Load presets from file
def load_presets():
    presets_file = os.path.join(os.path.dirname(__file__), "..", "presets.json")
    if os.path.exists(presets_file):
        with open(presets_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return DEFAULT_PRESETS
    return DEFAULT_PRESETS


# Save presets to file
def save_presets(presets):
    presets_file = os.path.join(os.path.dirname(__file__), "..", "presets.json")
    with open(presets_file, "w") as f:
        json.dump(presets, f, indent=2)


# Function to save model configuration
def save_model_config(model_config):
    model_config_file = os.path.join(
        os.path.dirname(__file__), "..", "model_config.json"
    )
    with open(model_config_file, "w") as f:
        json.dump(model_config, f, indent=2)


# Function to load model configuration
def load_model_config():
    model_config_file = os.path.join(
        os.path.dirname(__file__), "..", "model_config.json"
    )
    default_config = {"default_model": "gpt-4o"}

    if os.path.exists(model_config_file):
        with open(model_config_file, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return default_config
    return default_config


# Main function
def main():
    st.title(f"{config.APP_ICON} Agent and Tool Configuration")

    # Load presets
    presets = load_presets()

    # Load model configuration
    model_config = load_model_config()

    # Create tabs for different configuration sections
    tab1, tab2, tab3 = st.tabs(["Configuration", "Models", "API Keys"])

    with tab1:
        st.header("Configuration Management")

        # Create two columns for the layout
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("Preset Management")

            # Select or create preset
            preset_names = list(presets.keys())
            selected_preset = st.selectbox(
                "Select or create a preset", preset_names + ["Create New..."]
            )

            if selected_preset == "Create New...":
                new_preset_name = st.text_input("New preset name")
                if new_preset_name and new_preset_name not in presets:
                    if st.button("Create Preset"):
                        presets[new_preset_name] = {"agents": [], "tools": []}
                        save_presets(presets)
                        st.success(f"Preset '{new_preset_name}' created!")
                        st.rerun()

            # Delete preset (if not default)
            if selected_preset != "Create New..." and selected_preset != "Default":
                # Use session state to track confirmation state
                if "delete_confirmation" not in st.session_state:
                    st.session_state.delete_confirmation = False
                    st.session_state.preset_to_delete = None

                # Show delete button or confirmation dialog based on state
                if (
                    not st.session_state.delete_confirmation
                    or st.session_state.preset_to_delete != selected_preset
                ):
                    # Show the delete button
                    if st.button(
                        "Delete Preset", type="secondary", key="delete_button"
                    ):
                        st.session_state.delete_confirmation = True
                        st.session_state.preset_to_delete = selected_preset
                        st.rerun()
                else:
                    # Show confirmation warning
                    st.warning(
                        f"Are you sure you want to delete preset '{selected_preset}'? This action cannot be undone."
                    )

                    # Use a different approach for buttons - no columns nesting
                    confirm_delete = st.button(
                        "Yes, Delete", type="primary", key="confirm_delete_btn"
                    )
                    cancel_delete = st.button("Cancel", key="cancel_delete_btn")

                    # Handle button actions
                    if confirm_delete:
                        del presets[selected_preset]
                        save_presets(presets)
                        st.session_state.delete_confirmation = False
                        st.session_state.preset_to_delete = None
                        st.success(f"Preset '{selected_preset}' deleted!")
                        st.rerun()

                    if cancel_delete:
                        st.session_state.delete_confirmation = False
                        st.session_state.preset_to_delete = None
                        st.rerun()

        # Only show configuration if a valid preset is selected
        if selected_preset != "Create New..." and selected_preset in presets:
            with col2:
                st.subheader(f"Configure {selected_preset}")

                # Agent selection
                st.write("**Available Agents**")

                # Create a container with max height and scrollable
                agent_container = st.container(height=300, border=True)

                # Prepare agent data
                selected_agents = []

                # Display agents in a simpler layout to avoid nesting issues
                with agent_container:
                    # Create a simple grid using HTML/CSS
                    agent_html = "<div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px;'>"

                    # Create checkboxes for each agent without using columns
                    for agent_name, agent_id in AGENT_OPTIONS.items():
                        is_selected = agent_id in presets[selected_preset]["agents"]
                        if st.checkbox(
                            agent_name, value=is_selected, key=f"agent_{agent_id}"
                        ):
                            selected_agents.append(agent_id)

                # Tool selection
                st.write("**Available Tools**")

                # Create a container with max height and scrollable
                tool_container = st.container(height=200, border=True)

                # Prepare tool data
                selected_tools = []

                # Display tools in a simpler layout to avoid nesting issues
                with tool_container:
                    # Create checkboxes for each tool without using columns
                    for tool_name, tool_id in TOOL_OPTIONS.items():
                        is_selected = tool_id in presets[selected_preset].get(
                            "tools", []
                        )
                        if st.checkbox(
                            tool_name, value=is_selected, key=f"tool_{tool_id}"
                        ):
                            selected_tools.append(tool_id)

                # Save button
                if st.button("Save Configuration", type="primary"):
                    presets[selected_preset]["agents"] = selected_agents
                    presets[selected_preset]["tools"] = selected_tools
                    save_presets(presets)
                    st.success("Configuration saved!")

    with tab2:
        st.header("AI Model Configuration")

        # Define available models
        model_options = {
            "gpt-4o": "openai:gpt-4o",
            "gpt-4o-mini": "openai:gpt-4o-mini",
            "gpt-5": "openai:gpt-5",
        }

        # Get current default model
        current_default = model_config.get("default_model", "gpt-4o")

        # Model selection
        st.subheader("Default Model")
        st.write(
            "Select the default model to use across the application. This model will be used for all HALO/GodsinWhite sessions."
        )

        selected_model_key = st.selectbox(
            "Select a model",
            options=list(model_options.keys()),
            index=(
                list(model_options.keys()).index(current_default)
                if current_default in model_options
                else 0
            ),
            key="model_selector_config",
        )

        # Save model configuration
        if st.button("Save Model Configuration", type="primary"):
            model_config["default_model"] = selected_model_key
            save_model_config(model_config)
            st.success(f"Default model set to {selected_model_key}")

    with tab3:
        st.header("API Keys Configuration")

        # Check if running on Streamlit Cloud or locally
        is_cloud = os.environ.get("STREAMLIT_RUNTIME_ENV") == "cloud"

        # Initialize session state for API keys if not already done
        if "api_keys" not in st.session_state:
            st.session_state.api_keys = {}

        st.subheader("OpenAI API Key")

        st.write(
            "How you get an [OpenAI API Key](https://help.openai.com/en/articles/4936850-where-do-i-find-my-openai-api-key)."
        )

        if is_cloud:
            # Running on Streamlit Cloud - user needs to provide their own API key
            st.warning(
                "You're running this app online. Please enter your own API key below. "
                "This key will be stored in your session and won't be saved permanently."
            )

            # Get API key from session state or empty string as default
            default_key = st.session_state.api_keys.get("OPENAI_API_KEY", "")

            # OpenAI API Key input
            openai_api_key = st.text_input(
                "Enter your OpenAI API Key",
                value=default_key,
                type="password",
                help="Your OpenAI API key for accessing GPT models",
            )

            # Save API key to session state when entered
            if openai_api_key:
                st.session_state.api_keys["OPENAI_API_KEY"] = openai_api_key
                # Update environment variable for current session
                os.environ["OPENAI_API_KEY"] = openai_api_key
                if st.button("Apply API Key"):
                    st.success("API Key applied for this session!")
            else:
                st.warning("Please enter your OpenAI API key to use this application.")

        else:
            # Running locally - read from .env file
            st.error(
                "You're running this app locally. API keys will be saved to the .env file."
            )

            # Load existing environment variables
            env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
            if os.path.exists(env_path):
                dotenv.load_dotenv(env_path)

            # OpenAI API Key
            openai_api_key = st.text_input(
                "Enter your OpenAI API Key",
                value=os.environ.get("OPENAI_API_KEY", ""),
                type="password",
                help="Your OpenAI API key for accessing GPT models",
            )

            # Save API Keys button
            if st.button("Save API Keys"):
                # Create or update .env file
                env_vars = {}
                if os.path.exists(env_path):
                    # Load existing variables
                    with open(env_path, "r") as f:
                        for line in f:
                            if "=" in line and not line.startswith("#"):
                                key, value = line.strip().split("=", 1)
                                env_vars[key] = value

                # Update with new values
                env_vars["OPENAI_API_KEY"] = openai_api_key

                # Write back to .env file
                with open(env_path, "w") as f:
                    for key, value in env_vars.items():
                        f.write(f"{key}={value}\n")

                # Update current environment
                os.environ["OPENAI_API_KEY"] = openai_api_key

                st.success("API Keys saved successfully to .env file!")


if __name__ == "__main__":
    main()
