"""Generate chapter-4 bank blocks Q101-Q290 with computed, verified keys."""
from fractions import Fraction as F
L = 'abcd'
BN = {2: 'binary', 8: 'octal', 10: 'decimal', 16: 'hexadecimal'}
SUB = {2: '₂', 8: '₈', 10: '₁₀', 16: '₁₆'}
DIG = '0123456789ABCDEF'


def val(s, b):
    """value of a numeral string (may contain a point) in base b, as Fraction"""
    if '.' in s:
        i, f = s.split('.')
    else:
        i, f = s, ''
    v = F(0)
    for ch in i:
        v = v * b + DIG.index(ch.upper())
    for k, ch in enumerate(f, 1):
        v += F(DIG.index(ch.upper()), b ** k)
    return v


def to_int(n, b):
    if n == 0:
        return '0'
    s = ''
    while n:
        s = DIG[n % b] + s
        n //= b
    return s


def to_frac(x, b, maxd=12):
    s = ''
    x = F(x)
    k = 0
    while x and k < maxd:
        x *= b
        d = int(x)
        s += DIG[d]
        x -= d
        k += 1
    return '0.' + (s or '0')


def same(a, b, base):
    try:
        return val(a, base) == val(b, base)
    except ValueError:
        return False


def fmt_num(x):
    x = F(x)
    if x.denominator == 1:
        return str(x.numerator)
    s = f'{float(x):.10f}'.rstrip('0')
    return s


def place_sum(s, b):
    i = s.split('.')[0]
    parts = []
    n = len(i)
    for k, ch in enumerate(i):
        d = DIG.index(ch.upper())
        if d == 0:
            continue
        p = b ** (n - 1 - k)
        parts.append(f'{p}' if (b == 2 and d == 1) else f'{d}\\times{p}')
    return ' + '.join(parts) if parts else '0'


out = []


def emit(n, qp, ap, q, opts, key, book, X, S, N=''):
    out.append(f'#{n} p{qp}' + (f' a{ap}' if ap else ''))
    out.append('Q: ' + q)
    for i, o in enumerate(opts):
        out.append(f'{L[i]}) {o}')
    out.append('K: ' + key)
    if book and book != key:
        out.append('B: ' + book)
    out.append('X: ' + X)
    out.append('S: ' + S)
    if N:
        out.append('N: ' + N)
    elif book and book != key:
        out.append(f'N: The book prints ({book}) {opts[L.index(book)]}; the correct value is {opts[L.index(key)]}, so the key is ({key}).')
    elif not book:
        out.append('N: The book prints no answer for this question; the key was supplied.')
    out.append('')


def item(n, qp, ap, q, opts, correct, base_out, book, X, S, fix=None, N=None):
    """correct: string numeral in base base_out (or plain text).  fix=(idx, new)
    replaces a printed option that is wrong/unusable."""
    opts = list(opts)
    note = N
    if fix:
        fi, new = fix
        old = opts[fi]
        opts[fi] = new
        if note is None:
            if book:
                note = (f'The book keys ({book}) {old if fi == L.index(book) else opts[L.index(book)]}, and none of its printed options '
                        f'equals the correct value {new}. Option ({L[fi]}) has been changed from {old} to {new}.')
            else:
                note = f'None of the printed options equals the correct value {new}; option ({L[fi]}) has been changed from {old} to {new}.'
    hits = [i for i, o in enumerate(opts) if (same(o, correct, base_out) if base_out else o == correct)]
    if len(hits) != 1:
        raise SystemExit(f'Q{n}: correct {correct} matches {hits} in {opts}')
    k = L[hits[0]]
    if fix and book and book != k and N is None:
        note += f' The book\'s printed key ({book}) is also wrong; the key is ({k}).'
    emit(n, qp, ap, q, opts, k, book, X, S, note or '')


# ---------------------------------------------------------- Q101-110 bin->dec
B2D = [
 (101, 205, 232, '1010', ['5', '8', '10', '13'], 'c', 'What is the decimal value of the binary number 1010?'),
 (102, 205, 233, '11011', ['13', '19', '22', '27'], 'b', 'What is the decimal representation of the binary number 11011?'),
 (103, 205, 233, '111', ['3', '5', '7', '9'], 'c', 'What is the decimal value of the binary number 111?'),
 (104, 205, 233, '1111', ['8', '10', '14', '15'], 'd', 'Which decimal number is represented by the binary number 1111?'),
 (105, 205, 233, '10110', ['18', '22', '26', '30'], 'b', 'What is the decimal representation of the binary number 10110?'),
 (106, 205, 233, '110001', ['17', '33', '49', '57'], 'd', 'What is the decimal value of the binary number 110001?'),
 (107, 205, 233, '100111', ['23', '39', '47', '55'], 'b', 'What is the decimal representation of the binary number 100111?'),
 (108, 205, 233, '101010', ['32', '40', '42', '52'], 'c', 'Which decimal number is represented by the binary number 101010?'),
 (109, 205, 233, '1100101', ['85', '97', '101', '117'], 'b', 'What is the decimal value of the binary number 1100101?'),
 (110, 206, 233, '111101', ['45', '57', '61', '62'], 'c', 'What is the decimal representation of the binary number 111101?'),
]
for n, qp, ap, s, opts, book, q in B2D:
    v = val(s, 2)
    item(n, qp, ap, q, opts, str(v), 10, book,
         f'${s}_2 = {place_sum(s, 2)} = {v}$.',
         'Binary → decimal: add the place values (1, 2, 4, 8, 16, 32, 64 …) of the 1-bits.')

