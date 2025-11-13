"""
System command execution tools with safety controls
"""
import subprocess
import shutil
from typing import Dict, Any, List
from .base import Tool


class SystemCommand(Tool):
    """Execute system commands with safety controls"""

    # Whitelist of safe commands
    SAFE_COMMANDS = {
        'ls', 'pwd', 'whoami', 'date', 'echo', 'cat', 'head', 'tail',
        'grep', 'find', 'wc', 'sort', 'uniq', 'diff', 'which',
        'pip', 'npm', 'node', 'python', 'python3', 'git',
        'docker', 'kubectl', 'make', 'cargo', 'go', 'rustc',
        'java', 'javac', 'gcc', 'g++', 'clang',
        'curl', 'wget', 'ping', 'traceroute', 'netstat',
        'ps', 'top', 'df', 'du', 'free', 'uptime'
    }

    # Blacklist of dangerous commands
    DANGEROUS_COMMANDS = {
        'rm', 'rmdir', 'del', 'format', 'mkfs', 'dd',
        'chmod', 'chown', 'kill', 'killall', 'shutdown',
        'reboot', 'init', 'systemctl', 'service'
    }

    def get_name(self) -> str:
        return "system_command"

    def get_description(self) -> str:
        return "Execute whitelisted system commands safely with output capture"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Command to execute"
                },
                "args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Command arguments"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30)",
                    "default": 30
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory",
                    "default": "."
                }
            },
            "required": ["command"]
        }

    def execute(
        self,
        command: str,
        args: List[str] = None,
        timeout: int = 30,
        working_dir: str = "."
    ) -> Dict[str, Any]:
        """Execute system command"""
        try:
            # Security check
            cmd_name = command.split()[0] if ' ' in command else command

            if cmd_name in self.DANGEROUS_COMMANDS:
                return {
                    "error": f"Command '{cmd_name}' is blacklisted for safety",
                    "blocked": True
                }

            if cmd_name not in self.SAFE_COMMANDS:
                # Check if command exists
                if not shutil.which(cmd_name):
                    return {"error": f"Command not found: {cmd_name}"}

            # Build command
            cmd = [command]
            if args:
                cmd.extend(args)

            # Execute
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=min(timeout, 300),
                cwd=working_dir
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode,
                "command": ' '.join(cmd)
            }

        except subprocess.TimeoutExpired:
            return {"error": f"Command timed out after {timeout} seconds"}
        except Exception as e:
            return {"error": str(e)}


class PackageManager(Tool):
    """Manage packages with pip, npm, etc."""

    def get_name(self) -> str:
        return "package_manager"

    def get_description(self) -> str:
        return "Install, update, or list packages using pip, npm, or other package managers"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "manager": {
                    "type": "string",
                    "enum": ["pip", "npm", "yarn", "cargo", "go"],
                    "description": "Package manager to use"
                },
                "action": {
                    "type": "string",
                    "enum": ["install", "uninstall", "list", "update", "search"],
                    "description": "Action to perform"
                },
                "package": {
                    "type": "string",
                    "description": "Package name (required for install/uninstall/search)"
                },
                "global": {
                    "type": "boolean",
                    "description": "Install globally (for npm/yarn)",
                    "default": False
                }
            },
            "required": ["manager", "action"]
        }

    def execute(
        self,
        manager: str,
        action: str,
        package: str = None,
        global_install: bool = False
    ) -> Dict[str, Any]:
        """Manage packages"""
        try:
            # Build command based on manager and action
            cmd = []

            if manager == "pip":
                cmd = ["pip"]
                if action == "install":
                    if not package:
                        return {"error": "Package name required for install"}
                    cmd.extend(["install", package])
                elif action == "uninstall":
                    if not package:
                        return {"error": "Package name required for uninstall"}
                    cmd.extend(["uninstall", "-y", package])
                elif action == "list":
                    cmd.extend(["list"])
                elif action == "search":
                    if not package:
                        return {"error": "Package name required for search"}
                    cmd.extend(["search", package])
                else:
                    return {"error": f"Unknown action: {action}"}

            elif manager == "npm":
                cmd = ["npm"]
                if action == "install":
                    if not package:
                        return {"error": "Package name required for install"}
                    if global_install:
                        cmd.extend(["install", "-g", package])
                    else:
                        cmd.extend(["install", package])
                elif action == "uninstall":
                    if not package:
                        return {"error": "Package name required for uninstall"}
                    if global_install:
                        cmd.extend(["uninstall", "-g", package])
                    else:
                        cmd.extend(["uninstall", package])
                elif action == "list":
                    cmd.extend(["list", "-g" if global_install else "--depth=0"])
                elif action == "update":
                    if package:
                        cmd.extend(["update", package])
                    else:
                        cmd.extend(["update"])
                else:
                    return {"error": f"Unknown action: {action}"}

            # Execute command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # Package operations can take time
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "return_code": result.returncode
            }

        except subprocess.TimeoutExpired:
            return {"error": "Package operation timed out"}
        except Exception as e:
            return {"error": str(e)}


class ProcessManager(Tool):
    """Manage processes"""

    def get_name(self) -> str:
        return "process_manager"

    def get_description(self) -> str:
        return "List or manage running processes"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "enum": ["list", "find", "info"],
                    "description": "Action to perform"
                },
                "pattern": {
                    "type": "string",
                    "description": "Process name pattern (for find action)"
                }
            },
            "required": ["action"]
        }

    def execute(self, action: str, pattern: str = None) -> Dict[str, Any]:
        """Manage processes"""
        try:
            if action == "list":
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return {
                    "success": True,
                    "processes": result.stdout
                }

            elif action == "find":
                if not pattern:
                    return {"error": "Pattern required for find action"}
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                lines = [line for line in result.stdout.split('\n') if pattern in line]
                return {
                    "success": True,
                    "matches": lines,
                    "count": len(lines)
                }

            elif action == "info":
                result = subprocess.run(
                    ["ps", "aux"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                return {
                    "success": True,
                    "info": result.stdout
                }

            else:
                return {"error": f"Unknown action: {action}"}

        except Exception as e:
            return {"error": str(e)}
