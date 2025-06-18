import pytest
from pathlib import Path
from slidetd import extractor

INPUT_PATH = "tests/output/unique/"
OUTPUT_PATH = "tests/output/contents/"

# ensure the output directory exists
Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

def test_main_no_exceptions(monkeypatch):
    # Patch argparse to avoid parsing sys.argv
    class DummyArgs:
        inputslides = INPUT_PATH
        outpath = OUTPUT_PATH
        lang = "it"

    monkeypatch.setattr("argparse.ArgumentParser.parse_args", lambda self: DummyArgs())

    # Should not raise any exceptions
    try:
        extractor.main()
    except Exception as e:
        pytest.fail(f"extractor.main() raised an exception: {e}")


