"""
This module provides essential utility functions and classes for the agentic framework,
including AI model configuration, memory management, state handling, and persistence.

Key Features:
    1. Azure OpenAI Integration: Configures and manages chat completion models
    2. Memory Management: Implements short-term and long-term memory capabilities using LangMem
    3. State Management: Defines custom state schemas and message handling for agent workflows
    4. Cosmos DB Checkpointing: Provides persistent conversation storage and resumption
    5. Telemetry and Logging: Integrates Azure Monitor for comprehensive observability
    6. CopilotKit Integration: Enables advanced AI assistant capabilities
    7. Message Processing: Handles message trimming, tokenization, and summarization

Architecture:
The module serves as the backbone for the agentic framework, providing:
- Model Configuration: Azure OpenAI chat completion and embedding models
- State Schema: Custom state management for multi-agent workflows
- Persistence: Cosmos DB-based checkpointing for conversation continuity
- Memory: Integration with LangMem for enhanced memory capabilities
- Monitoring: Azure Application Insights integration for telemetry

Key Classes:
- State: Custom state schema extending CopilotKitState for agent workflows
- SessionAwareLangGraphAgent: Manages agent sessions with persistent storage
- CosmosCheckpointSaver: Implements Cosmos DB-based conversation persistence
- SummarizationNode: Provides message summarization capabilities

Integration:
This module is imported throughout the framework and provides the foundational
services that enable multi-agent conversations, persistence, and monitoring.
"""

from backend.config import chat_completion_model_name, azure_openai_api_key, azure_openai_api_version, azure_openai_endpoint, chat_completion_model_temperature, chat_completion_model_max_tokens, database_name, cosmosdb_endpoint, container_checkpoint_name, container_checkpoint_writes_name, container_conversations_name, cosmosdb_credential, app_insight_connection_string
from langchain_openai import AzureChatOpenAI
from langmem import  create_manage_memory_tool, create_search_memory_tool
from langgraph.store.memory import InMemoryStore
from langchain.embeddings import init_embeddings
from langmem.short_term import SummarizationNode
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.messages.utils import trim_messages, count_tokens_approximately
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.prebuilt.chat_agent_executor import AgentState
from typing import Any, AsyncIterator, Dict, Optional, Sequence, Tuple, List
from opentelemetry._logs import (
    get_logger_provider,
    set_logger_provider,
)
from opentelemetry.sdk._logs import (
    LoggerProvider,
    LoggingHandler,
)
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter
import logging
from copilotkit import CopilotKitState, LangGraphAgent
from pydantic import BaseModel
from azure.cosmos.aio import CosmosClient, DatabaseProxy
from langchain_core.runnables import RunnableConfig
from azure.identity import DefaultAzureCredential
from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id
)
import base64
from datetime import datetime
import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor

chat_completion_model = AzureChatOpenAI(
    model=chat_completion_model_name, 
    api_key=azure_openai_api_key, 
    api_version=azure_openai_api_version, 
    azure_endpoint=azure_openai_endpoint,
    temperature=chat_completion_model_temperature,
    max_tokens=chat_completion_model_max_tokens
)

# Define a pre_model_hook function or runnable that takes graph state and returns an updated state that contains the message history
def pre_model_hook(state):
    trimmed_messages = trim_messages(
        state["messages"],
        strategy="last",
        token_counter=count_tokens_approximately,
        max_tokens=2048,  
        start_on="human",
        end_on=("human", "tool"),
    )
    return {"llm_input_messages": trimmed_messages}


# Define the summarization node for condensing earlier messages in the history. 
# It use a different strategy from the pre_model_hook for managing message history. Maintains context while reducing token count
# Once the message history reaches the token limit, the summarization node will summarize earlier messages to make sure they fit into max_tokens.
summarization_node = SummarizationNode( 
    token_counter=count_tokens_approximately,
    model=chat_completion_model,
    max_tokens=4000,  # Increased for better context
    max_summary_tokens=512,  # Increased summary size
    output_messages_key="llm_input_messages",
)

