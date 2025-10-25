#!/usr/bin/env python3
import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
from rich.markdown import Markdown
from rich.align import Align
from rich.live import Live
from rich.box import ROUNDED
from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
import openai
from groq import Groq
from mistralai import Mistral
import google.generativeai as genai
import requests
import re

# Tool definitions and implementations
filesystem_tools = [
    {
        "type": "function",
        "function": {
            "name": "list_directory",
            "description": "List all files and subdirectories in a given path with their types and sizes",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative directory path to list"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read content from a file with optional line range limits",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite content to a file",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_directory",
            "description": "Create a new directory and any necessary parent directories",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative directory path to create"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_path",
            "description": "Delete a file or directory (recursive for directories)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to delete"
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "move_path",
            "description": "Move or rename a file or directory",
            "parameters": {
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
        }
    },
    {
        "type": "function",
        "function": {
            "name": "file_exists",
            "description": "Check if a path exists and return its type and metadata",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Path to check for existence"
                    }
                },
                "required": ["path"]
            }
        }
    }
]

def validate_path(path: str, allow_parent_traversal: bool = False) -> Path:
    """
    Validate and resolve a file path with security checks
    """
    try:
        resolved_path = Path(path).resolve()

        # Prevent directory traversal attacks unless explicitly allowed
        if not allow_parent_traversal:
            cwd = Path.cwd()
            try:
                resolved_path.relative_to(cwd)
            except ValueError:
                raise ValueError(f"Path outside working directory: {path}")

        return resolved_path
    except Exception as e:
        raise ValueError(f"Invalid path: {path} - {str(e)}")

def execute_filesystem_tool(name: str, **kwargs) -> Dict[str, Any]:
    """
    Execute a filesystem tool by name with given parameters
    """
    try:
        if name == "list_directory":
            path = kwargs.get("path")
            if not isinstance(path, str):
                return {"error": "Missing or invalid 'path' parameter"}
            return list_directory(path)
        elif name == "read_file":
            path = kwargs.get("path")
            if not isinstance(path, str):
                return {"error": "Missing or invalid 'path' parameter"}
            offset = kwargs.get("offset", 0)
            limit = kwargs.get("limit", 2000)
            return read_file(path, offset, limit)
        elif name == "write_file":
            path = kwargs.get("path")
            content = kwargs.get("content")
            if not isinstance(path, str) or not isinstance(content, str):
                return {"error": "Missing or invalid 'path' or 'content' parameter"}
            return write_file(path, content)
        elif name == "create_directory":
            path = kwargs.get("path")
            if not isinstance(path, str):
                return {"error": "Missing or invalid 'path' parameter"}
            return create_directory(path)
        elif name == "delete_path":
            path = kwargs.get("path")
            if not isinstance(path, str):
                return {"error": "Missing or invalid 'path' parameter"}
            return delete_path(path)
        elif name == "move_path":
            src = kwargs.get("src")
            dst = kwargs.get("dst")
            if not isinstance(src, str) or not isinstance(dst, str):
                return {"error": "Missing or invalid 'src' or 'dst' parameter"}
            return move_path(src, dst)
        elif name == "file_exists":
            path = kwargs.get("path")
            if not isinstance(path, str):
                return {"error": "Missing or invalid 'path' parameter"}
            return file_exists(path)
        else:
            return {"error": f"Unknown tool: {name}"}
    except Exception as e:
        return {"error": f"Tool execution failed: {str(e)}"}

def list_directory(path: str) -> Dict[str, Any]:
    """List contents of a directory"""
    try:
        resolved_path = validate_path(path)

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
                # Skip items we can't stat
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

def read_file(path: str, offset: int = 0, limit: int = 2000) -> Dict[str, Any]:
    """Read content from a file"""
    try:
        resolved_path = validate_path(path)

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

