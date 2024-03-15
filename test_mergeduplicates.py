"""Merge TSV Duplicates."""

import io
import runpy
import sys

import pytest

from mergeduplicates import merge


def test_merge(capfd: pytest.CaptureFixture[str]) -> None:
    """Test merging TSV duplicates."""
    input_tsv = """a b 1 2 3 4
a b 5 6 7 8
a c 1 2 3 4
""".replace(
        " ",
        "\t",
    )

    # No arguments so key is empty and all lines are merged
    # (not possible if run as a script)
    expected_tsv = """a b,b,c 1,5,1 2,6,2 3,7,3 4,8,4
""".replace(
        " ",
        "\t",
    )
    merge(io.StringIO(input_tsv), header=False)
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    # Key is first two columns
    expected_tsv = """a b 1,5 2,6 3,7 4,8
a c 1 2 3 4
""".replace(
        " ",
        "\t",
    )
    merge(io.StringIO(input_tsv), header=False, keys=[1, 2])
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    # Key is 1st and 6th columns
    expected_tsv = """a b,c 1 2 3 4
a b 5 6 7 8
""".replace(
        " ",
        "\t",
    )
    merge(io.StringIO(input_tsv), header=False, keys=[1, 6])
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    # Sum 3rd and 4th and get mean of 5th and 6th without floats
    expected_tsv = """a b 6 8 5 6
a c 1 2 3 4
""".replace(
        " ",
        "\t",
    )
    merge(io.StringIO(input_tsv), header=False, keys=[1, 2], sums=[3, 4], means=[5, 6])
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    # Minimum of 3rd and 4th and maximum of 5th and 6th
    expected_tsv = """a b 1 2 7 8
a c 1 2 3 4
""".replace(
        " ",
        "\t",
    )
    merge(io.StringIO(input_tsv), header=False, keys=[1, 2], mins=[3, 4], maxs=[5, 6])
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    # 2nd field can't be summed because is not numeric
    expected_err = r"field 2 is not numeric \('b'\)"
    with pytest.raises(SystemExit, match=expected_err):
        merge(io.StringIO(input_tsv), header=False, keys=[1], sums=[2])

    # Unknown action specified
    expected_err = r"unknown action specified: \['unknown'\]"
    with pytest.raises(KeyError, match=expected_err):
        merge(io.StringIO(input_tsv), header=False, keys=[1], sums=[3], unknown=[4])

    # Sum 3rd and 4th and get mean of 5th and 6th with floats
    input_tsv = """a b 1.5 2 3 4
a b 5.5 6.5 8 8
a c 1.5 2 3 4.5
""".replace(
        " ",
        "\t",
    )
    expected_tsv = """a b 7 8.5 5.5 6
a c 1.5 2 3 4.5
""".replace(
        " ",
        "\t",
    )
    merge(io.StringIO(input_tsv), header=False, keys=[1, 2], sums=[3, 4], means=[5, 6])
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    # 5th column is empty
    input_tsv = """a b 1 2  4
a b 5 6  8
a c 1 2  4
""".replace(
        " ",
        "\t",
    )
    expected_tsv = """a b 1,5 2,6  4,8
a c 1 2  4
""".replace(
        " ",
        "\t",
    )
    merge(io.StringIO(input_tsv), header=False, keys=[1, 2])
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    # 5th column is partially empty
    input_tsv = """a b 1 2  4
a b 5 6 7 8
a c 1 2  4
""".replace(
        " ",
        "\t",
    )
    expected_tsv = """a b 1,5 2,6 7 4,8
a c 1 2  4
""".replace(
        " ",
        "\t",
    )
    merge(io.StringIO(input_tsv), header=False, keys=[1, 2])
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv

    # Header kept
    input_tsv = """A B C D E F
a b 1 2 3 4
a b 5 6 7 8
a c 1 2 3 4
""".replace(
        " ",
        "\t",
    )
    expected_tsv = """A B C D E F
a b,b,c 1,5,1 2,6,2 3,7,3 4,8,4
""".replace(
        " ",
        "\t",
    )
    merge(io.StringIO(input_tsv), header=True)
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv


def test_script() -> None:
    """Test running script."""
    args = [
        ["mergeduplicates.py"],
        ["mergeduplicates.py", "-h"],
        ["mergeduplicates.py", "-k", "1", "-s", "1"],
        ["mergeduplicates.py", "-k", "1", "-m", "1"],
        ["mergeduplicates.py", "-k", "1", "-s", "2", "-m", "2"],
    ]
    for argv in args:
        sys.argv = argv
        with pytest.raises(SystemExit):
            runpy.run_module("mergeduplicates", run_name="__main__")
    sys.argv = ["mergeduplicates.py", "-k", "1", "mergeduplicates.py"]
    runpy.run_module("mergeduplicates", run_name="__main__")
