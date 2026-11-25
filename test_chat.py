"""Scripted tests: plays each test conversation through the chatbot and records what happened.

    python test_chat.py           print the results
    python test_chat.py --save    also write them to docs/test_script_results.md

My hand-test record (what I saw in the browser) is docs/test_record.md; this script replays those conversations.
Each test starts a fresh chat. The messages are the same ones a customer would type or click.
"""
import os, sys, datetime

import app
from bank_data import PAYMENTS, ACCOUNTS, THIS_MONTH, option_text, payment_text

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = []


def say(message):
    return app.turn({"message": message})


def confirm(note):
    return app.turn({"confirm_note": note})


def fresh():
    say("Start again")


def short(text, n=90):
    text = text.replace("**", "").replace("\n", " ").replace("|", "/")
    return text if len(text) <= n else text[:n].rstrip() + "…"


def record(name, did, happened, ok, result=None):
    RESULTS.append((name, did, happened, result or ("Pass" if ok else "Fail")))


# ---------- Path A: fixed in the chat ----------

def t1():
    fresh()
    r1 = say("I sent money to my friend and she wants proof")
    r2 = say(option_text("payment_confirmation"))
    r3 = say(payment_text(PAYMENTS[0]))
    ok = (r1["options"][0] == option_text("payment_confirmation") and r2["reply"] == "Which payment?"
          and "simulated" in r2 and "Payment confirmations" in r3.get("source", ""))
    record("A1 Path A: payment proof", '"I sent money to my friend and she wants proof" → Payment confirmation → ' + payment_text(PAYMENTS[0]),
           "Best match shown first; asked which payment (list tagged as made up); answered from help page with source: "
           + r3.get("source", "none"), ok)


def t2():
    fresh()
    say("give me statement")
    r2 = say(option_text("statement"))
    r3 = say(ACCOUNTS[0])
    r4 = say(THIS_MONTH)
    ok = "Which account" in r2["reply"] and "Which month" in r3["reply"] and "ready to download now" in r4["reply"] and r4.get("source")
    record("A4 Path A: statement", '"give me statement" → Statement → ' + ACCOUNTS[0] + " → " + THIS_MONTH,
           "Asked which account, then which month, then: " + short(r4["reply"], 70) + " (source shown)", ok)


def t3():
    fresh()
    say("I lost my card")
    r2 = say(option_text("card"))
    r3 = say("Lost or stolen")
    fresh()
    say("my card got stuck in the cash machine")
    say(option_text("card"))
    r4 = say("Not working or stuck")
    r5 = say("Yes, connect me")
    ok = ("What's happened" in r2["reply"] and "Cards" in r3.get("source", "")
          and "won't guess" in r4["reply"] and r5.get("note", {}).get("need"))
    record("A6, A7 Path A: card problems", '"I lost my card" → Card help → Lost or stolen; then "my card got stuck in the cash machine" → Card help → Not working or stuck',
           "Lost: answer from the Cards help page. Not working: \"" + short(r4["reply"], 60) + "\" → note: "
           + r5["note"]["need"], ok)


def ending():
    fresh()
    say("show my transfer went through")
    say(option_text("payment_confirmation"))
    say(payment_text(PAYMENTS[0]))
    r1 = say("Yes, thanks")
    r2 = say("No, that's all")
    ok = r1["reply"].startswith("Great!") and r2["reply"].startswith("Thanks for chatting")
    record("Polite ending", "After an answer: Yes, thanks → No, that's all",
           "\"" + short(r1["reply"], 50) + "\" → \"" + short(r2["reply"], 50) + "\"", ok)


def more_help():
    fresh()
    say("give me statement")
    say(option_text("statement"))
    say(ACCOUNTS[0])
    say(THIS_MONTH)
    r = say("No, I need more help")
    ok = "A person can" in r["reply"] and "Yes, connect me" in r["options"]
    record("Answer did not help", "Statement answer → No, I need more help", "\"" + short(r["reply"]) + "\"", ok)


# ---------- Path B: handed over ----------