# ---------------------------------------------------------- Q111-120 dec->oct
D2O = [
 (111, 206, 233, 10, ['8', '10', '12', '16'], 'a', 'What is the octal equivalent of the decimal number 10?', None),
 (112, 206, 233, 25, ['20', '23', '25', '31'], 'b', 'What is the octal representation of the decimal number 25?', None),
 (113, 206, 233, 7, ['4', '5', '6', '7'], 'd', 'What is the octal equivalent of the decimal number 7?', None),
 (114, 206, 233, 15, ['14', '15', '17', '20'], 'b', 'Which octal number represents the decimal number 15?', None),
 (115, 206, 234, 42, ['42', '50', '52', '64'], 'c', 'What is the octal representation of the decimal number 42?', None),
 (116, 206, 234, 56, ['66', '70', '76', '100'], 'c', 'What is the octal equivalent of the decimal number 56?', None),
 (117, 206, 234, 63, ['63', '77', '100', '117'], 'b', 'What is the octal representation of the decimal number 63?', None),
 (118, 206, 234, 82, ['82', '100', '122', '122'], 'c', 'What is the octal equivalent of the decimal number 82?', (3, '132')),
 (119, 206, 234, 97, ['111', '125', '140', '157'], 'd', 'Which octal number represents the decimal number 97?', (2, '141')),
 (120, 207, 234, 120, ['120', '130', '160', '174'], 'c', 'What is the octal representation of the decimal number 120?', (2, '170')),
]
for n, qp, ap, v, opts, book, q, fix in D2O:
    s = to_int(v, 8)
    steps = []
    x = v
    while x:
        steps.append(f'{x} ÷ 8 = {x // 8} r {x % 8}')
        x //= 8
    N = None
    if n == 118:
        N = 'The book prints "122" as both option (c) and option (d); option (d) has been replaced by 132 so that only one option is correct.'
    if n == 119:
        N = ('The book prints (d) 157 (= 111). Option (c) is partly hidden under the watermark and reads like 140; it has been set to 141, '
             'the correct value (97 = 141₈), and the key is (c).')
    item(n, qp, ap, q, opts, s, 8, book,
         f'Divide repeatedly by 8 and read the remainders upward: {"; ".join(steps)} → ${v} = {s}_8$.',
         'Decimal → octal: repeated ÷8, remainders bottom-up.', fix=fix, N=N)

# ---------------------------------------------------------- Q121-130 oct->bin
O2B = [
 (121, 207, 234, '12', ['100', '101', '110', '111'], 'c', 'What is the binary equivalent of the octal number 12?', (0, '1010')),
 (122, 207, 234, '34', ['10010', '10100', '11010', '11100'], 'b', 'What is the binary representation of the octal number 34?', None),
 (123, 207, 234, '56', ['10110', '11010', '11100', '11110'], 'c', 'What is the binary equivalent of the octal number 56?', (0, '101110')),
 (124, 207, 234, '77', ['111101', '100101', '110101', '111001'], 'a', 'Which binary number represents the octal number 77?', (0, '111111')),
 (125, 207, 235, '123', ['1010111', '1100111', '1110111', '1111111'], 'd', 'What is the binary representation of the octal number 123?', (0, '1010011')),
 (126, 207, 235, '232', ['10011010', '10101010', '11001010', '11101010'], 'c', 'What is the binary equivalent of the octal number 232?', None),
 (127, 207, 235, '456', ['100110110', '101110110', '110110110', '111110110'], 'a', 'What is the binary representation of the octal number 456?', (0, '100101110')),
 (128, 207, 235, '777', ['11111111', '11110101', '11011011', '10101010'], 'a', 'Which binary number represents the octal number 777?', (0, '111111111')),
 (129, 207, 235, '625', ['110010101', '100100101', '101010101', '110110101'], 'a', 'What is the binary equivalent of the octal number 625?', None),
 (130, 208, 235, '347', ['11010111', '11101011', '11110111', '11111011'], 'a', 'What is the binary representation of the octal number 347?', (0, '11100111')),
]
for n, qp, ap, s, opts, book, q, fix in O2B:
    groups = ' | '.join(format(DIG.index(c), '03b') for c in s)
    b = to_int(int(val(s, 8)), 2)
    item(n, qp, ap, q, opts, b, 2, book,
         f'Replace each octal digit by its 3-bit group: {" ".join(s)} → {groups}, so ${s}_8 = {b}_2$ (leading zeros dropped).',
         'Octal → binary: each digit becomes 3 bits (0=000 … 7=111).', fix=fix)

