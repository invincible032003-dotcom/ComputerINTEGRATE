# Computer tab — source

`python3 integrate.py` rebuilds `../UPSC-ISS-Statistics-Dashboard-STANDALONE.html`
from the uploaded dashboard (`base/`) plus the files below. The build fails if
any chapter would produce a practice set outside 40–50 questions.

| Path | What it holds |
|---|---|
| `bank/chNN.txt` | Question bank, one file per book chapter (2009 book questions + 44 added to fill sets) |
| `sheets/chNN.txt` | Crisp pointers, one sheet per chapter (`## Section` + `- bullet`; a leading ★ marks a high-yield point) |
| `cs-tab.js` / `cs-tab.css` | Computer tab screens: chapter chips, sets, Learn/Exam sessions, fold-out pointers, one-at-a-time Revise |
| `mobile.js` / `mobile.css` | Android-style phone shell: titled app bar, bottom nav, session bar, palette bottom sheet, swipe, back button |
| `tools/smoke_test.js` | Headless check on desktop and a 360 px phone: `NODE_PATH=$(npm root -g) node tools/smoke_test.js ../UPSC-ISS-Statistics-Dashboard-STANDALONE.html <outdir>` |
| `tools/ocr_*.py`, `merge_ocr.py`, `parse_ocr.py`, `auto_clean.py` | One-off OCR pipeline used to transcribe the book (work dir: `$OCR_WORK`) |

## Bank format

```
@chapter 3
@title Computer Memory
@pages 138-167 168-194  question pages, answer pages
@codes C3 C1 C2       topic codes allowed in this chapter (first match wins)
@default C3           code used when no rule matches
@themes 1 Set-1 theme text

#12 p88 a97           book question 12, question page 88, answer page 97
Q: Stem text (`code` in backticks, math in \( \))
- statement line      (optional, for statement-type items)
?: Which of the above is/are correct?
a) … b) … c) … d)     two or four options
K: c                  correct key
B: b                  book's printed key, only when it is wrong (not shipped)
X: Explanation
S: 15-second exam shortcut
N: Maintainer note, e.g. why the printed key was corrected (not shipped)

#121 iss              added question (not from the book) that fills a set to 40-50
R: reference          what the added question is modelled on (not shipped)
```

Only clean study content reaches the dashboard: topic, question, options,
explanation and shortcut. Page numbers, printed keys, notes and references
stay in the bank files as the audit trail.

Optional `T:` overrides the question type and `C:` the topic code.
