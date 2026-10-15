# Installation

## Requirements

- Python 3.9 or newer
- That's it.

No Node.js, no npm, no system libraries, no compiler. mmdr ships as a
pre-built native wheel for all major platforms.

## Install from PyPI

```bash
pip install mmdr
```

## Verify

```bash
mmdr --version
```

```python
import mmdr
print(mmdr.__version__)
print(mmdr.backends())
# ['merman', 'mermaid-rs-renderer']
```

## Dependencies

mmdr depends on [novasvg](https://mohammadraziei.github.io/novasvg/) (`>=0.10`),
which handles PNG / raw-pixel output, and on [NumPy](https://numpy.org/)
(`>=1.20`), which is how raw pixels are read out of novasvg. Both are installed
automatically and ship pre-built wheels for the common platforms.

## Build from source

If you want to build from source (e.g. to use the latest unreleased code),
you need [Rust](https://rustup.rs) and [maturin](https://github.com/PyO3/maturin):

```bash
git clone https://github.com/MohammadRaziei/mmdr.git
cd mmdr
pip install maturin
maturin develop --release
```
