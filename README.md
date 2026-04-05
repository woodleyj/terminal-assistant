# TASS (Terminal Assistant)

```text
 ████████╗ █████╗ ███████╗███████╗
 ╚══██╔══╝██╔══██╗██╔════╝██╔════╝
    ██║   ███████║███████╗███████╗
    ██║   ██╔══██║╚════██║╚════██║
    ██║   ██║  ██║███████║███████║
    ╚═╝   ╚═╝  ╚═╝╚══════╝╚══════╝
```

**TASS** is a lightweight AI assistant designed for your terminal. It translates natural language queries into precise terminal commands, specifically tailored to your Operating System and Shell environment.

---

## 🚀 Key Features

-   **Smart Model Management**: Choose between official 3.x models (`Pro`, `Flash`, `Flash-Lite`) to balance speed and power.
-   **Automated Fallback**: Automatically switches to a lightweight model if your primary model's quota is reached.
-   **OS & Shell Aware**: Automatically detects if you are using PowerShell, CMD, Bash, or Zsh to provide compatible syntax.
-   **Streaming Responses**: Real-time AI feedback for a more responsive and "alive" feel.
-   **Command Breakdown**: Deconstructs complex commands and flags to help you learn as you go.
-   **Automated Integration**: One-click (or one-command) setup to register aliases in your shell profile.
-   **Dynamic Aliases**: Choose your own name to call TASS (e.g., `ask`, `ai`, `cmd`) during setup.
-   **Smart Memory**: Remembers recent interactions for context-aware follow-up questions.
-   **Automatic Clipboard**: Your suggested commands are instantly copied to your clipboard for immediate use.
-   **Interactive Menu**: A sleek, arrow-key driven menu for easier management and querying.

---

## 🛠 Installation

### The Easy Way (User)
Install directly from GitHub using `pip`:

```bash
pip install git+https://github.com/woodleyj/terminal-assistant.git
```

### The Dev Way (Contributor)
If you want to modify the code or contribute:

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/woodleyj/terminal-assistant.git
    cd terminal-assistant
    ```
2.  **Install in editable mode**:
    ```bash
    pip install -e .
    ```

---

## 🏁 Getting Started

### 1. Get your Gemini API Key
TASS requires a Gemini API key to process your natural language queries. You can get one for free:
1.  Go to the [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Sign in with your Google account.
3.  Click **"Create API key"**.
4.  Copy your key for the next step.

### 2. Setup TASS
On your first run, TASS will guide you through a quick setup to securely save your key and choose your **primary alias**.

1.  Simply run:
    ```bash
    tass
    ```
2.  Follow the on-screen wizard to enter your key and choose a name (e.g., `ask`).

---

## 📖 Usage

### Command Line Mode
Pass your query directly to `tass` (or your chosen alias):

```powershell
# Commands are shell-aware!
tass "how do I find all python files recursively?"
```

### Interactive Mode
Run `tass` without arguments to open the interactive menu. Use your **arrow keys** to navigate:

-   **Ask a Question**: Direct chat or command generation.
-   **Manage Aliases**: Add or remove custom names for TASS.
-   **Manage Memory**: View or clear your interaction history.
-   **System Settings**: Configure the memory limit or edit the AI's system prompt.
-   **Shell Integration**: Automatically add aliases to your shell profile (`$PROFILE`, `.bashrc`, etc.).

### Management Commands
You can manage TASS settings directly from the terminal:

-   `tass /alias list` - View all active aliases.
-   `tass /integrate` - Automatically add TASS aliases to your shell profile.
-   `tass /memories show` - View stored interaction history.
-   `tass /prompt show` - View current AI instructions.
-   `tass /reset` - Completely wipe TASS configuration and history.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
