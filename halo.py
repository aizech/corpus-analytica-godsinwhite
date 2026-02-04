import os
from dataclasses import dataclass
from pathlib import Path
from textwrap import dedent
from typing import List, Optional

from agents import get_agent
from agno.agent import Agent
from agno.knowledge.embedder.openai import OpenAIEmbedder
from agno.memory import MemoryManager
from agno.db.sqlite import SqliteDb
#from agno.models.anthropic import Claude
#from agno.models.google import Gemini
#from agno.models.groq import Groq
from agno.models.openai import OpenAIChat
from agno.team import Team
from agno.tools import Toolkit
from agno.tools.reasoning import ReasoningTools
from agno.utils.log import logger
from agno.vectordb.lancedb import LanceDb, SearchType
from knowledge import HaloKnowledge
from tools import get_toolkit
from config import config
import base64
import json
import sqlite3
import time
from datetime import datetime, timezone
from uuid import uuid4


cwd = Path(__file__).parent.resolve()
tmp_dir = cwd.joinpath("tmp")
tmp_dir.mkdir(exist_ok=True, parents=True)

# Define paths for storage, memory and knowledge
DB_PATH = tmp_dir.joinpath("halo.db")
SESSIONS_PATH = DB_PATH
MEMORY_PATH = DB_PATH
# Use a user-specific directory for knowledge to avoid permission issues
KNOWLEDGE_PATH = Path(os.path.join(os.path.expanduser("~"), "halo_knowledge"))
KNOWLEDGE_PATH.mkdir(exist_ok=True, parents=True)


def ensure_memory_schema(db_path: Path) -> None:
    """Ensure agno_memories table has the exact schema expected by current agno."""
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            def _create_v2_table() -> None:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS agno_memories (
                        memory_id VARCHAR NOT NULL PRIMARY KEY,
                        memory JSON NOT NULL,
                        input VARCHAR,
                        agent_id VARCHAR,
                        team_id VARCHAR,
                        user_id VARCHAR,
                        topics JSON,
                        feedback VARCHAR,
                        created_at BIGINT NOT NULL,
                        updated_at BIGINT
                    )
                    """
                )

            def _table_exists(table_name: str) -> bool:
                row = conn.execute(
                    "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,),
                ).fetchone()
                return row is not None

            def _to_epoch(value) -> int:
                now = int(time.time())
                if value is None:
                    return now
                if isinstance(value, (int, float)):
                    return int(value)
                if isinstance(value, str):
                    try:
                        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                        if dt.tzinfo is None:
                            dt = dt.replace(tzinfo=timezone.utc)
                        return int(dt.timestamp())
                    except Exception:
                        try:
                            return int(float(value))
                        except Exception:
                            return now
                return now

            if not _table_exists("agno_memories"):
                _create_v2_table()
                conn.commit()
                logger.info(f"Verified memory schema for {db_path}")
                return

            cursor = conn.execute("PRAGMA table_info(agno_memories)")
            existing_info = cursor.fetchall()
            existing_columns = {row[1] for row in existing_info}
            existing_pk = [row[1] for row in existing_info if row[5]]

            required_columns = {
                "memory_id",
                "memory",
                "input",
                "agent_id",
                "team_id",
                "user_id",
                "topics",
                "feedback",
                "created_at",
                "updated_at",
            }
            needs_migration = (
                not required_columns.issubset(existing_columns)
                or existing_pk != ["memory_id"]
            )

            if not needs_migration:
                logger.info(f"Verified memory schema for {db_path}")
                return

            legacy_table = f"agno_memories_legacy_{int(time.time())}"
            conn.execute(f"ALTER TABLE agno_memories RENAME TO {legacy_table}")
            _create_v2_table()

            legacy_info = conn.execute(f"PRAGMA table_info({legacy_table})").fetchall()
            legacy_columns = {row[1] for row in legacy_info}

            rows = conn.execute(f"SELECT * FROM {legacy_table}").fetchall()
            for row in rows:
                row_dict = dict(zip([d[0] for d in conn.execute(f"SELECT * FROM {legacy_table} LIMIT 0").description], row))

                memory_id = (
                    row_dict.get("memory_id")
                    or row_dict.get("id")
                    or str(uuid4())
                )

                raw_memory = row_dict.get("memory")
                if raw_memory is None:
                    memory_json = json.dumps("")
                elif isinstance(raw_memory, str):
                    try:
                        json.loads(raw_memory)
                        memory_json = raw_memory
                    except Exception:
                        memory_json = json.dumps(raw_memory)
                else:
                    memory_json = json.dumps(raw_memory)

                raw_topics = row_dict.get("topics")
                topics_json = None
                if raw_topics is not None:
                    if isinstance(raw_topics, str):
                        try:
                            json.loads(raw_topics)
                            topics_json = raw_topics
                        except Exception:
                            topics_json = json.dumps([raw_topics])
                    else:
                        topics_json = json.dumps(raw_topics)

                created_at = _to_epoch(row_dict.get("created_at"))
                updated_at = _to_epoch(row_dict.get("updated_at")) if "updated_at" in legacy_columns else created_at

                conn.execute(
                    """
                    INSERT OR IGNORE INTO agno_memories (
                        memory_id, memory, input, agent_id, team_id, user_id, topics, feedback, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        memory_id,
                        memory_json,
                        row_dict.get("input") if "input" in legacy_columns else None,
                        row_dict.get("agent_id") if "agent_id" in legacy_columns else None,
                        row_dict.get("team_id") if "team_id" in legacy_columns else None,
                        row_dict.get("user_id"),
                        topics_json,
                        row_dict.get("feedback"),
                        created_at,
                        updated_at,
                    ),
                )

            conn.commit()
            logger.info(f"Verified memory schema for {db_path}")
        finally:
            conn.close()
    except Exception as e:
        logger.warning(f"Failed to ensure memory schema: {e}")


