"""The version must have a single source of truth (Cargo.toml)."""

from importlib.metadata import version

import mmdr


def test_package_version_matches_extension_version():
    assert version("mmdr") == mmdr.__version__
