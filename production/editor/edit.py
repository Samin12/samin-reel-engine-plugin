#!/usr/bin/env python3
"""Build and render local Samin A-roll edits; no HeyGen cloud-render API jobs.

python3 edit.py build --spec timeline.json --project /path/to/composition
python3 edit.py render --project /path/to/composition --output /path/to/pilot.mp4
"""
import argparse
import html
import json
import math
import os
from pathlib import Path
import shutil
import struct
import subprocess
import wave
from motion_scenes import scene_markup, CSS as MOTION_CSS
from editorial_scenes import artifact_markup, CSS as ARTIFACT_CSS

HERE = Path(__file__).resolve().parent


def probe(path):
    command = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)]
    return json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)


def escape(value):
    return html.escape(str(value), quote=True)


def resolve(value, base):
    path = Path(value).expanduser()
    return (base / path).resolve() if not path.is_absolute() else path.resolve()


def finite_number(value, label):
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{label} must be finite")
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def validate_music(sound, spec_path, project, duration, index):
    path = resolve(sound.get("path"), spec_path.parent)
    if not path.is_file() or not path.stat().st_size:
        raise ValueError(f"music {index} missing or empty: {path}")
    start = finite_number(sound.get("start", 0), f"music {index} start")
    end = finite_number(sound.get("end", duration), f"music {index} end")
    source_start = finite_number(sound.get("source_start", 0), f"music {index} source_start")
    gain = finite_number(sound.get("gain", 1), f"music {index} gain")
    if start < 0 or end <= start or end > duration + 0.0001:
        raise ValueError(f"music {index} timeline bounds are invalid")
    if source_start < 0 or gain < 0 or gain > 1:
        raise ValueError(f"music {index} source_start/gain are invalid")
    info = probe(path)
    if not any(stream.get("codec_type") == "audio" for stream in info.get("streams", [])):
        raise ValueError(f"music {index} has no audio stream")
    source_duration = finite_number(info["format"]["duration"], f"music {index} duration")
    clip_duration = end - start
    if source_start + clip_duration > source_duration + 0.05:
        raise ValueError(f"music {index} exceeds source duration")
    envelope = sound.get("envelope")
    if envelope is not None:
        if not isinstance(envelope, list) or not envelope:
            raise ValueError(f"music {index} envelope must be a non-empty list")
        previous = None
        audible = False
        for point_index, point in enumerate(envelope):
            if not isinstance(point, dict):
                raise ValueError(f"music {index} envelope point {point_index} must be an object")
            t = finite_number(point.get("t"), f"music {index} envelope t")
            v = finite_number(point.get("v"), f"music {index} envelope v")
            if t < 0 or t > clip_duration or (previous is not None and t <= previous):
                raise ValueError(f"music {index} envelope times must increase within clip bounds")
            if v < 0 or v > 1:
                raise ValueError(f"music {index} envelope volume must be between 0 and 1")
            previous, audible = t, audible or v > 0
        if not audible:
            raise ValueError(f"music {index} has only zero volume")
    elif gain == 0:
        raise ValueError(f"music {index} has only zero volume")
    return path, start, end, source_start, gain, envelope


def read_words(path):
    data = json.loads(path.read_text())
    if isinstance(data, list):
        return data
    if "words" in data:
        return data["words"]
    return [word for segment in data.get("segments", []) for word in segment.get("words", [])]


def map_words(words, segments):
    result, cursor = [], 0.0
    if any(float(w["start"]) < 0 or float(w["end"]) <= float(w["start"]) for w in words):
        raise ValueError("word timings must have nonnegative starts and end after start")
    words = sorted(words, key=lambda w: float(w["start"]))
    for segment in segments:
        start, end = float(segment["start"]), float(segment["end"])
        for word in words:
            a, b = float(word["start"]), float(word["end"])
            if start <= (a + b) / 2 < end:
                text = str(word.get("word", word.get("text", ""))).strip()
                if text:
                    result.append({**word, "word": text, "start": cursor + max(a, start) - start,
                                   "end": cursor + min(b, end) - start})
        cursor += end - start
    return result


