"""Loopback-only synthetic HTTP boundary; header actors are not production identity."""

from __future__ import annotations

import argparse
import json
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ITEMS = {"alpha": ("actor-a", "Reference item"), "beta": ("actor-b", "Reference item B")}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        request = urlsplit(self.path)
        query = parse_qs(request.query, keep_blank_values=True)
        actor = self.headers.get("X-Reference-Actor")
        item = query.get("item", ["alpha"])[0]
        owned_item = ITEMS.get(item)
        if request.path == "/":
            body = Path(__file__).with_name("index.html").read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        if request.path == "/api/item":
            time.sleep(0.2 if query.get("slow") == ["1"] else 0.1)
        status, body = 200, {"version": 1, "item": "alpha", "value": "Reference item"}
        if request.path == "/health":
            body = {"service": "domain-reference", "healthy": True}
        elif request.path != "/api/item":
            status, body = 404, {"error": "not-found"}
        elif actor not in {"actor-a", "actor-b"}:
            status, body = 401, {"error": "unauthorized"}
        elif len(request.query) > 1024 or any(
            key not in {"item", "version", "fault", "empty", "slow"}
            or len(values) != 1
            or (key in {"fault", "empty", "slow"} and values[0] not in {"0", "1"})
            for key, values in query.items()
        ):
            status, body = 400, {"error": "invalid-input"}
        elif owned_item is None or owned_item[0] != actor:
            status, body = 403, {"error": "forbidden"}
        elif query.get("version", ["1"])[0] != "1":
            status, body = 409, {"error": "unsupported-version"}
        elif query.get("fault", ["0"])[0] == "1":
            status, body = 503, {"error": "controlled-unavailable"}
        elif query.get("empty", ["0"])[0] == "1":
            body = {"version": 1, "item": None, "value": "Empty"}
        if status == 200 and request.path == "/api/item" and query.get("empty", ["0"]) != ["1"]:
            body = {"version": 1, "item": item, "value": ITEMS[item][1]}
        payload = json.dumps(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), Handler) as server:
        server.serve_forever()


if __name__ == "__main__":
    main()
