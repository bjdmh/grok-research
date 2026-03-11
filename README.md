# grok-research

Utilities and a ready-to-install Codex skill for using Grok through the `chat.tabcode.cc` gateway with verification guardrails.

## Install the Skill

Copy and paste:

```bash
curl -fsSL https://raw.githubusercontent.com/bjdmh/grok-research/dev/install_grok_research_skill.sh -o install_grok_research_skill.sh
bash install_grok_research_skill.sh --api-key sk-...
```

One-line version:

```bash
curl -fsSL https://raw.githubusercontent.com/bjdmh/grok-research/dev/install_grok_research_skill.sh -o install_grok_research_skill.sh && bash install_grok_research_skill.sh --api-key sk-...
```

> [!IMPORTANT]
> This generic one-line install also honors `CODEX_HOME`.

```bash
export CODEX_HOME=~/.codex && curl -fsSL https://raw.githubusercontent.com/bjdmh/grok-research/dev/install_grok_research_skill.sh -o install_grok_research_skill.sh && bash install_grok_research_skill.sh --api-key sk-...
```

What the installer does:

- Downloads the `dev` branch archive of this repository by default
- Extracts the `grok-research` skill into `$CODEX_HOME/skills`
- Writes `GROK_API_KEY` into `$CODEX_HOME/secrets/grok_api_key`

You can override the source archive if needed:

```bash
bash install_grok_research_skill.sh --api-key sk-... --zip-url https://github.com/bjdmh/grok-research/archive/refs/heads/dev.zip
```

> [!IMPORTANT]
> One-line deployment targeting `~/.paolu-codex`.

```bash
export CODEX_HOME=~/.paolu-codex && curl -fsSL https://raw.githubusercontent.com/bjdmh/grok-research/dev/install_grok_research_skill.sh -o install_grok_research_skill.sh && bash install_grok_research_skill.sh --api-key sk-...
```

## Repository Contents

- `grok-research/` — installable Codex skill
- `install_grok_research_skill.sh` — installer
- `scripts/grok_chat.py` — local development copy of the client
- `references/prompt-patterns.md` — reusable prompt templates

## Local Usage

```bash
python grok-research/scripts/grok_chat.py \
  --system "You are a concise research assistant." \
  --prompt "List 5 current options for X, with risks and validation ideas."
```

The client resolves credentials in this order:

1. `GROK_API_KEY`
2. current working directory `.env` → `GROK_API_KEY=...`
3. `~/.config/grok/api_key`
4. `$CODEX_HOME/secrets/grok_api_key`

When `CODEX_HOME` is unset, both the installer and runtime client default to `~/.codex`.

## Notes

- Default endpoint is `https://chat.tabcode.cc/v1/chat/completions`
- Default model is `grok-4.20-beta`
- Override with `GROK_API_BASE` or `GROK_MODEL` when needed