def log_memory_schema(db_path: Path) -> None:
    """Log current memory table schema for debugging."""
    try:
        conn = sqlite3.connect(str(db_path))
        try:
            columns = conn.execute("PRAGMA table_info(agno_memories)").fetchall()
            count = conn.execute("SELECT COUNT(*) FROM agno_memories").fetchone()
            logger.info(f"agno_memories columns: {columns}")
            logger.info(f"agno_memories row count: {count[0] if count else 'unknown'}")
        finally:
            conn.close()
    except Exception as e:
        logger.warning(f"Failed to log memory schema: {e}")


@dataclass
class HaloConfig:
    user_id: str
    model_id: str = "openai:gpt-5"
    tools: Optional[List[str]] = None
    agents: Optional[List[str]] = None


# Setup memory database
ensure_memory_schema(MEMORY_PATH)
halo_db = SqliteDb(db_file=str(DB_PATH), memory_table="agno_memories")
logger.info(f"Using memory database: {DB_PATH}")
halo_memory = MemoryManager(
    db=halo_db,
    # Select the model used for memory creation and updates. If unset, the default model of the Agent is used.
    #model=OpenAIChat(id="gpt-5-mini"),
    # You can also provide additional instructions for memory management
    additional_instructions="Store important user information and preferences to personalize interactions"
)
log_memory_schema(DB_PATH)

# Setup sessions storage database
halo_sessions = halo_db

# setup knowledge database
try:
    # First try to initialize with existing table
    halo_knowledge = HaloKnowledge(
        vector_db=LanceDb(
            table_name="halo_knowledge",
            uri=str(KNOWLEDGE_PATH),
            search_type=SearchType.hybrid,
            embedder=OpenAIEmbedder(id="text-embedding-3-small"),
        )
    )
    logger.info("Successfully initialized LanceDb with existing table")
