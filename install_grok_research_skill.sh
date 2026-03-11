#!/bin/bash
set -euo pipefail

DEFAULT_REMOTE_ZIP="https://github.com/bjdmh/grok-research/archive/refs/heads/dev.zip"
ZIP_URL="${ZIP_URL:-$DEFAULT_REMOTE_ZIP}"
CODEX_HOME="${CODEX_HOME:-$HOME/.codex}"
API_KEY="${GROK_API_KEY:-}"

usage() {
  cat <<'EOF'
Usage:
  install_grok_research_skill.sh --api-key <key> [--zip-url <url>] [--codex-home <path>]

Options:
  --api-key <key>      Grok API key
  --zip-url <url>      Skill zip download URL
  --codex-home <path>  Target CODEX_HOME
  -h, --help           Show this help

Notes:
  - If --api-key is omitted, GROK_API_KEY will be used.
  - The script installs the skill under $CODEX_HOME/skills/grok-research
  - The script writes the key to $CODEX_HOME/secrets/grok_api_key
  - Default ZIP_URL points to the GitHub `dev` branch archive of `bjdmh/grok-research`
  - GitHub public repo zip example:
    https://github.com/<owner>/<repo>/archive/refs/heads/<branch>.zip
  - Prefer a tag or commit zip in production for reproducibility
EOF
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --api-key)
      [ "$#" -ge 2 ] || { echo "error: --api-key requires a value" >&2; exit 1; }
      API_KEY="$2"
      shift 2
      ;;
    --zip-url)
      [ "$#" -ge 2 ] || { echo "error: --zip-url requires a value" >&2; exit 1; }
      ZIP_URL="$2"
      shift 2
      ;;
    --codex-home)
      [ "$#" -ge 2 ] || { echo "error: --codex-home requires a value" >&2; exit 1; }
      CODEX_HOME="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

API_KEY="$(printf '%s' "$API_KEY" | tr -d '\r' | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"

if [ -z "$API_KEY" ]; then
  echo "error: missing API key; pass --api-key or set GROK_API_KEY" >&2
  exit 1
fi

SKILLS_DIR="$CODEX_HOME/skills"
SECRETS_DIR="$CODEX_HOME/secrets"
TMP_ZIP="/tmp/grok-research-skill.zip"
TMP_DIR="/tmp/grok-research-install"

mkdir -p "$SKILLS_DIR"
mkdir -p "$SECRETS_DIR"
chmod 700 "$SECRETS_DIR"
rm -rf "$TMP_DIR"
mkdir -p "$TMP_DIR"

curl --fail --silent --show-error \
  --connect-timeout 10 \
  --max-time 60 \
  -L "$ZIP_URL" \
  -o "$TMP_ZIP"

unzip -oq "$TMP_ZIP" -d "$TMP_DIR"

SKILL_SOURCE_DIR=""
if [ -f "$TMP_DIR/grok-research/SKILL.md" ]; then
  SKILL_SOURCE_DIR="$TMP_DIR/grok-research"
else
  MATCH="$(find "$TMP_DIR" -path '*/grok-research/SKILL.md' | sed -n '1p' || true)"
  if [ -n "$MATCH" ]; then
    SKILL_SOURCE_DIR="$(dirname "$MATCH")"
  fi
fi

if [ -z "$SKILL_SOURCE_DIR" ] || [ ! -f "$SKILL_SOURCE_DIR/SKILL.md" ]; then
  echo "error: grok-research skill not found after unzip" >&2
  exit 1
fi

rm -rf "$SKILLS_DIR/grok-research"
cp -R "$SKILL_SOURCE_DIR" "$SKILLS_DIR/grok-research"

printf 'GROK_API_KEY=%s\n' "$API_KEY" > "$SECRETS_DIR/grok_api_key"
chmod 600 "$SECRETS_DIR/grok_api_key"

echo "installed: $SKILLS_DIR/grok-research"
echo "skill file: $SKILLS_DIR/grok-research/SKILL.md"
echo "secret file: $SECRETS_DIR/grok_api_key"
