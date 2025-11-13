#!/usr/bin/env python3
"""
Chalice Enhanced - Full-featured AI Assistant with Tools and Agents
Version 2.0.0
"""
import os
import json
import logging
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
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

# Import our new tools and agents
from tools import create_default_registry, ToolRegistry
from tools.execution import PythonExecutor, JavaScriptExecutor, BashExecutor
from tools.git import GitStatus, GitDiff, GitCommit, GitBranch, GitPush, GitPull, GitLog
from tools.api import HTTPRequest, GraphQLQuery, WebhookSender
from tools.system import SystemCommand, PackageManager, ProcessManager
from agents.core import AgentRegistry, AgentLoader, AgentCommunicator, AgentChain

# Load environment variables
load_dotenv()

# Suppress Google library warnings
logging.getLogger('absl').setLevel(logging.ERROR)

console = Console()


def format_tool_result(tool_name: str, result: Dict[str, Any]) -> str:
    """Format tool results for display"""
    if "error" in result:
        return f"❌ **Error**: {result['error']}"

    # Git tools
    if tool_name == "git_status":
        lines = [f"📊 **Git Status**"]
        lines.append(f"**Branch**: {result.get('branch', 'unknown')}")
        lines.append(f"**Clean**: {'✅ Yes' if result.get('clean') else '❌ No'}")
        if result.get('files'):
            lines.append(f"\n**Modified Files**: {len(result['files'])}")
        return "\n".join(lines)

    elif tool_name == "git_diff":
        if result.get('has_changes'):
            return f"```diff\n{result.get('diff', '')}\n```"
        return "No changes to display"

    elif tool_name == "git_commit":
        return f"✅ **Commit Created**\n{result.get('output', '')}"

    elif tool_name == "git_branch":
        if 'branches' in result:
            return f"**Branches**:\n" + "\n".join(f"- {b}" for b in result['branches'])
        return f"✅ **Branch {result.get('action', '')}**: {result.get('branch', '')}"

    elif tool_name == "git_push" or tool_name == "git_pull":
        return f"✅ **{tool_name.replace('_', ' ').title()} Successful**\n{result.get('output', '')}"

    elif tool_name == "git_log":
        return f"**Recent Commits** ({result.get('count', 0)}):\n" + "\n".join(result.get('commits', []))

    # Execution tools
    elif tool_name in ["execute_python", "execute_javascript", "execute_bash"]:
        status = "✅ Success" if result.get('success') else "❌ Failed"
        output = []
        output.append(f"**Status**: {status}")
        if result.get('timeout'):
            output.append(f"⏱️ **Timeout**: Command exceeded time limit")
        if result.get('stdout'):
            output.append(f"\n**Output**:\n```\n{result['stdout']}\n```")
        if result.get('stderr'):
            output.append(f"\n**Errors**:\n```\n{result['stderr']}\n```")
        return "\n".join(output)

    # API tools
    elif tool_name == "http_request":
        status = "✅ Success" if result.get('success') else "❌ Failed"
        output = [f"**Status**: {status} ({result.get('status_code', 'N/A')})"]
        output.append(f"**Time**: {result.get('elapsed_ms', 0):.0f}ms")
        if result.get('json'):
            output.append(f"\n**Response**:\n```json\n{json.dumps(result['json'], indent=2)}\n```")
        elif result.get('body'):
            body = result['body'][:500] + "..." if len(result.get('body', '')) > 500 else result.get('body', '')
            output.append(f"\n**Body**:\n```\n{body}\n```")
        return "\n".join(output)

    elif tool_name == "graphql_query":
        status = "✅ Success" if result.get('success') else "❌ Failed"
        output = [f"**Status**: {status}"]
        if result.get('data'):
            output.append(f"\n**Data**:\n```json\n{json.dumps(result['data'], indent=2)}\n```")
        if result.get('errors'):
            output.append(f"\n**Errors**:\n```json\n{json.dumps(result['errors'], indent=2)}\n```")
        return "\n".join(output)

    # System tools
    elif tool_name == "system_command":
        if result.get('blocked'):
            return f"🚫 **Command Blocked**: {result.get('error', '')}"
        status = "✅ Success" if result.get('success') else "❌ Failed"
        output = [f"**Command**: `{result.get('command', '')}`", f"**Status**: {status}"]
        if result.get('stdout'):
            output.append(f"\n**Output**:\n```\n{result['stdout']}\n```")
        if result.get('stderr'):
            output.append(f"\n**Errors**:\n```\n{result['stderr']}\n```")
        return "\n".join(output)

    elif tool_name == "package_manager":
        status = "✅ Success" if result.get('success') else "❌ Failed"
        output = [f"**Status**: {status}"]
        if result.get('stdout'):
            stdout = result['stdout'][:500] + "..." if len(result.get('stdout', '')) > 500 else result.get('stdout', '')
            output.append(f"\n**Output**:\n```\n{stdout}\n```")
        return "\n".join(output)

    # Default
    return f"```json\n{json.dumps(result, indent=2)}\n```"


