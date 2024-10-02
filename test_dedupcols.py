"""Deduplicate Columns."""

import io
import runpy
import sys

import pytest

from dedupcols import deduplicate


def test_deduplicate(capfd: pytest.CaptureFixture[str]) -> None:
    """Test deduplicating columns."""
    input_tsv = """a b c d
a 1 1 1
b 3 2 2
c 4 3 3
""".replace(
        " ",
        "\t",
    )

    expected_tsv = """a b-c-d
a 1
b 2;3
c 3;4
""".replace(
        " ",
        "\t",
    )
    deduplicate(io.StringIO(input_tsv), noheader=False, keys=[1], dedupcols=[2, 3, 4])
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    expected_tsv = """a b;c;d
a 1
b 2;3
c 3;4
""".replace(
        " ",
        "\t",
    )
    deduplicate(io.StringIO(input_tsv), noheader=True, keys=[1], dedupcols=[2, 3, 4])
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    expected_tsv = """a b-c-d
a 1
b 2
c 4
""".replace(
        " ",
        "\t",
    )
    deduplicate(
        io.StringIO(input_tsv),
        noheader=False,
        keys=[1],
        dedupcols=[2, 3, 4],
        prefixes=["3"],
    )
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv


def test_script() -> None:
    """Test running script."""
    args = [
        ["dedupcols.py", "-h"],
    ]
    for argv in args:
        sys.argv = argv
        with pytest.raises(SystemExit):
            runpy.run_module("dedupcols", run_name="__main__")
    sys.argv = ["dedupcols.py", "dedupcols.py", "-k", "1", "-c", "2"]
    runpy.run_module("dedupcols", run_name="__main__")
