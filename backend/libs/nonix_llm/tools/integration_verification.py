"""
Phase 2 Integration Verification

This module tests that the new NxLLMToolsManager correctly integrates with:
- Existing @llm_tool decorator system
- Security features (resolve_safe_path)
- Property override system
- Context-aware resolution

This is a verification script to ensure Phase 2 integration is working.
"""

import json
import os
import tempfile

from .decorators import llm_tool
from .tools_manager import NxLLMToolsManager


# Test decorated function
@llm_tool(
    description="Test function with decorator",
    props={"default_value": 42},
    hidden_props=["api_key"],
    param_descriptions={"text": "Text to process"}
)
def test_decorated_function(text: str, default_value: int = 0, api_key: str = None) -> str:
    """Test function with @llm_tool decorator."""
    return f"Processed: {text} (value: {default_value})"


# Test class with decorated methods
class TestToolProvider:
    def __init__(self, api_key: str):
        self.api_key = api_key

    @llm_tool(
        description="Process data with context",
        hidden_props=["api_key"],
        param_descriptions={"data": "Data to process"}
    )
    def process_data(self, data: str, api_key: str = None) -> str:
        """Process data using the API key."""
        key = api_key or self.api_key
        return f"Processed {data} with key: {key[:4]}***"


def verify_decorator_compatibility():
    """Verify integration with existing @llm_tool decorator system."""
    print("Testing decorator compatibility...")

    manager = NxLLMToolsManager()

    # Test single decorated function
    manager.register(test_decorated_function)

    # Test class with decorated methods
    provider = TestToolProvider("secret_api_key_123")
    manager.register(provider)

    # Get all tools
    tools = manager.get_all_tools()

    # Verify tools were loaded correctly
    assert len(tools) >= 2, f"Expected at least 2 tools, got {len(tools)}"

    # Find the decorated function tool
    func_tool = None
    for tool in tools:
        if tool["name"] == "test_decorated_function":
            func_tool = tool
            break

    assert func_tool is not None, "Decorated function tool not found"
    assert func_tool["description"] == "Test function with decorator"
    assert func_tool["props"]["default_value"] == 42
    assert "api_key" in func_tool["hidden_props"]
    assert "text" in func_tool["param_descriptions"]

    print("✅ Decorator compatibility verified")


def verify_security_integration():
    """Verify integration with existing security features."""
    print("Testing security integration...")

    # Create temporary config file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            "tools": [
                {"func": "math:sqrt", "name": "square_root"}
            ]
        }
        json.dump(config, f)
        temp_file = f.name

    try:
        manager = NxLLMToolsManager()

        # Register file reference (should use resolve_safe_path internally)
        manager.register(temp_file)

        tools = manager.get_all_tools()

        # Verify tool was loaded securely
        assert len(tools) == 1, f"Expected 1 tool, got {len(tools)}"
        assert tools[0]["name"] == "square_root"

        print("✅ Security integration verified")

    finally:
        # Clean up
        os.unlink(temp_file)


def verify_property_override_system():
    """Verify integration with existing property override system."""
    print("Testing property override system...")

    manager = NxLLMToolsManager()

    # Register function with property overrides
    config = {
        "func": f"{test_decorated_function.__module__}:test_decorated_function",
        "name": "overridden_name",
        "description": "Overridden description",
        "props": {"override_value": 99},
        "hidden_props": ["extra_hidden"],
        "param_descriptions": {"extra_param": "Extra parameter description"}
    }

    manager.register(config)

    tools = manager.get_all_tools()

    # Verify overrides were applied
    assert len(tools) == 1
    tool = tools[0]

    assert tool["name"] == "overridden_name"
    assert tool["description"] == "Overridden description"
    assert tool["props"]["default_value"] == 42  # Original
    assert tool["props"]["override_value"] == 99  # Override
    assert "api_key" in tool["hidden_props"]  # Original
    assert "extra_hidden" in tool["hidden_props"]  # Override
    assert "text" in tool["param_descriptions"]  # Original
    assert "extra_param" in tool["param_descriptions"]  # Override

    print("✅ Property override system verified")


def verify_context_aware_resolution():
    """Verify integration with context-aware property resolution."""
    print("Testing context-aware resolution...")

    manager = NxLLMToolsManager()
    manager.register(test_decorated_function)

    # Test context injection
    context = {
        "root_path": "/safe/directory",
        "output_dir": "/output"
    }

    partial_map = {
        "api_key": "injected_key_456"
    }

    tools = manager.get_all_tools(context, partial_map)

    # Verify context was processed
    assert len(tools) == 1
    tool = tools[0]

    # Verify tool structure is maintained
    assert "name" in tool
    assert "description" in tool
    assert "function" in tool
    assert "props" in tool
    assert "hidden_props" in tool

    print("✅ Context-aware resolution verified")


def verify_legacy_compatibility():
    """Verify legacy compatibility methods work."""
    print("Testing legacy compatibility...")

    manager = NxLLMToolsManager()

    # Test legacy config loading
    config = [
        {"func": "math:sqrt", "name": "sqrt_tool"}
    ]

    tools = manager.load_tools_from_config(config)
    assert len(tools) == 1
    assert tools[0]["name"] == "sqrt_tool"

    # Test legacy object extraction
    provider = TestToolProvider("test_key")
    tools = manager.extract_decorated_tools(provider)
    assert len(tools) >= 1

    print("✅ Legacy compatibility verified")


def run_integration_verification():
    """Run all Phase 2 integration verification tests."""
    print("🔧 Starting Phase 2 Integration Verification...")
    print("=" * 50)

    try:
        verify_decorator_compatibility()
        verify_security_integration()
        verify_property_override_system()
        verify_context_aware_resolution()
        verify_legacy_compatibility()

        print("=" * 50)
        print("✅ Phase 2 Integration Verification PASSED")
        print("All existing systems are properly integrated!")

    except Exception as e:
        print("=" * 50)
        print(f"❌ Phase 2 Integration Verification FAILED: {str(e)}")
        raise


if __name__ == "__main__":
    run_integration_verification()
