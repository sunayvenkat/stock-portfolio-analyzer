
#Serves the dashboard and its JSON API using only the Python standard library
#Run from the project root: python web/server.py   (HOST and PORT env vars override 127.0.0.1:8000)
import json
import logging
import math
import os
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

ROOT_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import numpy as np
from yfinance.exceptions import YFRateLimitError

from web import api
from utils.logger import logger


STATIC_DIR = os.path.join(ROOT_DIR, "web", "static")
MAX_BODY_BYTES = 64 * 1024


#Converts numpy values and NaN into plain JSON (browsers reject a bare NaN)
def to_json_safe(value):
    if isinstance(value, dict):
        return {str(key): to_json_safe(item) for key, item in value.items()}

    if isinstance(value, (list, tuple)):
        return [to_json_safe(item) for item in value]

    if isinstance(value, np.generic):
        value = value.item()

    if isinstance(value, float) and not math.isfinite(value):
        return None

    return value


class DashboardHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    #Holdings never appear in URLs, and outbound news links carry no referrer
    def end_headers(self):
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("X-Content-Type-Options", "nosniff")
        super().end_headers()

    def send_json(self, status, payload):
        body = json.dumps(to_json_safe(payload)).encode("utf-8")

        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    #Bad input becomes a 400 with its message; anything else is logged and reported as a data outage
    def respond(self, handler, argument):
        try:
            self.send_json(200, handler(argument))

        except (ValueError, TypeError) as error:
            self.send_json(400, {"error": str(error)})

        except YFRateLimitError:
            self.send_json(503, {"error": "Yahoo Finance is limiting requests from this server. Try again in a few minutes."})

        except Exception:
            logger.exception("Request failed: %s", self.path)

            self.send_json(502, {"error": "Market data is unavailable right now. Try again in a minute."})

    def do_POST(self):
        handler = {
            "/api/analyze": api.analyze,
            "/api/simulate": api.simulate,
            "/api/news": api.news,
        }.get(urlparse(self.path).path)

        if handler is None:
            return self.send_json(404, {"error": "Not found."})

        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self.send_json(400, {"error": "Invalid Content-Length."})

        if length > MAX_BODY_BYTES:
            return self.send_json(413, {"error": "Request is too large."})

        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except (json.JSONDecodeError, UnicodeDecodeError):
            return self.send_json(400, {"error": "Request body must be JSON."})

        if not isinstance(payload, dict):
            return self.send_json(400, {"error": "Request body must be a JSON object."})

        self.respond(handler, payload)


if __name__ == "__main__":
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))

    server = ThreadingHTTPServer((host, port), DashboardHandler)

    logger.info("Portfolio Analyzer running at http://%s:%d", host, port)

    #The data layer logs every ticker it fetches at INFO; a public server keeps visitors' holdings out of its logs
    logger.setLevel(logging.WARNING)

    server.serve_forever()
