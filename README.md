# AI Commit Summarizer

A command-line tool that analyzes code changes (git diff) and automatically generates clear and structured commit messages in natural language.

## 🎯 Problem Solved

Commit messages are often neglected or uninformative, making Git history difficult to understand. This tool helps developers generate meaningful commit messages with no extra effort.

## 💡 Features

- **Semantic Analysis**: Understanding the context of modifications to generate relevant messages
- **Customization**: Ability to choose the message style (conventional, descriptive, etc.)
- **Multilingual Support**: Message generation in different languages
- **Easy Integration**: Compatible with existing Git workflows

## 🚀 Installation

```bash
pip install -e .
```

## 📋 Usage

```bash
# Generate a commit message from staged changes
git-commit-summarizer

# Specify a message style
git-commit-summarizer --style conventional

# Generate a message in a specific language
git-commit-summarizer --lang en

# Create a commit directly with the generated message
git-commit-summarizer --commit
```

## 🔧 Development

### Prerequisites

- Python 3.8+
- Git

### Installation for Development

```bash
git clone https://github.com/meliem/ai-commit-summarizer.git
cd ai-commit-summarizer
pip install -e ".[dev]"
```

## 📄 License

MIT
