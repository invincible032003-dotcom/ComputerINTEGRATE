"""Chapter 5 (Boolean algebra & logic gates): 10 templated questions per gate."""
L = 'abcd'
F = {
    'AND': lambda a, b: a & b, 'OR': lambda a, b: a | b,
    'NAND': lambda a, b: 1 - (a & b), 'NOR': lambda a, b: 1 - (a | b),
    'XOR': lambda a, b: a ^ b, 'XNOR': lambda a, b: 1 - (a ^ b),
}
RULE = {
    'AND': 'output 1 only when all inputs are 1',
    'OR': 'output 1 when at least one input is 1',
    'NAND': 'NOT of AND — output 0 only when all inputs are 1',
    'NOR': 'NOT of OR — output 1 only when all inputs are 0',
    'XOR': 'output 1 when the inputs differ',
    'XNOR': 'output 1 when the inputs are equal',
}
EXPR = {'AND': '`A * B` (A·B)', 'OR': '`A + B`', 'NAND': "`(A * B)'`", 'NOR': "`(A + B)'`",
        'XOR': '`A XOR B` (A ⊕ B = A′B + AB′)', 'XNOR': '`A XNOR B` (A ⊙ B = AB + A′B′)'}
MNEM = {
    'AND': 'AND = series switches: any 0 → 0.',
    'OR': 'OR = parallel switches: any 1 → 1.',
    'NAND': 'NAND = AND then invert: only 11 gives 0. Universal gate.',
    'NOR': 'NOR = OR then invert: only 00 gives 1. Universal gate.',
    'XOR': 'XOR = "odd-one-out" / inequality detector: 1 when inputs differ.',
    'XNOR': 'XNOR = equality detector: 1 when inputs match.',
}
TABLES = {  # printed truth-table options, as output columns for AB = 00, 01, 10, 11
    'AND': ['0110', '0001', '0101', '1110'],
    'OR': ['0001', '0110', '0111', '1000'],
    'NAND': ['0111', '1000', '1110', '0001'],
    'NOR': ['0111', '1000', '1110', '0001'],
    'XOR': ['0110', '1001', '0001', '1110'],
    'XNOR': ['0110', '1001', '0001', '1110'],
}
out = []


def tt(col):
    return ', '.join(f'{ab}→{y}' for ab, y in zip(['00', '01', '10', '11'], col))


def emit(n, qp, ap, q, opts, key, book, X, S, N=''):
    out.append(f'#{n} p{qp} a{ap}')
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
    out.append('')


OUT4 = ['0', '1', 'X (undefined)', 'None of the above']
OUT4b = ['1', '0', 'X (undefined)', 'None of the above']  # AND block order
SHAPES = ['Triangle', 'Rectangle', 'Circle', 'Diamond']
COMBOS = ['0 and 1', '0 and 0', '1 and 1', 'All of the above']
EXPRS_AND = ['`A + B`', '`A * B`', '`A XOR B`', "`A' + B'`"]
EXPRS_NAND = ['`A + B`', '`A * B`', '`A XOR B`', "`(A * B)'`"]
EXPRS_NOR = ['`A + B`', '`A * B`', '`A XOR B`', "`(A + B)'`"]
EXPRS_XNOR = ['`A + B`', '`A * B`', '`A XNOR B`', "`(A + B)'`"]
TWICE = ['The original input', '0', '1', 'X (undefined)']


def out_q(g, n, qp, ap, a, b, book, opts=OUT4):
    y = F[g](a, b)
    k = L[opts.index(str(y))]
    both = 'both inputs are ' + str(a) if a == b else f'one input is {a} and the other is {b}'
    q = f'What is the output of an {g} gate if {both}?' if g[0] in 'AEIOUX' else f'What is the output of a {g} gate if {both}?'
    N = ''
    if book != k:
        N = f'The book prints ({book}) {opts[L.index(book)]}. For inputs {a} and {b} the {g} gate gives {y}, so the key is ({k}).'
    emit(n, qp, ap, q, opts, k, book,
         f'{g}: {RULE[g]}. With inputs {a} and {b} the output is {y}.', MNEM[g], N)


def art(g):
    return 'an' if g[0] in 'AEIOUX' else 'a'


