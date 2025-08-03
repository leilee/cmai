#!/bin/bash

# Default version to install
VERSION="py"  # Default to Python version

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --sh|--bash)
            VERSION="sh"
            shift
            ;;
        --py|--python)
            VERSION="py"
            shift
            ;;
        -h|--help)
            echo "Usage: $0 [--sh|--bash|--py|--python] [-h|--help]"
            echo ""
            echo "Options:"
            echo "  --sh, --bash     Install bash version (git-commit.sh)"
            echo "  --py, --python   Install Python version (git-commit.py) [default]"
            echo "  -h, --help       Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0               # Install Python version (default)"
            echo "  $0 --py          # Install Python version"
            echo "  $0 --sh          # Install bash version"
            exit 0
            ;;
        *)
            echo "Error: Unknown argument $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Detect OS
OS="unknown"
case "$(uname)" in
    "Darwin")
        OS="macos"
        ;;
    "Linux")
        OS="linux"
        ;;
    "MINGW"*|"MSYS"*|"CYGWIN"*)
        OS="windows"
        ;;
esac

# Configuration based on version
if [ "$VERSION" = "py" ]; then
    SCRIPT_NAME="git-commit.py"
    SCRIPT_TYPE="Python"
else
    SCRIPT_NAME="git-commit.sh"
    SCRIPT_TYPE="Bash"
fi

if [ "$OS" = "windows" ]; then
    SCRIPT_DIR="$USERPROFILE/git-commit-ai"
    EXECUTABLE_NAME="cmai.sh"
else
    SCRIPT_DIR="$HOME/git-commit-ai"
    EXECUTABLE_NAME="cmai"
fi
CONFIG_DIR="${HOME:-$USERPROFILE}/.config/git-commit-ai"

# Debug function
debug_log() {
    echo "Install Script > $1"
}

# Check if script is being run with sudo (skip on Windows)
if [ "$OS" != "windows" ] && [ "$EUID" -eq 0 ]; then
    echo "Please do not run this script with sudo. Run as a regular user."
    exit 1
fi

# Check if the source script exists
SOURCE_SCRIPT="$(dirname "$0")/$SCRIPT_NAME"
if [ ! -f "$SOURCE_SCRIPT" ]; then
    echo "Error: $SCRIPT_NAME not found in the current directory."
    echo "Please ensure both git-commit.sh and git-commit.py are in the same directory as install.sh"
    exit 1
fi

echo "Installing $SCRIPT_TYPE version of git-commit-ai..."

# Create directory for the script
debug_log "Creating script directory"
mkdir -p "$SCRIPT_DIR"

# Copy the selected script to the directory
debug_log "Copying $SCRIPT_TYPE git-commit script"
cp "$SOURCE_SCRIPT" "$SCRIPT_DIR/$SCRIPT_NAME"
chmod +x "$SCRIPT_DIR/$SCRIPT_NAME"

# Handle executable installation
if [ "$OS" = "windows" ]; then
    # On Windows, we rely on PATH
    cp "$SCRIPT_DIR/$SCRIPT_NAME" "$SCRIPT_DIR/$EXECUTABLE_NAME"
else
    # Create symbolic link on Unix systems
    debug_log "Creating symbolic link"
    # Ensure ~/bin directory exists
    mkdir -p "$HOME/bin"
    ln -sf "$SCRIPT_DIR/$SCRIPT_NAME" "$HOME/bin/$EXECUTABLE_NAME"
fi

# Ensure config directory exists
debug_log "Ensuring config directory exists"
mkdir -p "$CONFIG_DIR"
if [ "$OS" != "windows" ]; then
    chmod 700 "$CONFIG_DIR"
fi

# Add instructions for API key
echo ""
echo "============================================"
echo "Installation complete!"
echo "============================================"
echo ""
echo "Installed: $SCRIPT_TYPE version ($SCRIPT_NAME)"
echo "Location: $SCRIPT_DIR/$SCRIPT_NAME"
echo "Executable: $EXECUTABLE_NAME"
echo ""

if [ "$VERSION" = "py" ]; then
    echo "Python version features:"
    echo "- Better code organization and maintainability"
    echo "- No external dependencies (uses built-in urllib)"
    echo "- Object-oriented design for easier extension"
    echo ""
fi

echo "Setup:"
echo "1. To set up your OpenRouter API key, run:"
echo "   cmai --api-key <your_openrouter_api_key>"
echo ""
echo "2. Or use alternative providers:"
echo "   cmai --use-ollama     # Use local Ollama"
echo "   cmai --use-lmstudio   # Use local LMStudio"
echo ""
echo "Usage:"
echo "- Stage your git changes with 'git add'"
echo "- Run 'cmai' to generate a commit message"
echo "- Use 'cmai --dry-run' to preview without committing"
echo "- Use 'cmai --help' for all options"
echo ""

if [ "$OS" != "windows" ]; then
    echo "Note: Make sure $HOME/bin is in your PATH to use 'cmai' command"
    echo "Add this to your shell profile if needed:"
    echo "export PATH=\"\$HOME/bin:\$PATH\""
fi
