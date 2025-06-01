"""Interface en ligne de commande pour l'AI Commit Summarizer."""

import sys
import os
import click
from colorama import init, Fore, Style

from .main import CommitSummarizer


# Initialiser colorama pour les couleurs dans le terminal
init()


def print_colored(text, color=Fore.WHITE, style=Style.NORMAL, end='\n'):
    """Affiche du texte coloré dans le terminal."""
    print(f"{style}{color}{text}{Style.RESET_ALL}", end=end)


def print_header():
    """Affiche l'en-tête de l'application."""
    print_colored("🧠 AI Commit Summarizer", Fore.CYAN, Style.BRIGHT)
    print_colored("Générateur de résumés intelligents pour les commits Git", Fore.CYAN)
    print()


def print_summary(result):
    """Affiche le résumé de l'analyse des changements."""
    if result["status"] == "error":
        print_colored(f"⚠️  {result['message']}", Fore.YELLOW)
        return
        
    diff_analysis = result["diff_analysis"]
    categories = result["categories"]
    functions = result.get("functions", [])
    
    print_colored("📊 Analyse des changements:", Fore.GREEN, Style.BRIGHT)
    print_colored(f"  • Fichiers modifiés: {diff_analysis['files_changed']}", Fore.GREEN)
    print_colored(f"  • Lignes ajoutées: {diff_analysis['additions']}", Fore.GREEN)
    print_colored(f"  • Lignes supprimées: {diff_analysis['deletions']}", Fore.GREEN)
    
    if diff_analysis['file_types']:
        print_colored(f"  • Types de fichiers: {', '.join(diff_analysis['file_types'])}", Fore.GREEN)
    
    if categories:
        print_colored(f"  • Catégories: {', '.join(categories)}", Fore.GREEN)
    
    if functions:
        print_colored(f"  • Fonctions modifiées: {', '.join(functions[:5])}", Fore.GREEN)
        if len(functions) > 5:
            print_colored(f"    et {len(functions) - 5} autres...", Fore.GREEN)
    
    print()
    
    print_colored("✨ Message de commit suggéré:", Fore.MAGENTA, Style.BRIGHT)
    print_colored(f"{result['commit_message']}", Fore.MAGENTA)


@click.command()
@click.option('--style', '-s', default='descriptive', 
              type=click.Choice(['conventional', 'descriptive']),
              help='Style du message de commit.')
@click.option('--lang', '-l', default='fr',
              type=click.Choice(['fr', 'en']),
              help='Langue du message de commit.')
@click.option('--unstaged', '-u', is_flag=True,
              help='Analyser les changements non stagés au lieu des changements en staging.')
@click.option('--commit', '-c', is_flag=True,
              help='Créer directement un commit avec le message généré.')
def main(style, lang, unstaged, commit):
    """
    Analyse les changements Git et génère un message de commit intelligent.
    
    Exemple d'utilisation:
        git-commit-summarizer --style conventional --lang fr
    """
    print_header()
    
    # Vérifier que nous sommes dans un dépôt Git
    if not os.path.exists('.git'):
        print_colored("⚠️  Ce n'est pas un dépôt Git valide.", Fore.RED)
        sys.exit(1)
    
    # Créer le résumeur de commits
    summarizer = CommitSummarizer(lang=lang, style=style)
    
    # Analyser les changements
    if unstaged:
        result = summarizer.summarize_unstaged_changes()
    else:
        result = summarizer.summarize_staged_changes()
    
    # Afficher le résumé
    print_summary(result)
    
    # Créer un commit si demandé
    if commit and result["status"] == "success":
        commit_message = result["commit_message"]
        
        try:
            # Utiliser la commande git directement
            os.system(f'git commit -m "{commit_message}"')
            print_colored("\n✅ Commit créé avec succès!", Fore.GREEN, Style.BRIGHT)
        except Exception as e:
            print_colored(f"\n❌ Erreur lors de la création du commit: {str(e)}", Fore.RED)


if __name__ == '__main__':
    main()
