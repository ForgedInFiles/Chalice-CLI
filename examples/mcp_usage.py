"""
Chalice MCP Usage Examples
Demonstrates the Model Context Protocol patterns following Anthropic's best practices
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Example 1: Tool Discovery
def example_tool_discovery():
    """Discover tools by exploring the filesystem"""
    import os

    print("=== Tool Discovery ===")

    # List available servers
    servers = os.listdir('./servers')
    print(f"Available servers: {servers}")

    # Explore git server
    git_tools = os.listdir('./servers/git')
    print(f"Git server tools: {git_tools}")

    # Read tool documentation
    with open('./servers/git/status.py') as f:
        print("\nGit status tool:")
        print(f.read()[:500] + "...")


# Example 2: Simple File Operations
def example_file_operations():
    """Use filesystem tools for basic operations"""
    from servers.filesystem import read_file, write_file, list_directory

    print("\n=== File Operations ===")

    # Write a file
    result = write_file(
        path="example.txt",
        content="Hello from Chalice MCP!\nThis is a test file."
    )
    print(f"✓ Wrote {result['bytes_written']} bytes")

    # Read it back
    content = read_file(path="example.txt")
    print(f"✓ Read {content['lines_read']} lines")
    print(f"Content: {content['content'][:50]}...")

    # List directory
    listing = list_directory(path=".")
    print(f"✓ Found {listing['count']} items in directory")


# Example 3: Git Workflow
def example_git_workflow():
    """Complete git workflow with multiple tools"""
    from servers.git import status, commit, push, log

    print("\n=== Git Workflow ===")

    # Check status
    git_status = status(repo_path=".")
    print(f"Branch: {git_status['branch']}")
    print(f"Clean: {git_status['clean']}")

    # View recent commits
    history = log(repo_path=".", limit=5)
    print(f"\nRecent commits ({history['count']}):")
    for commit in history['commits'][:3]:
        print(f"  - {commit}")


# Example 4: Context-Efficient Data Processing
def example_data_processing():
    """Process large data in execution environment"""
    from servers.api import http
    from servers.filesystem import write_file
    import json

    print("\n=== Data Processing (Context Efficient) ===")

    # Simulate fetching large dataset
    print("Fetching data from API...")

    # In real scenario, would fetch from API:
    # response = http(url="https://api.example.com/data", method="GET")

    # Simulate large dataset
    large_dataset = [
        {"id": i, "status": "active" if i % 3 == 0 else "inactive", "value": i * 10}
        for i in range(1000)
    ]

    # Filter in execution environment (not in model context!)
    active_items = [item for item in large_dataset if item['status'] == 'active']

    # Only log summary, not full data
    print(f"Filtered {len(large_dataset)} items to {len(active_items)} active items")

    # Save processed results
    write_file(
        path="active_items.json",
        content=json.dumps(active_items[:10], indent=2)  # Sample only
    )
    print("✓ Saved processed data (sample)")


# Example 5: Code Execution
def example_code_execution():
    """Execute code in sandboxed environment"""
    from servers.execution import python, javascript

    print("\n=== Code Execution ===")

    # Python execution
    python_result = python(
        code="""
import math
result = sum(math.sqrt(i) for i in range(1, 101))
print(f"Sum of square roots: {result:.2f}")
        """,
        timeout=5
    )

    if python_result['success']:
        print(f"✓ Python: {python_result['stdout'].strip()}")
    else:
        print(f"✗ Python error: {python_result['stderr']}")

    # JavaScript execution
    js_result = javascript(
        code="""
const fibonacci = n => {
    let a = 0, b = 1;
    for (let i = 0; i < n; i++) [a, b] = [b, a + b];
    return a;
};
console.log('Fibonacci(20):', fibonacci(20));
        """,
        timeout=5
    )

    if js_result['success']:
        print(f"✓ JavaScript: {js_result['stdout'].strip()}")


# Example 6: API Interactions
def example_api_interactions():
    """Make HTTP requests to external APIs"""
    from servers.api import http

    print("\n=== API Interactions ===")

    # Simple GET request
    response = http(
        url="https://api.github.com/zen",
        method="GET",
        timeout=10
    )

    if response.get('success'):
        print(f"✓ GitHub Zen: {response['body']}")
        print(f"  Status: {response['status_code']}")
        print(f"  Time: {response['elapsed_ms']:.0f}ms")
    else:
        print(f"✗ Error: {response.get('error', 'Unknown error')}")


# Example 7: MCP Client Usage
def example_mcp_client():
    """Use the MCP client directly for advanced operations"""
    from mcp import get_mcp_client

    print("\n=== MCP Client ===")

    client = get_mcp_client()

    # List all servers
    servers = client.list_servers()
    print(f"Registered servers: {servers}")

    # Search for tools
    tools = client.search_tools("file", detail_level="name_and_description")
    print(f"\nTools matching 'file':")
    for tool in tools[:3]:
        print(f"  - {tool['server']}.{tool['tool']}: {tool['description']}")

    # Get tool definition
    tool_def = client.get_tool_definition("filesystem", "read_file")
    print(f"\nTool definition for filesystem.read_file:")
    print(f"  Parameters: {list(tool_def['parameters']['properties'].keys())}")


# Example 8: Error Handling
def example_error_handling():
    """Proper error handling with MCP tools"""
    from servers.filesystem import read_file

    print("\n=== Error Handling ===")

    # Try to read non-existent file
    result = read_file(path="nonexistent.txt")

    if 'error' in result:
        print(f"✗ Expected error: {result['error']}")
    else:
        print(f"✓ Read {result['lines_read']} lines")


def main():
    """Run all examples"""
    print("Chalice MCP Usage Examples")
    print("=" * 50)

    try:
        example_tool_discovery()
        example_file_operations()
        example_git_workflow()
        example_data_processing()
        example_code_execution()
        example_api_interactions()
        example_mcp_client()
        example_error_handling()

        print("\n" + "=" * 50)
        print("✓ All examples completed successfully!")

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
