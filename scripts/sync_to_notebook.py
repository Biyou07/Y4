#!/usr/bin/env python3
"""
sync_to_notebook.py
===================
Automated synchronization script linking Git repository study materials directly
to Google NotebookLM (Gemini Notebooks) via the `notebooklm-py` CLI/library.

Supported Course Content Types:
- Markdown notes & summaries: .md, .markdown, .txt
- Lecture slides & presentations: .pptx, .ppt
- Textbooks, lecture notes & handouts: .pdf, .docx, .doc
- Educational diagrams & formulas: .png, .jpg, .jpeg, .webp

Strictly Excluded:
- Code files (.py, .cpp, .c, .sh, etc.)
- Jupyter notebooks (.ipynb)
- Datasets & raw archives (.csv, .tsv, .parquet, .json, .zip, etc.)
- Virtual environments (.venv/, env/)
- Caches and editor configurations (.obsidian/, .vscode/, .git/)

Features:
- Dynamic notebook discovery and creation: maps modules to dedicated notebooks.
- Clean title extraction from YAML frontmatter, Markdown H1 headers, or clean filenames.
- Duplicate prevention: replaces existing sources on document update.
- Symlink safety and canonical path resolution.
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# ==============================================================================
# Filter Definitions & Constants
# ==============================================================================

# Ingest all course content: notes, slides, documents, and figures
ALLOWED_EXTENSIONS: Set[str] = {
    # Markdown & plain text notes
    ".md",
    ".markdown",
    ".txt",
    # Documents & Lecture notes
    ".pdf",
    ".docx",
    ".doc",
    # Slides & presentations
    ".pptx",
    ".ppt",
    # Course figures, diagrams, and formulas
    ".png",
    ".jpg",
    ".jpeg",
    ".webp",
}

EXCLUDED_DIR_NAMES: Set[str] = {
    ".git",
    ".github",
    ".vscode",
    ".idea",
    ".obsidian",
    ".claude",
    ".gemini",
    ".venv",
    "venv",
    "env",
    "ENV",
    "__pycache__",
    "node_modules",
    ".ipynb_checkpoints",
    "scripts",
    "tests",
}

# Root-level non-study documentation files to ignore
EXCLUDED_ROOT_FILENAMES: Set[str] = {
    "README.md",
    "CLAUDE.md",
    "GEMINI.md",
    "AGENTS.md",
    "LICENSE.md",
    "CONTRIBUTING.md",
    "build_bundle.sh",
}

# Known academic abbreviation to clean human title mapping
FRIENDLY_MODULE_TITLES: Dict[str, str] = {
    "DL": "Deep Learning",
    "DEEP_LEARNING": "Deep Learning",
    "GEO_AI": "Geo AI",
    "AI&ETHICS": "AI & Ethics",
    "AI_ETHICS": "AI & Ethics",
    "HCI": "Human-Computer Interaction",
    "NLP": "Natural Language Processing",
    "ROBOTICS": "Robotics",
    "WC": "Wireless Communications",
    "COMPUTER_VISION": "Computer Vision",
    "CV": "Computer Vision",
}

# ==============================================================================
# Helper: NotebookLM CLI Runner
# ==============================================================================

def find_notebooklm_cmd() -> List[str]:
    """Locate the notebooklm executable or fallback to python module execution."""
    # 1. System PATH
    cli_path = shutil.which("notebooklm")
    if cli_path:
        return [cli_path]

    # 2. ~/.local/bin/notebooklm (common for uv tool or pip --user)
    user_local = os.path.expanduser("~/.local/bin/notebooklm")
    if os.path.isfile(user_local) and os.access(user_local, os.X_OK):
        return [user_local]

    # 3. Fallback to python module execution
    return [sys.executable, "-m", "notebooklm.notebooklm_cli"]


def run_cli_command(args: List[str], check: bool = True) -> Tuple[int, str, str]:
    """Execute a NotebookLM CLI command and capture output."""
    cmd = find_notebooklm_cmd() + args
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if check and proc.returncode != 0:
            print(f"[ERROR] CLI command failed ({proc.returncode}): {' '.join(cmd)}", file=sys.stderr)
            if proc.stdout:
                print(f"[STDOUT] {proc.stdout.strip()}", file=sys.stderr)
            if proc.stderr:
                print(f"[STDERR] {proc.stderr.strip()}", file=sys.stderr)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except Exception as e:
        print(f"[ERROR] Subprocess failed to execute {' '.join(cmd)}: {e}", file=sys.stderr)
        return -1, "", str(e)


def run_cli_json(args: List[str]) -> Optional[Any]:
    """Execute a CLI command expecting JSON output."""
    if "--json" not in args:
        args = list(args) + ["--json"]
    ret, stdout, stderr = run_cli_command(args, check=False)
    if not stdout:
        return None
    try:
        return json.loads(stdout)
    except json.JSONDecodeError:
        for line in stdout.splitlines():
            line = line.strip()
            if (line.startswith("{") and line.endswith("}")) or (line.startswith("[") and line.endswith("]")):
                try:
                    return json.loads(line)
                except Exception:
                    pass
        print(f"[WARN] Failed to parse JSON from CLI output: {stdout[:200]}...", file=sys.stderr)
        return None


# ==============================================================================
# NotebookLM Operations (Notebooks & Sources)
# ==============================================================================

def get_account_notebooks() -> List[Dict[str, Any]]:
    """List all notebooks in the connected NotebookLM account."""
    data = run_cli_json(["list"])
    if isinstance(data, dict) and "notebooks" in data:
        return data["notebooks"]
    return []


def create_new_notebook(title: str) -> Optional[str]:
    """Create a new NotebookLM notebook and return its unique ID."""
    print(f"[INFO] Creating new NotebookLM notebook: '{title}'...")
    data = run_cli_json(["create", title])
    if isinstance(data, dict):
        if "notebook" in data and "id" in data["notebook"]:
            nb_id = data["notebook"]["id"]
            print(f"[SUCCESS] Notebook created with ID: {nb_id}")
            return nb_id
        if "active_notebook_id" in data:
            return data["active_notebook_id"]

    ret, stdout, _ = run_cli_command(["create", title])
    match = re.search(r"Created notebook:\s*([a-f0-9-]+)", stdout, re.IGNORECASE)
    if match:
        nb_id = match.group(1)
        print(f"[SUCCESS] Notebook created with ID (parsed): {nb_id}")
        return nb_id

    print(f"[ERROR] Failed to obtain notebook ID for title '{title}'", file=sys.stderr)
    return None


def get_notebook_sources(notebook_id: str) -> List[Dict[str, Any]]:
    """Get all existing sources for a notebook."""
    data = run_cli_json(["source", "list", "-n", notebook_id])
    if isinstance(data, dict) and "sources" in data:
        return data["sources"]
    return []


def delete_source(notebook_id: str, source_id: str) -> bool:
    """Delete a source by ID."""
    ret, stdout, stderr = run_cli_command(
        ["source", "delete", source_id, "-n", notebook_id, "-y", "--json"],
        check=False,
    )
    return ret == 0


def add_source_to_notebook(notebook_id: str, filepath: str, title: str) -> bool:
    """Upload a file to the specified notebook as a cleanly titled source."""
    resolved_path = os.path.realpath(filepath)
    ret, stdout, stderr = run_cli_command(
        [
            "source",
            "add",
            resolved_path,
            "-n",
            notebook_id,
            "--title",
            title,
            "--follow-symlinks",
            "--json",
        ],
        check=False,
    )
    if ret == 0:
        print(f"[SUCCESS] Uploaded '{title}' ({filepath}) -> Notebook {notebook_id}")
        return True
    else:
        print(f"[ERROR] Failed uploading '{title}': {stderr or stdout}", file=sys.stderr)
        return False


# ==============================================================================
# Filtering & Title Extraction
# ==============================================================================

def is_course_content_file(rel_path: str) -> bool:
    """
    Strict filter: returns True ONLY if the file is course content documentation,
    slides, documents, or study diagrams.
    Strictly excludes code, notebooks, datasets, virtual environments, binaries, and configs.
    """
    norm_path = os.path.normpath(rel_path)
    parts = norm_path.split(os.sep)

    # 1. Reject any path within excluded directories or hidden folders
    for part in parts[:-1]:
        if part in EXCLUDED_DIR_NAMES or part.startswith("."):
            return False

    filename = parts[-1]
    # 2. Reject hidden files
    if filename.startswith("."):
        return False

    # 3. Whitelist file extensions: course content formats only
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False

    # 4. Exclude repository root meta-documentation files
    if len(parts) == 1 and filename in EXCLUDED_ROOT_FILENAMES:
        return False

    return True


def extract_clean_title(filepath: str) -> str:
    """
    Extract a clean title from course content:
    - Markdown (.md, .markdown): YAML Frontmatter 'title: ...' or '# H1' header
    - Text (.txt): First non-empty header line or cleaned filename
    - Slides/Documents/Images (.pdf, .pptx, .docx, .png, etc.): Cleaned filename stem
    """
    stem = os.path.splitext(os.path.basename(filepath))[0]
    clean_stem = stem.replace("_", " ").replace("-", " ").strip()
    ext = os.path.splitext(filepath)[1].lower()

    if ext in {".md", ".markdown"}:
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    lines = [f.readline() for _ in range(50)]

                # Check YAML frontmatter
                in_frontmatter = False
                for line in lines:
                    sline = line.strip()
                    if sline == "---":
                        in_frontmatter = not in_frontmatter
                        continue
                    if in_frontmatter and sline.startswith("title:"):
                        raw_title = sline.split(":", 1)[1].strip().strip("\"'")
                        if raw_title:
                            return raw_title

                # Check Markdown H1
                for line in lines:
                    sline = line.strip()
                    if sline.startswith("# ") and not sline.startswith("## "):
                        h1 = sline.lstrip("# ").strip()
                        h1 = re.sub(r"[*_~`]", "", h1).strip()
                        if h1:
                            return h1
        except Exception as e:
            print(f"[WARN] Error reading title from {filepath}: {e}", file=sys.stderr)

    elif ext == ".txt":
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                    first_line = f.readline().strip()
                    if first_line and len(first_line) < 80 and not first_line.startswith("#"):
                        return first_line
        except Exception:
            pass

    return clean_stem.title() if clean_stem.islower() else clean_stem


# ==============================================================================
# Mapping Resolution & Dynamic Notebook Creation
# ==============================================================================

def load_notebooks_mapping(mapping_path: str) -> Dict[str, Any]:
    """Load notebooks.json mapping or return empty dict if missing."""
    if os.path.exists(mapping_path):
        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load {mapping_path}: {e}", file=sys.stderr)
    return {}


def save_notebooks_mapping(mapping_path: str, mapping: Dict[str, Any]) -> None:
    """Save notebooks.json mapping formatted cleanly."""
    try:
        with open(mapping_path, "w", encoding="utf-8") as f:
            json.dump(mapping, f, indent=2, sort_keys=True)
            f.write("\n")
        print(f"[INFO] Persisted updated mappings to {mapping_path}")
    except Exception as e:
        print(f"[ERROR] Failed to save {mapping_path}: {e}", file=sys.stderr)


def derive_module_info(rel_path: str) -> Tuple[str, str]:
    """
    Derive the module key and human-friendly title from a relative file path.
    Examples:
      'S7/DL/lab1/note.md' -> ('S7/DL', 'Deep Learning')
      'S7/AI&ETHICS/slides.pptx' -> ('S7/AI&ETHICS', 'AI & Ethics')
      'Computer_Vision/week1.pdf' -> ('Computer_Vision', 'Computer Vision')
      '01_PROFILE.md' -> ('_default', 'Career')
    """
    norm_path = os.path.normpath(rel_path)
    parts = norm_path.split(os.sep)

    # Semester Mono-Repo pattern: S[0-9]+/<module>/...
    if len(parts) >= 2 and re.match(r"^S\d+$", parts[0], re.IGNORECASE):
        semester = parts[0].upper()
        raw_mod = parts[1]
        module_key = f"{semester}/{raw_mod}"
        clean_name = FRIENDLY_MODULE_TITLES.get(
            raw_mod.upper(),
            raw_mod.replace("_", " ").replace("-", " ").title()
        )
        return module_key, clean_name

    # Subdirectory pattern: <module>/...
    if len(parts) >= 2:
        raw_mod = parts[0]
        clean_name = FRIENDLY_MODULE_TITLES.get(
            raw_mod.upper(),
            raw_mod.replace("_", " ").replace("-", " ").title()
        )
        return raw_mod, clean_name

    # Root-level note pattern: Career or default
    return "_default", "Career"


def resolve_notebook_id(
    rel_path: str,
    mapping: Dict[str, Any],
    mapping_path: str,
    dry_run: bool = False,
) -> Tuple[Optional[str], str]:
    """
    Resolve or dynamically create the NotebookLM notebook for the given file path.
    Returns (notebook_id, notebook_title).
    """
    norm_path = os.path.normpath(rel_path)
    matched_key: Optional[str] = None

    # 1. Longest prefix match against mapping keys
    sorted_keys = sorted(mapping.keys(), key=len, reverse=True)
    for key in sorted_keys:
        if key == "_default":
            continue
        if norm_path == key or norm_path.startswith(key + os.sep) or norm_path.startswith(key + "/"):
            matched_key = key
            break

    # 2. Check directory name matches
    if not matched_key:
        parts = norm_path.split(os.sep)
        for part in parts[:-1]:
            if part in mapping:
                matched_key = part
                break

    # 3. Fallback to derived module info
    if not matched_key:
        derived_key, derived_title = derive_module_info(rel_path)
        if derived_key in mapping:
            matched_key = derived_key
        elif "_default" in mapping and len(parts) == 1:
            matched_key = "_default"
        else:
            matched_key = derived_key
            mapping[matched_key] = {"notebook_id": "", "title": derived_title}

    # Extract ID and Title from mapping entry
    entry = mapping.get(matched_key)
    notebook_id = ""
    notebook_title = matched_key

    if isinstance(entry, str):
        notebook_id = entry
        notebook_title = matched_key
    elif isinstance(entry, dict):
        notebook_id = entry.get("notebook_id", "")
        notebook_title = entry.get("title") or derive_module_info(rel_path)[1]

    # 4. If notebook ID is missing, dynamically discover or create
    if not notebook_id:
        if dry_run:
            print(f"[DRY-RUN] Would create new notebook for '{notebook_title}' ({matched_key})")
            return "dry-run-notebook-id", notebook_title

        print(f"[INFO] Missing Notebook ID for '{matched_key}'. Searching existing notebooks...")
        existing_nbs = get_account_notebooks()
        for nb in existing_nbs:
            nb_title = (nb.get("title") or "").strip().lower()
            if nb_title and (nb_title == notebook_title.strip().lower() or nb_title == matched_key.strip().lower()):
                notebook_id = nb.get("id")
                print(f"[INFO] Found matching existing notebook: '{nb.get('title')}' -> {notebook_id}")
                break

        if not notebook_id:
            notebook_id = create_new_notebook(notebook_title)

        if notebook_id:
            if isinstance(mapping.get(matched_key), dict):
                mapping[matched_key]["notebook_id"] = notebook_id
                mapping[matched_key]["title"] = notebook_title
            else:
                mapping[matched_key] = {
                    "notebook_id": notebook_id,
                    "title": notebook_title,
                }
            save_notebooks_mapping(mapping_path, mapping)
        else:
            print(f"[ERROR] Could not resolve or create notebook for '{matched_key}'", file=sys.stderr)
            return None, notebook_title

    return notebook_id, notebook_title


# ==============================================================================
# Synchronization Core
# ==============================================================================

def sync_course_file(
    repo_root: str,
    rel_path: str,
    action: str,
    mapping: Dict[str, Any],
    mapping_path: str,
    dry_run: bool = False,
) -> bool:
    """
    Sync an individual course file (addition, update, or deletion) to its target Notebook.
    """
    abs_path = os.path.join(repo_root, rel_path)
    clean_title = extract_clean_title(abs_path) if action != "delete" else os.path.basename(rel_path)

    notebook_id, notebook_title = resolve_notebook_id(
        rel_path,
        mapping,
        mapping_path,
        dry_run=dry_run,
    )

    if not notebook_id:
        print(f"[SKIP] No notebook available for {rel_path}")
        return False

    if dry_run:
        print(f"[DRY-RUN] {action.upper()}: '{clean_title}' ({rel_path}) -> Notebook '{notebook_title}' ({notebook_id})")
        return True

    # Check existing sources in target notebook to avoid duplicate notes
    existing_sources = get_notebook_sources(notebook_id)
    basename = os.path.basename(rel_path)
    matched_source_id: Optional[str] = None

    for s in existing_sources:
        stitle = s.get("title", "")
        if stitle == clean_title or stitle == basename:
            matched_source_id = s.get("id")
            break

    if action == "delete":
        if matched_source_id:
            print(f"[INFO] Removing deleted content source '{clean_title}' ({matched_source_id}) from {notebook_title}...")
            return delete_source(notebook_id, matched_source_id)
        else:
            print(f"[INFO] Source for deleted file '{rel_path}' was not in notebook {notebook_title}. Nothing to delete.")
            return True

    # Addition or Modification: Upsert
    if matched_source_id:
        print(f"[INFO] Updating existing source '{clean_title}' ({matched_source_id}) in notebook '{notebook_title}'...")
        delete_source(notebook_id, matched_source_id)
        time.sleep(1)  # Brief pause for backend consistency

    return add_source_to_notebook(notebook_id, abs_path, clean_title)


# ==============================================================================
# Change Detection (Git Diff / All Files / Explicit)
# ==============================================================================

def get_git_changed_files(repo_root: str) -> List[Tuple[str, str]]:
    """
    Determine changed files from Git.
    Returns list of tuples: (action, relative_path), where action is 'upsert' or 'delete'.
    """
    before_sha = os.getenv("GITHUB_EVENT_BEFORE")
    current_sha = os.getenv("GITHUB_SHA")

    cmd = ["git", "diff", "--name-status"]

    if before_sha and current_sha and before_sha != "0000000000000000000000000000000000000000":
        cmd += [before_sha, current_sha]
    else:
        rev_check = subprocess.run(
            ["git", "rev-parse", "--verify", "HEAD~1"],
            cwd=repo_root,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if rev_check.returncode == 0:
            cmd += ["HEAD~1", "HEAD"]
        else:
            print("[INFO] No commit history to diff against. Listing all tracked repository files...")
            ls_proc = subprocess.run(
                ["git", "ls-files"],
                cwd=repo_root,
                stdout=subprocess.PIPE,
                text=True,
                check=True,
            )
            return [("upsert", line.strip()) for line in ls_proc.stdout.splitlines() if line.strip()]

    print(f"[INFO] Detecting Git changes with: {' '.join(cmd)}")
    proc = subprocess.run(
        cmd,
        cwd=repo_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=False,
    )

    if proc.returncode != 0:
        print(f"[WARN] git diff failed: {proc.stderr}. Falling back to git status.", file=sys.stderr)
        stat_proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            text=True,
            check=False,
        )
        changes = []
        for line in stat_proc.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            status_code = line[:2].strip()
            filepath = line[2:].strip()
            action = "delete" if "D" in status_code else "upsert"
            changes.append((action, filepath))
        return changes

    changes = []
    for line in proc.stdout.splitlines():
        parts = line.split(maxsplit=2)
        if not parts:
            continue
        status = parts[0]
        if status.startswith("D"):
            changes.append(("delete", parts[1]))
        elif status.startswith("R"):
            if len(parts) >= 3:
                changes.append(("delete", parts[1]))
                changes.append(("upsert", parts[2]))
        else:
            changes.append(("upsert", parts[1]))

    return changes


def get_all_course_files(repo_root: str) -> List[Tuple[str, str]]:
    """Scan the entire repository for eligible course content files."""
    files = []
    for root, dirs, filenames in os.walk(repo_root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES and not d.startswith(".")]
        for fname in filenames:
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, repo_root)
            if is_course_content_file(rel_path):
                files.append(("upsert", rel_path))
    return files


# ==============================================================================
# CLI Entry Point
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Sync course content files (.md, .pdf, .docx, .pptx, images) from Git repository to NotebookLM."
    )
    parser.add_argument(
        "--files",
        nargs="*",
        help="Specific file paths to sync (relative to repository root).",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Scan and sync all course content files in the repository.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the sync process without making changes in NotebookLM.",
    )
    parser.add_argument(
        "--mapping-file",
        default="notebooks.json",
        help="Path to the notebook mapping JSON file (default: notebooks.json).",
    )

    args = parser.parse_args()

    repo_root = os.getcwd()
    mapping_path = os.path.abspath(os.path.join(repo_root, args.mapping_file))

    print(f"============================================================")
    print(f"NotebookLM Course Content Sync Pipeline")
    print(f"Repository Root : {repo_root}")
    print(f"Mapping File    : {mapping_path}")
    print(f"Dry Run Mode    : {args.dry_run}")
    print(f"============================================================")

    mapping = load_notebooks_mapping(mapping_path)

    # Determine files to process
    target_items: List[Tuple[str, str]] = []

    if args.files:
        for f in args.files:
            target_items.append(("upsert", f))
    elif args.all:
        print("[INFO] Mode: Full repository scan (--all)")
        target_items = get_all_course_files(repo_root)
    else:
        print("[INFO] Mode: Git change detection")
        target_items = get_git_changed_files(repo_root)

    # Filter candidates strictly
    eligible_items: List[Tuple[str, str]] = []
    ignored_count = 0

    for action, rel_path in target_items:
        if is_course_content_file(rel_path):
            eligible_items.append((action, rel_path))
        else:
            ignored_count += 1

    print(f"[INFO] Found {len(eligible_items)} eligible course content files ({ignored_count} files excluded by filters).")

    if not eligible_items:
        print("[INFO] No course content files to sync. Pipeline complete.")
        return

    # Process each course file
    success_count = 0
    fail_count = 0

    for action, rel_path in eligible_items:
        print(f"\n--- Processing: {rel_path} ({action}) ---")
        ok = sync_course_file(
            repo_root=repo_root,
            rel_path=rel_path,
            action=action,
            mapping=mapping,
            mapping_path=mapping_path,
            dry_run=args.dry_run,
        )
        if ok:
            success_count += 1
        else:
            fail_count += 1

    print(f"\n============================================================")
    print(f"Sync Summary: {success_count} succeeded, {fail_count} failed.")
    print(f"============================================================")

    if fail_count > 0 and not args.dry_run:
        sys.exit(1)


if __name__ == "__main__":
    main()