# ---------------------------------------------------------- Q131-140 hex->dec
H2D = [
 (131, 208, 235, '1A', ['16', '18', '26', '32'], 'b', 'What is the decimal equivalent of the hexadecimal number 1A?'),
 (132, 208, 235, '2F', ['37', '45', '47', '57'], 'a', 'What is the decimal representation of the hexadecimal number 2F?'),
 (133, 208, 235, '5C', ['86', '92', '98', '108'], 'a', 'What is the decimal equivalent of the hexadecimal number 5C?'),
 (134, 208, 235, '7D', ['113', '125', '141', '157'], 'b', 'Which decimal number represents the hexadecimal number 7D?'),
 (135, 208, 235, 'A3', ['155', '163', '173', '183'], 'b', 'What is the decimal representation of the hexadecimal number A3?'),
 (136, 208, 236, 'F0', ['225', '240', '248', '255'], 'b', 'What is the decimal equivalent of the hexadecimal number F0?'),
 (137, 208, 236, '9E', ['155', '158', '162', '178'], 'b', 'What is the decimal representation of the hexadecimal number 9E?'),
 (138, 208, 236, 'C8', ['192', '200', '216', '248'], 'c', 'Which decimal number represents the hexadecimal number C8?'),
 (139, 208, 236, 'E5', ['228', '229', '233', '237'], 'c', 'What is the decimal equivalent of the hexadecimal number E5?'),
 (140, 209, 236, '10F', ['239', '255', '271', '287'], 'c', 'What is the decimal representation of the hexadecimal number 10F?'),
]
for n, qp, ap, s, opts, book, q in H2D:
    v = int(val(s, 16))
    terms = []
    for k, ch in enumerate(s):
        p = 16 ** (len(s) - 1 - k)
        d = DIG.index(ch)
        if d:
            terms.append(f'{d}\\times{p}')
    item(n, qp, ap, q, opts, str(v), 10, book,
         f'${s}_{{16}} = {" + ".join(terms)} = {v}$ (A=10, B=11, C=12, D=13, E=14, F=15).',
         'Hex → decimal: left digit × 16, add the right digit.')

# ---------------------------------------------------------- Q141-150 hex<->oct
HO = [
 (141, 209, 236, '3A', 16, 8, ['52', '64', '76', '102'], 'c', 'What is the octal representation of the hexadecimal number 3A?', (0, '72')),
 (142, 209, 236, '27', 8, 16, ['13', '17', '23', '47'], 'b', 'What is the hexadecimal representation of the octal number 27?', None),
 (143, 209, 236, '58', 16, 8, ['102', '130', '160', '230'], 'd', 'What is the octal representation of the hexadecimal number 58?', None),
 (144, 209, 236, '55', 8, 16, ['37', '47', '57', '67'], 'b', 'What is the hexadecimal representation of the octal number 55?', (0, '2D')),
 (145, 209, 236, 'AB', 16, 8, ['245', '313', '527', '653'], 'b', 'What is the octal representation of the hexadecimal number AB?', (0, '253')),
 (146, 209, 237, '127', 8, 16, ['4F', '5F', '6F', '7F'], 'a', 'What is the hexadecimal representation of the octal number 127?', (0, '57')),
 (147, 209, 237, 'C9', 16, 8, ['147', '210', '311', '451'], 'd', 'What is the octal representation of the hexadecimal number C9?', None),
 (148, 209, 237, '345', 8, 16, ['55', '95', '155', '255'], 'c', 'What is the hexadecimal representation of the octal number 345?', (0, 'E5')),
 (149, 210, 237, 'EF', 16, 8, ['157', '247', '357', '457'], 'b', 'What is the octal representation of the hexadecimal number EF?', None),
 (150, 210, 237, '632', 8, 16, ['1A6', '256', '366', '466'], 'c', 'What is the hexadecimal representation of the octal number 632?', (0, '19A')),
]
for n, qp, ap, s, bi, bo, opts, book, q, fix in HO:
    v = int(val(s, bi))
    r = to_int(v, bo)
    bits = to_int(v, 2)
    if bo == 8:
        pad = (-len(bits)) % 3
        grp = ' | '.join(((('0' * pad) + bits)[i:i + 3]) for i in range(0, len(bits) + pad, 3))
        how = f'hex → binary {bits}; regroup in threes: {grp} → octal {r}'
    else:
        pad = (-len(bits)) % 4
        grp = ' | '.join(((('0' * pad) + bits)[i:i + 4]) for i in range(0, len(bits) + pad, 4))
        how = f'octal → binary {bits}; regroup in fours: {grp} → hex {r}'
    item(n, qp, ap, q, opts, r, bo, book,
         f'Go through binary: {how} (both equal {v} in decimal).',
         'Hex ↔ octal: convert via binary (4-bit groups ↔ 3-bit groups).', fix=fix)

