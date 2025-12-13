# Autonomous Coding Agent Demo

A minimal harness demonstrating long-running autonomous coding with the Claude Agent SDK. This demo implements a two-agent pattern (initializer + coding agent) that can build complete applications over multiple sessions.

## Prerequisites

**Required:** Install the latest versions of both Claude Code and the Claude Agent SDK:

```bash
# Install Claude Code CLI (latest version required)
npm install -g @anthropic-ai/claude-code

# Install Python dependencies
pip install -r requirements.txt
```

Verify your installations:
```bash
claude --version  # Should be latest version
pip show claude-code-sdk  # Check SDK is installed
```

## Configuration

Copy the example environment file and add your credentials:

```bash
cp .env.example .env
```

Edit `.env` and configure at least one authentication method:

```bash
# Authentication (at least one required)
ANTHROPIC_API_KEY=your-api-key-here
# OR
CLAUDE_CODE_OAUTH_TOKEN=your-oauth-token-here

# Optional: N8N webhook for progress notifications
# PROGRESS_N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/...
```

**Getting credentials:**
- **API Key:** Get from https://console.anthropic.com/
- **OAuth Token:** Run `claude setup-token` if using Claude Code CLI authentication

## Quick Start

```bash
python autonomous_agent_demo.py --project-dir ./my_project
```

For testing with limited iterations:
```bash
python autonomous_agent_demo.py --project-dir ./my_project --max-iterations 3
```

## Important Timing Expectations

> **Warning: This demo takes a long time to run!**

- **First session (initialization):** The agent generates a `feature_list.json` with 200 test cases. This takes several minutes and may appear to hang - this is normal. The agent is writing out all the features.

- **Subsequent sessions:** Each coding iteration can take **5-15 minutes** depending on complexity.

- **Full app:** Building all 200 features typically requires **many hours** of total runtime across multiple sessions.

**Tip:** The 200 features parameter in the prompts is designed for comprehensive coverage. If you want faster demos, you can modify `prompts/initializer_prompt.md` to reduce the feature count (e.g., 20-50 features for a quicker demo).

## How It Works

### Two-Agent Pattern

1. **Initializer Agent (Session 1):** Reads `app_spec.txt`, creates `feature_list.json` with 200 test cases, sets up project structure, and initializes git.

2. **Coding Agent (Sessions 2+):** Picks up where the previous session left off, implements features one by one, and marks them as passing in `feature_list.json`.

### Session Management

- Each session runs with a fresh context window
- Progress is persisted via `feature_list.json` and git commits
- The agent auto-continues between sessions (3 second delay)
- Press `Ctrl+C` to pause; run the same command to resume

## Security Model

This demo uses a defense-in-depth security approach (see `security.py` and `client.py`):

1. **OS-level Sandbox:** Bash commands run in an isolated environment
2. **Filesystem Restrictions:** File operations restricted to the project directory only
3. **Bash Allowlist:** Only specific commands are permitted:
   - File inspection: `ls`, `cat`, `head`, `tail`, `wc`, `grep`
   - Node.js: `npm`, `node`
   - Version control: `git`
   - Process management: `ps`, `lsof`, `sleep`, `pkill` (dev processes only)

Commands not in the allowlist are blocked by the security hook.

## Project Structure

```
autonomous-coding/
├── autonomous_agent_demo.py  # Main entry point
├── agent.py                  # Agent session logic
├── client.py                 # Claude SDK client configuration
├── security.py               # Bash command allowlist and validation
├── progress.py               # Progress tracking utilities
├── prompts.py                # Prompt loading utilities
├── prompts/
│   ├── app_spec.txt          # Application specification
│   ├── initializer_prompt.md # First session prompt
│   └── coding_prompt.md      # Continuation session prompt
├── requirements.txt          # Python dependencies
└── .env.example              # Environment variables template
```

## Generated Project Structure

After running, your project directory will contain:

```
my_project/
├── feature_list.json         # Test cases (source of truth)
├── app_spec.txt              # Copied specification
├── init.sh                   # Environment setup script
├── claude-progress.txt       # Session progress notes
├── .claude_settings.json     # Security settings
└── [application files]       # Generated application code
```

## Running the Generated Application

After the agent completes (or pauses), you can run the generated application:

```bash
cd generations/my_project

# Run the setup script created by the agent
./init.sh

# Or manually (typical for Node.js apps):
npm install
npm run dev
```

The application will typically be available at `http://localhost:3000` or similar (check the agent's output or `init.sh` for the exact URL).

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--project-dir` | Directory for the project | `./autonomous_demo_project` |
| `--max-iterations` | Max agent iterations | Unlimited |
| `--model` | Claude model to use | `claude-sonnet-4-5-20250929` |

## Customization

### Changing the Application

Edit `prompts/app_spec.txt` to specify a different application to build.

### Adjusting Feature Count

Edit `prompts/initializer_prompt.md` and change the "200 features" requirement to a smaller number for faster demos.

### Modifying Allowed Commands

Edit `security.py` to add or remove commands from `ALLOWED_COMMANDS`.

## N8N Webhook Integration (Optional)

The agent can send progress notifications to an N8N webhook when tests pass. This is useful for monitoring long-running agent sessions.

### Setup

Add the webhook URL to your `.env` file:

```bash
PROGRESS_N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/your-webhook-id
```

### Webhook Payload

When test progress increases, the agent sends a POST request with the following JSON structure (wrapped in an array as N8N expects):

```json
[
  {
    "event": "test_progress",
    "passing": 45,
    "total": 200,
    "percentage": 22.5,
    "previous_passing": 42,
    "tests_completed_this_session": 3,
    "completed_tests": [
      "[Authentication] User can log in with valid credentials",
      "[Dashboard] Display user profile information",
      "[API] GET /users endpoint returns user list"
    ],
    "project": "my_project",
    "timestamp": "2025-01-15T14:30:00.000Z"
  }
]
```

### Payload Fields

| Field | Type | Description |
|-------|------|-------------|
| `event` | string | Always `"test_progress"` |
| `passing` | number | Current number of passing tests |
| `total` | number | Total number of tests |
| `percentage` | number | Percentage complete (0-100) |
| `previous_passing` | number | Passing tests before this update |
| `tests_completed_this_session` | number | Tests completed since last notification |
| `completed_tests` | array | Descriptions of newly passing tests |
| `project` | string | Project name (from `--project-dir` argument) |
| `timestamp` | string | ISO 8601 timestamp (UTC) |

### Notes

- Notifications are only sent when progress **increases** (not on every check)
- If the webhook URL is not configured, no notifications are sent (silent skip)
- Failed webhook calls are logged but don't stop the agent

## Troubleshooting

**"Appears to hang on first run"**
This is normal. The initializer agent is generating 200 detailed test cases, which takes significant time. Watch for `[Tool: ...]` output to confirm the agent is working.

**"Command blocked by security hook"**
The agent tried to run a command not in the allowlist. This is the security system working as intended. If needed, add the command to `ALLOWED_COMMANDS` in `security.py`.

**"API key not set"**
Ensure you have configured either `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` in your `.env` file. See the [Configuration](#configuration) section.

## License

Internal Anthropic use.
