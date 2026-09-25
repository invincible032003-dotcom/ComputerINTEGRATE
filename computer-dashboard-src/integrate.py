#!/usr/bin/env python3
"""Build the standalone dashboard with the Computer tab.

Inputs (all in computer-dashboard-src/):
  base/UPSC-ISS-Statistics-Dashboard-base.html  the dashboard as uploaded
  bank/chNN.txt      curated question bank, one file per book chapter
  sheets/chNN.txt    crisp pointers (UPSC ISS Paper-I) per chapter
  cs-tab.css / cs-tab.js   the tab's styles and screens
  mobile.css / mobile.js   Android-style phone shell (bottom nav, session bar, swipe, back button)

Output:
  ../UPSC-ISS-Statistics-Dashboard-STANDALONE.html

Every edit to the base file is an exact, asserted string replacement, so the
build fails loudly instead of silently if the base ever changes.

usage: python3 integrate.py [--provisional AUTO_DIR]
"""
import json, math, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.join(HERE, 'base', 'UPSC-ISS-Statistics-Dashboard-base.html')
OUT = os.path.join(os.path.dirname(HERE), 'UPSC-ISS-Statistics-Dashboard-STANDALONE.html')

SOURCE = 'the Sunrise Classes Computer MCQ book (Chapter-wise Practice Set, mainly dedicated to ISS)'
PAGES = 465
SET_MIN, SET_MAX = 40, 50
UNIT = 'Computer Application and Data Processing'
LET = 'abcd'

TOPIC_NAMES = {
    'C1': 'Computer Organisation: CPU, ALU, Control & Memory Units, I/O Units',
    'C2': 'Hardware: Input, Output & Peripheral Devices',
    'C3': 'Memory: RAM, ROM, Cache; Units of Memory & Storage Capacity',
    'C4': 'Number Systems & Binary Arithmetic',
    'C5': 'Software, Operating Systems, Packages & Utilities',
    'C6': 'Languages, Compiler, Assembler, Interpreter; Low & High Level',
    'C7': 'Networks: LAN, WAN, Internet, Intranet',
    'C8': 'Computer Security: Virus, Antivirus, Firewall, Spyware, Malware',
    'C9': 'Programming Basics: Algorithm, Flowchart, Control Structures, Arrays, Functions',
    'C10': 'Data, Information, Database & DBMS; Frontend/Backend',
}

# keyword rules for the PYQ syllabus topic of each question; the first rule
# whose code the chapter allows wins, else the chapter default
RULES = [
    ('C8', r'virus|worm\b|trojan|malware|spyware|firewall|phishing|anti-?virus|hack|ransomware|adware|'
           r'encrypt|decrypt|cyber|spam|password|authenticat|security|intrusion'),
    ('C10', r'database|dbms|\bsql\b|primary key|foreign key|relational|normali[sz]|tuple|schema|'
            r'\bquery|record|\bfield|entity|attribute'),
    ('C6', r'compiler|interpreter|assembler|linker|loader|high-level|low-level|machine language|'
           r'assembly language|source code|object code|translator|syntax error|bytecode'),
    ('C7', r'network|\blan\b|\bwan\b|\bman\b|internet|intranet|extranet|protocol|\btcp|\bip\b|ip address|'
           r'http|\bftp|smtp|\bdns|router|\bswitch|\bhub\b|modem|topology|bandwidth|e-?mail|\bweb|browser|'
           r'\burl|\bisp\b|\bosi\b|ethernet|wi-?fi|bluetooth|website|download|upload|search engine'),
    ('C9', r'algorithm|flowchart|flow chart|loop|array|function|variable|pseudo|recursion|sort|'
           r'\bstack|\bqueue|pointer|printf|scanf|operator|data type|\bint\b|\bchar\b|#include|'
           r'if-else|switch-case|while|structure|program'),
    ('C4', r'binary|octal|hexa|decimal|complement|\bbcd\b|ascii|ebcdic|unicode|number system|gray code|'
           r'excess-?3|floating|parity|boolean|logic gate|\band\b gate|\bor\b gate|nand|\bnor\b|xor|xnor|'
           r'truth table|de ?morgan|karnaugh|k-map|radix|base \d|\bbits?\b'),
    ('C3', r'memory|\bram\b|\brom\b|cache|register|eeprom|eprom|prom|dram|sram|kilobyte|megabyte|'
           r'gigabyte|terabyte|storage|hard disk|flash|\bbyte|disk|magnetic tape|optical|cd-?rom|dvd'),
    ('C2', r'input device|output device|keyboard|mouse|printer|monitor|scanner|\bocr\b|\bomr\b|micr|'
           r'plotter|joystick|light pen|touch ?screen|speaker|webcam|barcode|peripheral|display'),
    ('C5', r'operating system|\bos\b|software|utility|application|kernel|process|thread|schedul|'
           r'deadlock|paging|file system|boot|gui|multitask|multiprogram|time-?shar|spooling|driver|'
           r'windows|linux|unix|\bdos\b'),
    ('C1', r'cpu|\balu\b|control unit|processor|\bbus\b|motherboard|instruction|machine cycle|risc|cisc|'
           r'clock|generation'),
]


