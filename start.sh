#!/bin/bash
cd "$(dirname "$0")"

echo ""
echo "========================================"
echo "  Autonomous Coding Agent"
echo "========================================"
echo ""

# Check if Claude CLI is installed
CLAUDE_CMD=""

# First check if claude is already in PATH
if command -v claude &> /dev/null; then
    CLAUDE_CMD="claude"
# Check common macOS installation path
elif [ -x "$HOME/.claude/local/bin/claude" ]; then
    CLAUDE_CMD="$HOME/.claude/local/bin/claude"
    export PATH="$HOME/.claude/local/bin:$PATH"
# Check Linux installation path
elif [ -x "$HOME/.local/bin/claude" ]; then
    CLAUDE_CMD="$HOME/.local/bin/claude"
    export PATH="$HOME/.local/bin:$PATH"
fi

if [ -z "$CLAUDE_CMD" ]; then
    echo "[ERROR] Claude CLI not found"
    echo ""
    echo "Please install Claude CLI first:"
    echo "  curl -fsSL https://claude.ai/install.sh | bash"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "[OK] Claude CLI found at: $CLAUDE_CMD"

# Check if user has credentials
CLAUDE_CREDS="$HOME/.claude/.credentials.json"
if [ -f "$CLAUDE_CREDS" ]; then
    echo "[OK] Claude credentials found"
else
    echo "[!] Not authenticated with Claude"
    echo ""
    echo "You need to run 'claude login' to authenticate."
    echo "This will open a browser window to sign in."
    echo ""
    read -p "Would you like to run 'claude login' now? (y/n): " LOGIN_CHOICE

    if [[ "$LOGIN_CHOICE" =~ ^[Yy]$ ]]; then
        echo ""
        echo "Running 'claude login'..."
        echo "Complete the login in your browser, then return here."
        echo ""
        $CLAUDE_CMD login

        # Check if login succeeded
        if [ -f "$CLAUDE_CREDS" ]; then
            echo ""
            echo "[OK] Login successful!"
        else
            echo ""
            echo "[ERROR] Login failed or was cancelled."
            echo "Please try again."
            exit 1
        fi
    else
        echo ""
        echo "Please run 'claude login' manually, then try again."
        exit 1
    fi
fi

echo ""

# Check if venv exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --quiet

# Run the app
python start.py
