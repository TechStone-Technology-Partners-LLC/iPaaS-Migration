"""Package intake: turn an uploaded zip into WebMethods/<PackageName>/ at repo root.

The instruction docs (initiate_migration/Instruction_Workato.md, WebMethods/start.md)
expect packages at WebMethods/<PackageName>/ — landing the extraction there lets the
workflow run unmodified. Zip attachment only (Chat uploads allow up to 200MB; package
zips are a few MB).
"""

import io
import re
import shutil
import tempfile
import zipfile
from pathlib import Path

from .env import REPO_ROOT

WM_DIR = REPO_ROOT / "WebMethods"

# webMethods IS package marker files
_MANIFEST_NAMES = {"manifest.v3", "manifest.rel"}

_SAFE_NAME = re.compile(r"[^A-Za-z0-9_.-]")


class IntakeError(Exception):
    pass


def _find_package_root(extract_dir: Path) -> Path:
    """Locate the directory that IS the package (contains manifest.v3/.rel).

    Handles both zip shapes: the package dir at zip root, or the package
    files directly at zip root.
    """
    for manifest in _MANIFEST_NAMES:
        if (extract_dir / manifest).exists():
            return extract_dir
    hits = [
        p.parent
        for p in extract_dir.rglob("*")
        if p.is_file() and p.name in _MANIFEST_NAMES
    ]
    if not hits:
        raise IntakeError(
            "No webMethods package found in the zip (no manifest.v3 / manifest.rel). "
            "Please zip the package directory exported from webMethods IS."
        )
    # Shallowest hit wins — a package can contain nested manifests in ns/
    return min(hits, key=lambda p: len(p.parts))


def _package_name(zip_name: str, package_root: Path, extract_dir: Path) -> str:
    if package_root != extract_dir:
        name = package_root.name
    else:
        name = Path(zip_name).stem or "UploadedPackage"
    name = _SAFE_NAME.sub("_", name).strip("._") or "UploadedPackage"
    return name


def extract_package(zip_bytes: bytes, zip_name: str = "package.zip") -> tuple[str, Path, bool]:
    """Extract a package zip into WebMethods/<PackageName>/.

    Returns (package_name, package_dir, reused_existing).
    If WebMethods/<PackageName>/ already exists it is reused untouched.
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile as exc:
        raise IntakeError("That file is not a valid zip archive.") from exc

    with tempfile.TemporaryDirectory(prefix="gchat_pkg_") as tmp:
        tmp_dir = Path(tmp)
        for member in zf.namelist():
            # zip-slip guard
            target = (tmp_dir / member).resolve()
            if not str(target).startswith(str(tmp_dir.resolve())):
                raise IntakeError(f"Unsafe path in zip: {member}")
        zf.extractall(tmp_dir)

        package_root = _find_package_root(tmp_dir)
        name = _package_name(zip_name, package_root, tmp_dir)
        dest = WM_DIR / name

        if dest.exists():
            return name, dest, True

        WM_DIR.mkdir(parents=True, exist_ok=True)
        shutil.copytree(package_root, dest)
        return name, dest, False
