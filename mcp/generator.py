"""
MCP Tool Discovery Generator
Generates filesystem-based tool discovery structure following Anthropic's MCP best practices

This creates a servers/ directory that agents can explore to discover tools on-demand,
implementing the progressive disclosure pattern from the MCP blog post.
"""
from pathlib import Path
from typing import Dict, Any, List
import json


def generate_tool_file(server_name: str, tool_name: str, tool_info: Dict[str, Any]) -> str:
    """
    Generate a Python tool file following TypeScript-style interface pattern

    Example structure from Anthropic blog:
    ```typescript
    interface GetDocumentInput {
      documentId: string;
    }

    interface GetDocumentResponse {
      content: string;
    }

    /* Read a document from Google Drive */
    export async function getDocument(input: GetDocumentInput): Promise<GetDocumentResponse> {
      return callMCPTool<GetDocumentResponse>('google_drive__get_document', input);
    }
    ```
    """
    description = tool_info.get('description', '')
    parameters = tool_info.get('parameters', {})

    # Extract parameter types
    props = parameters.get('properties', {})
    required = parameters.get('required', [])

    # Generate type hints for parameters
    param_hints = []
    for param_name, param_info in props.items():
        param_type = param_info.get('type', 'Any')
        type_map = {
            'string': 'str',
            'integer': 'int',
            'boolean': 'bool',
            'object': 'Dict[str, Any]',
            'array': 'List[Any]'
        }
        py_type = type_map.get(param_type, 'Any')

        if param_name not in required:
            default_val = param_info.get('default', 'None')
            if isinstance(default_val, str) and default_val not in ['None', 'True', 'False']:
                default_val = f'"{default_val}"'
            param_hints.append(f"    {param_name}: {py_type} = {default_val}")
        else:
            param_hints.append(f"    {param_name}: {py_type}")

    param_str = ',\n'.join(param_hints) if param_hints else '    **kwargs: Any'

    # Generate the file content
    content = f'''"""
{description}

This tool is part of the {server_name} MCP server.
"""
from typing import Dict, Any, List, Optional
from mcp.client import call_mcp_tool


def {tool_name}(
{param_str}
) -> Dict[str, Any]:
    """
    {description}

    Parameters:
{chr(10).join(f"        {name}: {info.get('description', '')}" for name, info in props.items())}

    Returns:
        Dict[str, Any]: Tool execution result
    """
    params = {{k: v for k, v in locals().items() if v is not None and k != 'kwargs'}}
    if 'kwargs' in locals():
        params.update(kwargs)

    return call_mcp_tool(
        server_name="{server_name}",
        tool_name="{tool_name}",
        **params
    )
'''
    return content


def generate_server_index(server_name: str, tools: List[str]) -> str:
    """Generate the index file for a server"""
    imports = [f"from .{tool} import {tool}" for tool in tools]
    exports = ', '.join([f'"{tool}"' for tool in tools])

    content = f'''"""
{server_name.title()} MCP Server
Auto-generated index for tool discovery
"""
{chr(10).join(imports)}

__all__ = [{exports}]
'''
    return content


def generate_mcp_filesystem_structure(output_dir: Path, client):
    """
    Generate the filesystem-based tool discovery structure

    Creates a servers/ directory that agents can explore:
    ```
    servers/
    ├── filesystem/
    │   ├── __init__.py
    │   ├── read_file.py
    │   ├── write_file.py
    │   └── ...
    ├── git/
    │   ├── __init__.py
    │   ├── status.py
    │   ├── commit.py
    │   └── ...
    └── ...
    ```
    """
    servers_dir = output_dir / "servers"
    servers_dir.mkdir(exist_ok=True)

    # Generate for each server
    for server_name in client.list_servers():
        server = client.get_server(server_name)
        server_dir = servers_dir / server_name
        server_dir.mkdir(exist_ok=True)

        tools_generated = []

        # Generate each tool file
        for tool_name in server.list_tools():
            tool_def = client.get_tool_definition(server_name, tool_name)

            # Generate tool file
            tool_content = generate_tool_file(server_name, tool_name, tool_def)
            tool_file = server_dir / f"{tool_name}.py"
            tool_file.write_text(tool_content)

            tools_generated.append(tool_name)

        # Generate server index
        index_content = generate_server_index(server_name, tools_generated)
        index_file = server_dir / "__init__.py"
        index_file.write_text(index_content)

    # Generate top-level index
    top_level_index = servers_dir / "__init__.py"
    server_names = client.list_servers()
    top_content = f'''"""
Chalice MCP Servers
Auto-generated for progressive tool discovery
"""
# Import all servers
{chr(10).join(f"from . import {name}" for name in server_names)}

__all__ = [{', '.join(f'"{name}"' for name in server_names)}]
'''
    top_level_index.write_text(top_content)

    print(f"✓ Generated MCP filesystem structure in {servers_dir}")
    print(f"  - {len(server_names)} servers")
    total_tools = sum(len(client.get_server(name).tools) for name in server_names)
    print(f"  - {total_tools} total tools")


def generate_readme(output_dir: Path, client):
    """Generate README for the servers directory"""
    servers_dir = output_dir / "servers"
    readme = servers_dir / "README.md"

    content = """# Chalice MCP Servers

This directory contains auto-generated tool discovery files following Anthropic's MCP best practices.

## Structure

Each server is a directory containing individual tool files:

```
servers/
├── filesystem/       # File and directory operations
├── git/             # Git repository management
├── execution/       # Code execution (Python, JavaScript, Bash)
├── api/             # HTTP, GraphQL, webhook interactions
└── system/          # System commands and package management
```

## Usage Pattern

Agents can explore this filesystem to discover tools on-demand:

```python
# List available servers
import os
servers = os.listdir('./servers')

# Explore a specific server
from servers.filesystem import read_file, write_file

# Use tools in code
content = read_file(path="example.txt")
write_file(path="output.txt", content=content['content'])
```

## Progressive Disclosure

This structure implements the progressive disclosure pattern from Anthropic's MCP blog:
- Agents don't need to load all tool definitions upfront
- Tools are discovered by exploring the filesystem
- Only needed tools are loaded into context
- Reduces token usage by 90%+ for large tool sets

## Auto-Generation

This structure is auto-generated from the MCP server definitions.
Run `python -m mcp.generator` to regenerate after changes.
"""

    # Add server details
    content += "\n## Available Servers\n\n"
    for server_name in client.list_servers():
        server = client.get_server(server_name)
        tools = server.list_tools()
        content += f"### {server_name.title()}\n\n"
        content += f"{server.description}\n\n"
        content += f"**Tools ({len(tools)}):**\n"
        for tool_name in tools:
            tool = server.get_tool(tool_name)
            content += f"- `{tool_name}`: {tool.description}\n"
        content += "\n"

    readme.write_text(content)
    print(f"✓ Generated README in {readme}")


if __name__ == "__main__":
    from mcp import initialize_mcp_servers

    # Initialize all servers
    client = initialize_mcp_servers()

    # Generate filesystem structure
    output_dir = Path(__file__).parent.parent
    generate_mcp_filesystem_structure(output_dir, client)
    generate_readme(output_dir, client)

    print("\n✓ MCP filesystem structure generated successfully!")
    print("Agents can now discover tools by exploring the servers/ directory")
