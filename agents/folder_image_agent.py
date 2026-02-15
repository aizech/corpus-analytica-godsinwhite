"""Folder Image Agent module.
This module provides a factory function to create an agent that can display images from folders.
"""

import sys
import os
from copy import deepcopy
from textwrap import dedent

from agno.agent import Agent
from agno.memory import MemoryManager
from agno.knowledge.knowledge import Knowledge
from agno.models.base import Model

# from agno.tools.thinking import ThinkingTools

# Windows-specific event loop policy for asyncio compatibility
if sys.platform == "win32":
    import asyncio

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Add the parent directory to the path to import FolderImageDisplayTools
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)


def create_folder_image_agent(
    model: Model, memory: MemoryManager, knowledge: Knowledge
) -> Agent:
    """
    Create a folder image agent that can display images from folders.

    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent

    Returns:
        An Agent instance configured as a folder image display agent
    """
    # Import FolderImageDisplayTools inside the function to avoid pickling issues
    from tools.folder_image_display import FolderImageDisplayTools

    # Create a copy of the model to avoid side effects of the model being modified
    model_copy = deepcopy(model)

    return Agent(
        name="FolderImageViewer",
        role="Display and manage images from folders",
        model=model_copy,
        # Give the Agent the ability to update memories
        enable_agentic_memory=True,
        # OR - Run the MemoryManager automatically after each response
        enable_user_memories=True,
        knowledge=knowledge,
        tools=[FolderImageDisplayTools()],
        description=dedent("""\
            You are a helpful assistant specialized in displaying and managing images from folders.
            You can browse folders, list image files, and display multiple images directly in the chat interface.
            You have expertise in file management and image organization.\
        """),
        instructions=dedent("""\
            As a folder image viewer assistant, follow these guidelines:
            
            1. **Understanding Requests**: Carefully analyze user requests about displaying images from folders
            2. **Path Validation**: Always validate folder paths and provide helpful error messages if paths don't exist
            3. **Image Discovery**: Use the list_images_in_folder tool first to show what images are available
            4. **Batch Display**: Use display_images_from_folder to show multiple images at once in the chat
            5. **User Guidance**: Provide clear information about what you're doing and what images you found
            6. **Error Handling**: If folders don't exist or contain no images, provide helpful suggestions
            
            Available tools:
            - `list_images_in_folder`: List all image files in a folder with their sizes
            - `display_images_from_folder`: Display images from a folder directly in the chat interface
            
            Always be helpful and provide clear feedback about the images you find and display!\
        """),
    )
