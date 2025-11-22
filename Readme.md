# 🌐 Browser Agent

[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-orange.svg)](LICENSE)

> **An AI-powered automation tool that controls web browsers through natural language commands**

<a href="https://www.youtube.com/watch?v=Xp3w5H4-pOw" target="_blank">
      <img src="https://img.youtube.com/vi/Xp3w5H4-pOw/maxresdefault.jpg" alt="AI Browser Navigation Demo" width="700" height="400" />
   </a>
   <p><em>Click the image above to watch the demo video</em></p>

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Contributing](#contributing)
- [License](#license)

## 🔍 Overview

Browser Agent is a sophisticated Python application that enables users to control web browsers through natural language instructions. It uses a combination of AI models, browser automation, and DOM analysis to navigate websites, fill forms, click buttons, and perform complex web tasks based on natural language descriptions.

The agent features intelligent page analysis, robust error handling, and flexible interaction capabilities, making it ideal for automating repetitive browser tasks, web scraping, site testing, and interactive browsing sessions.

<details>
<summary><strong>Why use Browser Agent?</strong></summary>

- **Simplify Web Automation** - No more complex automation scripts or browser extensions
- **Reduce Learning Curve** - Use natural language instead of programming syntax
- **Improve Productivity** - Automate repetitive web tasks with minimal effort
- **Enhance Accessibility** - Enable browser control for users with limited technical knowledge
- **Rapid Prototyping** - Quickly test and iterate on web workflows
</details>

## ✨ Features

- **🗣️ Natural Language Control**: Control your browser with simple human language instructions
- **🔍 Intelligent Page Analysis**: Automatic detection and mapping of interactive elements on web pages
- **🧭 Context-Aware Navigation**: Smart navigation with history tracking and state awareness
- **📝 Form Handling**: Fill forms, select options from dropdowns, and submit data seamlessly
- **⚡ Dynamic Content Support**: Handle AJAX, infinite scrolling, popups, and dynamically loaded content
- **🔄 Error Recovery**: Robust error detection and recovery strategies
- **👤 User Interaction**: Request information from the user during task execution when needed
- **🌍 Multi-Browser Support**: Connect to existing Chrome browsers or launch new instances
- **🔧 Multiple LLM Providers**: Support for OpenAI, Azure OpenAI, Groq, and Anthropic (Claude Sonnet 4.5)

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- uv (Python package manager) - **recommended** - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- Chrome browser

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/browser-agent.git
cd browser-agent

# Install dependencies (recommended: uv)
uv sync

# Install Playwright browsers
uv run playwright install chromium

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys
```

### Basic Usage

```bash
# Check system status
uv run main.py diagnose

# Launch the agent
uv run main.py run

# Run with a specific task
uv run main.py run --task "Navigate to google.com and search for 'AI news'"
```

## 📚 Documentation

Comprehensive documentation is available in the `docs/` folder:

### Getting Started

- **[Installation Guide](docs/INSTALLATION.md)** - Complete installation instructions and troubleshooting
- **[Quick Start Guide](docs/QUICK_START.md)** - Get up and running in minutes
- **[Configuration Guide](docs/CONFIGURATION.md)** - Customize the agent for your needs

### Usage and Examples

- **[CLI Reference](docs/CLI_REFERENCE.md)** - Complete command-line interface documentation
- **[Usage Examples](docs/USAGE_EXAMPLES.md)** - Real-world examples and use cases
- **[Browser Tools Reference](docs/BROWSER_TOOLS.md)** - Complete guide to available automation tools

### Advanced Topics

- **[Architecture Guide](docs/ARCHITECTURE.md)** - Technical architecture and design patterns
- **[Troubleshooting Guide](docs/TROUBLESHOOTING.md)** - Common issues and solutions

### Quick Reference

| Task               | Command                                         |
| ------------------ | ----------------------------------------------- |
| Install            | `uv sync && uv run playwright install chromium` |
| Run agent          | `uv run main.py run`                            |
| Check status       | `uv run main.py diagnose`                       |
| Get help           | `uv run main.py help`                           |
| View configuration | `uv run main.py config get`                     |

## 💼 Use Cases

- **Web Automation**: Automate repetitive web tasks
- **Site Testing**: Test web applications with natural language
- **Data Collection**: Extract information from websites
- **Interactive Assistance**: Guide users through complex processes
- **Research Tasks**: Gather and analyze information from multiple sources

## ⚠️ Limitations

- Cannot handle CAPTCHA or complex authentication challenges
- May face challenges with highly dynamic web applications
- Not designed for high-security operations (banking, etc.)
- Performance depends on website complexity and instructions

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  Made with ❤️ by rkvalandasu
</p>
