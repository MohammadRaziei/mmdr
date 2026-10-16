"""PNG and raw output must work without NumPy installed (it is optional)."""

import subprocess
import sys
import textwrap


def run_without_numpy(code: str) -> subprocess.CompletedProcess:
    # Setting sys.modules["numpy"] = None makes `import numpy` raise ImportError.
    prologue = "import sys; sys.modules['numpy'] = None\n"
    return subprocess.run(
        [sys.executable, "-c", prologue + textwrap.dedent(code)],
        capture_output=True,
        text=True,
    )


def test_png_and_raw_work_without_numpy():
    result = run_without_numpy(
        """
        import mmdr
        d = mmdr.render("flowchart LR; A-->B")
        assert d.png(background="#ffffff")[:8] == b"\\x89PNG\\r\\n\\x1a\\n"
        raw, w, h = d.raw()
        assert len(raw) == w * h * 4
        """
    )
    assert result.returncode == 0, result.stderr


def test_numpy_method_gives_a_clear_error_without_numpy():
    result = run_without_numpy(
        """
        import mmdr
        try:
            mmdr.render("flowchart LR; A-->B").numpy()
        except ImportError as e:
            assert "pip install numpy" in str(e)
        else:
            raise SystemExit("expected ImportError")
        """
    )
    assert result.returncode == 0, result.stderr