def write_file(path: str, content: str) -> Dict[str, Any]:
    """Write content to a file"""
    try:
        resolved_path = validate_path(path)

        # Create parent directories if they don't exist
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

def create_directory(path: str) -> Dict[str, Any]:
    """Create a directory"""
    try:
        resolved_path = validate_path(path)

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

def delete_path(path: str) -> Dict[str, Any]:
    """Delete a file or directory"""
    try:
        resolved_path = validate_path(path)

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

def move_path(src: str, dst: str) -> Dict[str, Any]:
    """Move or rename a path"""
    try:
        src_path = validate_path(src)
        dst_path = validate_path(dst)

        if not src_path.exists():
            return {"error": f"Source path does not exist: {src_path}"}

        # Ensure destination directory exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        shutil.move(str(src_path), str(dst_path))

        return {
            "src": str(src_path),
            "dst": str(dst_path),
            "moved": True
        }
    except Exception as e:
        return {"error": str(e)}

def file_exists(path: str) -> Dict[str, Any]:
    """Check if a path exists and get metadata"""
    try:
        resolved_path = validate_path(path)

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

# Tool registry
all_tools = filesystem_tools
tool_executors = {
    "list_directory": execute_filesystem_tool,
    "read_file": execute_filesystem_tool,
    "write_file": execute_filesystem_tool,
    "create_directory": execute_filesystem_tool,
    "delete_path": execute_filesystem_tool,
    "move_path": execute_filesystem_tool,
    "file_exists": execute_filesystem_tool,
}

def format_tool_result(tool_name: str, result: Dict[str, Any]) -> str:
    """Format tool results for display"""
    if "error" in result:
        return f"❌ Error: {result['error']}"

    if tool_name == "list_directory":
        if "items" in result:
            lines = [f"📁 Directory: {result['path']}", f"📊 Total items: {result['count']}", ""]
            for item in result["items"]:
                icon = "📁" if item["type"] == "directory" else "📄"
                size = f" ({item['size']} bytes)" if item["size"] else ""
                lines.append(f"{icon} {item['name']}{size}")
            return "\n".join(lines)
        else:
            return f"📁 {result.get('message', 'Directory listed')}"

    elif tool_name == "read_file":
        if "content" in result:
            lines = [f"📖 File: {result['path']}", f"📏 Lines: {result['lines_read']} of {result['total_lines']}", ""]
            lines.append(result["content"])
            return "\n".join(lines)
        else:
            return f"📖 {result.get('message', 'File read')}"

    elif tool_name == "write_file":
        return f"✏️ File written: {result['path']} ({result['bytes_written']} bytes, {result['lines_written']} lines)"

    elif tool_name == "create_directory":
        return f"📁 Directory created: {result['path']}"

    elif tool_name == "delete_path":
        return f"🗑️ {'Directory' if result['type'] == 'directory' else 'File'} deleted: {result['path']}"

    elif tool_name == "move_path":
        return f"📦 Moved: {result['src']} → {result['dst']}"

    elif tool_name == "file_exists":
        if result["exists"]:
            type_icon = "📁" if result["type"] == "directory" else "📄"
            size = f" ({result['size']} bytes)" if result.get("size") else ""
            return f"{type_icon} Exists: {result['path']}{size}"
        else:
            return f"❓ Not found: {result['path']}"

    return json.dumps(result, indent=2)

# Load environment variables
load_dotenv()

# Manually parse .env file to ensure keys are loaded
try:
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
except FileNotFoundError:
    pass

# Suppress Google library warnings
logging.getLogger('absl').setLevel(logging.ERROR)

console = Console()

class AIProvider:
    def __init__(self, name, api_key):
        self.name = name
        self.api_key = api_key
        self.models = []

    def get_models(self):
        raise NotImplementedError

    def chat(self, messages, model):
        content = ""
        for token in self.stream_chat(messages, model):
            content += token
        return content

    def stream_chat(self, messages, model, tools=None):
        raise NotImplementedError

    def supports_tools(self) -> bool:
        """Return True if this provider supports tool calling"""
        return False

    def get_tool_calls(self, messages, model, tools):
        """Get tool calls from a non-streaming response"""
        raise NotImplementedError

class OpenRouterProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__("OpenRouter", api_key)
        self.client = openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

    def get_models(self):
        try:
            response = requests.get("https://openrouter.ai/api/v1/models", headers={"Authorization": f"Bearer {self.api_key}"})
            if response.status_code == 200:
                data = response.json()
                self.models = [model["id"] for model in data.get("data", [])]
            else:
                self.models = ["openai/gpt-4o-mini", "openai/gpt-3.5-turbo", "anthropic/claude-3-haiku"]
        except:
            self.models = ["openai/gpt-4o-mini", "openai/gpt-3.5-turbo", "anthropic/claude-3-haiku"]

    def stream_chat(self, messages, model, tools=None):
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            if tools:
                kwargs["tools"] = tools
            response = self.client.chat.completions.create(**kwargs)
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

    def supports_tools(self):
        return True

    def get_tool_calls(self, messages, model, tools):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools
            )
            return response.choices[0].message.tool_calls
        except Exception:
            return None

class GroqProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__("Groq", api_key)
        self.client = Groq(api_key=api_key)

    def get_models(self):
        try:
            models = self.client.models.list()
            self.models = [model.id for model in models.data]
        except:
            self.models = ["llama3-8b-8192", "mixtral-8x7b-32768", "gemma2-9b-it"]

    def stream_chat(self, messages, model, tools=None):
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            if tools:
                kwargs["tools"] = tools
            response = self.client.chat.completions.create(**kwargs)
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

    def supports_tools(self) -> bool:
        return True

    def get_tool_calls(self, messages, model, tools):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools
            )
            return response.choices[0].message.tool_calls
        except Exception:
            return None

class MistralProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__("Mistral", api_key)
        self.client = Mistral(api_key=api_key)

    def get_models(self):
        try:
            models = self.client.models.list()
            self.models = [model.id for model in models.data]
        except:
            self.models = ["mistral-large-latest", "mistral-medium", "mistral-small"]

    def stream_chat(self, messages, model, tools=None):
        try:
            kwargs = {
                "model": model,
                "messages": messages,
                "stream": True
            }
            if tools:
                kwargs["tools"] = tools
            response = self.client.chat.completions.create(**kwargs)
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

    def supports_tools(self) -> bool:
        return True

    def get_tool_calls(self, messages, model, tools):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools
            )
            return response.choices[0].message.tool_calls
        except Exception:
            return None

class GeminiProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__("Gemini", api_key)
        genai.configure(api_key=api_key)
        self.models = []

    def get_models(self):
        try:
            models_list = genai.list_models()
            self.models = [model.name.replace("models/", "") for model in models_list if "gemini" in model.name]
        except:
            self.models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"]  # fallback

    def stream_chat(self, messages, model, tools=None):
        # TODO: Implement tool calling for Gemini
        # For now, ignore tools
        try:
            # Build conversation prompt
            conversation = ""
            for msg in messages:
                role = "User" if msg["role"] == "user" else "Assistant"
                conversation += f"{role}: {msg['content']}\n"
            conversation += "Assistant: "

            gen_model = genai.GenerativeModel(model)
            response = gen_model.generate_content(conversation, stream=True)
            for chunk in response:
                yield chunk.text
        except Exception as e:
            yield f"Error: {str(e)}"

    def supports_tools(self) -> bool:
        return False  # TODO: Implement Gemini tool calling

class ZAIProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__("ZAI", api_key)
        # Assuming ZAI uses a similar API, but since unknown, placeholder
        self.models = []  # Need to implement

    def get_models(self):
        # Placeholder
        pass

    def stream_chat(self, messages, model, tools=None):
        # Placeholder
        yield "ZAI provider not implemented yet."

