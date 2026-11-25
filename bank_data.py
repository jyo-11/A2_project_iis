"""Made-up bank data for the prototype: what customers need, the words they use, and their payments.

    python bank_data.py      check which need each test phrase matches
"""

# Each need: the bank's name for it, how fast it is, whether the bot can do it,
# which help page answers it, the everyday words customers use for it,
# and related needs to offer as extra options (so the customer always has a real choice).
NEEDS = {
    "statement": {
        "label": "Statement",
        "speed": "ready to download now",
        "bot_can_do": True,
        "help_section": "Statements",
        "words": ["statement", "account history", "transactions", "bank summary", "printout", "list of payments", "list of transfers", "last 3 months", "last 6 months", "last year"],
        "related": ["payment_confirmation", "balance_letter"],
    },
    "payment_confirmation": {
        "label": "Payment confirmation",
        "speed": "in the app now",
        "bot_can_do": True,
        "help_section": "Payment confirmations",
        "words": ["proof", "receipt", "went through", "confirmation", "transfer", "paid", "sent money", "payment", "transfer"],
        "related": ["statement", "unknown_payment"],
    },
    "card": {
        "label": "Card help",
        "speed": "freeze now, new card in about 5 days",
        "bot_can_do": True,
        "help_section": "Cards",
        "words": ["card", "lost", "stolen", "pin", "stuck", "broken", "not working", "chip", "contactless","freeze", "cancel", "block", "unblock"],
        "related": ["unknown_payment"],
    },
    "balance_letter": {
        "label": "Balance confirmation letter",
        "speed": "same working day, made by a person",
        "bot_can_do": False,
        "help_section": "Bank letters",
        "words": ["balance", "letter", "visa", "proof of funds", "how much money","hoe much left", "how much is in my account", "visa application", "visa letter", "visa proof"],
        "related": ["address_letter", "statement"],
    },
    "address_letter": {
        "label": "Proof of address letter",
        "speed": "about 2 working days, made by a person",
        "bot_can_do": False,
        "help_section": "Bank letters",
        "words": ["address", "letter", "landlord", "gp"],
        "related": ["balance_letter", "statement"],
    },
    "unknown_payment": {
        "label": "Report a payment I don't recognise",
        "speed": "a person helps now",
        "bot_can_do": False,
        "help_section": "Cards",
        "words": ["didn't spend", "don't recognise", "weird charge", "not me", "someone used","dont know this payment", "not my payment", "not my transfer", "not my card", "not my account","I dont know"],
        "related": ["card", "payment_confirmation"],
    },
}

# Made-up accounts and months, so the bot can ask which statement the customer needs.
ACCOUNTS = ["Current account", "Savings account"]
PAST_MONTH = "October 2026"
THIS_MONTH = "November 2026 (so far)"

# What can be wrong with a card, and where each answer comes from.
CARD_PROBLEMS = {
    "Lost or stolen": "help_page",              # the Cards help page covers this
    "Not working or stuck": "no_page",          # no help page, so the bot won't guess
    "Someone used it without me": "unknown_payment",
}

# Made-up payments, so the bot can look a payment up instead of guessing it.
PAYMENTS = [
    {"to": "Priya", "amount": "£40", "date": "14 Nov"},
    {"to": "Supermarket", "amount": "£12.50", "date": "15 Nov"},
    {"to": "Landlord", "amount": "£650", "date": "1 Nov"},
]


def option_text(key):
    """What the customer sees on an option button, e.g. 'Statement (ready to download now)'."""
    need = NEEDS[key]
    if need.get("speed"):                    # an option without a speed just shows its label
        return need["label"] + " (" + need["speed"] + ")"
    return need["label"]


def payment_text(p):
    return p["amount"] + " to " + p["to"] + ", " + p["date"]


def understand(message):
    """Return the needs whose everyday words appear in the message (can be none, one or several)."""
    m = message.lower()
    GENERIC = {"letter"}                     # a vague word: only used if nothing more specific matches
    specific = [key for key, need in NEEDS.items() if any(w.lower() in m for w in need["words"] if w not in GENERIC)]
    if specific:
        return specific
    return [key for key, need in NEEDS.items() if any(w in m for w in need["words"] if w in GENERIC)]


def suggestions(found, most=3):
    """The needs that matched first, then their related needs, so there are always 2 to 3 real options."""
    out = list(found)
    for key in found:
        for r in NEEDS[key].get("related", []):
            if r not in out:
                out.append(r)
    return out[:max(most, len(found))]


if __name__ == "__main__":
    TESTS = [
        ("show my transfer went through", "payment_confirmation"),
        ("receipt for money I sent", "payment_confirmation"),
        ("account history for last month", "statement"),
        ("list of my transactions", "statement"),
        ("I lost my card", "card"),
        ("letter showing my balance for my visa", "balance_letter"),
        ("bank letter for my landlord", "address_letter"),
        ("there's a weird charge on my account", "unknown_payment"),
        ("I need proof I have money for my visa", "balance_letter"),
        ("there's a payment on my account I never made", "unknown_payment"),
        ("need my last 3 months of spending", "statement"),
        ("my card got stuck in the cash machine", "card"),
    ]
    right = 0
    for phrase, expected in TESTS:
        found = understand(phrase)
        ok = expected in found
        right += ok
        print(("OK   " if ok else "MISS ") + phrase + "  ->  " + (", ".join(found) or "nothing"))
    print("%d of %d phrases reached the right need" % (right, len(TESTS)))