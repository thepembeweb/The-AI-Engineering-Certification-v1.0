# Installing Claude Code

## What is Claude Code?

Claude Code is Anthropic's agentic coding tool. It runs in your terminal, and unlike a chat window it can **act**: it reads your files, edits them, runs shell commands, executes your tests, and iterates until the job is done — all inside a permission system that keeps you in control.

Under the hood it is an **agent loop**: the model decides which tool to call (read a file, run a command, make an edit), observes the result, and decides what to do next. You have been building loops like this by hand with LangGraph since Session 2 — this is what one looks like as a polished product. In Guide 3 you will use the **Claude Agent SDK** to embed this exact loop in your own applications.

## System Requirements

| Requirement | Minimum                                                                                        |
| :---------- | :--------------------------------------------------------------------------------------------- |
| OS          | macOS 13.0+, Windows 10 1809+ / Server 2019+, Ubuntu 20.04+ / Debian 10+, Alpine 3.19+         |
| Hardware    | 4 GB+ RAM, x64 or ARM64                                                                        |
| Shell       | Bash, Zsh, PowerShell, or CMD                                                                  |
| Network     | Internet connection required                                                                   |
| Node.js     | **Only** needed for the npm install method (v22+); the native installer has no Node dependency |

> **Windows users:** Claude Code runs natively in PowerShell/CMD, and also works great inside WSL if you prefer a Linux environment.

## Install

### Option A: Native installer (recommended)

**macOS / Linux / WSL:**

```bash
curl -fsSL https://claude.ai/install.sh | bash
```

**Windows (PowerShell):**

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Windows (CMD):**

```batch
curl -fsSL https://claude.ai/install.cmd -o install.cmd && install.cmd && del install.cmd
```

The native installer is self-contained (no Node.js needed) and **auto-updates**: it checks for a new version on startup and applies it the next time you launch.

### Option B: Homebrew (macOS / Linux)

```bash
brew install --cask claude-code          # stable channel (~1 week behind)
brew install --cask claude-code@latest   # latest channel
```

Update manually with `brew upgrade claude-code`.

### Option C: WinGet (Windows)

```powershell
winget install Anthropic.ClaudeCode
```

Update manually with `winget upgrade Anthropic.ClaudeCode`.

### Option D: npm (requires Node.js 22+)

```bash
npm install -g @anthropic-ai/claude-code
```

Update manually with `npm install -g @anthropic-ai/claude-code@latest`.

> **Which one should I pick?** Use the **native installer** unless you have a reason not to — it needs no Node.js and keeps itself up to date. Package-manager installs (brew/winget/apt) fit teams that already manage software that way, at the cost of manual updates.

## First Run & Authentication

Navigate to any project directory and start Claude Code:

```bash
cd your-project
claude
```

On first run, your browser opens a login page (if it doesn't, press `c` in the terminal to copy the URL). Sign in with one of:

1. **Claude subscription (Pro / Max / Team / Enterprise)** — usage is included in your plan. This is the simplest option for this course if you have a subscription.
2. **Claude Console account** — usage is billed against API credits. A "Claude Code" workspace is created automatically in your Console so you can track spend.
3. **Enterprise cloud credentials** — Amazon Bedrock, Google Vertex, or Microsoft Foundry (you won't need these for this course).

> **Working over SSH, in a container, or in WSL2 where the browser callback can't reach the terminal?** The login page will show a code you can paste back into the terminal instead.

You can switch accounts at any time from inside a session with `/login` and `/logout`.

## Verify Your Install

```bash
claude --version    # prints the installed version
claude doctor       # runs a diagnostic health check on your installation
```

Then start a session and confirm the agent can actually see your project:

```bash
claude "give me a one-paragraph overview of this project"
```

If Claude reads files and answers, you're fully set up.

## Updating

```bash
claude update
```

Native installs also auto-update on startup. You can pin behavior in `~/.claude/settings.json`:

```json
{
  "autoUpdatesChannel": "stable",
  "env": { "DISABLE_AUTOUPDATER": "1" }
}
```

(Leave auto-updates on for this course — you want current features.)

## Troubleshooting Quick Hits

- **`claude: command not found`** — restart your terminal (the installer appends to your shell profile); check `~/.local/bin` is on your `PATH`.
- **Browser login loop / no callback** — press `c` for the copyable URL, or use the paste-a-code flow.
- **Corporate proxy or VPN issues** — run `claude doctor` first; it diagnoses most network problems.
- **npm permission errors** — prefer the native installer; it avoids global npm entirely.

## ✅ Checkpoint (Task 1)

You are done with this guide when:

- [ ] `claude --version` prints a version
- [ ] `claude doctor` reports a healthy install
- [ ] You have authenticated and run one prompt against a real project

**Next:** [`02_Using_Claude_Code.md`](./02_Using_Claude_Code.md) — learn to drive Claude Code, then use it to scaffold your chat app.
