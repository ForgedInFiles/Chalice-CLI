# Chalice Agent Marketplace

Welcome to the Chalice Agent Marketplace! This is a community-driven collection of specialized AI agents that extend Chalice's capabilities.

## What is the Agent Marketplace?

The marketplace allows developers to:
- **Discover** specialized agents for specific tasks
- **Share** their own custom agents with the community
- **Install** agents with a simple command
- **Rate and review** agents to help others find the best ones

## Installing Agents from the Marketplace

To install an agent from the marketplace, use the `/agent install` command:

```
/agent install agent-name
```

Or manually download the agent `.md` file to your `agents/custom/` directory.

## Creating Your Own Agent

Creating an agent is simple! Just create a Markdown file with the following structure:

```markdown
# Agent: Your Agent Name

**Version**: 1.0.0
**Description**: Brief description of what your agent does
**Author**: Your Name
**Tags**: tag1, tag2, tag3

## Capabilities

- List of things your agent can do
- Another capability
- And another

## System Prompt

Your detailed system prompt here. This is what tells the AI how to behave as this agent.
Include:
- Domain expertise
- Tools and frameworks
- Best practices
- How to help users
- Examples of interactions

## Examples

**Example 1: Title**
User: "Example query"
Agent: "Example response..."
```

## Submitting to the Marketplace

1. Create your agent following the format above
2. Test it thoroughly with Chalice
3. Submit a pull request to the [Agent Marketplace Repository](https://github.com/chalice-ai/agent-marketplace)
4. Include a README with usage examples
5. Add appropriate tags and metadata

## Agent Categories

- **Development**: Coding, debugging, reviewing
- **Design**: UI/UX, graphics, branding
- **Data**: Analytics, ML, statistics
- **Security**: Auditing, pentesting, compliance
- **DevOps**: CI/CD, infrastructure, monitoring
- **Content**: Writing, documentation, translation
- **Domain-Specific**: Finance, healthcare, legal, etc.

## Featured Agents

### Built-in Agents

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

## Community Guidelines

When creating agents:
1. **Be Specific**: Focus on a clear, well-defined domain
2. **Be Helpful**: Include examples and clear instructions
3. **Be Ethical**: Follow responsible AI practices
4. **Be Professional**: Maintain high-quality standards
5. **Be Collaborative**: Accept feedback and iterate

## Agent Ratings

Agents are rated on:
- **Usefulness** (1-5 stars)
- **Accuracy** (1-5 stars)
- **Documentation** (1-5 stars)
- **Reliability** (1-5 stars)

## Support

- Report issues: [GitHub Issues](https://github.com/chalice-ai/agent-marketplace/issues)
- Request agents: [Feature Requests](https://github.com/chalice-ai/agent-marketplace/discussions)
- Share feedback: [Discussions](https://github.com/chalice-ai/agent-marketplace/discussions)

## License

All marketplace agents are MIT licensed unless otherwise specified.

---

**Happy agent building!** 🎉
