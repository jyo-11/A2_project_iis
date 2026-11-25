# Test record

How I tested: I ran the conversations by hand in the browser (`python app.py`, then http://localhost:8001), clicking **Start again** before each test so it starts clean. Screenshots of the runs used in the report are in `docs/` (A1 to A4, B1 to B5). After my last changes on 25 Nov 2026, every conversation below was replayed through the final code with a short script (written with Claude) to check the results still hold.

The payment list, accounts, AI note, wait time and agent are simulated (made-up data and recorded replies).

## Path A: fixed in the chat

| # | What I typed or clicked | What the bot did | Result | Screenshot |
|---|---|---|---|---|
| A1 | "I sent money to my friend and she wants proof" → Payment confirmation → £40 to Priya, 14 Nov | "I think you're asking about **Payment confirmation**" + Statement and Report a payment as other options → "Which payment?" (made-up list) → steps from the help page, with **Source: Northgate Bank Help: Payment confirmations** → "Did this answer your question?" | ✅ | A1, A2 |
| A2 | "Yes, thanks" → "No, that's all" | "Great! Is there anything else I can help with?" → "Thanks for chatting with Northgate Bank. Have a lovely day! 👋" | ✅ | A3 |
| A3 | Same as A1, but **None of these** → No thanks → No, that's all | Explains the payment may still be on its way (usually minutes, some up to 24 hours), a confirmation is only possible once it shows, and offers a person → polite ending | ✅ | A4 |
| A4 | "give me statement" → Statement → Current account → November 2026 (so far) | Asks which account, then which month → "ready to download now" + steps + source (statements stay in the app; an email says when each is ready) | ✅ | |
| A5 | Same as A4, then "No, I need more help" | "Sorry that didn't help. A person can. Shall I connect you?" | ✅ | |
| A6 | "I lost my card" → Card help → Lost or stolen | "What's happened to your card?" → freeze steps + source | ✅ | |
| A7 | "my card got stuck in the cash machine" → Card help → Not working or stuck | "I don't have a help page for a card that isn't working, so I won't guess. A person can help." → note "Help with a card that is not working" | ✅ | |

## Path B: handed over to a person

| # | What I typed or clicked | What the bot did | Result | Screenshot |
|---|---|---|---|---|
| B1 | "I need a bank letter for my visa by Friday" → Balance confirmation letter → Yes, connect me | "I'm a bot and I can't help with this. A person can." → AI note: **Up-to-date statement** (wrong need, on purpose), For: Visa application, Needed by: Friday | ✅ | B2, B3 |
| B2 | Change → need = Balance confirmation letter → Yes, send it | Wait about 6 minutes + help while waiting; agent screen shows the **corrected** note first, earlier chat folded; agent: "…I'll make sure it's done by Friday." | ✅ | B4, B5 |
| B3 | Same as B1, but **Yes, send it** without changing the note | Agent gets "Up-to-date statement", the wrong need | ✅ works as built, shows a limit (below) | |
| B4 | "bank letter for my landlord" → Proof of address letter → Yes, connect me | Note says "Statement" for "Landlord", needed by empty; I corrected it before sending | ✅ | |

## Unclear requests

| # | What I typed or clicked | What the bot did | Result |
|---|---|---|---|
| C1 | "I need a bank letter right now" | "I found a few things that could match": Balance confirmation letter, Proof of address letter, Statement | ✅ after the fix (before: "Sorry, I'm not sure", see screenshot B1) |
| C2 | "someone used my card" | Offers both Card help and Report a payment I don't recognise, instead of guessing | ✅ |
| C3 | "blah" | "Sorry, I'm not sure what you need" + all 6 options + Talk to a person | ✅ |
| C4 | "letter for my visa" → letter → No thanks | "OK. Is there anything else I can help with?" Nothing goes to the agent | ✅ |
| C5 | "I lost my card" → Something else | "Tell me in a few words, or talk to a person." | ✅ |
| C6 | "hi", then "thanks" | Greeting listing what the bot can do + quick options → "You're welcome! Is there anything else I can help with?" | ✅ |

## Phrase test (`python bank_data.py`)

12 everyday phrases, checked against the need they should reach: **11 of 12** (was 10 of 12 before I added more everyday words).

Miss: "there's a payment on my account I never made" reaches Payment confirmation instead of Report a payment I don't recognise.

## What testing changed

| Found in testing | What I changed |
|---|---|
| One suggested option gave no real choice | Best match + 2 related options + Something else |
| The bot didn't say what it understood | "I think you're asking about…" before the options |
| Options didn't say how long things take; in my real chat I only found out after choosing | Each option shows its timing, e.g. "(in the app now)" |
| Customers use words the bot didn't know | Added everyday words, e.g. "last 3 months", "not working", "freeze", "visa letter", "not my payment" |
| "Statement" left me asking "statement of what?" | Bot asks which account and month |
| Statement and balance letter timings were unrealistic | Statements ready to download now (email when ready); balance letter same working day |
| Answers ended with no check | "Did this answer your question?", with a person offered if not, and a polite ending |
| "Hi" showed the "not sure" menu | Friendly greeting |
| A missing payment had no way forward | "None of these" explains the delay and offers a person |
| "I need a bank letter" was not understood | "Letter" offers both letter types when nothing more specific matches |

## Limits

- Only I tested it; no other users.
- If the customer sends the note without reading it (B3), the agent still gets the wrong need. The handover is only as accurate as the customer's check.
- The phrase test is small (12 phrases) and one still misses.
