#!/usr/bin/env python3
import os
import json
import logging
from pathlib import Path
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

    def stream_chat(self, messages, model):
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
                self.models = [model['id'] for model in data['data']]
            else:
                self.models = ["openai/gpt-4o-mini", "openai/gpt-3.5-turbo", "anthropic/claude-3-haiku"]
        except:
            self.models = ["openai/gpt-4o-mini", "openai/gpt-3.5-turbo", "anthropic/claude-3-haiku"]

    def stream_chat(self, messages, model):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

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

    def stream_chat(self, messages, model):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

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

    def stream_chat(self, messages, model):
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True
            )
            for chunk in response:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"

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

    def stream_chat(self, messages, model):
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

class ZAIProvider(AIProvider):
    def __init__(self, api_key):
        super().__init__("ZAI", api_key)
        # Assuming ZAI uses a similar API, but since unknown, placeholder
        self.models = []  # Need to implement

    def get_models(self):
        # Placeholder
        pass

    def stream_chat(self, messages, model):
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
        data = {'messages': messages}
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

                # Get AI response with streaming
                provider = providers[current_provider]
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

                # Handle agent chaining
                current_content = content
                while True:
                    agent_calls = re.findall(r'\[AGENT: (\w+)\] (.*?) \[/AGENT\]', current_content, re.DOTALL)
                    if not agent_calls:
                        break
                    for agent_name, query in agent_calls:
                        agent_response = invoke_agent(agent_name, query)
                        agent_message = f"**{agent_name.title()} Agent:** {agent_response}"
                        messages.append({"role": "assistant", "content": agent_message})
                        print_message("assistant", agent_message)
                        current_content = agent_response

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