from __future__ import annotations

from typing import Any, Dict, List
import importlib


def run_chat(provider: Any, mapping: Any, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Provider adapter for purpose='chat' driven entirely by DB configuration.

    - Imports provider.module, resolves provider.class
    - Instantiates with merged kwargs: provider.config_json + model + mapping.parameters_json
    - Calls provider.method (default 'invoke') with LangChain-formatted messages
    """
    cfg: Dict[str, Any] = provider.config_json or {}
    model_name: str = mapping.model_name
    params: Dict[str, Any] = mapping.parameters_json or {}

    module_name: str = getattr(provider, 'module', '') or ''
    class_name: str = getattr(provider, 'cls', '') or ''
    method_name: str = (getattr(provider, 'method', None) or 'invoke')

    if not module_name or not class_name:
        # Fallback: echo last user
        last_user = next((m for m in reversed(messages) if m.get('role') == 'user'), None)
        text = (last_user or {}).get('content', '')
        if isinstance(text, dict):
            text = text.get('text', str(text))
        return { 'type': 'text', 'text': f"Provider not configured (module/class missing). Echo: {text}" }

    # Build kwargs: provider creds/connection + model + mapping params (mapping overrides)
    kwargs: Dict[str, Any] = {}
    kwargs.update(cfg or {})
    # Standardize model kw for LangChain chat clients
    kwargs['model'] = model_name
    kwargs.update(params or {})

    try:
        module = importlib.import_module(module_name)
        client_cls = getattr(module, class_name)
    except Exception as exc:  # noqa: BLE001
        return { 'type': 'text', 'text': f'Provider import error: {exc}' }

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
        client = client_cls(**kwargs)
        method = getattr(client, method_name, None)
        if not callable(method):
            return { 'type': 'text', 'text': f"Provider method '{method_name}' not found on {class_name}" }
        resp = method(lc_messages)
        text = getattr(resp, 'content', '') if hasattr(resp, 'content') else (resp or '')
        if isinstance(text, dict):
            # Normalize to text response
            text = text.get('text', str(text))
        return { 'type': 'text', 'text': text or '' }
    except Exception as exc:  # noqa: BLE001
        return { 'type': 'text', 'text': f'Provider error: {exc}' }


def _openai_langchain(*args: Any, **kwargs: Any) -> Dict[str, Any]:
    # Kept only to avoid import-time errors if referenced elsewhere; not used now.
    return { 'type': 'text', 'text': 'Deprecated path' }


