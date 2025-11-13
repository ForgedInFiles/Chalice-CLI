"""
Chalice Agents Package
Multi-agent system with dynamic loading and communication
"""
from .core import (
    Agent,
    AgentMetadata,
    AgentLoader,
    AgentRegistry,
    AgentCommunicator,
    AgentChain
)

__all__ = [
    'Agent',
    'AgentMetadata',
    'AgentLoader',
    'AgentRegistry',
    'AgentCommunicator',
    'AgentChain'
]
