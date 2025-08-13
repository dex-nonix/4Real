from __future__ import annotations

from typing import Any, Dict, List

from langchain_openai import ChatOpenAI


def run_chat(provider: Any, mapping: Any, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Provider adapter for purpose='chat' with runtime-only (DB) configuration.

    All credentials, base URLs, and parameters come from provider.config_json and mapping.
    Nothing is read from environment variables; no hardcoded defaults.
    """
    ptype = (provider.provider_type or '').lower()
    cfg = provider.config_json or {}
    model = mapping.model_name
    params = mapping.parameters_json or {}

    if ptype == 'openai':
        return _openai_langchain(cfg, model, params, messages)

    # Default fallback: echo last user
    last_user = next((m for m in reversed(messages) if m.get('role') == 'user'), None)
    text = (last_user or {}).get('content', '')
    if isinstance(text, dict):
        text = text.get('text', str(text))
    return { 'type': 'text', 'text': f"Echo: {text}" }


def _openai_langchain(cfg: Dict[str, Any], model: str, params: Dict[str, Any], messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    api_key = cfg.get('api_key')
    base_url = cfg.get('base_url')
    if not api_key:
        return { 'type': 'text', 'text': 'OpenAI API key missing in provider.config_json' }

    # Instantiate LC client strictly from DB config
    client = ChatOpenAI(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=params.get('temperature'),
    )

    # Convert to LC messages (simple text only)
    from langchain.schema import HumanMessage, SystemMessage, AIMessage
    lc_messages = []
    for m in messages:
        role = m.get('role')
        content = m.get('content')
        if isinstance(content, dict):
            content = content.get('text', str(content))
        if role == 'system':
            lc_messages.append(SystemMessage(content=content))
        elif role == 'assistant':
            lc_messages.append(AIMessage(content=content))
        else:
            lc_messages.append(HumanMessage(content=content))

    try:
        resp = client.invoke(lc_messages)
        text = getattr(resp, 'content', '')
        return { 'type': 'text', 'text': text or '' }
    except Exception as exc:  # noqa: BLE001
        return { 'type': 'text', 'text': f'OpenAI error: {exc}' }


