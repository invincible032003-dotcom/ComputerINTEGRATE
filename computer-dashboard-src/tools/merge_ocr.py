"""Merge two OCR readings (v2 threshold, v3 stroke-repair) word by word and
spell-correct what neither reading got right.

Validity of a word = English frequency (pyspellchecker) or frequency in the
book itself (both readings pooled).  Where the readings differ we keep the
more plausible word; leftover unknown words are corrected with SymSpell
against English + the book's own vocabulary.
"""
import re, os, glob, math, difflib, json
from collections import Counter
from spellchecker import SpellChecker
from symspellpy import SymSpell, Verbosity

SP = os.environ.get('OCR_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work'))  # OCR scratch dir
V2, V3, OUT = SP + '/ocr2', SP + '/ocr3', SP + '/ocrm'
os.makedirs(OUT, exist_ok=True)

EN = SpellChecker().word_frequency
TOK = re.compile(r'\S+')
CORE = re.compile(r'^([^A-Za-z0-9]*)(.*?)([^A-Za-z0-9]*)$')


def cols(path):
    if not os.path.exists(path):
        return {}
    txt = open(path).read()
    parts = re.split(r'=====(TOP|LEFT|RIGHT)\n', txt)
    return {parts[k]: parts[k + 1] for k in range(1, len(parts), 2)}


pages = sorted(int(os.path.basename(p)[1:4]) for p in glob.glob(V2 + '/p*.txt'))
pages = [p for p in pages if p >= 11]

# corpus vocabulary from both readings
corpus = Counter()
for gp in pages:
    for src in (V2, V3):
        for c in cols(f'{src}/p{gp:03d}.txt').values():
            for t in TOK.findall(c):
                w = CORE.match(t).group(2).lower()
                if w.isalpha():
                    corpus[w] += 1


def score(tok):
    w = CORE.match(tok).group(2)
    lw = w.lower()
    if not lw:
        return 0.0
    if not re.fullmatch(r"[A-Za-z][a-z'\-]*|[A-Z0-9/\-\.]+|[0-9.,%]+", w):
        return -3.0  # mixed garbage like "get.Pration", "197@="
    e = EN[lw] if lw in EN else 0
    c = corpus[lw]
    if e == 0 and c < 3:
        return -1.0
    return math.log10(1 + e) + 1.5 * math.log10(1 + c)


def merge_col(a, b):
    """a, b: column texts. Returns merged text with a's line structure."""
    la = a.split('\n')
    ta = []  # (token, line index)
    for i, line in enumerate(la):
        for t in TOK.findall(line):
            ta.append((t, i))
    tb = TOK.findall(b)
    sa = [t for t, _ in ta]
    sm = difflib.SequenceMatcher(None, sa, tb, autojunk=False)
    out = list(sa)
    for op, i1, i2, j1, j2 in sm.get_opcodes():
        if op != 'replace':
            continue
        if i2 - i1 == j2 - j1:
            for k in range(i2 - i1):
                x, y = sa[i1 + k], tb[j1 + k]
                if score(y) > score(x) + 0.3:
                    out[i1 + k] = y
        elif i2 - i1 == 1 and j2 - j1 == 2:
            # "developnent" vs "develop ment": leave
            pass
    lines = [[] for _ in la]
    for (t, i), o in zip(ta, out):
        lines[i].append(o)
    return '\n'.join(' '.join(l) for l in lines)


# SymSpell over English + book vocabulary (garbled variants excluded)
sym = SymSpell(max_dictionary_edit_distance=2, prefix_length=8)
VOCAB = {}
for w, f in EN.dictionary.items():
    if w.isalpha() and f >= 30:
        VOCAB[w] = f
for w, f in corpus.items():
    if (w in EN and EN[w] >= 5) or f >= 15:
        VOCAB[w] = VOCAB.get(w, 0) + f * 3000
for w, f in VOCAB.items():
    sym.create_dictionary_entry(w, f)

