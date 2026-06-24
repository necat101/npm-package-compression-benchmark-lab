#!/usr/bin/env python3
"""
NPM Package Compression Benchmark - Complete Implementation
Tests gzip, bzip2, xz with level sweeps, decompression timing, and verification.
"""

import subprocess
import time
import os
import hashlib
import statistics
from pathlib import Path
import tarfile
import gzip
import bz2
import lzma
import sys
import platform

def get_dir_size(path):
    """Get total size of directory"""
    return sum(f.stat().st_size for f in Path(path).rglob('*') if f.is_file())

def get_file_count(path):
    """Get file count"""
    return sum(1 for _ in Path(path).rglob('*') if _.is_file())

def sha256_tree(path):
    """Calculate SHA256 of directory tree structure and contents"""
    h = hashlib.sha256()
    for f in sorted(Path(path).rglob('*')):
        if f.is_file():
            rel_path = str(f.relative_to(path))
            h.update(rel_path.encode('utf-8'))
            h.update(f.read_bytes())
    return h.hexdigest()

def benchmark_compression(name, compress_func, decompress_func, 
                         source_dir, archive_path, extract_dir, trials=3):
    """Benchmark compression with multiple trials"""
    print(f"\n  {name}:")
    
    compress_times = []
    decompress_times = []
    sizes = []
    
    original_checksum = sha256_tree(source_dir)
    original_size = get_dir_size(source_dir)
    
    for trial in range(trials):
        # Clean up from previous trial
        if archive_path.exists():
            archive_path.unlink()
        if extract_dir.exists():
            import shutil
            shutil.rmtree(extract_dir)
        
        # Compression
        start = time.perf_counter()
        try:
            compress_func(source_dir, archive_path)
            compress_time = time.perf_counter() - start
            compress_success = archive_path.exists()
        except Exception as e:
            print(f"    Trial {trial+1}: Compress failed - {e}")
            return None
        
        if not compress_success:
            print(f"    Trial {trial+1}: No output file")
            return None
        
        compressed_size = archive_path.stat().st_size
        
        # Decompression
        extract_dir.mkdir(parents=True, exist_ok=True)
        start = time.perf_counter()
        try:
            decompress_func(archive_path, extract_dir)
            decompress_time = time.perf_counter() - start
        except Exception as e:
            print(f"    Trial {trial+1}: Decompress failed - {e}")
            decompress_time = 0
        
        # Verify
        extracted = list(extract_dir.iterdir())
        verified = False
        if extracted and extracted[0].is_dir():
            extracted_checksum = sha256_tree(extracted[0])
            verified = (extracted_checksum == original_checksum)
        
        compress_times.append(compress_time)
        decompress_times.append(decompress_time)
        sizes.append(compressed_size)
        
        print(f"    Trial {trial+1}: {compress_time*1000:.1f}ms / "
              f"{decompress_time*1000:.1f}ms, {compressed_size/1024:.1f}KB, "
              f"{'✓' if verified else '✗'}")
    
    return {
        'name': name,
        'compress_mean': statistics.mean(compress_times) * 1000,
        'compress_min': min(compress_times) * 1000,
        'decompress_mean': statistics.mean(decompress_times) * 1000,
        'compressed_size': statistics.mean(sizes),
        'original_size': original_size,
        'ratio': statistics.mean(sizes) / original_size,
        'verified': verified,
        'trials': compress_times
    }

def compress_gzip(src, dst, level=6):
    with tarfile.open(dst, f"w:gz", compresslevel=level) as tar:
        tar.add(src, arcname=src.name)

def decompress_gzip(src, dst):
    with tarfile.open(src, "r:gz") as tar:
        tar.extractall(dst)

def compress_bz2(src, dst):
    with tarfile.open(dst, "w:bz2") as tar:
        tar.add(src, arcname=src.name)

def decompress_bz2(src, dst):
    with tarfile.open(src, "r:bz2") as tar:
        tar.extractall(dst)

def compress_xz(src, dst, preset=6):
    with tarfile.open(dst, "w:xz", preset=preset) as tar:
        tar.add(src, arcname=src.name)

def decompress_xz(src, dst):
    with tarfile.open(src, "r:xz") as tar:
        tar.extractall(dst)

def main():
    import shutil
    print("=" * 70)
    print("NPM Package Compression Benchmark")
    print("=" * 70)
    
    corpus_dir = Path("corpus")
    results = []
    tmp_dir = Path("/tmp/npm-bench")
    tmp_dir.mkdir(exist_ok=True)
    
    for pkg_dir in sorted([d for d in corpus_dir.iterdir() if d.is_dir()]):
        print(f"\n{pkg_dir.name}:")
        size = get_dir_size(pkg_dir)
        count = get_file_count(pkg_dir)
        print(f"  {size/1024:.1f} KB, {count} files")
        
        tests = [
            ("gzip-1", lambda s, d: compress_gzip(s, d, 1), decompress_gzip),
            ("gzip-6", lambda s, d: compress_gzip(s, d, 6), decompress_gzip),
            ("gzip-9", lambda s, d: compress_gzip(s, d, 9), decompress_gzip),
            ("bzip2", compress_bz2, decompress_bz2),
            ("xz-6", lambda s, d: compress_xz(s, d, 6), decompress_xz),
        ]
        
        for name, comp, decomp in tests:
            archive = tmp_dir / f"{pkg_dir.name}.tar"
            extract = tmp_dir / "extracted"
            r = benchmark_compression(name, comp, decomp, pkg_dir, archive, extract)
            if r:
                r['package'] = pkg_dir.name
                results.append(r)
                if archive.exists():
                    archive.unlink()
                if extract.exists():
                    shutil.rmtree(extract)
    
    # Save results
    with open("RESULTS.md", "w") as f:
        f.write("# Results\n\n")
        f.write("| Package | Compressor | Compress | Decompress | Size | Ratio | Verified |\n")
        f.write("|---------|------------|----------|------------|------|-------|----------|\n")
        for r in results:
            f.write(f"| {r['package']} | {r['name']} | {r['compress_mean']:.1f}ms | "
                   f"{r['decompress_mean']:.1f}ms | {r['compressed_size']/1024:.1f}KB | "
                   f"{r['ratio']:.1%} | {'✓' if r['verified'] else '✗'} |\n")
    
    print("\n✓ Complete - see RESULTS.md")

if __name__ == "__main__":
    main()
