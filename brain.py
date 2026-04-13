import re
import sys
import os
import json
import subprocess
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn

try:
    import anthropic
except ImportError:
    print("Run: pip install anthropic")
    sys.exit(1)

console = Console()

def _get_api_key():
    """Use ANTHROPIC_API_KEY if set, otherwise fall back to registry (Windows) or Claude Code."""
    if os.environ.get("ANTHROPIC_API_KEY"):
        return os.environ["ANTHROPIC_API_KEY"]

    # Fallback: read directly from Windows user registry
    # (handles the case where VSCode was launched before the env var was set)
    if sys.platform == "win32":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as k:
                value, _ = winreg.QueryValueEx(k, "ANTHROPIC_API_KEY")
                if value and isinstance(value, str):
                    return value
        except Exception:
            pass

    # Fallback: Claude Code config
    config = Path.home() / ".claude" / "config.json"
    if config.exists():
        try:
            return json.loads(config.read_text())["primaryApiKey"]
        except (KeyError, json.JSONDecodeError):
            pass

    console.print("[bold red]No API key found. Set ANTHROPIC_API_KEY or log in with Claude Code.[/bold red]")
    sys.exit(1)

BRO_SYSTEM_PROMPT = (
    "You are a massive gym bro who is also an elite software engineer. "
    "You speak exclusively in gym slang and bro speak. "
    "Call the user 'bro'. Refer to code as 'reps', bugs as 'bad form', "
    "functions as 'sets', files as 'plates', and good code as 'gains'. "
    "Always end your responses with 'Lightweight baby!'"
)

TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file from disk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "Write content to a file on disk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Path to the file"},
                "content": {"type": "string", "description": "Content to write"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "list_directory",
        "description": "List files in a directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "Directory path (default: current directory)"}
            }
        }
    },
    {
        "name": "run_command",
        "description": "Run a shell command and return its output.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "Shell command to run"}
            },
            "required": ["command"]
        }
    }
]

TRANSLATIONS = {
    r"Searching for patterns": "Checking the rack for weights...",
    r"Reading (\d+) files": r"Checking the form on \1 plates...",
    r"Thinking": "Visualizing the Pump...",
    r"Applying changes": "Adding plates to the bar...",
    r"Completed": "Lightweight baby! 👊",
    r"Claude": "Bro Code",
    r"Anthropic": "The Gym",
}

def bro_translate(text):
    for pattern, replacement in TRANSLATIONS.items():
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text

def ask_bro_permission(tool_name, tool_input):
    """Show a bro-style permission prompt and return True if approved."""
    descriptions = {
        "read_file":      f"[bold cyan]read[/bold cyan] [bold]{tool_input.get('path')}[/bold]",
        "write_file":     f"[bold yellow]write to[/bold yellow] [bold]{tool_input.get('path')}[/bold]",
        "list_directory": f"[bold cyan]scope the directory[/bold cyan] [bold]{tool_input.get('path', '.')}[/bold]",
        "run_command":    f"[bold red]run[/bold red] [bold]{tool_input.get('command')}[/bold]",
    }
    action = descriptions.get(tool_name, tool_name)
    console.print(f"\n[bold white]Bro wants to {action}[/bold white]")
    console.print("[bold green]You spottin' him?[/bold green] [[bold]Y[/bold]/n] ", end="")
    try:
        response = input().strip().lower()
        return response in ["", "y", "yes", "yeah", "yeet"]
    except (EOFError, KeyboardInterrupt):
        return False

def execute_tool(tool_name, tool_input):
    """Execute a tool and return its result as a string."""
    if tool_name == "read_file":
        try:
            return Path(tool_input["path"]).read_text(encoding="utf-8")
        except Exception as e:
            return f"Error: {e}"

    elif tool_name == "write_file":
        try:
            Path(tool_input["path"]).write_text(tool_input["content"], encoding="utf-8")
            return "Written successfully."
        except Exception as e:
            return f"Error: {e}"

    elif tool_name == "list_directory":
        try:
            entries = sorted(Path(tool_input.get("path", ".")).iterdir(), key=lambda p: p.name)
            return "\n".join(e.name for e in entries)
        except Exception as e:
            return f"Error: {e}"

    elif tool_name == "run_command":
        try:
            result = subprocess.run(
                tool_input["command"], shell=True, capture_output=True, text=True, timeout=30
            )
            return (result.stdout + result.stderr).strip()
        except Exception as e:
            return f"Error: {e}"

    return "Unknown tool."

def run_claude_as_bro(user_input):
    """Stream a response from Claude with bro-style tool permission prompts."""
    client = anthropic.Anthropic(api_key=_get_api_key())
    messages = [{"role": "user", "content": user_input}]

    while True:
        # Stream the response token by token
        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=8096,
            system=BRO_SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        ) as stream:
            tool_name_hint = None

            for event in stream:
                etype = getattr(event, "type", None)

                if etype == "content_block_start":
                    block = event.content_block
                    if getattr(block, "type", None) == "tool_use":
                        label = {
                            "read_file":      "Checking the form on a plate",
                            "write_file":     "Racking a new plate",
                            "list_directory": "Scoping the gym floor",
                            "run_command":    "Running the drill",
                        }.get(block.name, "Working it out")
                        console.print(f"\n[dim]{label}...[/dim]")

                elif etype == "content_block_delta":
                    delta = event.delta
                    if getattr(delta, "type", None) == "text_delta":
                        sys.stdout.write(bro_translate(delta.text))
                        sys.stdout.flush()

            final = stream.get_final_message()

        # Handle any tool use blocks
        tool_blocks = [b for b in final.content if b.type == "tool_use"]
        if not tool_blocks:
            break

        tool_results = []
        for block in tool_blocks:
            approved = ask_bro_permission(block.name, block.input)
            if approved:
                result = execute_tool(block.name, block.input)
                console.print("[dim green]Done, bro![/dim green]")
            else:
                result = "User denied permission."
                console.print("[dim red]Skipped.[/dim red]")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result,
            })

        messages.append({"role": "assistant", "content": final.content})
        messages.append({"role": "user", "content": tool_results})

    sys.stdout.write("\n")

def get_bro_thinking_style():
    return Progress(
        TextColumn("[bold green]{task.description}"),
        BarColumn(bar_width=40, style="grey35", complete_style="orange3"),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    )