class State(CopilotKitState):
    # NOTE: we're adding this key to keep track of previous summary information
    # to make sure we're not summarizing on every LLM call
    context: dict[str, Any]
    remaining_steps: int

# Logging
logger_provider = LoggerProvider()
set_logger_provider(logger_provider)
exporter = AzureMonitorLogExporter.from_connection_string(app_insight_connection_string)
get_logger_provider().add_log_record_processor(BatchLogRecordProcessor(exporter, schedule_delay_millis=60000))

# Attach LoggingHandler to namespaced logger
handler = LoggingHandler()
logger = logging.getLogger()
logger.addHandler(handler)
logger.setLevel(logging.INFO)


class AsyncCosmosDBCheckpointSaverConfig(BaseModel):

    DATABASE: str
    ENDPOINT: str
    CONVERSATIONS_CONTAINER: str
    CHECKPOINTS_CONTAINER: str
    CHECKPOINT_WRITES_CONTAINER: str

def serialize_for_cosmosdb(obj: Any) -> Any:
    """
    Recursively serialize objects for CosmosDB storage.
    Handles LangChain messages and other complex objects that can't be directly stored in CosmosDB.
    """
    if hasattr(obj, '__dict__'):
        # If it's a complex object (like LangChain messages), convert to dict
        if hasattr(obj, 'content') and hasattr(obj, 'type'):
            # LangChain message object
            return {
                "_type": obj.__class__.__name__,
                "content": obj.content,
                "type": obj.type,
                "additional_kwargs": getattr(obj, 'additional_kwargs', {}),
                "response_metadata": getattr(obj, 'response_metadata', {}),
                "id": getattr(obj, 'id', None)
            }
        else:
            # General object serialization
            result = {"_type": obj.__class__.__name__}
            result.update({k: serialize_for_cosmosdb(v)
                          for k, v in obj.__dict__.items()})
            return result
    elif isinstance(obj, dict):
        return {k: serialize_for_cosmosdb(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [serialize_for_cosmosdb(item) for item in obj]
    elif isinstance(obj, (str, int, float, bool, type(None))):
        return obj
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        # For any other type, try to convert to string as a fallback
        try:
            return str(obj)
        except Exception:
            return f"<unserializable: {type(obj).__name__}>"
        
def deserialize_from_cosmosdb(obj: Any) -> Any:
    """
    Recursively deserialize objects from CosmosDB storage.
    Reconstructs LangChain messages and other complex objects from serialized format.
    """
    if isinstance(obj, dict) and "_type" in obj:
        obj_type = obj["_type"]
        if obj_type in ["HumanMessage", "AIMessage", "SystemMessage"]:
            # Reconstruct LangChain message
            message_classes = {
                "HumanMessage": HumanMessage,
                "AIMessage": AIMessage,
                "SystemMessage": SystemMessage
            }
            message_class = message_classes.get(obj_type, HumanMessage)
            return message_class(
                content=obj.get("content", ""),
                additional_kwargs=obj.get("additional_kwargs", {}),
                response_metadata=obj.get("response_metadata", {}),
                id=obj.get("id")
            )
        else:
            # General object reconstruction (return as dict for now)
            result = {k: deserialize_from_cosmosdb(
                v) for k, v in obj.items() if k != "_type"}
            return result
    elif isinstance(obj, dict):
        return {k: deserialize_from_cosmosdb(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [deserialize_from_cosmosdb(item) for item in obj]
    elif isinstance(obj, str):
        # Try to parse ISO datetime strings
        if len(obj) > 10 and 'T' in obj and (obj.endswith('Z') or '+' in obj[-6:]):
            try:
                return datetime.fromisoformat(obj.replace('Z', '+00:00'))
            except ValueError:
                pass
        return obj
    else:
        return obj

class AsyncCosmosDBCheckpointSaver(BaseCheckpointSaver):
    """A checkpoint saver that stores checkpoints in a CosmosDB database."""

    client: CosmosClient
    db: DatabaseProxy

    def __init__(self, credential: DefaultAzureCredential, config: AsyncCosmosDBCheckpointSaverConfig) -> None:
        super().__init__()

        self.config = config

        # Initialize Cosmos DB client
        self.client = CosmosClient(url=config.ENDPOINT, credential=credential)
        self.db = self.client.get_database_client(config.DATABASE)

        # Get containers: conversations, checkpoints and checkpoint_writes
        self.conversations_container = self.db.get_container_client(
            config.CONVERSATIONS_CONTAINER
        )
        self.checkpoints_container = self.db.get_container_client(
            config.CHECKPOINTS_CONTAINER
        )
        self.writes_container = self.db.get_container_client(
            config.CHECKPOINT_WRITES_CONTAINER
        )

    async def ensure_indexes(self):
        """Ensure database and containers exist in CosmosDB."""
        try:
            # Create database if it doesn't exist
            await self.client.create_database_if_not_exists(
                id=self.config.DATABASE
            )

            # For CosmosDB emulator, we need to use proper partition key specification
            from azure.cosmos import PartitionKey

            # Create containers if they don't exist
            await self.db.create_container_if_not_exists(
                id=self.config.CONVERSATIONS_CONTAINER,
                partition_key=PartitionKey(path="/userId")
            )

            await self.db.create_container_if_not_exists(
                id=self.config.CHECKPOINTS_CONTAINER,
                partition_key=PartitionKey(path="/thread_id")
            )

            await self.db.create_container_if_not_exists(
                id=self.config.CHECKPOINT_WRITES_CONTAINER,
                partition_key=PartitionKey(path="/thread_id")
            )

            logger.info(
                f"Database '{self.config.DATABASE}' and containers created/verified successfully")

        except Exception as e:
            logger.error(f"Error creating database/containers: {e}")
            raise

    async def close(self):
        """Close the CosmosDB client."""
        await self.client.close()

    def dumps_typed(self, obj: Any) -> Tuple[str, str]:
        """
        Serializes an object and encodes the serialized data in base64 format.
        Args:
            obj (Any): The object to be serialized.
        Returns:
            Tuple[str, str]: A tuple containing the type of the object as a string and the base64 encoded serialized data.
        """
        try:
            type_, serialized_ = self.serde.dumps_typed(obj)
            return type_, base64.b64encode(serialized_).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to serialize object: {e}")

    def loads_typed(self, data: Tuple[str, str]) -> Any:
        """
        Deserialize a tuple containing a string and a base64 encoded string.
        Args:
            data (Tuple[str, str]): A tuple where the first element is a string and the second element is a base64 encoded string.
        Returns:
            Any: The deserialized object.
        """
        try:
            return self.serde.loads_typed(
                (data[0], base64.b64decode(data[1].encode("utf-8")))
            )
        except Exception as e:
            raise ValueError(f"Failed to deserialize data: {e}")

    def dumps(self, obj: Any) -> str:
        """
        Serializes an object to a base64-encoded string.
        Args:
            obj (Any): The object to serialize.
        Returns:
            str: The base64-encoded string representation of the serialized object.
        """
        try:
            return base64.b64encode(self.serde.dumps(obj)).decode("utf-8")
        except Exception as e:
            raise ValueError(f"Failed to serialize object: {e}")

    def loads(self, data: str) -> Any:
        """
        Deserialize a base64 encoded string into a Python object.
        Args:
            data (str): The base64 encoded string to be deserialized.
        Returns:
            Any: The deserialized Python object.
        """
        try:
            return self.serde.loads(base64.b64decode(data.encode("utf-8")))
        except Exception as e:
            raise ValueError(f"Failed to deserialize data: {e}")

    async def aget_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple from the database.

        This method retrieves a checkpoint tuple from the CosmosDB database based on the
        provided config. If the config contains a "checkpoint_id" key, the checkpoint with
        the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
        for the given thread ID is retrieved.

        Args:
            config (RunnableConfig): The config to use for retrieving the checkpoint.

        Returns:
            Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """
        try:
            assert "configurable" in config
            thread_id = config["configurable"]["thread_id"]
            checkpoint_ns = config["configurable"].get("checkpoint_ns", "")
            
            if checkpoint_id := get_checkpoint_id(config):
                query = "SELECT * FROM c WHERE c.thread_id = @thread_id AND c.checkpoint_ns = @checkpoint_ns AND c.checkpoint_id = @checkpoint_id"
                parameters = [
                    {"name": "@thread_id", "value": thread_id},
                    {"name": "@checkpoint_ns", "value": checkpoint_ns},
                    {"name": "@checkpoint_id", "value": checkpoint_id}
                ]
            else:
                query = "SELECT * FROM c WHERE c.thread_id = @thread_id AND c.checkpoint_ns = @checkpoint_ns ORDER BY c.checkpoint_id DESC"
                parameters = [
                    {"name": "@thread_id", "value": thread_id},
                    {"name": "@checkpoint_ns", "value": checkpoint_ns}
                ]

            result = [item async for item in self.checkpoints_container.query_items(
                query=query,
                parameters=parameters
            )]
            
            if result:
                doc = result[0]
                config_values = {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": doc["checkpoint_id"],
                }
                checkpoint = self.loads_typed((doc["type"], doc["checkpoint"]))
                
                writes_query = "SELECT * FROM c WHERE c.thread_id = @thread_id AND c.checkpoint_ns = @checkpoint_ns AND c.checkpoint_id = @checkpoint_id"
                writes_parameters = [
                    {"name": "@thread_id", "value": thread_id},
                    {"name": "@checkpoint_ns", "value": checkpoint_ns},
                    {"name": "@checkpoint_id", "value": doc['checkpoint_id']}
                ]
                
                _serialized_writes = self.writes_container.query_items(
                    query=writes_query,
                    parameters=writes_parameters
                )
                serialized_writes = [writes async for writes in _serialized_writes]

                pending_writes = [
                    (
                        write_doc["task_id"],
                        write_doc["channel"],
                        self.loads_typed((write_doc["type"], write_doc["value"])),
                    )
                    for write_doc in serialized_writes
                ]
                return CheckpointTuple(
                    {"configurable": config_values},
                    checkpoint,
                    self.loads(doc["metadata"]),
                    (
                        {
                            "configurable": {
                                "thread_id": thread_id,
                                "checkpoint_ns": checkpoint_ns,
                                "checkpoint_id": doc["parent_checkpoint_id"],
                            }
                        }
                        if doc.get("parent_checkpoint_id")
                        else None
                    ),
                    pending_writes,
                )
        except Exception as e:
            # Log error and return None instead of raising
            print(f"Error retrieving checkpoint: {e}")
            return None

    async def alist(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        """List checkpoints from the database.

        This method retrieves a list of checkpoint tuples from the CosmosDB database based
        on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).

        Args:
            config (RunnableConfig): The config to use for listing the checkpoints.
            filter (Optional[Dict[str, Any]]): Additional filtering criteria for metadata. Defaults to None.
            before (Optional[RunnableConfig]): If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None.
            limit (Optional[int]): The maximum number of checkpoints to return. Defaults to None.

        Yields:
            Iterator[CheckpointTuple]: An iterator of checkpoint tuples.
        """
        try:
            if config is None:
                raise ValueError("Config is required")
            
            if "configurable" not in config:
                raise ValueError("Config.configurable is required")

            query_parts = ["SELECT * FROM c WHERE c.thread_id = @thread_id AND c.checkpoint_ns = @checkpoint_ns"]    
            parameters = [
                {"name": "@thread_id", "value": config['configurable']['thread_id']},
                {"name": "@checkpoint_ns", "value": config['configurable'].get('checkpoint_ns', '')}
            ]


            if filter:
                for i, (key, value) in enumerate(filter.items()):
                    param_name = f"@filter_value_{i}"
                    query_parts.append(f" AND c.metadata.{key} = {param_name}")
                    parameters.append({"name": param_name, "value": value})

            if before is not None:
                assert "configurable" in before
                query_parts.append(" AND c.checkpoint_id < @before_checkpoint_id")
                parameters.append({"name": "@before_checkpoint_id", "value": before['configurable']['checkpoint_id']})

            query_parts.append(" ORDER BY c.checkpoint_id DESC")

            if limit is not None:
                query_parts.append(f" OFFSET 0 LIMIT {int(limit)}")

            query = "".join(query_parts)

            result = self.checkpoints_container.query_items(
                query=query,
                parameters=parameters
            )

            async for doc in result:
                try:
                    checkpoint = self.loads_typed((doc["type"], doc["checkpoint"]))
                    yield CheckpointTuple(
                        {
                            "configurable": {
                                "thread_id": doc["thread_id"],
                                "checkpoint_ns": doc["checkpoint_ns"],
                                "checkpoint_id": doc["checkpoint_id"],
                            }
                        },
                        checkpoint,
                        self.loads(doc["metadata"]),
                        (
                            {
                                "configurable": {
                                    "thread_id": doc["thread_id"],
                                    "checkpoint_ns": doc["checkpoint_ns"],
                                    "checkpoint_id": doc["parent_checkpoint_id"],
                                }
                            }
                            if doc.get("parent_checkpoint_id")
                            else None
                        ),
                    )
                except Exception as e:
                    # Skip corrupted checkpoints and continue
                    print(f"Error processing checkpoint {doc.get('checkpoint_id', 'unknown')}: {e}")
                    continue
        except Exception as e:
            print(f"Error listing checkpoints: {e}")
            return

    async def aput(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Save a checkpoint to the database.

        This method saves a checkpoint to the CosmosDB database. The checkpoint is associated
        with the provided config and its parent config (if any).

        Args:
            config (RunnableConfig): The config to associate with the checkpoint.
            checkpoint (Checkpoint): The checkpoint to save.
            metadata (CheckpointMetadata): Additional metadata to save with the checkpoint.
            new_versions (ChannelVersions): New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint.
        """
        try:
            assert "configurable" in config
            thread_id = config["configurable"]["thread_id"]
            checkpoint_ns = config["configurable"]["checkpoint_ns"]
            checkpoint_id = checkpoint["id"]
            type_, serialized_checkpoint = self.dumps_typed(checkpoint)
            doc = {
                "id": f"{thread_id}_{checkpoint_ns}_{checkpoint_id}",
                "parent_checkpoint_id": config["configurable"].get("checkpoint_id"),
                "type": type_,
                "checkpoint": serialized_checkpoint,
                "metadata": self.dumps(metadata),
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint_id,
            }
            await self.checkpoints_container.upsert_item(doc)

            # Also update/create conversation document for our conversation management
            await self._update_conversation_document(config, checkpoint, metadata)

            return {
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint_id,
                }
            }
        except Exception as e:
            raise RuntimeError(f"Failed to save checkpoint: {e}")

    async def aput_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Store intermediate writes linked to a checkpoint.

        This method saves intermediate writes associated with a checkpoint to the CosmosDB database.

        Args:
            config (RunnableConfig): Configuration of the related checkpoint.
            writes (Sequence[Tuple[str, Any]]): List of writes to store, each as (channel, value) pair.
            task_id (str): Identifier for the task creating the writes.
        """
        try:
            assert "configurable" in config
            thread_id = config["configurable"]["thread_id"]
            checkpoint_ns = config["configurable"]["checkpoint_ns"]
            checkpoint_id = config["configurable"]["checkpoint_id"]
            for idx, (channel, value) in enumerate(writes):
                try:
                    type_, serialized_value = self.dumps_typed(value)
                    doc = {
                        "id": f"{thread_id}_{checkpoint_ns}_{checkpoint_id}_{task_id}_{idx}",
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": checkpoint_id,
                        "task_id": task_id,
                        "idx": idx,
                        "channel": channel,
                        "type": type_,
                        "value": serialized_value,
                    }
                    await self.writes_container.upsert_item(doc)
                except Exception as e:
                    # Log error for individual write but continue with others
                    print(f"Error storing write {idx} for task {task_id}: {e}")
                    continue
        except Exception as e:
            raise RuntimeError(f"Failed to store writes: {e}")
        
    # Conversation management methods
    async def _update_conversation_document(self, config: RunnableConfig, checkpoint: Checkpoint, metadata: CheckpointMetadata):
        """Update the conversation document for conversation management."""
        thread_id = config["configurable"]["thread_id"]

        # Extract user_id from the LangGraph config (passed when creating the conversation)
        user_id = config["configurable"].get("user_id")

        if not user_id:
            logger.warning(
                f"No user_id found in config for thread_id: {thread_id}")
            return  # Skip if we can't extract user_id

        logger.info(
            f"Updating conversation document for user_id: {user_id}, thread_id: {thread_id}")

        # Get messages from checkpoint
        messages = []
        if 'channel_values' in checkpoint and 'messages' in checkpoint['channel_values']:
            messages = checkpoint['channel_values']['messages']

        # Serialize messages for CosmosDB storage
        serialized_messages = serialize_for_cosmosdb(messages)

        now = datetime.utcnow()

        # Create or update conversation document
        conversation_doc = {
            "id": thread_id,
            "userId": user_id,
            "lastUpdated": now.isoformat(),
            "messages": serialized_messages,
            "checkpointId": checkpoint["id"],
            "metadata": serialize_for_cosmosdb(metadata)
        }

        try:
            # In CosmosDB, the partition key value is automatically extracted from the document
            await self.conversations_container.upsert_item(body=conversation_doc)
            logger.info(
                f"Successfully saved conversation document for user_id: {user_id}")
        except Exception as e:
            logger.error(f"Error saving conversation document: {e}")
            raise

    async def get_conversations_by_user(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversations for a specific user."""
        query = f"SELECT * FROM c WHERE c.userId = @user_id ORDER BY c.lastUpdated DESC OFFSET 0"
        if limit is not None:
            query += f" LIMIT {limit}"
        parameters = [
            {"name": "@user_id", "value": user_id}
        ]
        results = []

        async for doc in self.conversations_container.query_items(query=query, parameters=parameters):
            # Calculate message count
            messages = doc.get("messages", [])
            message_count = len(messages) if isinstance(messages, list) else 0

            # Get first message preview
            first_message_preview = None
            if messages and isinstance(messages, list) and len(messages) > 0:
                first_msg = messages[0]
                if isinstance(first_msg, dict):
                    content = first_msg.get("content", "")
                    first_message_preview = {
                        "role": first_msg.get("type", ""),
                        "content": content[:100] + "..." if len(content) > 100 else content,
                        "timestamp": doc.get("lastUpdated", "")
                    }

            results.append({
                "thread_id": doc["id"],
                "user_id": doc["userId"],
                "last_updated": datetime.fromisoformat(doc["lastUpdated"]) if isinstance(doc["lastUpdated"], str) else doc["lastUpdated"],
                "message_count": message_count,
                "first_message_preview": first_message_preview
            })

        return results

    async def get_or_create_user_conversation(self, user_id: str) -> str:
        """Get the user's single conversation thread_id, or create one if it doesn't exist."""
        # Check if user already has a conversation
        query = f"SELECT * FROM c WHERE c.userId = @user_id ORDER BY c.lastUpdated DESC OFFSET 0 LIMIT 1"
        parameters = [{"name": "@user_id", "value": user_id}]
        results = [doc async for doc in self.conversations_container.query_items(query=query, parameters=parameters)]

        if results:
            return results[0]["id"]

        # Create a new GUID-format thread_id for this user
        thread_id = str(uuid.uuid4())
        return thread_id

    async def cleanup_old_conversations(self, user_id: str):
        """Clean up any extra conversations for a user, keeping only the most recent one."""
        query = f"SELECT * FROM c WHERE c.userId = @user_id ORDER BY c.lastUpdated DESC"
        parameters = [{"name": "@user_id", "value": user_id}]
        conversations = [doc async for doc in self.conversations_container.query_items(query=query, parameters=parameters)]

        if len(conversations) <= 1:
            return  # Nothing to clean up

        # Keep the most recent conversation, delete the rest
        delete_conversations = conversations[1:]

        for conv in delete_conversations:
            await self.conversations_container.delete_item(item=conv["id"], partition_key=conv["userId"])

    async def delete_conversation(self, thread_id: str) -> bool:
        """Delete a conversation and all its associated checkpoints."""
        try:
            # First, get the conversation to find the userId (needed for partition key)
            query = f"SELECT * FROM c WHERE c.id = @thread_id"
            parameters = [{"name": "@thread_id", "value": thread_id}]
            conversations = [doc async for doc in self.conversations_container.query_items(query=query, parameters=parameters)]

            if conversations:
                conv = conversations[0]
                # Delete conversation document (partition key is userId)
                await self.conversations_container.delete_item(item=thread_id, partition_key=conv["userId"])

            # Delete associated checkpoints (partition key is thread_id)
            query = f"SELECT * FROM c WHERE c.thread_id = @thread_id"
            parameters = [{"name": "@thread_id", "value": thread_id}]
            checkpoints = [doc async for doc in self.checkpoints_container.query_items(query=query, parameters=parameters)]

            for checkpoint in checkpoints:
                await self.checkpoints_container.delete_item(item=checkpoint["id"], partition_key=checkpoint["thread_id"])

            # Delete associated checkpoint writes (partition key is thread_id)
            writes = [doc async for doc in self.writes_container.query_items(query)]
            for write in writes:
                await self.writes_container.delete_item(item=write["id"], partition_key=write["thread_id"])

            return True
        except Exception as e:
            logger.error(f"Error deleting conversation {thread_id}: {e}")
            return False

    async def get_total_conversations(self) -> int:
        """Get the total number of conversations in the database."""
        try:
            query = "SELECT VALUE COUNT(1) FROM c"
            result = [item async for item in self.conversations_container.query_items(query)]
            return result[0] if result else 0
        except Exception as e:
            logger.error(f"Error getting total conversations count: {e}")
            return 0

    async def get_all_unique_user_ids(self) -> List[str]:
        """Get all unique user IDs from the conversations."""
        try:
            query = "SELECT DISTINCT VALUE c.userId FROM c"
            user_ids = [item async for item in self.conversations_container.query_items(query)]
            return sorted(user_ids)
        except Exception as e:
            logger.error(f"Error getting unique user IDs: {e}")
            return []

    async def get_all_unique_thread_ids(self) -> List[str]:
        """Get all unique thread IDs from the conversations."""
        try:
            query = "SELECT DISTINCT VALUE c.id FROM c"
            thread_ids = [item async for item in self.conversations_container.query_items(query)]
            return sorted(thread_ids)
        except Exception as e:
            logger.error(f"Error getting unique thread IDs: {e}")
            return []


checkpoint_store_config = AsyncCosmosDBCheckpointSaverConfig(
        DATABASE=database_name,
        ENDPOINT=cosmosdb_endpoint,
        CONVERSATIONS_CONTAINER=container_conversations_name,
        CHECKPOINTS_CONTAINER=container_checkpoint_name,
        CHECKPOINT_WRITES_CONTAINER=container_checkpoint_writes_name,
    )

# Correct instantiation of AsyncCosmosDBCheckpointSaver
checkpointer = AsyncCosmosDBCheckpointSaver(
    credential=cosmosdb_credential,  # Ensure this is an instance of DefaultAzureCredential
    config=checkpoint_store_config  # Ensure this is an instance of AsyncCosmosDBCheckpointSaverConfig
)

class SessionAwareLangGraphAgent(LangGraphAgent):
    """
    LangGraph agent that automatically handles session restoration based on recent activity.

    If a user has a conversation within the last 3 hours, it restores that session.
    Otherwise, it creates a new conversation thread.
    """

    def __init__(self, checkpointer: AsyncCosmosDBCheckpointSaver, hours_threshold: int = 3, **kwargs):
        """
        Initialize the session-aware agent.

        Args:
            checkpointer: MongoDB checkpointer instance
            hours_threshold: Hours to look back for recent conversations (default: 3)
            **kwargs: Other arguments passed to LangGraphAgent
        """
        super().__init__(**kwargs)
        self.checkpointer = checkpointer
        self.hours_threshold = hours_threshold

    async def _ensure_thread_id(self, config: RunnableConfig) -> RunnableConfig:
        """
        Ensure a thread_id exists in config.
        New strategy: Each user has exactly one persistent conversation.
        """
        try:
            configurable = config.get("configurable", {})

            # Try to get user_id from different possible locations
            user_id = configurable.get("user_id")

            # If no user_id provided, create a new thread (anonymous session)
            if not user_id:
                try:
                    new_thread_id = str(uuid.uuid4())
                    config["configurable"] = {
                        **configurable, "thread_id": new_thread_id}
                    return config
                except Exception as e:
                    logger.error(f"Error creating anonymous thread ID: {str(e)}")
                    raise
            
            try:
                # Get or create the user's single conversation
                thread_id = await self.checkpointer.get_or_create_user_conversation(user_id)
            except Exception as e:
                logger.error(f"Error getting/creating user conversation for user {user_id}: {str(e)}")
                raise

            try:
                # Clean up any duplicate conversations for this user (maintenance)
                await self.checkpointer.cleanup_old_conversations(user_id)
            except Exception as e:
                logger.error(f"Error cleaning up conversation for user {user_id}: {str(e)}")
                raise

            config["configurable"] = {
                **configurable,
                "thread_id": thread_id,
                "user_id": user_id
            }

            return config
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise

    async def ainvoke(self, input_data: Dict[str, Any], config: Optional[RunnableConfig] = {}, **kwargs) -> Any:
        """
        Async invoke with automatic session management.
        """

        # Ensure thread_id exists (restore recent or create new)
        config = await self._ensure_thread_id(config)

        # Call the parent's ainvoke method
        return await super().ainvoke(input_data, config, **kwargs)

    def invoke(self, input_data: Dict[str, Any], config: Optional[RunnableConfig] = {}, **kwargs) -> Any:
        """
        Sync invoke with automatic session management.
        """

        # Handle async session management in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Run in a separate thread to avoid the running loop
                with ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._ensure_thread_id(config))
                    config = future.result()
            else:
                config = loop.run_until_complete(self._ensure_thread_id(config))
        except RuntimeError:
            # If no event loop is running, create a new one
            config = asyncio.run(self._ensure_thread_id(config))

        # Call the parent's invoke method
        return super().invoke(input_data, config, **kwargs)

    async def astream(self, input_data: Dict[str, Any], config: Optional[RunnableConfig] = {}, **kwargs):
        """
        Async stream with automatic session management.
        """

        # Ensure thread_id exists (restore recent or create new)
        config = await self._ensure_thread_id(config)

        # Call the parent's astream method
        async for chunk in super().astream(input_data, config, **kwargs):
            yield chunk

    def stream(self, input_data: Dict[str, Any], config: Optional[RunnableConfig] = {}, **kwargs):
        """
        Sync stream with automatic session management.
        """

        # Handle async session management in sync context
        try:
            loop = asyncio.get_event_loop()
            config = loop.run_until_complete(self._ensure_thread_id(config))
        except RuntimeError:
            # If no event loop is running, create a new one
            config = asyncio.run(self._ensure_thread_id(config))

        # Call the parent's stream method
        for chunk in super().stream(input_data, config, **kwargs):
            yield chunk