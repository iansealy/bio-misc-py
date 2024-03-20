"""Remove Superfluous Columns."""

import io
import runpy
import sys

import pytest

from removesuperfluouscols import remove


def test_remove(capfd: pytest.CaptureFixture[str]) -> None:
    """Test removing superfluous columns."""
    input_tsv = """a b 1 1
a b 2 2
a c 3 3
a c 4 4
a c 5 5
a c 6 6
a c 7 7
""".replace(
        " ",
        "\t",
    )

    expected_tsv = """b 1
b 2
c 3
c 4
c 5
c 6
c 7
""".replace(
        " ",
        "\t",
    )
    remove(io.StringIO(input_tsv), noheader=True)
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv
    remove(io.StringIO(input_tsv), noheader=False)
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv


def test_script() -> None:
    """Test running script."""
    args = [
        ["removesuperfluouscols.py", "-h"],
    ]
    for argv in args:
        sys.argv = argv
        with pytest.raises(SystemExit):
            runpy.run_module("removesuperfluouscols", run_name="__main__")
    sys.argv = ["removesuperfluouscols.py", "removesuperfluouscols.py"]
    runpy.run_module("removesuperfluouscols", run_name="__main__")
