"""Northgate Bank helper: a prototype bank chatbot (built on the supplied Lab 4 prototype).

    python app.py            then open http://localhost:8001

Path A: the bot understands everyday words, offers options and answers from a help page.
Path B: if the bot cannot do it, it drafts a note, the customer checks it, then a (simulated) person takes over.
"""
import json, os, re, sys
from http.server import BaseHTTPRequestHandler, HTTPServer

import model, retrieve
from bank_data import (NEEDS, PAYMENTS, ACCOUNTS, PAST_MONTH, THIS_MONTH, CARD_PROBLEMS,
                       option_text, payment_text, understand, suggestions)

HERE = os.path.dirname(os.path.abspath(__file__))

# Small talk: messages made only of these words get a friendly reply instead of the menu.
GREETING_WORDS = {"hi", "hello", "hey", "hiya", "heya", "good", "morning", "afternoon", "evening", "there", "bot", "helper"}
THANKS_WORDS = {"thanks", "thank", "you", "so", "much", "cheers", "ok", "okay", "great"}
NONE_OF_THESE = "None of these"
NONE_WORDS = {"none", "none of these", "none of them", "not there", "not listed", "it's not there", "its not there"}

# One conversation at a time is enough for a prototype.
STATE = {"history": [], "need": None, "account": None}

NOTE_SCHEMA = {"need": str, "for": str, "needed_by": str}
NOTE_INSTRUCTIONS = ("Write the note for the agent. Use only what the customer said in this chat. "
                     "Reply in JSON with the keys need, for, needed_by. Leave a key empty if the customer did not say it.")


def reply(text, options=None, **extra):
    """Every answer has the same shape, and is also added to the chat history."""
    STATE["history"].append("Bot: " + text)
    out = {"reply": text, "options": options or []}
    out.update(extra)
    return out


def help_page(section):
    """Find the help page for a section. Returns (page info, page text with its line breaks kept), or (None, "")."""
    pages = [p for p in retrieve.load() if p["section"].lower() == section.lower()]
    if not pages:
        return None, ""
    with open(os.path.join(retrieve.CORPUS, pages[0]["file"]), encoding="utf-8") as f:
        _meta, body = retrieve._front_matter(f.read())   # keeps steps, bullet points and **bold** as written
    return pages[0], body


def help_answer(section):
    """Answer only from an approved help page. If there is none, say so instead of guessing."""
    page, body = help_page(section)
    if not page:
        return reply("I can't find a help page for this, so I won't guess. A person can help.", ["Talk to a person"])
    return reply(body, ["Start again"], source=page["source"] + ": " + page["section"])


def choose_need(key):
    """The customer picked an option. Path A if the bot can do it, Path B if not."""
    STATE["need"] = key
    need = NEEDS[key]
    if key == "payment_confirmation":
        return reply("Which payment?", [payment_text(p) for p in PAYMENTS] + [NONE_OF_THESE], simulated="payment list is made up")
    if key == "statement":                              # ask which statement before answering
        return reply("Sure. Which account is the statement for?", ACCOUNTS, simulated="accounts are made up")
    if key == "card":
        return reply("Sorry to hear that. What's happened to your card?", list(CARD_PROBLEMS))
    if need["bot_can_do"]:
        return help_answer(need["help_section"])
    return reply("I'm a bot and I can't help with this (" + need["label"] + "). A person can. Shall I connect you?",
                 ["Yes, connect me", "No thanks"])


def draft_note():
    """The AI drafts the note. The check below guarantees its shape, not that it is true, so the customer checks it."""
    chat = "\n".join(STATE["history"])
    messages = [{"role": "system", "content": NOTE_INSTRUCTIONS},
                {"role": "user", "content": "Write the note for the agent from this chat:\n" + chat}]
    data = model.call_json(messages, NOTE_SCHEMA)
    ok = isinstance(data, dict) and all(isinstance(data.get(k), str) for k in NOTE_SCHEMA)
    if not ok:
        return {"need": "", "for": "", "needed_by": "", "problem": "I couldn't draft the note. Please fill it in."}
    if not any(data[k] for k in NOTE_SCHEMA):
        return {"need": "", "for": "", "needed_by": "", "problem": "I'm not sure what you need. Please fill it in."}
    return {k: data[k] for k in NOTE_SCHEMA}


def hand_over(note):
    """Runs only after the customer confirmed the note."""
    STATE["history"].append("Customer confirmed the note: " + json.dumps(note))
    section = NEEDS[STATE["need"]]["help_section"] if STATE["need"] else ""
    _page, waiting = help_page(section)                   # help while waiting, from the same help page
    agent_reply = "Hello, I've read your note (" + (note.get("need") or "your request") + "). I'll take it from here"
    if note.get("needed_by"):
        agent_reply += " and make sure it's done by " + note["needed_by"]
    agent_reply += "."
    return reply("Thanks. A person will join in about 6 minutes.", ["Start again"],
                 wait="about 6 minutes (simulated)", while_waiting=waiting,
                 agent={"note": note, "earlier_chat": STATE["history"][:-1], "reply": agent_reply})


