"""
PDF Analyst Agent module.
This module provides a factory function to create a PDF analyst agent.
"""

from pathlib import Path
from copy import deepcopy

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.memory import MemoryManager
from agno.models.base import Model
from agno.utils.media import download_file


def create_pdf_analyst_agent(
    model: Model, memory: MemoryManager, knowledge: Knowledge
) -> Agent:
    """
    Create a PDF analyst agent that can analyze PDF files and extract insights.

    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent

    Returns:
        An Agent instance configured as a data analyst agent
    """
    # Create a copy of the model to avoid side effects of the model being modified
    deepcopy(model)

    pdf_path = Path.cwd().joinpath("downloads", "medical_history.pdf")

    # Download the file using the download_file function
    download_file(
        "https://github.com/aizech/godsinwhite/blob/main/demo_data/medical_history.pdf",
        str(pdf_path),
    )

    # agent.print_response(
    #    "Summarize the contents of the attached file.",
    #    files=[File(filepath=pdf_path)],
    # )
    # agent.print_response("Suggest me a recipe from the attached file.")

    return Agent(
        name="PDF Analyst",
        role="Analyze PDF files and extract meaningful insights",
        model=deepcopy(model),
        # Give the Agent the ability to update memories
        enable_agentic_memory=True,
        # OR - Run the MemoryManager automatically after each response
        enable_user_memories=True,
        knowledge=knowledge,
        tools=[{"type": "file_search"}],
        description="You are an expert PDF Data Analyst specialized in exploratory data analysis, statistical modeling, and data visualization. Your goal is to transform raw data into actionable insights that address user questions.",
        instructions=[
            "Start by examining data structure, types, and distributions when analyzing new datasets.",
            "Use file_search to execute SQL queries for data exploration and aggregation.",
            "When provided with a file path, create appropriate tables and verify data loaded correctly before analysis.",
            "Apply statistical rigor in your analysis and clearly state confidence levels and limitations.",
            "Accompany numerical results with clear interpretations of what the findings mean in context.",
            "Suggest visualizations that would best illustrate key patterns and relationships in the data.",
            "Proactively identify potential data quality issues or biases that might affect conclusions.",
            "Request clarification when user queries are ambiguous or when additional information would improve analysis.",
        ],
    )
