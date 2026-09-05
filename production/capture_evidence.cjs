#!/usr/bin/env node
'use strict';

// Public pages only. Each run uses a new temporary Chrome profile; no cookies,
// authentication headers, extensions, existing profiles, or page-content edits.
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const { createRequire } = require('node:module');

const help = `Capture public source evidence with isolated Chrome.

Usage: node production/capture_evidence.cjs --sources sources.json --out directory
       node production/capture_evidence.cjs --help

Input: [{"id":"unique-slug","url":"https://public.example/page","heading":"Optional heading"}]
       {"sources":[...]} is also accepted. Multiple targets use "headings":["One","Two"].

Options:
  --sources FILE  JSON source list (public HTTP(S), no credentials or secret queries)
  --out DIR       New/empty output directory; existing captures are never overwritten
  --chrome FILE   Optional Chrome executable; never a browser profile or connection
  --help          Show this help without loading browser dependencies

Saves original overview screenshots, HTML, requested heading crops and manifest.json.
GitHub repository URLs automatically get a README crop when no heading is supplied.
Captures require human visual review; a screenshot is not a verified product result.
Exit: 0 captures completed, 1 input/setup failure, 2 one or more captures incomplete.
`;

function argumentsFrom(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    const key = argv[i];
    if (key === '--help' || key === '-h') return { help: true };
    if (!['--sources', '--out', '--chrome'].includes(key) || !argv[i + 1] || argv[i + 1].startsWith('--')) {
      throw new Error('Invalid arguments; use --help.');
    }
    if (args[key.slice(2)]) throw new Error('Duplicate option; use --help.');
    args[key.slice(2)] = argv[++i];
  }
  if (!args.sources || !args.out) throw new Error('--sources and --out are required.');
  return args;
}

function publicUrl(value) {
  if (typeof value !== 'string') throw new Error('Each source needs a URL string.');
  let url;
  try { url = new URL(value); } catch { throw new Error('Invalid source URL.'); }
  if (!['http:', 'https:'].includes(url.protocol) || url.username || url.password) {
    throw new Error('Only HTTP(S) URLs without embedded credentials are allowed.');
  }
  const sensitive = /(?:token|password|passwd|secret|authorization|api[-_]?key|signature|^sig$|^code$|^key$|^auth$)/i;
  if ([...url.searchParams.keys()].some(key => sensitive.test(key)) || /(?:token|password|secret)=/i.test(url.hash)) {
    throw new Error('Credential-like URL parameters are not allowed.');
  }
  return url.href;
}

function readSources(file) {
  const value = JSON.parse(fs.readFileSync(file, 'utf8'));
  const list = Array.isArray(value) ? value : value.sources;
  if (!Array.isArray(list) || !list.length) throw new Error('Sources must be a nonempty array.');
  const seen = new Set();
  return list.map(source => {
    if (!source || typeof source !== 'object' || Array.isArray(source)) throw new Error('Invalid source entry.');
    if (Object.keys(source).some(key => !['id', 'url', 'heading', 'headings'].includes(key))) {
      throw new Error('Source entries allow only id, url, heading and headings; no authentication fields.');
    }
    if (typeof source.id !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,79}$/.test(source.id) || seen.has(source.id)) {
      throw new Error('Source IDs must be unique safe slugs of at most 80 characters.');
    }
    seen.add(source.id);
    if (source.heading !== undefined && source.headings !== undefined) throw new Error('Choose heading or headings, not both.');
    const headings = source.heading !== undefined ? [source.heading] : (source.headings ?? []);
    if (!Array.isArray(headings) || headings.some(h => typeof h !== 'string' || !h.trim())) {
      throw new Error('Headings must be nonempty strings.');
    }
    return { id: source.id, url: publicUrl(source.url), headings };
  });
}

function browserExecutable(explicit) {
  if (explicit) return path.resolve(explicit);
  return [
    '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
    '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
    process.env.PROGRAMFILES && path.join(process.env.PROGRAMFILES, 'Google/Chrome/Application/chrome.exe')
  ].filter(Boolean).find(file => fs.existsSync(file));
}

