"""Merge TSV Duplicates."""

import io

import pytest

from mergeduplicates import merge


def test_merge(capfd: pytest.CaptureFixture) -> None:
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

    # 2nd field can't be summed because is not numeric
    expected_err = r"field 2 is not numeric \('b'\) so can't be summed or averaged"
    with pytest.raises(SystemExit, match=expected_err):
        merge(io.StringIO(input_tsv), header=False, keys=[1], sums=[2])

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