def inputs_q(g, n, qp, ap, book):
    emit(n, qp, ap, f'How many inputs does {art(g)} {g} gate typically have?', ['1', '2', '3', 'It can vary'], 'b', book,
         f'The basic {g} gate has two inputs (multi-input versions exist, but the standard gate is 2-input).',
         f'Every basic gate except NOT is drawn with 2 inputs; NOT has 1.')


def x_q(g, n, qp, ap, book):
    q = f'What is the output of {art(g)} {g} gate if one or both inputs are X (undefined)?'
    extra = {
        'AND': ' (If the other input is 0 the output is forced to 0, but in general an unknown input gives an unknown output.)',
        'OR': ' (If the other input is 1 the output is forced to 1; otherwise it stays unknown.)',
        'NAND': ' (A 0 on the other input would force the output to 1; otherwise it stays unknown.)',
        'NOR': ' (A 1 on the other input would force the output to 0; otherwise it stays unknown.)',
        'XOR': ' (No value of the other input can force an XOR output, so it is always unknown.)',
        'XNOR': ' (No value of the other input can force an XNOR output, so it is always unknown.)',
    }[g]
    N = ''
    if book != 'c':
        N = f'The book prints ({book}) {OUT4[L.index(book)]}. An undefined input generally makes the {g} output undefined (X), so the key is (c).'
    emit(n, qp, ap, q, OUT4, 'c', book, 'An undefined (X) input propagates to an undefined output.' + extra,
         'X in → X out, unless a controlling value forces the result (0 for AND, 1 for OR).', N)


def shape_q(g, n, qp, ap, book):
    distinct = {'AND': 'a D shape', 'OR': 'a curved shield shape', 'NAND': 'a D shape with a bubble',
                'NOR': 'a curved shield with a bubble', 'XOR': 'an OR shape with an extra curved line at the input',
                'XNOR': 'an XOR shape with a bubble'}[g]
    N = ''
    if book != 'b':
        N = (f'The book prints ({book}) {SHAPES[L.index(book)]}, but no standard draws the {g} gate as a diamond. Of the options, only the '
             f'rectangle (the IEC / IEEE Std 91 rectangular symbol) is a recognised form, so the key is (b).')
    emit(n, qp, ap, f'In a logic circuit diagram, how is {art(g)} {g} gate typically represented?', SHAPES, 'b', book,
         f'In the distinctive-shape (ANSI) convention the {g} gate is {distinct}; in the rectangular IEC 60617 / IEEE 91 convention every gate is a rectangle '
         f'with a function label (such as &, ≥1 or =1). Among the options only "rectangle" fits.',
         'Triangle (+ bubble) = NOT/buffer; other gates are rectangles in IEC notation.', N)


def combos_q(g, n, qp, ap, book):
    emit(n, qp, ap, f'In a truth table, what are the possible combinations of inputs for {art(g)} {g} gate?', COMBOS, 'd', book,
         'A 2-input truth table lists every input pair — 00, 01, 10 and 11 — so all the listed combinations occur.',
         'n inputs → 2ⁿ rows (2 inputs → 4 rows).')


def expr_q(g, n, qp, ap, opts, key, book):
    emit(n, qp, ap, f'Which Boolean expression represents the operation of {art(g)} {g} gate?', opts, key, book,
         f'The {g} operation is written {EXPR[g]}.',
         'AND = ·, OR = +, NOT = ′ (bar), NAND = (A·B)′, NOR = (A+B)′, XOR = ⊕.')


def twice_q(g, n, qp, ap, book):
    how = {
        'NOT': "NOT(NOT A) = A — double inversion cancels (involution law).",
        'NAND': 'A NAND gate with its inputs tied together acts as NOT, so applying it twice inverts twice and returns the original input.',
        'NOR': 'A NOR gate with its inputs tied together acts as NOT, so applying it twice returns the original input.',
        'XOR': 'XOR-ing a value twice with the same operand restores it: (A ⊕ B) ⊕ B = A — the basis of XOR encryption and parity tricks.',
        'XNOR': 'XNOR-ing twice with the same operand restores the value: (A ⊙ B) ⊙ B = A.',
    }[g]
    emit(n, qp, ap, f'What is the result of applying {art(g)} {g} operation twice ({g}({g})) to an input?', TWICE, 'a', book,
         how, 'Double NOT = original (A″ = A).')


