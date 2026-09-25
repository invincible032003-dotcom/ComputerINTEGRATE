"""Parse merged OCR (ocrm/) into raw per-chapter banks with fuzzy numbering."""
import re, json, os, sys, difflib
SP = os.environ.get('OCR_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work'))  # OCR scratch dir
SRC = SP + '/' + (sys.argv[1] if len(sys.argv) > 1 else 'ocrm')
os.makedirs(SP + '/raw', exist_ok=True)

CH = [
    (1, 'Computer Fundamentals', 11, 41, 42, 73),
    (2, 'Computer Architecture', 74, 104, 105, 137),
    (3, 'Computer Memory', 138, 167, 168, 194),
    (4, 'Number Systems & Binary Arithmetic', 195, 224, 225, 242),
    (5, 'Boolean Algebra & Logic Gates', 243, 252, 253, 260),
    (6, 'Introduction to Software', 261, 276, 277, 293),
    (7, 'Basic Concepts of Operating System', 294, 307, 308, 318),
    (8, 'Internet & its Services', 319, 335, 336, 345),
    (9, 'Database Concepts', 346, 368, 369, 385),
    (10, 'Flowchart & Algorithm', 386, 393, 394, 401),
    (11, 'Basics of C Programming', 402, 453, 454, 465),
]
WM = re.compile(r'(ww|EGU|GUE|EGE|\bGe\b|Sw ww|EOE|ESE)')
DIG = {'O': '0', 'o': '0', 'D': '0', 'Q': '0', 'C': '0', 'I': '1', 'l': '1', 'i': '1', '|': '1',
       '!': '1', 'L': '1', 'Z': '2', 'z': '2', 'S': '5', 's': '5', 'G': '6', 'b': '6', '&': '8',
       'B': '8', 'g': '9', 'q': '9', 'T': '7', 'A': '4', 'y': '4', '$': '8', '%': '9'}


def page_lines(gp):
    txt = open(f'{SRC}/p{gp:03d}.txt').read()
    parts = re.split(r'=====(TOP|LEFT|RIGHT)\n', txt)
    cols = {parts[k]: parts[k + 1] for k in range(1, len(parts), 2)}
    out = []
    for c in ('LEFT', 'RIGHT'):
        lines = [l.rstrip() for l in cols.get(c, '').split('\n') if l.strip()]
        while lines and WM.search(lines[0]) and not re.match(r'^\s*\d', lines[0]):
            lines.pop(0)
        while lines and len(lines[-1].strip()) <= 4 and not re.match(r'^\s*[a-dA-D][\)\}]', lines[-1]):
            lines.pop()
        for l in lines:
            if re.fullmatch(r'\s*View Answer\s*', l):
                continue
            out.append((gp, c, l))
    return out


NUMTOK = re.compile(r'^\s*[\'"‘’\*\-=«»]?\s*([0-9A-Za-z&|!$%]{1,4}?)\s*[.,:;]\s*(.*)$')


def fnum(tok):
    s = ''.join(DIG.get(ch, ch) for ch in tok)
    return int(s) if s.isdigit() else None


def opt_match(line, expect):
    m = re.match(r'^\s*[\(\[]?(\S{1,2}?)\s*[\)\}\]\\|>]\)?\s?(.*)$', line)
    if not m:
        m = re.match(r'^\s*([a-dA-D])[‘\'\.;:,]\s*(.*)$', line)
        if not m:
            m = re.match(r'^\s*(al|bi|hY|ci|di|dl|cl|bl|a1|b1|c1|d1)\s+(.*)$', line)
            if not m:
                return None
    tok, rest = m.group(1), m.group(2)
    t = tok.lower()
    L = 'abcd'[expect]
    if t == L:
        return rest
    conf = {'a': ['@', '«', 'o', 'e', 'q', 'u', 'ai', '4', 'al', 'a1', 'aj'],
            'b': ['9', '6', 'h', 'k', 'ki', 'fb', 'lb', '8', 'p', 'bi', 'hy', 'bl', 'b1', 'bj', 'n'],
            'c': ['<', '¢', '©', 'e', '(', 'o', 'cc', '¢}', 'g', 'ci', 'cl', 'c1', 'cj'],
            'd': ['a', 'cd', 'q', 'di', 'al', 'ad', 'o', 'ci', 'dl', 'd1', 'dj', 'c']}
    if t in conf[L]:
        return rest
    return None