# ---------------------------------------------------------- Q151-160 bin->hex
B2H = [
 (151, 210, 237, '1101', ['A', 'B', 'C', 'D'], 'a', 'What is the hexadecimal representation of the binary number 1101?'),
 (152, 210, 237, '101010', ['2A', '2B', '2C', '2D'], 'a', 'What is the hexadecimal representation of the binary number 101010?'),
 (153, 210, 237, '11110000', ['F0', 'F1', 'F2', 'F3'], 'a', 'What is the hexadecimal representation of the binary number 11110000?'),
 (154, 210, 237, '10011011', ['9B', '9C', '9D', '9E'], 'a', 'What is the hexadecimal representation of the binary number 10011011?'),
 (155, 210, 237, '11001010', ['CA', 'CB', 'CC', 'CD'], 'a', 'What is the hexadecimal representation of the binary number 11001010?'),
 (156, 210, 238, '10111101', ['BD', 'BE', 'BF', 'C0'], 'a', 'What is the hexadecimal representation of the binary number 10111101?'),
 (157, 210, 238, '11100011', ['E3', 'E4', 'E5', 'E6'], 'a', 'What is the hexadecimal representation of the binary number 11100011?'),
 (158, 211, 238, '11010111', ['D7', 'D8', 'D9', 'DA'], 'a', 'What is the hexadecimal representation of the binary number 11010111?'),
 (159, 211, 238, '10011101', ['9D', '9E', '9F', 'A0'], 'a', 'What is the hexadecimal representation of the binary number 10011101?'),
 (160, 211, 238, '11111111', ['FF', '100', '101', '110'], 'a', 'What is the hexadecimal representation of the binary number 11111111?'),
]
for n, qp, ap, s, opts, book, q in B2H:
    pad = (-len(s)) % 4
    t = '0' * pad + s
    grp = ' | '.join(t[i:i + 4] for i in range(0, len(t), 4))
    r = to_int(int(val(s, 2)), 16)
    item(n, qp, ap, q, opts, r, 16, book,
         f'Group the bits in fours from the right: {grp} → {" ".join(r)} = ${r}_{{16}}$.',
         'Binary → hex: 4-bit groups from the right (1010=A … 1111=F).')

# ---------------------------------------------------------- Q161-170 dec frac -> bin
DF = [
 (161, 211, 238, '0.375', ['0.110', '0.011', '0.101', '0.111'], 'a', None),
 (162, 211, 238, '0.625', ['0.010', '0.101', '0.110', '0.111'], 'c', None),
 (163, 211, 238, '0.875', ['0.101', '0.110', '0.111', '0.1001'], 'b', None),
 (164, 211, 238, '0.25', ['0.001', '0.010', '0.011', '0.100'], 'b', None),
 (165, 211, 238, '0.125', ['0.001', '0.010', '0.011', '0.100'], 'c', None),
 (166, 211, 239, '0.5', ['0.1', '0.01', '0.001', '0.0001'], 'a', None),
 (167, 212, 239, '0.0625', ['0.0001', '0.001', '0.0101', '0.011'], 'a', None),
 (168, 212, 239, '0.875', ['0.110', '0.111', '0.1001', '0.101'], 'b', None),
 (169, 212, 239, '0.875', ['0.101', '0.110', '0.111', '0.1001'], 'b', None),
]
for n, qp, ap, s, opts, book, fix in DF:
    x = F(s)
    r = to_frac(x, 2)
    steps = []
    y = x
    while y:
        y2 = y * 2
        steps.append(f'{fmt_num(y)}×2 = {fmt_num(y2)} → {int(y2)}')
        y = y2 - int(y2)
    item(n, qp, ap, f'What is the binary representation of the decimal fraction {s}?', opts, r, 2, book,
         f'Multiply the fraction by 2 repeatedly and read the integer parts downward: {"; ".join(steps)} → ${s} = {r}_2$.',
         'Fraction → binary: repeated ×2, integer parts top-down.', fix=fix)
emit(170, 212, 239, 'What is the binary equivalent of the decimal fraction 0.3, correct to four binary places?',
     ['0.0101', '0.101', '0.0011', '0.0100'], 'd', 'c',
     '0.3×2 = 0.6 → 0; 0.6×2 = 1.2 → 1; 0.2×2 = 0.4 → 0; 0.4×2 = 0.8 → 0; 0.8×2 = 1.6 → 1 … so 0.3 = 0.0100110011…₂ (the pattern 0011 repeats forever). To four places it is 0.0100.',
     'A decimal fraction terminates in binary only if its denominator is a power of 2; 0.3 = 3/10 does not.',
     'The book prints (c) 0.0011 (= 0.1875), and none of its printed options is the binary form of 0.3, which never terminates. The question now asks for four binary places and option (d) has been changed from 0.011 to 0.0100.')

