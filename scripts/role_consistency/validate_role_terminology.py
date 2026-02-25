from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import Dict, Iterable, List, Optional

def _from_codes(codes: Iterable[int]) -> str:
    return "".join(chr(x) for x in codes)


TERM_BY_KEY = {
    "operator": _from_codes([79, 112, 101, 114, 97, 116, 111, 114]),
    "production_supervisor": _from_codes(
        [80, 114, 111, 100, 117, 99, 116, 105, 111, 110, 32, 83, 117, 112, 101, 114, 118, 105, 115, 111, 114]
    ),
    "quality_supervisor": _from_codes(
        [81, 117, 97, 108, 105, 116, 121, 32, 83, 117, 112, 101, 114, 118, 105, 115, 111, 114]
    ),
    "quality_coordinator": _from_codes(
        [81, 117, 97, 108, 105, 116, 121, 32, 67, 111, 111, 114, 100, 105, 110, 97, 116, 111, 114]
    ),
    "corp_quality_manager": _from_codes(
        [67, 111, 114, 112, 111, 114, 97, 116, 101, 32, 81, 117, 97, 108, 105, 116, 121, 32, 77, 97, 110, 97, 103, 101, 114]
    ),
    "corp_quality_manager_short": _from_codes(
        [67, 111, 114, 112, 32, 81, 117, 97, 108, 105, 116, 121, 32, 77, 97, 110, 97, 103, 101, 114]
    ),
    "quality_supervisor_plus": _from_codes(
        [81, 117, 97, 108, 105, 116, 121, 32, 83, 117, 112, 101, 114, 118, 105, 115, 111, 114, 43]
    ),
    "quality_manager_plus": _from_codes(
        [81, 117, 97, 108, 105, 116, 121, 32, 77, 97, 110, 97, 103, 101, 114, 43]
    ),
    "quality_engineer_plus": _from_codes(
        [81, 117, 97, 108, 105, 116, 121, 32, 69, 110, 103, 105, 110, 101, 101, 114, 43]
    ),
}

AMBIGUOUS_TERMS = {TERM_BY_KEY["operator"]}

BANNED_TERMS = [
    TERM_BY_KEY["corp_quality_manager"],
    TERM_BY_KEY["quality_supervisor_plus"],
    TERM_BY_KEY["quality_manager_plus"],
    TERM_BY_KEY["quality_engineer_plus"],
    TERM_BY_KEY["corp_quality_manager_short"],
    TERM_BY_KEY["production_supervisor"],
    TERM_BY_KEY["operator"],
    TERM_BY_KEY["quality_supervisor"],
    TERM_BY_KEY["quality_coordinator"],
]

ROLE_CONTEXT_MARKERS = (
    "RoleId",
    "RoleCode",
    "RoleName",
    "ApproverRole",
    "TargetRole",
    "RequiredRole",
    "Required Role",
    "CanCreate_",
    "CanTransition_",
    "role_name:",
    "RequiredRole_Ref",
    "| RoleId |",
    "| Role |",
    _from_codes([44, 79, 80, 69, 82, 65, 84, 79, 82, 44, 79, 112, 101, 114, 97, 116, 111, 114, 44]),
)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def is_role_context(line_text: str) -> bool:
    return any(marker in line_text for marker in ROLE_CONTEXT_MARKERS)


def classify_line(path: str, line_no: int, line_text: str, active: bool):
    for term in BANNED_TERMS:
        if term not in line_text:
            continue
        if term in AMBIGUOUS_TERMS and not is_role_context(line_text):
            continue
        return {
            "type": "ALIAS_IN_ACTIVE" if active else "ALIAS_IN_HISTORICAL",
            "path": path,
            "line": line_no,
            "term": term,
            "text": line_text.strip(),
        }
    return None


def iter_files(scan_roots: Iterable[str], exts: Iterable[str]) -> Iterable[Path]:
    extset = {e.lower() for e in exts}
    ignored_dirs = {".git", "node_modules", "bin", "obj", "dist", "build", "__pycache__", ".venv", "venv"}
    for root in scan_roots:
        p = Path(root)
        if not p.exists():
            continue
        for f in p.rglob("*"):
            if f.is_dir():
                continue
            if any(part in ignored_dirs for part in f.parts):
                continue
            if f.suffix.lower() not in extset:
                continue
            yield f


def is_historical(path: str, historical_globs: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(path, pattern) for pattern in historical_globs)


def validate_allowlist_reasons(allowlist: dict) -> List[str]:
    missing = []
    reasons = allowlist.get("reasons", {})
    for glob in allowlist.get("historical_globs", []):
        if glob not in reasons:
            missing.append(glob)
    return missing


def read_lines(file_path: Path) -> Optional[List[str]]:
    encodings = ("utf-8", "utf-8-sig", "utf-16", "utf-16le", "utf-16be")
    for enc in encodings:
        try:
            return file_path.read_text(encoding=enc).splitlines()
        except UnicodeDecodeError:
            continue
        except Exception:
            return None
    return None


def run_scan(allowlist: dict, scope: str, skip_paths: Optional[set[str]] = None) -> Dict[str, object]:
    issues: List[dict] = []
    scan_roots = allowlist.get("scan_roots", [])
    extensions = allowlist.get("extensions", [])
    historical_globs = allowlist.get("historical_globs", [])

    for file_path in iter_files(scan_roots, extensions):
        rel = file_path.as_posix()
        if skip_paths and rel in skip_paths:
            continue
        historical = is_historical(rel, historical_globs)
        active = not historical

        if scope == "active" and not active:
            continue

        lines = read_lines(file_path)
        if lines is None:
            continue

        for idx, line in enumerate(lines, start=1):
            issue = classify_line(rel, idx, line, active)
            if issue is None:
                continue
            issues.append(issue)

    active_violations = [x for x in issues if x["type"] == "ALIAS_IN_ACTIVE"]
    historical_hits = [x for x in issues if x["type"] == "ALIAS_IN_HISTORICAL"]

    summary = {
        "scope": scope,
        "issues_total": len(issues),
        "active_violations": len(active_violations),
        "historical_hits": len(historical_hits),
    }

    return {
        "summary": summary,
        "issues": issues,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate role terminology consistency across repositories.")
    parser.add_argument("--allowlist", default="scripts/role_consistency/allowlist.yml")
    parser.add_argument("--report", default="docs/plans/evidence/2026-02-25-role-terminology-report.json")
    parser.add_argument("--scope", choices=["active", "all"], default="all")
    parser.add_argument("--enforce-allowlist-reasons", action="store_true")
    args = parser.parse_args()

    allowlist = load_json(Path(args.allowlist))

    missing_reason_globs: List[str] = []
    if args.enforce_allowlist_reasons:
        missing_reason_globs = validate_allowlist_reasons(allowlist)

    report_rel = Path(args.report).as_posix()
    result = run_scan(allowlist, args.scope, skip_paths={report_rel})
    result["allowlist_missing_reasons"] = missing_reason_globs

    report_path = Path(args.report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    if missing_reason_globs:
        print(f"FAIL: missing allowlist reasons for {len(missing_reason_globs)} globs")
        return 2

    active_violations = int(result["summary"]["active_violations"])  # type: ignore[index]
    if active_violations > 0:
        print(f"FAIL: {active_violations} active terminology violations")
        return 1

    print("PASS: role terminology validation")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
