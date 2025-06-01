"""Module pour analyser les différences Git et extraire des informations pertinentes."""

import os
from typing import Dict, List, Tuple
import git
from git import Repo


class DiffAnalyzer:
    """Classe pour analyser les différences Git et extraire des informations pertinentes."""

    def __init__(self, repo_path: str = None):
        """
        Initialise l'analyseur de diff.

        Args:
            repo_path: Chemin vers le dépôt Git. Si None, utilise le répertoire courant.
        """
        self.repo_path = repo_path or os.getcwd()
        try:
            self.repo = Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            raise ValueError(f"Le répertoire {self.repo_path} n'est pas un dépôt Git valide.")

    def get_staged_diff(self) -> str:
        """
        Récupère les différences des fichiers en staging.

        Returns:
            Le texte de différence des fichiers en staging.
        """
        diff = self.repo.git.diff("--staged")
        return diff

    def get_unstaged_diff(self) -> str:
        """
        Récupère les différences des fichiers non stagés.

        Returns:
            Le texte de différence des fichiers non stagés.
        """
        diff = self.repo.git.diff()
        return diff

    def analyze_diff(self, diff_text: str) -> Dict:
        """
        Analyse le texte de différence pour extraire des informations utiles.

        Args:
            diff_text: Le texte de différence à analyser.

        Returns:
            Un dictionnaire contenant des informations sur les modifications:
            {
                'files_changed': nombre de fichiers modifiés,
                'additions': nombre de lignes ajoutées,
                'deletions': nombre de lignes supprimées,
                'file_types': types de fichiers modifiés,
                'file_changes': détails des modifications par fichier
            }
        """
        if not diff_text:
            return {
                'files_changed': 0,
                'additions': 0,
                'deletions': 0,
                'file_types': [],
                'file_changes': {}
            }

        files_changed = []
        additions = 0
        deletions = 0
        file_types = set()
        file_changes = {}

        # Analyse de base des fichiers modifiés
        current_file = None
        file_content = []

        for line in diff_text.split('\n'):
            if line.startswith('diff --git'):
                # Nouveau fichier dans le diff
                if current_file:
                    file_changes[current_file] = '\n'.join(file_content)
                
                file_path = line.split(' b/')[1]
                current_file = file_path
                files_changed.append(file_path)
                file_content = []
                
                # Extraire l'extension du fichier
                file_ext = os.path.splitext(file_path)[1][1:] if '.' in file_path else 'no_extension'
                if file_ext:
                    file_types.add(file_ext)
            
            elif line.startswith('+') and not line.startswith('+++'):
                additions += 1
                file_content.append(line)
            
            elif line.startswith('-') and not line.startswith('---'):
                deletions += 1
                file_content.append(line)
            
            else:
                file_content.append(line)
        
        # Ajouter le dernier fichier
        if current_file:
            file_changes[current_file] = '\n'.join(file_content)

        return {
            'files_changed': len(files_changed),
            'additions': additions,
            'deletions': deletions,
            'file_types': list(file_types),
            'file_changes': file_changes
        }

    def categorize_changes(self, diff_analysis: Dict) -> List[str]:
        """
        Catégorise les types de modifications effectuées.

        Args:
            diff_analysis: Le résultat de l'analyse de diff.

        Returns:
            Une liste de catégories de modifications (feat, fix, refactor, etc.)
        """
        categories = []
        
        # Analyse basée sur les noms de fichiers et extensions
        file_types = diff_analysis['file_types']
        
        # Tests modifiés
        if any(file.endswith('test.py') or file.endswith('_test.py') or '/tests/' in file 
               for file in diff_analysis['file_changes'].keys()):
            categories.append('test')
        
        # Documentation
        if 'md' in file_types or 'rst' in file_types or 'txt' in file_types:
            categories.append('docs')
            
        # Configuration
        config_files = ['.json', '.yaml', '.yml', '.toml', '.ini', '.conf']
        if any(ext in file_types for ext in ['json', 'yaml', 'yml', 'toml', 'ini', 'conf']):
            categories.append('config')
            
        # Par défaut, si aucune catégorie n'est détectée
        if not categories:
            categories.append('feat')  # Par défaut, considérer comme une fonctionnalité
            
        return categories

    def extract_modified_functions(self, diff_text: str) -> List[str]:
        """
        Extrait les noms de fonctions modifiées à partir du texte de différence.
        Ceci est une implémentation simple et pourrait nécessiter une analyse syntaxique plus avancée.

        Args:
            diff_text: Le texte de différence à analyser.

        Returns:
            Une liste de noms de fonctions modifiées.
        """
        functions = []
        
        # Recherche basique des définitions de fonctions (pour Python)
        for line in diff_text.split('\n'):
            if line.startswith('+') and 'def ' in line:
                # Extraction simple du nom de fonction
                func_name = line.split('def ')[1].split('(')[0].strip()
                functions.append(func_name)
        
        return functions