# ---------------------------------------------------------------- parsing
def parse_bank(path):
    meta = {'themes': {}}
    items = []
    cur = None
    field = None
    in_code = False
    for raw in open(path, encoding='utf-8').read().split('\n'):
        line = raw.rstrip('\n')
        if in_code:
            if line.strip() == '```':
                in_code = False
                continue
            cur['code'].append(line)
            continue
        s = line.strip()
        if not s:
            field = None
            continue
        if s.startswith('@') and cur is None:
            k, _, v = s[1:].partition(' ')
            if k == 'themes':
                n, _, t = v.partition(' ')
                meta['themes'][int(n)] = t.strip()
            else:
                meta[k] = v.strip()
            continue
        m = re.match(r'^#(\d+)\s+(?:p(\d+)(?:\s+a(\d+))?|(iss))\s*$', s)
        if m:
            cur = {'n': int(m.group(1)), 'qPage': int(m.group(2)) if m.group(2) else None,
                   'aPage': int(m.group(3)) if m.group(3) else None, 'booster': bool(m.group(4)),
                   'Q': '', 'code': [], 'stmts': [], 'ask': '', 'opts': [], 'K': '', 'B': '',
                   'X': '', 'S': '', 'N': '', 'T': '', 'C': '', 'R': ''}
            items.append(cur)
            field = None
            continue
        if cur is None:
            continue
        if s == '```':
            in_code = True
            continue
        m = re.match(r'^([a-d])\)\s?(.*)$', s)
        if m and field not in ('X', 'S', 'N'):
            cur['opts'].append(m.group(2).strip())
            field = 'opt'
            continue
        m = re.match(r'^([QKBXSNTCR]):\s?(.*)$', s)
        if m:
            field = m.group(1)
            cur[field] = m.group(2).strip()
            continue
        m = re.match(r'^-\s+(.*)$', s)
        if m and field in ('Q', 'stmt'):
            cur['stmts'].append(m.group(1).strip())
            field = 'stmt'
            continue
        m = re.match(r'^\?:\s?(.*)$', s)
        if m:
            cur['ask'] = m.group(1).strip()
            field = 'ask'
            continue
        # continuation of the previous field
        if field == 'opt':
            cur['opts'][-1] += ' ' + s
        elif field == 'stmt':
            cur['stmts'][-1] += ' ' + s
        elif field in ('Q', 'X', 'S', 'N', 'ask'):
            cur[field if field != 'ask' else 'ask'] += ' ' + s
        else:
            raise SystemExit(f'{path}: stray line in #{cur["n"]}: {s!r}')
    return meta, items


def parse_sheet(path):
    sections = []
    for line in open(path, encoding='utf-8').read().split('\n'):
        s = line.strip()
        if not s:
            continue
        if s.startswith('## '):
            t = s[3:].strip()
            pyq = t.startswith('PYQ:')
            sections.append({'title': t[4:].strip() if pyq else t, 'items': [], 'pyq': pyq})
        elif s.startswith('- '):
            sections[-1]['items'].append(s[2:].strip())
        elif sections and sections[-1]['items']:
            sections[-1]['items'][-1] += ' ' + s
    return sections


def qtype(it):
    if it['T']:
        return it['T']
    q = it['Q'].lower()
    opts = [o.lower() for o in it['opts']]
    if it['code']:
        return 'Code / output'
    if opts in (['true', 'false'], ['false', 'true']):
        return 'True / False'
    if it['stmts'] or 'consider the following' in q:
        return 'Statement-based'
    if sum(1 for o in opts if re.fullmatch(r'[\s\(\)0-9a-f.+\-×x^,/]*[0-9][\s\(\)0-9a-f.+\-×x^,/]*(\s*(bits?|bytes?|kb|mb|gb))?', o)) >= 3:
        return 'Numerical'
    return 'Conceptual'


