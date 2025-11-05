#!/usr/bin/env python3
"""serve_repo.py

Lightweight local HTTP server to browse this repository as a simple website.

Usage:
  python3 serve_repo.py            # serves at http://127.0.0.1:8000
  python3 serve_repo.py --port 9000 --bind 0.0.0.0

This script does NOT move or delete any files. It runs an HTTP server
rooted at the repository directory and provides a friendly index page
rendered from README.md (if present) plus clickable listings of files
and folders.

Optional: if the Python `markdown` package is installed, README.md will
be rendered as HTML. Otherwise the README will be shown as preformatted
text.
"""
from http import HTTPStatus
import argparse
import os
import socketserver
import urllib
import html
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))


def html_escape(s: str) -> str:
    return html.escape(s)


def build_index_html(root_path: str) -> str:
    """Build a minimal homepage that exposes only `Assignments/` (and
    `docs/` if present) per the user's request.
    """
    items = []
    if os.path.isdir(os.path.join(root_path, "Assignments")):
        items.append(("Assignments", "/Assignments/"))
    if os.path.isdir(os.path.join(root_path, "docs")):
        items.append(("docs", "/docs/"))

    list_items = [
        f'<li><a href="{html_escape(href)}">{html_escape(name)}</a></li>'
        for name, href in items
    ]
    list_html = "\n".join(list_items)

    html_page = f"""<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>{html_escape(os.path.basename(root_path))} - Assignments</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; margin: 2rem; }}
        nav {{ margin-top:1rem }}
    </style>
</head>
<body>
    <h1>{html_escape(os.path.basename(root_path))}</h1>
    <p>This site exposes the course Assignments. Click below to browse.</p>
    <nav>
        <ul>
            {list_html}
        </ul>
    </nav>
    <p>Served from <code>{html_escape(root_path)}</code></p>
</body>
</html>"""
    return html_page


def run_server(bind: str = "127.0.0.1", port: int = 8000) -> None:
    # Use http.server's SimpleHTTPRequestHandler for static file serving
    from http.server import SimpleHTTPRequestHandler

    os.chdir(ROOT)

    class Handler(SimpleHTTPRequestHandler):
        # Render a friendly homepage on '/'
        def do_GET(self):
            # Normalize path (strip query)
            path = urllib.parse.urlsplit(self.path).path
            # If requesting root, send our generated index page
            if path == "/" or path == "":
                html_page = build_index_html(ROOT)
                encoded = html_page.encode("utf-8")
                self.send_response(HTTPStatus.OK)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)
                return

            # Otherwise, fall back to default behaviour (serves files/dir listings)
            return super().do_GET()

    with socketserver.TCPServer((bind, port), Handler) as httpd:
        sa = httpd.socket.getsockname()
        host = sa[0]
        bound_port = sa[1]
        print(f"Serving repository at http://{host}:{bound_port}/")
        print("Press Ctrl-C to stop")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Serve repository as a lightweight website"
    )
    parser.add_argument("--port", "-p", type=int, default=8000, help="Port to bind")
    parser.add_argument(
        "--bind", default="127.0.0.1", help="Address to bind to (default 127.0.0.1)"
    )
    args = parser.parse_args()

    # Note: README rendering was removed from the homepage per user's request.

    try:
        run_server(bind=args.bind, port=args.port)
    except OSError as e:
        print(f"Failed to start server: {e}")
        sys.exit(1)