class AIProvider:
    def __init__(self, name, api_key):
        self.name = name
        self.api_key = api_key
        self.models = []

    def get_models(self):
        raise NotImplementedError

    def stream_chat(self, messages, model, tools=None):
        raise NotImplementedError

    def supports_tools(self) -> bool:
        return False


class OpenRouterProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__("OpenRouter", api_key)
        self.client = openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

    def get_models(self):
        try:
            import requests
            response = requests.get("https://openrouter.ai/api/v1/models", headers={"Authorization": f"Bearer {self.api_key}"})
            if response.status_code == 200:
                data = response.json()
                self.models = [model["id"] for model in data.get("data", [])]
            else:
                self.models = ["openai/gpt-4o-mini", "openai/gpt-3.5-turbo"]
        except:
            self.models = ["openai/gpt-4o-mini", "openai/gpt-3.5-turbo"]

    def stream_chat(self, messages, model, tools=None):
        try:
            kwargs = {"model": model, "messages": messages, "stream": True}
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
            response = self.client.chat.completions.create(model=model, messages=messages, tools=tools)
            return response.choices[0].message.tool_calls
        except:
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
            self.models = ["llama3-8b-8192", "mixtral-8x7b-32768"]

    def stream_chat(self, messages, model, tools=None):
        try:
            kwargs = {"model": model, "messages": messages, "stream": True}
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
            response = self.client.chat.completions.create(model=model, messages=messages, tools=tools)
            return response.choices[0].message.tool_calls
        except:
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
            self.models = ["mistral-large-latest", "mistral-small"]

    def stream_chat(self, messages, model, tools=None):
        try:
            kwargs = {"model": model, "messages": messages, "stream": True}
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
            response = self.client.chat.completions.create(model=model, messages=messages, tools=tools)
            return response.choices[0].message.tool_calls
        except:
            return None


class GeminiProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__("Gemini", api_key)
        genai.configure(api_key=api_key)

    def get_models(self):
        try:
            models_list = genai.list_models()
            self.models = [model.name.replace("models/", "") for model in models_list if "gemini" in model.name]
        except:
            self.models = ["gemini-1.5-flash", "gemini-1.5-pro"]

    def stream_chat(self, messages, model, tools=None):
        try:
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


