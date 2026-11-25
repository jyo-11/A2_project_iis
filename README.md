README prose word count: about 1,170 (code, commands and links not counted)

# Northgate Bank helper

A prototype banking chatbot for a made-up bank. It fixes what it can in the chat and hands over what it cannot, with a note the customer checks first.

**Repository:** https://github.com/jyo-11/A2_project_iis

**Module:** Intelligent Interactive Systems (IIS), Assignment 2, University of Birmingham.

## Problem

Bank customers, especially international students, describe documents in their own words. These may not match fixed chatbot menus.

When I asked a UK bank chatbot for proof of a payment, it did not understand and passed me to an agent. The agent assumed I wanted a statement and did not check what I actually needed.

## Project status

| Status | Details |
|---|---|
| Implemented | Chat page; rule-based dialogue controller (not AI); everyday-words matcher; answers only from approved help pages, with the source shown; follow-up questions about the account and month, the payment, or what happened to the card; "None of these" explains the up-to-24-hour delay and offers a person; customer checks and edits the agent note before handover. |
| Simulated | AI note drafter ("I think you need", "For", "Needed by") uses recorded replies, not a live model; accounts, payments, handover queue, wait time and bank agent use made-up data. |
| Planned (not built) | Real bank data and login; urgent-case priority; notifications. |

## Technology

- **Python 3, standard library only (`http.server`):** web server and dialogue controller in `app.py`. Nothing to install.
- **HTML/CSS/JavaScript:** chat page in `index.html`.
- **Help pages:** Markdown files in `corpus/` cover statements, payment confirmation, bank letters and cards. This is the only source the bot answers from; `retrieve.py` searches it.
- **Model wrapper:** `model.py` and `mock_model.py` return recorded replies from `recorded_runs/note_*.json`.
- **Bank data:** `bank_data.py` contains customer needs, everyday words, related options, and made-up accounts and payments.
- **System diagram:** created in draw.io.

I use a rule-based controller to keep behaviour predictable and safe when handling money. The only AI part is the note drafter, and the customer confirms its output.

Recorded replies mean the project runs without an API key or cost and gives the same results every test.

**Live model for the note drafter:** not decided yet. The wrapper works with any chat-completions endpoint, so a live model can be swapped in later.

## Run locally

Run the server:

```bash
python app.py
```

Then open:

http://localhost:8001

I use port 8001 because port 8000 was used by another program on my laptop.

To use another port:

```bash
python app.py --port 8002
```

### Check the everyday-words matcher

```bash
python bank_data.py
```

Expected output:

```text
11 of 12 phrases reached the right need
```

### Check what happens if the AI note comes back broken

```powershell
$env:IIS_MOCK_BREAK="1"; python app.py
```

The bot does not pass the broken note on. It says "I couldn't draft the note. Please fill it in." and the customer writes it.

### Live model configuration

No keys are stored. To try a live model, set your own values in the terminal, never in a file. In Windows PowerShell:

```powershell
$env:IIS_MODEL="http"; $env:IIS_MODEL_URL="<endpoint>"; $env:IIS_API_KEY="<your key>"; python app.py
```

## Original and reused work

I reused `retrieve.py` and `model.py` unchanged from the module's Lab 4 pack.

I changed `mock_model.py` so it returns my recorded notes (`recorded_runs/note_*.json`); `malformed.txt` is from Lab 4. I also reused the web-server pattern in `app.py`.

