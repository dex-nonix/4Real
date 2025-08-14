"""
File operation tools with built-in security features.

This module provides a set of file operation tools that use the resolve_safe_path
utility to prevent path traversal attacks and ensure safe file operations.
"""

import os
import glob
import json
import yaml
from typing import List, Dict, Any
import logging

from nonix_llm import llm_tool
from nonix_llm.tools.utils import resolve_safe_path


logger = logging.getLogger("nonix_llm.tools.file_tools")


@llm_tool(
    description="Read file contents securely",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={"file_path": "Path to the file you want to read"}
)
def read_file(context, file_path: str, root_path=None, context_key=None, bind_root=True) -> str:
    """Read file contents with path safety."""
    logger.debug(f"read_file called with context={context}, file_path={file_path}, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            must_exist=True
        )
        
        with open(safe_path, 'r') as f:
            return f.read()
    except Exception as e:
        return f"Error: {str(e)}"


@llm_tool(
    description="Write content to a file securely",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "file_path": "Path to the file you want to write to",
        "content": "Content to write to the file"
    }
)
def write_file(context, file_path: str, content: str, root_path=None, context_key=None, bind_root=True) -> str:
    """Write content to file with path safety."""
    logger.debug(f"write_file called with context={context}, file_path={file_path}, content=<hidden>, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            create_dirs=True
        )
        
        with open(safe_path, 'w') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@llm_tool(
    description="Append content to a file securely",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "file_path": "Path to the file you want to append to",
        "content": "Content to append to the file"
    }
)
def append_file(context, file_path: str, content: str, root_path=None, context_key=None, bind_root=True) -> str:
    """Append content to file with path safety."""
    logger.debug(f"append_file called with context={context}, file_path={file_path}, content=<hidden>, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            create_dirs=True
        )
        
        with open(safe_path, 'a') as f:
            f.write(content)
        return f"Successfully appended to {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@llm_tool(
    description="Find files matching a pattern in a directory",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "pattern": "Glob pattern to match files (e.g., '*.txt', '*.py') (optional, defaults to '*')",
        "directory": "Directory to search in (optional, defaults to current directory)",
        "recursive": "Whether to search subdirectories recursively (optional, defaults to False)"
    }
)
def find_files(context, pattern: str = "*", directory: str = ".", recursive: bool = False, 
               root_path=None, context_key=None, bind_root=True) -> List[str]:
    """Find files matching pattern with path safety."""
    logger.debug(f"find_files called with context={context}, pattern={pattern}, directory={directory}, recursive={recursive}, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_dir = resolve_safe_path(
            path=directory,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            must_exist=True
        )
        
        if recursive:
            search_pattern = os.path.join(safe_dir, "**", pattern)
            files = glob.glob(search_pattern, recursive=True)
        else:
            search_pattern = os.path.join(safe_dir, pattern)
            files = glob.glob(search_pattern)
            
        # Convert absolute paths back to relative paths if needed
        if bind_root and root_path:
            files = [os.path.relpath(f, root_path) for f in files]
            
        return files
    except Exception as e:
        return [f"Error: {str(e)}"]


@llm_tool(
    description="Check if a file or directory exists",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "path": "Path to check for existence"
    }
)
def path_exists(context, path: str, root_path=None, context_key=None, bind_root=True) -> bool:
    """Check if a path exists with path safety."""
    logger.debug(f"path_exists called with context={context}, path={path}, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=path,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root
        )
        return os.path.exists(safe_path)
    except Exception:
        return False


@llm_tool(
    description="Get file information (size, modification time, etc.)",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "file_path": "Path to the file you want information about"
    }
)
def file_info(context, file_path: str, root_path=None, context_key=None, bind_root=True) -> Dict[str, Any]:
    """Get file information with path safety."""
    logger.debug(f"file_info called with context={context}, file_path={file_path}, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            must_exist=True
        )
        
        stat_info = os.stat(safe_path)
        return {
            "exists": True,
            "size": stat_info.st_size,
            "modified": stat_info.st_mtime,
            "created": stat_info.st_ctime,
            "is_file": os.path.isfile(safe_path),
            "is_dir": os.path.isdir(safe_path)
        }
    except Exception as e:
        return {"exists": False, "error": str(e)}


