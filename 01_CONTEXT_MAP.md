# 01_CONTEXT_MAP.md

## What this file is for

Context means **all the information your app sends to the model for one request**. In the supplied
Lab 4 starting app, the model receives only the current user message. If you use a different app,
replace the examples below with what you actually observe.

Run `python app.py`, make one normal request in the browser, and read the `CONTEXT:` lines in the
terminal. Fill in one row for each part that your app actually sends. The rows below are examples:
change them if your app uses different parts. If a part is not present, write `not present`.

| part | where it comes from | what kind of information it is | size |
|---|---|---|---|
| current user message | message entered in the browser | user input | short |
| app instructions | not present in the model request | not present | not present |
| history | not present in the model request | not present | not present |
| retrieved passages | not present in the model request; retrieval results are displayed after the model call | not present in the model request | not present |
| tool definitions | not present in the model request; the app handles its fixed tool call separately | not present | not present |

For the third column, write what kind of information it is. For example: `instructions from my app`,
`user input`, or `quoted source material`. This helps you notice when outside text is being treated
like an instruction.

For `size`, write `short`, `medium` or `long`. You do not need an exact token count.

**Removal decision:** `nothing redundant to remove` for the supplied starting app. If your app has a redundant part, name what you removed and why.

**One thing I would review after retrieval is added:** <name a part to review, or write `not applicable yet`>
