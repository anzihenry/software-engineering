"""Actual loopback regression for query parsing and object-response ownership."""

from __future__ import annotations

import importlib.util
import json
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from urllib.error import HTTPError
from urllib.request import ProxyHandler, Request, build_opener


class DomainReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        path = Path(__file__).parent / "fixtures/domain-reference/server.py"
        spec = importlib.util.spec_from_file_location("domain_fixture", path)
        if spec is None or spec.loader is None:
            raise RuntimeError("reference fixture unavailable")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), module.Handler)
        cls.worker = Thread(target=cls.server.serve_forever, kwargs={"poll_interval": 0.05})
        cls.worker.start()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.worker.join(timeout=3)
        if cls.worker.is_alive():
            raise RuntimeError("reference worker did not stop")

    def request(self, query: str, actor: str) -> tuple[int, dict]:
        url = f"http://127.0.0.1:{self.server.server_port}/api/item?{query}"
        try:
            response = build_opener(ProxyHandler({})).open(
                Request(url, headers={"X-Reference-Actor": actor}), timeout=3
            )
        except HTTPError as error:
            response = error
        with response:
            return response.code, json.loads(response.read())

    def test_blank_parameters_cannot_bypass_format_validation(self) -> None:
        for query in ("version=1&version=", "unknown=", "fault=oops"):
            self.assertEqual(self.request(query, "actor-a"), (400, {"error": "invalid-input"}))

    def test_empty_zero_cannot_return_another_owners_item(self) -> None:
        status, body = self.request("item=beta&empty=0", "actor-b")
        self.assertEqual((status, body["item"], body["value"]), (200, "beta", "Reference item B"))
        self.assertEqual(self.request("item=alpha&empty=0", "actor-b")[0], 403)
        self.assertEqual(self.request("item=beta&empty=1", "actor-b")[1]["item"], None)
