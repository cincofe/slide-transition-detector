import pytest
from pathlib import Path
from slidetd import detector

VIDEO_FILE = "tests/assets/2025-02-27 08-15-59.mkv"
OUTPUT_PATH = "tests/output/"

# ensure the output directory exists
Path(OUTPUT_PATH).mkdir(parents=True, exist_ok=True)

def test_main_no_exceptions(monkeypatch):
    # Patch argparse to avoid parsing sys.argv
    class DummyArgs:
        device = VIDEO_FILE
        # Ensure the output path ends with a slash
        outpath = str(Path(OUTPUT_PATH) / "slides") + "/"
        fileformat = ".png"
        framerate = 0.1
        threshold = 0.95
    

    monkeypatch.setattr("argparse.ArgumentParser.parse_args", lambda self: DummyArgs())

    # Should not raise any exceptions
    try:
        detector.main()
    except Exception as e:
        pytest.fail(f"detector.main() raised an exception: {e}")
