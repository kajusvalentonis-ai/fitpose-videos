import numpy as np, wave, sys, json, re, os
SR = 44100
rng = np.random.default_rng(1)

def env(n, a=0.002, d=0.2):
    t = np.arange(n) / SR
    return np.minimum(t / a, 1) * np.exp(-t / d)

def kick():
    n = int(.45 * SR); t = np.arange(n) / SR
    f = 45 + 120 * np.exp(-t * 28); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) * 1.0
def clap():
    n = int(.25 * SR); x = rng.standard_normal(n)
    x = np.convolve(x, [1, -0.9], 'same')
    return x * env(n, .001, .06) * .35
def hat():
    n = int(.06 * SR); x = rng.standard_normal(n); x = np.diff(np.r_[0, x])
    return x * env(n, .0005, .015) * .18
def bass(freq, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2*np.pi*freq*t) + .4*np.sin(4*np.pi*freq*t) + .15*np.sign(np.sin(2*np.pi*freq*t))
    return x * env(n, .005, dur*.6) * .28
def whoosh():
    n = int(.5 * SR); x = rng.standard_normal(n); t = np.arange(n)/n
    # moving lowpass via cumulative smoothing
    a = .02 + .3 * np.sin(np.pi * t)
    y = np.zeros(n); s = 0
    for i in range(n): s += a[i] * (x[i] - s); y[i] = s
    return y * np.sin(np.pi * t) ** 2 * 1.6
def riser():
    n = int(.65 * SR); t = np.arange(n)/SR; f = 300 + 1500 * (t/t[-1])**2
    return (np.sin(2*np.pi*np.cumsum(f)/SR)*.15 + rng.standard_normal(n)*.05) * (t/t[-1])**2
def ding():
    n = int(1.0 * SR); t = np.arange(n)/SR
    x = sum(a*np.sin(2*np.pi*f*t) for f, a in [(1318.5, 1), (1975.5, .5), (2637, .25)])
    y = sum(a*np.sin(2*np.pi*f*t) for f, a in [(1760, 1), (2637, .4)])
    out = x * np.exp(-t*5) * .3
    k = int(.09*SR); out[k:] += y[:n-k] * np.exp(-t[:n-k]*4) * .3
    return out
def buzz():
    n = int(.28 * SR); t = np.arange(n)/SR
    x = np.sign(np.sin(2*np.pi*98*t)) + .5*np.sign(np.sin(2*np.pi*103*t))
    return x * env(n, .003, .12) * .22
def pop():
    n = int(.12*SR); t = np.arange(n)/SR; f = 500 + 900*np.exp(-t*40)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * env(n, .001, .03) * .35
def tick():
    n = int(.1*SR); t = np.arange(n)/SR
    return (np.sin(2*np.pi*2000*t) + .5*np.sin(2*np.pi*3000*t)) * env(n, .0005, .02) * .3
def hit():
    k = kick(); n = len(k); x = rng.standard_normal(n) * env(n, .001, .12) * .4
    return k * 1.2 + x
def scan():
    n = int(1.2*SR); t = np.arange(n)/SR
    return np.sin(2*np.pi*(600+400*np.sin(2*np.pi*3*t))*t) * .06 * np.sin(np.pi*t/t[-1])
def confetti():
    n = int(.6*SR); out = np.zeros(n)
    for i in range(14):
        p = pop() * .5; s = int(rng.uniform(0, .45)*SR); out[s:s+len(p)] += p[:n-s] * rng.uniform(.3, 1)
    return out
def slow():
    n = int(.8*SR); t = np.arange(n)/SR; f = 400*np.exp(-t*3)+60
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*3) * .25

FX = dict(whoosh=whoosh, riser=riser, ding=ding, buzz=buzz, pop=pop, tick=tick, hit=hit, scan=scan, confetti=confetti, slow=slow)

def build(D, sfx, bpm=124):
    n = int(D * SR) + SR; mus = np.zeros(n); fx = np.zeros(n)
    def put(buf, x, t, g=1):
        s = int(t*SR)
        if s >= n: return
        e = min(n, s+len(x)); buf[s:e] += x[:e-s] * g
    beat = 60 / bpm; roots = [55, 55, 65.4, 49]  # A, A, C, G
    t = 0; i = 0
    while t < D:
        put(mus, kick(), t, .9)
        if i % 2 == 1: put(mus, clap(), t)
        put(mus, hat(), t + beat/2); put(mus, hat(), t + beat/4, .5); put(mus, hat(), t + 3*beat/4, .5)
        put(mus, bass(roots[(i//4) % 4], beat*.45), t + beat/2)
        t += beat; i += 1
    for name, tt in sfx: put(fx, FX[name](), tt)
    out = mus * .55 + fx * .9
    fade = int(.4*SR); out[int(D*SR)-fade:int(D*SR)] *= np.linspace(1, 0, fade)
    out = out[:int(D*SR)]
    out = np.tanh(out * 1.3) / np.tanh(1.3)
    out = out / np.max(np.abs(out)) * .89
    return out

if __name__ == '__main__':
    name, D, sfx = sys.argv[1], float(sys.argv[2]), json.loads(sys.argv[3])
    a = build(D, sfx)
    st = np.stack([a, a], 1)
    out_dir = os.path.join(os.environ.get('WORK', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'work')), 'out'); os.makedirs(out_dir, exist_ok=True)
    with wave.open(os.path.join(out_dir, f'{name}.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    print('ok', name)
