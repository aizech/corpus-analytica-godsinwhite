"""
YouTube Agent module.
This module provides a factory function to create a youtube agent.
https://docs.agno.com/tools/toolkits/others/youtube
"""

from copy import deepcopy

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.memory import MemoryManager
from agno.models.base import Model
from agno.tools.youtube import YouTubeTools


def create_youtube_agent(
    model: Model, memory: MemoryManager, knowledge: Knowledge
) -> Agent:
    """
    Create a YouTube agent that can obtain the captions of a YouTube video and answer questions.

    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent

    Returns:
        An Agent instance configured as a YouTube agent
    """
    # Create a copy of the model to avoid side effects of the model being modified
    model_copy = deepcopy(model)

    return Agent(
        name="YouTube",
        role="Obtain the captions of a YouTube video and answer questions.",
        model=model_copy,
        # memory=memory,
        # Give the Agent the ability to update memories
        enable_agentic_memory=True,
        # OR - Run the MemoryManager automatically after each response
        enable_user_memories=True,
        knowledge=knowledge,
        tools=[YouTubeTools()],
        description="You are a YouTube agent. Obtain the captions of a YouTube video and answer questions.",
        instructions=[],
    )