def print_header(current_provider, current_model):
    header = Panel(
        Align.center(
            Text("🔥 Chalice Enhanced v2.0", style="bold magenta") + "\n" +
            "AI Development Assistant with Full Tool Integration" + "\n" +
            f"Provider: {current_provider or 'None'} | Model: {current_model or 'None'}"
        ),
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

    md = Markdown(content, code_theme="github-dark")
    panel = Panel(md, title=f"[bold]{title}[/bold]", border_style=style, padding=(1, 2), box=ROUNDED)
    console.print(panel)
    console.print()


def main():
    # Initialize tool registry
    tool_registry = create_default_registry()

    # Initialize agent registry
    agent_registry = AgentRegistry()
    agent_communicator = AgentCommunicator(agent_registry)

    # Load agents from directories
    builtin_dir = Path("agents/builtin")
    custom_dir = Path("agents/custom")
    prompts_dir = Path("prompts")

    if builtin_dir.exists():
        agent_registry.load_from_directory(builtin_dir, is_builtin=True)

    if custom_dir.exists():
        agent_registry.load_from_directory(custom_dir, is_builtin=False)

    if prompts_dir.exists():
        agent_registry.load_from_directory(prompts_dir, is_builtin=False)

    # System prompt
    system_prompt_file = Path("prompts/system.md")
    if system_prompt_file.exists():
        system_content = system_prompt_file.read_text()
    else:
        system_content = "You are Chalice, an expert AI assistant with access to powerful tools and specialized agents."

    system_prompt = {"role": "system", "content": system_content}

    # Load providers
    providers = {}
    if os.getenv("OPENROUTER_API_KEY"):
        providers["openrouter"] = OpenRouterProvider(os.getenv("OPENROUTER_API_KEY"))
    if os.getenv("GROQ_API_KEY"):
        providers["groq"] = GroqProvider(os.getenv("GROQ_API_KEY"))
    if os.getenv("MISTRAL_API_KEY"):
        providers["mistral"] = MistralProvider(os.getenv("MISTRAL_API_KEY"))
    if os.getenv("GEMINI_API_KEY"):
        providers["gemini"] = GeminiProvider(os.getenv("GEMINI_API_KEY"))

    for name, provider in providers.items():
        provider.get_models()

    # Default settings
    current_provider = "openrouter" if "openrouter" in providers else (list(providers.keys())[0] if providers else None)
    default_model = "openai/gpt-4o-mini"
    current_model = default_model if current_provider and default_model in providers[current_provider].models else (
        providers[current_provider].models[0] if current_provider and providers[current_provider].models else None)

    # Chat history
    messages = [system_prompt]

    print_header(current_provider, current_model)

    # Show loaded agents
    agents_loaded = agent_registry.get_all()
    if agents_loaded:
        console.print(f"[green]✓ Loaded {len(agents_loaded)} agents[/green]")
        console.print()

    # Command completer
    commands = ['/help', '/model', '/settings', '/clear', '/export', '/test', '/quit', '/agents', '/tools', '/agent']

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
                # Handle commands
                if user_input == "/help":
                    help_text = """\
**Commands:**
/model - Select provider and model
/settings - Show current settings
/clear - Clear chat history
/export <filename> - Export conversation
/agents - List available agents
/tools - List available tools
/agent <name> - Use a specific agent
/test - Send a test message
/quit - Exit
"""
                    console.print(Panel(Markdown(help_text), title="Help", border_style="cyan", box=ROUNDED))

                elif user_input == "/agents":
                    agents = agent_registry.get_all()
                    if agents:
                        agent_list = "\n".join([f"- **{a.name}**: {a.metadata.description}" for a in agents])
                        console.print(Panel(Markdown(f"**Available Agents ({len(agents)})**:\n\n{agent_list}"),
                                          title="Agents", border_style="cyan", box=ROUNDED))
                    else:
                        console.print("[yellow]No agents loaded[/yellow]")

                elif user_input == "/tools":
                    tools = tool_registry.get_all()
                    tool_list = "\n".join([f"- **{t.name}**: {t.description}" for t in tools])
                    console.print(Panel(Markdown(f"**Available Tools ({len(tools)})**:\n\n{tool_list}"),
                                      title="Tools", border_style="cyan", box=ROUNDED))

                elif user_input.startswith("/agent "):
                    agent_name = user_input.split(" ", 1)[1]
                    agent = agent_registry.get(agent_name)
                    if agent:
                        console.print(f"[green]Switched to agent: {agent_name}[/green]")
                    else:
                        console.print(f"[red]Agent not found: {agent_name}[/red]")

                elif user_input == "/model":
                    provider_list = list(providers.keys())
                    console.print("[bold cyan]Available Providers:[/bold cyan]")
                    for i, p in enumerate(provider_list, 1):
                        console.print(f"{i}. {p}")
                    try:
                        provider_num = int(prompt("Select provider number: ").strip())
                        selected_provider = provider_list[provider_num - 1]
                        current_provider = selected_provider

                        models = providers[selected_provider].models
                        console.print("[bold cyan]Available Models:[/bold cyan]")
                        for i, m in enumerate(models, 1):
                            console.print(f"{i}. {m}")
                        model_num = int(prompt("Select model number: ").strip())
                        current_model = models[model_num - 1]
                        console.print(f"[green]Switched to: {current_provider}/{current_model}[/green]")
                    except (ValueError, IndexError):
                        console.print("[red]Invalid selection[/red]")

                elif user_input == "/settings":
                    console.print(f"[yellow]Provider: {current_provider}[/yellow]")
                    console.print(f"[yellow]Model: {current_model}[/yellow]")
                    console.print(f"[yellow]Agents: {len(agent_registry.get_all())}[/yellow]")
                    console.print(f"[yellow]Tools: {len(tool_registry.get_all())}[/yellow]")

                elif user_input.startswith("/export "):
                    filename = user_input.split(" ", 1)[1]
                    try:
                        with open(filename, 'w') as f:
                            for msg in messages[1:]:
                                if msg['role'] == 'user':
                                    f.write(f"## You\n\n{msg['content']}\n\n")
                                elif msg['role'] == 'assistant':
                                    f.write(f"## Chalice\n\n{msg['content']}\n\n")
                        console.print(f"[green]Exported to {filename}[/green]")
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")

                elif user_input == "/clear":
                    messages = [system_prompt]
                    console.print("[green]Chat history cleared[/green]")

                elif user_input == "/quit":
                    break

                else:
                    console.print("[red]Unknown command[/red]")

            elif user_input:
                if not current_provider:
                    console.print("[red]No provider selected[/red]")
                    continue

                messages.append({"role": "user", "content": user_input})
                print_message("user", user_input)

                provider = providers[current_provider]

                if provider.supports_tools():
                    # Get tools in OpenAI format
                    tools = tool_registry.get_openai_tools()

                    # Stream response
                    content = ""
                    with Live(console=console, refresh_per_second=10) as live:
                        md = Markdown("", code_theme="github-dark")
                        panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]",
                                    border_style="green", padding=(1, 2), box=ROUNDED)
                        live.update(panel)
                        for token in provider.stream_chat(messages, current_model, tools=tools):
                            content += token
                            md = Markdown(content, code_theme="github-dark")
                            panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]",
                                        border_style="green", padding=(1, 2), box=ROUNDED)
                            live.update(panel)

                    # Get tool calls
                    response = provider.client.chat.completions.create(
                        model=current_model,
                        messages=messages,
                        tools=tools
                    )
                    tool_calls = response.choices[0].message.tool_calls or []

                    # Add assistant message
                    messages.append({"role": "assistant", "content": content})

                    # Execute tool calls
                    if tool_calls:
                        for tool_call in tool_calls:
                            tool_name = tool_call.function.name
                            tool_args = json.loads(tool_call.function.arguments)

                            result = tool_registry.execute(tool_name, **tool_args)

                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "content": json.dumps(result)
                            })

                            # Display tool result
                            formatted = format_tool_result(tool_name, result)
                            panel = Panel(
                                Markdown(formatted, code_theme="github-dark"),
                                title=f"[bold blue]🔧 {tool_name.replace('_', ' ').title()}[/bold blue]",
                                border_style="blue",
                                box=ROUNDED,
                                padding=(1, 2)
                            )
                            console.print(panel)

                        # Get final response
                        final_content = ""
                        with Live(console=console, refresh_per_second=10) as live:
                            md = Markdown("", code_theme="github-dark")
                            panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]",
                                        border_style="green", padding=(1, 2), box=ROUNDED)
                            live.update(panel)
                            for token in provider.stream_chat(messages, current_model):
                                final_content += token
                                md = Markdown(final_content, code_theme="github-dark")
                                panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]",
                                            border_style="green", padding=(1, 2), box=ROUNDED)
                                live.update(panel)
                        messages.append({"role": "assistant", "content": final_content})

                else:
                    # No tool support
                    content = ""
                    with Live(console=console, refresh_per_second=10) as live:
                        md = Markdown("", code_theme="github-dark")
                        panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]",
                                    border_style="green", padding=(1, 2), box=ROUNDED)
                        live.update(panel)
                        for token in provider.stream_chat(messages, current_model):
                            content += token
                            md = Markdown(content, code_theme="github-dark")
                            panel = Panel(md, title="[bold green]🤖 Chalice[/bold green]",
                                        border_style="green", padding=(1, 2), box=ROUNDED)
                            live.update(panel)
                    messages.append({"role": "assistant", "content": content})

        except KeyboardInterrupt:
            console.print("\n[red]Exiting...[/red]")
            break
        except EOFError:
            break


if __name__ == "__main__":
    main()
