#!/usr/bin/env python3
"""
NPM Package Compression Benchmark
Tests gzip, bzip2, xz/lzma compression.
"""

import subprocess
import time
import os
from pathlib import Path
import tarfile
import gzip
import bz2
import lzma

def get_dir_size(path):
    return sum(f.stat().st_size for f in Path(path).rglob('*') if f.is_file())

def benchmark_python_tar(pkg_path, mode):
    """Benchmark Python tarfile compression"""
    output = Path(f"/tmp/{pkg_path.name}.tar.{mode.split(':')[1]}")
    if output.exists():
        output.unlink()
    
    start = time.perf_counter()
    with tarfile.open(output, f"w:{mode.split(':')[1]}") as tar:
        tar.add(pkg_path, arcname=pkg_path.name)
    elapsed = time.perf_counter() - start
    
    size = output.stat().st_size
    output.unlink()
    return elapsed, size

def main():
    print("=" * 70)
    print("NPM Package Compression Benchmark")
    print("=" * 70)
    
    corpus_dir = Path("corpus")
    if not corpus_dir.exists():
        print("Error: Run 'python3 generate_corpus.py' first")
        return
    
    results = []
    
    for pkg_dir in sorted(corpus_dir.iterdir()):
        if not pkg_dir.is_dir():
            continue
        
        print(f"\n{pkg_dir.name}:")
        original_size = get_dir_size(pkg_dir)
        file_count = sum(1 for _ in pkg_dir.rglob('*') if _.is_file())
        print(f"  Original: {original_size/1024:.1f} KB, {file_count} files")
        
        # Test Python gzip
        try:
            elapsed, size = benchmark_python_tar(pkg_dir, "w:gz")
            ratio = size / original_size
            print(f"  Python gzip: {elapsed*1000:.1f}ms, {size/1024:.1f}KB ({ratio:.1%})")
            results.append({
                'package': pkg_dir.name,
                'compressor': 'python-gzip',
                'time_ms': elapsed * 1000,
                'size': size,
                'ratio': ratio
            })
        except Exception as e:
            print(f"  Python gzip: Failed - {e}")
        
        # Test Python bzip2
        try:
            elapsed, size = benchmark_python_tar(pkg_dir, "w:bz2")
            ratio = size / original_size
            print(f"  Python bzip2: {elapsed*1000:.1f}ms, {size/1024:.1f}KB ({ratio:.1%})")
            results.append({
                'package': pkg_dir.name,
                'compressor': 'python-bz2',
                'time_ms': elapsed * 1000,
                'size': size,
                'ratio': ratio
            })
        except Exception as e:
            print(f"  Python bzip2: Failed - {e}")
        
        # Test Python xz
        try:
            elapsed, size = benchmark_python_tar(pkg_dir, "w:xz")
            ratio = size / original_size
            print(f"  Python xz: {elapsed*1000:.1f}ms, {size/1024:.1f}KB ({ratio:.1%})")
            results.append({
                'package': pkg_dir.name,
                'compressor': 'python-xz',
                'time_ms': elapsed * 1000,
                'size': size,
                'ratio': ratio
            })
        except Exception as e:
            print(f"  Python xz: Failed - {e}")
    
    # Save results
    print("\n" + "=" * 70)
    with open("RESULTS.md", "w") as f:
        f.write("# NPM Package Compression Results\n\n")
        f.write("| Package | Compressor | Time (ms) | Size (KB) | Ratio |\n")
        f.write("|---------|------------|-----------|-----------|-------|\n")
        for r in results:
            f.write(f"| {r['package']} | {r['compressor']} | {r['time_ms']:.1f} | "
                   f"{r['size']/1024:.1f} | {r['ratio']:.1%} |\n")
    
    print("✓ Results saved to RESULTS.md")
    print("\nNote: Install brotli, zstd, and hyperfine for complete comparison")
    print("  pip install brotli zstandard")
    print("  apt-get install hyperfine")

if __name__ == "__main__":
    main()
