"""The supplied Lab 4 prototype.

    python app.py            serve on 8000
    python app.py --port 8001

The two turns below are local code: they work with no model at all. The model is only asked for the
ordinary case, and its reply is checked before anything is rendered.
"""
import json, os, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import model  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEMA = {"reply": str, "options": list, "action": (dict, type(None)), "unsupported_claims": list}
APPOINTMENTS = [{"id": "derm-14nov", "clinic": "Dermatology", "date": "14 Nov", "time": "10:20"},
                {"id": "physio-20nov", "clinic": "Physiotherapy", "date": "20 Nov", "time": "09:00"}]


def valid(data):
    return isinstance(data, dict) and all(k in data and isinstance(data[k], t) for k, t in SCHEMA.items())


def fallback_turn():
    """A malformed reply is a caught error, never a blank page."""
    return {"reply": "I could not read the reply, so I have not changed anything. Try again or ask the module lead.",
            "options": [], "action": None, "unsupported_claims": []}


def clarification_turn(candidates):
    names = " or ".join("%s on %s" % (a["clinic"], a["date"]) for a in candidates)
    return {"reply": "Which appointment: %s?" % names,
            "options": [a["id"] for a in candidates], "action": None, "unsupported_claims": []}


def decline_turn():
    return {"reply": "Dr Achebe has no clinic next week, and I cannot see your dialysis days, so I cannot "
                     "avoid them. Here are the open slots; you choose.",
            "options": ["Thu 09:40", "Fri 14:10"], "action": None, "unsupported_claims": ["clinic availability beyond next week"]}


def turn(message):
    m = (message or "").lower()
    if "achebe" in m or "next week" in m:
        return decline_turn()
    named = [a for a in APPOINTMENTS if a["clinic"].lower()[:5] in m]
    if "appointment" in m and len(named) != 1:
        return clarification_turn(APPOINTMENTS)
    data = model.call_json([{"role": "user", "content": message}], SCHEMA)
    return data if valid(data) else fallback_turn()


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        with open(os.path.join(HERE, "index.html"), "rb") as f:
            self._send(200, f.read(), "text/html; charset=utf-8")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        msg = json.loads(self.rfile.read(n).decode("utf-8")).get("message", "")
        self._send(200, json.dumps(turn(msg)).encode("utf-8"))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = 8000
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    print("serving on http://localhost:%d" % port)
    HTTPServer(("localhost", port), Handler).serve_forever()
