"""Build the auto-cleaned bank from raw/chNN.json and dump review text.

usage: python3 auto.py CH FROM TO   -> prints review text for that range
       python3 auto.py build        -> writes auto/chNN.json for every chapter
"""
import re, json, sys, os, difflib
from spellchecker import SpellChecker

SP = '/tmp/claude-0/-home-user-ComputerINTEGRATE/746bcd46-4034-5506-ab6a-1cf4e2b6e837/scratchpad'
os.makedirs(SP + '/auto', exist_ok=True)
EN = SpellChecker().word_frequency
corpus = {}
for fn in os.listdir(SP + '/ocrm'):
    for t in re.findall(r'[A-Za-z]+', open(SP + '/ocrm/' + fn).read()):
        corpus[t.lower()] = corpus.get(t.lower(), 0) + 1


def valid(w):
    lw = w.lower()
    return (lw in EN and EN[lw] >= 5) or corpus.get(lw, 0) >= 4


def join(lines):
    out = ''
    for l in lines:
        l = l.strip()
        if not l:
            continue
        if not out:
            out = l
            continue
        if out.endswith('-') and l[:1].islower():
            a = re.search(r'([A-Za-z]+)-$', out)
            b = re.match(r'([A-Za-z]+)', l)
            if a and b and valid(a.group(1) + b.group(1)) and not (valid(a.group(1)) and valid(b.group(1)) and len(a.group(1)) > 3):
                out = out[:-1] + l
                continue
            out = out + l
            continue
        out += ' ' + l
    out = re.sub(r'\s+([,.;:?!])', r'\1', out)
    out = re.sub(r'\s{2,}', ' ', out)
    return out.strip()


def flag(s):
    def f(m):
        w = m.group(0)
        if len(w) < 3 or valid(w) or w.isupper():
            return w
        return '⟦' + w + '⟧'
    return re.sub(r'[A-Za-z]+', f, s)


LET = 'abcd'
XMAX = int(os.environ.get('XMAX', '170'))


def split_answer(text, opts):
    """Answer text = '<letter>) <option text> <explanation>' -> (letter_idx, explanation)."""
    t = join(text)
    t = re.sub(r'^\W*\S{1,4}\s+\S{3,9}\s+\S{3,8}\s+(?:is|1s|Is|ts|js|iz|i5)?\s*:?\s*(?:option\s*)?', '', t, count=1)
    m = re.match(r'^\(?\s*([a-dA-D@«<¢©9])\s*[\)\}\]\|]?\s*[\)\}\]]?\s*(.*)$', t)
    letter, rest = None, t
    if m:
        c = m.group(1).lower()
        letter = {'@': 'a', '«': 'a', '<': 'c', '¢': 'c', '©': 'c', '9': 'b'}.get(c, c)
        rest = m.group(2)
    # strip the option text from the start of rest
    best = (0, None, 0)
    for i, o in enumerate(opts):
        o = o.strip().rstrip('.')
        if not o:
            continue
        head = rest[:len(o) + 2]
        r = difflib.SequenceMatcher(None, head[:len(o)].lower(), o.lower()).ratio()
        if r > best[0]:
            best = (r, i, len(o))
    idx = LET.index(letter) if letter and letter in LET else None
    exp = rest
    if best[1] is not None and best[0] >= 0.75:
        exp = rest[best[2]:].lstrip(' .:;,-)')
        if idx is None:
            idx = best[1]
    return idx, exp, (best[1] if best[0] >= 0.75 else None), rest


INL = re.compile(r'\s[\(\[]?([<«@(]|[a-d]|[1tl]|cl|al)[\)\}\]]\)?\s')


def split_inline(opts):
    out = []
    for o in opts:
        parts = [o]
        while len(out) + len(parts) < 4:
            m = INL.search(parts[-1])
            if not m:
                break
            parts[-1:] = [parts[-1][:m.start()].strip(), parts[-1][m.end():].strip()]
        out.extend(parts)
    return out


def build(ch):
    d = json.load(open(f'{SP}/raw/ch{ch:02d}.json'))
    ans = {}
    for a in d['ans']:
        ans.setdefault(a['n'], a)
    items = []
    for q in d['qs']:
        stem = join(q['stem'])
        opts = [join(o) for o in q['opts']]
        if len(opts) < 4:
            opts = split_inline(opts)
        a = ans.get(q['n'])
        key = exp = match = rest = None
        apage = None
        if a:
            key, exp, match, rest = split_answer(a['text'], opts)
            apage = a['page']
        items.append({'n': q['n'], 'page': q['page'], 'q': stem, 'o': opts, 'key': key,
                      'match': match, 'x': exp, 'apage': apage, 'araw': rest})
    have = {it['n'] for it in items}
    for n, a in ans.items():
        if n not in have:
            items.append({'n': n, 'page': None, 'q': None, 'o': [], 'key': None, 'match': None,
                          'x': join(a['text']), 'apage': a['page'], 'araw': join(a['text'])})
    items.sort(key=lambda x: x['n'])
    json.dump({'num': d['num'], 'title': d['title'], 'items': items},
              open(f'{SP}/auto/ch{ch:02d}.json', 'w'), indent=0, ensure_ascii=False)
    return items


def review(ch, lo, hi):
    items = build(ch)
    got = {it['n'] for it in items}
    for n in range(lo, hi + 1):
        if n not in got:
            print(f'#{n} !!! MISSING ENTIRELY')
            continue
    for it in items:
        if not (lo <= it['n'] <= hi):
            continue
        k = LET[it['key']] if it['key'] is not None else '?'
        warn = []
        if it['q'] is None:
            warn.append('Q-MISSING')
        if len(it['o']) not in (2, 4):
            warn.append(f'{len(it["o"])}opts')
        if it['key'] is None:
            warn.append('NOKEY')
        elif it['match'] is not None and it['match'] != it['key']:
            warn.append(f'KEYMATCH={LET[it["match"]]}')
        print(f'#{it["n"]} p{it["page"]}/{it["apage"]} {" ".join(warn)}')
        print('Q: ' + flag(it['q'] or ''))
        for i, o in enumerate(it['o']):
            print(f' {LET[i] if i < 4 else i}) ' + flag(o))
        x = it['x'] or ''
        print(f'K: {k}  X: ' + flag(x[:XMAX]) + ('…' if len(x) > XMAX else ''))


if __name__ == '__main__':
    if sys.argv[1] == 'build':
        for c in range(1, 12):
            build(c)
    else:
        review(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
