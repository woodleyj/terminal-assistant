import os
import sys
import platform
from pathlib import Path
from dotenv import load_dotenv, set_key, unset_key
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt
import json
from google import genai
import pyperclip
import questionary

# Setup Rich Console
console = Console()

TASS_BANNER = """
 ████████╗ █████╗ ███████╗███████╗
 ╚══██╔══╝██╔══██╗██╔════╝██╔════╝
    ██║   ███████║███████╗███████╗
    ██║   ██╔══██║╚════██║╚════██║
    ██║   ██║  ██║███████║███████║
    ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
"""

# Pathing - Confirmed for src/assistant/main.py structure
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = ROOT_DIR / ".env"
MEMORY_FILE = ROOT_DIR / ".tass_memory.json"

VERSION = "0.2.0"

SUPPORTED_MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview"
]

DEFAULT_MODEL = "gemini-3-flash-preview"
DEFAULT_FALLBACK_MODEL = "gemini-3.1-flash-lite-preview"

def get_current_model():
    """Get the preferred model from .env."""
    load_dotenv(ENV_FILE, override=True)
    model = os.getenv("TASS_MODEL", DEFAULT_MODEL)
    return model if model in SUPPORTED_MODELS else DEFAULT_MODEL

def set_current_model(model):
    """Set the preferred model in .env."""
    if model in SUPPORTED_MODELS:
        set_key(str(ENV_FILE), "TASS_MODEL", model)
        console.print(f"[bold green]Model set to {model}.[/bold green]")
        return True
    return False

