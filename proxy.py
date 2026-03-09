# proxy.py - Ultra-dynamic proxy: target URL passed via ?url= query parameter
# Example: http://localhost:8000/proxy?url=https://api.x.ai/v1/chat/completions

import http.server
import socketserver
import urllib.request
import urllib.parse
import json
import sys
from urllib.error import HTTPError, URLError

ALLOWED_ORIGIN = "*"  # Or restrict to http://localhost:* etc.

# Optional: whitelist domains to prevent open proxy abuse (strongly recommended!)
ALLOWED_DOMAINS = [
    "api.x.ai",
    "api.openai.com",
    "api.anthropic.com",
    "api.groq.com",
    "api.together.xyz",
    "api.fireworks.ai",
    # "generativelanguage.googleapis.com",  # add others as needed
]

# Headers to exclude (browser / connection internals)
EXCLUDE_HEADERS = [
    "host", "connection", "content-length", "accept-encoding",
    "origin", "referer",
]

class UltraProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers",
                         "Content-Type, Authorization, x-api-key, anthropic-version, "
                         "OpenAI-Organization, User-Agent, Accept, Accept-Language")
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/proxy":
            self.send_error(404, "Use /proxy?url=https://...")
            return

        query = urllib.parse.parse_qs(parsed.query)
        target_url = query.get("url", [None])[0]

        if not target_url:
            self.send_error(400, "Missing ?url= parameter (full HTTPS endpoint)")
            return

        if not target_url.startswith("https://"):
            self.send_error(400, "?url must be a https:// URL")
            return

        # Optional security: check domain whitelist
        target_host = urllib.parse.urlparse(target_url).hostname
        if ALLOWED_DOMAINS and target_host not in ALLOWED_DOMAINS:
            self.send_error(403, f"Domain {target_host} not allowed. Add to ALLOWED_DOMAINS if trusted.")
            return

        # Read body once
        content_length = int(self.headers.get("Content-Length", 0))
        raw_body = self.rfile.read(content_length)

        # Optional: validate JSON (not required, but helps early fail)
        try:
            json.loads(raw_body)
        except json.JSONDecodeError:
            self.send_error(400, "Request body must be valid JSON")
            return

        # Forward headers
        forward_headers = {}
        for key, value in self.headers.items():
            if key.lower() not in EXCLUDE_HEADERS:
                forward_headers[key] = value
        forward_headers["Content-Type"] = "application/json"

        req = urllib.request.Request(
            target_url,
            data=raw_body,
            headers=forward_headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req) as resp:
                response_data = resp.read()
                self.send_response(resp.getcode())
                self.send_header("Content-Type", resp.headers.get("Content-Type", "application/json"))
                self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
                self.end_headers()
                self.wfile.write(response_data)
        except HTTPError as e:
            self.send_response(e.code)
            self.send_header("Content-Type", e.headers.get("Content-Type", "text/plain"))
            self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
            self.end_headers()
            self.wfile.write(e.read())
        except URLError as e:
            self.send_error(502, f"Upstream connection failed: {str(e)}")
        except Exception as e:
            self.send_error(500, str(e))

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"Ultra-dynamic proxy running on http://localhost:{port}/proxy?url=...")
    print("Example: http://localhost:8000/proxy?url=https://api.x.ai/v1/chat/completions")
    print(f"Allowed domains (optional whitelist): {', '.join(ALLOWED_DOMAINS) if ALLOWED_DOMAINS else 'ALL https domains (open proxy - use with caution)'}")
    with socketserver.TCPServer(("", port), UltraProxyHandler) as httpd:
        httpd.serve_forever()