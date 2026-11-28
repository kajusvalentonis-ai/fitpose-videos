# FitPose ad videos — how to make and post them

Short vertical ads (1080×1920, 30 fps, 10–12 s) for FitPose (fitpose-2.vercel.app), a web app that checks lifting form from a phone video. Audience: US fitness beginners. Posted to TikTok + Instagram Reels through Buffer, which pulls each file from
`https://raw.githubusercontent.com/kajusvalentonis-ai/fitpose-videos/main/videos/<file>.mp4` (this repo is public).

## Make a video
- Every video is a scene defined in `tools/ads.html` as `V.<name>={D, beats, sfx, draw(t)}`. `draw(t)` paints frame t on a 1080×1920 canvas.
- Helpers in ads.html: `bg`, `cam` (zoom punch/shake on hit times), `pop` (words popping in), `pill`, `T`, `ring` (score ring), `side`/`squatJ`/`dlJ` + `skel` (side-view lifter + glowing skeleton), `front`/`frontSkel` (front-view squat, `cave` param), `arrow`, `scanLine`, `confetti`, `flash`, `wipe`, `cta(t,t0,'WORD')` (end card), `brand`, `vignette`. `cyc(t+offset, period)` gives squat depth 0..1.
- `sfx` names (tools/audio.py): hit, whoosh, riser, ding, buzz, pop, tick, scan, confetti, slow. A 124 BPM beat is added under them.
- Check frames first: `python3 tools/render.py stills <name> 0.3,3,6,9` → `tools/work/stills/`, then LOOK at them (Read the jpgs). Fix overlaps, cut-off text, empty space.
- Build: `tools/build.sh <name> <NN>` → `videos/<NN>_<name>.mp4` (NN = next number, see LOG.md).

## Rules that make them work (from the Nov 2026 audit)
- The mistake / result must be on screen in the FIRST second (start squats mid-rep with `cyc(t+.7,…)`). Avg watch time was ~4 s.
- 10–12 s total. Bold colors, constant movement, camera punches, before/after, numbers.
- Every video must be NEW: a new concept or a clearly new edit. Never re-post an old file. Each new one should be more colorful, more action, more movement than the last.
- No prices in videos or captions. No fake reviews, user counts or claims. Kind wording about bodies.
- End card: "Link in bio" + "or comment <WORD>".
- Captions: hook line, 1–2 short sentences, "🔗 Link in bio", "💬 Comment WORD for the link", 5 correctly spelled hashtags ending with #fitpose. Check spelling of every hashtag.

## Post schedule (Buffer)
- Organization "My organization" id 6b06e238e6466fe00add13d9. Channels: TikTok "fitpose" 6b06e35b8541f09ecb9d1088, Instagram "fitp.ose" 6b06e6968541f09ecb9d2cc1 (metadata instagram {type:"reel", shouldShareToFeed:true}).
- 2 videos a day. Slots (UTC): 17:30 (12:30 pm New York) and 00:30 (7:30 pm New York). Instagram goes 15 min after TikTok.
- Buffer free plan: max 10 scheduled posts at once.

## LOG.md
Every video made, its concept, file and post dates. Read it before inventing a new concept so nothing repeats.
