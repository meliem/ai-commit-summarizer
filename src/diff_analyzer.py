"""Module for analyzing Git diffs."""

import re
import os
from typing import Dict, List, Optional, Set, Tuple
from git import Repo


class DiffAnalyzer:
    """Class for analyzing Git diffs."""

    def __init__(self, repo_path: str = None):
        """
        Initialize the diff analyzer.

        Args:
            repo_path: Path to the Git repository. If None, the current directory is used.
        """
        self.repo_path = repo_path or os.getcwd()
        self.repo = Repo(self.repo_path)

    def get_staged_diff(self) -> str:
        """
        Get the diff for staged changes.

        Returns:
            The diff text for staged changes.
        """
        return self.repo.git.diff("--cached")

    def get_unstaged_diff(self) -> str:
        """
        Get the diff for unstaged changes.

        Returns:
            The diff text for unstaged changes.
        """
        return self.repo.git.diff()

    def analyze_diff(self, diff_text: str) -> Dict:
        """
        Analyze a diff and extract information.

        Args:
            diff_text: The diff text to analyze.

        Returns:
            A dictionary with the analysis results.
        """
        lines = diff_text.split("\n")
        files_changed = 0
        additions = 0
        deletions = 0
        file_types: Set[str] = set()
        file_paths: List[str] = []

        # Regular expressions for parsing diff
        file_pattern = re.compile(r"^diff --git a/(.+) b/(.+)$")
        addition_pattern = re.compile(r"^\+[^+]")
        deletion_pattern = re.compile(r"^-[^-]")

        current_file = None

        for line in lines:
            # Match file changes
            file_match = file_pattern.match(line)
            if file_match:
                files_changed += 1
                current_file = file_match.group(2)
                file_paths.append(current_file)
                
                # Extract file extension
                _, ext = os.path.splitext(current_file)
                if ext:
                    file_types.add(ext[1:])  # Remove the dot
                
            # Count additions and deletions
            elif addition_pattern.match(line):
                additions += 1
            elif deletion_pattern.match(line):
                deletions += 1

        return {
            "files_changed": files_changed,
            "additions": additions,
            "deletions": deletions,
            "file_types": list(file_types),
            "file_paths": file_paths,
        }

    def categorize_changes(self, diff_text: str, file_paths: List[str]) -> List[str]:
        """
        Categorize the changes in the diff.

        Args:
            diff_text: The diff text to analyze.
            file_paths: List of file paths modified in the diff.

        Returns:
            A list of change categories (feat, fix, docs, etc.).
        """
        categories: Set[str] = set()
        
        # Helper function to check if any path matches a pattern
        def any_path_matches(pattern: str) -> bool:
            return any(re.search(pattern, path, re.IGNORECASE) for path in file_paths)
            
        # Check for documentation changes
        if any_path_matches(r'README|docs|\.md$|documentation|wiki'):
            categories.add('docs')
            
        # Check for test changes
        if any_path_matches(r'test|spec|\.test\.|\.spec\.'):
            categories.add('test')
            
        # Check for style changes
        if any_path_matches(r'\.css$|\.scss$|\.less$|style|theme'):
            categories.add('style')
            
        # Check for build system changes
        if any_path_matches(r'package\.json|requirements\.txt|setup\.py|Makefile|CMakeLists\.txt|webpack|build'):
            categories.add('build')
            
        # Check for CI changes
        if any_path_matches(r'\.github|\.travis|\.gitlab|\.circleci|\.jenkins|\.azure'):
            categories.add('ci')
            
        # Look for potential bug fixes in the diff content
        if re.search(r'fix|bug|issue|problem|error|crash|exception', diff_text, re.IGNORECASE):
            categories.add('fix')
            
        # Look for potential features or enhancements
        if re.search(r'feat|feature|add|new|implement', diff_text, re.IGNORECASE):
            categories.add('feat')
            
        # Look for potential refactoring
        if re.search(r'refactor|clean|improve|enhance|optimize', diff_text, re.IGNORECASE):
            categories.add('refactor')
            
        # If no specific category was identified, default to 'chore'
        if len(categories) == 0:
            categories.add('chore')
            
        return list(categories)

    def extract_modified_functions(self, diff_text: str) -> List[str]:
        """
        Extract the names of modified functions from the diff.

        Args:
            diff_text: The diff text to analyze.

        Returns:
            A list of modified function names.
        """
        functions: Set[str] = set()
        
        # Regular expressions for identifying functions in different languages
        patterns = {
            "python": r'^\+\s*def\s+([a-zA-Z0-9_]+)\s*\(',
            "javascript": r'^\+\s*(async\s+)?function\s+([a-zA-Z0-9_$]+)|^\+\s*const\s+([a-zA-Z0-9_$]+)\s*=\s*(?:async\s*)?\(|^\+\s*([a-zA-Z0-9_$]+)\s*:\s*(?:async\s*)?\(',
            "java": r'^\+\s*(public|private|protected|static)?\s+(?:\w+)\s+([a-zA-Z0-9_]+)\s*\(',
            "cpp": r'^\+\s*(?:\w+\s+)+([a-zA-Z0-9_]+)\s*\(',
        }
        
        # Process each line of the diff
        lines = diff_text.split('\n')
        for line in lines:
            # Check for Python functions
            python_match = re.search(patterns["python"], line)
            if python_match:
                functions.add(python_match.group(1))
                continue
                
            # Check for JavaScript functions
            js_match = re.search(patterns["javascript"], line)
            if js_match:
                # Check which group matched (regular function, arrow function, or method)
                func_name = next((g for g in js_match.groups() if g), None)
                if func_name:
                    functions.add(func_name)
                continue
                
            # Check for Java/C# methods
            java_match = re.search(patterns["java"], line)
            if java_match:
                functions.add(java_match.group(2))
                continue
                
            # Check for C/C++ functions
            cpp_match = re.search(patterns["cpp"], line)
            if cpp_match:
                functions.add(cpp_match.group(1))
                continue
        
        return list(functions)
