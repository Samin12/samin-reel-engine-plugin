"""Original animated prompt demonstrations; never presented as captured product output."""
import html
import json


def scene_markup(scene, ident, start, end, width, height):
    esc = lambda value: html.escape(str(value), quote=True)
    duration = end - start
    split = height < width
    scale = .72 if split else 1
    pad, font = round(52 * scale), round(43 * scale)
    kind = scene.get('kind', 'typed_prompt')
    blocks = scene.get('blocks', [])
    body = []
    animations = []
    title = esc(scene.get('title', 'Claude Council'))
    tabs = ['Advocate', 'Skeptic', 'Investor', 'Judge']
    selected = scene.get('tab', '')
    nav = ''.join(f'<span style="background:{"#705483" if tab==selected else "#2b292f"};border-radius:12px;padding:12px 18px;">{tab}</span>' for tab in tabs)
    for j, block in enumerate(blocks):
        bid = f'{ident}-block-{j}'
        tid = f'{bid}-text'
        text = block.get('text', '')
        scroll_intent = ' data-layout-allow-overlap' if kind == 'prompt_scroll' else ''
        body.append(f'<div id="{bid}" class="motion-block"><div class="motion-label"{scroll_intent}>{esc(block.get("label", "PROMPT"))}</div><div class="motion-code"><span id="{tid}"{scroll_intent}></span><span class="motion-cursor"{scroll_intent}>▍</span></div></div>')
        appear = start + .10 + j * min(.23, duration / max(3, len(blocks)*2))
        text_duration = min(max(.3, len(text) / 105), max(.25, end-appear-.12))
        if kind == 'prompt_scroll':
            # Actual prompt text stays intact while the viewport moves over it.
            animations.append(f'document.getElementById({json.dumps(tid)}).textContent={json.dumps(text)};')
        else:
            variable = ident.replace('-', '_') + '_chars_' + str(j)
            animations.append(f'const {variable}={{n:0}};tl.to({variable},{{n:{len(text)},duration:{text_duration},ease:"none",onUpdate:()=>{{document.getElementById({json.dumps(tid)}).textContent={json.dumps(text)}.slice(0,Math.floor({variable}.n));}}}},{appear});')
        animations.append(f'tl.fromTo("#{bid}",{{opacity:0,y:32}},{{opacity:1,y:0,duration:.14,ease:"power3.out"}},{appear});')
    inner = ''.join(body)
    grid = ' motion-grid' if scene.get('block_layout') == 'grid' else ''
    top = 0 if split else 84
    bottom = 0 if split else 550
    markup = f'<section id="{ident}" class="motion-screen clip" data-start="{start}" data-duration="{duration}" data-track-index="2" style="width:{width}px;height:{height}px;--motion-pad:{pad}px;--motion-font:{font}px;"><div class="motion-window" style="top:{top}px;bottom:{bottom}px"><div class="motion-toolbar"><i></i><i></i><i></i><span>council.md</span><b>PROMPT DEMO</b></div><div class="motion-content" id="{ident}-camera" data-layout-allow-overflow><div class="motion-kicker">{esc(scene.get("eyebrow", "THE ACTUAL GIVEAWAY PROMPTS"))}</div><h2>{title}</h2><div class="motion-tabs">{nav}</div><div class="motion-scroll-view" data-layout-allow-overflow data-layout-allow-occlusion><div id="{ident}-scroll" class="motion-blocks{grid}">{inner}</div></div><div class="motion-command"><span>›</span> {esc(scene.get("command", "Save the brief. Review one decision."))}</div></div></div></section>'
    if kind == 'prompt_scroll':
        travel = scene.get('scroll_pixels', 300 if split else 640)
        animations.append(f'tl.to("#{ident}-scroll",{{y:-{travel},duration:{max(.25,duration-.3)},ease:"power1.inOut"}},{start+.18});')
    animations.append(f'tl.fromTo("#{ident}-camera",{{scale:1}},{{scale:1.025,duration:{duration},ease:"none"}},{start});')
    return markup, animations


CSS = """
.motion-screen{position:absolute;left:0;top:0;z-index:2;background:#131216;color:#eeeaf1;font-family:Arial,sans-serif;overflow:hidden}
.motion-window{position:absolute;left:0;right:0;border:2px solid #39343f;background:#1c1a20;box-shadow:0 0 90px #9d69c925;overflow:hidden}
.motion-toolbar{height:72px;display:flex;align-items:center;gap:12px;background:#29262e;padding:0 28px;font-size:25px;color:#bcb5c6}.motion-toolbar i{width:14px;height:14px;border-radius:50%;background:#77687e}.motion-toolbar i:first-child{background:#bc7689}.motion-toolbar span{margin-left:22px}.motion-toolbar b{margin-left:auto;letter-spacing:.1em;font-size:22px;color:#d4a1f7}
.motion-content{height:calc(100% - 72px);padding:var(--motion-pad);position:relative;transform-origin:50% 40%;overflow:hidden;display:flex;flex-direction:column}
.motion-kicker{font-size:22px;letter-spacing:.13em;color:#bba7ca;font-weight:700}.motion-content h2{font-size:calc(var(--motion-font)*1.22);line-height:1.07;letter-spacing:-.04em;margin:18px 0 24px;color:#fff}
.motion-tabs{display:flex;gap:10px;font-size:23px;margin-bottom:25px;flex-shrink:0}.motion-scroll-view{position:relative;overflow:hidden;flex:1;min-height:0}.motion-blocks{display:flex;flex-direction:column;gap:22px;}
.motion-block{border:1px solid #4d3f58;border-left:6px solid #d4a1f7;border-radius:14px;background:linear-gradient(120deg,#302637,#242128);padding:22px 24px;min-height:132px;}
.motion-label{color:#d4a1f7;font-size:23px;font-weight:700;letter-spacing:.08em;margin-bottom:14px}.motion-code{font-family:Menlo,monospace;white-space:pre-wrap;font-size:var(--motion-font);line-height:1.32;letter-spacing:-.04em;color:#f2edf5}.motion-cursor{color:#d4a1f7;font-size:.85em}
.motion-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.motion-grid .motion-code{font-size:32px}.motion-grid .motion-label{font-size:22px}.motion-grid .motion-block{padding:20px;min-height:260px}.motion-command{flex-shrink:0;border:2px solid #776186;border-radius:16px;background:#17151b;padding:22px;margin-top:24px;font-size:25px;color:#dbd0e4;line-height:1.2}.motion-command span{color:#d4a1f7;font-weight:bold;font-size:32px}
"""
