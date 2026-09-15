# MigrAIte — User Guide

MigrAIte migrates a webMethods Integration Server package to a Workato
recipe, driven entirely from Google Chat. You upload the package, review the
analysis it produces, approve it, and it builds the recipe in your Workato
workspace.

---

## What it does — and doesn't

**Does**
- Reads every file in the package (flow services, adapters, document types,
  manifests) and writes a full analysis: what the integration does, the
  systems involved, every construct and how it maps to Workato, data
  mappings, business rules, error handling, and a proposed recipe structure.
- Flags gaps and deviations it cannot resolve from the package alone
  (endpoints, credentials, source defects) so you can decide.
- Revises the analysis from your feedback until you approve it.
- Builds the recipe in the Workato folder you choose, and tells you exactly
  which manual steps remain.

**Doesn't**
- Create or authorize connections (HTTP, Oracle, SFTP…) — those need real
  credentials and are done in the Workato UI afterwards.
- Migrate things with no Workato equivalent without telling you (for example
  custom flat-file generation); these appear in the gaps section.
- Run anything against your systems. It reads the package and writes a
  recipe; nothing executes until you turn the recipe on.

---

## Starting a migration

1. Open the MigrAIte space (or a direct message with the app).
2. In a **new thread**, @mention the app and **attach the package zip** — the
   folder exported from webMethods IS (it contains `manifest.v3`, `ns/`,
   `pub/`). In a direct message no @mention is needed.
3. Optionally add instructions in the same message, e.g. "focus on the ACH
   path; the CheckWriter service is being retired". They are honored
   throughout.

You'll see **📦 Received &lt;package&gt;. Starting analysis** within a few
seconds. Ignore the "migrAIte isn't responding" banner that flashes when you
post — it is a Google Chat quirk for this kind of app and clears on its own.

---

## What to expect

| Phase | Duration | What you see |
|---|---|---|
| Analysis | 10–15 min | "⏳ Still working…" every few minutes, then one summary message ending with a question |
| Review | your pace | Links to the analysis as Google Docs; the conversation waits for you |
| Build | 20–30 min | Heartbeats, then one final message with the recipe link and remaining steps |

The bot only speaks when it has something for you: a summary, a question, a
result. Every message ends with a small cost footer so you can see what a
run costs.

---

## Reviewing the analysis

The summary message is followed by **📄 Analysis documents** with two links:

- **Package Analysis (Workato blueprint)** — what will be built: recipe
  structure, connections, mappings, rules, error handling, gaps. This is the
  document you are approving.
- **Detailed Source Analysis** — the evidence: every component of the
  package, decoded.

Two ways to give feedback, use either or both:

- **Reply in the thread** — "the Wire payment path is intentional, drop gap
  G-4", "ACH should use the Oracle connector".
- **Edit the Google Doc directly** — change the text, add notes. When you
  next reply in the thread, the bot picks the edits up (you'll see
  "📝 Picked up your edits from Google Docs") and treats the edited document
  as authoritative.

After each round the bot revises and checks in again. Notes: put feedback in
the Doc's *text* — Doc comments are not read; and reply **in the thread** of
your migration, not in a new thread (a new thread starts a new
conversation).

When it asks a question, answer it directly; it asks one at a time.

---

## Approving and building

1. Reply **"approved"** (or words to that effect) when the blueprint is
   right.
2. It asks **which Workato folder** to build in and suggests a default.
   Answer with the folder name or id.
3. The build runs. The final message contains:
   - the **recipe URL** in your workspace,
   - what was built (trigger, loops, branches, error handling),
   - **remaining manual steps** — usually creating connections in the
     Workato UI and wiring them to the listed steps, and any values that need
     a subject-matter expert (endpoint URLs, stored-procedure names).
4. Want changes? Keep replying in the thread: "rename step 4", "add a logger
   in the rescue block". It updates the same recipe.

---

## Commands

| Command | Effect |
|---|---|
| `/abort` | Stop the current migration immediately |
| `/new` | Reset the conversation so you can start another migration in it |
| `/continue` | Resume after a cost or turn limit pause (the bot tells you when this applies) |

---

## Good to know

- **One migration at a time.** If another migration is running, the bot asks
  you to wait.
- **Time limits.** Very long steps may pause with "hit the time limit" — send
  any message to continue.
- **Cost limits.** Each conversation has a spend cap; if reached, the bot
  pauses and offers `/continue` or `/abort`.
- **Where things live.** Analysis Docs are in the shared MigrAIte Drive
  folder under `<package> — <date> — <requester>`; the recipe is in the
  Workato folder you chose.
- **Support.** Reply in the thread with what you saw, or contact TechStone
  with the package name and the time of the run.
