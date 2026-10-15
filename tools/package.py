from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
PACKAGE = DIST / 'Zomput-Random_Talent'
DIST.mkdir(exist_ok=True)
if PACKAGE.exists():
    assert PACKAGE.resolve().parent == DIST.resolve()
    shutil.rmtree(PACKAGE)
target = PACKAGE / 'Contents/mods/ZomputRandomTalent'
shutil.copytree(ROOT / 'Contents/mods/ZomputRandomTalent', target)
for name in ('preview.png', 'workshop.txt'):
    shutil.copy2(ROOT / name, PACKAGE / name)
with zipfile.ZipFile(DIST / 'Zomput-Random_Talent.zip', 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(target.rglob('*')):
        archive.write(path, path.relative_to(PACKAGE / 'Contents/mods'))
print('Packaged Zomput-Random_Talent.')