@llm_tool(
    description="Create a directory securely",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "directory": "Path to the directory you want to create",
        "parents": "Whether to create parent directories if they don't exist (optional, defaults to True)"
    }
)
def create_directory(context, directory: str, parents: bool = True, root_path=None, context_key=None, bind_root=True) -> str:
    """Create a directory with path safety."""
    logger.debug(f"create_directory called with context={context}, directory={directory}, parents={parents}, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=directory,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            create_dirs=parents
        )
        
        if not parents:
            os.mkdir(safe_path)
        else:
            os.makedirs(safe_path, exist_ok=True)
        return f"Successfully created directory {directory}"
    except Exception as e:
        return f"Error: {str(e)}"


@llm_tool(
    description="List directory contents",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "directory": "Path to the directory you want to list (optional, defaults to current directory)",
        "include_hidden": "Whether to include hidden files starting with . (optional, defaults to False)"
    }
)
def list_directory(context, directory: str = ".", include_hidden: bool = False, root_path=None, context_key=None, bind_root=True) -> List[str]:
    """List directory contents with path safety."""
    logger.debug(f"list_directory called with context={context}, directory={directory}, include_hidden={include_hidden}, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=directory,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            must_exist=True
        )
        
        items = os.listdir(safe_path)
        if not include_hidden:
            items = [item for item in items if not item.startswith('.')]
        return items
    except Exception as e:
        return [f"Error: {str(e)}"]


@llm_tool(
    description="Read and parse JSON file securely",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "file_path": "Path to the JSON file you want to read"
    }
)
def read_json_file(context, file_path: str, root_path=None, context_key=None, bind_root=True) -> Dict[str, Any]:
    """Read and parse JSON file with path safety."""
    logger.debug(f"read_json_file called with context={context}, file_path={file_path}, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            must_exist=True
        )
        
        with open(safe_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON format"}
    except Exception as e:
        return {"error": str(e)}


@llm_tool(
    description="Write data to a JSON file securely",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "file_path": "Path to the JSON file you want to write to",
        "data": "Data to write to the JSON file (required)",
        "indent": "Number of spaces for indentation (optional, defaults to 2)"
    }
)
def write_json_file(context, file_path: str, data: Dict[str, Any], indent: int = 2, root_path=None, context_key=None, bind_root=True) -> str:
    """Write data to a JSON file with path safety."""
    logger.debug(f"write_json_file called with context={context}, file_path={file_path}, data=<hidden>, indent={indent}, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            create_dirs=True
        )
        
        with open(safe_path, 'w') as f:
            json.dump(data, f, indent=indent)
        return f"Successfully wrote JSON to {file_path}"
    except Exception as e:
        return f"Error: {str(e)}"


@llm_tool(
    description="Read and parse YAML file securely",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "file_path": "Path to the YAML file you want to read"
    }
)
def read_yaml_file(context, file_path: str, root_path=None, context_key=None, bind_root=True) -> Dict[str, Any]:
    """Read and parse YAML file with path safety."""
    logger.debug(f"read_yaml_file called with context={context}, file_path={file_path}, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            must_exist=True
        )
        
        with open(safe_path, 'r') as f:
            return yaml.safe_load(f)
    except yaml.YAMLError:
        return {"error": "Invalid YAML format"}
    except Exception as e:
        return {"error": str(e)}


@llm_tool(
    description="Write data to a YAML file securely",
    partial=["context"],
    hidden_props=["root_path", "bind_root", "context_key"],
    param_descriptions={
        "file_path": "Path to the YAML file you want to write to",
        "data": "Data to write to the YAML file (required)"
    }
)
def write_yaml_file(context, file_path: str, data: Dict[str, Any], root_path=None, context_key=None, bind_root=True) -> str:
    """Write data to a YAML file with path safety."""
    logger.debug(f"write_yaml_file called with context={context}, file_path={file_path}, data=<hidden>, root_path={root_path}, context_key={context_key}, bind_root={bind_root}")
    try:
        safe_path = resolve_safe_path(
            path=file_path,
            root_path=root_path,
            context=context,
            context_key=context_key,
            bind_root=bind_root,
            create_dirs=True
        )
        
        with open(safe_path, 'w') as f:
            yaml.safe_dump(data, f)
        return f"Successfully wrote YAML to {file_path}"
    except Exception as e:
        return f"Error: {str(e)}" 