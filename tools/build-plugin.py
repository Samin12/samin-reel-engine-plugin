#!/usr/bin/env python3
"""Copy maintained stage references into the plugin, preserving authored skills/scripts."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/samin-reel-engine'


def main():
    target = PLUGIN / 'references'
    target.mkdir(parents=True, exist_ok=True)
    receipt = {'source': 'skill/references', 'target': 'plugins/samin-reel-engine/references',
               'runtime': 'Configured local project; resolve with plugin scripts/reel.py context', 'files': []}
    for source in sorted((ROOT / 'skill/references').glob('*.md')):
        content = source.read_text()
        # Project files live in the configured checkout, not alongside the installed cache.
        content = re.sub(r'\[([^\]]+)\]\(\.\./\.\./production/([^\)]+)\)',
                         lambda m: f'{m[1]} (`<project>/production/{m[2]}`)', content)
        output = target / source.name
        output.write_text(content)
        receipt['files'].append({'path': str(output.relative_to(ROOT)),
                                 'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
                                 'packaged_sha256': hashlib.sha256(output.read_bytes()).hexdigest()})
    (PLUGIN / 'reference-build.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({'plugin': str(PLUGIN), 'packaged_references': len(receipt['files'])}))


if __name__ == '__main__':
    main()
