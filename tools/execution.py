"""
Code execution tools with sandboxing and safety controls
"""
import subprocess
import tempfile
import os
import signal
from pathlib import Path
from typing import Dict, Any
from .base import Tool


class PythonExecutor(Tool):
    """Execute Python code in a controlled environment"""

    def get_name(self) -> str:
        return "execute_python"

    def get_description(self) -> str:
        return "Execute Python code in a sandboxed environment with timeout and resource controls"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Python code to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30, max: 300)",
                    "default": 30
                },
                "input_data": {
                    "type": "string",
                    "description": "Input data to pass to the code via stdin",
                    "default": ""
                }
            },
            "required": ["code"]
        }

    def execute(self, code: str, timeout: int = 30, input_data: str = "") -> Dict[str, Any]:
        """Execute Python code with safety controls"""
        try:
            # Limit timeout
            timeout = min(max(timeout, 1), 300)

            # Create temporary file for code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                # Execute with timeout
                process = subprocess.Popen(
                    ['python3', temp_file],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )

                try:
                    stdout, stderr = process.communicate(input=input_data, timeout=timeout)
                    return_code = process.returncode

                    return {
                        "success": return_code == 0,
                        "stdout": stdout,
                        "stderr": stderr,
                        "return_code": return_code,
                        "timeout": False
                    }
                except subprocess.TimeoutExpired:
                    # Kill the process group
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        process.terminate()
                    process.wait()

                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": f"Execution timed out after {timeout} seconds",
                        "return_code": -1,
                        "timeout": True
                    }
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_file)
                except:
                    pass

        except Exception as e:
            return {"error": str(e)}


class JavaScriptExecutor(Tool):
    """Execute JavaScript code using Node.js"""

    def get_name(self) -> str:
        return "execute_javascript"

    def get_description(self) -> str:
        return "Execute JavaScript code using Node.js with timeout controls"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "JavaScript code to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30, max: 300)",
                    "default": 30
                }
            },
            "required": ["code"]
        }

    def execute(self, code: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute JavaScript code"""
        try:
            # Check if Node.js is available
            check = subprocess.run(['which', 'node'], capture_output=True)
            if check.returncode != 0:
                return {"error": "Node.js is not installed"}

            timeout = min(max(timeout, 1), 300)

            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
                f.write(code)
                temp_file = f.name

            try:
                process = subprocess.Popen(
                    ['node', temp_file],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    preexec_fn=os.setsid if os.name != 'nt' else None
                )

                try:
                    stdout, stderr = process.communicate(timeout=timeout)
                    return_code = process.returncode

                    return {
                        "success": return_code == 0,
                        "stdout": stdout,
                        "stderr": stderr,
                        "return_code": return_code,
                        "timeout": False
                    }
                except subprocess.TimeoutExpired:
                    if os.name != 'nt':
                        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    else:
                        process.terminate()
                    process.wait()

                    return {
                        "success": False,
                        "stdout": "",
                        "stderr": f"Execution timed out after {timeout} seconds",
                        "return_code": -1,
                        "timeout": True
                    }
            finally:
                try:
                    os.unlink(temp_file)
                except:
                    pass

        except Exception as e:
            return {"error": str(e)}


class BashExecutor(Tool):
    """Execute Bash commands safely"""

    def get_name(self) -> str:
        return "execute_bash"

    def get_description(self) -> str:
        return "Execute Bash commands with safety controls and timeout"

    def get_parameters(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "Bash command to execute"
                },
                "timeout": {
                    "type": "integer",
                    "description": "Timeout in seconds (default: 30, max: 300)",
                    "default": 30
                },
                "working_dir": {
                    "type": "string",
                    "description": "Working directory for command execution",
                    "default": "."
                }
            },
            "required": ["command"]
        }

    def execute(self, command: str, timeout: int = 30, working_dir: str = ".") -> Dict[str, Any]:
        """Execute bash command"""
        try:
            # Dangerous commands blacklist
            dangerous = ['rm -rf /', 'mkfs', 'dd if=', ':(){:|:&};:', 'chmod -R 777 /']
            if any(danger in command for danger in dangerous):
                return {"error": "Dangerous command blocked for safety"}

            timeout = min(max(timeout, 1), 300)

            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=working_dir,
                preexec_fn=os.setsid if os.name != 'nt' else None
            )

            try:
                stdout, stderr = process.communicate(timeout=timeout)
                return_code = process.returncode

                return {
                    "success": return_code == 0,
                    "stdout": stdout,
                    "stderr": stderr,
                    "return_code": return_code,
                    "timeout": False
                }
            except subprocess.TimeoutExpired:
                if os.name != 'nt':
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                else:
                    process.terminate()
                process.wait()

                return {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Command timed out after {timeout} seconds",
                    "return_code": -1,
                    "timeout": True
                }

        except Exception as e:
            return {"error": str(e)}
