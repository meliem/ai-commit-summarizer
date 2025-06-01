"""Module pour générer des messages de commit à partir de l'analyse des différences."""

from typing import Dict, List, Optional
import os
from transformers import pipeline


class MessageGenerator:
    """Classe pour générer des messages de commit à partir de l'analyse des différences."""

    def __init__(self, model_name: str = "gpt2", lang: str = "fr"):
        """
        Initialise le générateur de messages.

        Args:
            model_name: Nom du modèle à utiliser pour la génération de texte.
            lang: Langue dans laquelle générer les messages (fr, en, es, etc.).
        """
        self.model_name = model_name
        self.lang = lang
        self.generator = None

        # Initialiser le modèle seulement lors de la première utilisation
        # pour éviter de charger le modèle si on n'en a pas besoin

    def _ensure_model_loaded(self):
        """Assure que le modèle est chargé avant utilisation."""
        if self.generator is None:
            self.generator = pipeline('text-generation', model=self.model_name)

    def _get_commit_type(self, categories: List[str]) -> str:
        """
        Détermine le type de commit basé sur les catégories de modifications.

        Args:
            categories: Liste des catégories de modifications.

        Returns:
            Le type de commit (feat, fix, docs, etc.).
        """
        # Priorité des types de commit
        priority_order = ['fix', 'feat', 'test', 'docs', 'style', 'refactor', 'perf', 'build', 'ci', 'chore']
        
        for type_name in priority_order:
            if type_name in categories:
                return type_name
                
        # Par défaut
        return 'feat'

    def generate_conventional_commit(self, diff_analysis: Dict, categories: List[str]) -> str:
        """
        Génère un message de commit au format conventionnel.

        Args:
            diff_analysis: Résultat de l'analyse des différences.
            categories: Liste des catégories de modifications.

        Returns:
            Message de commit au format conventionnel.
        """
        commit_type = self._get_commit_type(categories)
        
        # Construire une description basée sur les fichiers modifiés
        file_types = diff_analysis['file_types']
        files_changed = diff_analysis['files_changed']
        
        description = ""
        if 'python' in file_types or 'py' in file_types:
            description = "mise à jour du code Python"
        elif 'js' in file_types or 'ts' in file_types:
            description = "mise à jour du code JavaScript/TypeScript"
        elif 'css' in file_types or 'scss' in file_types:
            description = "mise à jour des styles"
        elif 'html' in file_types:
            description = "mise à jour des templates HTML"
        else:
            description = f"mise à jour de {files_changed} fichier(s)"
            
        # Format: type(scope): description
        # Pas de scope pour l'instant
        conventional_message = f"{commit_type}: {description}"
        
        return conventional_message

    def generate_descriptive_commit(self, diff_analysis: Dict, categories: List[str], 
                                   functions: List[str] = None) -> str:
        """
        Génère un message de commit descriptif.

        Args:
            diff_analysis: Résultat de l'analyse des différences.
            categories: Liste des catégories de modifications.
            functions: Liste des fonctions modifiées.

        Returns:
            Message de commit descriptif.
        """
        commit_type = self._get_commit_type(categories)
        
        # Statistiques de base
        files_changed = diff_analysis['files_changed']
        additions = diff_analysis['additions']
        deletions = diff_analysis['deletions']
        
        # Construire le message descriptif
        if commit_type == 'feat':
            prefix = "Ajout"
        elif commit_type == 'fix':
            prefix = "Correction"
        elif commit_type == 'refactor':
            prefix = "Refactorisation"
        elif commit_type == 'docs':
            prefix = "Documentation"
        elif commit_type == 'test':
            prefix = "Tests"
        else:
            prefix = "Mise à jour"
            
        description = f"{prefix} "
        
        # Ajouter des détails sur les fonctions si disponibles
        if functions and len(functions) > 0:
            if len(functions) == 1:
                description += f"de la fonction {functions[0]}"
            else:
                description += f"des fonctions {', '.join(functions[:3])}"
                if len(functions) > 3:
                    description += f" et {len(functions) - 3} autres"
        else:
            # Sinon, description basée sur les fichiers
            if files_changed == 1:
                description += "d'un fichier"
            else:
                description += f"de {files_changed} fichiers"
                
        # Ajouter des statistiques
        stats = f" ({additions}+ {deletions}-)"
        
        return description + stats

    def generate_ai_commit_message(self, diff_text: str, diff_analysis: Dict, 
                                  categories: List[str], style: str = "descriptive") -> str:
        """
        Génère un message de commit intelligent en utilisant l'IA.
        
        Args:
            diff_text: Texte de différence brut.
            diff_analysis: Résultat de l'analyse des différences.
            categories: Liste des catégories de modifications.
            style: Style de message à générer (conventional, descriptive, ai).

        Returns:
            Message de commit généré.
        """
        # Pour un MVP, nous utilisons une approche basée sur des règles
        # Dans une version future, nous utiliserions un modèle de langage plus avancé
        
        if style == "conventional":
            return self.generate_conventional_commit(diff_analysis, categories)
        
        # Style descriptif par défaut
        return self.generate_descriptive_commit(diff_analysis, categories)

    def translate_message(self, message: str, target_lang: str) -> str:
        """
        Traduit un message de commit dans une autre langue.

        Args:
            message: Message de commit à traduire.
            target_lang: Langue cible (fr, en, es, etc.).

        Returns:
            Message traduit.
        """
        # Pour un MVP, nous retournons simplement le message original
        # Dans une version future, nous implémenterions un service de traduction
        return message
