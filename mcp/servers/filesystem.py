"""
MCP Filesystem Server
Provides file and directory operations following MCP best practices
"""
from pathlib import Path
from typing import Dict, Any
from ..client import MCPServer, MCPTool
import os
import shutil


class ReadFileTool(MCPTool):
    """Read content from a file with optional line range limits"""

    def __init__(self):
        super().__init__(
            "read_file",
            "Read content from a file with optional line range limits"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative file path to read"
                },
                "offset": {
                    "type": "integer",
                    "description": "Starting line number (0-based)",
                    "default": 0
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of lines to read",
                    "default": 2000
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str, offset: int = 0, limit: int = 2000) -> Dict[str, Any]:
        try:
            resolved_path = Path(path).resolve()

            if not resolved_path.exists():
                return {"error": f"File does not exist: {resolved_path}"}

            if not resolved_path.is_file():
                return {"error": f"Path is not a file: {resolved_path}"}

            with open(resolved_path, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            total_lines = len(lines)
            start_line = max(0, min(offset, total_lines))
            end_line = min(start_line + limit, total_lines)

            content = ''.join(lines[start_line:end_line])

            return {
                "path": str(resolved_path),
                "content": content,
                "lines_read": end_line - start_line,
                "total_lines": total_lines,
                "start_line": start_line,
                "end_line": end_line - 1
            }
        except Exception as e:
            return {"error": str(e)}


class WriteFileTool(MCPTool):
    """Write or overwrite content to a file"""

    def __init__(self):
        super().__init__(
            "write_file",
            "Write or overwrite content to a file"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative file path to write to"
                },
                "content": {
                    "type": "string",
                    "description": "Content to write to the file"
                }
            },
            "required": ["path", "content"]
        }

    def execute(self, path: str, content: str) -> Dict[str, Any]:
        try:
            resolved_path = Path(path).resolve()
            resolved_path.parent.mkdir(parents=True, exist_ok=True)

            with open(resolved_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                "path": str(resolved_path),
                "bytes_written": len(content.encode('utf-8')),
                "lines_written": len(content.splitlines())
            }
        except Exception as e:
            return {"error": str(e)}


class ListDirectoryTool(MCPTool):
    """List all files and subdirectories in a given path"""

    def __init__(self):
        super().__init__(
            "list_directory",
            "List all files and subdirectories in a given path with their types and sizes"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative directory path to list"
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str) -> Dict[str, Any]:
        try:
            resolved_path = Path(path).resolve()

            if not resolved_path.exists():
                return {"error": f"Path does not exist: {resolved_path}"}

            if not resolved_path.is_dir():
                return {"error": f"Path is not a directory: {resolved_path}"}

            items = []
            for item in sorted(resolved_path.iterdir()):
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified": stat.st_mtime
                    })
                except OSError:
                    items.append({
                        "name": item.name,
                        "type": "unknown",
                        "size": None,
                        "modified": None
                    })

            return {
                "path": str(resolved_path),
                "items": items,
                "count": len(items)
            }
        except Exception as e:
            return {"error": str(e)}


class CreateDirectoryTool(MCPTool):
    """Create a new directory and any necessary parent directories"""

    def __init__(self):
        super().__init__(
            "create_directory",
            "Create a new directory and any necessary parent directories"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative directory path to create"
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str) -> Dict[str, Any]:
        try:
            resolved_path = Path(path).resolve()

            if resolved_path.exists():
                if resolved_path.is_dir():
                    return {"message": f"Directory already exists: {resolved_path}"}
                else:
                    return {"error": f"Path exists but is not a directory: {resolved_path}"}

            resolved_path.mkdir(parents=True, exist_ok=True)

            return {
                "path": str(resolved_path),
                "created": True
            }
        except Exception as e:
            return {"error": str(e)}


class DeletePathTool(MCPTool):
    """Delete a file or directory (recursive for directories)"""

    def __init__(self):
        super().__init__(
            "delete_path",
            "Delete a file or directory (recursive for directories)"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Absolute or relative path to delete"
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str) -> Dict[str, Any]:
        try:
            resolved_path = Path(path).resolve()

            if not resolved_path.exists():
                return {"error": f"Path does not exist: {resolved_path}"}

            if resolved_path.is_file():
                resolved_path.unlink()
                return {
                    "path": str(resolved_path),
                    "deleted": True,
                    "type": "file"
                }
            elif resolved_path.is_dir():
                shutil.rmtree(resolved_path)
                return {
                    "path": str(resolved_path),
                    "deleted": True,
                    "type": "directory"
                }
            else:
                return {"error": f"Unknown path type: {resolved_path}"}
        except Exception as e:
            return {"error": str(e)}


class MovePathTool(MCPTool):
    """Move or rename a file or directory"""

    def __init__(self):
        super().__init__(
            "move_path",
            "Move or rename a file or directory"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "src": {
                    "type": "string",
                    "description": "Source path to move"
                },
                "dst": {
                    "type": "string",
                    "description": "Destination path"
                }
            },
            "required": ["src", "dst"]
        }

    def execute(self, src: str, dst: str) -> Dict[str, Any]:
        try:
            src_path = Path(src).resolve()
            dst_path = Path(dst).resolve()

            if not src_path.exists():
                return {"error": f"Source path does not exist: {src_path}"}

            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))

            return {
                "src": str(src_path),
                "dst": str(dst_path),
                "moved": True
            }
        except Exception as e:
            return {"error": str(e)}


class FileExistsTool(MCPTool):
    """Check if a path exists and return its type and metadata"""

    def __init__(self):
        super().__init__(
            "file_exists",
            "Check if a path exists and return its type and metadata"
        )

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Path to check for existence"
                }
            },
            "required": ["path"]
        }

    def execute(self, path: str) -> Dict[str, Any]:
        try:
            resolved_path = Path(path).resolve()

            if not resolved_path.exists():
                return {
                    "path": str(resolved_path),
                    "exists": False
                }

            stat = resolved_path.stat()

            return {
                "path": str(resolved_path),
                "exists": True,
                "type": "directory" if resolved_path.is_dir() else "file",
                "size": stat.st_size if resolved_path.is_file() else None,
                "modified": stat.st_mtime,
                "permissions": oct(stat.st_mode)[-3:]
            }
        except Exception as e:
            return {"error": str(e)}


def create_filesystem_server() -> MCPServer:
    """Create and configure the filesystem MCP server"""
    server = MCPServer(
        "filesystem",
        "File and directory operations with secure path handling"
    )

    # Register all tools
    server.register_tool(ReadFileTool())
    server.register_tool(WriteFileTool())
    server.register_tool(ListDirectoryTool())
    server.register_tool(CreateDirectoryTool())
    server.register_tool(DeletePathTool())
    server.register_tool(MovePathTool())
    server.register_tool(FileExistsTool())

    return server
