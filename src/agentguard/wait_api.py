"""Bounded readiness check for the repo-owned local demo runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time
from urllib.error import URLError
from urllib.request import urlopen


def _port_from_ready_file(path: Path, attempts: int) -> int:
    for _ in range(attempts):
        try:
            port = int(path.read_text(encoding="ascii").strip())
            if 1024 <= port <= 65535:
                return port
        except (OSError, UnicodeError, ValueError):
            pass
        time.sleep(0.1)
    raise SystemExit("local API did not publish a valid port")


def wait_for_api(port: int, attempts: int) -> None:
    url = f"http://localhost:{port}/api/health"
    for _ in range(attempts):
        try:
            with urlopen(url, timeout=1) as response:
                payload = json.load(response)
            if (
                payload.get("status") == "ok"
                and payload.get("mode")
                in {
                    "local-synthetic",
                    "local-synthetic-compliance",
                    "live-aws-read-only",
                }
            ):
                return
        except (OSError, URLError, ValueError, json.JSONDecodeError):
            pass
        time.sleep(0.1)
    raise SystemExit("local API readiness check failed")


def main() -> None:
    parser = argparse.ArgumentParser(description="Wait for the local AgentGuard API")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--port", type=int)
    source.add_argument("--ready-file", type=Path)
    parser.add_argument("--attempts", type=int, default=50)
    args = parser.parse_args()
    if not 1 <= args.attempts <= 100:
        parser.error("attempts must be between 1 and 100")

    port = args.port
    if args.ready_file is not None:
        port = _port_from_ready_file(args.ready_file, args.attempts)
    if port is None or not 1024 <= port <= 65535:
        parser.error("port must be between 1024 and 65535")

    wait_for_api(port, args.attempts)
    print(port)


if __name__ == "__main__":
    main()