# ---------------------------------------------------------- Q171-180 bin frac -> dec
BF = [
 (171, 212, 239, '0.101', ['0.625', '0.6255', '0.625625', '0.6250625'], 'a', None),
 (172, 212, 239, '0.011', ['0.25', '0.375', '0.4375', '0.6875'], 'b', None),
 (173, 212, 239, '0.1101', ['0.625', '0.65625', '0.734375', '0.84375'], 'b', (1, '0.8125')),
 (174, 212, 239, '0.0011', ['0.0625', '0.15625', '0.1875', '0.4375'], 'a', None),
 (175, 212, 239, '0.10001', ['0.15625', '0.59375', '0.78125', '0.9375'], 'b', (1, '0.53125')),
 (176, 213, 239, '0.111', ['0.84375', '0.875', '0.90625', '0.96875'], 'b', None),
 (177, 213, 240, '0.0101', ['0.15625', '0.34375', '0.53125', '0.71875'], 'c', (0, '0.3125')),
 (178, 213, 240, '0.10101', ['0.65625', '0.78125', '0.90625', '0.96875'], 'c', None),
 (179, 213, 240, '0.01111', ['0.34375', '0.46875', '0.59375', '0.71875'], 'c', None),
 (180, 213, 240, '0.11011', ['0.671875', '0.796875', '0.921875', '0.984375'], 'a', (0, '0.84375')),
]
for n, qp, ap, s, opts, book, fix in BF:
    x = val(s, 2)
    terms = [f'2^{{-{k}}}' for k, ch in enumerate(s[2:], 1) if ch == '1']
    item(n, qp, ap, f'What is the decimal equivalent of the binary fraction {s}?', opts, fmt_num(x), 10, book,
         f'${s}_2 = {" + ".join(terms)} = {fmt_num(x)}$.',
         'Binary places after the point: 0.5, 0.25, 0.125, 0.0625, 0.03125 …', fix=fix)

# ---------------------------------------------------------- Q181-190 dec frac -> oct
DO = [
 (181, 213, 240, '0.125', ['0.1', '0.2', '0.3', '0.4'], 'b', None),
 (182, 213, 240, '0.375', ['0.3', '0.4', '0.5', '0.6'], 'c', None),
 (183, 213, 240, '0.625', ['0.4', '0.5', '0.6', '0.7'], 'c', None),
 (184, 213, 240, '0.875', ['0.6', '0.7', '0.8', '0.9'], 'b', None),
 (185, 213, 240, '0.25', ['0.2', '0.3', '0.4', '0.5'], 'c', None),
 (186, 213, 240, '0.5', ['0.4', '0.5', '0.6', '0.7'], 'c', None),
 (187, 214, 240, '0.0625', ['0.04', '0.05', '0.06', '0.07'], 'b', None),
 (188, 214, 241, '0.03125', ['0.02', '0.03', '0.04', '0.05'], 'c', None),
 (189, 214, 241, '0.15625', ['0.1', '0.2', '0.3', '0.4'], 'b', (0, '0.12')),
 (190, 214, 241, '0.78125', ['0.5', '0.6', '0.7', '0.8'], 'd', (3, '0.62')),
]
for n, qp, ap, s, opts, book, fix in DO:
    x = F(s)
    r = to_frac(x, 8)
    steps = []
    y = x
    while y:
        y2 = y * 8
        steps.append(f'{fmt_num(y)}×8 = {fmt_num(y2)} → {int(y2)}')
        y = y2 - int(y2)
    item(n, qp, ap, f'What is the octal equivalent of the decimal fraction {s}?', opts, r, 8, book,
         f'Multiply by 8 repeatedly and read the integer parts: {"; ".join(steps)} → ${s} = {r}_8$.',
         'Fraction → octal: repeated ×8.', fix=fix)

# ---------------------------------------------------------- Q191-200 oct frac -> dec
OD = [
 (191, 214, 241, '0.2', ['0.125', '0.25', '0.375', '0.5'], 'b', None),
 (192, 214, 241, '0.4', ['0.125', '0.25', '0.375', '0.5'], 'b', None),
 (193, 214, 241, '0.6', ['0.375', '0.5', '0.625', '0.75'], 'b', None),
 (194, 214, 241, '0.7', ['0.5', '0.625', '0.75', '0.875'], 'c', None),
 (195, 214, 241, '0.3', ['0.125', '0.25', '0.375', '0.5'], 'c', None),
 (196, 214, 241, '0.5', ['0.3125', '0.375', '0.4375', '0.5'], 'c', (0, '0.625')),
 (197, 215, 241, '0.05', ['0.015625', '0.03125', '0.0625', '0.125'], 'b', (0, '0.078125')),
 (198, 215, 241, '0.04', ['0.015625', '0.03125', '0.0625', '0.125'], 'b', None),
 (199, 215, 241, '0.2', ['0.125', '0.25', '0.375', '0.5'], 'b', None),
]
for n, qp, ap, s, opts, book, fix in OD:
    x = val(s, 8)
    terms = [f'{DIG.index(ch)}/8^{k}' if k > 1 else f'{DIG.index(ch)}/8' for k, ch in enumerate(s[2:], 1) if ch != '0']
    item(n, qp, ap, f'What is the decimal equivalent of the octal fraction {s}?', opts, fmt_num(x), 10, book,
         f'${s}_8 = {" + ".join(terms)} = {fmt_num(x)}$.',
         'Octal places after the point: 1/8 = 0.125, 1/64 = 0.015625.', fix=fix)