def t4():
    fresh()
    say("I need a bank letter for my visa by Friday")
    r2 = say(option_text("balance_letter"))
    r3 = say("Yes, connect me")
    corrected = dict(r3["note"], need="Balance confirmation letter")
    r4 = confirm(corrected)
    ok = ("I'm a bot" in r2["reply"] and r3["note"]["need"] == "Up-to-date statement"
          and r4["agent"]["note"]["need"] == "Balance confirmation letter" and "Friday" in r4["agent"]["reply"] and r4.get("wait"))
    record("T4 Path B: visa letter", '"I need a bank letter for my visa by Friday" → Balance letter → Yes, connect me → Change need → Yes, send it',
           "Bot said it can't do letters and offered a person. AI note guessed \"" + r3["note"]["need"]
           + "\" (wrong); the customer corrected it. Agent saw the corrected note first: \"" + short(r4["agent"]["reply"], 80) + "\"; wait time shown", ok)


def t5():
    fresh()
    say("bank letter for my landlord")
    say(option_text("address_letter"))
    r3 = say("Yes, connect me")
    r4 = confirm(dict(r3["note"], need="Proof of address letter", needed_by="Monday"))
    ok = r3["note"]["need"] == "Statement" and r4["agent"]["note"]["need"] == "Proof of address letter" and "Monday" in r4["agent"]["reply"]
    record("T5 Path B: landlord letter", '"bank letter for my landlord" → Proof of address letter → Yes, connect me → Change → Yes, send it',
           "AI note guessed \"" + r3["note"]["need"] + "\" with no date; the customer corrected it and added Monday; agent: \""
           + short(r4["agent"]["reply"], 70) + "\"", ok)


def t11():
    fresh()
    say("I need a bank letter for my visa by Friday")
    say(option_text("balance_letter"))
    r3 = say("Yes, connect me")
    r4 = confirm(r3["note"])                     # sent without reading it
    wrong = r4["agent"]["note"]["need"] == "Up-to-date statement"
    record("T11 Limit: note sent unread", "Same as T4, but pressed Yes, send it without changing the note",
           "Agent received the wrong need: \"" + r4["agent"]["note"]["need"] + "\". Expected: this is the limit of the design", wrong,
           "Known limit" if wrong else "Fail")


# ---------- Unclear or tricky requests ----------

def t6():
    fresh()
    r1 = say("someone used my card")
    both = option_text("card") in r1["options"] and option_text("unknown_payment") in r1["options"]
    r2 = say(option_text("unknown_payment"))
    r3 = say("Yes, connect me")
    ok = both and "I'm a bot" in r2["reply"] and "note" in r3
    record("T6 Two meanings", '"someone used my card" → Report a payment I don\'t recognise → Yes, connect me',
           "Offered both Card help and Report a payment instead of guessing; note before handover: \""
           + (r3["note"].get("need") or r3["note"].get("problem", "")) + "\"", ok)


def t7():
    fresh()
    say("letter for my visa")
    say(option_text("balance_letter"))
    r3 = say("No thanks")
    ok = "anything else" in r3["reply"] and "agent" not in r3
    record("T7 Saying no to a person", '"letter for my visa" → Balance letter → No thanks',
           "\"" + short(r3["reply"]) + "\" Nothing sent to an agent", ok)


def t8():
    fresh()
    r1 = say("blah")
    r2 = say("Talk to a person")
    ok = r1["reply"].startswith("Sorry, I'm not sure") and "Talk to a person" in r1["options"] and "note" in r2
    record("T8 Words it doesn't know", '"blah" → Talk to a person',
           "Showed all options plus Talk to a person, did not guess; then a note to fill in: \""
           + r2["note"].get("problem", r2["note"].get("need", "")) + "\"", ok)


def t9():
    fresh()
    say("I lost my card")
    r2 = say("Something else")
    ok = "Tell me in a few words" in r2["reply"] and "Talk to a person" in r2["options"]
    record("T9 Something else", '"I lost my card" → Something else', "\"" + short(r2["reply"]) + "\" + Talk to a person", ok)


