from __future__ import annotations

import importlib

from typing import Any, Dict, List, Optional, AsyncGenerator

from langchain.tools import StructuredTool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.prebuilt import create_react_agent
from pydantic import BaseModel, Field



from .llm_message_utils import iter_messages, LCAIMessage, LCToolMessage
from ..services.chat.streaming_interface import StreamingChunk

# Get logger for this module
