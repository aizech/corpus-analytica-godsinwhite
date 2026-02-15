"""
Medical Imaging Agent module.
This module provides a factory function to create a medical imaging analysis agent.
"""

from copy import deepcopy

from agno.agent import Agent
from agno.knowledge.knowledge import Knowledge
from agno.memory import MemoryManager
from agno.models.base import Model
from agno.tools.duckduckgo import DuckDuckGoTools

# Base prompt that defines the agent's expertise and response structure
BASE_PROMPT = """You are a highly skilled medical imaging expert with extensive knowledge in radiology 
and diagnostic imaging. Your role is to provide comprehensive, accurate, and ethical analysis of medical images.

Key Responsibilities:
1. Maintain patient privacy and confidentiality
2. Provide objective, evidence-based analysis
3. Highlight any urgent or critical findings
4. Explain findings in both professional and patient-friendly terms

For each image analysis, structure your response as follows:"""

# Detailed instructions for image analysis
ANALYSIS_TEMPLATE = """
### 1. Image Technical Assessment
- Imaging modality identification
- Anatomical region and patient positioning
- Image quality evaluation (contrast, clarity, artifacts)
- Technical adequacy for diagnostic purposes

### 2. Professional Analysis
- Systematic anatomical review
- Primary findings with precise measurements
- Secondary observations
- Anatomical variants or incidental findings
- Severity assessment (Normal/Mild/Moderate/Severe)

### 3. Clinical Interpretation
- Primary diagnosis (with confidence level)
- Differential diagnoses (ranked by probability)
- Supporting evidence from the image
- Critical/Urgent findings (if any)
- Recommended follow-up studies (if needed)

### 4. Patient Education
- Clear, jargon-free explanation of findings
- Visual analogies and simple diagrams when helpful
- Common questions addressed
- Lifestyle implications (if any)

### 5. Evidence-Based Context
Using search:
- Recent relevant medical literature
- Standard treatment guidelines
- Similar case studies
- Technological advances in imaging/treatment
- 2-3 authoritative medical references

Please maintain a professional yet empathetic tone throughout the analysis.
"""

# Combine prompts for the final instruction
FULL_INSTRUCTIONS = BASE_PROMPT + ANALYSIS_TEMPLATE


def create_medical_imaging_agent(
    model: Model, memory: MemoryManager, knowledge: Knowledge
) -> Agent:
    """
    Create a medical imaging agent that can analyze various types of medical images.

    Args:
        model: The model to use for the agent
        memory: The memory to use for the agent
        knowledge: The knowledge to use for the agent

    Returns:
        An Agent instance configured as a medical imaging expert agent
    """
    # Create a copy of the model to avoid side effects of the model being modified
    model_copy = deepcopy(model)

    return Agent(
        name="Medical Imaging Expert",
        role="Analyze and interpret medical images with professional expertise",
        model=model_copy,
        # Give the Agent the ability to update memories
        enable_agentic_memory=True,
        # OR - Run the MemoryManager automatically after each response
        enable_user_memories=True,
        knowledge=knowledge,
        tools=[DuckDuckGoTools()],
        description="You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging.",
        instructions=FULL_INSTRUCTIONS,
        markdown=True,  # Enable markdown formatting for structured output
        # add_history_to_messages=True,
        add_history_to_context=True,
        # add_datetime_to_instructions=True,
        exponential_backoff=True,
    )
