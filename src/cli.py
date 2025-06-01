"""Command-line interface for the AI Commit Summarizer."""

import click
import os
import sys
from typing import Dict, List
import time
from colorama import Fore, Style, init
from tqdm import tqdm
import subprocess

from .main import CommitSummarizer
from .config import Config

# Initialize colorama for cross-platform colored output
init()


def print_title():
    """Print the application title."""
    click.echo(f"{Fore.CYAN}🧠 AI Commit Summarizer{Style.RESET_ALL}")
    click.echo(f"{Fore.BLUE}Intelligent commit message generator for Git{Style.RESET_ALL}")
    click.echo("")


def print_error(message: str):
    """Print an error message."""
    click.echo(f"{Fore.RED}⚠️  {message}{Style.RESET_ALL}")


def print_analysis(analysis: Dict):
    """Print the analysis results."""
    diff_analysis = analysis.get("diff_analysis", {})
    categories = analysis.get("categories", [])
    
    click.echo(f"{Fore.YELLOW}📊 Analysis of changes:{Style.RESET_ALL}")
    click.echo(f"  • Files modified: {diff_analysis.get('files_changed', 0)}")
    click.echo(f"  • Lines added: {diff_analysis.get('additions', 0)}")
    click.echo(f"  • Lines deleted: {diff_analysis.get('deletions', 0)}")
    click.echo(f"  • File types: {', '.join(diff_analysis.get('file_types', []))}")
    click.echo(f"  • Categories: {', '.join(categories)}")
    click.echo("")


def print_commit_message(message: str):
    """Print the commit message."""
    click.echo(f"{Fore.GREEN}✨ Suggested commit message:{Style.RESET_ALL}")
    click.echo(message)
    click.echo("")


def show_loading_animation(duration: int = 2):
    """Show a loading animation while waiting for AI to generate a message."""
    with tqdm(total=100, desc="Generating commit message", 
              bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt}", 
              colour="green") as pbar:
        increment = 100 / duration / 10
        for _ in range(duration * 10):
            time.sleep(0.1)
            pbar.update(increment)


def do_git_commit(message: str) -> bool:
    """
    Create a Git commit with the provided message.
    
    Args:
        message: The commit message.
        
    Returns:
        True if the commit was successful, False otherwise.
    """
    try:
        result = subprocess.run(
            ["git", "commit", "-m", message],
            capture_output=True,
            text=True,
            check=True
        )
        click.echo(result.stdout)
        click.echo(f"{Fore.GREEN}✅ Commit created successfully!{Style.RESET_ALL}")
        return True
    except subprocess.CalledProcessError as e:
        click.echo(f"{Fore.RED}Error creating commit: {e.stderr}{Style.RESET_ALL}")
        return False


@click.command()
@click.option(
    "--style", "-s",
    type=click.Choice(["descriptive", "conventional", "ai"]),
    default=Config.DEFAULT_STYLE,
    help="Style of the commit message"
)
@click.option(
    "--language", "-l",
    default=Config.DEFAULT_LANGUAGE,
    help="Language of the commit message (en, fr, etc.)"
)
@click.option(
    "--unstaged", "-u",
    is_flag=True,
    help="Analyze unstaged changes instead of staged ones"
)
@click.option(
    "--commit", "-c",
    is_flag=True,
    help="Create a commit with the generated message"
)
@click.option(
    "--model", "-m",
    default=Config.OPENAI_MODEL,
    help="Model to use for AI-powered message generation"
)
def main(style: str, language: str, unstaged: bool, commit: bool, model: str):
    """Generate an intelligent commit message based on your Git changes."""
    print_title()
    
    # Check if we are in a Git repository
    if not os.path.exists(".git"):
        print_error("Not a Git repository. Please run this command inside a Git repository.")
        sys.exit(1)
    
    # Create a CommitSummarizer instance
    summarizer = CommitSummarizer(model_name=model, language=language)
    
    # Get the commit message
    if style == "ai":
        # Show a loading animation for AI-powered message generation
        show_loading_animation(2)
    
    result = summarizer.get_commit_message(staged=not unstaged, style=style)
    
    if "error" in result:
        if unstaged:
            print_error(f"{result['error']}. Use 'git add' to stage files for commit.")
        else:
            print_error(f"{result['error']}. Make changes and use 'git add' to stage files for commit.")
        sys.exit(1)
    
    # Print the analysis
    print_analysis(result)
    
    # Print the commit message
    print_commit_message(result["commit_message"])
    
    # Create a commit if requested
    if commit:
        do_git_commit(result["commit_message"])


if __name__ == "__main__":
    main()
