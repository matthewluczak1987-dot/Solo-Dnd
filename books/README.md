# Adventure Books

Drop PDFs of adventures **you own** into this directory. They are gitignored and
never leave your machine — the DM reads them locally to pull exact encounter text,
stat blocks, and room descriptions instead of working from memory.

```
books/
  lost-mine-of-phandelver.pdf
  monster-manual.pdf
```

Any filename works. Reference a book by number or by any unique part of its name:

```bash
./tools/candlekeep.py list
./tools/candlekeep.py toc phandelver
./tools/candlekeep.py pages phandelver -p "21-23"
./tools/candlekeep.py search phandelver "Klarg"
```

**A note on sourcing:** use PDFs you have legitimately purchased — the D&D Beyond
digital version, a DriveThruRPG download, or a publisher's PDF. *Lost Mine of
Phandelver* ships with the 5e Starter Set; it is also included in
*Phandelver and Below: The Shattered Obelisk*.

Scanned PDFs without a text layer will return empty pages. If that happens, run the
file through OCR (`ocrmypdf in.pdf out.pdf`) and re-index.
