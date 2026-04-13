import subprocess
import os
import sys
import time
from rich.console import Console
from rich.panel import Panel

console = Console()

def run_command(command, description):
    """Helper to run shell commands with a clean UI."""
    with console.status(f"[bold orange3]{description}...[/bold orange3]", spinner="bouncingBar"):
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            console.print(f"[bold green]✓[/bold green] {description} Successful.")
            return True
        else:
            console.print(f"[bold red]✗[/bold red] {description} Failed.")
            console.print(f"[grey50]{result.stderr}[/grey50]")
            return False

def setup_bro_code():
    console.clear()
    console.print(Panel.fit("[bold orange3]BRO CODE: ULTIMATE ONBOARDING[/bold orange3]", border_style="orange3"))

    # 1. Check for Node/NPM
    if not run_command("npm -v", "Checking for NPM (The Pre-Workout)"):
        console.print("[bold red]ERROR:[/bold red] You need Node.js installed to run the Claude engine.")
        return

    # 2. Install Claude Code Globally
    run_command("npm install -g @anthropic-ai/claude-code", "Installing Claude Engine (Adding Plates)")

    # 3. Add to PATH (Windows Specific)
    npm_path = subprocess.run("npm config get prefix", shell=True, capture_output=True, text=True).stdout.strip()
    if npm_path:
        # Construct the user-level path update
        try:
            current_path = os.environ.get("PATH", "")
            if npm_path not in current_path:
                os.system(f'setx PATH "%PATH%;{npm_path}"')
                console.print(f"[bold green]✓[/bold green] PATH updated with {npm_path}")
            else:
                console.print("[bold blue]i[/bold blue] PATH already contains NPM bin.")
        except Exception as e:
            console.print(f"[bold red]![/bold red] Could not auto-update PATH: {e}")

    # 4. Final Handshake
    console.print("\n[bold white]NEXT STEP: Login to the Rack[/bold white]")
    console.print("[grey50]A browser window will open. Sign in to finish the setup.[/grey50]\n")
    
    # We run 'claude login' and wait for it to finish
    subprocess.run("claude login", shell=True)

    console.print("\n" + "="*50)
    console.print("[bold green]SETUP COMPLETE. GAINS SECURED.[/bold green]")
    console.print("Restart your terminal and type [bold orange3]bro[/bold orange3] to begin.")
    console.print("="*50 + "\n")

if __name__ == "__main__":
    setup_bro_code()