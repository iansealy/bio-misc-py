#!/usr/bin/env python3

"""Deduplicate Columns.

This script takes a tab-delimited file on either STDIN or as an
argument and removes duplicate values across specified columns.
It also indentifies where a value appears in more than one row.
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
import typing
from collections import defaultdict

__version__ = "1.0.0"


logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


def main(arg: argparse.Namespace) -> None:
    """Deduplicate Columns.

    Wrapper function used when file is run as a script.
    """
    deduplicate(
        arg.file,
        noheader=arg.noheader,
        keys=arg.keys,
        dedupcols=arg.dedupcols,
        prefixes=arg.prefixes,
    )


def deduplicate(
    file: typing.TextIO,
    *,
    noheader: bool,
    keys: typing.Sequence[int] = (),
    dedupcols: typing.Sequence[int] = (),
    prefixes: typing.Sequence[str] = (),
) -> None:
    """Deduplicate Columns."""
    try:
        # Get any header
        if not noheader:
            _print_header(file, dedupcols)
        # Iterate over file
        potential_row_dupes = _print_body(file, keys, dedupcols, prefixes)
    except BrokenPipeError:
        # Redirect output to /dev/null to avoid broken pipe error
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(1)

    row_dupes = {
        dupe: keys for dupe, keys in potential_row_dupes.items() if len(keys) > 1
    }
    for dupe_field, dupe_keys in row_dupes.items():
        logging.info("Field %s appears in: %s", dupe_field, "; ".join(dupe_keys))


def _print_header(file: typing.TextIO, dedupcols: typing.Sequence[int]) -> None:
    """Print header."""
    header = file.readline().rstrip().split("\t")
    last_header = "-".join(
        field for i, field in enumerate(header) if i + 1 in dedupcols
    )
    header = [field for i, field in enumerate(header) if i + 1 not in dedupcols]
    header.append(last_header)
    print("\t".join(header))


def _print_body(
    file: typing.TextIO,
    keys: typing.Sequence[int] = (),
    dedupcols: typing.Sequence[int] = (),
    prefixes: typing.Sequence[str] = (),
) -> defaultdict[str, set[str]]:
    """Print body."""
    potential_row_dupes = defaultdict(set)
    for line in file:
        fields = line.rstrip().split("\t")
        key = " ".join(field for i, field in enumerate(fields) if i + 1 in keys)
        output_fields = [
            field for i, field in enumerate(fields) if i + 1 not in dedupcols
        ]
        dedup_fields = {
            field
            for i, field in enumerate(fields)
            if i + 1 in dedupcols and field != "-"
        }
        for field in dedup_fields:
            potential_row_dupes[field].add(key)
        for prefix in prefixes:
            dedup_fields = {
                field for field in dedup_fields if not field.startswith(prefix)
            }
        if not dedup_fields:
            logging.info("No fields left for: %s", key)
            dedup_fields = {"-"}
        output_fields.append(";".join(sorted(dedup_fields)))
        print("\t".join(output_fields))
        sys.stdout.flush()
    return potential_row_dupes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 dedupcols.py -k 1 -c 2 -c 3 -c 4 < in.tsv > out.tsv

If in.tsv is:

a   1   1   1
b   3   2   2
c   4   3   3

Then "python3 dedupcols.py --noheader -k 1 -c 2 -c 3 -c 4 < in.tsv"
will produce:

a   1
b   2;3
c   3;4

And will flag up that the value 3 appears for both b and c.""",
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
        "--key",
        "-k",
        action="extend",
        dest="keys",
        metavar="FLD",
        nargs=1,
        type=int,
        required=True,
        help="the field(s) specifying the key for identifying duplicates across rows",
    )
    parser.add_argument(
        "--cols",
        "-c",
        action="extend",
        dest="dedupcols",
        metavar="FLD",
        nargs=1,
        type=int,
        required=True,
        help="the field(s) to be deduplicated",
    )
    parser.add_argument(
        "--prefixes",
        "-p",
        action="extend",
        dest="prefixes",
        metavar="FLD",
        nargs=1,
        type=str,
        default=[],
        help="values with any of these prefixes will be removed",
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
