"""Module for generating commit messages from diff analysis."""

from typing import Dict, List, Optional
import os
import importlib.util
import json

from .config import Config

# Check if transformers is available for local models
HAS_TRANSFORMERS = importlib.util.find_spec("transformers") is not None

# Check if OpenAI is available
HAS_OPENAI = importlib.util.find_spec("openai") is not None


class MessageGenerator:
    """Class for generating commit messages from diff analysis."""

    def __init__(self, model_name: str = None, lang: str = None):
        """
        Initialize the message generator.

        Args:
            model_name: Name of the model to use for text generation.
            lang: Language in which to generate messages (en, fr, es, etc.).
        """
        self.model_name = model_name or Config.OPENAI_MODEL
        self.lang = lang or Config.DEFAULT_LANGUAGE
        self.generator = None
        self.openai_client = None

    def _ensure_openai_client_loaded(self):
        """Ensure that the OpenAI client is loaded before use."""
        if not HAS_OPENAI:
            return False
            
        if self.openai_client is None and Config.has_openai_key():
            try:
                import openai
                self.openai_client = openai.OpenAI(api_key=Config.OPENAI_API_KEY)
                return True
            except Exception as e:
                print(f"Warning: Unable to load OpenAI client: {str(e)}")
                print("Using rule-based mode instead.")
                self.openai_client = False
                return False
        
        return self.openai_client is not False

    def _ensure_model_loaded(self):
        """Ensure that the local model is loaded before use."""
        if self.generator is None and HAS_TRANSFORMERS:
            try:
                from transformers import pipeline
                self.generator = pipeline('text-generation', model=self.model_name)
                return True
            except Exception as e:
                print(f"Warning: Unable to load model: {str(e)}")
                print("Using rule-based mode instead.")
                self.generator = False
                return False
        
        return self.generator is not False

    def _get_commit_type(self, categories: List[str]) -> str:
        """
        Determine the commit type based on the categories of changes.

        Args:
            categories: List of change categories.

        Returns:
            The commit type (feat, fix, docs, etc.).
        """
        # Priority order of commit types
        priority_order = ['fix', 'feat', 'test', 'docs', 'style', 'refactor', 'perf', 'build', 'ci', 'chore']
        
        for type_name in priority_order:
            if type_name in categories:
                return type_name
                
        # Default
        return 'feat'

    def generate_conventional_commit(self, diff_analysis: Dict, categories: List[str]) -> str:
        """
        Generate a commit message in conventional format.

        Args:
            diff_analysis: Result of the diff analysis.
            categories: List of change categories.

        Returns:
            Commit message in conventional format.
        """
        commit_type = self._get_commit_type(categories)
        
        # Build a description based on the modified files
        file_types = diff_analysis['file_types']
        files_changed = diff_analysis['files_changed']
        
        description = ""
        if 'python' in file_types or 'py' in file_types:
            description = "update Python code"
        elif 'js' in file_types or 'ts' in file_types:
            description = "update JavaScript/TypeScript code"
        elif 'css' in file_types or 'scss' in file_types:
            description = "update styles"
        elif 'html' in file_types:
            description = "update HTML templates"
        else:
            description = f"update {files_changed} file(s)"
            
        # Format: type(scope): description
        # No scope for now
        conventional_message = f"{commit_type}: {description}"
        
        return conventional_message

    def generate_descriptive_commit(self, diff_analysis: Dict, categories: List[str], 
                                   functions: List[str] = None) -> str:
        """
        Generate a descriptive commit message.

        Args:
            diff_analysis: Result of the diff analysis.
            categories: List of change categories.
            functions: List of modified functions.

        Returns:
            Descriptive commit message.
        """
        commit_type = self._get_commit_type(categories)
        
        # Basic statistics
        files_changed = diff_analysis['files_changed']
        additions = diff_analysis['additions']
        deletions = diff_analysis['deletions']
        
        # Build the descriptive message
        if commit_type == 'feat':
            prefix = "Add"
        elif commit_type == 'fix':
            prefix = "Fix"
        elif commit_type == 'refactor':
            prefix = "Refactor"
        elif commit_type == 'docs':
            prefix = "Document"
        elif commit_type == 'test':
            prefix = "Test"
        else:
            prefix = "Update"
            
        description = f"{prefix} "
        
        # Add details about functions if available
        if functions and len(functions) > 0:
            if len(functions) == 1:
                description += f"function {functions[0]}"
            else:
                description += f"functions {', '.join(functions[:3])}"
                if len(functions) > 3:
                    description += f" and {len(functions) - 3} others"
        else:
            # Otherwise, description based on files
            if files_changed == 1:
                description += "one file"
            else:
                description += f"{files_changed} files"
                
        # Add statistics
        stats = f" ({additions}+ {deletions}-)"
        
        return description + stats

    def generate_openai_commit(self, diff_text: str, diff_analysis: Dict, 
                              categories: List[str], functions: List[str] = None) -> str:
        """
        Generate a commit message using OpenAI.

        Args:
            diff_text: Raw diff text.
            diff_analysis: Result of the diff analysis.
            categories: List of change categories.
            functions: List of modified functions.

        Returns:
            AI-generated commit message.
        """
        if not self._ensure_openai_client_loaded():
            return None

        # Create a prompt for the OpenAI API
        prompt = self._create_openai_prompt(diff_text, diff_analysis, categories, functions)
        
        try:
            # Call the OpenAI API
            response = self.openai_client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a Git commit message writer assistant. Your job is to create clear, concise, and informative commit messages based on the code changes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=100,
                temperature=0.5
            )
            
            # Extract the message from the response
            message = response.choices[0].message.content.strip()
            
            # Clean up the message (remove quotes if any)
            if message.startswith('"') and message.endswith('"'):
                message = message[1:-1]
                
            return message
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return None

    def _create_openai_prompt(self, diff_text: str, diff_analysis: Dict, 
                             categories: List[str], functions: List[str] = None) -> str:
        """
        Create a prompt for the OpenAI API.

        Args:
            diff_text: Raw diff text.
            diff_analysis: Result of the diff analysis.
            categories: List of change categories.
            functions: List of modified functions.

        Returns:
            Prompt for the OpenAI API.
        """
        # Extract key information to include in the prompt
        files_changed = diff_analysis['files_changed']
        additions = diff_analysis['additions']
        deletions = diff_analysis['deletions']
        file_types = diff_analysis.get('file_types', [])
        
        # Limit the diff text to avoid exceeding token limits
        max_diff_length = 2000
        short_diff = diff_text[:max_diff_length]
        if len(diff_text) > max_diff_length:
            short_diff += "\n... (diff truncated)"
        
        # Create a structured prompt
        prompt = f"""Generate a concise and informative Git commit message based on the following code changes:

DIFF SUMMARY:
- Files changed: {files_changed}
- Lines added: {additions}
- Lines deleted: {deletions}
- File types: {', '.join(file_types) if file_types else 'N/A'}
- Categories: {', '.join(categories) if categories else 'N/A'}
"""

        if functions and len(functions) > 0:
            prompt += f"- Modified functions: {', '.join(functions[:5])}"
            if len(functions) > 5:
                prompt += f" and {len(functions) - 5} others"
            prompt += "\n"
        
        prompt += f"""
DIFF DETAILS:
{short_diff}

Please generate a concise commit message that clearly explains the purpose and impact of these changes. 
If it's a feature, explain what was added. If it's a bug fix, explain what was fixed.
If it's a refactor, explain what was improved.

The message should be:
1. Informative but concise (50-75 characters for the subject line)
2. In the present tense (e.g., "Add feature" not "Added feature")
3. In English

If appropriate, use the conventional commit format (type: description).
"""
        
        return prompt

    def generate_ai_commit_message(self, diff_text: str, diff_analysis: Dict, 
                                  categories: List[str], style: str = "descriptive", 
                                  functions: List[str] = None) -> str:
        """
        Generate an intelligent commit message using AI.
        
        Args:
            diff_text: Raw diff text.
            diff_analysis: Result of the diff analysis.
            categories: List of change categories.
            style: Message style to generate (conventional, descriptive, ai).
            functions: List of modified functions.

        Returns:
            Generated commit message.
        """
        # Try to use OpenAI if style is 'ai' and OpenAI is available
        if style == "ai" and HAS_OPENAI and Config.has_openai_key():
            ai_message = self.generate_openai_commit(diff_text, diff_analysis, categories, functions)
            if ai_message:
                return ai_message
                
        # Try to use local transformer models if OpenAI fails or is not available
        if style == "ai" and HAS_TRANSFORMERS:
            if self._ensure_model_loaded():
                # TODO: implement text generation with local models
                # For now, fall back to descriptive style
                pass
        
        # Use rule-based approaches
        if style == "conventional":
            return self.generate_conventional_commit(diff_analysis, categories)
        
        # Descriptive style by default
        return self.generate_descriptive_commit(diff_analysis, categories, functions)

    def translate_message(self, message: str, target_lang: str) -> str:
        """
        Translate a commit message to another language.

        Args:
            message: Commit message to translate.
            target_lang: Target language (en, fr, es, etc.).

        Returns:
            Translated message.
        """
        # For an MVP, we simply return the original message
        # In a future version, we would implement a translation service
        
        # If OpenAI is available, we could use it for translation
        if HAS_OPENAI and self._ensure_openai_client_loaded() and target_lang != "en":
            try:
                response = self.openai_client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {"role": "system", "content": f"You are a translator. Translate the following Git commit message to {target_lang}."},
                        {"role": "user", "content": message}
                    ],
                    max_tokens=100,
                    temperature=0.3
                )
                
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"Error translating message: {str(e)}")
                
        return message