except Exception as e:
    logger.warning(f"Error initializing LanceDb: {e}")
    try:
        # Create a new LanceDb instance with schema definition
        from lancedb import connect
        import pyarrow as pa
        
        # Create a connection to the database
        logger.info(f"Creating new LanceDB connection to {KNOWLEDGE_PATH}")
        connection = connect(str(KNOWLEDGE_PATH))
        
        # Define schema for the table to match agno's LanceDB implementation
        schema = pa.schema([
            pa.field('vector', pa.list_(pa.float32(), 1536)),  # Vector field for embeddings
            pa.field('id', pa.string()),  # Document ID
            pa.field('payload', pa.string()),  # JSON string containing name, meta_data, content, usage
        ])
        
        # Create an empty table if it doesn't exist
        if "halo_knowledge" not in connection.table_names():
            logger.info("Creating new 'halo_knowledge' table with schema")
            # Create empty DataFrame with the schema
            import pandas as pd
            import numpy as np
            
            # Create a single empty row to initialize the table
            empty_df = pd.DataFrame({
                'vector': [np.zeros(1536, dtype=np.float32)],  # Vector field for embeddings
                'id': ['init'],
                'payload': [json.dumps({
                    'name': 'initialization',
                    'meta_data': {},
                    'content': 'initialization',
                    'usage': {}
                })]
            })
            
            # Create the table
            connection.create_table("halo_knowledge", data=empty_df)
            logger.info("Successfully created new 'halo_knowledge' table")
        else:
            logger.info("Table 'halo_knowledge' already exists in the database")
        
        # Initialize Knowledge with the new table
        halo_knowledge = HaloKnowledge(
            vector_db=LanceDb(
                table_name="halo_knowledge",
                uri=str(KNOWLEDGE_PATH),
                search_type=SearchType.hybrid,
                embedder=OpenAIEmbedder(id="text-embedding-3-small"),
            )
        )
        logger.info("Successfully initialized Knowledge with new table")
    except Exception as inner_e:
        logger.error(f"Failed to create LanceDB table: {inner_e}")
        # Create a fallback by recreating the database directory
        import shutil
        logger.warning("Attempting to recreate the database directory as fallback")
        
        # Backup the existing directory if it exists
        if KNOWLEDGE_PATH.exists():
            backup_path = KNOWLEDGE_PATH.with_name(f"{KNOWLEDGE_PATH.name}_backup")
            logger.info(f"Backing up existing database to {backup_path}")
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.copytree(KNOWLEDGE_PATH, backup_path)
            
            # Remove the existing directory
            logger.info(f"Removing existing database at {KNOWLEDGE_PATH}")
            shutil.rmtree(KNOWLEDGE_PATH)
        
        # Create a fresh directory
        KNOWLEDGE_PATH.mkdir(exist_ok=True, parents=True)
        
        # Try one more time with a fresh database
        try:
            from lancedb import connect
            import pandas as pd
            import numpy as np
            
            # Create a connection to the fresh database
            logger.info(f"Creating fresh LanceDB connection to {KNOWLEDGE_PATH}")
            connection = connect(str(KNOWLEDGE_PATH))
            
            # Create a single empty row to initialize the table with correct schema
            empty_df = pd.DataFrame({
                'vector': [np.zeros(1536, dtype=np.float32)],  # Vector field for embeddings
                'id': ['init'],
                'payload': [json.dumps({
                    'name': 'initialization',
                    'meta_data': {},
                    'content': 'initialization',
                    'usage': {}
                })]

            })
            
            # Define schema for the table
            schema = pa.schema([
                pa.field('vector', pa.list_(pa.float32(), 1536)),  # Vector field for embeddings
                pa.field('id', pa.string()),  # Document ID
                pa.field('payload', pa.string()),  # JSON string containing name, meta_data, content, usage
            ])
            
            # Create the table with explicit schema
            connection.create_table("halo_knowledge", data=empty_df, schema=schema)
            logger.info("Successfully created fresh 'halo_knowledge' table")
            
            # Initialize Knowledge with the new table
            halo_knowledge = HaloKnowledge(
                vector_db=LanceDb(
                    table_name="halo_knowledge",
                    uri=str(KNOWLEDGE_PATH),
                    search_type=SearchType.hybrid,
                    embedder=OpenAIEmbedder(id="text-embedding-3-small"),
                )
            )
            logger.info("Successfully initialized HaloKnowledge with fresh table")
        except Exception as final_e:
            logger.error(f"All attempts to create LanceDB failed: {final_e}")
            # Create a mock HaloKnowledge as absolute fallback
            logger.warning("Creating mock HaloKnowledge instance as final fallback")
            
            # Create a minimal mock class that implements the required interface
            class MockKnowledge:
                def search(self, *args, **kwargs):
                    return []
                    
                def add(self, *args, **kwargs):
                    logger.warning("Mock knowledge base cannot store data")
                    return True
                    
                def delete(self, *args, **kwargs):
                    return True
            
            halo_knowledge = MockKnowledge()

