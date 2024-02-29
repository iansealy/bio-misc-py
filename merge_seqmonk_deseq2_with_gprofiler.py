#!/usr/bin/env python3

"""Merge SeqMonk DESeq2 with g:Profiler.

This script takes a tab-delimited file of DESeq2 results from SeqMonk and merges it with
a CSV file output by g:Profiler. Both files must have a header line.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

__version__ = "1.0.0"


def main(arg: argparse.Namespace) -> None:
    """Merge SeqMonk DESeq2 with g:Profiler.

    Wrapper function used when file is run as a script.
    """
    try:
        merge(arg.deseq2, arg.gprofiler, arg.deseq2_id, arg.gprofiler_id)
    except FileNotFoundError as err:
        sys.exit(f"ERROR: '{err.filename}' could not be found")
    except OSError as err:
        sys.exit(f"ERROR: '{err.filename}' could not be opened")


def merge(
    deseq2_file: str,
    gprofiler_file: str,
    deseq2_key: str,
    gprofiler_key: str,
) -> None:
    """Merge SeqMonk DESeq2 with g:Profiler."""
    # Read in DESeq2 data and store by gene ID
    deseq2_data = _read_deseq2(deseq2_file, deseq2_key)
    # Read in g:Profiler data and merge with DESeq2 data
    merged_data = _read_and_merge_gprofiler(
        deseq2_file,
        gprofiler_file,
        deseq2_key,
        gprofiler_key,
        deseq2_data,
    )
    # Print merged data as TSV
    _print_merged_data(merged_data)


def _read_deseq2(deseq2_file: str, deseq2_key: str) -> dict[str, dict[str, str]]:
    """Read in DESeq2 data and store by gene ID."""
    deseq2_data = {}
    with Path(deseq2_file).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter="\t")
        for row in reader:
            try:
                key = row.pop(deseq2_key)
            except KeyError:
                sys.exit(f"ERROR: '{deseq2_key}' column not found in '{deseq2_file}'")
            deseq2_data[key] = row
    return deseq2_data


def _read_and_merge_gprofiler(
    deseq2_file: str,
    gprofiler_file: str,
    deseq2_key: str,
    gprofiler_key: str,
    deseq2_data: dict[str, dict[str, str]],
) -> list[dict[str, str]]:
    """Read in g:Profiler data and merge with DESeq2 data."""
    merged_data: list[dict[str, str]] = []
    with Path(gprofiler_file).open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                keys = row.pop(gprofiler_key)
            except KeyError:
                sys.exit(
                    f"ERROR: '{gprofiler_key}' column not found in '{gprofiler_file}'",
                )
            try:
                merged_data.extend(
                    {**row, deseq2_key: key, **deseq2_data[key]}
                    for key in keys.split(",")
                )
            except KeyError as err:
                sys.exit(
                    "ERROR: "
                    f"{err} ID from '{gprofiler_key}' column of '{gprofiler_file}' "
                    f"not found in '{deseq2_key}' column of '{deseq2_file}'",
                )
    return merged_data


def _print_merged_data(merged_data: list[dict[str, str]]) -> None:
    """Print merged data as TSV."""
    header = merged_data[0].keys()
    writer = csv.DictWriter(
        sys.stdout,
        fieldnames=header,
        delimiter="\t",
        lineterminator="\n",
    )
    writer.writeheader()
    try:
        for row in merged_data:
            writer.writerow(row)
            sys.stdout.flush()
    except BrokenPipeError:
        # Redirect output to /dev/null to avoid broken pipe error
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 merge_seqmonk_deseq2_with_gprofiler.py SeqMonk.tsv gProfiler.csv
  python3 merge_seqmonk_deseq2_with_gprofiler.py SeqMonk.tsv gProfiler.csv > merged.tsv
  python3 merge_seqmonk_deseq2_with_gprofiler.py \\
    --deseq2-id ID --gprofiler-id intersections SeqMonk.tsv gProfiler.csv > merged.tsv
""",
    )

    parser.add_argument(
        "deseq2",
        metavar="FILE",
        type=str,
        help="a TSV DESeq2 file from SeqMonk",
    )
    parser.add_argument(
        "gprofiler",
        metavar="FILE",
        type=str,
        help="a CSV file from g:Profiler",
    )
    parser.add_argument(
        "-did",
        "--deseq2-id",
        metavar="ID",
        default="ID",
        type=str,
        help="name of gene ID column in DESeq2 file from SeqMonk",
    )
    parser.add_argument(
        "-gid",
        "--gprofiler-id",
        metavar="ID",
        default="intersections",
        type=str,
        help="name of gene IDs column in file from g:Profiler",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s " + __version__,
    )

    args = parser.parse_args()

    main(args)