CHEAP = {('i', 'l'), ('l', 'i'), ('c', 'e'), ('e', 'c'), ('a', 'o'), ('o', 'a'), ('n', 'h'), ('h', 'n'),
         ('rn', 'm'), ('in', 'm'), ('ii', 'n'), ('li', 'h'), ('cl', 'd'), ('vv', 'w'), ('u', 'n'),
         ('n', 'u'), ('t', 'f'), ('f', 't'), ('a', 'd'), ('d', 'a'), ('s', 'e'), ('z', 's'), ('v', 'y'),
         ('c', 'o'), ('o', 'c'), ('i', 'r'), ('r', 'i'), ('l', 't'), ('t', 'l'), ('e', 'o'), ('o', 'e'),
         ('ri', 'n'), ('n', 'ri'), ('m', 'rn'), ('i', 'f'), ('f', 'i'), ('s', 'a'), ('a', 's'), ('y', 'v'),
         ('k', 'h'), ('h', 'k'), ('b', 'h'), ('h', 'b'), ('g', 'q'), ('q', 'g'), ('e', 'a'), ('i', 'j'),
         ('ni', 'm'), ('iv', 'w'), ('c', 'r'), ('r', 'c'), ('n', 'r'), ('r', 'n'), ('ll', 'n'), ('t', 'i'),
         ('i', 't'), ('1', 'l'), ('l', '1'), ('0', 'o'), ('5', 's'), ('8', 'b'), ('v', 'r'), ('r', 'v'),
         ('p', 'n'), ('n', 'p'), ('ct', 'd'), ('cj', 'g'), ('j', 'i'), ('s', 'z'), ('w', 'v')}


def ocr_cost(a, b):
    cost = 0.0
    for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if op == 'equal':
            continue
        x, y = a[i1:i2], b[j1:j2]
        if op == 'replace':
            if (x, y) in CHEAP:
                cost += 0.35
            elif len(x) == len(y):
                cost += 1.0 * len(x)
            else:
                cost += 1.0 * max(len(x), len(y))
        else:
            cost += 0.8 * max(len(x), len(y))
    return cost


fixed = Counter()
unknown = Counter()
PROTECT = set('''neumann overclocking webcams webcam stdout stdin stderr txt dropbox pagerank zuckerberg
worldwideweb datasets defragmenter northbridge southbridge printf scanf malloc calloc realloc sizeof typedef
struct enum const argc argv fopen fclose fprintf fscanf fgets fputs getchar putchar strlen strcpy strcat strcmp
eeprom eprom prom dram sram sdram ddr bios cmos uefi gpu cpu alu ram rom hdd ssd usb lan wan man pan isp url
html http https ftp smtp pop imap dns dhcp tcp udp ip wifi bluetooth nand nor xor xnor latin unicode ascii
ebcdic bcd excess gray hamming parity dbms rdbms sql nosql mysql oracle java python cobol fortran pascal basic
linux unix windows macos android ios kernel shell gui cli bitwise ptr int char float double void'''.split())
BADTARGET = {'ternary', 'hermann', 'overlooking', 'say', 'sue', 'stout', 'text', 'is', 'us', 'me', 'he',
             'rent', 'cart', 'webcam', 'item', 'mari', 'ask', 'frown', 'cornier', 'marrying', 'starboard',
             'medication', 'newman', 'deuces', 'decurrent', 'persona'}


def fix_tok(t):
    m = CORE.match(t)
    pre, w, post = m.groups()
    if not w.isalpha() or len(w) < 3:
        return t
    lw = w.lower()
    if (lw in EN and EN[lw] >= 5) or corpus[lw] >= 4:
        return t
    if w.isupper() and len(w) <= 6:
        return t
    if lw in PROTECT:
        return t
    cands = sym.lookup(lw, Verbosity.ALL, max_edit_distance=2)
    best = None
    for c in cands:
        cost = ocr_cost(lw, c.term)
        sc = math.log10(1 + c.count) - 2.2 * cost
        if best is None or sc > best[0]:
            best = (sc, c.term, cost)
    if (not best or best[2] > 1.45 or (best[2] > 0.8 and len(lw) < 6)
            or (len(lw) <= 4 and best[2] > 0.35) or best[1] in BADTARGET):
        unknown[w] += 1
        return pre + w + post
    c = best[1]
    if w[0].isupper():
        c = c[0].upper() + c[1:]
    fixed[(w, c)] += 1
    return pre + c + post


def fix_text(s):
    return '\n'.join(' '.join(fix_tok(t) for t in TOK.findall(line)) for line in s.split('\n'))


for gp in pages:
    c2 = cols(f'{V2}/p{gp:03d}.txt')
    c3 = cols(f'{V3}/p{gp:03d}.txt')
    res = []
    for c in ('LEFT', 'RIGHT'):
        a = c2.get(c, '')
        b = c3.get(c, '')
        m = merge_col(a, b) if b else a
        res.append('=====' + c + '\n' + fix_text(m))
    open(f'{OUT}/p{gp:03d}.txt', 'w').write('\n'.join(res))

json.dump([[a, b, n] for (a, b), n in fixed.most_common()], open(SP + '/spellfix.json', 'w'), indent=0)
json.dump(unknown.most_common(), open(SP + '/unknown.json', 'w'), indent=0)
print('pages', len(pages), 'spell fixes', sum(fixed.values()), 'distinct', len(fixed), 'unknown', sum(unknown.values()))
