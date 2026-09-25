# Computer tab — source

`python3 integrate.py` rebuilds `../UPSC-ISS-Statistics-Dashboard-STANDALONE.html`
from the uploaded dashboard (`base/`) plus the files below. The build fails if
any chapter would produce a practice set outside 40–50 questions.

| Path | What it holds |
|---|---|
| `bank/chNN.txt` | Question bank, one file per book chapter (2009 book questions + 44 ISS Boosters) |
| `sheets/chNN.txt` | Crisp pointers for UPSC ISS Paper-I, one sheet per chapter |
| `cs-tab.js` / `cs-tab.css` | Computer tab screens: chapter tabs, sets, learning/exam modes, pointers |
| `mobile.js` / `mobile.css` | Android-style phone shell: bottom nav, session bar, swipe, back button |
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
B: b                  book's printed key, only when it is wrong
X: Explanation
S: 15-second exam shortcut
N: Note shown with the answer

#121 iss              ISS Booster (written for the dashboard, not from the book)
R: ISS 2021 Q14       previous-year question it mirrors
```

Optional `T:` overrides the question type and `C:` the topic code.
