# Chalice Agent Marketplace

Welcome to the Chalice Agent Marketplace! Discover, install, and share community-created agents.

## Features

- **🔍 Agent Discovery**: Browse and search thousands of community agents
- **📦 One-Click Install**: Install agents with a single command
- **⭐ Ratings & Reviews**: See what the community thinks
- **🔄 Version Management**: Keep your agents up to date
- **🏷️ Categories & Tags**: Find exactly what you need
- **👥 Community Driven**: Share your own agents with the world

## Quick Start

### Search for Agents

```bash
# Search all agents
python -m agents.marketplace.cli search

# Search by keyword
python -m agents.marketplace.cli search "react"

# Filter by category
python -m agents.marketplace.cli search --category frontend

# Filter by tags
python -m agents.marketplace.cli search --tags "javascript,typescript"

# Sort by rating
python -m agents.marketplace.cli search --sort rating
```

### Install an Agent

```bash
# Install by ID
python -m agents.marketplace.cli install community_react_expert

# Force reinstall
python -m agents.marketplace.cli install community_react_expert --force
```

### Get Agent Info

```bash
python -m agents.marketplace.cli info community_react_expert
```

### Leave a Review

```bash
python -m agents.marketplace.cli review community_react_expert "john_doe" 5 "Excellent agent!"
```

### List Installed Agents

```bash
python -m agents.marketplace.cli list
```

### List Categories

```bash
python -m agents.marketplace.cli list --categories
```

## Publishing Your Agent

### 1. Create Your Agent

Create a markdown file following the agent template:

```markdown
# Agent: Your Agent Name

**Version**: 1.0.0
**Description**: What your agent does
**Author**: Your Name
**Tags**: tag1, tag2, tag3
**Category**: your-category

## Capabilities

- Capability 1
- Capability 2

## System Prompt

Your detailed system prompt here...

## Examples

Your examples here...
```

### 2. Create Metadata

Create a `metadata.json` file:

```json
{
  "name": "Your Agent Name",
  "description": "What your agent does",
  "author": "Your Name",
  "version": "1.0.0",
  "category": "your-category",
  "tags": ["tag1", "tag2"],
  "capabilities": [
    "Capability 1",
    "Capability 2"
  ],
  "dependencies": []
}
```

### 3. Publish

```bash
python -m agents.marketplace.cli publish your_agent.md -m metadata.json
```

Or inline:

```bash
python -m agents.marketplace.cli publish your_agent.md \
  --name "Your Agent" \
  --description "What it does" \
  --author "Your Name" \
  --category "your-category" \
  --tags "tag1,tag2"
```

## Categories

- **frontend**: Frontend development (React, Vue, Angular)
- **backend**: Backend development (APIs, databases)
- **devops**: DevOps and infrastructure
- **data**: Data science and analytics
- **security**: Security and auditing
- **testing**: Testing and QA
- **design**: UI/UX design
- **general**: General purpose

## Programmatic Usage

```python
from agents.marketplace import get_marketplace

# Get marketplace instance
marketplace = get_marketplace()

# Search agents
results = marketplace.search_agents(
    query="react",
    category="frontend",
    min_rating=4.0
)

# Install agent
result = marketplace.install_agent("community_react_expert")
if result['success']:
    print(f"Installed to: {result['installed_path']}")

# Get agent info
agent = marketplace.get_agent("community_react_expert")
print(f"Agent: {agent.name}")
print(f"Rating: {agent.rating}")
print(f"Downloads: {agent.downloads}")

# Add review
marketplace.add_review(
    agent_id="community_react_expert",
    user="john_doe",
    rating=5,
    comment="Excellent agent!"
)

# List categories
categories = marketplace.list_categories()

# List installed
installed = marketplace.list_installed()
```

## Agent Metadata Schema

```python
{
    "id": str,              # Unique identifier (author_name)
    "name": str,            # Agent name
    "version": str,         # Semantic version (e.g., "1.0.0")
    "description": str,     # Short description
    "author": str,          # Author name
    "tags": List[str],      # Tags for discovery
    "category": str,        # Primary category
    "capabilities": List[str],  # What the agent can do
    "dependencies": List[str],  # Required tools/libraries
    "rating": float,        # Average rating (0.0-5.0)
    "downloads": int,       # Download count
    "created_at": str,      # ISO timestamp
    "updated_at": str,      # ISO timestamp
    "file_url": str,        # Download URL
    "file_hash": str        # SHA-256 hash for verification
}
```

## Built-in Agents

### Core Agents

These agents come pre-installed with Chalice:
- **Planning Agent**: Project planning and task breakdown
- **Coding Agent**: Code generation and implementation
- **Debugging Agent**: Bug identification and fixing
- **Reviewing Agent**: Code review and feedback
- **Task Creation Agent**: Task decomposition

### Specialized Agents

Available in `agents/builtin/`:
- **UI/UX Designer**: Interface and experience design
- **Data Analyst**: Data analysis and visualization
- **Security Auditor**: Security review and pentesting
- **DevOps Engineer**: Infrastructure and automation
- **Database Expert**: Database design and optimization
- **API Architect**: API design and documentation
- **Testing Specialist**: Test strategy and automation
- **Performance Optimizer**: Performance analysis and tuning

## Security

All agents are:
- **Verified**: File hashes checked on download
- **Sandboxed**: Run in isolated environments
- **Reviewed**: Community reviewed and rated
- **Transparent**: Source code visible before install

## Best Practices

1. **Clear Descriptions**: Make your agent's purpose obvious
2. **Good Examples**: Include usage examples in your agent file
3. **Semantic Versioning**: Follow semver for versions
4. **Test Thoroughly**: Test your agent before publishing
5. **Document Dependencies**: List all required tools/libraries
6. **Respond to Reviews**: Engage with the community
7. **Keep Updated**: Maintain and update your agents

## Community Guidelines

When creating agents:
1. **Be Specific**: Focus on a clear, well-defined domain
2. **Be Helpful**: Include examples and clear instructions
3. **Be Ethical**: Follow responsible AI practices
4. **Be Professional**: Maintain high-quality standards
5. **Be Collaborative**: Accept feedback and iterate

## Support

- **Issues**: [GitHub Issues](https://github.com/ForgedInFiles/Chalice-CLI/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ForgedInFiles/Chalice-CLI/discussions)
- **Documentation**: [Full Docs](../../docs/)

## Contributing

We love community contributions! See [CONTRIBUTING.md](../../CONTRIBUTING.md) for details.

---

**Happy agent building!** 🚀
