"""
Data Analyst Agent module.
This module provides a factory function to create a data analyst agent.
"""

from copy import deepcopy

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.memory import MemoryManager
from agno.models.base import Model
from agno.tools.duckdb import DuckDbTools


def create_data_analyst_agent(
    model: Model, memory: MemoryManager, knowledge: Knowledge
) -> Agent:
    """
    Create a data analyst agent that can analyze data sets and extract insights.

    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent

    Returns:
        An Agent instance configured as a data analyst agent
    """
    # Create a copy of the model to avoid side effects of the model being modified
    model_copy = deepcopy(model)

    return Agent(
        name="Data Analyst",
        role="Analyze data sets and extract meaningful insights",
        model=model_copy,
        # Give the Agent the ability to update memories
        enable_agentic_memory=True,
        # OR - Run the MemoryManager automatically after each response
        enable_user_memories=True,
        knowledge=knowledge,
        tools=[DuckDbTools()],
        description="You are an expert Data Scientist specialized in exploratory data analysis, statistical modeling, and data visualization. Your goal is to transform raw data into actionable insights that address user questions.",
        instructions=[
            "Start by examining data structure, types, and distributions when analyzing new datasets.",
            "Use DuckDbTools to execute SQL queries for data exploration and aggregation.",
            "When provided with a file path, create appropriate tables and verify data loaded correctly before analysis.",
            "Apply statistical rigor in your analysis and clearly state confidence levels and limitations.",
            "Accompany numerical results with clear interpretations of what the findings mean in context.",
            "Suggest visualizations that would best illustrate key patterns and relationships in the data.",
            "Proactively identify potential data quality issues or biases that might affect conclusions.",
            "Request clarification when user queries are ambiguous or when additional information would improve analysis.",
        ],
    )