def caption_groups(words, max_words=4, max_chars=27):
    groups, current = [], []
    for word in words:
        gap = current and word["start"] - current[-1]["end"] > 0.35
        too_long = len(" ".join(w["word"] for w in current + [word])) > max_chars
        if current and (len(current) >= max_words or too_long or gap):
            groups.append(current)
            current = []
        current.append(word)
        if word["word"].endswith((".", "?", "!", ":", ";")):
            groups.append(current)
            current = []
    if current:
        groups.append(current)
    return groups


def phrase_groups(words, phrases):
    """Optional reviewed semantic captions, with complete ordered word coverage."""
    groups, cursor = [], 0
    for phrase in phrases:
        start, end = phrase["word_range"]
        if start != cursor or not start < end <= len(words):
            raise ValueError("caption phrases must cover words once, in order")
        breaks = phrase.get("line_breaks", [])
        if breaks != sorted(set(breaks)) or any(not 0 < b < end-start for b in breaks):
            raise ValueError("caption line break is outside its phrase")
        groups.append(words[start:end])
        cursor = end
    if cursor != len(words):
        raise ValueError("caption phrases do not cover the complete transcript")
    return groups


def make_pop(path):
    """Original short synthetic accent, not third-party SFX or generated speech."""
    rate, duration = 48000, 0.16
    with wave.open(str(path), "wb") as out:
        out.setparams((1, 2, rate, 0, "NONE", "not compressed"))
        samples = []
        for n in range(int(rate * duration)):
            t = n / rate
            envelope = (1 - t / duration) ** 3 * min(1, t / 0.003)
            phase = 2 * math.pi * (850 * t - 1800 * t * t)
            samples.append(struct.pack("<h", int(11000 * envelope * math.sin(phase))))
        out.writeframes(b"".join(samples))


