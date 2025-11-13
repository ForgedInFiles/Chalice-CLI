# Chalice MCP Architecture

## Overview

Chalice implements the **Model Context Protocol (MCP)** following Anthropic's latest best practices for code execution with MCP servers. This architecture enables efficient, scalable agent interactions with tools while minimizing token usage and maximizing performance.

## What is MCP?

The Model Context Protocol is an open standard for connecting AI agents to external systems. Instead of loading all tool definitions upfront and passing intermediate results through the context window, MCP with code execution allows agents to:

1. **Discover tools on-demand** by exploring a filesystem
2. **Write code to call tools** instead of direct tool calls
3. **Process data in the execution environment** before returning results
4. **Load only the tools needed** for the current task

## Architecture Principles

### 1. Progressive Disclosure

Tools are presented as code APIs on a filesystem that agents can explore:

```
servers/
├── filesystem/
│   ├── read_file.py
│   ├── write_file.py
│   └── ...
├── git/
│   ├── status.py
│   ├── commit.py
│   └── ...
└── ...
```

Agents list directories to find servers, then read specific tool files to understand their interfaces. This reduces upfront token usage by **98.7%** compared to loading all tool definitions.

### 2. Code Execution Pattern

Instead of this (direct tool calls):
```python
TOOL CALL: filesystem.read_file(path="data.csv")
     → returns 10,000 rows (loaded into context)

TOOL CALL: filesystem.write_file(path="filtered.csv", content="[all 10,000 rows]")
```

Agents write code like this:
```python
from servers.filesystem import read_file, write_file

# Read and filter in execution environment
data = read_file(path="data.csv")
rows = data['content'].split('\n')
filtered = [row for row in rows if 'pending' in row]

# Only log summary, not full data
print(f"Found {len(filtered)} pending rows")
write_file(path="filtered.csv", content='\n'.join(filtered))
```

### 3. Context Efficiency

**Benefits:**
- Only needed tool definitions load into context
- Intermediate results stay in execution environment
- Data filtering happens before returning to model
- Loops and conditionals execute without round trips

**Example savings:**
- Traditional: 150,000 tokens for 1,000 tools
- MCP: 2,000 tokens (98.7% reduction)

## Implementation Structure

### MCP Client (`mcp/client.py`)

The central orchestrator that manages servers and tool calls:

```python
from mcp import get_mcp_client

client = get_mcp_client()

# Progressive disclosure
servers = client.list_servers()  # ['filesystem', 'git', 'execution', ...]
tools = client.search_tools("file", detail_level="name_only")

# Tool execution
result = client.call_tool("filesystem", "read_file", path="example.txt")
```

### MCP Servers (`mcp/servers/`)

Each server groups related tools:

- **filesystem**: File and directory operations
- **git**: Repository management and version control
- **execution**: Code execution (Python, JavaScript, Bash)
- **api**: HTTP, GraphQL, webhook interactions
- **system**: System commands and package management

### Generated Tool Files (`servers/`)

Auto-generated files that agents can explore:

```python
# servers/filesystem/read_file.py
from typing import Dict, Any
from mcp.client import call_mcp_tool

def read_file(
    path: str,
    offset: int = 0,
    limit: int = 2000
) -> Dict[str, Any]:
    """
    Read content from a file with optional line range limits

    Parameters:
        path: Absolute or relative file path to read
        offset: Starting line number (0-based)
        limit: Maximum number of lines to read

    Returns:
        Dict[str, Any]: Tool execution result
    """
    return call_mcp_tool(
        server_name="filesystem",
        tool_name="read_file",
        path=path,
        offset=offset,
        limit=limit
    )
```

## Usage Patterns

### 1. Tool Discovery

```python
import os

# List available servers
servers = os.listdir('./servers')  # ['filesystem', 'git', 'execution', ...]

# Explore a specific server
files = os.listdir('./servers/git')  # ['status.py', 'commit.py', 'push.py', ...]

# Read tool documentation
with open('./servers/git/status.py') as f:
    print(f.read())  # See parameter types and descriptions
```

### 2. Simple Tool Usage

```python
from servers.filesystem import read_file, write_file

# Read file
content = read_file(path="config.json")
print(f"Read {content['lines_read']} lines")

# Write file
result = write_file(path="output.txt", content="Hello, World!")
print(f"Wrote {result['bytes_written']} bytes")
```

