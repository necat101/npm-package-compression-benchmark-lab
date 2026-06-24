# NPM Package Compression Benchmark Results

**Generated:** 2026-06-24 22:13:00  
**Platform:** Linux 6.17.0-1009-aws x86_64  
**Python:** 3.12.3

## Test Environment
- **Corpus:** 3 npm-like packages generated locally
  - small-package: 25 files, 6.7 KB
  - medium-package: 101 files, 64.7 KB  
  - large-package: 325 files, 507.8 KB
- **Tools available:** Python gzip, bz2, lzma (stdlib only)
- **Tools NOT available:** brotli, zstd, hyperfine, Node.js zlib

## Results

| Package | Compressor | Time (ms) | Size (KB) | Ratio | Status |
|---------|------------|-----------|-----------|-------|--------|
| small-package | Python gzip | 39.2 | 1.3 | 19.4% | ✓ |
| small-package | Python bzip2 | - | - | - | Failed* |
| small-package | Python xz | - | - | - | Failed* |
| medium-package | Python gzip | 149.7 | 2.8 | 4.3% | ✓ |
| medium-package | Python bzip2 | - | - | - | Failed* |
| medium-package | Python xz | - | - | - | Failed* |
| large-package | Python gzip | 495.5 | 161.2 | 31.7% | ✓ |
| large-package | Python bzip2 | - | - | - | Failed* |
| large-package | Python xz | - | - | - | Failed* |

*Failed due to tar command path issues in benchmark script - Python tarfile module works but CLI integration needs fixing

## Raw Terminal Output

```
$ python3 generate_corpus.py
Generating npm package corpus...
✓ Corpus generated in corpus/
  small-package: 25 files, 6.7 KB
  medium-package: 101 files, 64.7 KB
  large-package: 325 files, 507.8 KB

$ python3 benchmark.py
======================================================================
NPM Package Compression Benchmark
======================================================================

large-package:
----------------------------------------------------------------------
Original: 507.8 KB, 325 files
  Python gzip:
    Compress: 495.5ms, Size: 161.2KB

medium-package:
----------------------------------------------------------------------
Original: 64.7 KB, 101 files
  Python gzip:
    Compress: 149.7ms, Size: 2.8KB

small-package:
----------------------------------------------------------------------
Original: 6.7 KB, 25 files
  Python gzip:
    Compress: 39.2ms, Size: 1.3KB
```

## Verification

```bash
$ python3 -m py_compile generate_corpus.py benchmark.py
$ echo $?
0
✓ Both files compile successfully
```

## Limitations

This benchmark run demonstrates:
- ✅ Corpus generation works
- ✅ Python gzip compression works via tarfile module
- ✅ Basic timing measurements work
- ❌ CLI tools (gzip, bzip2, xz via tar command) failed due to path issues
- ❌ Brotli not available (requires `pip install brotli`)
- ❌ Zstd not available (requires `pip install zstandard`)
- ❌ No level sweeps implemented
- ❌ No decompression timing
- ❌ No correctness verification (checksums)
- ❌ No multiple trials with statistics
- ❌ No Node.js baselines

## Next Steps

To complete the benchmark lab:
1. Fix tar command path handling in benchmark.py
2. Install optional dependencies: `pip install brotli zstandard`
3. Implement level sweeps (gzip 1/6/9, etc.)
4. Add decompression timing
5. Add SHA256 tree verification
6. Run 3+ trials with statistics
7. Test with real npm packages (optional)
