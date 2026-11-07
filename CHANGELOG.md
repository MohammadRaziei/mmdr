# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.4.1] - 2026-11-08

### Fixed
- `import mmdr` raised `TypeError` on Python 3.9, which the package declares as supported: the
  `str | None` annotation in `mmdr/__init__.py` was evaluated at import time. Added
  `from __future__ import annotations`.
- `examples/test.py` still called `mmdr.render_png()`, which was removed in 0.4.0.

### Documentation
- Rewrote the README: runnable example first, benchmark table from the
  [mermaidx benchmark](https://mohammadraziei.github.io/mermaidx/benchmarks) with its caveats, and a
  diagram that shows who does what.
- Removed claims the benchmark does not back from the docs ("100–1400x faster", "~0ms startup",
  "~7 MB wheel").
- Corrected the diagram-support tables: both backends render all the listed types, and
  `mermaid-rs-renderer` differs by rejecting some syntax, not whole diagram types.
- Docs now say novasvg is pinned to 0.11.5 instead of `>=0.10`.

### Changed
- Dependencies are now pinned to exact versions: `pyo3 =0.30.1`, `mermaid-rs-renderer =0.3.1`
  and `merman =0.9.3` in `Cargo.toml`, and `novasvg==0.11.5` in `pyproject.toml` (and in the
  CI test job), so builds and test runs are reproducible.
- Updated backend `merman` 0.9.0 → 0.9.3 and `pyo3` 0.30 → 0.30.1 (no code changes were needed).
- Package description now says that both backends, `mermaid-rs-renderer` and `merman`, are
  supported.
- Tuned the `release` profile for a smaller binary without slowing rendering:
  `lto = "fat"`, `codegen-units = 1`, `panic = "abort"` (plus the existing `strip = true`).
  In local tests on x86_64 the wheel shrank by about 7% (11.93 MB → 11.13 MB, both backends)
  with the same render speed as before; all features of both backends are unchanged.
- A panic inside the Rust extension now aborts the Python process instead of being raised as
  `pyo3_runtime.PanicException`. Invalid diagrams still raise `ValueError` as before.

### Added
- Test coverage (branch coverage of the Python package) is now measured in CI with
  `pytest-cov`. The report is printed in the job log, shown in the job summary and uploaded as a
  `coverage-xml` artifact. Settings are in `.coveragerc`. Coverage of the Rust extension is not
  measured.

## [0.4.0] - 2026-10-17

### Changed
- **Breaking:** rasterization (PNG / raw pixels / NumPy) no longer uses `resvg`.
  It is now done in Python with [novasvg](https://mohammadraziei.github.io/novasvg/)
  `>=0.11`, which is a new required dependency. The Rust extension only produces SVG.
  NumPy stays optional and is only needed by `.numpy()` (`pip install mmdr[numpy]`).
- **Breaking:** the `mermaid-rs` backend now raises `ValueError` on invalid
  diagrams (mermaid-rs-renderer 0.3), like `merman`, instead of returning an error SVG.
- `width` / `height` now actually scale the output image. If only one is given,
  the other follows the aspect ratio. Previously they were only a size hint.
- `.raw()` and `.numpy()` now return straight (non-premultiplied) RGBA.
- Updated backends: `merman` 0.7.0 → 0.9.0 and `mermaid-rs-renderer` 0.2.2 → 0.3.1.
  `merman` 0.9 requires Rust 1.95 or newer to build from source.
- Updated `pyo3` 0.22 → 0.30 (no code changes were needed).

### Removed
- `resvg` and `usvg` dependencies, and the `raster` feature of `merman`.
- **Breaking:** `mmdr.svg_to_png()` and `mmdr.svg_to_raw()` (and the Rust functions behind them).
  mmdr only renders Mermaid now; to rasterize an arbitrary SVG string use novasvg directly
  (`novasvg.Document.load_from_data(svg).render_to_bitmap(...)`). `Diagram.png()`,
  `.raw()` and `.numpy()` are unchanged.

### Fixed
- `mmdr.__version__` / `mmdr --version` reported `0.1.0` because `Cargo.toml` was out of sync
  with `pyproject.toml`. The version now lives only in `Cargo.toml` (`pyproject.toml` declares it
  as `dynamic`), so the two can no longer drift apart.
- Package metadata (author, e-mail, project URLs, classifiers) was left over from a template
  and pointed at another project; it now matches this repository.
- An invalid `background` color now raises `ValueError` instead of being ignored.

### Documentation
- Removed the pinned "Mermaid @11.15.0" parity claim; the baseline is defined by the `merman` crate.
- Documented the new novasvg dependency and the new size / alpha behaviour.

## [0.3.0] - 2026-07-05

### Added
- Python API documentation and usage examples.
- Docs deployment step in the publish workflow.

### Changed
- MkDocs theme palette and toggle icons.
- Updated project description.

## [0.2.0] - 2026-07-05

### Changed
- Restructured the Python source directory.
- CI: re-enabled the `pyproject.toml` removal step before running tests in the publish workflow.

## [0.1.0] - 2026-07-04

First public release.

### Added
- Python bindings for Mermaid rendering with two SVG backends:
  `mermaid-rs-renderer` and `merman` (full Mermaid parity), with backend selection.
- PNG and raw-pixel output.
- Command-line interface with input handling improvements and a `--version` flag.
- `--info` flag that renders Mermaid's built-in info diagram and extracts its text.
- `Diagram` class with lazy rendering and a richer API.
- pytest configuration and test suite.
- README with CLI and Python API documentation.
- GitHub Actions workflow that builds wheels, runs tests, publishes to PyPI and automates releases.

### Changed
- `Cargo.lock` is no longer tracked.

### Fixed
- Several publish-workflow issues (build matrix formatting, `maturin` flags,
  `pytest` invocation and working directory).

[Unreleased]: https://github.com/mohammadraziei/mmdr/compare/v0.4.1...HEAD
[0.4.1]: https://github.com/mohammadraziei/mmdr/compare/v0.4.0...v0.4.1
[0.4.0]: https://github.com/mohammadraziei/mmdr/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/mohammadraziei/mmdr/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mohammadraziei/mmdr/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mohammadraziei/mmdr/releases/tag/v0.1.0
