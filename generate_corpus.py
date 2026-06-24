#!/usr/bin/env python3
"""
Generate npm-like package corpus for compression benchmarking
"""

import os
import json
import random
from pathlib import Path

def generate_corpus(base_dir="corpus"):
    base = Path(base_dir)
    base.mkdir(exist_ok=True)
    
    print("Generating npm package corpus...")
    
    # Small package
    small = base / "small-package"
    small.mkdir(exist_ok=True)
    pkg = {"name": "test-package-small", "version": "1.0.0", "main": "index.js"}
    (small / "package.json").write_text(json.dumps(pkg, indent=2))
    (small / "README.md").write_text("# Test\n" + "Content\n" * 10)
    
    src = small / "src"
    src.mkdir(exist_ok=True)
    for i in range(20):
        (src / f"module{i}.js").write_text(f"export const v{i} = {i};\n" + "// comment\n" * 10)
    
    # Medium package
    medium = base / "medium-package"
    medium.mkdir(exist_ok=True)
    (medium / "package.json").write_text(json.dumps({**pkg, "name": "test-package-medium"}, indent=2))
    for i in range(100):
        (medium / f"file{i}.js").write_text("const x = 1;\n" * 50)
    
    # Large package
    large = base / "large-package"
    large.mkdir(exist_ok=True)
    (large / "package.json").write_text(json.dumps({**pkg, "name": "test-package-large"}, indent=2))
    
    tiny_dir = large / "node_modules" / "tiny-pkg"
    tiny_dir.mkdir(parents=True, exist_ok=True)
    for i in range(300):
        (tiny_dir / f"t{i}.js").write_text(f"module.exports={i};\n")
    
    for i in range(20):
        (large / f"large{i}.js").write_text("/* Large */\n" + ("const data = 'x';\n" * 1000))
    
    (large / "café.txt").write_text("unicode\n")
    (large / "file with spaces.js").write_text("// spaces\n")
    (large / "binary.dat").write_bytes(os.urandom(102400))
    
    print(f"✓ Corpus generated")
    for d in [small, medium, large]:
        if d.exists():
            count = sum(1 for _ in d.rglob("*") if _.is_file())
            size = sum(_.stat().st_size for _ in d.rglob("*") if _.is_file())
            print(f"  {d.name}: {count} files, {size/1024:.1f} KB")

if __name__ == "__main__":
    generate_corpus()
