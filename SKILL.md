---
name: grok-research
description: Use this skill when you want to call Grok through the `chat.tabcode.cc` gateway for time-sensitive research, external fact discovery, option generation, risk review, or critique of a draft plan. It is especially useful when a task benefits from web-aware model output but still requires local verification, source skepticism, and anti-sycophancy guardrails.
---

# Grok Research

## Overview

This skill wraps Grok usage into a repeatable workflow that is reusable across repositories and domains. It includes a small client script for `chat.tabcode.cc`, handles SSE-style responses, and adds guardrails so Grok is used as a candidate-generator and critic rather than a source of unquestioned truth.

## When To Use

Use this skill when at least one of these is true:

1. The task depends on recent external information and local repo context alone is insufficient.
2. You need candidate approaches, tradeoffs, failure modes, or implementation risks.
3. You want a fast second opinion on a plan, migration, debugging path, or architecture choice.
4. You need a structured research artifact such as a checklist, decision table, or validation plan.

Do not use this skill for:

1. Purely local, deterministic edits.
2. Tasks involving secrets in prompts beyond what is strictly required.
3. Final high-stakes conclusions without a separate verification step.

## Quick Start

Prerequisites:

1. Export `GROK_API_KEY`.
2. Or put `GROK_API_KEY=...` in the current working directory `.env`.
3. Never hardcode keys into repo files, prompts, or logs.
4. If you want a machine-local default without exporting env vars every time, store the key in `~/.config/grok/api_key` or `$CODEX_HOME/secrets/grok_api_key` with `chmod 600`.
5. The key file accepts either plain text (`sk-...`) or `.env` style (`GROK_API_KEY=sk-...`).

Minimal call:

```bash
python "${CODEX_HOME:-$HOME/.codex}/skills/grok-research/scripts/grok_chat.py" \
  --system "You are a concise research assistant." \
  --prompt "List 5 current options for X, with risks and validation ideas."
```

The client resolves credentials in this order:

1. `GROK_API_KEY`
2. current working directory `.env` → `GROK_API_KEY=...`
3. `~/.config/grok/api_key`
4. `$CODEX_HOME/secrets/grok_api_key` (defaults to `~/.codex/secrets/grok_api_key` when `CODEX_HOME` is unset)

For multi-turn or fully controlled prompts, create a `messages.json` file and pass `--messages-file`. The script accepts standard Chat Completions `messages`.

## Default Workflow

### 1. Frame the task

Ask Grok for one of these outputs first, not for the final answer:

1. Research plan
2. Options table
3. Risk checklist
4. Validation protocol

This reduces premature certainty and makes later verification easier.

### 2. Force a critique pass

Grok can be overly agreeable. Always add a second pass that asks for:

1. Failure conditions
2. Negative side effects
3. Cases where a simpler baseline is better
4. What evidence would falsify the recommendation

Use the prompts in `references/prompt-patterns.md`.

### 3. Verify locally or with primary sources

Treat Grok output as candidate material. Verify important claims with one or more of:

1. Repository code or tests
2. Official documentation
3. Direct API responses
4. Reproducible commands

### 4. Produce a tagged summary

Split the result into:

1. Verified facts
2. Inferences
3. Unverified claims
4. Recommended next action

## Anti-Sycophancy Guardrails

Use all of these by default for decisions that matter:

1. Ask for disagreement explicitly: “What is wrong with the first recommendation?”
2. Request a conservative baseline and compare against it.
3. Ask for triggers that would make the recommendation invalid.
4. Ask for hidden costs: latency, maintenance, complexity, lock-in, compliance, data quality.
5. Prefer prompts that require evidence tiers and confidence labels.
6. Never present Grok output as final truth unless independently verified.

If the first answer sounds unusually confident or flattering, do a counter-prompt before acting.

## Output Hygiene

The gateway may return `text/event-stream` even when `stream=false`. The bundled script already:

1. Parses `data: ...` chunks
2. Concatenates `delta.content`
3. Stops on `[DONE]`
4. Strips `<think>...</think>` and `AgentThink` style traces by default

Use `--raw-output` only when you intentionally want the unfiltered model text.

## Files

1. `scripts/grok_chat.py` — minimal reusable Grok client with SSE parsing
2. `references/prompt-patterns.md` — reusable prompt patterns for research, critique, and synthesis

## Notes

1. Default endpoint is `https://chat.tabcode.cc/v1/chat/completions`.
2. Default model is `grok-4.20-beta`.
3. Override with `GROK_API_BASE` or `GROK_MODEL` when needed.
