# Solo D&D

A solo Dungeons & Dragons 5e setup for Claude Code. One player, one character,
a sidekick, and a Dungeon Master that runs published adventures straight from
PDFs you own.

**→ [SETUP.md](SETUP.md)** to get started.

```bash
./tools/candlekeep.py list                          # what books do I have?
./tools/candlekeep.py pages phandelver -p "21-23"   # what's in this encounter?
claude                                              # play
```

Campaign state lives in `campaigns/` and is committed to git — the repo is the
save file, so a campaign survives across machines and sessions.
