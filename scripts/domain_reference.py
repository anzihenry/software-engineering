"""Collect real HTTP observations from the loopback synthetic reference only."""

from __future__ import annotations

import argparse
import json
import platform
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener


def probe(port: int) -> dict:
    def request(query: str, actor: str = "actor-a") -> dict:
        url = f"http://127.0.0.1:{port}/api/item{query}"
        headers = {"X-Reference-Actor": actor} if actor else {}
        started = time.monotonic()
        try:
            response = build_opener(ProxyHandler({})).open(Request(url, headers=headers), timeout=2)
        except HTTPError as error:
            response = error
        with response:
            return {
                "url": url,
                "actor": actor,
                "status": response.code,
                "body": json.loads(response.read()),
                "elapsed_ms": (time.monotonic() - started) * 1000,
            }

    timeout_started = time.monotonic()
    try:
        with build_opener(ProxyHandler({})).open(
            Request(
                f"http://127.0.0.1:{port}/api/item?slow=1", headers={"X-Reference-Actor": "actor-a"}
            ),
            timeout=0.05,
        ) as response:
            response.read()
        timeout = {"state": "unexpected-response"}
    except TimeoutError:
        timeout = {
            "state": "client-timeout",
            "elapsed_ms": (time.monotonic() - timeout_started) * 1000,
        }
    observations = {
        "normal": request(""),
        "anonymous": request("", ""),
        "other-owner": request("?item=beta", "actor-b"),
        "reverse-object-denied": request("?item=alpha", "actor-b"),
        "object-denied": request("?item=beta"),
        "version-denied": request("?version=2"),
        "failure": request("?fault=1"),
        "recovered": request(""),
        "input-size": request("?item=" + "x" * 2048),
        "input-format": request("?version=1&version=2"),
        "blank-duplicate": request("?version=1&version="),
        "blank-unknown": request("?unknown="),
        "invalid-flag": request("?fault=oops"),
        "other-owner-empty-zero": request("?empty=0&item=beta", "actor-b"),
        "input-path": request("?item=../../etc/passwd"),
        "input-injection": request("?item=SELECT%20*%20FROM%20items"),
        "input-version": request("?version=NaN"),
    }
    with ThreadPoolExecutor(max_workers=4) as pool:
        concurrent = list(pool.map(request, [""] * 16))
    return {
        "executed_at": datetime.now(UTC).isoformat(),
        "python": platform.python_version(),
        "observations": observations,
        "concurrent": concurrent,
        "timeout": timeout,
        "limits": (
            "16 immutable reads / 4 workers; "
            "no database, load-capacity or production identity claim"
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.write_text(
        json.dumps(probe(args.port), ensure_ascii=False, indent=2), encoding="utf-8"
    )


if __name__ == "__main__":
    main()
