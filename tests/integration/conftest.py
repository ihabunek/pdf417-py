import pytest
import os
# Perform the import check once when pytest starts
dependency_missing = False
dependency_import_error = None
try:
    # Use __import__ for dynamic import checking based on the string name
    import pdf417decoder
    print(f"\nINFO: Optional dependency 'pdf417decoder' found. "
          f"Integration tests in will be collected.")
except ImportError as e:
    dependency_missing = True
    dependency_import_error = e
    print(f"\nWARNING: Optional dependency 'pdf417decoder' not found (Error: {e}). "
          f"Integration tests in 'integration/' will be skipped.")

# Define the reason message for skipping
skip_reason = f"Skipping integration tests: Optional dependency 'pdf417decoder' not found."

def pytest_collection_modifyitems(config, items):
    """
    Hook to modify the list of collected test items.

    Skips tests if pdf417decoder is not installed.
    """
    if not dependency_missing:
        # Dependency was found, don't skip anything based on this condition
        return

    skip_marker = pytest.mark.skip(reason=skip_reason)

    integration_path_prefix = "tests/integration/"

    for item in items:
        # item.location[0] usually gives the file path relative to the rootdir
        if item.location[0].startswith(integration_path_prefix):
            item.add_marker(skip_marker)
