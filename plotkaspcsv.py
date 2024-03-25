#!/usr/bin/env python3

"""Plot KASP CSV files.

This script makes useful plots from KlusterCaller KASP CSV files.
"""

from __future__ import annotations

import argparse
import typing
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages

if TYPE_CHECKING:
    from collections.abc import Sequence

__version__ = "1.0.0"


def main(arg: argparse.Namespace) -> None:
    """Plot KASP CSV files.

    Wrapper function used when file is run as a script.
    """
    plot(arg.files, arg.output)


class Plate:
    """Object representing a KASP microtiter plate."""

    def __init__(self: Plate, name: str, wells: list[Well]) -> None:
        """Initialise a plate instance."""
        self.name: str = name
        self.wells: list[Well] = sorted(wells, key=lambda w: w.rowcol)

    def __str__(self: Plate) -> str:
        """Return string representation of a plate instance."""
        return f"{self.num_wells()} well plate named '{self.name}'"

    def num_wells(self: Plate) -> int:
        """Get number of plate wells."""
        return len(self.wells)


class Well:
    """Object representing a KASP microtiter plate well."""

    def __init__(
        self: Well,
        rowcol: str,
        sample: str,
        fluorophores: tuple[int, int, int],
    ) -> None:
        """Initialise a well instance."""
        self.rowcol = rowcol
        self.sample = sample
        self.fam = fluorophores[0]  # FAM; excitation 485 nm; emission 520 nm
        self.hex = fluorophores[1]  # HEX; excitation 535 nm; emission 556 nm
        self.rox = fluorophores[2]  # ROX; excitation 575 nm; emission 610 nm

    def __str__(self: Well) -> str:
        """Return string representation of a well instance."""
        return (
            f"Well {self.rowcol} labelled '{self.sample}': "
            f"({self.fam}, {self.hex}, {self.rox})"
        )

    def norm_fam(self: Well) -> float:
        """Normalised FAM."""
        return self.fam / self.rox

    def norm_hex(self: Well) -> float:
        """Normalised HEX."""
        return self.hex / self.rox


def plot(files: list[typing.TextIO], output: str) -> None:
    """Plot KASP CSV files."""
    with PdfPages(output) as pdf:
        plates = [make_plate_from_file(file) for file in files]

        unnorm_fams = [w.fam for plate in plates for w in plate.wells]
        unnorm_hexs = [w.hex for plate in plates for w in plate.wells]
        norm_fams = [w.norm_fam() for plate in plates for w in plate.wells]
        norm_hexs = [w.norm_hex() for plate in plates for w in plate.wells]
        roxs = [w.rox for plate in plates for w in plate.wells]
        hues = [plate.name for plate in plates for w in plate.wells]
        wells = [w.rowcol for plate in plates for w in plate.wells]

        # Unnormalised FAM vs HEX
        _scatterplot(
            pdf,
            unnorm_fams,
            unnorm_hexs,
            hues,
            ("Unnormalised FAM vs HEX", "FAM", "HEX"),
        )

        # Normalised FAM vs HEX
        _scatterplot(
            pdf,
            norm_fams,
            norm_hexs,
            hues,
            ("Normalised FAM vs HEX", "FAM", "HEX"),
        )

        # Unnormalised FAM
        _scatterplot(
            pdf,
            wells,
            unnorm_fams,
            hues,
            ("Unnormalised FAM", "Well", "FAM"),
        )

        # Unnormalised HEX
        _scatterplot(
            pdf,
            wells,
            unnorm_hexs,
            hues,
            ("Unnormalised HEX", "Well", "HEX"),
        )

        # Normalised FAM
        _scatterplot(
            pdf,
            wells,
            norm_fams,
            hues,
            ("Normalised FAM", "Well", "FAM"),
        )

        # Normalised HEX
        _scatterplot(
            pdf,
            wells,
            norm_hexs,
            hues,
            ("Normalised HEX", "Well", "HEX"),
        )

        # ROX
        _scatterplot(
            pdf,
            wells,
            roxs,
            hues,
            ("ROX", "Well", "ROX"),
        )


def _scatterplot(
    pdf: PdfPages,
    x: Sequence[int | float | str],
    y: Sequence[int | float],
    hue: Sequence[str],
    labels: tuple[str, str, str],
) -> None:
    """Plot scatterplot."""
    plt.figure(figsize=(11.69, 8.27))  # A4
    sns.scatterplot(x=x, y=y, hue=hue)
    plt.title(labels[0])
    plt.xlabel(labels[1])
    plt.ylabel(labels[2])
    if isinstance(x[0], str):
        # If showing wells then rotate and use smaller font
        plt.xticks(rotation=90)
        plt.tick_params(labelsize=5)
    plt.plot()
    pdf.savefig()
    plt.close()


def make_plate_from_file(file: typing.TextIO) -> Plate:
    """Make plate from KlusterCaller KASP CSV file."""
    # Get name from header
    name = ""
    for line in file:
        if line.startswith("Content,"):
            break
        if line.startswith("ID1"):
            name = line.rstrip().split(": ")[1]
            name = name.split(",")[0]

    wells = []
    for line in file:
        fields = line.rstrip().split(",")
        rowcol = fields[2] + f"{int(fields[1]):02d}"
        sample = fields[0]
        fluorophores = (int(fields[3]), int(fields[4]), int(fields[5]))
        wells.append(Well(rowcol, sample, fluorophores))

    return Plate(name, wells)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "files",
        metavar="FILE",
        nargs="+",
        type=argparse.FileType("r"),
        help="CSV files",
    )
    parser.add_argument(
        "--output",
        "-o",
        dest="output",
        metavar="OUTPUT",
        type=str,
        default="kasp.pdf",
        help="the name of the output file",
    )
    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s " + __version__,
    )

    args = parser.parse_args()

    main(args)
