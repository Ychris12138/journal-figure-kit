"""Build source and installable-skill ZIPs, excluding local outputs and caches."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT/'skills/journal-matplotlib'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(destination):
    destination = Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    version = (SKILL/'VERSION').read_text().strip()
    files = sorted(p for p in ROOT.rglob('*') if p.is_file()
                   and not set(p.relative_to(ROOT).parts) & {'build', '.git', '__pycache__', '.venv', '.mplconfig'}
                   and p.suffix != '.pyc' and destination not in p.parents)
    for path in files:
        if path.is_symlink():
            raise ValueError(f'Package source must not be a symlink: {path}')
    manifest = {p.relative_to(ROOT).as_posix(): digest(p) for p in files}
    packages = []
    for name, selected, prefix, base in (
        (f'journal-figure-kit-{version}-source.zip', files, f'journal-figure-kit-{version}', ROOT),
        (f'journal-figure-kit-{version}-skill.zip', [p for p in files if SKILL in p.parents], 'journal-matplotlib', SKILL),
    ):
        target = destination/name
        with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as archive:
            for path in selected:
                archive.write(path, prefix+'/'+path.relative_to(base).as_posix())
        with zipfile.ZipFile(target) as archive:
            assert archive.testzip() is None
            assert len(archive.namelist()) == len(selected)
        packages.append({'name': name, 'sha256': digest(target), 'files': len(selected), 'bytes': target.stat().st_size})
    for name in ('install.py', 'install.ps1', 'install.sh'):
        installer = destination/name
        shutil.copyfile(ROOT/name, installer)
        packages.append({'name': installer.name, 'sha256': digest(installer), 'files': 1, 'bytes': installer.stat().st_size})
    (destination/'file-manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (destination/'SHA256SUMS.txt').write_text(''.join(f"{item['sha256']}  {item['name']}\n" for item in packages), encoding='ascii')
    (destination/'packages.json').write_text(json.dumps(packages, indent=2), encoding='utf-8')
    print(json.dumps(packages, indent=2))
    return manifest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default=str(ROOT/'build/dist'))
    build(parser.parse_args().output)