def table_q(g, n, qp, ap, book):
    cols = TABLES[g]
    want = ''.join(str(F[g](a, b)) for a, b in [(0, 0), (0, 1), (1, 0), (1, 1)])
    k = L[cols.index(want)]
    opts = ['A B → Output: ' + tt(c) for c in cols]
    N = ''
    if book != k:
        N = f'The book prints ({book}), which is the table {tt(cols[L.index(book)])}. The {g} gate gives {tt(want)}, so the key is ({k}).'
    emit(n, qp, ap, f'What is the truth table representation of {art(g)} {g} gate with two inputs?', opts, k, book,
         f'{g}: {RULE[g]} — {tt(want)}.', MNEM[g], N)


# ---------------- AND 1-10
out_q('AND', 1, 243, 253, 1, 1, 'a', OUT4b)
inputs_q('AND', 2, 243, 253, 'b')
out_q('AND', 3, 243, 253, 0, 1, 'b', OUT4b)
expr_q('AND', 4, 243, 253, EXPRS_AND, 'b', 'b')
# Q5 stem missing in print
emit(5, 243, 253, 'What is the output of an AND gate if both inputs are 0?', OUT4b, 'b', 'b',
     'AND: output 1 only when all inputs are 1. With inputs 0 and 0 the output is 0.', MNEM['AND'],
     'The printed book omits the stem of this question (only its options appear); it has been restored from the book\'s own explanation, which refers to both inputs being 0.')
combos_q('AND', 6, 243, 253, 'd')
emit(7, 243, 253, 'What is the output of an AND gate if one or both inputs are X (undefined)?', OUT4b, 'c', 'b',
     'An undefined (X) input generally gives an undefined output. Only a 0 on the other input would force the AND output to 0.',
     'X in → X out, unless a controlling value (0 for AND) forces the result.',
     'The book prints (b) 0, which holds only when the other input is 0. In general an undefined input makes the AND output undefined, so the key is (c).')
shape_q('AND', 8, 243, 253, 'b')
emit(9, 243, 253, 'What is the result of an AND operation between any input and 0?', ['0', '1', 'X (undefined)', 'None of the above'], 'a', 'a',
     'A · 0 = 0 for every A (null/annulment law).', 'A·0 = 0, A·1 = A, A+1 = 1, A+0 = A.')
table_q('AND', 10, 244, 253, 'c')
# ---------------- OR 11-20
out_q('OR', 11, 244, 254, 0, 0, 'b')
inputs_q('OR', 12, 244, 254, 'b')
out_q('OR', 13, 244, 254, 1, 0, 'b')
expr_q('OR', 14, 244, 254, ['`A + B`', '`A * B`', '`A XOR B`', "`A' + B'`"], 'a', 'a')
out_q('OR', 15, 244, 254, 1, 1, 'b')
combos_q('OR', 16, 244, 254, 'd')
x_q('OR', 17, 245, 254, 'c')
shape_q('OR', 18, 245, 254, 'b')
emit(19, 245, 254, 'What is the result of an OR operation between any input and 1?', OUT4, 'b', 'b',
     'A + 1 = 1 for every A (null law for OR).', 'A + 1 = 1, A + 0 = A.')
table_q('OR', 20, 245, 254, 'c')
# ---------------- NOT 21-30
emit(21, 245, 254, 'What is the output of a NOT gate if the input is 0?', OUT4, 'b', 'b',
     'A NOT gate (inverter) outputs the complement of its input: 0 → 1.', 'NOT flips: 0 ↔ 1.')
emit(22, 245, 254, 'How many inputs does a NOT gate typically have?', ['1', '2', '3', 'It can vary'], 'a', 'a',
     'The NOT gate is the only basic gate with a single input.', 'NOT = 1 input, 1 output.')
emit(23, 245, 255, 'What is the output of a NOT gate if the input is 1?', OUT4, 'a', 'a',
     'NOT 1 = 0.', 'NOT flips: 1 → 0.')
emit(24, 246, 255, 'Which Boolean expression represents the operation of a NOT gate?', ['`A + B`', '`A * B`', '`A XOR B`', "`A'`"], 'd', 'd',
     "NOT is written A′ (A-bar, or ¬A).", "Complement = prime or bar: A′, Ā.")
emit(25, 246, 255, 'What is the output of a NOT gate if the input is X (undefined)?', OUT4, 'c', 'c',
     'The complement of an unknown value is unknown, so the output is X.', 'NOT(X) = X.')
