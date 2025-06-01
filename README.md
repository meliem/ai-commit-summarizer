# 🧠 AI Commit Summarizer

Intelligent commit message generator for Git repositories.

## 📝 Overview

The AI Commit Summarizer is a command-line tool that automatically generates clear, structured Git commit messages based on your code changes. It analyzes the diff of your staged (or unstaged) changes and produces a human-readable message that describes what was changed and why.

## ✨ Features

- 🔍 Automatic analysis of staged and unstaged Git changes
- 📊 Categorization of changes into types (feat, fix, docs, test, etc.)
- 💻 Detection of modified functions and files
- 🌐 Support for multiple message formats:
  - Descriptive messages
  - Conventional commit messages
  - AI-powered custom messages (using OpenAI)
- 🌍 Multilingual support
- 🎨 Colorized command-line output
- 🚀 Direct commit creation option

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/meliem/ai-commit-summarizer.git
cd ai-commit-summarizer

# Install the package
pip install -e .
```

### OpenAI API Configuration

To use the AI-powered commit message generation, you need to set up an OpenAI API key:

1. Create a `.env` file in the project root directory
2. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   OPENAI_MODEL=gpt-4o-mini  # Or another model of your choice
   ```

## 📋 Usage

```bash
# Generate a commit message for staged changes
git-commit-summarizer

# Generate a commit message for unstaged changes
git-commit-summarizer --unstaged

# Generate a commit message in conventional format
git-commit-summarizer --style conventional

# Generate an AI-powered commit message
git-commit-summarizer --style ai

# Generate a commit message and commit the changes
git-commit-summarizer --commit

# Generate a commit message in a specific language
git-commit-summarizer --language fr
```

### Command-line Options

- `--style, -s`: Message style (descriptive, conventional, ai)
- `--language, -l`: Message language (en, fr, etc.)
- `--unstaged, -u`: Analyze unstaged changes
- `--commit, -c`: Create a commit with the generated message
- `--model, -m`: Specify which model to use for AI-powered generation

## 🔧 Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## 📝 Example

Here's an example of a generated commit message:

```
feat: improved user sorting performance by replacing insertion sort with quicksort algorithm
```

This was generated from code changes that replaced a sorting algorithm in the user management module.

## 📄 License

MIT
