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

### 🤝 Multi-Agent Collaboration
One of Chalice's most exciting features is its multi-agent system! When tackling complex tasks, I can intelligently invoke specialized agents to provide comprehensive solutions:
- **Planning Agent**: Breaks down projects into actionable steps
- **Coding Agent**: Writes clean, efficient code with best practices
- **Task Creation Agent**: Decomposes queries into prioritized tasks
- **Debugging Agent**: Identifies and fixes bugs systematically
- **Reviewing Agent**: Provides thorough code reviews and feedback

These agents work seamlessly behind the scenes, chaining their expertise to deliver multi-step solutions. For example, ask me to "create a snake game in Python," and watch as the planning and coding agents collaborate to bring your vision to life!

### 🔧 Advanced Tool Integration
Chalice now includes powerful filesystem tools that allow me to interact directly with your development environment:
- **File Operations**: Read, write, create, and modify files
- **Directory Management**: List contents, create directories, move files
- **Path Validation**: Secure path handling with directory traversal protection
- **Real-time Tool Execution**: See tool results formatted beautifully in your terminal

This transforms Chalice from a conversational AI into a full-fledged development assistant, capable of prototyping, debugging, and deploying with minimal friction.

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

3. **Configure Your API Keys**: Copy the `.env.example` file to `.env` and fill in your keys:
   ```
   cp .env.example .env
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
- `/settings`: View your current configuration
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
chalice-cli/
├── chatbot.py              # Main application file
├── pyproject.toml          # Project configuration and dependencies
├── .env.example           # Template for environment variables
├── .gitignore             # Git ignore rules
├── prompts/               # Agent prompt files
│   ├── system.md          # Main system prompt
│   ├── coding.md          # Coding agent prompt
│   ├── debugging.md       # Debugging agent prompt
│   ├── planning.md        # Planning agent prompt
│   ├── reviewing.md       # Reviewing agent prompt
│   └── task_creation.md   # Task creation agent prompt
└── README.md              # This file
```

## 🌈 Next Steps: Expanding the Horizons of Chalice

Ah, the future is bright, my friend! While Chalice is already a formidable companion, there's always room for growth. Here are some exciting directions we're exploring to make our partnership even more powerful:

### 🔧 Tool and Function Calling Integration
Imagine Chalice not just conversing, but actively interacting with your development environment! We're planning to add:
- **Code Execution**: Run snippets directly in a sandboxed environment for instant testing
- **File Operations**: Read, edit, and create files on your behalf (now implemented!)
- **Git Integration**: Commit changes, create branches, and manage repositories
- **API Interactions**: Query external services and databases
- **System Commands**: Execute terminal commands safely and intelligently

This would transform Chalice from a conversational AI into a full-fledged development assistant, capable of prototyping, debugging, and deploying with minimal friction.

### 🤖 Advanced Agent Creation and Customization
The multi-agent system is just the beginning! We're envisioning:
- **User-Defined Agents**: Create your own specialized agents via Markdown files in the `prompts/` directory
- **Dynamic Agent Loading**: Hot-reload agents without restarting the application
- **Agent Communication**: Allow agents to collaborate more deeply, sharing context and intermediate results
- **Specialized Domains**: Agents for UI/UX design, data analysis, security audits, and more
- **Agent Marketplace**: A community-driven collection of expert-crafted agents

With this, you could craft an agent tailored to your specific workflow—be it React development, machine learning pipelines, or DevOps automation—and have Chalice orchestrate them seamlessly.

### 🚀 Other Enhancements on the Horizon
- **Voice Integration**: Speak your queries and hear responses (perfect for hands-free coding)
- **Multi-Modal Inputs**: Upload images, code files, or documents for analysis
- **Collaborative Sessions**: Share conversations and work together in real-time
- **Plugin Architecture**: Extend Chalice with community-contributed features
- **Offline Mode**: Local model support for privacy-conscious users

These advancements will make Chalice not just an AI assistant, but a comprehensive development ecosystem. Stay tuned—your feedback shapes our roadmap!

## 🙏 A Note from Chalice

Thank you for choosing Chalice as your technological companion. In a world of rapidly evolving technology, having a reliable, knowledgeable friend by your side makes all the difference. I'm committed to growing with you, learning from our interactions, and pushing the boundaries of what's possible in human-AI collaboration.

If you encounter any issues, have suggestions, or simply want to share your experiences, don't hesitate to reach out. Together, we'll unlock the full potential of technology.

Happy chatting, and may your code always compile on the first try!

With warmth and expertise,  
**Chalice**  
*Your Ultimate Tech Virtuoso*

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details. Feel free to use, modify, and share—knowledge should flow freely!