# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Changed
- **Breaking:** rasterization (PNG / raw pixels / NumPy) no longer uses `resvg`.
  It is now done in Python with [novasvg](https://mohammadraziei.github.io/novasvg/)
  `>=0.10`, which is a new required dependency, together with `numpy>=1.20`
  (needed to read raw pixels from novasvg). The Rust extension only produces SVG.
- **Breaking:** the `mermaid-rs` backend now raises `ValueError` on invalid
  diagrams (mermaid-rs-renderer 0.3), like `merman`, instead of returning an error SVG.
- `width` / `height` now actually scale the output image. If only one is given,
  the other follows the aspect ratio. Previously they were only a size hint.
- `.raw()` and `.numpy()` now return straight (non-premultiplied) RGBA.
- Updated backends: `merman` 0.7.0 → 0.9.0 and `mermaid-rs-renderer` 0.2.2 → 0.3.1.
  `merman` 0.9 requires Rust 1.95 or newer to build from source.

### Removed
- `resvg` and `usvg` dependencies, and the `raster` feature of `merman`.
- `mmdr._mmdr.svg_to_png` / `svg_to_raw` in the Rust extension
  (`mmdr.svg_to_png` and `mmdr.svg_to_raw` remain available, now implemented in Python).

### Fixed
- `mmdr.__version__` / `mmdr --version` reported `0.1.0` because `Cargo.toml` was out of sync
  with `pyproject.toml`. The version now lives only in `Cargo.toml` (`pyproject.toml` declares it
  as `dynamic`), so the two can no longer drift apart.
- Package metadata (author, e-mail, project URLs, classifiers) was left over from a template
  and pointed at another project; it now matches this repository.
- An invalid `background` color now raises `ValueError` instead of being ignored.
- Invalid SVG input raises `ValueError` with a clear message.

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

[Unreleased]: https://github.com/mohammadraziei/mmdr/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/mohammadraziei/mmdr/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/mohammadraziei/mmdr/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/mohammadraziei/mmdr/releases/tag/v0.1.0
