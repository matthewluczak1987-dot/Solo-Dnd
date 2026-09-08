# Setup

Local setup, start to finish. Should take about ten minutes.

## 1. Clone the repo

```bash
git clone https://github.com/matthewluczak1987-dot/solo-dnd.git
cd solo-dnd
```

## 2. Install `uv`

The book-query tool declares its own dependencies inline, so `uv` is the only
prerequisite — no virtualenv, no `pip install` step.

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify: `uv --version`

## 3. Add your adventure PDF

Drop a PDF of an adventure you own into `books/`:

```bash
cp ~/Downloads/lost-mine-of-phandelver.pdf books/
./tools/candlekeep.py list
```

You should see the book listed. Then confirm text extraction works:

```bash
./tools/candlekeep.py toc phandelver
./tools/candlekeep.py search phandelver "Cragmaw"
```

If pages come back empty, the PDF is a scan with no text layer — run it through
OCR first (`ocrmypdf in.pdf out.pdf`).

## 4. Optional: NPC voices

Skip this if you don't want text-to-speech; everything works without it.

```bash
cd .claude/skills/solo-dm
npm install
echo "ELEVENLABS_API_KEY=your_key_here" > .env
```

Free key from https://elevenlabs.io/app/settings/api-keys.
Audio playback needs `afplay` (macOS, built in) or `mpg123` (Linux).

## 5. Start playing

From the repo root:

```bash
claude
```

Then: **"Let's roll up a character and start Lost Mine of Phandelver."**

The `solo-dm` skill activates automatically. To resume later, say
**"continue lost-mine"**.

---

## What's here

| Path | Purpose |
|---|---|
| `tools/candlekeep.py` | Queries your adventure PDFs by page, TOC, or keyword |
| `.claude/skills/solo-dm/` | The DM skill — solo rules, encounter scaling, session logging |
| `.claude/skills/solo-dm/roll-dice.sh` | Dice roller with advantage/disadvantage and hidden rolls |
| `.claude/skills/solo-dm/speak-npc.js` | Optional ElevenLabs NPC voices |
| `books/` | Your adventure PDFs (gitignored) |
| `campaigns/` | Campaign state — your save files, committed to git |

## Notes on what was changed from the original skill

This repo is a fork of the `dnd-dm` skill bundled with the MCPmarket plugin, with
three fixes that were needed to make it run:

1. **The book tool was rebuilt.** The original called a private CLI at a hardcoded
   path on the skill author's own machine (`/Users/saharcarmel/.../CandleKeep`),
   which isn't a public project. `tools/candlekeep.py` is a self-contained
   replacement with the same `list` / `toc` / `pages` interface, plus `search`.
2. **Solo rules were added.** The original assumes a 4-5 person party. Running an
   unmodified published encounter with one 1st-level character is lethal, so the
   skill now carries an encounter-rescaling table, sidekick guidance, and safety nets.
3. **Campaign state moved** from `.claude/skills/dnd-dm/sessions/` to `campaigns/`,
   so saves are ordinary tracked files rather than buried inside a skill directory.