emit(200, 215, 242, 'What is the decimal equivalent of the octal fraction 0.7?',
     ['0.625', '0.75', '0.875', '1.0'], 'c', 'c',
     '$0.7_8 = 7/8 = 0.875$.', 'Octal digits run 0–7 only; 0.7₈ = 7/8.',
     'The book prints the fraction as "0.8", which is not a valid octal numeral (8 is not an octal digit). The stem has been corrected to 0.7, which gives the book\'s key (c) 0.875.')

# ---------------------------------------------------------- Q201-210 oct frac -> bin
OB = [
 (201, 215, 242, '0.2', ['0.001', '0.010', '0.100', '0.110'], 'b', None),
 (202, 215, 242, '0.4', ['0.001', '0.010', '0.100', '0.110'], 'b', None),
 (203, 215, 242, '0.6', ['0.011', '0.101', '0.110', '0.111'], 'c', None),
 (204, 215, 242, '0.7', ['0.111', '0.1001', '0.1011', '0.1101'], 'a', None),
 (205, 215, 242, '0.3', ['0.001', '0.010', '0.100', '0.110'], 'b', (0, '0.011')),
 (206, 215, 242, '0.5', ['0.010', '0.011', '0.100', '0.101'], 'b', None),
 (207, 215, 242, '0.05', ['0.0000101', '0.000101', '0.001010', '0.010101'], 'c', None),
 (208, 216, 242, '0.04', ['0.0000101', '0.000101', '0.001010', '0.010101'], 'c', (0, '0.000100')),
 (209, 216, 242, '0.2', ['0.001', '0.010', '0.100', '0.110'], 'b', None),
]
for n, qp, ap, s, opts, book, fix in OB:
    groups = ' '.join(format(DIG.index(c), '03b') for c in s[2:])
    r = '0.' + groups.replace(' ', '')
    item(n, qp, ap, f'What is the binary equivalent of the octal fraction {s}?', opts, r, 2, book,
         f'Replace each octal digit after the point by 3 bits: {" ".join(s[2:])} → {groups}, so ${s}_8 = {r}_2$.',
         'Octal → binary: every digit → 3 bits, point stays put.', fix=fix)
emit(210, 216, 242, 'What is the binary equivalent of the octal fraction 0.7?',
     ['0.111', '0.1001', '0.1011', '0.1101'], 'a', 'a',
     'The octal digit 7 is 111 in three bits, so $0.7_8 = 0.111_2$ (= 0.875).', 'Octal 7 = 111.',
     'The book prints the fraction as "0.8", which is not a valid octal numeral (8 is not an octal digit). The stem has been corrected to 0.7, which gives the book\'s key (a) 0.111.')

# ---------------------------------------------------------- Q211-220 bin frac -> oct
BO = [
 (211, 216, 242, '0.001', ['0.1', '0.2', '0.3', '0.4'], 'b', None),
 (212, 216, 242, '0.010', ['0.1', '0.2', '0.3', '0.4'], 'b', None),
 (213, 216, 242, '0.011', ['0.3', '0.4', '0.5', '0.6'], 'd', None),
 (214, 216, 242, '0.111', ['0.7', '0.6', '0.5', '0.4'], 'a', None),
 (215, 216, 242, '0.00101', ['0.12', '0.13', '0.14', '0.15'], 'c', None),
 (216, 216, 242, '0.0101', ['0.22', '0.23', '0.24', '0.25'], 'c', None),
 (217, 216, 242, '0.000101', ['0.05', '0.06', '0.07', '0.08'], 'b', None),
 (218, 217, 242, '0.001101', ['0.15', '0.16', '0.17', '0.18'], 'c', None),
 (219, 217, 242, '0.1001', ['0.46', '0.47', '0.48', '0.49'], 'd', (0, '0.44')),
 (220, 217, 242, '0.11101', ['0.75', '0.76', '0.77', '0.78'], 'b', (0, '0.72')),
]
for n, qp, ap, s, opts, book, fix in BO:
    f = s[2:]
    pad = (-len(f)) % 3
    t = f + '0' * pad
    grp = ' | '.join(t[i:i + 3] for i in range(0, len(t), 3))
    r = '0.' + ''.join(str(int(t[i:i + 3], 2)) for i in range(0, len(t), 3))
    item(n, qp, ap, f'What is the octal equivalent of the binary fraction {s}?', opts, r, 8, book,
         f'After the point, group the bits in threes from the left (padding with 0s on the right): {grp} → {r}₈.',
         'Fraction bits → octal: 3-bit groups rightward from the point.', fix=fix)

