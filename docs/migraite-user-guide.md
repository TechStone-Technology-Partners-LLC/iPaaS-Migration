# MigrAIte — User Guide

## What MigrAIte is

MigrAIte is an interactive way of using an AI migration agent. You talk to
it in Google Chat. It turns a webMethods Integration Server package into a
Workato recipe, and it does the slow parts for you: reading every file in
the package, writing the analysis and design document, and building the
recipe through Workato's AIRO.

Your job is to review and decide. The agent does the rest.

**The flow, start to finish:**

1. Send it the package zip.
2. It analyzes the package and writes an analysis and a design document.
3. You go back and forth with it until the analysis and design are right.
4. You tell it to build. It builds the recipe in Workato using AIRO.
5. You check the recipe in Workato. If you have more changes, keep talking
   to it in the same chat and it will keep working on them.

You can keep iterating for as long as you have not started a new session.

**What it does not do:**

- Create or authorize connections (HTTP, Oracle, SFTP). Those need real
  credentials and are done in the Workato UI afterwards.
- Migrate things with no Workato equivalent without telling you. These show
  up in the gaps section of the analysis.
- Run anything against your systems. Nothing executes until you turn the
  recipe on.

---

## Step by step

### 1. Find the app

There is nothing to download or install. MigrAIte is a Google Chat app.

1. Open Google Chat (chat.google.com, or the Chat tab in Gmail).
2. Click **New chat** and search for **migrAIte**.
3. Start a chat with it.

If the app does not show up in search, ask your admin to add you to its
visibility list.

Three words come up throughout this guide. From broadest to narrowest:

- **Chat** is the window where you talk to the migrAIte app. It is just the
  UI. One chat can hold many sessions over time.
- **Session** is one conversation with the agent. Everything you and the
  agent have said, and everything it has learned about your package, is
  remembered for the life of the session.
- **Migration** happens inside a session: one package, analyzed and built.

If you restart the session, the memory and context for that migration are
gone, even though you are still in the same chat.

**One chat holds one session at a time.** Three commands control it:

| Command | What it does |
|---|---|
| `/new` or `/reset` | Start a fresh session in this chat |
| `/abort` | Stop the current migration immediately, even mid-step |
| `/continue` | Resume after the bot pauses for a cost or time limit. It tells you when this applies |

### 2. Send the package

1. Export the package from webMethods IS as a zip. It should contain
   `manifest.v3`, `ns/` and `pub/`.
2. Attach the zip to a message.
3. Optionally add instructions in the same message, for example "focus on
   the ACH path" or "the CheckWriter service is being retired". The agent
   honors these for the whole run. You can also send the zip with no text.
4. Send it.

Within a few seconds you should see:

> 📦 Received *PackageName*. Starting analysis — I'll post progress here and ask when I need input.

> **Side note: two Google Chat quirks to ignore.**
> Google Chat briefly flashes **"migrAIte isn't responding"** every time you
> post. It clears on its own.
> Google Chat may also say the **zip was removed for a policy violation**.
> The bot still received and read it. As long as you got the "📦 Received"
> message, everything is working.

### 3. Wait for the analysis

Analysis takes about **3 to 7 minutes**.

While it works, the bot posts **⏳ Still working…** roughly **every 3
minutes**. That is your sign it is alive. Nothing else is posted until it
has a result.

**If you see no message at all for more than 5 minutes**, the bot is
probably hung. Do not re-upload the zip. Contact your admin with the package
name and the time you sent it.

When analysis finishes you get one summary message: what the package does,
which systems it talks to, the proposed recipe structure, and any gaps it
could not resolve. It ends with **one question**. Answer that question.

### 4. Open the documents

Right after the summary, the bot posts links:

> 📄 Analysis documents (edit in place — your edits are picked up when you reply here):
> 📁 Run folder: …
> • Package Analysis (Workato blueprint): …
> • Detailed Source Analysis: …

These live in a **shared Google Drive**, in a folder named
`<Package> — <date time> — <your name>`.

- **Package Analysis (Workato blueprint)** is the design document you are
  approving. It describes exactly what will be built.
- **Detailed Source Analysis** is the evidence: every component of the
  package, decoded.

You should already have access to the shared drive. If a link asks you to
request access, ask your admin to add you as a **Contributor**. You need edit
rights to give feedback in the Doc.

### 5. Give feedback

There are two ways to change the analysis. Use either, or both.

**Reply in the chat.** Type what you want changed.

> "The Wire payment path is intentional, drop gap G-4."
> "ACH should use the Oracle connector, not HTTP."

**Edit the Google Doc.** Open the Package Analysis Doc, change the text
directly, then send **any message** in the chat (even just "updated the
doc"). The bot reads your edits first and confirms with:

> 📝 Picked up your edits from Google Docs: PackageAnalysis.md

The edited Doc is then treated as the source of truth.

Two rules:

- Edit the Doc's **text**. Doc *comments* are not read.
- The bot asks **one question at a time**. Answer it directly.

After each round the bot revises the Docs, updates the same links, and
checks in again. Repeat until you are happy.

### 6. Approve and build

1. Reply **"approved"** (any clear wording works).
2. The bot asks **which Workato folder** to build in and suggests a default.
   Reply with the folder name or id.
3. The build takes **5 to 10 minutes**. The same heartbeat rule applies: a
   ⏳ every 3 minutes means it is working.
4. The final message contains:
   - the **recipe URL** in Workato,
   - what was built (trigger, loops, branches, error handling),
   - **remaining manual steps**. These are usually connections that need
     real credentials, which you create and wire in the Workato UI, plus
     any values that need a subject-matter expert (endpoint URLs, stored
     procedure names).

### 7. Keep iterating after the build

The session does not end when the recipe is built. Go check the recipe in
Workato. If you want changes:

- Edit the Package Analysis Doc and send a message, or
- Describe the change in the chat: "rename step 4", "add a logger in the
  rescue block".

The bot updates the documents and builds again.

**By default it creates a new recipe** rather than changing the one it
already built. If you want the existing recipe changed in place, say so:
"update the existing recipe, do not create a new one."

This works for as long as the session is open. Once you send `/new`, the
old session is gone and you start over with a zip.

---

## Things that will trip you up

- **One migration at a time.** If someone else's run is in progress, you
  get "🚧 A migration is already running". Wait and retry.
- **Messages sent mid-step are not lost.** If you reply while the bot is
  working, it says "⏳ Still working on the previous step" and uses your
  latest message as soon as it is free. An early "approved" is fine.
- **Cost limit.** Each session has a spend cap. When it is hit the bot
  pauses and offers `/continue` or `/abort`. Every bot message ends with a
  small cost footer so you can see what a run costs.
- **Time limit.** A very long step may stop with "⏱️ That step hit the time
  limit." Send any message to continue.
- **"⚠️ Something went wrong during that step."** Send any message to
  retry. If it happens twice in a row, contact your admin.
- **Drive delivery failed.** If a Doc link is replaced by "⚠️ Drive
  delivery failed (network)", the file is still safe. Reply with anything
  and the bot retries the upload.
- **Finished session.** After `/abort` the session is done. Send `/new` to
  start another.

---

## Getting help

Reply in the chat with what you saw. If the bot is not responding at all,
contact your admin with the package name and the time of the run.
