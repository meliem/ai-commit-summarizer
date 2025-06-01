"""Module principal pour l'AI Commit Summarizer."""

from typing import Dict, List, Optional
import os

from .diff_analyzer import DiffAnalyzer
from .message_generator import MessageGenerator


class CommitSummarizer:
    """Classe principale pour résumer les commits Git."""

    def __init__(self, repo_path: str = None, lang: str = "fr", style: str = "descriptive"):
        """
        Initialise le résumeur de commits.

        Args:
            repo_path: Chemin vers le dépôt Git. Si None, utilise le répertoire courant.
            lang: Langue dans laquelle générer les messages (fr, en, es, etc.).
            style: Style de message à générer (conventional, descriptive).
        """
        self.repo_path = repo_path or os.getcwd()
        self.lang = lang
        self.style = style
        self.diff_analyzer = DiffAnalyzer(self.repo_path)
        self.message_generator = MessageGenerator(lang=self.lang)

    def summarize_staged_changes(self) -> Dict:
        """
        Résume les changements en staging.

        Returns:
            Un dictionnaire contenant l'analyse et le message de commit suggéré.
        """
        # Récupérer les différences
        diff_text = self.diff_analyzer.get_staged_diff()
        
        # Si aucun changement en staging, retourner un message vide
        if not diff_text:
            return {
                "status": "error",
                "message": "Aucun changement en staging. Utilisez 'git add' pour ajouter des fichiers.",
                "commit_message": ""
            }
        
        # Analyser les différences
        diff_analysis = self.diff_analyzer.analyze_diff(diff_text)
        
        # Catégoriser les changements
        categories = self.diff_analyzer.categorize_changes(diff_analysis)
        
        # Extraire les fonctions modifiées
        functions = self.diff_analyzer.extract_modified_functions(diff_text)
        
        # Générer le message de commit
        commit_message = self.message_generator.generate_ai_commit_message(
            diff_text, diff_analysis, categories, self.style
        )
        
        return {
            "status": "success",
            "diff_analysis": diff_analysis,
            "categories": categories,
            "functions": functions,
            "commit_message": commit_message
        }

    def summarize_unstaged_changes(self) -> Dict:
        """
        Résume les changements non stagés.

        Returns:
            Un dictionnaire contenant l'analyse et le message de commit suggéré.
        """
        # Récupérer les différences
        diff_text = self.diff_analyzer.get_unstaged_diff()
        
        # Si aucun changement non stagé, retourner un message vide
        if not diff_text:
            return {
                "status": "error",
                "message": "Aucun changement non stagé.",
                "commit_message": ""
            }
        
        # Analyser les différences
        diff_analysis = self.diff_analyzer.analyze_diff(diff_text)
        
        # Catégoriser les changements
        categories = self.diff_analyzer.categorize_changes(diff_analysis)
        
        # Extraire les fonctions modifiées
        functions = self.diff_analyzer.extract_modified_functions(diff_text)
        
        # Générer le message de commit
        commit_message = self.message_generator.generate_ai_commit_message(
            diff_text, diff_analysis, categories, self.style
        )
        
        return {
            "status": "success",
            "diff_analysis": diff_analysis,
            "categories": categories,
            "functions": functions,
            "commit_message": commit_message
        }

    def get_commit_message(self, staged: bool = True) -> str:
        """
        Obtient un message de commit suggéré.

        Args:
            staged: Si True, analyse les changements en staging, sinon les changements non stagés.

        Returns:
            Le message de commit suggéré.
        """
        if staged:
            result = self.summarize_staged_changes()
        else:
            result = self.summarize_unstaged_changes()
            
        return result.get("commit_message", "")
