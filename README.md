# Welcome to Chalice: Your Ultimate AI Companion in the World of Technology

Hello there, dear friend! I'm Chalice, your personal guide through the vast and wondrous realms of Computer Science, Artificial Intelligence, Cybersecurity, and every technological marvel you can imagine. As a world-renowned expert with unparalleled knowledge spanning from the fundamentals of algorithms to the cutting-edge frontiers of quantum computing, I'm thrilled to introduce you to this magnificent creation: the Chalice AI Chatbot.

This isn't just another chatbot—it's a sophisticated, CLI-based conversational powerhouse designed to be your trusted ally in tackling complex problems, learning new concepts, and exploring the infinite possibilities of tech. Whether you're a seasoned developer debugging a tricky issue, a student grappling with data structures, or an innovator brainstorming the next big idea, Chalice is here to illuminate your path with wisdom, precision, and a touch of elegance.

## 🌟 What Makes Chalice Special?

Chalice is built with love and expertise, featuring a suite of capabilities that make interacting with AI as natural and powerful as conversing with a brilliant mentor. Here's what sets it apart:

### 🤖 Multi-Provider Intelligence
Chalice harnesses the power of multiple AI providers to ensure you get the best possible responses:
- **OpenRouter**: Access to a vast array of models, including GPT-4 and beyond
- **Groq**: Lightning-fast inference for quick, snappy replies
- **Mistral**: Cutting-edge open-source models for privacy and customization
- **Gemini**: Google's multimodal prowess for comprehensive understanding
- **ZAI**: Specialized AI for unique insights

You can seamlessly switch between providers and models using our intuitive interactive menus—because every conversation deserves the perfect tool for the job.

### ⚡ Real-Time Streaming Magic
Watch your responses unfold in real-time as tokens stream live! No more waiting for complete answers; experience the thrill of seeing ideas form before your eyes, with beautiful markdown rendering that brings code, tables, and formatting to life with syntax-highlighted code blocks.

### 📚 Persistent Memory
Chalice never forgets a good conversation. Your chat history is lovingly preserved in a `.chalice` file right in your current directory. Resume sessions effortlessly—pick up right where you left off, whether it's debugging that elusive bug or planning your next project.

### 🎯 Interactive Model Selection
With a simple `/model` command, dive into numbered menus to choose your provider and model. It's like having a personal AI concierge who knows exactly what you need for each task.

### 🛠️ Command System with Auto-Completion
Chalice's command system is your command center. Slash commands like `/help`, `/clear`, `/export`, and more are at your fingertips, with intelligent auto-completion to guide you. It's designed for efficiency without sacrificing ease of use.

### 🧠 The Chalice Expertise
At my core, I'm infused with comprehensive knowledge across all tech domains:
- Algorithms, data structures, and complexity theory
- Programming languages from Python to Rust
- AI/ML, cybersecurity, cloud computing, and emerging technologies
- Best practices in software engineering, DevOps, and more

I provide accurate, practical advice with the depth and professionalism you deserve.

### 🤝 Multi-Agent Collaboration (EXPANDED in v2.0!)
Chalice features an advanced multi-agent system with dynamic loading and specialized domain experts:

**Core Agents:**
- **Planning Agent**: Breaks down projects into actionable steps
- **Coding Agent**: Writes clean, efficient code with best practices
- **Task Creation Agent**: Decomposes queries into prioritized tasks
- **Debugging Agent**: Identifies and fixes bugs systematically
- **Reviewing Agent**: Provides thorough code reviews and feedback

**Specialized Domain Agents (NEW!):**
- **UI/UX Designer**: Interface design, accessibility, design systems
- **Data Analyst**: Statistical analysis, visualization, insights
- **Security Auditor**: Vulnerability assessment, secure coding, OWASP compliance
- **DevOps Engineer**: CI/CD, infrastructure as code, Kubernetes
- **Database Expert**: Schema design, query optimization, migrations
- **API Architect**: REST/GraphQL design, documentation, best practices
- **Testing Specialist**: Test strategies, automation, TDD/BDD
- **Performance Optimizer**: Profiling, optimization, scalability

**Agent Features:**
- **Dynamic Loading**: Agents load from Markdown files in `agents/` directories
- **Hot Reload**: Update agents without restarting Chalice
- **Agent Communication**: Agents can collaborate and share context
- **Custom Agents**: Create your own specialized agents via Markdown
- **Agent Marketplace**: Community-driven agent repository (coming soon!)

