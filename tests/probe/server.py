"""A local server that stands in for the model. It makes no model call. For the main request of a session it
answers with the next tool call of a fixed script; the session sends the result of each call back, and the
server writes each request body to a file. Usage: server.py PORT OUT_DIR SCRIPT_JSON"""
import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

OUT = Path(sys.argv[2])
SCRIPT = json.loads(Path(sys.argv[3]).read_text())
COUNT = [0]


def results(body: dict) -> int:
    count = 0
    for message in body.get("messages", []):
        content = message.get("content")
        if isinstance(content, list):
            count += sum(1 for block in content if isinstance(block, dict) and block.get("type") == "tool_result")
    return count


def events(body: dict) -> list:
    model = body.get("model", "stand-in")
    main = any(tool.get("name") == "Bash" for tool in body.get("tools", []) if isinstance(tool, dict))
    step = results(body)
    start = {"type": "message_start", "message": {"id": f"msg_{COUNT[0]}", "type": "message", "role": "assistant",
             "model": model, "content": [], "stop_reason": None, "stop_sequence": None,
             "usage": {"input_tokens": 10, "output_tokens": 1}}}
    if main and step < len(SCRIPT):
        call = SCRIPT[step]
        block = {"type": "tool_use", "id": f"toolu_{step:02d}", "name": call["name"], "input": {}}
        delta = {"type": "input_json_delta", "partial_json": json.dumps(call["input"])}
        reason = "tool_use"
    else:
        block = {"type": "text", "text": ""}
        delta = {"type": "text_delta", "text": "done"}
        reason = "end_turn"
    return [start,
            {"type": "content_block_start", "index": 0, "content_block": block},
            {"type": "content_block_delta", "index": 0, "delta": delta},
            {"type": "content_block_stop", "index": 0},
            {"type": "message_delta", "delta": {"stop_reason": reason, "stop_sequence": None},
             "usage": {"output_tokens": 5}},
            {"type": "message_stop"}]


def whole(body: dict) -> dict:
    return {"id": f"msg_{COUNT[0]}", "type": "message", "role": "assistant", "model": body.get("model", "stand-in"),
            "content": [{"type": "text", "text": "done"}], "stop_reason": "end_turn", "stop_sequence": None,
            "usage": {"input_tokens": 10, "output_tokens": 1}}


class Handler(BaseHTTPRequestHandler):
    def send(self, kind: str, payload: bytes):
        self.send_response(200)
        self.send_header("content-type", kind)
        self.send_header("content-length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        raw = self.rfile.read(int(self.headers.get("content-length") or 0))
        COUNT[0] += 1
        (OUT / f"request-{COUNT[0]:03d}.json").write_bytes(raw)
        (OUT / f"request-{COUNT[0]:03d}.path").write_text(self.path)
        try:
            body = json.loads(raw)
        except ValueError:
            body = {}
        if "/messages" not in self.path or "count_tokens" in self.path:
            self.send("application/json", b'{"input_tokens": 10}')
        elif body.get("stream"):
            text = "".join(f"event: {e['type']}\ndata: {json.dumps(e)}\n\n" for e in events(body))
            self.send("text/event-stream", text.encode())
        else:
            self.send("application/json", json.dumps(whole(body)).encode())

    def do_GET(self):
        self.send("application/json", b"{}")

    def log_message(self, *args):
        pass


HTTPServer(("127.0.0.1", int(sys.argv[1])), Handler).serve_forever()
