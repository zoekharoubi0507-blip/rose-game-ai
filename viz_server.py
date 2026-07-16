"""
Local browser viewer for driver edge cases.

Run with `python viz_server.py` and open http://localhost:8090.
Every case registered in cases/ (see cases/tests_runner.py) shows up here
automatically - adding a new cases/*.py file is enough, nothing else
needs to change.
"""

import argparse
import http.server
import json
import socketserver
from pathlib import Path

import cases
from rose.common import obstacles

STATIC_DIR = Path(__file__).parent / "viz_static"


def case_summary(index, case):
    return {"index": index, "name": case.name, "description": case.description}


def trim_track(track, car):
    """
    Drop leading rows that carry no obstacle and aren't the car's own row,
    so the viewer only shows the rows that matter for a given case instead
    of the full padded track the driver actually runs against.
    """
    first_obstacle_row = next(
        (i for i, row in enumerate(track) if any(cell != obstacles.NONE for cell in row)),
        car["y"],
    )
    start = min(first_obstacle_row, car["y"])
    if len(track) - start == 2 and start > 0:
        start -= 1
    return track[start:], {"x": car["x"], "y": car["y"] - start}


def case_detail(index, case):
    actual, error = cases.run(case)
    display_track, display_car = trim_track(case.track, case.car)
    return {
        "index": index,
        "name": case.name,
        "description": case.description,
        "track": display_track,
        "car": display_car,
        "expected": case.expected,
        "actual": actual,
        "error": error,
        "passed": error is None and actual == case.expected,
    }


class Handler(http.server.BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path, content_type):
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._send_file(STATIC_DIR / "index.html", "text/html")
            return

        if self.path == "/api/cases":
            self._send_json([case_summary(i, c) for i, c in enumerate(cases.CASES)])
            return

        if self.path.startswith("/api/case/"):
            try:
                index = int(self.path.rsplit("/", 1)[-1])
                case = cases.CASES[index]
            except (ValueError, IndexError):
                self._send_json({"error": "case not found"}, status=404)
                return
            self._send_json(case_detail(index, case))
            return

        self.send_response(404)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description="Serve the edge-case viewer.")
    parser.add_argument("-p", "--port", type=int, default=4398)
    args = parser.parse_args()

    with socketserver.TCPServer(("", args.port), Handler) as httpd:
        print(f"Serving edge-case viewer at http://localhost:{args.port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
