"""
Test suite for Chalice agents
"""
import pytest
from pathlib import Path
import tempfile
from agents.core import Agent, AgentMetadata, AgentLoader, AgentRegistry, AgentCommunicator


class TestAgentMetadata:
    """Test agent metadata"""

    def test_metadata_creation(self):
        """Test creating agent metadata"""
        metadata = AgentMetadata(
            name="Test Agent",
            version="1.0.0",
            description="A test agent",
            capabilities=["testing", "validation"],
            system_prompt="You are a test agent"
        )

        assert metadata.name == "Test Agent"
        assert metadata.version == "1.0.0"
        assert len(metadata.capabilities) == 2


class TestAgent:
    """Test agent functionality"""

    def test_agent_creation(self):
        """Test creating an agent"""
        metadata = AgentMetadata(
            name="Test Agent",
            system_prompt="You are a test agent"
        )
        agent = Agent(metadata)

        assert agent.name == "Test Agent"
        assert agent.system_prompt == "You are a test agent"

    def test_agent_messages(self):
        """Test agent message generation"""
        metadata = AgentMetadata(
            name="Test Agent",
            system_prompt="You are a test agent"
        )
        agent = Agent(metadata)

        messages = agent.get_messages("Hello")
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Hello"

    def test_agent_history(self):
        """Test agent conversation history"""
        metadata = AgentMetadata(
            name="Test Agent",
            system_prompt="You are a test agent"
        )
        agent = Agent(metadata)

        agent.add_to_history("user", "Hello")
        agent.add_to_history("assistant", "Hi there!")

        assert len(agent.conversation_history) == 2
        agent.clear_history()
        assert len(agent.conversation_history) == 0


class TestAgentLoader:
    """Test agent loading from Markdown"""

    def test_parse_markdown_agent(self):
        """Test parsing agent from Markdown"""
        # Create a temporary Markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Agent: Test Agent

**Version**: 1.0.0
**Description**: A test agent for unit testing
**Author**: Test Suite

## Capabilities

- Testing
- Validation
- Verification

## System Prompt

You are a test agent designed for unit testing.
You help validate the agent system.
""")
            temp_path = Path(f.name)

        try:
            metadata = AgentLoader.parse_markdown_agent(temp_path)
            assert metadata is not None
            assert metadata.name == "Test Agent"
            assert metadata.version == "1.0.0"
            assert metadata.description == "A test agent for unit testing"
            assert len(metadata.capabilities) >= 3
            assert "test agent" in metadata.system_prompt.lower()
        finally:
            temp_path.unlink()

    def test_load_agent(self):
        """Test loading complete agent"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""# Agent: Test Agent

## System Prompt

You are a test agent.
""")
            temp_path = Path(f.name)

        try:
            agent = AgentLoader.load_agent(temp_path)
            assert agent is not None
            assert agent.name == "Test Agent"
        finally:
            temp_path.unlink()


class TestAgentRegistry:
    """Test agent registry"""

    def test_registry_creation(self):
        """Test creating registry"""
        registry = AgentRegistry()
        assert len(registry.get_all()) == 0

    def test_agent_registration(self):
        """Test registering agents"""
        registry = AgentRegistry()
        metadata = AgentMetadata(name="Test", system_prompt="Test prompt")
        agent = Agent(metadata)

        registry.register(agent)
        assert len(registry.get_all()) == 1
        assert registry.get("Test") == agent

    def test_agent_unregistration(self):
        """Test unregistering agents"""
        registry = AgentRegistry()
        metadata = AgentMetadata(name="Test", system_prompt="Test prompt")
        agent = Agent(metadata)

        registry.register(agent)
        registry.unregister("Test")
        assert len(registry.get_all()) == 0


class TestAgentCommunicator:
    """Test agent communication"""

    def test_communicator_creation(self):
        """Test creating communicator"""
        registry = AgentRegistry()
        communicator = AgentCommunicator(registry)
        assert communicator is not None

    def test_send_message(self):
        """Test sending messages between agents"""
        registry = AgentRegistry()
        communicator = AgentCommunicator(registry)

        communicator.send_message("agent1", "agent2", "Hello")
        messages = communicator.get_messages_for("agent2")

        assert len(messages) == 1
        assert messages[0]["from"] == "agent1"
        assert messages[0]["message"] == "Hello"

    def test_broadcast(self):
        """Test broadcasting messages"""
        registry = AgentRegistry()

        # Add some agents
        for i in range(3):
            metadata = AgentMetadata(name=f"agent{i}", system_prompt="Test")
            registry.register(Agent(metadata))

        communicator = AgentCommunicator(registry)
        communicator.broadcast("agent0", "Broadcast message")

        # Check that other agents received it
        messages_1 = communicator.get_messages_for("agent1")
        messages_2 = communicator.get_messages_for("agent2")

        assert len(messages_1) == 1
        assert len(messages_2) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