def build(spec_path, project):
    spec_path, project = Path(spec_path).resolve(), Path(project).resolve()
    spec = json.loads(spec_path.read_text())
    project.mkdir(parents=True, exist_ok=True)
    assets = project / "assets"
    assets.mkdir(exist_ok=True)
    copied = {}

    def media(value):
        source = resolve(value, spec_path.parent)
        if not source.is_file() or not source.stat().st_size:
            raise ValueError(f"media missing or empty: {source}")
        if source not in copied:
            target = assets / f"media-{len(copied):03}{source.suffix.lower()}"
            if target.exists() and not os.path.samefile(source, target):
                target.unlink()
            if not target.exists():
                try:
                    os.link(source, target)
                except OSError:
                    shutil.copy2(source, target)
            copied[source] = target.relative_to(project).as_posix()
        return copied[source]

    source_path = resolve(spec["source"]["path"], spec_path.parent)
    source_info = probe(source_path)
    source_duration = float(source_info["format"]["duration"])
    segments = spec["source"].get("segments") or [{"start": 0, "end": source_duration}]
    for segment in segments:
        if not 0 <= float(segment["start"]) < float(segment["end"]) <= source_duration + 0.05:
            raise ValueError("source segment lies outside the source video")
    duration = sum(float(s["end"]) - float(s["start"]) for s in segments)
    music = spec.get("music", [])
    music_required = bool(spec.get("audio_policy", {}).get("music_required", False))
    if music_required and not music:
        raise ValueError("audio_policy.music_required=true but music is missing")
    output = spec.get("output", {})
    width, height, fps = int(output.get("width", 1080)), int(output.get("height", 1920)), int(output.get("fps", 30))
    split_fraction = float(output.get("split_fraction", 0.5))
    if not 0.25 <= split_fraction <= 0.75:
        raise ValueError("split_fraction must leave room for both visual and presenter")
    split_height = round(height * split_fraction)
    captions = spec.get("captions", {})
    font_size = float(captions.get("font_size", width * 0.08))
    accent = captions.get("accent", "#D4A1F7")
    position = spec["source"].get("object_position", "50% 40%")
    font_name = captions.get("font_family", "Arial Black")
    font_css = ""
    if captions.get("font_path"):
        font_name = "SaminCaption"
        font_css = f"@font-face{{font-family:'SaminCaption';src:url('{media(captions['font_path'])}');font-weight:900;}}"
    gsap = HERE / "node_modules/gsap/dist/gsap.min.js"
    if not gsap.is_file():
        raise ValueError("run npm ci in production/editor before building")
    shutil.copy2(gsap, assets / "gsap.min.js")
    parts, animations, audio, cursor = [], [], [], 0.0
    source = media(str(source_path))
    has_audio = any(stream.get("codec_type") == "audio" for stream in source_info["streams"])
    for i, segment in enumerate(segments):
        length = float(segment["end"]) - float(segment["start"])
        timing = f'data-start="{cursor:.6f}" data-duration="{length:.6f}" data-media-start="{segment["start"]}"'
        parts.append(f'<video id="aroll-{i}" class="aroll clip" src="{source}" {timing} data-track-index="0" muted playsinline></video>')
        if has_audio:
            audio.append(f'<audio id="voice-{i}" src="{source}" {timing} data-track-index="10" data-volume="1"></audio>')
        cursor += length
    parts = ['<div id="presenter"><div id="presenter-camera" data-layout-allow-overflow>', *parts, '</div></div>']
    shots = spec.get("shots", [])
    for i, shot in enumerate(shots):
        start, end = float(shot["start"]), float(shot["end"])
        if not 0 <= start < end <= duration + 0.05:
            raise ValueError(f"shot {i} lies outside output timeline")
        layout = shot.get("layout", "presenter")
        if layout not in {"split", "full_broll", "presenter"}:
            raise ValueError(f"unknown shot layout: {layout}")
        split = layout == "split"
        animations.append(f'tl.set("#presenter",{{top:{split_height if split else 0},height:{height-split_height if split else height}}},{start});')
        animations.append(f'tl.set("#caption-anchor",{{top:"{shot.get("caption_y",44 if split else 60)}%"}},{start});')
        backing = captions.get("background", "rgba(0,0,0,0)")
        animations.append(f'tl.set(".caption-text",{{backgroundColor:"{backing}"}},{start});')
        animations.append(f'tl.set("#presenter-camera",{{scale:{shot.get("zoom",1)},xPercent:{shot.get("x_percent",0)},yPercent:{shot.get("y_percent",0)}}},{start});')
        if layout == "presenter":
            continue
        rect = f'width:{width}px;height:{split_height if split else height}px;'
        timing = f'data-start="{start}" data-duration="{end-start}" data-track-index="2"'
        if shot.get("media"):
            path = media(shot["media"])
            image = Path(path).suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".svg", ".avif"}
            tag = "img" if image else "video"
            extra = '' if image else f' muted playsinline data-media-start="{shot.get("source_start",0)}"'
            media_style = f'{rect}object-fit:{escape(shot.get("fit","contain"))};object-position:{escape(shot.get("object_position","50% 50%"))};background:{escape(shot.get("background","#111"))};'
            if shot.get("media_crop"):
                x, y, cw, ch = map(float, shot["media_crop"])
                info = next(s for s in probe(project/path)["streams"] if s.get("codec_type") == "video")
                iw, ih = info["width"], info["height"]
                if min(x,y)<0 or min(cw,ch)<=0 or x+cw>iw or y+ch>ih:
                    raise ValueError(f"shot {i} crop is outside source pixels")
                scale = min(width/cw, (split_height if split else height)/ch)
                left = (width-cw*scale)/2-x*scale
                top = ((split_height if split else height)-ch*scale)/2-y*scale
                media_style = f'width:{iw*scale}px;height:{ih*scale}px;left:{left}px;top:{top}px;max-width:none;clip-path:inset({y*scale}px {(iw-x-cw)*scale}px {(ih-y-ch)*scale}px {x*scale}px);'
            # Native video composition may not paint the element's CSS background
            # behind contain-fit media. A timed canvas-sized fill keeps portrait
            # phone inserts from exposing strips of the presenter at their sides.
            parts.append(f'<div id="broll-fill-{i}" class="clip" data-start="{start}" data-duration="{end-start}" data-track-index="1" style="position:absolute;left:0;top:0;z-index:2;{rect}background:{escape(shot.get("background","#111"))};"></div>')
            parts.append(f'<div class="broll-viewport" style="{rect}"><div id="broll-camera-{i}" class="broll-camera" data-layout-allow-overflow><{tag} id="broll-{i}" class="broll clip" src="{path}" {timing}{extra} style="{media_style}"></{tag}></div></div>')
            if shot.get("media_zoom") and not shot.get("media_motion"):
                animations.append(f'tl.fromTo("#broll-camera-{i}",{{scale:1}},{{scale:{float(shot["media_zoom"])},duration:{end-start},ease:"none"}},{start});')
            motion = shot.get("media_motion")
            if motion is not None:
                if not isinstance(motion, dict) or not isinstance(motion.get("from"), dict) or not isinstance(motion.get("to"), dict):
                    raise ValueError(f"shot {i} media_motion needs from/to objects")
                def motion_values(state, label):
                    return {"scale": finite_number(state.get("scale", 1), f"shot {i} media_motion {label}.scale"),
                            "xPercent": finite_number(state.get("x_percent", 0), f"shot {i} media_motion {label}.x_percent"),
                            "yPercent": finite_number(state.get("y_percent", 0), f"shot {i} media_motion {label}.y_percent")}
                motion_from = motion_values(motion["from"], "from")
                motion_to = motion_values(motion["to"], "to")
                animations.append(f'tl.fromTo("#broll-camera-{i}",{json.dumps(motion_from,separators=(",",":"))},{json.dumps({**motion_to,"duration":end-start,"ease":"none"},separators=(",",":"))},{start});')
        elif shot.get("scene"):
            maker = artifact_markup if shot["scene"].get("kind") == "artifact_preview" else scene_markup
            scene, motion = maker(shot["scene"], f'motion-{i}', start, end, width, split_height if split else height)
            parts.append(scene)
            animations.extend(motion)
        elif shot.get("graphic"):
            graphic = shot["graphic"]
            cards = ''.join(f'<div class="role" id="role-{i}-{j}"><strong>{escape(c.get("label",""))}</strong><span>{escape(c.get("text",""))}</span></div>' for j,c in enumerate(graphic.get("cards",[])))
            parts.append(f'<section id="graphic-{i}" class="graphic clip" {timing} style="{rect}"><div class="graphic-inner"><p class="eyebrow">{escape(graphic.get("eyebrow","CONCEPTUAL ILLUSTRATION"))}</p><h1>{escape(graphic.get("title",""))}</h1><div class="roles">{cards}</div><p class="footer">{escape(graphic.get("footer",""))}</p></div></section>')
            animations.append(f'tl.fromTo("#graphic-{i} .role",{{y:18,opacity:0}},{{y:0,opacity:1,duration:0.22,stagger:0.08,ease:"power2.out"}},{start});')
        else:
            raise ValueError(f"shot {i} needs media or graphic for {layout}")
    for zoom in spec.get("zooms", []):
        animations.append(f'tl.to("#presenter-camera",{{scale:{float(zoom["scale"])},duration:{float(zoom.get("duration",0.16))},ease:"power2.out"}},{float(zoom["at"])});')
    words = map_words(read_words(resolve(spec["words_path"], spec_path.parent)), segments) if spec.get("words_path") else []
    phrases = captions.get("phrases", [])
    groups = phrase_groups(words, phrases) if phrases else caption_groups(words, int(captions.get("max_words",4)), int(captions.get("max_chars",27)))
    emphasis = {w.lower().strip(".,!?:;") for w in captions.get("emphasis", [])}
    parts.append('<div id="caption-anchor">')
    for i, group in enumerate(groups):
        start = group[0]["start"]
        next_start = groups[i+1][0]["start"] if i+1<len(groups) else duration
        end = min(next_start, group[-1]["end"] + float(captions.get("hold",0.12)))
        phrase = phrases[i] if phrases else {}
        breaks = [0, *phrase.get("line_breaks", []), len(group)]
        lines = []
        for j, (a, b) in enumerate(zip(breaks, breaks[1:])):
            connector = j == 0 and phrase.get("lead_in", False)
            spans = []
            for word in group[a:b]:
                text = word["word"].strip(".,!?:;") if captions.get("omit_terminal_punctuation", False) else word["word"]
                emphasized = word.get("emphasis") or text.lower().strip(".,!?:;") in emphasis
                text = text.upper() if captions.get("uppercase",True) and not connector else text
                spans.append(f'<span class="{"emphasis" if emphasized else "word"}">{escape(text)}</span>')
            line_id = f'caption-{i}-line-{j}'
            lines.append(f'<span id="{line_id}" class="caption-line {"connector" if connector else ""}">{" ".join(spans)}</span>')
            if j and phrase.get("progressive", True):
                animations.append(f'tl.fromTo("#{line_id}",{{opacity:0,y:6}},{{opacity:1,y:0,duration:0.07,ease:"power2.out"}},{group[a]["start"]});')
        parts.append(f'<div id="caption-{i}" class="caption clip" data-start="{start}" data-duration="{max(.01,end-start)}" data-track-index="5"><div class="caption-text">{"".join(lines)}</div></div>')
        animations.append(f'tl.fromTo("#caption-{i} .caption-text",{{scale:0.97}},{{scale:1,duration:0.07,ease:"power2.out"}},{start});')
    parts.append('</div>')
    for i, flash in enumerate(spec.get("flashes", [])):
        at, length = float(flash["at"]), float(flash.get("duration", .16))
        peak = min(.22, max(0, float(flash.get("opacity", .14))))
        color = escape(flash.get("color", "#D4A1F7"))
        parts.append(f'<div id="light-leak-clip-{i}" class="clip" data-start="{at}" data-duration="{length}" data-track-index="7" style="position:absolute;inset:0;z-index:7;pointer-events:none;"><div id="light-leak-{i}" style="position:absolute;inset:0;opacity:0;background:radial-gradient(ellipse at 95% 30%,{color},transparent 70%);"></div></div>')
        animations.append(f'tl.fromTo("#light-leak-{i}",{{opacity:0}},{{opacity:{peak},duration:{length*.3}}},{at});tl.to("#light-leak-{i}",{{opacity:0,duration:{length*.7}}},{at+length*.3});tl.set("#light-leak-{i}",{{opacity:0}},{at+length});')
    sound_tracks = {}
    for i, sound in enumerate(spec.get("sfx", [])):
        if sound.get("kind") == "soft_pop":
            target = assets / "soft-pop.wav"
            make_pop(target)
            path, length = target.relative_to(project).as_posix(), 0.16
        else:
            path = media(sound["path"])
            length = float(sound.get("duration", probe(project/path)["format"]["duration"]))
        track = sound_tracks.setdefault(path, 12 + len(sound_tracks))
        audio.append(f'<audio id="sfx-{i}" src="{path}" data-start="{sound["at"]}" data-duration="{length}" data-track-index="{track}" data-volume="{sound.get("gain",0.15)}"></audio>')
    for i, sound in enumerate(music):
        path, start, end, source_start, gain, envelope = validate_music(sound, spec_path, project, duration, i)
        relative = media(str(path))
        timing = f'data-start="{start:.6f}" data-duration="{end-start:.6f}" data-media-start="{source_start:.6f}" data-track-index="{11+i}" data-volume="{gain:.6f}"'
        automation = ""
        if envelope is not None:
            payload = {"version": 1, "lanes": [{"target": "volume", "points": [{"t": float(point["t"]), "v": float(point["v"])} for point in envelope]}]}
            automation = f' data-automation="{escape(json.dumps(payload, separators=(",", ":")))}"'
        audio.append(f'<audio id="music-{i}" src="{relative}" {timing}{automation}></audio>')
    for i, label in enumerate(spec.get("labels", [])):
        parts.append(f'<div id="label-{i}" class="editor-label clip" data-start="{label["start"]}" data-duration="{label["end"]-label["start"]}" data-track-index="6" style="top:{float(label.get("y",4))}%;left:{float(label.get("x",5))}%;">{escape(label["text"])}</div>')
    css = f'''{font_css}{MOTION_CSS}{ARTIFACT_CSS}
    *{{box-sizing:border-box}} body{{margin:0;background:#111}} #root{{position:relative;width:{width}px;height:{height}px;overflow:hidden;background:#111}}
    #presenter{{position:absolute;inset:0;width:{width}px;height:{height}px;overflow:hidden}} #presenter-camera{{position:relative;width:100%;height:100%;transform-origin:50% 38%}}
    .aroll{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{position}}} .broll,.graphic{{position:absolute;left:0;top:0;z-index:2}}
    .broll-viewport{{position:absolute;left:0;top:0;z-index:2;overflow:hidden}} .broll-camera{{position:relative;width:100%;height:100%;transform-origin:center}}
    #caption-anchor{{position:absolute;top:62%;left:0;width:100%;z-index:8}} .caption{{position:absolute;left:5%;width:90%;text-align:center}}
    .caption-text{{display:inline-block;max-width:100%;border-radius:.16em;padding:.07em .12em;font-family:"{font_name}",Arial,sans-serif;font-weight:900;font-size:{font_size}px;line-height:1.06;letter-spacing:-0.02em;color:white;-webkit-text-stroke:{width*.0035}px #222;paint-order:stroke fill;text-shadow:0 {width*.003}px {width*.004}px #111;}}
    .caption-line{{display:block}} .caption-line.connector{{font-family:Arial,sans-serif;font-size:.72em;font-weight:500;line-height:1.18;letter-spacing:0;-webkit-text-stroke:{width*.0017}px #222;}}
    .emphasis{{color:{accent}}} .graphic{{background:#efede8;color:#171719;font-family:Arial,sans-serif}}
    .editor-label{{position:absolute;z-index:8;font:700 30px Arial,sans-serif;letter-spacing:.08em;color:#fff;background:#1d1c20;padding:12px 18px;border-radius:6px;}}
    .graphic-inner{{position:absolute;inset:9% 8%;display:flex;flex-direction:column;justify-content:center;gap:{width*.02}px}} .eyebrow{{font-size:{width*.017}px;letter-spacing:.13em;font-weight:800;color:#706476;margin:0}}
    h1{{font-size:{width*.065}px;line-height:1.04;margin:0;letter-spacing:-.055em;font-weight:900}} .roles{{display:grid;grid-template-columns:1fr 1fr;gap:{width*.025}px}}
    .role{{background:#fff;border:2px solid #d4d0d9;border-radius:{width*.023}px;padding:{width*.022}px;display:flex;flex-direction:column;gap:{width*.012}px}} .role strong{{font-size:{width*.032}px;letter-spacing:-.03em}} .role span{{font-size:{width*.022}px;line-height:1.24;color:#57525e}} .footer{{font-size:{width*.022}px;color:#514757;margin:0;line-height:1.3}}
    '''
    markup = f'<!doctype html><html><head><meta charset="utf-8"><title>{escape(spec.get("title","Samin reel edit"))}</title><script src="assets/gsap.min.js"></script><style>{css}</style></head><body><div id="root" data-composition-id="main" data-width="{width}" data-height="{height}" data-duration="{duration}" data-fps="{fps}">{"".join(parts+audio)}</div><script>const tl=gsap.timeline({{paused:true}});{"".join(animations)}window.__timelines.main=tl;</script></body></html>'
    (project/"index.html").write_text(markup)
    (project/"timeline.json").write_text(json.dumps(spec,indent=2)+"\n")
    (project/"mapped-words.json").write_text(json.dumps(words,indent=2)+"\n")
    receipt = {"project":str(project),"duration":duration,"width":width,"height":height,"fps":fps,"words":len(words),"caption_groups":len(groups),"shots":len(shots),"original_audio_preserved":has_audio,"music_count":len(music),"music_required":music_required,"media_transfer":"local hardlink or copy; no upload","rendered":False}
    (project/"build-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n")
    return receipt


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("command",choices=["build","render"])
    ap.add_argument("--spec")
    ap.add_argument("--project",required=True)
    ap.add_argument("--output")
    ap.add_argument("--quality",choices=["draft","standard","high"],default="standard")
    ap.add_argument("--workers",type=int,default=1)
    args=ap.parse_args()
    if args.command=="build":
        if not args.spec: ap.error("build requires --spec")
        print(json.dumps(build(args.spec,args.project),indent=2))
    else:
        if not args.output: ap.error("render requires --output")
        command=[str(HERE/"node_modules/.bin/hyperframes"),"render",str(Path(args.project).resolve()),"--output",str(Path(args.output).resolve()),"--quality",args.quality,"--workers",str(args.workers),"--no-best-effort","--strict"]
        subprocess.run(command,check=True)
        result=probe(Path(args.output))
        (Path(args.project)/"render-receipt.json").write_text(json.dumps(result,indent=2)+"\n")
        print(json.dumps({"output":str(Path(args.output).resolve()),"duration":result["format"]["duration"],"bytes":Path(args.output).stat().st_size}))


if __name__=="__main__":
    main()
