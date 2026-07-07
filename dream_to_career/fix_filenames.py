r"""
fix_filenames.py
================
Run this ONCE from inside the dream_to_career folder to rename all
emoji page files to their clean Windows-safe equivalents.

Usage:
    cd D:/D2C/dream_to_career
    python fix_filenames.py
"""
import os, pathlib, sys

RENAMES = {
    # old (emoji) name           : new (clean) name
    "01_\U0001f3e0_Home.py"                     : "01_Home.py",
    "01_🏠_Home.py"                              : "01_Home.py",
    "02_🔭_Career_Analysis.py"                  : "02_Career_Analysis.py",
    "03_🧩_Skill_Assessment.py"                 : "03_Skill_Assessment.py",
    "04_🗺️_Roadmap_Generator.py"               : "04_Roadmap_Generator.py",
    "05_📚_Learning_Hub.py"                     : "05_Learning_Hub.py",
    "06_🤖_AI_Career_Twin.py"                   : "06_AI_Career_Twin.py",
    "07_⚡_WhatIf_Simulator.py"                 : "07_WhatIf_Simulator.py",
    "08_🎤_Mock_Interview.py"                   : "08_Mock_Interview.py",
    "09_📈_Progress_Dashboard.py"               : "09_Progress_Dashboard.py",
    "10_🔬_Analytics.py"                         : "10_Analytics.py",
    "10_📊_Progress_Dashboard.py"               : "09_Progress_Dashboard.py",
}

pages_dir = pathlib.Path(__file__).parent / "pages"
if not pages_dir.exists():
    print("ERROR: 'pages' folder not found. Run this from inside dream_to_career/")
    sys.exit(1)

renamed = 0
for old_name, new_name in RENAMES.items():
    old_path = pages_dir / old_name
    new_path = pages_dir / new_name
    if old_path.exists():
        if new_path.exists() and old_path != new_path:
            print(f"  SKIP (target exists): {old_name} -> {new_name}")
            continue
        old_path.rename(new_path)
        print(f"  Renamed: {old_name}  ->  {new_name}")
        renamed += 1
    else:
        # Try matching by glob (handles garbled Windows display like ≡ƒù║)
        matches = list(pages_dir.glob(f"{old_name[:3]}*.py"))
        for m in matches:
            if m.name not in RENAMES.values() and m.name != new_name:
                target = pages_dir / new_name
                if not target.exists():
                    m.rename(target)
                    print(f"  Renamed (glob): {m.name}  ->  {new_name}")
                    renamed += 1
                break

if renamed == 0:
    # Check if files are already correctly named
    current = [f.name for f in pages_dir.glob("*.py")]
    clean   = list(RENAMES.values())
    already_clean = all(any(c in current for c in clean) for c in clean[:3])
    if already_clean:
        print("Files already have clean names — nothing to rename ✅")
    else:
        print(f"Current files in pages/: {current}")
        print("No files matched. They may already be renamed or have unexpected names.")
else:
    print(f"\n{renamed} file(s) renamed successfully ✅")
    print("Now run:  streamlit run app.py")