The original, unchanged Lab 4 pack can be seen in commit [611928f](https://github.com/jyo-11/A2_project_iis/commit/611928f).

My own work includes the bank help pages, `bank_data.py`, the two-path dialogue in `app.py`, the chat page, the recorded AI notes, testing and the design.

## Development record

### 1. Start

I started from the Lab 4 prototype unchanged, so my own changes are easy to see:

https://github.com/jyo-11/A2_project_iis/commit/611928f

At the end, I removed the Lab 4 files my chatbot does not use (handouts, `tools.py`, `vlm.py`, sample images and old recorded replies), so the repository shows only this project.

I replaced the course documents with bank help pages, then split payment confirmation and bank letters into separate pages:

https://github.com/jyo-11/A2_project_iis/commit/ddb72c5

https://github.com/jyo-11/A2_project_iis/commit/c9a96cc

### 2. Understanding everyday words

I added needs, everyday words and made-up payments because customers may not know bank terms:

https://github.com/jyo-11/A2_project_iis/commit/bf2e1f6

The phrase test went from 10 of 12 to 11 of 12 after I changed the words:

https://github.com/jyo-11/A2_project_iis/commit/4453307

Each option shows how quickly it is ready, so customers can choose what fits their deadline. In my real chat, I was only offered a statement that took hours:

https://github.com/jyo-11/A2_project_iis/commit/89e10c6

The word "letter" alone was too vague, so I only use it when nothing more specific matches:

https://github.com/jyo-11/A2_project_iis/commit/e81d6dd

### 3. Two paths

Path A answers from a help page and shows the source. Path B drafts a note, the customer checks it, and then a person takes over:

https://github.com/jyo-11/A2_project_iis/commit/452b687

The recorded AI notes include one that deliberately picks the wrong need, to test whether the customer check catches it:

https://github.com/jyo-11/A2_project_iis/commit/8a03399

### 4. Changes from my own testing

Answers appeared as one long block, so I changed the help pages to keep their steps and bold text. "Statement" left me asking "statement of what?", so the bot now asks which account and month:

https://github.com/jyo-11/A2_project_iis/commit/d816bd1

"Hi" triggered the menu, so I added a greeting. A missing payment had no way forward, so "None of these" now explains the delay and offers a person:

https://github.com/jyo-11/A2_project_iis/commit/a6ffc57

I made the timings more realistic: statements are ready straight away and a balance letter is ready the same working day:

https://github.com/jyo-11/A2_project_iis/commit/dc20344

A single "Did you mean…?" gave no real choice, so the bot now states its best guess and shows related options:

https://github.com/jyo-11/A2_project_iis/commit/a875221

I changed the port to 8001:

https://github.com/jyo-11/A2_project_iis/commit/b556c00

### 5. Testing

The phrase test reached 11 of 12 phrases. Only "a payment I never made" reached the wrong need.

I also tested Path A, Path B and unclear requests by hand in the browser, starting a new chat each time. I took screenshots of each run; these are the screenshots in `docs/` and in Figures 3 and 4 of the report.

I found that if the customer sends the note without reading it, the agent still gets the wrong need. The handover is therefore only as accurate as the customer's check.

## AI assistance

- **Claude (in Antigravity and Claude Code), prototype:** helped write most of the code and the structure of the prototype from my design: the two paths, the customer check and the recorded notes. I ran every path by hand in the browser. My own testing found gaps ("hi" showed the whole menu, a missing payment had no way forward, one "Did you mean…?" option gave no real choice), and I decided how each should be fixed (see Development record, section 4).
- **Claude, system diagram:** I gave it the structure (the parts, the two paths, and which parts are implemented, simulated or planned) and it drew the diagram in draw.io.
- **Claude, report and README:** it checked my report against the brief and listed what was missing, and it drafted this README from my commits. I decided what to change and checked the facts against my code.
- **ChatGPT:** generated the drawings for Figure 2 (the problem I experienced). The storyboard idea, scenes and captions are mine. It also polished the wording of this README.
- **No AI:** Figures 3 and 4 are screenshots of my own test runs, which I laid out in Canva myself.

## Additional files

| File / folder | Contents |
|---|---|
| `docs/1.png`–`5.png` | Storyboard pages used in the report (Figures 2 to 4), laid out in Canva. |
| `docs/A1.png`–`A4.png`, `B1.png`–`B5.png` | Screenshots of Path A and Path B used in the storyboards. |
| `docs/system-diagram.drawio` / `.png` | System diagram. Open the `.drawio` file at app.diagrams.net. |

No ZIP is needed.
