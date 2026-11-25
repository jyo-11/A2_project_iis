# Northgate Bank helper

A prototype banking chatbot for a made-up bank. It fixes what it can in the chat and hands over what it can't, with a note the customer checks first.

IIS Assignment 2. **README prose word count: ✍️ [fill in at the end]**
Submitted commit: ✍️ [paste the commit ID after your last push]

---

## Project status

| Part | Status |
|---|---|
| Chat page, rule-based dialogue controller, everyday-words matcher | Implemented |
| Answers from approved help pages, with the source shown | Implemented |
| Follow-up questions (which account and month, which payment, what happened to the card) | Implemented |
| Customer checks and edits the note before handover | Implemented |
| AI note drafter ("I think you need", "For", "Needed by") | Simulated: recorded replies, no live model |
| Accounts, payments, handover queue, wait time, bank agent | Simulated: made-up data |
| Real bank data and login, urgent-case priority, notifications | Planned, not built |

## Technology stack

- **Python 3 (standard library only)**: web server and dialogue controller (`app.py`). No packages to install.
- **HTML, CSS, JavaScript**: the chat page (`index.html`).
- **Markdown help pages** (`corpus/`): the only source the bot answers from. Searched by `retrieve.py` (reused from Lab 4).
- **Model wrapper** (`model.py`, `mock_model.py`, reused from Lab 4): returns recorded replies from `recorded_runs/note_*.json`. A live model can be used through environment variables, but none was used.
- **draw.io**: system diagram (`docs/system-diagram.drawio`).
- ✍️ [Any choice still undecided? For example, which live model you would use for the note drafter.]

## How to run it

```
python app.py
```

Then open <http://localhost:8001>. No key, no network and no install are needed.

Check the everyday-words matcher:

```
python bank_data.py        # expect: 11 of 12 phrases reached the right need
```

**API keys:** none are stored in this repository. To try a live model instead of the recorded replies, set your own key in the terminal (not in a file): `IIS_MODEL=http`, `IIS_MODEL_URL=<endpoint>`, `IIS_API_KEY=<your key>`.

## What is original and what is reused

- **Reused from the module's Lab 4 pack:** `retrieve.py`, `model.py`, `tools.py`, `vlm.py` (unchanged), `mock_model.py` (I added the note replies) and the web-server pattern in `app.py`. The original Lab 4 README is kept in `reference/LAB4_README.md`.
- **My own work:** the bank help pages (`corpus/`), the needs, everyday words and made-up payments (`bank_data.py`), the two-path dialogue in `app.py`, the chat page (`index.html`), the recorded AI notes, the tests and the design.

## Development record

Grouped by stage. Each line says what changed, ✍️ **why**, and what you checked.

**1. Starting point**
- Started from the supplied Lab 4 prototype, unchanged, so my own changes are easy to see ([611928f](https://github.com/jyo-11/A2_project_iis/commit/611928f)).
- Replaced the course documents with bank help pages: statements, payment confirmation, bank letters, cards ([ddb72c5](https://github.com/jyo-11/A2_project_iis/commit/ddb72c5), [c9a96cc](https://github.com/jyo-11/A2_project_iis/commit/c9a96cc)). ✍️ Why: ...

**2. Understanding everyday words**
- Added customer needs, everyday words and made-up payments ([bf2e1f6](https://github.com/jyo-11/A2_project_iis/commit/bf2e1f6)). ✍️ Why: ...
- Changed the everyday words after the first phrase test. Checked with `python bank_data.py`: 10 of 12 phrases went up to 11 of 12 ([4453307](https://github.com/jyo-11/A2_project_iis/commit/4453307)). ✍️ Why: ...
- Added more everyday words and showed how quickly each option is ready ([89e10c6](https://github.com/jyo-11/A2_project_iis/commit/89e10c6)). ✍️ Why: ...
- ✍️ [Not committed yet] "letter" alone was too vague, so it is only used when no more specific word matches. Why: ...

**3. Two paths**
- Path A answers from a help page; Path B drafts a note, the customer checks it, then a person takes over ([452b687](https://github.com/jyo-11/A2_project_iis/commit/452b687)). ✍️ Why: ...
- Recorded AI notes, including one that deliberately picks the wrong need, to test the customer check ([8a03399](https://github.com/jyo-11/A2_project_iis/commit/8a03399)). ✍️ Why: ...

**4. Changes from my own testing**
- Answers appeared as one long block, so help pages keep their steps and bold text ([d816bd1](https://github.com/jyo-11/A2_project_iis/commit/d816bd1)).
- "Hi" showed the menu, so I added a greeting and a thank-you reply ([a6ffc57](https://github.com/jyo-11/A2_project_iis/commit/a6ffc57)).
- A single "Did you mean…?" gave no real choice, so the bot says its best guess and shows related options ([a875221](https://github.com/jyo-11/A2_project_iis/commit/a875221)).
- Made the letter timings realistic ([dc20344](https://github.com/jyo-11/A2_project_iis/commit/dc20344)).
- Port changed to 8001 because port 8000 is used by another program on my laptop ([b556c00](https://github.com/jyo-11/A2_project_iis/commit/b556c00)).
- ✍️ [Add "statement → asks which account and month" and "None of these → explains the 24-hour delay", with their commits.]

**5. Testing**
- Full test results: [docs/test_record.md](docs/test_record.md). ✍️ [This file is empty: fill it in with only the tests you ran.]
- Limit found: if the customer sends the note without reading it, the agent still gets the wrong need.

## AI assistance

✍️ Write this in your own words. Name each tool, what you asked it for, and what you checked or changed. Two or three examples are enough.

- **Claude (Claude Code):** ✍️ [for example: step-by-step build guides; drew the system diagram from my design; built this README skeleton from my commits, which I then completed and checked.] What I checked or changed: ...
- **ChatGPT (image generation):** ✍️ [for example: the Figure 2 "before" drawings in the report.] What I checked or changed: ...

## Additional files

- `docs/A1.png` to `A4.png`, `B1.png` to `B5.png`: screenshots of Path A and Path B used in the report storyboards.
- `docs/storyboard/`: the storyboard images and the script that builds them (`python docs/storyboard/make_storyboards.py`, needs Chrome or Edge).
- `docs/system-diagram.drawio` / `.png`: the system diagram (open the `.drawio` file at app.diagrams.net).
- `reference/`: original Lab 4 files, kept for comparison.
- No ZIP file is needed.