def is_answer_line(rest):
    r = rest.strip().lower()
    head = r[:24]
    return (difflib.SequenceMatcher(None, head[:21], 'the correct answer is').ratio() > 0.72
            or re.match(r'^\S{1,4}\s+c\S{3,6}\s+a\S{3,7}', r) is not None)


def parse_questions(lines):
    qs, cur, expect, state = [], None, 1, None
    for gp, col, l in lines:
        m = NUMTOK.match(l)
        if m:
            n = fnum(m.group(1))
            rest = m.group(2)
            ok = False
            if n is not None and rest[:1] and not re.match(r'^[#{}]|^(int|return|printf|char|float|void|for|while|if|else|scanf|main)\b', rest):
                if n == expect:
                    ok = True
                elif m.group(1).isdigit() and expect < n <= expect + 3 and cur and len(cur['opts']) >= 2:
                    ok = True
            if ok:
                cur = {'n': n, 'page': gp, 'stem': [rest], 'opts': [], 'raw': [l]}
                qs.append(cur)
                expect = n + 1
                state = 'stem'
                continue
        if cur is None:
            continue
        cur['raw'].append(l)
        k = len(cur['opts'])
        if k < 4:
            r = opt_match(l, k)
            if r is not None and (k > 0 or len(' '.join(cur['stem'])) > 3):
                cur['opts'].append([r])
                state = k
                continue
        if state == 'stem':
            cur['stem'].append(l)
        else:
            cur['opts'][-1].append(l)
    return qs


def parse_answers(lines):
    ans, cur, expect = [], None, 1
    for gp, col, l in lines:
        m = NUMTOK.match(l)
        if m and is_answer_line(m.group(2)):
            cur = {'raw_n': fnum(m.group(1)), 'page': gp, 'text': [m.group(2)]}
            ans.append(cur)
            continue
        if cur is not None:
            cur['text'].append(l)
    # anchor-based numbering: trust an OCR number when a neighbour agrees
    raw = [a['raw_n'] for a in ans]
    trusted = []
    for i, p in enumerate(raw):
        if p is None:
            continue
        prev_ok = i > 0 and raw[i - 1] is not None and raw[i - 1] + 1 == p
        next_ok = i + 1 < len(raw) and raw[i + 1] is not None and raw[i + 1] - 1 == p
        if prev_ok or next_ok or (i == 0 and p == 1):
            trusted.append(i)
    # keep trusted anchors strictly increasing in a consistent way
    anchors = []
    for i in trusted:
        if anchors and not (raw[i] - raw[anchors[-1]] >= i - anchors[-1]):
            continue
        anchors.append(i)
    num = [None] * len(ans)
    for i in anchors:
        num[i] = raw[i]
    last_i, last_n = -1, 0
    for i in range(len(ans)):
        if num[i] is not None:
            last_i, last_n = i, num[i]
        else:
            num[i] = last_n + (i - last_i)
    for a, n in zip(ans, num):
        a['n'] = n
    return ans


def main():
    tot = 0
    for num, title, q0, q1, a0, a1 in CH:
        ql, al = [], []
        for gp in range(q0, q1 + 1):
            ql += page_lines(gp)
        for gp in range(a0, a1 + 1):
            al += page_lines(gp)
        qs = parse_questions(ql)
        ans = parse_answers(al)
        nums = [q['n'] for q in qs]
        mx = max(nums)
        missing = sorted(set(range(1, mx + 1)) - set(nums))
        anums = [a['n'] for a in ans]
        amissing = sorted(set(range(1, mx + 1)) - set(anums))
        badopts = [q['n'] for q in qs if len(q['opts']) not in (2, 4)]
        tot += mx
        print(f'Ch{num}: {len(qs)} q (max {mx}), missing {missing}; {len(ans)} ans, '
              f'missing {amissing}; badopts {len(badopts)} {badopts}')
        json.dump({'num': num, 'title': title, 'qs': qs, 'ans': ans},
                  open(f'{SP}/raw/ch{num:02d}.json', 'w'), indent=0)
    print('total', tot)


if __name__ == '__main__':
    main()
