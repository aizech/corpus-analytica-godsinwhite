"""
Research Agent module.
This module provides a factory function to create a research agent.
"""

from copy import deepcopy
from textwrap import dedent
import sys
import os

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.memory import MemoryManager
from agno.models.base import Model
from agno.models.openai import OpenAIResponses

# from agno.tools.duckduckgo import DuckDuckGoTools
# from agno.tools.pubmed import PubmedTools
# from agno.tools.openai import OpenAITools
# from copy import deepcopy


def create_research_agent(
    model: Model, memory: MemoryManager, knowledge: Knowledge
) -> Agent:
    """
    Create a research agent that can search for and synthesize information.

    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent

    Returns:
        An Agent instance configured as a research agent
    """

    return Agent(
        name="Research Agent",
        role="Conduct comprehensive research and produce in-depth reports",
        model=OpenAIResponses(id="gpt-5"),
        # memory=memory,
        # Give the Agent the ability to update memories
        enable_agentic_memory=True,
        # OR - Run the MemoryManager automatically after each response
        enable_user_memories=True,
        knowledge=knowledge,
        # tools=[ExaTools(num_results=3)],
        # Use DirectWebSearchTool for more reliable web search
        # tools=[DuckDuckGoTools()],
        # tools=[Searxng(host="https://search.mdosch.de")],
        tools=[{"type": "web_search_preview"}],
        description="You are a meticulous research analyst with expertise in synthesizing information from diverse sources. Your goal is to produce balanced, fact-based, and thoroughly documented reports on any topic requested.",
        instructions=[
            "Begin with broad searches to understand the topic landscape before narrowing to specific aspects.",
            "For each research query, use at least 3 different search terms to ensure comprehensive coverage.",
            "Critically evaluate sources for credibility, recency, and potential biases.",
            "Prioritize peer-reviewed research and authoritative sources when available.",
            "Synthesize information across sources rather than summarizing each separately.",
            "Present contrasting viewpoints when the topic involves debate or controversy.",
            "Use clear section organization with logical flow between related concepts.",
            "Include specific facts, figures, and direct quotes with proper attribution.",
            "Conclude with implications of the findings and areas for further research.",
            "Ensure all claims are supported by references and avoid speculation beyond the evidence.",
        ],
        expected_output=dedent("""\
        An engaging, informative, and well-structured report in markdown format:

        ## Engaging Report Title

        ### Overview
        {give a brief introduction of the report and why the user should read this report}
        {make this section engaging and create a hook for the reader}

        ### Section 1
        {break the report into sections}
        {provide details/facts/processes in this section}

        ... more sections as necessary...

        ### Takeaways
        {provide key takeaways from the article}

        ### References
        - [Reference 1](link)
        - [Reference 2](link)
        - [Reference 3](link)
        """),
        # add_history_to_messages=True,
        add_history_to_context=True,
        # add_datetime_to_instructions=True,
        exponential_backoff=True,
    )
