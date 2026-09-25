"""OCR v3: repair text strokes hidden under the red watermark before OCR.

The watermark is opaque red drawn over the page, so where it crosses a
letter the letter's pixels are lost.  We treat red pixels as unknown and
fill each one from its non-red neighbourhood (dark if most known
neighbours are dark), which reconnects strokes cut by the thin watermark
lines.  Then the page body is split into its two columns and OCR'd.
"""
import pymupdf, numpy as np, sys, os, subprocess, glob
from PIL import Image
from scipy.ndimage import uniform_filter, binary_dilation

REPO = '/home/user/ComputerINTEGRATE'
SP = os.environ.get('OCR_WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work'))  # OCR scratch dir
OUT = SP + '/ocr3'
IMG = SP + '/clean3'
os.makedirs(OUT, exist_ok=True)
os.makedirs(IMG, exist_ok=True)
FILES = sorted(glob.glob(REPO + '/*-compress.pdf'))


def locate(gp):
    for f in FILES:
        a, b = os.path.basename(f).split('-')[:2]
        a = int(a); b = int(b)
        if a <= gp <= b:
            return f, gp - a


def cleaned(gp, dpi=240):
    f, i = locate(gp)
    d = pymupdf.open(f)
    pix = d[i].get_pixmap(dpi=dpi)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3].astype(np.int16)
    r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]
    red = (r - np.maximum(g, b)) > 50
    red = binary_dilation(red, iterations=1)
    gray = (r + g + b) / 3.0
    dark = (gray < 110) & ~red
    known = (~red).astype(float)
    k = 7
    num = uniform_filter(dark.astype(float), size=k)
    den = uniform_filter(known, size=k)
    frac = np.where(den > 0.05, num / np.maximum(den, 1e-6), 0)
    fill = red & (frac > 0.42)
    out = np.where(dark | fill, 0, 255).astype(np.uint8)
    return out


def tess(arr, name, psm='6'):
    png = f'{IMG}/{name}.png'
    Image.fromarray(arr).save(png)
    return subprocess.run(['tesseract', png, '-', '--psm', psm],
                          capture_output=True, text=True).stdout


def gutter(body, W):
    dark = (body < 128).sum(axis=0)
    lo, hi = int(W * 0.44), int(W * 0.56)
    seg = dark[lo:hi]
    m = seg.min()
    idx = np.where(seg <= m + 2)[0]
    best = (idx[0], idx[0]); s = p = idx[0]
    for x in list(idx[1:]) + [None]:
        if x is not None and x == p + 1:
            p = x
            continue
        if p - s > best[1] - best[0]:
            best = (s, p)
        if x is not None:
            s = p = x
    return lo + (best[0] + best[1]) // 2


def run(gp, force=False):
    out = f'{OUT}/p{gp:03d}.txt'
    if os.path.exists(out) and not force:
        return
    im = cleaned(gp)
    H, W = im.shape
    y0, y1 = int(H * 0.165), int(H * 0.86)
    body = im[y0:y1]
    g = gutter(body, W)
    L = tess(body[:, :g], f'p{gp:03d}L')
    Rr = tess(body[:, g:], f'p{gp:03d}R')
    open(out, 'w').write('=====LEFT\n' + L + '\n=====RIGHT\n' + Rr)


if __name__ == '__main__':
    if sys.argv[1] == 'pages':
        for gp in map(int, sys.argv[2:]):
            run(gp, force=True)
    else:
        k = int(sys.argv[1]); n = int(sys.argv[2])
        for gp in range(11, 466):
            if gp % n == k:
                run(gp)
                print(gp, flush=True)
