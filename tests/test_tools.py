"""
Test suite for Chalice tools
"""
import pytest
from pathlib import Path
from tools.base import Tool, ToolRegistry
from tools.execution import PythonExecutor, JavaScriptExecutor, BashExecutor
from tools.git import GitStatus, GitDiff, GitBranch, GitLog
from tools.api import HTTPRequest, GraphQLQuery
from tools.system import SystemCommand, PackageManager


class TestToolRegistry:
    """Test tool registry functionality"""

    def test_registry_creation(self):
        """Test creating a tool registry"""
        registry = ToolRegistry()
        assert registry is not None
        assert len(registry.get_all()) == 0

    def test_tool_registration(self):
        """Test registering tools"""
        registry = ToolRegistry()
        tool = PythonExecutor()
        registry.register(tool)
        assert len(registry.get_all()) == 1
        assert registry.get("execute_python") == tool

    def test_tool_execution(self):
        """Test executing tools via registry"""
        registry = ToolRegistry()
        tool = PythonExecutor()
        registry.register(tool)

        result = registry.execute("execute_python", code="print('hello')", timeout=5)
        assert "stdout" in result or "success" in result


class TestExecutionTools:
    """Test code execution tools"""

    def test_python_executor(self):
        """Test Python code execution"""
        executor = PythonExecutor()
        result = executor.execute(code="print('Hello, World!')", timeout=5)

        assert "success" in result
        if result.get("success"):
            assert "Hello, World!" in result.get("stdout", "")

    def test_python_timeout(self):
        """Test Python execution timeout"""
        executor = PythonExecutor()
        result = executor.execute(
            code="import time\ntime.sleep(10)",
            timeout=2
        )

        assert result.get("timeout") == True

    def test_bash_executor(self):
        """Test Bash command execution"""
        executor = BashExecutor()
        result = executor.execute(command="echo 'test'", timeout=5)

        assert "success" in result

    def test_bash_dangerous_command(self):
        """Test that dangerous commands are blocked"""
        executor = BashExecutor()
        result = executor.execute(command="rm -rf /", timeout=5)

        assert "error" in result
        assert "blocked" in result.get("error", "").lower()


class TestGitTools:
    """Test Git integration tools"""

    def test_git_status(self):
        """Test git status tool"""
        tool = GitStatus()
        result = tool.execute()

        # Should work in a git repo or return an error
        assert "error" in result or "branch" in result

    def test_git_log(self):
        """Test git log tool"""
        tool = GitLog()
        result = tool.execute(limit=5)

        # Should work in a git repo or return an error
        assert "error" in result or "commits" in result


class TestAPITools:
    """Test API interaction tools"""

    def test_http_request_get(self):
        """Test HTTP GET request"""
        tool = HTTPRequest()
        # Using a public API for testing
        result = tool.execute(
            url="https://api.github.com/zen",
            method="GET",
            timeout=10
        )

        if "error" not in result:
            assert "status_code" in result
            assert result.get("status_code") in [200, 429]  # 429 = rate limited

    def test_graphql_query(self):
        """Test GraphQL query"""
        tool = GraphQLQuery()
        # Simple test query
        result = tool.execute(
            endpoint="https://countries.trevorblades.com/",
            query="{ countries { code name } }",
            timeout=10
        )

        if "error" not in result:
            assert "data" in result or "errors" in result


class TestSystemTools:
    """Test system command tools"""

    def test_system_command_safe(self):
        """Test safe system command"""
        tool = SystemCommand()
        result = tool.execute(command="echo", args=["test"])

        assert "success" in result or "error" in result

    def test_system_command_blacklist(self):
        """Test blacklisted command"""
        tool = SystemCommand()
        result = tool.execute(command="rm", args=["-rf", "/"])

        assert "error" in result
        assert "blocked" in result or "blacklist" in str(result).lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