# Function to show bot 
def show_scotty(show=True):
    if not show:
        return
    
    # Function to encode the image
    def get_image_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # Path to your image
    image_path = os.path.join(config.ASSETS_DIR, "scotty.png")

    # Get base64 encoded image
    img_base64 = get_image_base64(image_path)

    st.markdown(f"""
        <style>
        .fixed-image {{
            position: fixed;
            bottom: 50px;
            right: 50px;
            z-index: 999;
        }}
        </style>
        <div class="fixed-image">
            <img src="data:image/png;base64,{img_base64}" width="100">
        </div>
        """, unsafe_allow_html=True
    )
    
    # Function to encode the image
    def get_image_base64(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()

    # Path to your image
    image_path = os.path.join(config.ASSETS_DIR, "scotty.png")

    # Get base64 encoded image
    img_base64 = get_image_base64(image_path)

    st.markdown(f"""
        <style>
        .fixed-image {{
            position: fixed;
            bottom: 50px;
            right: 50px;
            z-index: 999;
        }}
        </style>
        <div class="fixed-image">
            <img src="data:image/png;base64,{img_base64}" width="100">
        </div>
        """, unsafe_allow_html=True
    )


def create_halo(
    config: HaloConfig, session_id: Optional[str] = None, debug_mode: bool = True
) -> Team:
    """Returns an instance of the HALO Agent Interface (HALO)

    Args:
        config: HALO configuration
        session_id: Session identifier
        debug_mode: Enable debug logging
    """
    # Parse model provider and name
    provider, model_name = config.model_id.split(":")

    # Create model class based on provider
    model = None
    if provider == "openai":
        model = OpenAIChat(id=model_name)
    elif provider == "google":
        model = Gemini(id=model_name)
    elif provider == "anthropic":
        model = Claude(id=model_name)
    elif provider == "groq":
        model = Groq(id=model_name)
    else:
        raise ValueError(f"Unsupported model provider: {provider}")
    if model is None:
        raise ValueError(f"Failed to create model instance for {config.model_id}")

    # Default tools that should always be available
    default_tools = []
    
    # Combine default tools with user-selected tools, removing duplicates
    all_tools = list(set((config.tools or []) + default_tools))
    
    tools: List[Toolkit] = [ReasoningTools(add_instructions=True)]
    for tool_name in all_tools:
        tool = get_toolkit(tool_name)
        if tool is not None:
            tools.append(tool)
        else:
            logger.warning(f"Tool {tool_name} not found")

    agents: List[Agent] = []
    if config.agents:
        for agent_name in config.agents:
            agent = get_agent(agent_name, model, halo_memory, halo_knowledge, debug_mode=debug_mode)
            if agent is not None:
                agents.append(agent)
            else:
                logger.warning(f"Agent {agent_name} not found")

    description = dedent("""\
    You are an advanced AI System called `HALO Agent Interface` (HALO).
    You provide a unified interface to a team of AI Agents, that you coordinate to assist the user in the best way possible.

    Keep your responses short and to the point, while maintaining a conversational tone.
    You are able to handle easy conversations as well as complex requests by delegating tasks to the appropriate team members.
    You are also capable of handling errors and edge cases and are able to provide helpful feedback to the user.\
    """)
    instructions: List[str] = [
        "Your goal is to coordinate the team to assist the user in the best way possible.",
        "If the user sends a conversational message like 'Hello', 'Hi', 'How are you', 'What is your name', etc., you should respond in a friendly and engaging manner.",
        "If the user asks for something simple, like updating memory, you can do it directly without Thinking and Analyzing.",
        "If the user says, he loves or likes something or dislikes something, you can update the memory directly without Thinking and Analyzing.",
        "Keep your responses short and to the point, while maintaining a conversational tone.",
        "If the user asks for something complex, **think** and determine if:\n"
        " - You can answer by using a tool available to you\n"
        " - You need to search the knowledge base\n"
        " - You need to search the internet\n"
        " - You need to delegate the task to a team member\n"
        " - You need to ask a clarifying question",
        "You also have to a knowledge base of information provided by the user. If the user asks about a topic that might be in the knowledge base, first ALWAYS search your knowledge base using the `search_knowledge_base` tool.",
        "IMPORTANT: For domain-specific queries, delegate to specialized agents rather than using general search tools:",
        "- For travel planning, Airbnb listings, or accommodation searches, ALWAYS delegate to the Airbnb Agent",
        "- For LinkedIn-related queries or professional networking, delegate to the LinkedIn Agent",
        "- For data analysis tasks, delegate to the Data Analyst agent",
        "- For Python coding tasks, delegate to the Python Agent",
        "- For research tasks, delegate to the Research Agent",
        "Only if no specialized agent is available for the query, fall back to searching the knowledge base and then the internet.",
        "If the users message is unclear, ask clarifying questions to get more information.",
        "Based on the user request and the available team members, decide which member(s) should handle the task.",
        "Coordinate the execution of the task among the selected team members.",
        "Synthesize the results from the team members and provide a final, coherent answer to the user.",
        "Do not use phrases like 'based on my knowledge' or 'depending on the information'.",
    ]

    halo = Team(
        name="HALO Agent Interface",
        model=model,
        user_id=config.user_id,
        session_id=session_id,
        tools=tools,
        members=agents,
        db=halo_sessions,
        knowledge=halo_knowledge,
        description=description,
        instructions=instructions,
        respond_directly=True,  # Team can respond directly without always delegating
        delegate_to_all_members=False,  # Don't automatically delegate to all members
        determine_input_for_members=True,  # Team determines what input each member gets
        #enable_team_history=True,
        read_chat_history=True,
        #num_of_interactions_from_history=3,
        show_members_responses=True,
        enable_user_memories=True,  # This enables memory functionality
        markdown=True,
        debug_mode=debug_mode,
    )

    agent_names = [a.name for a in agents] if agents else []
    logger.info(f"HALO created with members: {agent_names}")
    return halo