function artifact(out, filename, kind, extra = {}) {
  const bytes = fs.readFileSync(path.join(out, filename));
  return { kind, path: filename, bytes: bytes.length, sha256: crypto.createHash('sha256').update(bytes).digest('hex'), ...extra };
}

async function capture(browser, source, out) {
  const record = {
    id: source.id, source_url: source.url, requested_headings: source.headings,
    captured_at: new Date().toISOString(), status: 'failed', artifacts: [], regions: [],
    capture_method: 'isolated headless Chrome; public page; scrolling and screenshots only; no source content altered',
    viewport: { width: 1440, height: 1000, deviceScaleFactor: 2 },
    verification: 'not_visually_reviewed',
    proof_limit: 'Documents the captured public page; does not verify its claims or demonstrate an independent product run.'
  };
  let context;
  try {
    context = await browser.createBrowserContext();
    const page = await context.newPage();
    await page.setViewport(record.viewport);
    await page.setRequestInterception(true);
    page.on('request', request => {
      if (request.isNavigationRequest() && request.frame() === page.mainFrame()) {
        try { publicUrl(request.url()); } catch { void request.abort(); return; }
      }
      void request.continue();
    });
    const response = await page.goto(source.url, { waitUntil: 'domcontentloaded', timeout: 45000 });
    await page.waitForNetworkIdle({ idleTime: 500, timeout: 5000 }).catch(() => {});
    await page.evaluate(() => Promise.race([document.fonts.ready, new Promise(resolve => setTimeout(resolve, 3000))]));
    record.http_status = response?.status() ?? null;
    record.final_url = publicUrl(page.url());
    record.title = await page.title();
    const state = await page.evaluate(() => ({
      text: document.body?.innerText.trim() ?? '',
      hasPassword: [...document.querySelectorAll('input[type="password"]')].some(e => e.getClientRects().length),
      images: [...document.images].filter(e => e.naturalWidth > 100 && e.getClientRects().length).length,
      headings: [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].map(e => e.textContent.trim()).filter(Boolean).slice(0, 100)
    }));
    record.headings_found = state.headings;
    const blockingText = `${record.title}\n${state.text.slice(0, 3000)}`;
    let failure = null;
    if (record.http_status === null || record.http_status >= 400) failure = 'http_error';
    else if (state.hasPassword || /\/(?:login|signin|sign-in)(?:[/?#]|$)/i.test(record.final_url) || /^(?:sign in|log in|login|authentication required)(?:\s|$)/i.test(record.title)) failure = 'login_required';
    else if (/just a moment|verify (?:that )?you are human|checking your browser|enable javascript and cookies to continue|access denied/i.test(blockingText)) failure = 'access_challenge';
    else if (state.text.length < 40 && state.images === 0) failure = 'blank_or_insufficient_content';
    if (failure) { record.failure = failure; return record; }

    const overview = `${source.id}-overview.png`;
    await page.screenshot({ path: path.join(out, overview) });
    record.artifacts.push(artifact(out, overview, 'original_viewport'));
    const html = `${source.id}-source.html`;
    fs.writeFileSync(path.join(out, html), await page.content(), { flag: 'wx' });
    record.artifacts.push(artifact(out, html, 'rendered_page_html'));

    const isGitHub = new URL(record.final_url).hostname === 'github.com';
    const targets = source.headings.map(heading => ({ heading, mode: 'heading' }));
    if (!targets.length && isGitHub) targets.push({ heading: 'README', mode: 'readme' });
    for (const [index, target] of targets.entries()) {
      const box = await page.evaluate(({ heading, mode }) => {
        const normalize = s => s.replace(/[\u200b-\u200d\ufeff]/g, '').replace(/\s+/g, ' ').trim().toLowerCase();
        const root = mode === 'readme'
          ? document.querySelector('article.markdown-body, #readme .markdown-body, [data-testid="readme"]')
          : [...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].find(e => normalize(e.textContent) === normalize(heading));
        if (!root || !root.getClientRects().length) return null;
        const b = root.getBoundingClientRect();
        const x = Math.max(0, b.x + window.scrollX - 16);
        const y = Math.max(0, b.y + window.scrollY - 24);
        const doc = document.documentElement;
        return { x, y, width: Math.min(doc.scrollWidth - x, Math.max(b.width + 32, 760)), height: Math.min(850, doc.scrollHeight - y) };
      }, target);
      if (!box || box.width < 1 || box.height < 1) {
        record.regions.push({ ...target, status: 'heading_not_found' });
        continue;
      }
      await page.evaluate(y => window.scrollTo(0, Math.max(0, y - 96)), box.y);
      const viewport = `${source.id}-region-${index + 1}-context.png`;
      await page.screenshot({ path: path.join(out, viewport) });
      record.artifacts.push(artifact(out, viewport, 'region_context', { heading: target.heading }));
      const filename = `${source.id}-region-${index + 1}.png`;
      await page.screenshot({ path: path.join(out, filename), clip: box, captureBeyondViewport: true });
      const image = artifact(out, filename, 'unaltered_source_crop', { heading: target.heading, clip_css_pixels: box });
      record.artifacts.push(image);
      record.regions.push({ ...target, status: 'captured_not_visually_reviewed', path: filename });
    }
    record.status = record.regions.some(region => region.status === 'heading_not_found') ? 'partial' : 'captured';
  } catch (error) {
    // Browser error messages can contain complete URLs or response data. Do not log them.
    record.failure = error.name === 'TimeoutError' ? 'navigation_or_capture_timeout' : 'navigation_or_capture_error';
  } finally {
    if (context) await context.close().catch(() => {});
  }
  return record;
}

async function main() {
  const args = argumentsFrom(process.argv.slice(2));
  if (args.help) { process.stdout.write(help); return; }
  const sources = readSources(args.sources);
  const out = path.resolve(args.out);
  if (fs.existsSync(out) && fs.readdirSync(out).length) throw new Error('Output directory must be new or empty.');
  const executablePath = browserExecutable(args.chrome);
  if (!executablePath || !fs.existsSync(executablePath)) throw new Error('Chrome not found; provide --chrome FILE.');
  let puppeteer;
  try { puppeteer = createRequire(path.join(__dirname, 'editor/package.json'))('puppeteer-core'); }
  catch { throw new Error('puppeteer-core is unavailable in production/editor; install that project’s pinned dependencies first.'); }
  fs.mkdirSync(out, { recursive: true });
  const profile = fs.mkdtempSync(path.join(os.tmpdir(), 'reel-public-evidence-'));
  const manifest = { schema_version: 1, started_at: new Date().toISOString(), browser_profile: 'fresh_temporary_no_imported_authentication', sources: [] };
  const save = () => fs.writeFileSync(path.join(out, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n');
  let browser;
  save();
  try {
    browser = await puppeteer.launch({ executablePath, userDataDir: profile, headless: true, args: ['--no-first-run', '--disable-extensions'] });
    manifest.browser_version = await browser.version();
    save();
    for (const source of sources) {
      const record = await capture(browser, source, out);
      manifest.sources.push(record);
      save();
      console.log(JSON.stringify({ id: record.id, status: record.status, failure: record.failure ?? null, artifacts: record.artifacts.length }));
    }
    manifest.finished_at = new Date().toISOString();
    save();
    if (manifest.sources.some(source => source.status !== 'captured')) process.exitCode = 2;
  } catch (error) {
    manifest.failure = browser ? 'capture_run_interrupted' : 'browser_launch_failed';
    manifest.finished_at = new Date().toISOString();
    save();
    throw error;
  } finally {
    try { if (browser) await browser.close(); }
    finally { fs.rmSync(profile, { recursive: true, force: true }); }
  }
}

main().catch(() => {
  // No raw inputs or browser errors in stderr; validation/help explains the contract.
  console.error('Evidence capture failed during input or browser setup. Check --help, input fields, an empty output directory, and Chrome/editor dependencies.');
  process.exitCode = 1;
});