# ---------------------------------------------------------- Q221-230 hex frac -> bin
HB = [
 (221, 217, 242, '0.1', ['0.0001', '0.0010', '0.0101', '0.1000'], 'b', None),
 (222, 217, 242, '0.3', ['0.0010', '0.0100', '0.0110', '0.1000'], 'c', (0, '0.0011')),
 (223, 217, 242, '0.5', ['0.0101', '0.1000', '0.1010', '0.1100'], 'd', None),
 (224, 217, 242, '0.7', ['0.0110', '0.1000', '0.1100', '0.1110'], 'd', (0, '0.0111')),
 (225, 217, 242, '0.2', ['0.0010', '0.0100', '0.0110', '0.1000'], 'b', None),
 (226, 217, 242, '0.4', ['0.0100', '0.0110', '0.1000', '0.1010'], 'a', None),
 (227, 217, 242, '0.06', ['0.000110', '0.001100', '0.011000', '0.110000'], 'c', (0, '0.00000110')),
 (228, 218, 242, '0.08', ['0.000100', '0.001000', '0.010000', '0.100000'], 'c', (0, '0.00001000')),
 (229, 218, 242, '0.09', ['0.000100', '0.001000', '0.010000', '0.100000'], 'c', (0, '0.00001001')),
 (230, 218, 242, '0.3A', ['0.00111010', '0.01011010', '0.01111010', '0.11111010'], 'c', None),
]
for n, qp, ap, s, opts, book, fix in HB:
    groups = ' '.join(format(DIG.index(c), '04b') for c in s[2:])
    r = '0.' + groups.replace(' ', '')
    item(n, qp, ap, f'What is the binary equivalent of the hexadecimal fraction {s}?', opts, r, 2, book,
         f'Replace each hex digit after the point by its 4-bit group: {" ".join(s[2:])} → {groups}, so ${s.replace("A", "A")}_{{16}} = {r}_2$.',
         'Hex → binary: every digit → 4 bits (keep the leading zeros after the point).', fix=fix)

# ---------------------------------------------------------- Q231-240 binary addition
BA = [
 (231, 218, 243, '1101', '1011', ['10000', '10100', '11110', '11111'], 'c', (0, '11000')),
 (232, 218, 243, '101010', '110011', ['1100101', '1111101', '10001001', '10101001'], 'b', (0, '1011101')),
 (233, 218, 243, '1111', '1111', ['1110', '11110', '10000', '10001'], 'c', None),
 (234, 218, 243, '1010101', '1101010', ['10101111', '11011111', '10011111', '11111111'], 'c', (0, '10111111')),
 (235, 218, 243, '10010', '111001', ['101011', '111011', '101101', '110101'], 'a', (0, '1001011')),
 (236, 218, 243, '11101', '1001', ['100110', '110000', '110010', '111010'], 'd', None),
 (237, 218, 243, '1111111', '1', ['10000000', '1111110', '1111111', '10000001'], 'a', None),
 (238, 218, 243, '1001', '10', ['1011', '1100', '1101', '1110'], 'c', None),
 (239, 219, 243, '11001100', '1010101', ['100100101', '111011101', '100101101', '111011000'], 'b', (0, '100100001')),
 (240, 219, 243, '111', '10101', ['100100', '111000', '101001', '110101'], 'd', (0, '11100')),
]
for n, qp, ap, a, b, opts, book, fix in BA:
    va, vb = int(val(a, 2)), int(val(b, 2))
    r = to_int(va + vb, 2)
    item(n, qp, ap, f'What is the result of adding {a} and {b} in binary?', opts, r, 2, book,
         f'In decimal: {a}₂ = {va} and {b}₂ = {vb}; {va} + {vb} = {va + vb} = {r}₂. (Column rules: 0+0=0, 0+1=1, 1+1=10, 1+1+1=11.)',
         'Check any binary sum by converting both numbers to decimal.', fix=fix)

# ---------------------------------------------------------- Q241-250 binary subtraction
BS = [
 (241, 219, 243, '10101', '1101', ['10010', '10011', '10110', '11000'], 'c', (0, '1000')),
 (242, 219, 243, '110101', '101010', ['1111', '10101', '100011', '100111'], 'c', (0, '1011')),
 (243, 219, 243, '100000', '11111', ['1001', '10001', '10101', '11010'], 'b', (0, '1')),
 (244, 219, 243, '110010', '10101', ['100111', '100110', '100101', '100011'], 'b', (0, '11101')),
 (245, 219, 243, '111001', '10010', ['100011', '101001', '101011', '110101'], 'a', (0, '100111')),
 (246, 219, 243, '11101', '1001', ['1010', '1100', '1101', '1111'], 'c', (0, '10100')),
 (247, 219, 243, '11111111', '10000000', ['1000001', '111', '1111111', '10000000'], 'b', None),
 (248, 220, 243, '1001', '10', ['101', '110', '111', '1000'], 'd', None),
 (249, 220, 243, '11001100', '1010101', ['101010', '100101', '1001001', '1011101'], 'd', (0, '1110111')),
 (250, 220, 243, '111111', '10101', ['100010', '110011', '111000', '111010'], 'a', (0, '101010')),
]
for n, qp, ap, a, b, opts, book, fix in BS:
    va, vb = int(val(a, 2)), int(val(b, 2))
    r = to_int(va - vb, 2)
    item(n, qp, ap, f'What is the result of subtracting {b} from {a} in binary?', opts, r, 2, book,
         f'In decimal: {a}₂ = {va} and {b}₂ = {vb}; {va} − {vb} = {va - vb} = {r}₂.',
         'Binary subtraction: 0−1 borrows 2 (10₂) from the next column; verify in decimal.', fix=fix)