def print_header(current_provider, current_model):
    header = Panel(
        Align.center(Text("🧠 Chalice - AI Assistant", style="bold magenta") + "\n" + "Your expert companion in tech, coding, and beyond!" + "\n" + f"Provider: {current_provider or 'None'} | Model: {current_model or 'None'}"),
        title="[bold blue]Welcome[/bold blue]",
        border_style="blue",
        padding=(1, 2),
        box=ROUNDED
    )
    console.print(header)
    console.print()

def print_message(role, content):
    if role == "user":
        style = "bold cyan"
        title = "👤 You"
    else:
        style = "bold green"
        title = "🤖 Chalice"
    
    # Render markdown with syntax highlighting
    md = Markdown(content, code_theme="github-dark")
    panel = Panel(md, title=f"[bold]{title}[/bold]", border_style=style, padding=(1, 2), box=ROUNDED)
    console.print(panel)
    console.print()

def main():
    # Load agent prompts from prompts/*.md
    def load_agent_prompts():
        agents = {}
        prompts_dir = Path('prompts')
        if prompts_dir.exists():
            for file in prompts_dir.glob('*.md'):
                name = file.stem
                try:
                    with open(file, 'r') as f:
                        content = f.read().strip()
                        agents[name] = content
                except:
                    pass
        return agents

    agents = load_agent_prompts()
    system_prompt = {"role": "system", "content": agents.get('system', "You are Chalice, a world-renowned expert in Computer Science, Programming, Security, AI/ML, and all tech fields. You provide accurate, practical, and professional advice. Stay in character as Chalice, the ultimate tech virtuoso.")}

    def invoke_agent(agent_name, query):
        if agent_name not in agents:
            return f"Agent {agent_name} not found."
        agent_messages = [{"role": "system", "content": agents[agent_name]}, {"role": "user", "content": query}]
        content = ""
        for token in providers[current_provider].stream_chat(agent_messages, current_model):
            content += token
        return content

    def clean_content(content):
        # Remove agent call markers for display
        return re.sub(r'\[AGENT: \w+\] .*? \[/AGENT\]', '', content, flags=re.DOTALL).strip()

    def load_history():
        history_file = Path('.chalice')
        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    data = json.load(f)
                    loaded_messages = data.get('messages', [])
                    # Ensure system prompt is first
                    if loaded_messages and loaded_messages[0].get('role') == 'system':
                        return loaded_messages
                    else:
                        return [system_prompt] + loaded_messages
            except:
                return [system_prompt]
        return [system_prompt]

    def save_history(messages):
        history_file = Path('.chalice')
        # Only save user and assistant messages, filter out tool messages
        filtered_messages = [msg for msg in messages if msg['role'] in ['user', 'assistant']]
        data = {'messages': filtered_messages}
        try:
            with open(history_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            pass  # Silent save errors

    # Load providers
    providers = {}
    if os.getenv("OPENROUTER_API_KEY"):
        providers["openrouter"] = OpenRouterProvider(os.getenv("OPENROUTER_API_KEY"))
    if os.getenv("GROQ_API_KEY"):
        providers["groq"] = GroqProvider(os.getenv("GROQ_API_KEY"))
    if os.getenv("MISTRAL_API_KEY"):
        providers["mistral"] = MistralProvider(os.getenv("MISTRAL_API_KEY"))
    if os.getenv("ZAI_API_KEY"):
        providers["zai"] = ZAIProvider(os.getenv("ZAI_API_KEY"))
    if os.getenv("GEMINI_API_KEY"):
        providers["gemini"] = GeminiProvider(os.getenv("GEMINI_API_KEY"))

    # Auto-detect models
    for name, provider in providers.items():
        provider.get_models()

    # Default settings: OpenRouter with gpt-4o-mini
    current_provider = "openrouter" if "openrouter" in providers else (list(providers.keys())[0] if providers else None)
    default_model = "openai/gpt-4o-mini"
    current_model = default_model if current_provider and default_model in providers[current_provider].models else (providers[current_provider].models[0] if current_provider and providers[current_provider].models else None)

    # Chat history
    messages = load_history()

    print_header(current_provider, current_model)

    # Command completer for slash commands
    commands = ['/help', '/model', '/settings', '/clear', '/export', '/test', '/quit']

    class SlashCompleter(Completer):
        def get_completions(self, document, complete_event):
            if not document.text.startswith('/'):
                return
            for cmd in commands:
                if cmd.startswith(document.text):
                    yield Completion(cmd, start_position=-len(document.text))

    completer = SlashCompleter()

    while True:
        try:
            user_input = prompt("👤 You > ", completer=completer).strip()

            if user_input.startswith("/"):
                # Handle slash commands
                if user_input == "/help":
                    help_text = """\
/model - Select provider and model interactively
/settings - Show current settings
/clear - Clear chat history
/export <filename> - Export conversation to markdown file
/test - Send a test message
/quit - Exit
"""
                    help_panel = Panel(help_text, title="[bold cyan]Available Commands[/bold cyan]", border_style="cyan", box=ROUNDED, padding=(1, 2))
                    console.print(help_panel)
                elif user_input.startswith("/provider "):
                    provider_name = user_input.split(" ", 1)[1]
                    if provider_name in providers:
                        current_provider = provider_name
                        current_model = providers[current_provider].models[0] if providers[current_provider].models else None
                        console.print(f"[green]Switched to provider: {provider_name}[/green]")
                    else:
                        console.print("[red]Invalid provider[/red]")
                elif user_input == "/model":
                    # Select provider
                    provider_list = list(providers.keys())
                    console.print("[bold cyan]Available Providers:[/bold cyan]")
                    for i, p in enumerate(provider_list, 1):
                        console.print(f"{i}. {p}")
                    try:
                        provider_num = int(prompt("Select provider number: ").strip())
                        selected_provider = provider_list[provider_num - 1]
                        current_provider = selected_provider
                        console.print(f"[green]Selected provider: {selected_provider}[/green]")
                        
                        # Select model
                        models = providers[selected_provider].models
                        if not models:
                            console.print("[red]No models available for this provider[/red]")
                            continue
                        console.print("[bold cyan]Available Models:[/bold cyan]")
                        for i, m in enumerate(models, 1):
                            console.print(f"{i}. {m}")
                        model_num = int(prompt("Select model number: ").strip())
                        selected_model = models[model_num - 1]
                        current_model = selected_model
                        console.print(f"[green]Switched to model: {selected_model}[/green]")
                    except (ValueError, IndexError):
                        console.print("[red]Invalid selection[/red]")
                elif user_input == "/settings":
                    console.print(f"[yellow]Current provider: {current_provider}[/yellow]")
                    console.print(f"[yellow]Current model: {current_model}[/yellow]")
                elif user_input.startswith("/export "):
                    filename = user_input.split(" ", 1)[1]
                    try:
                        with open(filename, 'w') as f:
                            for msg in messages[1:]:  # Skip system prompt
                                if msg['role'] == 'user':
                                    f.write(f"## You\n\n{msg['content']}\n\n")
                                elif msg['role'] == 'assistant':
                                    f.write(f"## Chalice\n\n{msg['content']}\n\n")
                        console.print(f"[green]Conversation exported to {filename}[/green]")
                    except Exception as e:
                        console.print(f"[red]Error exporting: {e}[/red]")
                elif user_input == "/clear":
                    messages = [system_prompt]
                    save_history(messages)
                    console.print("[green]Chat history cleared[/green]")
                elif user_input == "/quit":
                    break
                else:
                    console.print("[red]Unknown command. Type /help for commands.[/red]")
            elif user_input:
                if not current_provider or not current_model:
                    console.print("[red]No provider or model selected[/red]")
                    continue

                messages.append({"role": "user", "content": user_input})
                print_message("user", user_input)

                # Get AI response
                provider = providers[current_provider]

                if provider.supports_tools():
                    # Stream the initial response
                    try:
                        content = ""
                        tool_calls = []
                        with Live(console=console, refresh_per_second=10) as live:
                            md = Markdown("", code_theme="github-dark")
                            panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]", border_style="green", padding=(1, 2), box=ROUNDED)
                            live.update(panel)
                            for token in provider.stream_chat(messages, current_model, tools=all_tools):
                                content += token
                                cleaned = clean_content(content)
                                md = Markdown(cleaned, code_theme="github-dark")
                                panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]", border_style="green", padding=(1, 2), box=ROUNDED)
                                live.update(panel)
                        # Note: For simplicity, assuming tool_calls are not streamed; in full implementation, accumulate tool_calls from deltas
                        # For now, after streaming content, get tool_calls via non-streaming
                        response = provider.client.chat.completions.create(
                            model=current_model,
                            messages=messages,
                            tools=all_tools
                        )
                        assistant_message = response.choices[0].message
                        tool_calls = assistant_message.tool_calls or []

                        # Append the assistant message to conversation
                        assistant_dict = {"role": "assistant", "content": content}
                        if tool_calls:
                            assistant_dict["tool_calls"] = tool_calls
                        messages.append(assistant_dict)

                        # Handle tool calls
                        if tool_calls:
                            for tool_call in tool_calls:
                                tool_name = tool_call.function.name
                                tool_args = json.loads(tool_call.function.arguments)
                                if tool_name in tool_executors:
                                    result = tool_executors[tool_name](tool_name, **tool_args)
                                else:
                                    result = {"error": f"Unknown tool: {tool_name}"}
                                messages.append({
                                    "role": "tool",
                                    "tool_call_id": tool_call.id,
                                    "content": json.dumps(result)
                                })
                                # Display formatted tool result
                                tool_message = format_tool_result(tool_name, result)
                                tool_panel = Panel(tool_message, title=f"[bold blue]🔧 {tool_name.replace('_', ' ').title()}[/bold blue]", border_style="blue", box=ROUNDED, padding=(1, 2))
                                console.print(tool_panel)

                            # Stream the final response
                            final_content = ""
                            with Live(console=console, refresh_per_second=10) as live:
                                md = Markdown("", code_theme="github-dark")
                                panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]", border_style="green", padding=(1, 2), box=ROUNDED)
                                live.update(panel)
                                for token in provider.stream_chat(messages, current_model):
                                    final_content += token
                                    cleaned = clean_content(final_content)
                                    md = Markdown(cleaned, code_theme="github-dark")
                                    panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]", border_style="green", padding=(1, 2), box=ROUNDED)
                                    live.update(panel)
                            messages.append({"role": "assistant", "content": final_content})
                    except Exception as e:
                        error_msg = f"Error: {str(e)}"
                        console.print(Panel(error_msg, title="[red]Error[/red]", border_style="red", box=ROUNDED))
                else:
                    # Normal streaming for non-tool providers
                    content = ""
                    with Live(console=console, refresh_per_second=10) as live:
                        md = Markdown("", code_theme="github-dark")
                        panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]", border_style="green", padding=(1, 2), box=ROUNDED)
                        live.update(panel)
                        for token in provider.stream_chat(messages, current_model):
                            content += token
                            cleaned = clean_content(content)
                            md = Markdown(cleaned, code_theme="github-dark")
                            panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]", border_style="green", padding=(1, 2), box=ROUNDED)
                            live.update(panel)
                    messages.append({"role": "assistant", "content": content})

                save_history(messages)
            else:
                continue
        except KeyboardInterrupt:
            console.print("\n[red]Exiting...[/red]")
            break
        except EOFError:
            break

if __name__ == "__main__":
    main()