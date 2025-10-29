import json
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import print as rprint

def view_json_data(filename='scraped_data.json'):
    """Afficher les données JSON de manière lisible"""
    console = Console()
    
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        console.print(f"\n[bold cyan]📄 Contenu de {filename}[/bold cyan]\n")
        
        # Afficher le titre
        if 'title' in data and data['title']:
            console.print(Panel(data['title'], title="🏷️ Titre de la page", border_style="green"))
        
        # Afficher les h1
        if 'h1' in data and data['h1']:
            console.print("\n[bold yellow]📌 Titres H1:[/bold yellow]")
            for i, h1 in enumerate(data['h1'], 1):
                console.print(f"  {i}. {h1}")
        
        # Afficher les h2
        if 'h2' in data and data['h2']:
            console.print("\n[bold yellow]📌 Titres H2:[/bold yellow]")
            for i, h2 in enumerate(data['h2'], 1):
                console.print(f"  {i}. {h2}")
        
        # Afficher les h3
        if 'h3' in data and data['h3']:
            console.print("\n[bold yellow]📌 Titres H3:[/bold yellow]")
            for i, h3 in enumerate(data['h3'], 1):
                console.print(f"  {i}. {h3}")
        
        # Afficher les tableaux
        if 'tables' in data and data['tables']:
            console.print(f"\n[bold magenta]📊 Tableaux trouvés: {len(data['tables'])}[/bold magenta]\n")
            for idx, table_data in enumerate(data['tables'], 1):
                if not table_data:
                    continue
                    
                console.print(f"[bold]Tableau {idx}:[/bold]")
                
                # Créer un tableau Rich
                table = Table(show_header=True, header_style="bold magenta")
                
                # Utiliser la première ligne comme en-têtes si elle semble être un header
                headers = table_data[0] if table_data else []
                for header in headers:
                    table.add_column(str(header))
                
                # Ajouter les lignes de données
                for row in table_data[1:]:
                    table.add_row(*[str(cell) for cell in row])
                
                console.print(table)
                console.print()
        
        # Afficher les divs avec classes
        if 'divs_with_class' in data and data['divs_with_class']:
            console.print(f"\n[bold blue]🔍 DIVs intéressantes: {len(data['divs_with_class'])}[/bold blue]\n")
            for i, div in enumerate(data['divs_with_class'][:10], 1):  # Limiter à 10
                console.print(f"[bold]{i}. Classes:[/bold] {div['classes']}")
                console.print(f"   [dim]{div['text'][:150]}...[/dim]\n")
        
        # Si c'est une liste simple (ancien format)
        if isinstance(data, list):
            console.print("\n[bold green]📝 Données (liste):[/bold green]")
            for i, item in enumerate(data, 1):
                console.print(f"  {i}. {item}")
        
        console.print("\n[bold green]✅ Analyse terminée![/bold green]\n")
        
    except FileNotFoundError:
        console.print(f"[bold red]❌ Fichier '{filename}' introuvable![/bold red]")
    except json.JSONDecodeError:
        console.print(f"[bold red]❌ Erreur lors de la lecture du JSON![/bold red]")
    except Exception as e:
        console.print(f"[bold red]❌ Erreur: {e}[/bold red]")

if __name__ == "__main__":
    view_json_data()
