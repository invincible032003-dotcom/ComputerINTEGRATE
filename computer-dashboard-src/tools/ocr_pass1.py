import pymupdf, numpy as np, sys, os, subprocess, glob
from PIL import Image
REPO = '/home/user/ComputerINTEGRATE'
SP = '/tmp/claude-0/-home-user-ComputerINTEGRATE/746bcd46-4034-5506-ab6a-1cf4e2b6e837/scratchpad'
os.makedirs(SP + '/ocr2', exist_ok=True)
os.makedirs(SP + '/clean2', exist_ok=True)
FILES = sorted(glob.glob(REPO + '/*-compress.pdf'))


def locate(gp):
    for f in FILES:
        a, b = os.path.basename(f).split('-')[:2]
        a = int(a); b = int(b)
        if a <= gp <= b:
            return f, gp - a


def tess(arr, name, psm='6'):
    png = f'{SP}/clean2/{name}.png'
    Image.fromarray(arr).save(png)
    return subprocess.run(['tesseract', png, '-', '--psm', psm],
                          capture_output=True, text=True).stdout


def run(gp):
    out = f'{SP}/ocr2/p{gp:03d}.txt'
    if os.path.exists(out):
        return
    f, i = locate(gp)
    d = pymupdf.open(f)
    pix = d[i].get_pixmap(dpi=240)
    a = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
    r = a[:, :, 0]
    im = np.where(r < 150, 0, 255).astype(np.uint8)
    H, W = im.shape
    y0, y1 = int(H * 0.165), int(H * 0.86)
    body = im[y0:y1]
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
    g = lo + (best[0] + best[1]) // 2
    L = tess(body[:, :g], f'p{gp:03d}L')
    Rr = tess(body[:, g:], f'p{gp:03d}R')
    top = tess(im[int(H * 0.09):y0 + int(H * 0.02)], f'p{gp:03d}T', '6')
    open(out, 'w').write('=====TOP\n' + top + '\n=====LEFT\n' + L + '\n=====RIGHT\n' + Rr)


if __name__ == '__main__':
    k = int(sys.argv[1]); n = int(sys.argv[2])
    for gp in range(1, 466):
        if gp % n == k:
            run(gp)
            print(gp, flush=True)