def get_fallback_settings():
    """Get fallback settings from .env."""
    load_dotenv(ENV_FILE, override=True)
    use_fallback = os.getenv("TASS_USE_FALLBACK_MODEL", "True") == "True"
    fallback_model = os.getenv("TASS_FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL)
    if fallback_model not in SUPPORTED_MODELS:
        fallback_model = DEFAULT_FALLBACK_MODEL
    return use_fallback, fallback_model

def set_fallback_settings(use_fallback, fallback_model):
    """Set fallback settings in .env."""
    set_key(str(ENV_FILE), "TASS_USE_FALLBACK_MODEL", str(use_fallback))
    if fallback_model in SUPPORTED_MODELS:
        set_key(str(ENV_FILE), "TASS_FALLBACK_MODEL", fallback_model)
    console.print(f"[bold green]Fallback settings updated (Enabled: {use_fallback}, Model: {fallback_model}).[/bold green]")

DEFAULT_SYSTEM_PROMPT = (
    "You are TASS (v{version}), a Terminal Assistant. The user is on {os} using {shell}. "
    "Your goal is to assist with terminal commands or technical queries. "
    "\n\nMODES:"
    "\n1. COMMAND MODE: If the user asks for a task that requires a command, provide it."
    "\n2. CHAT MODE: If the user asks a general question, respond concisely."
    "\n\nCRITICAL (Command Mode): The command MUST be natively compatible with {shell}. "
    "\nSTYLE GUIDELINES:"
    "\n- ALWAYS prefer the SHORTEST possible command and use common ALIASES (e.g., 'gci' or 'ls')."
    "\n- If you use an alias, briefly mention what it stands for."
    "\n- For complex commands, provide a 'BREAKDOWN' section deconstructing the flags used."
    "\n{history_context}"
    "\n\nFORMATTING (Strict):"
    "\n- Line 1: The terminal command (OR 'NONE' if in CHAT MODE)."
    "\n- Line 2: A one-sentence explanation of what the command does."
    "\n- Line 3+: (Optional) A 'BREAKDOWN:' section with details for complex commands, or the full chat response."
)

def validate_alias(alias):
    """Ensure alias is <= 10 chars and alphanumeric."""
    return len(alias) <= 10 and alias.isalnum()

def get_user_aliases():
    """Get list of user-defined aliases from .env."""
    load_dotenv(ENV_FILE, override=True)
    aliases_str = os.getenv("TASS_USER_ALIASES", "")
    return [a.strip() for a in aliases_str.split(",") if a.strip()]

def add_user_alias(alias):
    """Add a new alias to .env."""
    if not validate_alias(alias):
        console.print("[bold red]Invalid alias! Must be <= 10 alphanumeric characters.[/bold red]")
        return False
    
    aliases = get_user_aliases()
    if alias in aliases or alias == "tass":
        console.print(f"[bold yellow]Alias '{alias}' already exists.[/bold yellow]")
        return False
    
    aliases.append(alias)
    set_key(str(ENV_FILE), "TASS_USER_ALIASES", ",".join(aliases))
    console.print(f"[bold green]Alias '{alias}' added successfully.[/bold green]")
    return True

def remove_user_alias(alias):
    """Remove an alias from .env."""
    if alias == "tass":
        console.print("[bold red]Cannot remove the primary 'tass' alias.[/bold red]")
        return False
    
    aliases = get_user_aliases()
    if alias not in aliases:
        console.print(f"[bold yellow]Alias '{alias}' not found.[/bold yellow]")
        return False
    
    aliases.remove(alias)
    set_key(str(ENV_FILE), "TASS_USER_ALIASES", ",".join(aliases))
    console.print(f"[bold green]Alias '{alias}' removed.[/bold green]")
    return True

def setup_env():
    """First-run wizard to set up API key and initial alias."""
    load_dotenv(ENV_FILE, override=True)
    api_key = os.getenv("GEMINI_TASS_API_KEY")
    user_aliases = get_user_aliases()
    setup_done = os.getenv("TASS_SETUP_COMPLETE") == "True"

    if not api_key or not setup_done:
        console.print(Text(TASS_BANNER, style="bold yellow"))
        console.print(Panel(f"Terminal Assistant v{VERSION}", expand=False, border_style="cyan"))
        console.print("[bold green]Welcome to TASS![/bold green] Let's get you set up.")
        
        # API Key Setup
        if not api_key:
            api_key = Prompt.ask("Enter your Gemini API Key")
            if not ENV_FILE.exists():
                ENV_FILE.touch()
            set_key(str(ENV_FILE), "GEMINI_TASS_API_KEY", api_key)
            console.print(f"[dim]Key saved to {ENV_FILE}[/dim]")

        # Initial Alias Setup
        if not user_aliases and not setup_done:
            console.print("\n[bold cyan]Alias Setup (Optional)[/bold cyan]")
            console.print("Choose a custom name to use TASS (e.g., 'ask', 'ai'). Max 10 chars, alphanumeric.")
            console.print("[dim]Press Enter to skip and use 'tass' only.[/dim]")
            while True:
                alias = Prompt.ask("Primary Alias", default="")
                if not alias:
                    console.print("[dim]No extra alias added.[/dim]")
                    break
                if validate_alias(alias):
                    add_user_alias(alias)
                    break
                console.print("[bold red]Invalid alias! Try again.[/bold red]")
        
        set_key(str(ENV_FILE), "TASS_SETUP_COMPLETE", "True")
        
        # Initialize default model settings if not present
        if not os.getenv("TASS_MODEL"):
            set_key(str(ENV_FILE), "TASS_MODEL", DEFAULT_MODEL)
        if not os.getenv("TASS_USE_FALLBACK_MODEL"):
            set_key(str(ENV_FILE), "TASS_USE_FALLBACK_MODEL", "True")
        if not os.getenv("TASS_FALLBACK_MODEL"):
            set_key(str(ENV_FILE), "TASS_FALLBACK_MODEL", DEFAULT_FALLBACK_MODEL)
            
        console.print("\n[bold green]Setup complete![/bold green]")
        load_dotenv(ENV_FILE, override=True)
        
    return os.getenv("GEMINI_TASS_API_KEY")

def detect_shell():
    """Detect the current shell environment."""
    parent_process = ""
    try:
        import psutil
        parent_process = psutil.Process(os.getppid()).name().lower()
    except ImportError:
        if os.name == 'nt':
            if os.getenv('PSModulePath'):
                parent_process = "powershell"
            else:
                parent_process = "cmd"
        else:
            parent_process = os.getenv('SHELL', 'bash').split('/')[-1]
    
    if "pwsh" in parent_process or "powershell" in parent_process:
        return "PowerShell"
    elif "cmd" in parent_process:
        return "Command Prompt (CMD)"
    elif "bash" in parent_process:
        return "Bash"
    elif "zsh" in parent_process:
        return "Zsh"
    return parent_process or "Terminal"

def get_system_prompt():
    """Get the current system prompt, preferring override from .env."""
    load_dotenv(ENV_FILE, override=True)
    return os.getenv("TASS_SYSTEM_PROMPT_OVERRIDE", DEFAULT_SYSTEM_PROMPT)

def set_system_prompt(prompt):
    """Set the system prompt override in .env."""
    if not prompt or prompt.strip() == "reset":
        unset_key(str(ENV_FILE), "TASS_SYSTEM_PROMPT_OVERRIDE")
        console.print("[bold green]System prompt reset to default.[/bold green]")
    else:
        set_key(str(ENV_FILE), "TASS_SYSTEM_PROMPT_OVERRIDE", prompt)
        console.print("[bold green]System prompt updated.[/bold green]")

def get_max_memory():
    """Get max memory from env, with a sensible limit of 20."""
    load_dotenv(ENV_FILE, override=True)
    try:
        limit = int(os.getenv("TASS_MEMORY_LIMIT", 5))
        return min(max(1, limit), 20)
    except (ValueError, TypeError):
        return 5

def set_max_memory(limit):
    """Update max memory limit in .env."""
    try:
        val = int(limit)
        if 1 <= val <= 20:
            set_key(str(ENV_FILE), "TASS_MEMORY_LIMIT", str(val))
            console.print(f"[bold green]Memory limit set to {val}.[/bold green]")
        else:
            console.print("[bold red]Limit must be between 1 and 20.[/bold red]")
    except ValueError:
        console.print("[bold red]Invalid limit value.[/bold red]")

def load_memory():
    """Load interaction history from disk."""
    if MEMORY_FILE.exists():
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []

def save_memory(query, response):
    """Save the latest interaction and prune old ones based on limit."""
    memory = load_memory()
    memory.append({"query": query, "response": response})
    
    limit = get_max_memory()
    if len(memory) > limit:
        memory = memory[-limit:]
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def clear_memory():
    """Delete the memory file."""
    if MEMORY_FILE.exists():
        MEMORY_FILE.unlink()
    console.print("[bold green]Memories cleared![/bold green]")

def reset_tass():
    """Completely wipe TASS configuration and history."""
    files_to_remove = [ENV_FILE, MEMORY_FILE]
    for file_path in files_to_remove:
        try:
            if file_path.exists():
                console.print(f"[dim]Deleting {file_path}...[/dim]")
                file_path.unlink()
        except Exception as e:
            console.print(f"[bold red]Error deleting {file_path.name}:[/bold red] {e}")
    
    console.print("\n[bold red]TASS has been completely reset.[/bold red]")
    console.print("[dim]All local configuration files have been removed.[/dim]")
    console.print("[bold yellow]Run 'tass' again to start fresh.[/bold yellow]\n")

def show_memory():
    """Display stored interactions."""
    memory = load_memory()
    limit = get_max_memory()
    console.print(f"[dim]Memory Limit: {limit} interactions[/dim]")
    if not memory:
        console.print("[dim]No memories found.[/dim]")
        return
    
    for i, entry in enumerate(memory, 1):
        console.print(Panel(
            f"[bold cyan]Q:[/bold cyan] {entry['query']}\n[bold green]A:[/bold green] {entry['response'].splitlines()[0]}",
            title=f"Memory {i}",
            expand=False
        ))

def show_init_instructions():
    """Show how to register aliases in the shell."""
    shell = detect_shell()
    aliases = ["tass"] + get_user_aliases()
    
    console.print(Panel(f"[bold cyan]Shell Integration ({shell})[/bold cyan]\n"
                        "To use your aliases, add the following to your profile/startup script:", expand=False))
    
    if shell == "PowerShell":
        for a in aliases:
            console.print(f"[green]Set-Alias -Name {a} -Value tass[/green]")
        console.print("\n[dim]Profile path: $PROFILE[/dim]")
    elif shell == "Command Prompt (CMD)":
        for a in aliases:
            console.print(f"[green]doskey {a}=tass $*[/green]")
    else:
        for a in aliases:
            console.print(f"[green]alias {a}='tass'[/green]")

def integrate_shell():
    """Automate alias registration in the user's shell profile."""
    shell = detect_shell()
    aliases = ["tass"] + get_user_aliases()
    
    profile_path = None
    commands = []
    
    if shell == "PowerShell":
        profile_path = Path(os.popen('echo $PROFILE').read().strip())
        for a in aliases:
            commands.append(f"if (!(Get-Alias -Name {a} -ErrorAction SilentlyContinue)) {{ Set-Alias -Name {a} -Value tass }}")
    elif shell in ["Bash", "Zsh"]:
        profile_file = ".bashrc" if shell == "Bash" else ".zshrc"
        profile_path = Path.home() / profile_file
        for a in aliases:
            commands.append(f"alias {a}='tass'")
    
    if not profile_path:
        console.print(f"[bold red]Automatic integration not supported for {shell}.[/bold red]")
        show_init_instructions()
        return

    console.print(f"[bold cyan]Target Profile:[/bold cyan] {profile_path}")
    if questionary.confirm(f"Append {len(commands)} alias(es) to your {shell} profile?").ask():
        try:
            if not profile_path.parent.exists():
                profile_path.parent.mkdir(parents=True)
            
            with open(profile_path, "a") as f:
                f.write("\n# TASS Aliases\n")
                for cmd in commands:
                    f.write(f"{cmd}\n")
            
            console.print("[bold green]Integration complete![/bold green] Restart your terminal or source your profile.")
        except Exception as e:
            console.print(f"[bold red]Failed to write to profile:[/bold red] {e}")

def handle_management_command(args):
    """Process management commands. Returns True if handled."""
    if not args:
        return False
    cmd = args[0].lower()
    
    if cmd.startswith("/mem"):
        subcmd = args[1].lower() if len(args) > 1 else "show"
        if subcmd == "clear":
            clear_memory()
        elif subcmd == "limit":
            if len(args) > 2:
                set_max_memory(args[2])
            else:
                console.print(f"[bold yellow]Current limit: {get_max_memory()}[/bold yellow]")
        else:
            show_memory()
        return True
    
    elif cmd.startswith("/prompt"):
        subcmd = args[1].lower() if len(args) > 1 else "show"
        if subcmd == "edit":
            new_prompt = Prompt.ask("Enter new system prompt (or 'reset' to use default)")
            set_system_prompt(new_prompt)
        else:
            console.print(Panel(get_system_prompt(), title="Current System Prompt", border_style="yellow"))
            console.print("[dim]Use 'tass /prompt edit' to modify.[/dim]")
        return True
    
    elif cmd.startswith("/alias"):
        subcmd = args[1].lower() if len(args) > 1 else "list"
        if subcmd == "add" and len(args) > 2:
            add_user_alias(args[2])
        elif subcmd == "remove" and len(args) > 2:
            remove_user_alias(args[2])
        else:
            aliases = ["tass"] + get_user_aliases()
            console.print(f"[bold cyan]Active Aliases:[/bold cyan] {', '.join(aliases)}")
            console.print("[dim]Use 'tass /alias add <name>' or 'tass /alias remove <name>' to manage.[/dim]")
        return True
    
    elif cmd.startswith("/init"):
        show_init_instructions()
        return True
    
    elif cmd.startswith("/integrate"):
        integrate_shell()
        return True
        
    return False

def run_query(query, api_key):
    """Execute a query with streaming output and command breakdown."""
    memory = load_memory()
    console.print("[bold blue]Thinking...[/bold blue]")
    
    full_response = ""
    header_captured = False
    explanation_captured = False
    header = ""
    explanation = ""
    breakdown = ""

    current_os = platform.system()
    current_shell = detect_shell()
    
    history_context = ""
    if memory:
        history_context = "\nRecent interactions:\n"
        for m in memory:
            history_context += f"User: {m['query']}\nTASS: {m['response'].splitlines()[0]}\n"

    template = get_system_prompt()
    try:
        system_prompt = template.format(
            version=VERSION,
            os=current_os,
            shell=current_shell,
            history_context=history_context
        )
    except KeyError as e:
        console.print(f"[bold red]System Prompt Error:[/bold red] Missing variable {e}")
        set_system_prompt("reset")
        return run_query(query, api_key)

    current_model = get_current_model()
    use_fallback, fallback_model = get_fallback_settings()

    def execute_request(model_to_use, is_fallback_attempt=False):
        nonlocal full_response, header_captured, explanation_captured, header, explanation, breakdown
        
        full_response = ""
        header_captured = False
        explanation_captured = False
        header = ""
        explanation = ""
        breakdown = ""

        if is_fallback_attempt:
            console.print(f"[bold yellow]Quota reached. Falling back to {model_to_use}...[/bold yellow]")

        try:
            client = genai.Client(api_key=api_key)
            stream = client.models.generate_content_stream(
                model=model_to_use,
                config={'system_instruction': system_prompt},
                contents=query
            )

            for chunk in stream:
                text = chunk.text
                full_response += text
                
                lines = full_response.split('\n')
                if len(lines) > 1 and not header_captured:
                    header = lines[0].strip()
                    header_captured = True
                    if header.upper() == "NONE":
                        console.print("\n[bold cyan]TASS:[/bold cyan] ", end="")
                    else:
                        console.print("\n[bold white]Suggested Command:[/bold white]")
                        console.print(Panel(Text(header, style="bold green"), border_style="cyan"))
                        try:
                            pyperclip.copy(header)
                            console.print("[dim](Copied to clipboard)[/dim]")
                        except (pyperclip.PyperclipException, Exception):
                            pass

                if len(lines) > 2 and not explanation_captured:
                    explanation = lines[1].strip()
                    explanation_captured = True
                    if header.upper() != "NONE":
                        console.print(f"[italic]{explanation}[/italic]\n")
                    else:
                        console.print(explanation, end="")

                if explanation_captured:
                    if header.upper() == "NONE":
                        console.print(text.replace(lines[0] + '\n', '').replace(lines[1] + '\n', ''), end="")
                    else:
                        if "BREAKDOWN:" in text or breakdown:
                            breakdown += text
            
            if breakdown:
                parts = breakdown.split("BREAKDOWN:")
                if len(parts) > 1:
                    console.print(Panel(parts[1].strip(), title="Command Breakdown", border_style="dim"))

            console.print()
            save_memory(query, full_response)
            return True

        except Exception as e:
            error_msg = str(e)
            if ("429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg) and not is_fallback_attempt and use_fallback:
                if model_to_use != fallback_model:
                    return execute_request(fallback_model, is_fallback_attempt=True)
            
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                console.print("\n[bold yellow]⚠️  API Quota Reached (429)[/bold yellow]")
                console.print(f"The model '{model_to_use}' has reached its limit.")
                console.print("\n[bold cyan]How to fix:[/bold cyan]")
                console.print("1. Wait about 60 seconds and try again.")
                console.print("2. Monitor your usage at: [link=https://aistudio.google.com/app/api-keys]Google AI Studio[/link]")
                console.print("3. Check rate limits: [link=https://ai.google.dev/gemini-api/docs/rate-limits]Gemini API Docs[/link]")
            else:
                console.print(f"[bold red]Error calling Gemini API:[/bold red] {e}")
            return False

    if not execute_request(current_model):
        sys.exit(1)


def check_for_updates():

    """Simple placeholder for update checking."""
    # In a real app, you might fetch from GitHub API or PyPI
    # For now, just a visual indicator of the version
    console.print(f"[dim]TASS v{VERSION} - Up to date[/dim]")

def main():
    try:
        # 1. IMMEDIATE PANIC CHECK: Is this a reset request?
        if len(sys.argv) > 1 and sys.argv[1].lower() in ["/reset", "reset"]:
            if questionary.confirm("COMPLETELY RESET TASS? This wipes your API key, aliases, and history.").ask():
                reset_tass()
            else:
                console.print("[dim]Reset cancelled.[/dim]")
            return

        # 2. Handle other CLI management commands
        if len(sys.argv) > 1 and sys.argv[1].startswith("/"):
            if handle_management_command(sys.argv[1:]):
                return

        # 3. Handle first-run/env setup
        api_key = setup_env()
        check_for_updates()
        
        # 4. Check for direct query via CLI args
        if len(sys.argv) > 1:
            query = " ".join(sys.argv[1:])
            run_query(query, api_key)
            return

        # 5. Interactive Menu
        while True:
            console.clear()
            console.print(Text(TASS_BANNER, style="bold yellow"))
            console.print(Panel(f"Terminal Assistant v{VERSION}", expand=False, border_style="cyan"))
            
            choice = questionary.select(
                "Main Menu",
                choices=[
                    "Ask a Question",
                    "Manage Aliases",
                    "Manage Memory",
                    "System Settings",
                    "Shell Integration",
                    "Exit"
                ]
            ).ask()
            
            if choice == "Ask a Question":
                query = questionary.text("How can I help you?").ask()
                if not query:
                    continue

                if query.lower().strip() in ["/reset", "reset"]:
                    if questionary.confirm("COMPLETELY RESET TASS?").ask():
                        reset_tass()
                        return
                    continue

                if query.strip():
                    run_query(query, api_key)
                    questionary.press_any_key_to_continue().ask()
            
            elif choice == "Manage Aliases":
                alias_choice = questionary.select(
                    "Alias Management",
                    choices=["List Aliases", "Add Alias", "Remove Alias", "Back"]
                ).ask()
                if alias_choice == "List Aliases":
                    handle_management_command(["/alias", "list"])
                elif alias_choice == "Add Alias":
                    new_alias = questionary.text("Enter new alias").ask()
                    if new_alias:
                        add_user_alias(new_alias)
                elif alias_choice == "Remove Alias":
                    aliases = get_user_aliases()
                    if not aliases:
                        console.print("[dim]No user aliases to remove.[/dim]")
                    else:
                        to_remove = questionary.select("Select alias to remove", choices=aliases).ask()
                        if to_remove:
                            remove_user_alias(to_remove)
                if alias_choice != "Back":
                    questionary.press_any_key_to_continue().ask()

            elif choice == "Manage Memory":
                mem_choice = questionary.select(
                    "Memory Management",
                    choices=["Show Memories", "Clear Memories", "Back"]
                ).ask()
                if mem_choice == "Show Memories": 
                    show_memory()
                    questionary.press_any_key_to_continue().ask()
                elif mem_choice == "Clear Memories": 
                    clear_memory()
                    questionary.press_any_key_to_continue().ask()
                
            elif choice == "System Settings":
                sys_choice = questionary.select(
                    "System Settings",
                    choices=["Show System Prompt", "Edit System Prompt", "Set Memory Limit", "Model Settings", "Back"]
                ).ask()
                if sys_choice == "Show System Prompt": 
                    handle_management_command(["/prompt", "show"])
                    questionary.press_any_key_to_continue().ask()
                elif sys_choice == "Edit System Prompt": 
                    handle_management_command(["/prompt", "edit"])
                    questionary.press_any_key_to_continue().ask()
                elif sys_choice == "Set Memory Limit": 
                    limit = questionary.text("Enter memory limit (1-20)").ask()
                    if limit:
                        set_max_memory(limit)
                        questionary.press_any_key_to_continue().ask()
                elif sys_choice == "Model Settings":
                    current_m = get_current_model()
                    use_fb, fb_m = get_fallback_settings()
                    
                    model_choice = questionary.select(
                        f"Model Settings (Current: {current_m})",
                        choices=[
                            "Change Primary Model",
                            f"Toggle Fallback (Currently: {'ON' if use_fb else 'OFF'})",
                            "Change Fallback Model",
                            "Back"
                        ]
                    ).ask()
                    
                    if model_choice == "Change Primary Model":
                        new_m = questionary.select("Select Primary Model", choices=SUPPORTED_MODELS).ask()
                        if new_m:
                            set_current_model(new_m)
                    elif model_choice.startswith("Toggle Fallback"):
                        set_fallback_settings(not use_fb, fb_m)
                    elif model_choice == "Change Fallback Model":
                        new_fb = questionary.select("Select Fallback Model", choices=SUPPORTED_MODELS).ask()
                        if new_fb:
                            set_fallback_settings(use_fb, new_fb)
                    
                    if model_choice != "Back":
                        questionary.press_any_key_to_continue().ask()
            
            elif choice == "Shell Integration":
                shell_choice = questionary.select(
                    "Shell Integration",
                    choices=["Show Manual Instructions", "Auto-Integrate (Write to Profile)", "Back"]
                ).ask()
                if shell_choice == "Show Manual Instructions":
                    show_init_instructions()
                    questionary.press_any_key_to_continue().ask()
                elif shell_choice == "Auto-Integrate (Write to Profile)":
                    integrate_shell()
                    questionary.press_any_key_to_continue().ask()
                
            elif choice == "Exit" or choice is None:
                console.print("[dim]Goodbye![/dim]")
                break
    except KeyboardInterrupt:
        console.print("\n[dim]Goodbye![/dim]")
        sys.exit(0)

if __name__ == "__main__":
    main()
