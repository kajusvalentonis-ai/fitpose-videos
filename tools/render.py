"""Render a video defined in ads.html (window.V[name]).
Usage:
  python3 render.py stills <name> 0.5,3,7    -> WORK/stills/<name>_<t>.jpg  (check frames)
  python3 render.py video  <name>            -> WORK/out/<name>_v.mp4       (silent video)
WORK defaults to ./work next to this file (env WORK overrides).
"""
import sys, base64, subprocess, os, asyncio
from playwright.async_api import async_playwright

HERE = os.path.dirname(os.path.abspath(__file__))
HTML = 'file://' + os.path.join(HERE, 'ads.html')
WORK = os.environ.get('WORK', os.path.join(HERE, 'work'))


async def main():
    mode, name = sys.argv[1], sys.argv[2]
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width': 1080, 'height': 1920})
        errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(HTML)
        await pg.evaluate('window.ready')
        grab = "(()=>{{render('{n}',{t});return document.getElementById('c').toDataURL('image/jpeg',{q})}})()"
        if mode == 'stills':
            os.makedirs(f'{WORK}/stills', exist_ok=True)
            for t in [float(x) for x in sys.argv[3].split(',')]:
                url = await pg.evaluate(grab.format(n=name, t=t, q=.85))
                open(f'{WORK}/stills/{name}_{t:05.2f}.jpg', 'wb').write(base64.b64decode(url.split(',')[1]))
        else:
            D = await pg.evaluate(f"V['{name}'].D")
            os.makedirs(f'{WORK}/out', exist_ok=True)
            tmp = f'{WORK}/out/{name}.tmp.mp4'
            ff = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-',
                                   '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp],
                                  stdin=subprocess.PIPE)
            for i in range(int(round(D * 30))):
                url = await pg.evaluate(grab.format(n=name, t=i / 30, q=.93))
                ff.stdin.write(base64.b64decode(url.split(',')[1]))
            ff.stdin.close()
            if ff.wait() == 0:
                os.replace(tmp, f'{WORK}/out/{name}_v.mp4')
        print('page errors:', errs[:5])
        await b.close()

asyncio.run(main())
