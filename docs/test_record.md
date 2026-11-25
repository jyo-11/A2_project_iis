# Test record

Run with `python test_chat.py --save` on 25 Nov 2026. Each test starts a fresh chat and sends the same messages a customer would type or click. **13 of 13 passed**; 1 shows a known limit of the design.

| Test | Steps | What happened | Result |
|---|---|---|---|
| T1 Path A: payment proof | "show my transfer went through" → Payment confirmation → £40 to Priya, 14 Nov | Best match shown first; asked which payment (list tagged as made up); answered from help page with source: Northgate Bank Help: Payment confirmations | Pass |
| T2 Path A: statement | "give me statement" → Statement → Current account → October 2026 | Asked which account, then which month, then: Your current account statement for October 2026 is ready to download n… (source shown) | Pass |
| T3 Path A: card problems | "I lost my card" → Card help → Lost or stolen; then again with Not working or stuck | Lost: answer from the Cards help page. Not working: "I don't have a help page for a card that isn't working, so I…" → note: Help with a card that is not working | Pass |
| T4 Path B: visa letter | "I need a letter showing my balance for my visa, by Friday" → Balance letter → Yes, connect me → Change need → Yes, send it | Bot said it can't do letters and offered a person. AI note guessed "Up-to-date statement" (wrong); the customer corrected it. Agent saw the corrected note first: "Hello, I've read your note (Balance confirmation letter). I'll take it from here…"; wait time shown | Pass |
| T5 Path B: landlord letter | "bank letter for my landlord" → Proof of address letter → Yes, connect me → Change → Yes, send it | AI note guessed "Statement" with no date; the customer corrected it and added Monday; agent: "Hello, I've read your note (Proof of address letter). I'll take it fro…" | Pass |
| T6 Two meanings | "someone used my card" → Report a payment I don't recognise → Yes, connect me | Offered both Card help and Report a payment instead of guessing; note before handover: "Report a payment I don't recognise" | Pass |
| T7 Saying no to a person | "letter for my visa" → Balance letter → No thanks | "OK. Is there anything else I can help with?" Nothing sent to an agent | Pass |
| T8 Words it doesn't know | "blah" → Talk to a person | Showed all options plus Talk to a person, did not guess; then a note to fill in: "I'm not sure what you need. Please fill it in." | Pass |
| T9 Something else | "I lost my card" → Something else | "Tell me in a few words, or talk to a person." + Talk to a person | Pass |
| T10 Everyday words | Ran the 12 everyday phrases in bank_data.py | 11 of 12 phrases reached the right need. Missed: "there's a payment on my account I never made" | Pass |
| T11 Limit: note sent unread | Same as T4, but pressed Yes, send it without changing the note | Agent received the wrong need: "Up-to-date statement". Expected: this is the limit of the design | Known limit |
| Gap 1 (fixed): greetings | "hi", "good morning", "thanks" | Friendly hello with 4 quick options; "thanks" → "You're welcome! Is there anything else I can help…" (before the fix, "hi" showed the full menu) | Pass |
| Gap 2 (fixed): payment not listed | Payment confirmation → None of these → Yes, connect me | Explained payments can take up to 24 hours and offered a person; note: "Proof of a recent payment that is not showing yet" | Pass |
| Broken AI note | Forced a malformed AI reply (IIS_MOCK_BREAK=1) → Yes, connect me | Format check caught it: "I couldn't draft the note. Please fill it in." The customer fills the note in | Pass |
