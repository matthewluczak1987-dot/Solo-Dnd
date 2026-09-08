# Windows Setup — Step by Step

Written for someone who has never used a terminal. Follow it top to bottom;
each step has a check so you know it worked before moving on.

**Before you start:** Claude Code needs a paid Claude plan (Pro, Max, Team, or
Enterprise). The free claude.ai plan does not include it.

---

## How to open PowerShell

You'll type commands into a program called PowerShell.

1. Press the **Windows key**
2. Type `powershell`
3. Click **Windows PowerShell**

A blue window opens with a prompt like `PS C:\Users\YourName>`. That `PS` at the
start matters — if it's missing, you're in a different program (CMD) and the
commands below won't work.

To run a command: click in the window, type it (or paste with **right-click**),
press **Enter**.

---

## Step 1 — Install Git for Windows

This is **required**, not optional. The dice roller is a script that needs Git's
bash shell to run, and you also need Git to download this project.

1. Go to https://git-scm.com/downloads/win
2. Download the **64-bit Git for Windows Setup**
3. Run the installer and click Next through every screen — the defaults are fine

**Check it worked.** Close PowerShell, open a fresh one, and run:

```powershell
git --version
```

You should see something like `git version 2.47.1.windows.1`.

> If you get `'git' is not recognized`, the install didn't finish or you didn't
> open a *new* PowerShell window. Close it, open a new one, try again.

---

## Step 2 — Install Claude Code

```powershell
irm https://claude.ai/install.ps1 | iex
```

Then **close PowerShell and open a new one** so it can find the new program.

**Check it worked:**

```powershell
claude --version
```

You should see a version number like `2.1.263 (Claude Code)`.

---

## Step 3 — Install uv

This runs the tool that reads your adventure PDFs.

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Again: **close PowerShell, open a new one.**

**Check it worked:**

```powershell
uv --version
```

---

## Step 4 — Download this project

```powershell
cd $HOME\Documents
git clone https://github.com/matthewluczak1987-dot/Solo-Dnd.git
cd Solo-Dnd
```

This puts the project in your Documents folder and moves you into it.

> **Important:** every command from here on must be run from inside this folder.
> If you close PowerShell and come back later, run `cd $HOME\Documents\Solo-Dnd`
> first. To check where you are, run `pwd`.

**Check it worked:**

```powershell
ls
```

You should see `books`, `campaigns`, `tools`, `README.md`, and others.

---

## Step 5 — Add your adventure PDF

Get a PDF of an adventure you own — the D&D Beyond digital version, a
DriveThruRPG download, or a publisher PDF. *Lost Mine of Phandelver* comes with
the 5e Starter Set, and is also inside *Phandelver and Below: The Shattered Obelisk*.

Copy it into the `books` folder. Easiest way: open File Explorer, navigate to
`Documents\Solo-Dnd\books`, and drag the PDF in.

Or from PowerShell, if it's in your Downloads:

```powershell
copy $HOME\Downloads\lost-mine-of-phandelver.pdf books\
```

**Check it worked:**

```powershell
uv run tools/candlekeep.py list
```

You should see your book listed with a number next to it. The first time you run
this, uv downloads what it needs — that can take a minute. It's instant after that.

---

## Step 6 — Confirm the PDF is readable

This is the step that catches the most common problem, so don't skip it.

```powershell
uv run tools/candlekeep.py toc phandelver
```

Replace `phandelver` with part of your file's name if it's called something else.

- **You see a list of chapters** → you're good, move on.
- **You see "No embedded table of contents"** → that's fine. Try a search instead:
  `uv run tools/candlekeep.py search phandelver "goblin"`. If that returns lines
  of text, everything works.
- **Everything comes back empty** → your PDF is a scan (pictures of pages, not
  real text). It needs OCR before it can be read. Tell Claude and it can walk you
  through fixing it.

---

## Step 7 — Start playing

```powershell
claude
```

The first time, it opens a browser window to log in to your Claude account.

Then just type what you want:

> Let's roll up a character and start Lost Mine of Phandelver.

To pick up an existing game later, start `claude` from the same folder and say
**"continue lost-mine"**.

**That's everything you need to play.** Voice acting below is entirely optional.

---

# Optional — NPC Voice Acting

This makes NPCs speak out loud in character voices. It costs money past a small
free allowance, and the game plays perfectly well without it. Skip it if you're
not sure — you can always add it later.

## Step A — Install Node.js

1. Go to https://nodejs.org
2. Download the **LTS** version
3. Run the installer, accept the defaults

Close PowerShell, open a new one, and check:

```powershell
node --version
```

## Step B — Install the voice tool's dependencies

From inside the project folder:

```powershell
cd $HOME\Documents\Solo-Dnd\.claude\skills\solo-dm
npm install
```

This downloads the ElevenLabs library. Takes a minute.

## Step C — Get an ElevenLabs API key

An "API key" is a long password that lets the tool use your account.

1. Sign up at https://elevenlabs.io
2. Go to https://elevenlabs.io/app/settings/api-keys
3. Create a key and copy it

Check their current pricing page for what the free tier includes — it's a limited
number of characters per month, and each spoken NPC line uses some of it.

## Step D — Save the key

Still in the `solo-dm` folder:

```powershell
copy .env.example .env
notepad .env
```

Notepad opens. Replace `your_api_key_here` with the key you copied, so the line
reads `ELEVENLABS_API_KEY=sk_abc123...`. Save (**Ctrl+S**) and close.

> **Keep this key private.** It's tied to your billing. The project is already
> set up to never upload `.env` to GitHub.

## Step E — Test it

```powershell
node speak-npc.js --text "You dare enter Klarg's lair?" --voice villain --npc "Klarg"
```

You should hear a voice. Then go back to the project root:

```powershell
cd $HOME\Documents\Solo-Dnd
```

If you hear nothing but see no error, your PC's volume or output device is the
likely culprit. If you get an error mentioning the API key, re-check Step D.

---

## If something goes wrong

Start Claude Code in the project folder (`claude`) and describe what happened —
paste the error text in. It can read the project files and diagnose it directly.
