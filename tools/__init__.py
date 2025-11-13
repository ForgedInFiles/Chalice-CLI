"""
Chalice Tools Package
Comprehensive tool system for filesystem, execution, git, API, and system operations
"""
from .base import Tool, ToolRegistry
from .execution import PythonExecutor, JavaScriptExecutor, BashExecutor
from .git import GitStatus, GitDiff, GitCommit, GitBranch, GitPush, GitPull, GitLog
from .api import HTTPRequest, GraphQLQuery, WebhookSender
from .system import SystemCommand, PackageManager, ProcessManager


def create_default_registry() -> ToolRegistry:
    """Create and populate the default tool registry"""
    registry = ToolRegistry()

    # Execution tools
    registry.register(PythonExecutor())
    registry.register(JavaScriptExecutor())
    registry.register(BashExecutor())

    # Git tools
    registry.register(GitStatus())
    registry.register(GitDiff())
    registry.register(GitCommit())
    registry.register(GitBranch())
    registry.register(GitPush())
    registry.register(GitPull())
    registry.register(GitLog())

    # API tools
    registry.register(HTTPRequest())
    registry.register(GraphQLQuery())
    registry.register(WebhookSender())

    # System tools
    registry.register(SystemCommand())
    registry.register(PackageManager())
    registry.register(ProcessManager())

    return registry


__all__ = [
    'Tool',
    'ToolRegistry',
    'PythonExecutor',
    'JavaScriptExecutor',
    'BashExecutor',
    'GitStatus',
    'GitDiff',
    'GitCommit',
    'GitBranch',
    'GitPush',
    'GitPull',
    'GitLog',
    'HTTPRequest',
    'GraphQLQuery',
    'WebhookSender',
    'SystemCommand',
    'PackageManager',
    'ProcessManager',
    'create_default_registry'
]