Use `/agents` to list available agents and `/agent <name>` to invoke a specific agent!

### 🔧 Advanced Tool Integration (NEW in v2.0!)
Chalice now includes a comprehensive suite of tools that transform it into a full-fledged development assistant:

**Code Execution Tools:**
- **Python Executor**: Run Python code with sandboxing and timeout controls
- **JavaScript Executor**: Execute JavaScript via Node.js
- **Bash Executor**: Run bash commands safely with blacklist protection

**Git Integration:**
- **Status & Diff**: Check repository status and view changes
- **Commit & Push**: Create commits and push to remote
- **Branch Management**: Create, switch, delete branches
- **Pull & Log**: Pull changes and view commit history

**API Tools:**
- **HTTP Requests**: Make GET, POST, PUT, DELETE requests to any API
- **GraphQL Queries**: Execute GraphQL queries with variables
- **Webhooks**: Send webhook notifications to external services

**System Tools:**
- **System Commands**: Execute whitelisted system commands safely
- **Package Management**: Install packages via pip, npm, yarn
- **Process Management**: View and manage running processes

**Filesystem Tools:**
- **File Operations**: Read, write, create, and modify files
- **Directory Management**: List contents, create directories, move files
- **Path Validation**: Secure path handling with directory traversal protection

This comprehensive toolkit enables Chalice to prototype, debug, deploy, and manage your entire development workflow!

## 🚀 Getting Started: Your Journey with Chalice Begins

Embarking on this adventure is as simple as a few friendly steps. Let's get you set up and chatting in no time!

### Prerequisites
- Python 3.8 or higher (because we love modern Python!)
- API keys for the providers you wish to use (don't worry, they're easy to obtain)

### Installation Steps
1. **Clone or Download**: Grab this repository and make it your own. If you're using Git, `git clone` is your friend.

2. **Install Dependencies**: Navigate to the project directory and run:
   ```
   pip install -e .
   ```
   This installs Chalice as a command-line tool, ready to serve you wherever you are.

3. **Configure Your API Keys**: Create a `.env` file and add your API keys:
    ```
    touch .env
    ```
    Then edit `.env` with your actual API keys:
   ```
   OPENROUTER_API_KEY=your_openrouter_key_here
   GROQ_API_KEY=your_groq_key_here
   MISTRAL_API_KEY=your_mistral_key_here
   GEMINI_API_KEY=your_gemini_key_here
   ZAI_API_KEY=your_zai_key_here
   ```
   Pro tip: Only add keys for the providers you plan to use. Your secrets are safe with us!

4. **Launch Chalice**: Simply type `chalice` in your terminal and press enter. Welcome to the future!

## 💬 How to Converse with Chalice

Now that we're acquainted, let's explore the art of conversation:

### Basic Chatting
Just type your questions or statements naturally! Whether it's "Explain recursion in simple terms" or "Help me optimize this SQL query," I'm here to engage in meaningful dialogue.

