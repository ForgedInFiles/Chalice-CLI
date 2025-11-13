"""
Core agent framework for Chalice
Supports dynamic loading, communication, and collaboration
"""
from typing import Dict, Any, List, Optional, Callable
from pathlib import Path
from dataclasses import dataclass, field
import json
import re


@dataclass
class AgentMetadata:
    """Agent metadata from Markdown file"""
    name: str
    version: str = "1.0.0"
    description: str = ""
    capabilities: List[str] = field(default_factory=list)
    system_prompt: str = ""
    examples: List[str] = field(default_factory=list)
    author: str = ""
    tags: List[str] = field(default_factory=list)


class Agent:
    """Base agent class"""

    def __init__(self, metadata: AgentMetadata, file_path: Optional[Path] = None):
        self.metadata = metadata
        self.file_path = file_path
        self.conversation_history: List[Dict[str, str]] = []

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def system_prompt(self) -> str:
        return self.metadata.system_prompt

    def get_messages(self, user_query: str) -> List[Dict[str, str]]:
        """Get messages for AI provider"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        messages.extend(self.conversation_history)
        messages.append({"role": "user", "content": user_query})
        return messages

    def add_to_history(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({"role": role, "content": content})

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()


class AgentLoader:
    """Load agents from Markdown files"""

    @staticmethod
    def parse_markdown_agent(file_path: Path) -> Optional[AgentMetadata]:
        """Parse agent definition from Markdown file"""
        try:
            content = file_path.read_text(encoding='utf-8')

            # Extract metadata
            name = file_path.stem
            version = "1.0.0"
            description = ""
            capabilities = []
            system_prompt = ""
            examples = []
            author = ""
            tags = []

            # Parse Markdown sections
            lines = content.split('\n')
            current_section = None
            section_content = []

            for line in lines:
                # Check for section headers
                if line.startswith('# Agent:'):
                    name = line.replace('# Agent:', '').strip()
                elif line.startswith('**Version**:'):
                    version = line.replace('**Version**:', '').strip()
                elif line.startswith('**Description**:'):
                    description = line.replace('**Description**:', '').strip()
                elif line.startswith('**Author**:'):
                    author = line.replace('**Author**:', '').strip()
                elif line.startswith('**Tags**:'):
                    tags_str = line.replace('**Tags**:', '').strip()
                    tags = [t.strip() for t in tags_str.split(',') if t.strip()]
                elif line.startswith('## Capabilities'):
                    current_section = 'capabilities'
                    section_content = []
                elif line.startswith('## System Prompt'):
                    current_section = 'system_prompt'
                    section_content = []
                elif line.startswith('## Examples'):
                    current_section = 'examples'
                    section_content = []
                elif line.startswith('##'):
                    # Save previous section
                    if current_section == 'system_prompt':
                        system_prompt = '\n'.join(section_content).strip()
                    current_section = None
                    section_content = []
                else:
                    if current_section:
                        section_content.append(line)
                        # Parse capabilities (list items)
                        if current_section == 'capabilities' and line.strip().startswith('-'):
                            cap = line.strip()[1:].strip()
                            if cap:
                                capabilities.append(cap)

            # Save last section
            if current_section == 'system_prompt':
                system_prompt = '\n'.join(section_content).strip()

            # Fallback: if no system prompt section, use entire content
            if not system_prompt:
                system_prompt = content.strip()

            return AgentMetadata(
                name=name,
                version=version,
                description=description,
                capabilities=capabilities,
                system_prompt=system_prompt,
                examples=examples,
                author=author,
                tags=tags
            )

        except Exception as e:
            print(f"Error parsing agent file {file_path}: {e}")
            return None

    @staticmethod
    def load_agent(file_path: Path) -> Optional[Agent]:
        """Load an agent from a Markdown file"""
        metadata = AgentLoader.parse_markdown_agent(file_path)
        if metadata:
            return Agent(metadata, file_path)
        return None


class AgentRegistry:
    """Registry for managing agents"""

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.builtin_dir: Optional[Path] = None
        self.custom_dir: Optional[Path] = None

    def register(self, agent: Agent):
        """Register an agent"""
        self.agents[agent.name] = agent

    def unregister(self, agent_name: str):
        """Unregister an agent"""
        if agent_name in self.agents:
            del self.agents[agent_name]

    def get(self, agent_name: str) -> Optional[Agent]:
        """Get an agent by name"""
        return self.agents.get(agent_name)

    def get_all(self) -> List[Agent]:
        """Get all registered agents"""
        return list(self.agents.values())

    def load_from_directory(self, directory: Path, is_builtin: bool = False):
        """Load all agents from a directory"""
        if not directory.exists():
            return

        for file_path in directory.glob('*.md'):
            agent = AgentLoader.load_agent(file_path)
            if agent:
                self.register(agent)
                if is_builtin:
                    print(f"Loaded built-in agent: {agent.name}")
                else:
                    print(f"Loaded custom agent: {agent.name}")

    def reload_agent(self, agent_name: str):
        """Reload a specific agent from disk"""
        agent = self.get(agent_name)
        if agent and agent.file_path:
            new_agent = AgentLoader.load_agent(agent.file_path)
            if new_agent:
                self.register(new_agent)
                return True
        return False

    def reload_all(self):
        """Reload all agents from their source files"""
        for agent in list(self.agents.values()):
            if agent.file_path:
                self.reload_agent(agent.name)


class AgentCommunicator:
    """Handles inter-agent communication"""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.message_queue: List[Dict[str, Any]] = []

    def send_message(
        self,
        from_agent: str,
        to_agent: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Send a message from one agent to another"""
        self.message_queue.append({
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "metadata": metadata or {}
        })

    def get_messages_for(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get all messages for a specific agent"""
        messages = [msg for msg in self.message_queue if msg["to"] == agent_name]
        # Remove delivered messages
        self.message_queue = [msg for msg in self.message_queue if msg["to"] != agent_name]
        return messages

    def broadcast(self, from_agent: str, message: str, metadata: Optional[Dict[str, Any]] = None):
        """Broadcast a message to all agents"""
        for agent in self.registry.get_all():
            if agent.name != from_agent:
                self.send_message(from_agent, agent.name, message, metadata)


class AgentChain:
    """Chain multiple agents for complex workflows"""

    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.steps: List[Dict[str, Any]] = []

    def add_step(self, agent_name: str, transform: Optional[Callable] = None):
        """Add a step to the chain"""
        self.steps.append({
            "agent": agent_name,
            "transform": transform
        })
        return self

    def execute(self, initial_query: str, ai_provider) -> List[Dict[str, Any]]:
        """Execute the agent chain"""
        results = []
        current_input = initial_query

        for step in self.steps:
            agent = self.registry.get(step["agent"])
            if not agent:
                results.append({
                    "agent": step["agent"],
                    "error": "Agent not found"
                })
                continue

            # Get agent response
            messages = agent.get_messages(current_input)
            response = ""

            # Stream response from AI provider
            for token in ai_provider.stream_chat(messages, ai_provider.current_model):
                response += token

            # Apply transformation if provided
            if step["transform"]:
                response = step["transform"](response)

            results.append({
                "agent": agent.name,
                "input": current_input,
                "output": response
            })

            # Next input is current output
            current_input = response

        return results