emit(26, 246, 255, 'In a logic circuit diagram, how is a NOT gate typically represented?', SHAPES, 'a', 'a',
     'The NOT gate is drawn as a triangle with a small bubble (circle) at the output; the bubble denotes inversion.', 'Triangle + bubble = NOT; triangle alone = buffer.')
twice_q('NOT', 27, 246, 255, 'a')
emit(28, 246, 255, 'In a truth table, what are the possible values of the input for a NOT gate?', ['0', '1', 'X (undefined)', 'Both a) and b)'], 'd', 'd',
     'A NOT gate has one binary input, so its truth table has just two rows: 0 and 1.', '1 input → 2 rows.')
emit(29, 246, 255, 'What is the output of a NOT gate if the input is X (undefined)?', OUT4, 'c', 'b',
     'An undefined input gives an undefined output: NOT(X) = X.', 'NOT(X) = X.',
     'The book prints (b) 1, although its own explanation says the output is X. The key is (c).')
emit(30, 246, 255, 'What is the truth table representation of a NOT gate?',
     ['Input → Output: 0→0, 1→1', 'Input → Output: 0→1, 1→0', 'Input → Output: 0→0, 1→0', 'Input → Output: 0→1, 1→1'], 'b', 'a',
     'The inverter maps 0 → 1 and 1 → 0.', 'NOT table: 0→1, 1→0.',
     'The book prints (a), the table 0→0, 1→1, which is a buffer (it passes the input through unchanged). The inverter table is 0→1, 1→0, so the key is (b).')
# ---------------- NAND 31-40
out_q('NAND', 31, 246, 256, 0, 0, 'b')
inputs_q('NAND', 32, 247, 256, 'b')
out_q('NAND', 33, 247, 256, 1, 0, 'a')
expr_q('NAND', 34, 247, 256, EXPRS_NAND, 'd', 'd')
out_q('NAND', 35, 247, 256, 1, 1, 'a')
combos_q('NAND', 36, 247, 256, 'd')
x_q('NAND', 37, 247, 256, 'b')
shape_q('NAND', 38, 247, 256, 'b')
twice_q('NAND', 39, 247, 257, 'a')
table_q('NAND', 40, 247, 257, 'c')
# ---------------- NOR 41-50
out_q('NOR', 41, 248, 257, 0, 0, 'b')
inputs_q('NOR', 42, 248, 257, 'b')
out_q('NOR', 43, 248, 257, 1, 0, 'a')
expr_q('NOR', 44, 248, 257, EXPRS_NOR, 'd', 'd')
out_q('NOR', 45, 248, 257, 1, 1, 'a')
combos_q('NOR', 46, 248, 257, 'd')
x_q('NOR', 47, 248, 257, 'b')
shape_q('NOR', 48, 249, 258, 'b')
twice_q('NOR', 49, 249, 258, 'a')
table_q('NOR', 50, 249, 258, 'c')
# ---------------- XOR 51-60
out_q('XOR', 51, 249, 258, 0, 0, 'b')
inputs_q('XOR', 52, 249, 258, 'b')
out_q('XOR', 53, 249, 258, 1, 0, 'b')
expr_q('XOR', 54, 249, 258, ['`A + B`', '`A * B`', '`A XOR B`', "`(A + B)'`"], 'c', 'c')
out_q('XOR', 55, 250, 258, 1, 1, 'b')
combos_q('XOR', 56, 250, 258, 'd')
x_q('XOR', 57, 250, 259, 'b')
shape_q('XOR', 58, 250, 259, 'd')
twice_q('XOR', 59, 250, 259, 'a')
table_q('XOR', 60, 250, 259, 'b')
# ---------------- XNOR 61-70
out_q('XNOR', 61, 250, 259, 0, 0, 'b')
inputs_q('XNOR', 62, 250, 259, 'b')
out_q('XNOR', 63, 251, 259, 1, 0, 'a')
expr_q('XNOR', 64, 251, 259, EXPRS_XNOR, 'c', 'c')
out_q('XNOR', 65, 251, 260, 1, 1, 'b')
combos_q('XNOR', 66, 251, 260, 'd')
x_q('XNOR', 67, 251, 260, 'b')
shape_q('XNOR', 68, 251, 260, 'd')
twice_q('XNOR', 69, 251, 260, 'a')
table_q('XNOR', 70, 251, 260, 'b')
print('\n'.join(out))
