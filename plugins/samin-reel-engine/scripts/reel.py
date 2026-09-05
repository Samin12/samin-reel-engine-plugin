#!/usr/bin/env python3
"""Resolve the local reel project and dispatch its real, existing production tools."""
import argparse
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

PLUGIN = Path(__file__).resolve().parents[1]
CONFIG = Path.home() / '.config/samin-reel-engine/project.json'
REQUIRED = ('skill/scripts/pipeline.py',
            'production/editor/edit.py', 'production/check_editorial.py')
COMMANDS = {
    'research': ('python', 'skill/scripts/research.py'),
    'pipeline': ('python', 'skill/scripts/pipeline.py'),
    'script-check': ('python', 'skill/scripts/check_script.py'),
    'intake': ('python', 'production/intake/intake.py'),
    'take': ('python', 'production/prepare_take.py'),
    'retime': ('python', 'production/retime_timeline.py'),
    'capture': ('node', 'production/capture_evidence.cjs'),
    'build': ('python', 'production/editor/edit.py', 'build'),
    'render': ('python', 'production/editor/edit.py', 'render'),
    'finalize': ('python', 'production/finalize_render.py'),
    'check': ('python', 'production/check_editorial.py'),
    'review-player': ('python', 'production/build_review.py'),
    'manychat-prepare': ('python', 'production/delivery/manychat_adapter.py', 'prepare'),
}


def validate_project(value):
    project = Path(value).expanduser().resolve(strict=True)
    missing = [name for name in REQUIRED if not (project / name).is_file()]
    if missing:
        raise ValueError(f'Not a reel-engine checkout; missing {", ".join(missing)}')
    return project


def resolve_project(explicit=None):
    if explicit:
        return validate_project(explicit), 'argument'
    if os.environ.get('SAMIN_REEL_PROJECT'):
        return validate_project(os.environ['SAMIN_REEL_PROJECT']), 'environment'
    if CONFIG.is_file():
        return validate_project(json.loads(CONFIG.read_text())['project_root']), 'local_configuration'
    for parent in PLUGIN.parents:
        if all((parent / name).is_file() for name in REQUIRED):
            return parent, 'source_checkout'
    raise ValueError('Project not configured. Clone/open Samin12/samin-reel-engine-plugin, then run --project PATH configure.')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--project', type=Path, help='Explicit local project checkout; overrides saved configuration')
    sub = ap.add_subparsers(dest='mode', required=True)
    sub.add_parser('context'); sub.add_parser('doctor'); sub.add_parser('configure')
    run = sub.add_parser('run', help='Run one existing project helper; arguments after -- pass through unchanged')
    run.add_argument('action', choices=sorted(COMMANDS))
    run.add_argument('arguments', nargs=argparse.REMAINDER)
    a = ap.parse_args()
    try:
        project, basis = resolve_project(a.project)
        if a.mode == 'run':
            engine, relative, *fixed = COMMANDS[a.action]
            executable = sys.executable if engine == 'python' else shutil.which(engine)
            if not executable:
                raise ValueError(f'{engine} is not installed/on PATH')
            forwarded = a.arguments[1:] if a.arguments[:1] == ['--'] else a.arguments
            if a.action == 'build':
                build_args = argparse.ArgumentParser(add_help=False)
                build_args.add_argument('--spec', required=True, type=Path)
                selected, _ = build_args.parse_known_args(forwarded)
                spec_path = selected.spec if selected.spec.is_absolute() else project / selected.spec
                timeline = json.loads(spec_path.read_text())
                policy = timeline.get('audio_policy', {})
                if not policy.get('user_opt_out'):
                    if policy.get('music_required') is not True or not timeline.get('music'):
                        raise ValueError('Samin reel builds require audio_policy.music_required=true and an actual music track. Only an explicit user opt-out recorded in audio_policy.user_opt_out waives this requirement.')
            return subprocess.run([executable, str(project / relative), *fixed, *forwarded], cwd=project).returncode
        result = {'project_root': str(project), 'project_resolution': basis, 'plugin_root': str(PLUGIN),
                  'read_first': str(PLUGIN / 'references/operator-runbook.md'),
                  'runtime_location': str(project / 'production'), 'voice_location': str(project / 'voice'),
                  'data_policy': 'Keep media, corpus and credentials in the project/local storage, outside plugin cache.'}
        if a.mode == 'configure':
            CONFIG.parent.mkdir(parents=True, exist_ok=True)
            if CONFIG.exists():
                previous = json.loads(CONFIG.read_text())
                if previous.get('project_root') != str(project):
                    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                    shutil.copy2(CONFIG, CONFIG.with_name(f'project.{stamp}.backup.json'))
            temp = CONFIG.with_suffix('.tmp')
            temp.write_text(json.dumps({'project_root': str(project)}, indent=2) + '\n')
            temp.chmod(0o600); os.replace(temp, CONFIG)
            result['configuration_saved'] = str(CONFIG)
        if a.mode == 'doctor':
            result['python_version'] = sys.version.split()[0]
            result['python_311_or_later'] = sys.version_info >= (3, 11)
            result['runtime_helpers_present'] = {name: (project / spec[1]).is_file() for name, spec in COMMANDS.items()}
            result['tools'] = {name: shutil.which(name) is not None for name in
                               ('node', 'ffmpeg', 'ffprobe', 'gh', 'higgsfield', 'multica')}
            result['python_modules'] = {name: importlib.util.find_spec(name) is not None for name in
                                        ('jsonschema', 'whisper', 'numpy', 'scipy', 'soundfile')}
            result['hyperframes_installed'] = (project / 'production/editor/node_modules/.bin/hyperframes').is_file()
            result['whisper_model_cached'] = (Path.home() / '.cache/whisper/base.en.pt').is_file()
            result['authentication'] = 'not_checked; use the relevant provider only when that stage needs it'
            result['core_edit_dependencies_present'] = (all(result['tools'][n] for n in ('node', 'ffmpeg', 'ffprobe'))
                                                         and result['hyperframes_installed'])
        print(json.dumps(result, indent=2))
        return 0
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        ap.error(str(error))


if __name__ == '__main__':
    raise SystemExit(main())
