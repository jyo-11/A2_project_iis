"""Recorded replies, so the prototype runs with no key and no network (based on the Lab 4 mock).

    python mock_model.py --selftest     check the recorded files load
    IIS_MOCK_BREAK=1                    force the malformed reply, to test the note's format check
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "recorded_runs")
FILES = ["note_visa.json", "note_address.json", "note_missing.json", "note_unknown.json",
         "note_card.json", "note_other.json", "malformed.txt"]


def _load(name):
    with open(os.path.join(RUNS, name), encoding="utf-8") as f:
        return f.read()


def _pick(text):
    """Choose the recorded note that fits the chat."""
    t = (text or "").lower()
    if os.environ.get("IIS_MOCK_BREAK"):
        return "malformed.txt"
    if "visa" in t or "balance" in t:
        return "note_visa.json"
    if "address" in t or "landlord" in t:
        return "note_address.json"
    if "can't see the payment" in t:
        return "note_missing.json"
    if "recognise" in t:
        return "note_unknown.json"
    if "not working" in t:
        return "note_card.json"
    return "note_other.json"


def call(messages, schema=None):
    last = messages[-1]["content"] if messages else ""
    return _load(_pick(last))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        for f in FILES:
            _load(f)
        print("ok: %d recorded notes" % (len(FILES) - 1))
