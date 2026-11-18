"""Made-up bank data for the prototype: what customers need, the words they use, and their payments.

    python bank_data.py      check which need each test phrase matches
"""

# Each need: the bank's name for it, how fast it is, whether the bot can do it,
# which help page answers it, and the everyday words customers use for it.
NEEDS = {
    "statement": {
        "label": "Statement",
        "speed": "next working day",
        "bot_can_do": True,
        "help_section": "Statements",
        "words": ["statement", "account history", "transactions", "bank summary", "printout"],
    },
    "payment_confirmation": {
        "label": "Payment confirmation",
        "speed": "in the app now",
        "bot_can_do": True,
        "help_section": "Payment confirmations",
        "words": ["proof", "receipt", "went through", "confirmation", "transfer", "paid", "sent money"],
    },
    "card": {
        "label": "Card help",
        "speed": "freeze now, new card in about 5 days",
        "bot_can_do": True,
        "help_section": "Cards",
        "words": ["card", "lost", "stolen", "pin"],
    },
    "balance_letter": {
        "label": "Balance confirmation letter",
        "speed": "about 2 working days, made by a person",
        "bot_can_do": False,
        "help_section": "Bank letters",
        "words": ["balance", "visa", "proof of funds", "how much money"],
    },
    "address_letter": {
        "label": "Proof of address letter",
        "speed": "about 2 working days, made by a person",
        "bot_can_do": False,
        "help_section": "Bank letters",
        "words": ["address", "landlord", "gp"],
    },
    "unknown_payment": {
        "label": "Report a payment I don't recognise",
        "speed": "a person helps now",
        "bot_can_do": False,
        "help_section": "Cards",
        "words": ["didn't spend", "don't recognise", "weird charge", "not me", "someone used"],
    },
}

# Made-up payments, so the bot can look a payment up instead of guessing it.
PAYMENTS = [
    {"to": "Priya", "amount": "£40", "date": "14 Nov"},
    {"to": "Corner Shop", "amount": "£12.50", "date": "15 Nov"},
    {"to": "Landlord", "amount": "£650", "date": "1 Nov"},
]


def option_text(key):
    """What the customer sees on an option button, e.g. 'Statement · next working day'."""
    need = NEEDS[key]
    return need["label"] + " · " + need["speed"]


def payment_text(p):
    return p["amount"] + " to " + p["to"] + ", " + p["date"]


def understand(message):
    """Return the needs whose everyday words appear in the message (can be none, one or several)."""
    m = message.lower()
    return [key for key, need in NEEDS.items() if any(w in m for w in need["words"])]


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