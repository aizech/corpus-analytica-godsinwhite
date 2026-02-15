"""
Visualizer Agent module.
This module provides a factory function to create a data visualization agent.
https://docs.agno.com/tools/visualization
"""

from copy import deepcopy

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.memory import MemoryManager
from agno.models.base import Model
from agno.models.openai import OpenAIChat
from agno.tools.visualization import VisualizationTools


def create_visualizer_agent(
    model: Model, memory: MemoryManager, knowledge: Knowledge
) -> Agent:
    """
    Create a Visualizer agent that can create various types of charts and data visualizations.

    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent

    Returns:
        An Agent instance configured as a Visualizer agent
    """

    # Create a copy of the model to avoid side effects of the model being modified
    # model_copy = deepcopy(model)

    return Agent(
        name="Visualizer",
        role="You are a data visualization expert and business analyst.",
        # model=model_copy,
        model=OpenAIChat(id="gpt-4o"),
        # memory=memory,
        # Give the Agent the ability to update memories
        enable_agentic_memory=True,
        # OR - Run the MemoryManager automatically after each response
        enable_user_memories=True,
        knowledge=knowledge,
        tools=[VisualizationTools(output_dir="dashboard_charts")],
        description="You are a data visualization expert and business analyst.",
        instructions=[
            "When asked to create charts, use the visualization tools available.",
            "Always provide meaningful titles, axis labels, and context.",
            "Suggest insights based on the data visualized.",
            "Format data appropriately for each chart type.",
        ],
    )
