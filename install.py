#!/usr/bin/env python3
"""Install Journal Figure Kit for a chosen agent. Python standard library only."""
from __future__ import annotations
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import http.client
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
import uuid
import venv
import zipfile

VERSION = '0.11.0'
NAME = 'journal-matplotlib'
REPO = 'https://github.com/Ychris12138/journal-figure-kit'
RECEIPT = '.journal-figure-kit-install.json'
AGENTS = {
    'codex': ('.agents/skills', '.agents/skills', '$journal-matplotlib'),
    'claude-code': ('.claude/skills', '.claude/skills', '/journal-matplotlib'),
    'cursor': ('.cursor/skills', '.cursor/skills', '/journal-matplotlib'),
    'gemini': ('.gemini/skills', '.gemini/skills', 'Use the journal-matplotlib skill'),
    'opencode': ('.opencode/skills', '.config/opencode/skills', 'Use the journal-matplotlib skill'),
    'copilot': ('.github/skills', '.copilot/skills', '/journal-matplotlib'),
    'generic': ('.agents/skills', '.agents/skills', 'Read journal-matplotlib/SKILL.md and use it'),
}
MANUAL_FRONTMATTER = {'claude-code', 'cursor', 'copilot'}


def linked(path):
    return path.is_symlink() or getattr(path, 'is_junction', lambda: False)()


def files(root):
    """Do not follow links/junctions while copying or backing up user files."""
    if linked(root):
        raise ValueError(f'Refusing linked directory: {root}')
    for directory, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for name in dirs + names:
            if linked(Path(directory)/name):
                raise ValueError(f'Refusing linked entry: {Path(directory)/name}')
        for name in names:
            p = Path(directory)/name
            if p.suffix != '.pyc':
                yield p


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def destination(agent, scope, project, home, env, dest=None):
    if dest:
        return Path(dest).expanduser().absolute()/NAME
    if scope == 'project':
        return Path(project).absolute()/AGENTS[agent][0]/NAME
    base = Path(home)
    if agent == 'codex':
        # Respect existing installs from Codex's bundled installer, without making
        # another same-named copy in the newer shared directory.
        if env.get('CODEX_HOME'):
            return Path(env['CODEX_HOME']).expanduser().absolute()/'skills'/NAME
        legacy = base/'.codex/skills'/NAME
        if legacy.exists() or linked(legacy):
            return legacy
    return base/AGENTS[agent][1]/NAME


def extract_skill(data, root):
    """Extract only a bounded, regular-file skill tree from the release ZIP."""
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        entries = archive.infolist()
        if len(entries) > 500 or sum(i.file_size for i in entries) > 32*1024*1024:
            raise ValueError('Archive exceeds the skill size limit')
        seen = set()
        for info in entries:
            path = PurePosixPath(info.filename)
            mode = info.external_attr >> 16
            if ('\\' in info.orig_filename or ':' in info.filename or path.is_absolute()
                    or '..' in path.parts or not path.parts or path.parts[0] != NAME
                    or stat.S_IFMT(mode) not in (0, stat.S_IFREG, stat.S_IFDIR)
                    or info.filename.casefold() in seen):
                raise ValueError(f'Unsafe archive member: {info.filename}')
            seen.add(info.filename.casefold())
        for info in entries:
            path = root.joinpath(*PurePosixPath(info.filename).parts)
            if not path.resolve().is_relative_to(root.resolve()):
                raise ValueError('Archive path escapes extraction directory')
            if info.is_dir():
                path.mkdir(parents=True, exist_ok=True)
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(info))
    return root/NAME