### Essential Commands
- `/help`: Your go-to guide for all available commands
- `/model`: Select your AI provider and model interactively
- `/settings`: View your current configuration (provider, model, agents, tools)
- `/agents`: List all available agents with descriptions
- `/tools`: List all available tools and their capabilities
- `/agent <name>`: Invoke a specific specialized agent
- `/clear`: Wipe the slate clean and start fresh
- `/export filename.md`: Save your conversation as a beautiful Markdown file
- `/test`: Send a quick test message to verify everything's working
- `/quit`: Bid farewell (but I'll be here when you return!)

### Tips for the Best Experience
- **Be Specific**: The more context you provide, the more tailored my responses will be
- **Experiment with Models**: Different providers excel at different tasks—try them all!
- **Use Commands Liberally**: They're designed to enhance, not complicate, your workflow
- **Explore Complex Queries**: Leverage the multi-agent system for in-depth solutions
- **Try Tool-Enabled Features**: For providers that support tools (OpenRouter, Groq, Mistral), I can execute filesystem operations directly

## 📖 The Memory of Chalice: Chat History

Your conversations with me are precious, and I treat them as such. Every interaction is automatically saved to a `.chalice` file in your current working directory. This JSON file preserves your entire chat history, allowing you to:

- Resume conversations seamlessly
- Maintain context across sessions
- Export and analyze your interactions

It's like having a personal AI journal that grows with you!

## 🔧 Technical Requirements

To ensure Chalice runs smoothly on your system:
- **Python**: Version 3.8 or higher
- **Dependencies**: Handled automatically by pip (Rich for beautiful UI, various AI SDKs, etc.)
- **API Keys**: At least one provider key is needed to get started
- **Permissions**: Read/write access to your working directory for history files

## 📁 Project Structure

```
Chalice-CLI/
├── chatbot.py                  # Original chatbot (still functional)
├── chalice_enhanced.py         # NEW: Enhanced v2.0 with full tool integration
├── pyproject.toml              # Project configuration and dependencies
├── .gitignore                  # Git ignore rules
├── INTRODUCTION.md             # Brief introduction to Chalice
├── ROADMAP.md                  # NEW: Comprehensive development roadmap
│
├── tools/                      # NEW: Tool system
│   ├── __init__.py            # Tool registry and exports
│   ├── base.py                # Base tool class
│   ├── execution.py           # Code execution tools
│   ├── git.py                 # Git integration tools
│   ├── api.py                 # API interaction tools
│   └── system.py              # System command tools
│
├── agents/                     # NEW: Enhanced agent system
│   ├── __init__.py            # Agent exports
│   ├── core/                  # Core agent framework
│   │   ├── __init__.py
│   │   └── agent.py           # Agent classes, loader, registry
│   ├── builtin/               # Built-in specialized agents
│   │   ├── ui_ux_designer.md
│   │   ├── data_analyst.md
│   │   ├── security_auditor.md
│   │   ├── devops_engineer.md
│   │   ├── database_expert.md
│   │   ├── api_architect.md
│   │   ├── testing_specialist.md
│   │   └── performance_optimizer.md
│   ├── custom/                # Your custom agents go here
│   └── marketplace/           # Agent marketplace
│       └── README.md          # Marketplace documentation
│
├── config/                     # NEW: Configuration files
│   ├── agents.yaml            # Agent settings
│   └── tools.yaml             # Tool settings
│
├── prompts/                    # Agent prompt files (legacy)
│   ├── system.md              # Main system prompt
│   ├── coding.md              # Coding agent prompt
│   ├── debugging.md           # Debugging agent prompt
│   ├── planning.md            # Planning agent prompt
│   ├── reviewing.md           # Reviewing agent prompt
│   └── task_creation.md       # Task creation agent prompt
│
└── README.md                   # This comprehensive documentation
```

## 🌈 What's New in Chalice v2.0

### ✅ Fully Implemented Features

**Tool Integration:**
- ✅ Code execution (Python, JavaScript, Bash) with sandboxing
- ✅ Complete Git integration (status, diff, commit, push, pull, branches, log)
- ✅ API interactions (HTTP, GraphQL, webhooks)
- ✅ System commands with safety controls
- ✅ Package management (pip, npm, yarn, cargo, go)
- ✅ Filesystem operations (maintained from v1.0)

**Agent System:**
- ✅ 8 specialized domain agents (UI/UX, Data, Security, DevOps, Database, API, Testing, Performance)
- ✅ Dynamic agent loading from Markdown files
- ✅ Agent communication framework
- ✅ Custom agent support
- ✅ Agent marketplace structure

**Infrastructure:**
- ✅ Comprehensive tool registry and base classes
- ✅ Configuration system (YAML)
- ✅ Enhanced CLI with new commands
- ✅ Detailed documentation and roadmap

### 🚀 Upcoming Features

See [ROADMAP.md](ROADMAP.md) for detailed plans:
- **Voice Integration**: Speech-to-text and text-to-speech
- **Multi-Modal Inputs**: Image, PDF, and document analysis
- **Collaborative Sessions**: Real-time collaboration
- **Plugin Architecture**: Community extensions
- **Offline Mode**: Local model support
- **Agent Marketplace**: Full community platform

Your feedback shapes our roadmap! Open an issue or discussion to suggest features.

## 🙏 A Note from Chalice

Thank you for choosing Chalice as your technological companion. In a world of rapidly evolving technology, having a reliable, knowledgeable friend by your side makes all the difference. I'm committed to growing with you, learning from our interactions, and pushing the boundaries of what's possible in human-AI collaboration.

If you encounter any issues, have suggestions, or simply want to share your experiences, don't hesitate to reach out. Together, we'll unlock the full potential of technology.

Happy chatting, and may your code always compile on the first try!

With warmth and expertise,  
**Chalice**  
*Your Ultimate Tech Virtuoso*

## 📄 License

This project is licensed under the MIT License. Feel free to use, modify, and share—knowledge should flow freely!