#!/usr/bin/env python3

"""Remove Superfluous Columns.

This script takes a tab-delimited file on either STDIN or as an
argument and looks for and removes superfluous columns. A superfluous
column is one that either contains a single repeated value or is
identical to another column.

Warning: The whole file is read into memory.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import typing

__version__ = "1.0.0"


logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)
NUM_UNIQUE_DATA_TO_SHOW = 5


def main(arg: argparse.Namespace) -> None:
    """Remove Superfluous Columns.

    Wrapper function used when file is run as a script.
    """
    remove(
        arg.file,
        noheader=arg.noheader,
    )


def remove(
    file: typing.TextIO,
    *,
    noheader: bool,
) -> None:
    """Remove Superfluous Columns."""
    # Get any header
    header = []
    if not noheader:
        header = file.readline().rstrip().split("\t")

    # Convert file to list of columns
    data = _get_file_as_cols(file)

    drop_cols: set[int] = set()
    # Look for columns that contain a single repeated value
    drop_cols = _get_single_value_cols(data, drop_cols)
    # Look for duplicate columns
    drop_cols = _get_dupe_cols(data, drop_cols)

    # Remove superfluous columns
    data, msgs = _remove_cols(data, drop_cols, header)

    # Print new file
    try:
        if header:
            print("\t".join(header))
        for i in range(len(data[0])):
            row = [col[i] for col in data]
            print("\t".join(row))
            sys.stdout.flush()
    except BrokenPipeError:
        # Redirect output to /dev/null to avoid broken pipe error
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)

    # Print removed columns
    for msg in reversed(msgs):
        logging.info(msg)
    if msgs:
        logging.info("Number of columns removed: %d", len(msgs))


def _get_file_as_cols(file: typing.TextIO) -> list[list[str]]:
    """Convert file to list of columns."""
    data: list[list[str]] = []
    for line in file:
        fields = line.rstrip().split("\t")
        if not data:
            data = [[] for field in fields]
        for d, f in zip(data, fields):
            d.append(f)
    return data


def _get_single_value_cols(data: list[list[str]], drop_cols: set[int]) -> set[int]:
    """Look for columns that contain a single repeated value."""
    for i, col in enumerate(data):
        if len(set(col)) == 1:
            drop_cols.add(i)
    return drop_cols


def _get_dupe_cols(data: list[list[str]], drop_cols: set[int]) -> set[int]:
    """Look for duplicate columns."""
    for i, col1 in enumerate(data):
        for j, col2 in enumerate(data):
            if j <= i:
                continue
            if col1 == col2:
                drop_cols.add(j)
    return drop_cols


def _remove_cols(
    data: list[list[str]],
    drop_cols: set[int],
    header: list[str],
) -> tuple[list[list[str]], list[str]]:
    """Remove superfluous columns."""
    msgs = []
    for i in sorted(drop_cols, reverse=True):
        msgs.append(f"Removed column {i + 1}")
        if header:
            msgs[-1] += " (" + header[i] + ")"
            del header[i]
        col = ["'" + field + "'" for field in sorted(set(data[i]))]
        msgs[-1] += ": " + ", ".join(col[slice(NUM_UNIQUE_DATA_TO_SHOW)])
        if len(col) > NUM_UNIQUE_DATA_TO_SHOW:
            msgs[-1] += ", ..."
        del data[i]
    return data, msgs


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 removesuperfluouscols.py < in.tsv > out.tsv

If in.tsv is:

a   b   1   1
a   b   2   2
a   c   3   3

Then "python3 removesuperfluouscols.py --noheader < in.tsv"
will produce:

b   1
b   2
c   3""",
    )

    parser.add_argument(
        "file",
        metavar="FILE",
        nargs="?",
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="a tab-delimited file",
    )
    parser.add_argument(
        "--noheader",
        action="store_true",
        help="tab-delimited file has no header line",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s " + __version__,
    )

    args = parser.parse_args()

    main(args)
