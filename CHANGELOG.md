# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-19

### Added
- **Streaming Responses**: AI feedback now streams in real-time for a more responsive feel.
- **Command Breakdown**: Complex commands now include a "BREAKDOWN:" section deconstructing flags and syntax.
- **Automated Shell Integration**: New `/integrate` command and interactive menu option to automatically add aliases to PowerShell `$PROFILE`, `.bashrc`, and `.zshrc`.
- **Unit Testing Framework**: Added `tests/` directory with initial utility tests.
- **CI/CD Pipeline**: Added GitHub Actions workflow for automated linting and testing across Python versions 3.9-3.12.
- **Version Checker**: Basic version display and placeholder for future update notifications.
- **Environment Template**: Added `.env.example` for easier contributor setup.

### Changed
- Refactored `src/assistant/main.py` for better modularity and streaming support.
- Updated `pyproject.toml` with professional metadata and correct author information.
- Improved the Interactive Menu with better categorization and new shell integration options.
- Enhanced the System Prompt for more consistent formatting and native shell compatibility.

### Fixed
- Cleaned up redundant build artifacts and IDE-specific configuration files.

## [0.1.0] - 2026-03-18

### Added
- Initial release of TASS (Terminal Assistant).
- Basic natural language to terminal command translation.
- OS and Shell detection (PowerShell, CMD, Bash, Zsh).
- Local memory and interaction history.
- Clipboard auto-copy for suggested commands.