def topic_code(it, allowed, default):
    text = ' '.join([it['Q']] + it['opts'] + ['\n'.join(it['code'])]).lower()
    if it['C']:
        return it['C']
    for code, rx in RULES:
        if code in allowed and re.search(rx, text):
            return code
    return default


def plan_sets(n):
    """Split n questions into k near-equal sets, keeping sizes in 40-50
    when possible and otherwise as close to that band as they can be."""
    best = None
    for k in range(1, max(2, n // 20) + 1):
        avg = n / k
        dev = 0 if SET_MIN <= avg <= SET_MAX else min(abs(avg - SET_MIN), abs(avg - SET_MAX))
        key = (dev, abs(avg - 45))
        if best is None or key < best[0]:
            best = (key, k)
    k = best[1]
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    return sizes


def build_bank(bank_dir, sheet_dir, provisional=None):
    chapters, data, sheets = [], [], []
    total_fix = 0
    files = sorted(f for f in os.listdir(bank_dir) if re.fullmatch(r'ch\d\d\.txt', f))
    for fn in files:
        meta, items = parse_bank(os.path.join(bank_dir, fn))
        num = int(meta['chapter'])
        allowed = meta.get('codes', 'C1').split()
        default = meta.get('default', allowed[0])
        items.sort(key=lambda x: x['n'])
        sizes = plan_sets(len(items))
        bad = [z for z in sizes if not SET_MIN <= z <= SET_MAX]
        if bad:
            raise SystemExit(f'{fn}: {len(items)} questions give sets {sizes}; every set must hold '
                             f'{SET_MIN}-{SET_MAX} questions (add ISS Booster items)')
        nb = 0
        sets = []
        pos = 0
        for k, sz in enumerate(sizes, 1):
            chunk = items[pos:pos + sz]
            pos += sz
            bk = [it for it in chunk if not it['booster']]
            sets.append({'k': k, 'n': sz, 'from': bk[0]['n'], 'to': bk[-1]['n'], 'boost': sz - len(bk),
                         'themes': meta['themes'].get(k, '')})
            for it in chunk:
                it['set'] = k
        for it in items:
            opts = it['opts']
            if len(opts) not in (2, 4):
                raise SystemExit(f'{fn} #{it["n"]}: {len(opts)} options')
            if it['K'] not in LET[:len(opts)]:
                raise SystemExit(f'{fn} #{it["n"]}: bad key {it["K"]!r}')
            for f in ('Q', 'X', 'S'):
                if not it[f] and not (f == 'Q' and it['code']):
                    raise SystemExit(f'{fn} #{it["n"]}: missing {f}')
            key = LET.index(it['K'])
            book = LET.index(it['B']) if it['B'] else key
            if book != key:
                total_fix += 1
            code = topic_code(it, allowed, default)
            if it['booster']:
                nb += 1
                if it['B'] or it['qPage']:
                    raise SystemExit(f'{fn} #{it["n"]}: a booster has no book key or page')
            elif not it['qPage']:
                raise SystemExit(f'{fn} #{it["n"]}: book item without page')
            data.append({
                'id': f'CS-{num:02d}.{it["n"]:03d}', 'globalId': 300000 + num * 1000 + it['n'],
                'isCS': True, 'provenance': 'COMPUTER BOOK BANK', 'year': 'Book',
                'questionNumber': it['n'], 'unit': UNIT, 'topicCode': code, 'topic': TOPIC_NAMES[code],
                'subtopic': f'Ch {num} · {meta["title"]}', 'form': 'PLAIN', 'sharedStem': '',
                'question': it['Q'], 'code': '\n'.join(it['code']), 'stmts': it['stmts'], 'ask': it['ask'],
                'options': opts, 'correctAnswer': key, 'bookKey': book,
                'questionType': qtype(it), 'answerConfidence': 'high', 'sourceIssue': '',
                'explanation': it['X'], 'examShortcut': it['S'], 'keyNote': it['N'],
                'tipsTricks': [], 'solution': [],
                'csChapter': num, 'csNum': it['n'], 'csSet': it['set'],
                'qPage': it['qPage'], 'aPage': it['aPage'],
                'isBooster': it['booster'], 'pyqRef': it['R'],
                'csLabel': ('Booster ' + str(nb)) if it['booster'] else ('Q' + str(it['n'])),
            })
        qp, ap = meta.get('pages', '').split() if meta.get('pages') else ('', '')
        chapters.append({'num': num, 'title': meta['title'], 'n': len(items), 'nBook': len(items) - nb,
                         'nBoost': nb, 'sets': sets,
                         'relCodes': allowed, 'qPages': qp, 'aPages': ap})
        sp = os.path.join(sheet_dir, fn)
        if os.path.exists(sp):
            sheets.append({'ch': num, 'sections': parse_sheet(sp)})
    chapters.sort(key=lambda c: c['num'])
    meta = {
        'label': 'COMPUTER BOOK BANK', 'source': SOURCE, 'pages': PAGES,
        'setMin': SET_MIN, 'setMax': SET_MAX,
        'total': len(data), 'nBoost': sum(1 for q in data if q['isBooster']), 'nSets': sum(len(c['sets']) for c in chapters), 'nKeyFixes': total_fix,
        'provenance': (
            'Every book question, option and answer key here comes from ' + SOURCE + ', read from the '
            '465 scanned pages, retyped as text and proof-read (code as code blocks, figures redrawn). '
            'The explanations and exam shortcuts were written fresh for this dashboard. Where the printed '
            'key is wrong, the correct answer is used and an answer-key note says what the book prints and '
            'why it is wrong (' + str(total_fix) + ' such corrections). Where a chapter\'s total cannot fill '
            'sets of 40-50, original ISS Booster questions, modelled on ISS Paper-I PYQs and marked as not '
            'from the book, complete the last set. None of these is a UPSC previous-year question and none '
            'enters a year, sectional, topic, subtopic or custom PYQ mock.'),
        'chapters': chapters, 'sheets': sheets,
    }
    return meta, data


# ----------------------------------------------------------------- inject
def sub1(s, old, new, what):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'anchor for {what!r} found {n} times')
    return s.replace(old, new)


def js_safe(obj):
    t = json.dumps(obj, ensure_ascii=False, separators=(',', ':'))
    return t.replace('</', '<\\/').replace('\u2028', '\\u2028').replace('\u2029', '\\u2029')


def integrate(meta, data):
    s = open(BASE, encoding='utf-8').read()
    css = open(os.path.join(HERE, 'cs-tab.css'), encoding='utf-8').read()
    css += open(os.path.join(HERE, 'mobile.css'), encoding='utf-8').read()
    js = open(os.path.join(HERE, 'cs-tab.js'), encoding='utf-8').read()
    js += '\n' + open(os.path.join(HERE, 'mobile.js'), encoding='utf-8').read()

    # styles
    s = sub1(s, '/* GK-CSS-END */\n', '/* GK-CSS-END */\n/* CS-CSS-BEGIN */\n' + css + '/* CS-CSS-END */\n', 'css')

    # Android: tint the browser toolbar to match the top app bar
    s = sub1(s, '<meta name="color-scheme" content="light dark">\n',
             '<meta name="color-scheme" content="light dark">\n'
             '<meta name="theme-color" content="#17457a" media="(prefers-color-scheme: light)">\n'
             '<meta name="theme-color" content="#15263c" media="(prefers-color-scheme: dark)">\n'
             '<meta name="mobile-web-app-capable" content="yes">\n', 'theme-color')

    # data, right after the Gupta & Kapoor bank
    i = s.index('<script id="gk-data">')
    j = s.index('</script>', i) + len('</script>')
    blob = ('\n<script id="cs-data">\n/* Computer book bank - generated by computer-dashboard-src/integrate.py\n'
            ' * from bank/ch*.txt and sheets/ch*.txt; do not edit by hand. */\n'
            'window.csMeta = ' + js_safe(meta) + ';\nwindow.csData = [\n' +
            ',\n'.join(js_safe(q) for q in data) + '\n];\n</script>')
    s = s[:j] + blob + s[j:]

    # top bar
    s = sub1(s, '<small>2018–2026 PYQ · 2027 Forecast Bank · Gupta Kapoor Ch 5–8 · 100% offline</small>',
             '<small>2018–2026 PYQ · 2027 Forecast Bank · Gupta Kapoor Ch 5–8 · Computer book · 100% offline</small>',
             'brand')
    s = sub1(s, '    <button type="button" data-act="go" data-r="gk" title="Gupta Kapoor Ch 5–8 problem bank">Gupta Kapoor</button>\n',
             '    <button type="button" data-act="go" data-r="cs" title="Computer — chapter-wise practice sets">Computer</button>\n'
             '    <button type="button" data-act="go" data-r="gk" title="Gupta Kapoor Ch 5–8 problem bank">'
             '<span class="tb-l">Gupta Kapoor</span><span class="tb-s">G&amp;K</span></button>\n',
             'topbar button')

    # data wiring
    s = sub1(s, 'var GMETA = window.gkMeta || null;\nvar ALL = DATA.concat(FDATA, GDATA);',
             'var GMETA = window.gkMeta || null;\n'
             'var CDATA = window.csData || [];          /* COMPUTER book bank (chapter-wise sets) */\n'
             'var CMETA = window.csMeta || null;\n'
             'var ALL = DATA.concat(FDATA, GDATA, CDATA);', 'ALL')
    s = sub1(s, "  return (q.id + ' ' + (q.isForecast ? 'forecast 2027' : q.isGK ? 'gupta kapoor chapter ' +",
             "  return (q.id + ' ' + (q.isCS ? 'computer book chapter ' + q.csChapter + ' ' + q.subtopic + ' set ' +\n"
             "          q.csSet + ' ' + q.questionType + ' ' + (q.code || '') : q.isForecast ? 'forecast 2027' : q.isGK ? 'gupta kapoor chapter ' +",
             'search index')

    # learning-mode prompt: Computer items reveal explanation then shortcut
    s = sub1(s, "    h += '<div class=\"banner mt\">Choose an option to reveal the verdict, the exam shortcut, ' +\n      'the tips and the full solution.</div>';",
             "    h += '<div class=\"banner mt\">' + (q.isCS ? 'Choose an option to reveal the verdict, the explanation and ' +\n"
             "      'the 15-second exam shortcut.' : 'Choose an option to reveal the verdict, the exam shortcut, ' +\n"
             "      'the tips and the full solution.') + '</div>';", 'learn prompt')

    # badges, meta line, reveal, options, body
    s = sub1(s, "  if (q.isGK) return '<span class=\"gk-badge\">GUPTA KAPOOR &middot; Ch ' + q.gkChapter + ' &middot; not PYQ</span>';",
             "  if (q.isCS) return '<span class=\"cs-badge' + (q.isBooster ? ' boost\">ISS BOOSTER' : '\">COMPUTER BOOK') + ' &middot; Ch ' + q.csChapter + ' &middot; Set ' + q.csSet + ' &middot; not PYQ</span>';\n"
             "  if (q.isGK) return '<span class=\"gk-badge\">GUPTA KAPOOR &middot; Ch ' + q.gkChapter + ' &middot; not PYQ</span>';",
             'badge')
    s = sub1(s, "    (q.isGK ? '<span>' + E(q.gkTopicLabel) + '</span><span>\\u00a7' + E(q.gkSection) + '</span>' : '') + '</div>';",
             "    (q.isGK ? '<span>' + E(q.gkTopicLabel) + '</span><span>\\u00a7' + E(q.gkSection) + '</span>' : '') +\n"
             "    (q.isCS ? '<span>' + (q.isBooster ? q.csLabel + ' \\u00b7 added, not in the book' : 'Book ' + q.csLabel + ' \\u00b7 PDF p. ' + q.qPage) + '</span>' : '') + '</div>';",
             'meta line')
    s = sub1(s, '  if (q.isGK) return gkRevealPanes(q, chosenOriginal, opts);',
             '  if (q.isCS) return csRevealPanes(q, chosenOriginal, opts);\n'
             '  if (q.isGK) return gkRevealPanes(q, chosenOriginal, opts);', 'reveal')
    s = sub1(s, "         '<span class=\"k\">' + LET[d] + '</span><span class=\"v\">' + R(q.options[orig]) + '</span>' +",
             "         '<span class=\"k\">' + LET[d] + '</span><span class=\"v\">' +\n"
             "         (q.isCS ? csR(q.options[orig]) : R(q.options[orig])) + '</span>' +", 'option text')
    s = sub1(s, 'function qBody(q) {\n  var h = R(q.question);',
             'function qBody(q) {\n  if (q.isCS) return csBody(q);\n  var h = R(q.question);', 'qBody')

    # sessions: 2-option items, key guard, live learning progress, persistence
    s = sub1(s, '    var order = [0, 1, 2, 3];\n',
             '    var order = (q.options && q.options.length && q.options.length !== 4)\n'
             '      ? q.options.map(function (x, i) { return i; }) : [0, 1, 2, 3];\n', 'order')
    s = sub1(s, 'function chooseOption(displayIdx) {\n  if (!S || S.finished) return;\n',
             'function chooseOption(displayIdx) {\n  if (!S || S.finished) return;\n'
             '  if (displayIdx < 0 || displayIdx >= S.items[S.cur].order.length) return;\n', 'choose guard')
    s = sub1(s, '  if (S.mode === \'learn\' && S.answers[S.cur] !== null) S.revealed[S.cur] = true;\n',
             '  if (S.mode === \'learn\' && S.answers[S.cur] !== null) S.revealed[S.cur] = true;\n'
             '  if (S.kind === \'cs\' && S.mode === \'learn\' && S.answers[S.cur] !== null) {\n'
             '    csMarkQ(curQ().id, chosenOriginal(S.cur) === curQ().correctAnswer);\n  }\n', 'learn mark')
    s = sub1(s, '  if (d.history.length > 60) d.history.length = 60;\n',
             '  if (d.history.length > 60) d.history.length = 60;\n  if (sess.kind === \'cs\') csRecord(sess);\n',
             'persist')

    # screens
    s = sub1(s, '  h += gkHomeSection();\n', '  h += csHomeSection();\n  h += gkHomeSection();\n', 'home')
    s = sub1(s, "  if (S.kind === 'gk') h += breakdownCard(r.perQ, 'gkTopicLabel', 'Performance by Gupta Kapoor subtopic');",
             "  if (S.kind === 'gk') h += breakdownCard(r.perQ, 'gkTopicLabel', 'Performance by Gupta Kapoor subtopic');\n"
             "  if (S.kind === 'cs') h += breakdownCard(r.perQ, 'subtopic', 'Performance by chapter');", 'result')
    s = sub1(s, "field === 'gkTopicLabel' ? 'Subtopic' : 'Type'",
             "field === 'gkTopicLabel' ? 'Subtopic' : field === 'subtopic' ? 'Chapter' : 'Type'", 'breakdown label')
    s = sub1(s, "    '<button type=\"button\" class=\"btn\" data-act=\"retakeSame\">Retake this mock</button>' +",
             "    '<button type=\"button\" class=\"btn\" data-act=\"retakeSame\">Retake this mock</button>' +\n"
             "    (S.kind === 'cs' ? '<button type=\"button\" class=\"btn\" data-act=\"go\" data-r=\"cs\">Back to Computer</button>' : '') +",
             'result back')
    s = sub1(s, '  h += optionList(q, [0, 1, 2, 3], null, { showAnswer: true, disabled: true });',
             '  h += optionList(q, (q.options && q.options.length) ? q.options.map(function (x, i) { return i; }) : [0, 1, 2, 3],\n'
             '    null, { showAnswer: true, disabled: true });', 'study options')
    s = sub1(s, "  if (q.isGK) h += '<div class=\"tiny muted mb\">Source: ' + gkSourceLine(q) + '.</div>';",
             "  if (q.isCS) h += '<div class=\"tiny muted mb\">Source: ' + csSourceLine(q) + '.</div>';\n"
             "  else if (q.isGK) h += '<div class=\"tiny muted mb\">Source: ' + gkSourceLine(q) + '.</div>';", 'study source')

    # search
    s = sub1(s, "    (GMETA ? ', the ' + GMETA.total + ' Gupta Kapoor textbook problems' : '') +",
             "    (GMETA ? ', the ' + GMETA.total + ' Gupta Kapoor textbook problems' : '') +\n"
             "    (CMETA ? ', the ' + CMETA.total + ' Computer book questions' : '') +", 'search sub')
    s = sub1(s, "      '<option value=\"\"' + (SEARCH.bank ? '' : ' selected') + '>Both banks</option>' +",
             "      '<option value=\"\"' + (SEARCH.bank ? '' : ' selected') + '>All banks</option>' +", 'search all')
    s = sub1(s, "        '>Gupta Kapoor (Ch 5\\u20138) only</option>' : '') + '</select></label>';",
             "        '>Gupta Kapoor (Ch 5\\u20138) only</option>' : '') +\n"
             "      (CMETA ? '<option value=\"cs\"' + (SEARCH.bank === 'cs' ? ' selected' : '') +\n"
             "        '>Computer book only</option>' : '') + '</select></label>';", 'search option')
    s = sub1(s, "    if (SEARCH.bank === 'pyq' && (q.isForecast || q.isGK)) continue;",
             "    if (SEARCH.bank === 'pyq' && (q.isForecast || q.isGK || q.isCS)) continue;\n"
             "    if (SEARCH.bank === 'cs' && !q.isCS) continue;", 'search filter')
    s = sub1(s, "      (q.isGK ? '<span class=\"gk-badge\">GUPTA KAPOOR</span>' : '') +",
             "      (q.isGK ? '<span class=\"gk-badge\">GUPTA KAPOOR</span>' : '') +\n"
             "      (q.isCS ? '<span class=\"cs-badge\">COMPUTER BOOK</span>' : '') +", 'search badge')

    # audit
    s = sub1(s, "  var flagged = DATA.filter(function (q) { return q.sourceIssue; });",
             "  if (CMETA) {\n"
             "    h += '<div class=\"card\"><h3>Computer book bank</h3><p class=\"small\">' + CS_AUDIT.total +\n"
             "      ' questions in ' + CMETA.nSets + ' sets across ' + CMETA.chapters.length + ' chapters, kept apart from the PYQs above \\u00b7 ' +\n"
             "      CMETA.nKeyFixes + ' printed answer keys corrected \\u00b7 ' + (CS_AUDIT.ok ? 'all structural checks passed'\n"
             "      : CS_AUDIT.errors.length + ' error(s)') + '.</p>' + (CS_AUDIT.errors.length ? '<ul class=\"small\">' +\n"
             "      CS_AUDIT.errors.slice(0, 50).map(function (e) { return '<li>' + E(e) + '</li>'; }).join('') + '</ul>' : '') +\n"
             "      '</div>';\n  }\n\n"
             "  var flagged = DATA.filter(function (q) { return q.sourceIssue; });", 'audit')

    # events, tab code, boot hook
    s = sub1(s, '  if (gkClick(act, t)) return;\n', '  if (gkClick(act, t)) return;\n  if (csClick(act, t)) return;\n', 'click')
    s = sub1(s, '/* GK-JS-END */\n', '/* GK-JS-END */\n' + js, 'js')
    s = sub1(s, '    gk: { total: GDATA.length, audit: GK_AUDIT },\n',
             '    gk: { total: GDATA.length, audit: GK_AUDIT },\n    cs: { total: CDATA.length, audit: CS_AUDIT },\n', 'ISSApp')

    # export / import / reset carry the Computer progress too
    s = sub1(s, "    datasetVersion: META.datasetVersion,\n    data: d\n",
             "    datasetVersion: META.datasetVersion,\n    data: d,\n    cs: CsStore.d()\n", 'export')
    s = sub1(s, "  d.seq = payload.seq || 0;\n  Store.save();\n",
             "  d.seq = payload.seq || 0;\n  Store.save();\n  if (obj && obj.cs) CsStore.replace(obj.cs);\n", 'import')
    s = sub1(s, "        Store.reset('all'); Store.save(); go('home');",
             "        Store.reset('all'); Store.save(); CsStore.reset(); go('home');", 'reset')
    return s


def main():
    bank = os.environ.get('CS_BANK_DIR', os.path.join(HERE, 'bank'))
    sheets = os.environ.get('CS_SHEET_DIR', os.path.join(HERE, 'sheets'))
    out = os.environ.get('CS_OUT', OUT)
    meta, data = build_bank(bank, sheets)
    html = integrate(meta, data)
    open(out, 'w', encoding='utf-8').write(html)
    print(f'{len(data)} questions, {meta["nSets"]} sets, {len(meta["chapters"])} chapters, '
          f'{len(meta["sheets"])} sheets, {meta["nKeyFixes"]} key fixes -> {out} '
          f'({os.path.getsize(out) / 1e6:.2f} MB)')
    for c in meta['chapters']:
        print(f'  Ch{c["num"]:>2} {c["title"]:<40} {c["n"]:>4} q  sets {[x["n"] for x in c["sets"]]}')


if __name__ == '__main__':
    main()
