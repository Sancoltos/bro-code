import typer
import time
from rich.console import Console
from ui import get_welcome_screen, print_logo
from brain import run_claude_as_bro, get_bro_thinking_style

app = typer.Typer()
console = Console()

@app.command()
def main():
    console.clear()
    print_logo()
    
    # "Split the difference" height
    console.print(get_welcome_screen(), height=8) 
    
    console.print("\n[bold white]Push **Enter** to Spot Me[/bold white]", justify="center")

    while True:
        try:
            user_input = console.input("\n[bold green]💪 What's the workout? > [/bold green]").strip()

            if not user_input:
                console.print("[dim]Need an actual rep here, bro — type what you want to work on.[/dim]")
                continue

            if user_input.lower() in ["exit", "done", "quit"]:
                console.print("[orange3]Keep grinding. See you at the rack. 🍗[/orange3]")
                break

            with get_bro_thinking_style() as progress:
                task = progress.add_task("Chalking up...", total=100)
                while not progress.finished:
                    progress.update(task, advance=33)
                    time.sleep(0.1)

            run_claude_as_bro(user_input)
            
        except KeyboardInterrupt:
            console.print("\n[orange3]Session cut short. Hit the showers. 🍗[/orange3]")
            break

if __name__ == "__main__":
    app()