def t10():
    """The 12 everyday phrases live in bank_data.py, so run that check and read its result."""
    import subprocess
    out = subprocess.run([sys.executable, os.path.join(HERE, "bank_data.py")], capture_output=True,
                         text=True, encoding="utf-8").stdout.splitlines()
    missed = [line[5:].split("  ->  ")[0] for line in out if line.startswith("MISS")]
    record("T10 Everyday words", "Ran the 12 everyday phrases in bank_data.py",
           out[-1] + ". Missed: " + ("; ".join('"%s"' % m for m in missed) or "none"), len(missed) <= 1)


# ---------- Gaps found while testing (now fixed) ----------

def letter_now():
    fresh()
    r = say("I need a bank letter right now")
    ok = (r["reply"].startswith("I found a few things") and option_text("balance_letter") in r["options"]
          and option_text("address_letter") in r["options"])
    record("Vague word \"letter\" (fixed)", '"I need a bank letter right now"',
           "Offered both letter types (before the fix: \"Sorry, I'm not sure\")", ok)


def gap1():
    fresh()
    r1 = say("hi")
    r2 = say("good morning")
    r3 = say("thanks")
    ok = r1["reply"].startswith("Hello!") and r2["reply"].startswith("Hello!") and r3["reply"].startswith("You're welcome")
    record("Gap 1 (fixed): greetings", '"hi", "good morning", "thanks"',
           "Friendly hello with 4 quick options; \"thanks\" → \"" + short(r3["reply"], 50) + "\" (before the fix, \"hi\" showed the full menu)", ok)


def gap2():
    fresh()
    say("show my transfer went through")
    say(option_text("payment_confirmation"))
    r3 = say("None of these")
    r4 = say("Yes, connect me")
    ok = "up to 24 hours" in r3["reply"] and r4.get("note", {}).get("need")
    record("Gap 2 (fixed): payment not listed", "Payment confirmation → None of these → Yes, connect me",
           "Explained payments can take up to 24 hours and offered a person; note: \"" + r4["note"]["need"] + "\"", ok)


def broken_note():
    os.environ["IIS_MOCK_BREAK"] = "1"
    try:
        fresh()
        say(option_text("balance_letter"))
        r = say("Yes, connect me")
    finally:
        del os.environ["IIS_MOCK_BREAK"]
    ok = r["note"].get("problem") == "I couldn't draft the note. Please fill it in."
    record("Broken AI note", "Forced a malformed AI reply (IIS_MOCK_BREAK=1) → Yes, connect me",
           "Format check caught it: \"" + r["note"].get("problem", "") + "\" The customer fills the note in", ok)


TESTS = [t1, t2, t3, ending, more_help, t4, t5, t6, t7, t8, t9, t10, t11, letter_now, gap1, gap2, broken_note]


def as_markdown():
    passed = sum(1 for r in RESULTS if r[3] == "Pass")
    limits = sum(1 for r in RESULTS if r[3] == "Known limit")
    lines = ["# Scripted test results", "",
             "Run with `python test_chat.py --save` on " + datetime.date.today().strftime("%d %b %Y") + ". "
             "Each test starts a fresh chat and sends the same messages a customer would type or click. "
             "**%d of %d passed**; %d shows a known limit of the design." % (passed, len(RESULTS) - limits, limits), "",
             "| Test | Steps | What happened | Result |", "|---|---|---|---|"]
    lines += ["| %s | %s | %s | %s |" % r for r in RESULTS]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    for test in TESTS:
        try:
            test()
        except Exception as e:                  # a crash is a failed test, not the end of the run
            record(test.__name__, "-", "Crashed: %r" % e, False)
    text = as_markdown()
    sys.stdout.buffer.write(text.encode("utf-8"))
    if "--save" in sys.argv:
        with open(os.path.join(HERE, "docs", "test_script_results.md"), "w", encoding="utf-8") as f:
            f.write(text)
        print("\nsaved docs/test_script_results.md")