def turn(request):
    """Decide what happens next. Simple rules decide the route, not the AI."""
    if request.get("confirm_note"):
        return hand_over(request["confirm_note"])
    message = (request.get("message") or "").strip()
    if message == "Start again":
        STATE["history"].clear(); STATE["need"] = None; STATE["account"] = None
        return {"reply": "Hi, I'm the Northgate Bank helper. How may I help you?", "options": [], "reset": True}
    STATE["history"].append("Customer: " + message)

    words = re.sub(r"[^a-z' ]", " ", message.lower()).split()
    if words and all(w in GREETING_WORDS for w in words):          # just "hi", "hello there", "good morning"...
        return reply("Hello! 👋 I'm the Northgate Bank helper. I can help with statements, payment confirmations, "
                     "card problems and bank letters. What do you need today?",
                     [option_text(k) for k in ("statement", "payment_confirmation", "card", "balance_letter")]
                     + ["Something else"])
    if words and all(w in THANKS_WORDS for w in words):            # "thanks", "thank you so much"...
        return reply("You're welcome! Is there anything else I can help with?", ["Start again"])
    if STATE["need"] == "payment_confirmation" and (message == NONE_OF_THESE or " ".join(words) in NONE_WORDS):
        return reply("If you can't see the payment yet, it may still be on its way. Payments to other banks usually show "
                     "within minutes, but some can take **up to 24 hours**, and I can only share a confirmation once it shows.\n\n"
                     "Need proof **sooner**, for example because someone is waiting for it? A person can help.",
                     ["Yes, connect me", "No thanks"])

    for key in NEEDS:                                   # the customer clicked an option button
        if message == option_text(key):
            return choose_need(key)
    for p in PAYMENTS:                                  # the customer picked a payment
        if message == payment_text(p):
            page, body = help_page("Payment confirmations")
            return reply("Here's how to get proof of your payment of " + payment_text(p) + ".\n\n" + body,
                         ["Start again"], source=page["source"] + ": " + page["section"] if page else "")
    if message in ACCOUNTS:                             # statement: which account?
        STATE["account"] = message
        return reply("Which month do you need?", [PAST_MONTH, THIS_MONTH])
    if message == PAST_MONTH:                           # a finished month is ready now
        page, body = help_page("Statements")
        return reply("Your " + (STATE["account"] or "account").lower() + " statement for " + PAST_MONTH +
                     " is **ready to download now**.\n\n" + body, ["Start again"],
                     source=page["source"] + ": " + page["section"] if page else "")
    if message == THIS_MONTH:                           # this month: next working day, so offer the faster option
        return reply("An up-to-date statement for this month will be ready the **next working day**.\n\n"
                     "Need proof of one payment **today**? A payment confirmation is ready in the app as soon as the payment shows.",
                     [option_text("payment_confirmation"), "Start again"])
    if message in CARD_PROBLEMS:                        # card: what happened?
        route = CARD_PROBLEMS[message]
        if route == "help_page":
            return help_answer("Cards")
        if route == "unknown_payment":
            return choose_need("unknown_payment")
        return reply("I don't have a help page for a card that isn't working, so I won't guess. "
                     "A person can help. Shall I connect you?", ["Yes, connect me", "No thanks"])
    if message in ("Yes, connect me", "Talk to a person"):
        return reply("Before I connect you, please check this note. The person will see it first.",
                     note=draft_note(), simulated="the AI note uses a recorded reply")
    if message == "No thanks":
        return reply("OK. Is there anything else?", ["Start again"])
    if message == "Something else":
        return reply("Tell me in a few words, or talk to a person.", ["Talk to a person"])

    found = understand(message)                         # the customer typed in their own words
    if found:
        options = [option_text(k) for k in suggestions(found)] + ["Something else"]
        if len(found) == 1:                             # one clear match: say what the bot thinks, so the customer can confirm
            return reply("I think you're asking about **" + NEEDS[found[0]]["label"] + "**. Tap it to carry on, "
                         "or pick another option if that's not quite right.", options)
        return reply("I found a few things that could match. Which one do you need?", options)
    return reply("Sorry, I'm not sure what you need. Here's what I can help with. Which one is closest?",
                 [option_text(k) for k in NEEDS] + ["Talk to a person"])


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        self.send_response(code); self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        with open(os.path.join(HERE, "index.html"), "rb") as f:
            self._send(200, f.read(), "text/html; charset=utf-8")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        request = json.loads(self.rfile.read(n).decode("utf-8"))
        self._send(200, json.dumps(turn(request)).encode("utf-8"))

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    port = 8001
    if "--port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--port") + 1])
    HTTPServer.allow_reuse_address = False   # on Windows, stops a second copy silently sharing the port
    try:
        server = HTTPServer(("localhost", port), Handler)
    except OSError:
        sys.exit("Port %d is already in use: the chatbot is probably running in another terminal. "
                 "Stop that one first (Ctrl + C there), or use: python app.py --port %d" % (port, port + 1))
    print("serving on http://localhost:%d" % port)
    server.serve_forever()