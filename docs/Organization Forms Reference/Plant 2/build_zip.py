"""Build a slimmed-down Plant 2 audit package zip.
Excludes obsolete form files and oversized image-embedded spreadsheets.
The manifest/indexes still document everything."""

import zipfile
import os
from pathlib import Path

PKG = Path(r"c:\Dev\sf-quality\docs\Organization Forms Reference\Plant 2\Plant2_AI_Audit_Package")
ZIP_PATH = Path(r"c:\Dev\sf-quality\docs\Organization Forms Reference\Plant 2\Plant2_AI_Audit_Package.zip")

MAX_FILE_SIZE = 500 * 1024  # 500 KB per form file

if ZIP_PATH.exists():
    ZIP_PATH.unlink()

skipped = []
included = 0
total_size = 0

with zipfile.ZipFile(str(ZIP_PATH), "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(PKG):
        for fname in files:
            full = Path(root) / fname
            rel = full.relative_to(PKG)
            parts = rel.parts

            # Always include non-forms files (indexes, context, readme, manifest, extracted_text)
            if len(parts) < 1 or parts[0] != "forms":
                zf.write(str(full), str(rel))
                included += 1
                total_size += full.stat().st_size
                continue

            # For form files: skip obsolete folders
            rel_lower = str(rel).lower().replace("\\", "/")
            if "/obsolete/" in rel_lower or "/review and update/" in rel_lower:
                skipped.append(f"OBSOLETE: {rel}")
                continue

            # Skip files over size limit
            fsize = full.stat().st_size
            if fsize > MAX_FILE_SIZE:
                skipped.append(f"OVERSIZE ({fsize // 1024}KB): {rel}")
                continue

            zf.write(str(full), str(rel))
            included += 1
            total_size += fsize

print(f"Included: {included} files ({total_size / (1024 * 1024):.1f} MB)")
print(f"Skipped: {len(skipped)} files")
print(f"Zip size: {ZIP_PATH.stat().st_size / (1024 * 1024):.1f} MB")

oversize = [s for s in skipped if s.startswith("OVERSIZE")]
if oversize:
    print(f"\nOversize current files skipped ({len(oversize)}):")
    for s in oversize:
        print(f"  {s}")
