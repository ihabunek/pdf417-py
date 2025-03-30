import pytest

def pytest_collect_file(parent, file_path):
    try:
        import pdf417decoder
    except ImportError:
        # If PDF417Decoder is not installed, don't collect any tests from this directory
        if str(file_path).startswith(str(parent.fspath) + "/integration"):
            return None