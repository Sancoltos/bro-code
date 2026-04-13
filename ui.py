from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.align import Align

console = Console()

def get_welcome_screen():
    # Left Panel: User Info
    user_info = Text.from_markup(
        "[bold white]Welcome back Swol-Adam![/bold white] 💪\n"
        "      __ \n"
        "     /💪\\\n" 
        "[orange3]Gains 6.9 • Bro Pro[/orange3]\n"
        "[grey50]C:/Users/Adam/Software/bro-code[/grey50]"
    )
    
    # Right Panel: Stats
    tips = Text.from_markup(
        "[bold orange3]Recent PRs[/bold orange3]\n"
        "Deadlift: [green]405 lbs[/green]\n"
        "Pull-ups: [green]20 reps[/green]\n"
        "Status: [bold green]JACKED[/bold green]"
    )

    layout = Layout()
    layout.split_row(
        Layout(Panel(user_info, border_style="orange3"), name="left", ratio=2),
        Layout(Panel(tips, border_style="orange3"), name="right", ratio=1)
    )
    return layout


def print_logo():
    logo = (
        "[orange3]██████╗ ██████╗  ██████╗      ██████╗ ██████╗ ██████╗ ███████╗\n"
        "██╔══██╗██╔══██╗██╔═══██╗     ██╔════╝██╔═══██╗██╔══██╗██╔════╝\n"
        "██████╔╝██████╔╝██║   ██║     ██║     ██║   ██║██║  ██║█████╗  \n"
        "██╔══██╗██╔══██╗██║   ██║     ██║     ██║   ██║██║  ██║██╔══╝  \n"
        "██████╔╝██║  ██║╚██████╔╝     ╚██████╗╚██████╔╝██████╔╝███████╗\n"
        "╚══════╝╚═╝  ╚═╝ ╚═════╝       ╚═════╝ ╚═════╝ ╚══════╝╚══════╝[/orange3]"
    )
    console.print(Align.center(Text.from_markup(logo)))