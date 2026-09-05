"""Short previews of actual giveaway files, never fabricated product output."""
import html
import json


def artifact_markup(scene, ident, start, end, width, height):
    esc = lambda text: html.escape(str(text), quote=True)
    files = scene['files']
    active = int(scene.get('active', 0))
    rows = ''.join(f'<div class="artifact-row {"active" if i == active else ""}"><span class="file-icon"></span>{esc(name)}</div>' for i, name in enumerate(files))
    excerpt = scene['excerpt']
    markup = f'''<section id="{ident}" class="artifact clip" data-start="{start}" data-duration="{end-start}" data-track-index="2" style="width:{width}px;height:{height}px;">
      <div class="artifact-heading">{esc(scene.get('heading', 'COUNCIL PROMPT PACK'))}</div>
      <div class="artifact-window"><div class="artifact-files">{rows}</div><div class="artifact-page">
      <div class="artifact-filename">{esc(files[active])}</div><div id="{ident}-quote" class="artifact-quote">{esc(excerpt)}</div>
      </div></div><div class="artifact-footer">{esc(scene.get('footer', 'Excerpt from the downloadable files'))}</div></section>'''
    # Reveals the exact excerpt in chunks; no generated reply or simulated success state.
    chunks = scene.get('reveals', [excerpt])
    states = [{'t': start + .2 + i * .38, 'text': text} for i, text in enumerate(chunks)]
    var = ident.replace('-', '_')
    animation = f'''const {var}_states={json.dumps(states)};const {var}_clock={{t:{start}}};tl.to({var}_clock,{{t:{end},duration:{end-start},ease:'none',onUpdate:()=>{{let value='';for(const state of {var}_states){{if({var}_clock.t>=state.t)value=state.text;}}document.getElementById('{ident}-quote').textContent=value;}}}},{start});'''
    return markup, [animation]


CSS = '''
.artifact{position:absolute;left:0;top:0;z-index:2;background:#e9e6df;color:#252420;font-family:Arial,sans-serif;overflow:hidden;padding:60px 48px 80px}
.artifact-heading{font-size:30px;letter-spacing:.12em;font-weight:800;margin-bottom:32px}
.artifact-window{display:flex;height:600px;background:#faf9f5;border:2px solid #c9c5bc;border-radius:18px;overflow:hidden;box-shadow:0 20px 45px #27231e22}
.artifact-files{width:390px;flex-shrink:0;padding:22px 12px;background:#ddd9d0;border-right:2px solid #c9c5bc}
.artifact-row{font-size:26px;line-height:1.2;padding:20px 10px;display:flex;gap:12px;align-items:center;border-radius:6px}
.artifact-row.active{background:#bcb3c6;color:#1c1720}
.file-icon{width:17px;height:22px;background:#faf9f5;border:1px solid #6f6876;display:inline-block;flex-shrink:0}
.artifact-page{padding:32px 28px;min-width:0;display:flex;flex-direction:column;gap:35px}
.artifact-filename{font:22px Menlo,monospace;color:#696259;padding-bottom:24px;border-bottom:2px solid #d1cbc2}
.artifact-quote{font-size:46px;line-height:1.16;font-weight:700;letter-spacing:-.025em}
.artifact-footer{font-size:26px;margin-top:24px;color:#696259}
'''