def download(url, maximum):
    request = urllib.request.Request(url, headers={'User-Agent': f'JournalFigureKit/{VERSION}'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                result = response.read(maximum+1)
            if len(result) > maximum:
                raise ValueError('Download exceeds size limit')
            return result
        except urllib.error.HTTPError as error:
            if error.code != 429 and not 500 <= error.code < 600:
                raise
            if attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError, http.client.IncompleteRead):
            if attempt == 2:
                raise
        print(f'Download interrupted; retrying ({attempt+2}/3).', file=sys.stderr)
        time.sleep(attempt+1)


@contextmanager
def source_tree(explicit=None):
    # python -c has no __file__; stdin sets it to <stdin>. Neither should
    # accidentally treat an unrelated current-directory skill as its payload.
    script_file = globals().get('__file__')
    local = Path(explicit).expanduser().resolve() if explicit else None
    if local is None and script_file and not str(script_file).startswith('<'):
        local = Path(script_file).resolve().parent/'skills'/NAME
    if explicit or (local is not None and local.is_dir()):
        validate_source(local)
        yield local
        return
    asset = f'journal-figure-kit-{VERSION}-skill.zip'
    base = f'{REPO}/releases/download/v{VERSION}'
    checksums = download(base+'/SHA256SUMS.txt', 65536).decode('ascii')
    matches = [line.split()[0] for line in checksums.splitlines() if len(line.split()) == 2 and line.split()[1] == asset]
    if len(matches) != 1 or not re.fullmatch('[0-9a-f]{64}', matches[0]):
        raise ValueError('Missing or ambiguous release checksum')
    data = download(base+'/'+asset, 8*1024*1024)
    if hashlib.sha256(data).hexdigest() != matches[0]:
        raise ValueError('Release checksum mismatch')
    with tempfile.TemporaryDirectory(prefix='journal-figure-kit-download-') as tmp:
        local = extract_skill(data, Path(tmp))
        validate_source(local)
        yield local


def validate_source(source):
    if not source.is_dir():
        raise ValueError(f'Skill source not found: {source}')
    list(files(source))
    for name in ('SKILL.md', 'VERSION', 'LICENSE', 'requirements.txt', 'agents/openai.yaml', 'scripts/layout_audit.py', 'references/layout-presets.json'):
        if not (source/name).is_file():
            raise ValueError(f'Skill source is incomplete: {name}')
    if (source/'VERSION').read_text().strip() != VERSION:
        raise ValueError('Installer and skill versions differ; use matching release files')


def adapted_skill(text, agent):
    # A local source must be the canonical full skill; discard a stale adapter flag.
    text = re.sub(r'^disable-model-invocation:.*\n', '', text, flags=re.M)
    if agent in MANUAL_FRONTMATTER:
        text = text.replace('---\n', '---\ndisable-model-invocation: true\n', 1)
    return text


def runtime_environment(path, requirements):
    path = Path(path).expanduser().absolute()
    if linked(path):
        raise ValueError('Refusing a linked virtual environment')
    if path.exists() and not (path/'pyvenv.cfg').is_file():
        raise ValueError('Existing --venv path is not a virtual environment')
    if not path.exists():
        venv.EnvBuilder(with_pip=True).create(path)
    python = path/('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    subprocess.run([str(python), '-m', 'pip', 'install', '--disable-pip-version-check', '-r', str(requirements)], check=True)
    # Resolving bin/python would bypass a symlink-based venv on POSIX systems.
    return str(python.absolute())


def preflight(target, update):
    if linked(target):
        raise ValueError(f'Refusing linked target: {target}')
    if target.exists():
        if not target.is_dir():
            raise ValueError(f'Target is not a directory: {target}')
        if not update:
            raise FileExistsError(f'Already installed: {target}. Use --update to back up and replace it.')
        list(files(target))


def install_one(source, target, agent, python=None, update=False):
    preflight(target, update)
    if python is None and (target/'local_runtime.json').is_file():
        python = json.loads((target/'local_runtime.json').read_text(encoding='utf-8')).get('python')
    target.parent.mkdir(parents=True, exist_ok=True)
    parent = target.parent.resolve()
    target = parent/NAME
    if target.resolve().parent != parent:
        raise ValueError('Target escapes its installation directory')
    backup = None
    with tempfile.TemporaryDirectory(prefix='.journal-figure-kit-stage-', dir=parent) as tmp:
        stage = Path(tmp).resolve()
        assert stage.parent == parent
        payload = stage/NAME
        for path in files(source):
            relative = path.relative_to(source)
            if agent not in ('codex', 'generic') and relative.parts[0] == 'agents':
                continue
            dest = payload/relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, dest)
        skill = payload/'SKILL.md'
        skill.write_text(adapted_skill(skill.read_text(encoding='utf-8'), agent), encoding='utf-8', newline='\n')
        if python:
            (payload/'local_runtime.json').write_text(json.dumps({'python': python, 'version': VERSION}, indent=2), encoding='utf-8')
        record = {'schema_version': 1, 'version': VERSION, 'agent': agent,
                  'python': python, 'invocation': AGENTS[agent][2],
                  'files': {p.relative_to(payload).as_posix(): digest(p) for p in files(payload)}}
        (payload/RECEIPT).write_text(json.dumps(record, indent=2), encoding='utf-8')
        # Recheck immediately before mutation; never follow a concurrently added link.
        preflight(target, update)
        if target.exists():
            backup_dir = parent/'.journal-figure-kit-backups'
            if linked(backup_dir):
                raise ValueError('Refusing linked backup directory')
            backup_dir.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            backup = backup_dir/f'{NAME}-{stamp}-{uuid.uuid4().hex[:8]}.zip'
            with zipfile.ZipFile(backup, 'x', zipfile.ZIP_DEFLATED) as archive:
                for path in files(target):
                    archive.write(path, NAME+'/'+path.relative_to(target).as_posix())
            # Both rename endpoints are verified children of the selected parent.
            old = stage/'old'
            assert old.is_relative_to(parent) and target.parent == parent
            target.rename(old)
            try:
                payload.rename(target)
            except BaseException:
                old.rename(target)
                raise
        else:
            payload.rename(target)
    return {'agent': agent, 'target': str(target), 'version': VERSION,
            'backup': str(backup) if backup else None, 'python': python,
            'invoke': AGENTS[agent][2]}


def check_install(target):
    if linked(target):
        raise ValueError('Refusing linked target')
    record = json.loads((target/RECEIPT).read_text(encoding='utf-8'))
    problems = []
    for name, expected in record['files'].items():
        path = target/name
        if not path.resolve().is_relative_to(target.resolve()) or linked(path):
            raise ValueError('Unsafe path in installation receipt')
        if not path.is_file() or digest(path) != expected:
            problems.append(f'Missing or modified: {name}')
    python = record.get('python') or sys.executable
    code = 'import importlib; [importlib.import_module(m) for m in ("matplotlib", "numpy", "PIL", "pypdf", "pymupdf", "colorspacious")]'
    result = subprocess.run([python, '-B', '-c', code], capture_output=True, text=True, timeout=60)
    if result.returncode:
        problems.append('Python dependencies unavailable: '+result.stderr[-1500:])
    return {'target': str(target), 'version': record['version'], 'agent': record['agent'],
            'python': python, 'ok': not problems, 'problems': problems}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', nargs='+', choices=AGENTS)
    parser.add_argument('--list-agents', action='store_true')
    parser.add_argument('--quick', action='store_true', help='Default to Codex, user scope, isolated dependencies and backed-up updates')
    parser.add_argument('--scope', choices=('project', 'user'))
    parser.add_argument('--project', type=Path)
    parser.add_argument('--dest', type=Path, help='Override the skills parent directory; one agent only')
    parser.add_argument('--source', type=Path, help='Local skill folder; otherwise use adjacent repo or pinned GitHub release')
    updates = parser.add_mutually_exclusive_group()
    updates.add_argument('--update', action='store_true', help='Back up the existing skill ZIP before replacing it')
    updates.add_argument('--no-update', action='store_true', help='In quick mode, refuse to replace an existing install')
    dependencies = parser.add_mutually_exclusive_group()
    dependencies.add_argument('--with-deps', action='store_true', help='Create a virtual environment and install plotting dependencies')
    dependencies.add_argument('--no-deps', action='store_true', help='In quick mode, use the existing Python environment')
    parser.add_argument('--venv', type=Path, help='Virtual environment path used with --with-deps')
    parser.add_argument('--dry-run', action='store_true', help='Show paths without writes or downloads')
    parser.add_argument('--check', action='store_true', help='Check installed files and Python dependencies')
    args = parser.parse_args(argv)
    if args.list_agents:
        print(json.dumps(AGENTS, indent=2));return 0
    if (args.no_deps or args.no_update) and not args.quick:
        parser.error('--no-deps and --no-update are quick-mode options')
    if args.quick:
        args.agent = args.agent or ['codex']
        if args.scope is None:
            args.scope = 'project' if args.project is not None else 'user'
        if not args.check:
            args.with_deps = args.with_deps or not args.no_deps
            args.update = args.update or not args.no_update
    args.scope = args.scope or 'project'
    args.project = args.project if args.project is not None else Path.cwd()
    if not args.agent:
        parser.error('--agent is required; use --list-agents')
    if args.dest and len(args.agent) != 1:
        parser.error('--dest requires exactly one agent')
    if args.venv and not args.with_deps:
        parser.error('--venv requires --with-deps')
    if args.check and (args.with_deps or args.update):
        parser.error('--check cannot be combined with --with-deps or --update')
    targets = [(agent, destination(agent, args.scope, args.project, Path.home(), os.environ, args.dest)) for agent in args.agent]
    if len({str(p.resolve()).casefold() for _, p in targets}) != len(targets):
        parser.error('Selected agents resolve to the same destination; install one of them')
    if args.dry_run:
        print(json.dumps([{'agent': a, 'target': str(p), 'version': VERSION, 'with_deps': args.with_deps} for a,p in targets], indent=2));return 0
    if args.check:
        results = [check_install(p) for _,p in targets]
        print(json.dumps(results, indent=2));return 0 if all(r['ok'] for r in results) else 1
    for _, target in targets:
        preflight(target, args.update)
    with source_tree(args.source) as source:
        python = None
        if args.with_deps:
            default_env = Path.home()/'.cache/journal-figure-kit/venvs'/f'{VERSION}-py{sys.version_info.major}.{sys.version_info.minor}'
            python = runtime_environment(args.venv or default_env, source/'requirements.txt')
        results = [install_one(source, p, a, python, args.update) for a,p in targets]
    print(json.dumps(results, indent=2))
    print('Reload skills or start a new agent session. Use --check to verify dependencies.')
    return 0


if __name__ == '__main__':
    if sys.version_info < (3,10):
        raise SystemExit('Python 3.10+ is required; Python 3.12 is the tested target.')
    try:
        raise SystemExit(main())
    except (OSError, ValueError, subprocess.SubprocessError, zipfile.BadZipFile, http.client.HTTPException) as error:
        print(f'Installation failed: {error}', file=sys.stderr)
        raise SystemExit(1)
