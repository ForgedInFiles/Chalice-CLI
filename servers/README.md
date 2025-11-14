# Chalice MCP Servers

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

## Available Servers

### Filesystem

File and directory operations with secure path handling

**Tools (7):**
- `read_file`: Read content from a file with optional line range limits
- `write_file`: Write or overwrite content to a file
- `list_directory`: List all files and subdirectories in a given path with their types and sizes
- `create_directory`: Create a new directory and any necessary parent directories
- `delete_path`: Delete a file or directory (recursive for directories)
- `move_path`: Move or rename a file or directory
- `file_exists`: Check if a path exists and return its type and metadata

### Git

Git repository management and version control operations

**Tools (7):**
- `status`: Get the status of the current git repository
- `diff`: View git diff for staged or unstaged changes
- `commit`: Create a git commit with the specified message
- `branch`: List, create, switch, or delete git branches
- `push`: Push commits to remote repository
- `pull`: Pull changes from remote repository
- `log`: View git commit history

### Execution

Code execution with sandboxing for Python, JavaScript, and Bash

**Tools (3):**
- `python`: Execute Python code in a sandboxed environment with timeout and resource controls
- `javascript`: Execute JavaScript code using Node.js with timeout controls
- `bash`: Execute Bash commands with safety controls and timeout

### Api

HTTP, GraphQL, and webhook interactions with external services

**Tools (3):**
- `http`: Make HTTP requests (GET, POST, PUT, DELETE, PATCH) to external APIs
- `graphql`: Execute GraphQL queries against a GraphQL endpoint
- `webhook`: Send webhook notifications to external services

### System

System commands, package management, and process operations

**Tools (3):**
- `command`: Execute whitelisted system commands safely with output capture
- `packages`: Install, update, or list packages using pip, npm, yarn, cargo, or go
- `processes`: List or find running processes

### Multimodal

Multi-modal input processing including images, PDFs, documents, and diagrams

**Tools (5):**
- `analyze_image`: Analyze images using GPT-4 Vision or Claude 3 Opus with vision capabilities
- `parse_pdf`: Extract text, metadata, and structure from PDF files
- `summarize_document`: Generate intelligent summaries of text documents
- `interpret_diagram`: Analyze and interpret diagrams, charts, flowcharts, and visual data
- `extract_code_from_screenshot`: Extract and format code from screenshot images