# ---------------------------------------------------------- Q251-260 1's complement
C1 = [
 (251, 220, 243, '11001', ['11001', '00110', '00111', '11010'], 'b'),
 (252, 220, 243, '1010101', ['1010101', '0101010', '0101011', '1010100'], 'b'),
 (253, 220, 244, '111000', ['111000', '000111', '000110', '111111'], 'b'),
 (254, 220, 244, '1001011', ['1001011', '0110100', '0110101', '1001010'], 'c'),
 (255, 220, 244, '11111', ['11111', '00000', '00001', '11110'], 'd'),
 (256, 220, 244, '1011', ['1011', '0100', '0101', '1010'], 'c'),
 (257, 220, 244, '11111111', ['11111111', '00000000', '00000001', '11111110'], 'd'),
 (258, 220, 244, '110', ['110', '001', '010', '101'], 'b'),
 (259, 221, 244, '1000101', ['1000101', '0111010', '0111011', '1000100'], 'b'),
 (260, 221, 244, '1110000', ['1110000', '0001111', '0001110', '1111111'], 'c'),
]
for n, qp, ap, s, opts, book in C1:
    r = ''.join('1' if c == '0' else '0' for c in s)
    item(n, qp, ap, f"What is the 1's complement of the binary number {s}?", opts, r, None, book,
         f"The 1's complement inverts every bit: {s} → {r}.",
         "1's complement = flip every bit (0↔1).")

# ---------------------------------------------------------- Q261-270 2's complement
C2 = [
 (261, 221, 244, '11001', ['11001', '00110', '00111', '11110'], None, None),
 (262, 221, 244, '1010101', ['1010101', '0101010', '0101011', '1010100'], 'b', None),
 (263, 221, 244, '111000', ['111000', '000111', '001000', '111001'], 'c', None),
 (264, 221, 244, '1001011', ['1001011', '0110100', '0110101', '1001010'], 'b', None),
 (265, 221, 244, '11111', ['11111', '00000', '00001', '11110'], 'd', None),
 (266, 221, 244, '1011', ['1011', '0100', '0101', '1101'], 'd', None),
 (267, 221, 244, '11111111', ['11111111', '00000000', '00000001', '11111110'], 'b', None),
 (268, 221, 244, '110', ['110', '001', '010', '011'], 'b', None),
 (269, 222, 244, '1000101', ['1000101', '0111010', '0111011', '1000110'], 'c', None),
 (270, 222, 244, '1110000', ['1110000', '0001111', '0010000', '1111111'], 'c', None),
]
C2N = {
 261: "The book's answer to this question is not legible in the scan; the key was supplied.",
 263: "The book keys (c), printed as 000110, and repeats 111000 as both (a) and (d); none of its options is the 2's complement 001000. Option (c) has been changed to 001000 and option (d) to 111001.",
 265: "The book prints (d) 11111, which repeats option (a) and is the number itself. The 2's complement of 11111 is 00001, so the key is (c); option (d) has been replaced by 11110 so that the options are distinct.",
 266: "The book prints (d) 1101. 1011 → 0100 + 1 = 0101, so the key is (c).",
 267: "The book prints (b) 00000000, which is only the 1's complement; adding 1 gives 00000001, so the key is (c). Option (d), a repeat of option (a), has been replaced by 11111110.",
 269: "The book prints 0111011 as both option (c) and option (d); option (d) has been replaced by 1000110 so that only one option is correct.",
 270: "The book keys (c), printed as 0001110, and repeats 0001111 as both (b) and (d); none of its options is the 2's complement 0010000. Option (c) has been changed to 0010000 and option (d) to 1111111.",
}
for n, qp, ap, s, opts, book, fix in C2:
    w = len(s)
    r = format(((1 << w) - int(s, 2)) % (1 << w), f'0{w}b')
    ones = ''.join('1' if c == '0' else '0' for c in s)
    N = C2N.get(n)
    if n == 268:
        N = 'The book prints "010" as both option (c) and option (d); option (d) has been replaced by 011. The book keys (b) 001, which is the 1\'s complement; the 2\'s complement is 010, so the key is (c).'
    item(n, qp, ap, f"What is the 2's complement of the binary number {s}?", opts, r, None, book,
         f"2's complement = 1's complement + 1: {s} → {ones} → {ones} + 1 = {r}.",
         "Shortcut: copy bits from the right up to and including the first 1, then flip the rest.",
         fix=fix, N=N)

print('\n'.join(out))
