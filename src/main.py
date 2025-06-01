"""Main module for the AI Commit Summarizer."""

from typing import Dict, List, Optional
import os

from .diff_analyzer import DiffAnalyzer
from .message_generator import MessageGenerator
from .config import Config


class CommitSummarizer:
    """Main class for summarizing Git commits."""

    def __init__(self, repo_path: str = None, model_name: str = None, language: str = None):
        """
        Initialize the commit summarizer.

        Args:
            repo_path: Path to the Git repository.
            model_name: Name of the model to use for message generation.
            language: Language to use for messages.
        """
        self.repo_path = repo_path or os.getcwd()
        self.diff_analyzer = DiffAnalyzer(self.repo_path)
        self.message_generator = MessageGenerator(model_name, language)
        self.language = language or Config.DEFAULT_LANGUAGE

    def summarize_staged_changes(self) -> Dict:
        """
        Summarize staged changes in the repository.

        Returns:
            Dictionary with summary information.
        """
        # Get the diff for staged changes
        diff_text = self.diff_analyzer.get_staged_diff()
        
        if not diff_text.strip():
            return {"error": "No staged changes found"}
        
        # Analyze the diff
        diff_analysis = self.diff_analyzer.analyze_diff(diff_text)
        
        # Categorize the changes
        categories = self.diff_analyzer.categorize_changes(diff_text, diff_analysis.get("file_paths", []))
        
        # Extract modified functions
        functions = self.diff_analyzer.extract_modified_functions(diff_text)
        
        return {
            "diff_text": diff_text,
            "diff_analysis": diff_analysis,
            "categories": categories,
            "functions": functions,
        }

    def summarize_unstaged_changes(self) -> Dict:
        """
        Summarize unstaged changes in the repository.

        Returns:
            Dictionary with summary information.
        """
        # Get the diff for unstaged changes
        diff_text = self.diff_analyzer.get_unstaged_diff()
        
        if not diff_text.strip():
            return {"error": "No unstaged changes found"}
        
        # Analyze the diff
        diff_analysis = self.diff_analyzer.analyze_diff(diff_text)
        
        # Categorize the changes
        categories = self.diff_analyzer.categorize_changes(diff_text, diff_analysis.get("file_paths", []))
        
        # Extract modified functions
        functions = self.diff_analyzer.extract_modified_functions(diff_text)
        
        return {
            "diff_text": diff_text,
            "diff_analysis": diff_analysis,
            "categories": categories,
            "functions": functions,
        }

    def get_commit_message(self, staged: bool = True, style: str = "descriptive") -> Dict:
        """
        Get a commit message for the current changes.

        Args:
            staged: Whether to analyze staged or unstaged changes.
            style: Message style to generate (conventional, descriptive, ai).

        Returns:
            Dictionary with commit message and analysis results.
        """
        # Get the summary for staged or unstaged changes
        if staged:
            summary = self.summarize_staged_changes()
        else:
            summary = self.summarize_unstaged_changes()
        
        # Check if there was an error
        if "error" in summary:
            return {"error": summary["error"]}
        
        # Generate a commit message
        diff_text = summary["diff_text"]
        diff_analysis = summary["diff_analysis"]
        categories = summary["categories"]
        functions = summary.get("functions", [])
        
        message = self.message_generator.generate_ai_commit_message(
            diff_text, diff_analysis, categories, style, functions
        )
        
        # Translate the message if needed (if language is not English)
        if self.language != "en":
            message = self.message_generator.translate_message(message, self.language)
        
        # Return the commit message along with the analysis results
        return {
            "commit_message": message,
            "diff_analysis": diff_analysis,
            "categories": categories,
            "functions": functions,
        }
