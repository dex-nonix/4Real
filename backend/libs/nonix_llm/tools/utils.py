"""Utility functions for LLM tools."""
import os
import pathlib
from os.path import abspath, isabs, dirname, exists, join, normpath
from typing import Dict, Any, Optional, Union


def resolve_safe_path(
    path: str,
    root_path: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
    context_key: Optional[str] = None,
    bind_root: bool = True,
    create_dirs: bool = False,
    must_exist: bool = False
) -> str:
    """Resolve and validate a file path to ensure it's within allowed boundaries.
    
    This function provides path safety for LLM tools by ensuring file operations
    cannot access files outside of a specified root directory.
    
    Args:
        path: The target path to validate (can be relative or absolute)
        root_path: Optional root directory to bind paths to
        context: Optional context dictionary to extract root path from
        context_key: Key to extract root path from context (e.g., "output_dir")
        bind_root: Whether to enforce path is within root directory
        create_dirs: Whether to create parent directories if they don't exist
        must_exist: Whether to verify the final path exists
        
    Returns:
        Absolute resolved path if valid
        
    Raises:
        ValueError: If path would escape the root directory when bind_root=True
        FileNotFoundError: If must_exist=True and the path doesn't exist
    """
    # Get effective root path (priority: direct root_path, then context_key)
    effective_root = root_path
    if not effective_root and context and context_key:
        effective_root = context.get(context_key)
    
    # If no root constraints, just return absolute path
    if not effective_root:
        abs_path = abspath(path)
    else:
        # Normalize the root path
        abs_root = abspath(effective_root)
        
        # Handle absolute paths differently than relative paths
        if isabs(path):
            abs_path = abspath(path)
            # For absolute paths, we only check if they're within root when bind_root=True
            # We don't join with the root
        else:
            # For relative paths, join with the root path
            abs_path = abspath(join(abs_root, path))
        
        # Check if path is within root when bind_root=True
        if bind_root and not abs_path.startswith(abs_root):
            raise ValueError(f"Path '{path}' attempts to escape root directory '{abs_root}'")
    
    # Create parent directories if requested
    if create_dirs:
        parent_dir = dirname(abs_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)
    
    # Check if path exists if required
    if must_exist and not exists(abs_path):
        raise FileNotFoundError(f"Path does not exist: {abs_path}")
    
    return abs_path


def is_path_safe(path: str, root_path: str) -> bool:
    """Check if a path is safely contained within a root directory.
    
    Args:
        path: The path to check
        root_path: The root directory path
        
    Returns:
        True if the path is within the root directory, False otherwise
    """
    try:
        return abspath(path).startswith(abspath(root_path))
    except Exception:
        return False


def normalize_path(path: Union[str, pathlib.Path]) -> str:
    """Normalize a path to an absolute path with consistent separators.
    
    Args:
        path: The path to normalize
        
    Returns:
        Normalized absolute path string
    """
    return abspath(normpath(str(path))) 