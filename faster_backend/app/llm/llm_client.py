"""Stub implementation of llm_client for faster_backend."""


async def run_chat_streaming(provider, mapping_obj, chat_history, available_tools_info, persona_id):
    """Stub implementation - yields error message for now."""
    yield {
        "chunk_type": "complete",
        "content": "LLM functionality not implemented in faster_backend",
        "metadata": {}
    }
