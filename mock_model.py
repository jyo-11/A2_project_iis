"""Recorded replies, so the lab runs with no key and no network.

    python mock_model.py --selftest     check the recorded files load
    IIS_MOCK_BREAK=1                    force the malformed reply (used in the demonstration)
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "recorded_runs")
FILES = ["good.json", "ambiguous.json", "unsupported.json", "malformed.txt"]


def _load(name):
    with open(os.path.join(RUNS, name), encoding="utf-8") as f:
        return f.read()


def _pick(text):
    t = (text or "").lower()
    if os.environ.get("IIS_MOCK_BREAK"):
        return "malformed.txt"
    if "note for the agent" in t:               # A2: recorded AI notes for the hand-over
        if "visa" in t or "balance" in t:
            return "note_visa.json"
        if "address" in t or "landlord" in t:
            return "note_address.json"
        if "recognise" in t:
            return "note_unknown.json"
        if "not working" in t:
            return "note_card.json"
        return "note_other.json"
    if "achebe" in t or "next week" in t:
        return "unsupported.json"
    if "appointment" in t and "dermatology" not in t and "physio" not in t:
        return "ambiguous.json"
    return "good.json"


def call(messages, schema=None):
    last = messages[-1]["content"] if messages else ""
    return _load(_pick(last))


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        for f in FILES:
            _load(f)
        print("ok: %d recorded replies" % (len(FILES) - 1))