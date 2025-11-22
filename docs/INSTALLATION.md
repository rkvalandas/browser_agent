# 🚀 Installation Guide

This guide will help you install and set up the Browser Agent on your system.

## Prerequisites

- Python 3.11 or higher
- uv (Python package manager) - **recommended** - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- OR pip (alternative Python package manager)
- Chrome browser

## Step-by-Step Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/browser-agent.git
cd browser-agent
```

### 2. Install Dependencies

The project uses direct LLM provider SDKs (OpenAI, Anthropic, Groq, Azure) without langchain wrapper dependencies.

#### Option A: Using uv (Recommended)

```bash
uv sync
```

#### Option B: Using pip

```bash
pip install -r requirements.txt
```

### 3. Install Playwright Browsers

```bash
# With uv
uv run playwright install chromium

# With pip
playwright install chromium
```

### 4. Set Up Environment Variables

#### Option A: Using .env File

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit the `.env` file with your preferred LLM provider and API keys:

```bash
# Choose your LLM provider
LLM_PROVIDER=groq

# Set the appropriate API key
GROQ_API_KEY=your_groq_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# AZURE_OPENAI_API_KEY=your_azure_api_key_here
# ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Browser settings
BROWSER_HEADLESS=false
FAST_MODE=true
```

#### Option B: Using Environment Variables

Set them directly in your terminal:

```bash
export LLM_PROVIDER=groq
export GROQ_API_KEY=your_api_key_here
```

### 5. Verify Installation

Run a quick test to verify everything is working:

```bash
# Check version and system info
uv run main.py version
# Or: python main.py version

# Run diagnostics
uv run main.py diagnose
# Or: python main.py diagnose
```

## Troubleshooting Installation

### Python Version Issues

Make sure you're using Python 3.11 or higher:

```bash
python --version
```

### Playwright Installation Issues

If Playwright installation fails, try:

```bash
# Install system dependencies (Linux)
sudo apt-get install -y libnss3 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libgbm1 libasound2

# Install Playwright with dependencies
uv run playwright install --with-deps chromium
```

### Environment Variable Issues

Verify your environment variables are set correctly:

```bash
# Check if variables are set
echo $LLM_PROVIDER
echo $GROQ_API_KEY  # or your chosen provider's key
```

### Permission Issues

On some systems, you might need to adjust permissions:

```bash
chmod +x main.py
```

## Next Steps

Once installation is complete, check out:

- [Quick Start Guide](QUICK_START.md) - Get up and running quickly
- [LLM Providers](LLM_PROVIDERS.md) - Configure different AI providers
- [CLI Reference](CLI_REFERENCE.md) - Learn all available commands
- [Configuration](CONFIGURATION.md) - Customize the browser agent
