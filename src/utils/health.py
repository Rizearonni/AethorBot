import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn
from typing import Callable, Optional


class _ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


class _Handler(BaseHTTPRequestHandler):
    status_func: Optional[Callable[[], dict]] = None

    def _send_json(self, payload: dict, code: int = 200):
        data = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):  # noqa: N802 (http.server naming)
        if self.path not in ("/", "/health", "/healthz", "/ready", "/live"):
            self._send_json({"ok": False, "error": "not found"}, code=404)
            return
        status = {"ok": True}
        if _Handler.status_func:
            try:
                status.update(_Handler.status_func() or {})
            except Exception as e:  # pragma: no cover
                status.update({"ok": False, "error": str(e)})
        self._send_json(status)

    # Silence default logging to stderr; our app handles logs
    def log_message(self, format: str, *args):  # noqa: A003
        return


def start_health_server(port: int, status_func: Optional[Callable[[], dict]] = None):
    _Handler.status_func = status_func
    server = _ThreadingHTTPServer(("0.0.0.0", port), _Handler)
    thread = threading.Thread(target=server.serve_forever, name="health-server", daemon=True)
    thread.start()
    return server, thread


def make_status_func(bot, started_at: float) -> Callable[[], dict]:
    def _status() -> dict:
        latency_ms = None
        try:
            if getattr(bot, "latency", None) is not None:
                latency_ms = round(bot.latency * 1000, 2)
        except Exception:
            pass
        guilds = 0
        try:
            guilds = len(getattr(bot, "guilds", []) or [])
        except Exception:
            pass
        return {
            "uptime_seconds": int(time.time() - started_at),
            "guilds": guilds,
            "latency_ms": latency_ms,
            "ready": getattr(bot, "user", None) is not None,
        }

    return _status
