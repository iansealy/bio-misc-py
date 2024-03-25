# mypy: warn_unused_ignores=False

"""Plot KASP CSV files."""

import runpy
import sys
from pathlib import Path

import pytest
from diff_pdf_visually import pdf_similar  # type: ignore[import-untyped]

from plotkaspcsv import make_plate_from_file, plot

TEST_PLATE_WELLS = 4


def test_plot(tmp_path: Path) -> None:
    """Test plotting KASP CSV files."""
    with Path("test_plotkaspcsv/plt1.csv").open("r", encoding="utf-8") as file1, Path(
        "test_plotkaspcsv/plt2.csv",
    ).open("r", encoding="utf-8") as file2:
        plot([file1, file2], str(Path(tmp_path / "kasp.pdf")))
        assert Path(tmp_path / "kasp.pdf").exists()
        Path(tmp_path / "diff").mkdir()
        assert pdf_similar(
            "test_plotkaspcsv/kasp.pdf",
            Path(tmp_path / "kasp.pdf"),
            tempdir=Path(tmp_path / "diff"),
        )


def test_make_plate_from_file() -> None:
    """Test making plate from KlusterCaller KASP CSV file."""
    with Path("test_plotkaspcsv/plt1.csv").open("r", encoding="utf-8") as file:
        plate = make_plate_from_file(file)
        assert plate.num_wells() == TEST_PLATE_WELLS
        assert str(plate) == "4 well plate named 'test1'"
        assert str(plate.wells[0]) == "Well A01 labelled 'S1': (10, 20, 5)"
    with Path("plotkaspcsv.py").open("r", encoding="utf-8") as file:
        plate = make_plate_from_file(file)
        assert plate.name == ""
        assert plate.wells == []


def test_script(tmp_path: Path) -> None:
    """Test running script."""
    args = [
        ["plotkaspcsv.py"],
        ["plotkaspcsv.py", "-h"],
    ]
    for argv in args:
        sys.argv = argv
        with pytest.raises(SystemExit):
            runpy.run_module("plotkaspcsv", run_name="__main__")
    sys.argv = [
        "plotkaspcsv.py",
        "-o",
        str(Path(tmp_path / "kasp.pdf")),
        "test_plotkaspcsv/plt1.csv",
        "test_plotkaspcsv/plt2.csv",
    ]
    runpy.run_module("plotkaspcsv", run_name="__main__")
