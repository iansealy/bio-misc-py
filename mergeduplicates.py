#!/usr/bin/env python3

"""Merge TSV Duplicates.

This script takes a tab-delimited file on either STDIN or as an
argument and looks for duplicates specified by a key of one or more
fields. Duplicates are removed and all other fields are merged. By
default fields are merged by comma separation (collapsed to a single
value if all the same), but numerical fields can optionally be merged
by summing or taking a mean.
"""

import argparse
import collections
import sys
import typing

__version__ = "1.0.0"


def main(args: argparse.Namespace) -> None:
    """Merge TSV Duplicates.

    Wrapper function used when file is run as a script.
    """
    merge(
        args.file,
        header=args.header,
        keys=args.keys,
        sums=args.sums,
        means=args.means,
    )


def merge(
    file: typing.TextIO,
    *,
    header: bool,
    keys: typing.Sequence = (),
    sums: typing.Sequence = (),
    means: typing.Sequence = (),
) -> None:
    """Merge TSV Duplicates."""
    # Print header?
    if header:
        print(file.readline().rstrip())

    # Read file and organise lines by key
    data = _group_by_key(file, keys)

    for key in data:
        # If key is unique then can just print line
        if len(data[key]) == 1:
            print("\t".join(data[key][0]))
            continue

        output = []
        for i in range(len(data[key][0])):
            if i + 1 in keys:
                # If field is a key then just add to output
                output.append(data[key][0][i])
                continue
            if i + 1 in sums or i + 1 in means:
                # If field needs to summed or averaged then convert to float
                flt_values = _conv_to_float(data[key], i)
                flt_val: float = sum(flt_values)
                if i + 1 in means:
                    flt_val /= len(flt_values)
                str_val = str(int(flt_val)) if flt_val.is_integer() else str(flt_val)
            else:
                # Otherwise field can be merged with comma separators or collapsed
                str_values = [fields[i] for fields in data[key] if len(fields[i]) > 0]
                if len(set(str_values)) == 1:
                    str_val = str_values[0]
                else:
                    str_val = ",".join(str_values)
            output.append(str_val)
        print("\t".join(output))


def _group_by_key(
    file: typing.TextIO,
    keys: typing.Sequence,
) -> collections.OrderedDict:
    """Group all lines in file by key."""
    data = collections.OrderedDict()
    for line in file:
        fields = line.rstrip().split("\t")
        key = "\t".join([fields[k - 1] for k in keys])
        if key not in data:
            data[key] = [fields]
        else:
            data[key].append(fields)
    return data


def _conv_to_float(data: list, i: int) -> list[float]:
    """Convert column to floats."""
    try:
        values = [float(fields[i]) for fields in data if len(fields[i]) > 0]
    except ValueError as err:
        field = i + 1
        string = str(err).split(": ")[1]
        msg = (
            f"error: field {field} is not numeric ({string})"
            " so can't be summed or averaged"
        )
        raise SystemExit(msg) from err
    return values


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Each option can be repeated for specifying multiple fields.

Examples:
  python3 mergeduplicates.py --key 1 < in.tsv > out.tsv
  python3 mergeduplicates.py --key 1 --sum 3 --mean 4 < in.tsv > out.tsv
  python3 mergeduplicates.py -k 1 -k 2 -s 3 -m 4 -m 5 in.tsv > out.tsv

If in.tsv is:

a   b   c   1   2
a   b   d   3   4
a   e   f   5   6

Then "python3 mergeduplicates.py --key 1 --key 2 --mean 4 < in.tsv"
will produce:

a   b   c,d 2   2,4
a   e   f   5   6""",
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
        help="the field(s) specifying the key for identifying duplicates",
    )
    parser.add_argument(
        "--sum",
        "-s",
        action="extend",
        dest="sums",
        metavar="FLD",
        nargs=1,
        type=int,
        default=[],
        help="the field(s) to be merged by summing the values",
    )
    parser.add_argument(
        "--mean",
        "-m",
        action="extend",
        dest="means",
        metavar="FLD",
        nargs=1,
        type=int,
        default=[],
        help="the field(s) to be merged by taking the mean of the values",
    )
    parser.add_argument(
        "--header",
        action="store_true",
        help="tab-delimited file has initial header line to be printed first",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s " + __version__,
    )

    args = parser.parse_args()

    if len(args.keys) + len(args.sums) != len(set(args.keys + args.sums)):
        parser.error("fields to be summed cannot also be keys")
    if len(args.keys) + len(args.means) != len(set(args.keys + args.means)):
        parser.error("fields to be averaged cannot also be keys")
    if len(args.sums) + len(args.means) != len(set(args.sums + args.means)):
        parser.error("fields cannot be both summed and averaged")

    main(args)