### 3. Complex Workflows

```python
from servers.git import status, commit, push
from servers.filesystem import read_file, write_file

# Check git status
git_status = status(repo_path=".")

if not git_status['clean']:
    # Add all changes and commit
    commit_result = commit(
        message="Auto-commit: Update configuration",
        add_all=True
    )

    if commit_result['success']:
        # Push to remote
        push(remote="origin")
        print("✓ Changes committed and pushed")
```

### 4. Data Processing in Execution Environment

```python
from servers.api import http
from servers.filesystem import write_file
import json

# Fetch large dataset
response = http(url="https://api.example.com/data", method="GET")

if response['success']:
    # Parse and filter in execution environment
    data = json.loads(response['body'])
    filtered = [item for item in data if item['status'] == 'active']

    # Only log summary
    print(f"Filtered {len(data)} items to {len(filtered)} active items")

    # Save processed data
    write_file(
        path="active_items.json",
        content=json.dumps(filtered, indent=2)
    )
```

## Security & Privacy

### Sandboxing

All code execution happens in controlled environments:
- **Timeouts**: Max 300 seconds per execution
- **Resource limits**: CPU and memory constraints
- **Command blacklists**: Dangerous commands blocked
- **Path validation**: Directory traversal protection

### Privacy-Preserving Operations

Sensitive data never enters the model's context:

```python
# PII stays in execution environment
from servers.filesystem import read_file
from servers.api import http

# Read sensitive data
customer_data = read_file(path="customers.csv")

# Process without exposing to model
for row in customer_data['content'].split('\n'):
    name, email, phone = row.split(',')
    http(
        url="https://api.crm.com/contacts",
        method="POST",
        body=json.dumps({"name": name, "email": email, "phone": phone})
    )

print(f"Imported {count} customers")  # Only summary logged
```

### Access Controls

- **Whitelisted commands**: Only safe system commands allowed
- **Confirmation for destructive ops**: Required for rm, delete, etc.
- **API key encryption**: Credentials stored securely
- **Audit logging**: All tool calls logged

## Performance Optimizations

### 1. Lazy Loading

Tools are only loaded when needed:
```python
# Bad: Load everything upfront
from servers import *  # Loads 100+ tools

# Good: Load on demand
from servers.git import status, commit  # Only 2 tools
```

### 2. Search Tools

Use `search_tools` for efficient discovery:
```python
from mcp import get_mcp_client

client = get_mcp_client()

# Find relevant tools
tools = client.search_tools("commit", detail_level="name_and_description")
# Returns only matching tools, not all 100+
```

### 3. Result Filtering

Filter data before returning:
```python
# Read large file
data = read_file(path="logs.txt")

# Filter in execution environment
errors = [line for line in data['content'].split('\n') if 'ERROR' in line]

# Return only what's needed
print(f"Found {len(errors)} errors")
print(errors[:10])  # First 10 only
```

## Regenerating Tool Files

When you update server definitions, regenerate the filesystem structure:

```bash
python -m mcp.generator
```

This will:
1. Scan all registered MCP servers
2. Generate individual tool files for each tool
3. Create index files for each server
4. Generate documentation

## Best Practices

### For Agent Developers

1. **Explore before loading**: List directories to find tools
2. **Load only what you need**: Import specific tools, not entire servers
3. **Filter early**: Process data in execution environment
4. **Log summaries**: Don't print full datasets
5. **Use error handling**: Wrap tool calls in try/except

### For Tool Developers

1. **Clear documentation**: Tool files include full parameter descriptions
2. **Type hints**: Use proper type annotations
3. **Sensible defaults**: Provide defaults for optional parameters
4. **Error messages**: Return clear, actionable error messages
5. **Idempotency**: Tools should be safe to call multiple times

## References

- [Anthropic MCP Blog Post](https://www.anthropic.com/news/code-execution-with-mcp)
- [MCP Specification](https://github.com/anthropics/model-context-protocol)
- [Chalice MCP Implementation](../mcp/)

## Examples

See `examples/mcp_usage.py` for complete usage examples demonstrating:
- Tool discovery patterns
- Complex workflows
- Error handling
- Privacy-preserving operations
- Performance optimizations
