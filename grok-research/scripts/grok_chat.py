#!/usr/bin/env python3
import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


DEFAULT_BASE = "https://chat.tabcode.cc/v1/chat/completions"
DEFAULT_MODEL = "grok-4.20-beta"


def default_key_paths() -> tuple[Path, ...]:
    codex_home = Path(os.environ.get("CODEX_HOME", Path.home() / ".paolu-codex")).expanduser()
    return (
        Path.home() / ".config" / "grok" / "api_key",
        codex_home / "secrets" / "grok_api_key",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Minimal Grok client for chat.tabcode.cc with SSE-compatible parsing."
    )
    parser.add_argument("--system", default="", help="Optional system prompt.")
    parser.add_argument("--prompt", default="", help="User prompt text.")
    parser.add_argument(
        "--prompt-file",
        help="Read user prompt from file instead of --prompt.",
    )
    parser.add_argument(
        "--messages-file",
        help="JSON file containing full Chat Completions messages array.",
    )
    parser.add_argument("--model", default=os.environ.get("GROK_MODEL", DEFAULT_MODEL))
    parser.add_argument(
        "--url",
        default=os.environ.get("GROK_API_BASE", DEFAULT_BASE),
        help="Full API URL.",
    )
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument(
        "--raw-output",
        action="store_true",
        help="Do not strip think/agent traces from final text.",
    )
    parser.add_argument(
        "--dump-json",
        action="store_true",
        help="Print final structured result as JSON.",
    )
    return parser.parse_args()


def load_messages(args: argparse.Namespace) -> list[dict]:
    if args.messages_file:
        raw = Path(args.messages_file).read_text(encoding="utf-8")
        messages = json.loads(raw)
        if not isinstance(messages, list):
            raise ValueError("--messages-file must contain a JSON array")
        return messages

    prompt = args.prompt
    if args.prompt_file:
        prompt = Path(args.prompt_file).read_text(encoding="utf-8")
    if not prompt and not sys.stdin.isatty():
        prompt = sys.stdin.read()
    if not prompt:
        raise ValueError("Provide --prompt, --prompt-file, stdin, or --messages-file")

    messages: list[dict] = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": prompt})
    return messages


def extract_text_from_chunk(obj: dict) -> str:
    choices = obj.get("choices") or []
    if not choices:
        return ""
    choice = choices[0] or {}
    delta = choice.get("delta") or {}
    if isinstance(delta.get("content"), str):
        return delta["content"]
    message = choice.get("message") or {}
    if isinstance(message.get("content"), str):
        return message["content"]
    return ""


def clean_output(text: str) -> str:
    cleaned = re.sub(r"<think>.*?</think>\s*", "", text, flags=re.S)
    cleaned = re.sub(r"^\[Agent[^\n]*\]\s*", "", cleaned, flags=re.M)
    cleaned = re.sub(r"^\s*AgentThink:.*$", "", cleaned, flags=re.M)
    return cleaned.strip()


def parse_api_key_text(raw_text: str) -> str:
    text = raw_text.strip()
    if not text:
        return ""

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("GROK_API_KEY="):
            return stripped.split("=", 1)[1].strip().strip("'\"")

    return text


def load_api_key_from_dotenv() -> str:
    dotenv_path = Path.cwd() / ".env"
    try:
        raw_text = dotenv_path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("GROK_API_KEY="):
            return stripped.split("=", 1)[1].strip().strip("'\"")
    return ""


def load_api_key() -> str:
    env_key = os.environ.get("GROK_API_KEY", "").strip()
    if env_key:
        return env_key

    dotenv_key = load_api_key_from_dotenv()
    if dotenv_key:
        return dotenv_key

    for path in default_key_paths():
        try:
            key = parse_api_key_text(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            continue
        if key:
            return key
    return ""


def call_grok(url: str, api_key: str, payload: dict, timeout: int) -> tuple[str, str]:
    data = json.dumps(payload).encode("utf-8")
    req = Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    parts: list[str] = []
    content_type = ""
    try:
        with urlopen(req, timeout=timeout) as resp:
            content_type = resp.headers.get("Content-Type", "")
            for raw_line in resp:
                line = raw_line.decode("utf-8", errors="replace").strip()
                if not line:
                    continue
                if line.startswith("data: "):
                    data_line = line[6:]
                    if data_line == "[DONE]":
                        break
                    try:
                        obj = json.loads(data_line)
                    except json.JSONDecodeError:
                        continue
                    parts.append(extract_text_from_chunk(obj))
                else:
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    parts.append(extract_text_from_chunk(obj))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code}: {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Network error: {exc}") from exc
    return "".join(parts), content_type


def main() -> int:
    args = parse_args()
    api_key = load_api_key()
    if not api_key:
        codex_secret_path = default_key_paths()[1]
        print(
            "error: missing GROK_API_KEY and no default key file found at "
            f".env, ~/.config/grok/api_key, or {codex_secret_path}",
            file=sys.stderr,
        )
        return 2

    try:
        messages = load_messages(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    payload = {
        "model": args.model,
        "messages": messages,
        "stream": False,
    }

    try:
        text, content_type = call_grok(args.url, api_key, payload, args.timeout)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    final_text = text if args.raw_output else clean_output(text)
    if args.dump_json:
        print(
            json.dumps(
                {
                    "model": args.model,
                    "url": args.url,
                    "content_type": content_type,
                    "messages": messages,
                    "text": final_text,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(final_text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
