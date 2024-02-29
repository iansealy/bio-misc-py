"""Merge SeqMonk DESeq2 with g:Profiler."""

import runpy
import sys

import pytest

from merge_seqmonk_deseq2_with_gprofiler import merge

TESTDIR = "test_merge_seqmonk_deseq2_with_gprofiler"


def test_merge(capfd: pytest.CaptureFixture[str]) -> None:
    """Test merging TSV duplicates."""
    expected_tsv = """Term ID pval
GO1 ENS1 0.01
GO2 ENS1 0.01
GO2 ENS2 0.02
GO3 ENS2 0.02
""".replace(
        " ",
        "\t",
    )
    merge(TESTDIR + "/test1_deseq2.tsv", TESTDIR + "/test1_gprofiler.csv", "ID", "IDs")
    captured_tsv = capfd.readouterr().out
    assert captured_tsv == expected_tsv


def test_script() -> None:
    """Test running script."""
    args = [
        ["merge_seqmonk_deseq2_with_gprofiler.py"],
        ["merge_seqmonk_deseq2_with_gprofiler.py", "-h"],
        [
            "merge_seqmonk_deseq2_with_gprofiler.py",
            "missing.tsv",  # Doesn't exist
            "test_merge_seqmonk_deseq2_with_gprofiler",
        ],
        [
            "merge_seqmonk_deseq2_with_gprofiler.py",
            "test_merge_seqmonk_deseq2_with_gprofiler",  # Can't be opened
            "missing.csv",
        ],
        [
            "merge_seqmonk_deseq2_with_gprofiler.py",
            "-did",
            "missing",  # Not in file
            "-gid",
            "IDs",
            TESTDIR + "/test1_deseq2.tsv",
            TESTDIR + "/test1_gprofiler.csv",
        ],
        [
            "merge_seqmonk_deseq2_with_gprofiler.py",
            "-did",
            "ID",
            "-gid",
            "missing",  # Not in file
            TESTDIR + "/test1_deseq2.tsv",
            TESTDIR + "/test1_gprofiler.csv",
        ],
        [
            "merge_seqmonk_deseq2_with_gprofiler.py",
            "-did",
            "ID",
            "-gid",
            "IDs",
            TESTDIR + "/test2_deseq2.tsv",  # Missing ID
            TESTDIR + "/test1_gprofiler.csv",
        ],
    ]
    for argv in args:
        sys.argv = argv
        with pytest.raises(SystemExit):
            runpy.run_module("merge_seqmonk_deseq2_with_gprofiler", run_name="__main__")
    sys.argv = [
        "merge_seqmonk_deseq2_with_gprofiler.py",
        "-did",
        "ID",
        "-gid",
        "IDs",
        TESTDIR + "/test1_deseq2.tsv",
        TESTDIR + "/test1_gprofiler.csv",
    ]
    runpy.run_module("merge_seqmonk_deseq2_with_gprofiler", run_name="__main__")
