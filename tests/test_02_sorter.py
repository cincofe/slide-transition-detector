import pytest
from pathlib import Path
from slidetd import sorter

INPUT_SLIDES = "tests/output/slides/"
OUTPUT_PATH = "tests/output/unique/"

# ensure the output directory exists
Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

def test_main_no_exceptions(monkeypatch):
    # Patch argparse to avoid parsing sys.argv
    class DummyArgs:
        inputslides = INPUT_SLIDES
        outpath = OUTPUT_PATH
        fileformat = ".png"
        timetable = None

    monkeypatch.setattr("argparse.ArgumentParser.parse_args", lambda self: DummyArgs())

    # Should not raise any exceptions
    try:
        sorter.main()
    except Exception as e:
        pytest.fail(f"sorter.main() raised an exception: {e}")
