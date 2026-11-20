"""
Release Packaging Script for AlphaCouncil.
Packages the clean, production codebase into a release ZIP archive,
strictly excluding internal agent planning files (.gsd), temporary test scripts,
caches, and build artifacts.
"""

import os
import zipfile

REPO_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DESKTOP_DIR = os.path.abspath(os.path.join(REPO_DIR, ".."))
ZIP_DESTINATION = os.path.join(DESKTOP_DIR, "alpha_council_complete_codebase.zip")

EXCLUDE_DIRS = {
    ".git",
    ".gsd",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "alpha_council.egg-info",
}

EXCLUDE_EXTENSIONS = {".pyc", ".pyo", ".zip"}

EXCLUDE_EXACT_FILES = {
    "pack_zip.py",
    "test_tune.py",
    "test_sim.py",
    "test_speed.py",
    "test_25_syms.py",
    "run_30_seeds.py",
    "run_sim_day_index.py",
    "calc_stats.py",
    "update_consolidated.py",
}


def create_release_zip():
    if os.path.exists(ZIP_DESTINATION):
        os.remove(ZIP_DESTINATION)

    file_count = 0
    with zipfile.ZipFile(ZIP_DESTINATION, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(REPO_DIR):
            # Prune directories in-place
            dirs[:] = [
                d for d in dirs
                if d not in EXCLUDE_DIRS and not d.endswith(".egg-info")
            ]
            for file in files:
                _, ext = os.path.splitext(file)
                if ext in EXCLUDE_EXTENSIONS or file in EXCLUDE_EXACT_FILES:
                    continue
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, REPO_DIR)
                zipf.write(full_path, rel_path)
                file_count += 1

    file_size_kb = os.path.getsize(ZIP_DESTINATION) / 1024.0
    print(f"Packaged {file_count} clean files into {ZIP_DESTINATION} ({file_size_kb:.1f} KB)")


if __name__ == "__main__":
    create_release_zip()
