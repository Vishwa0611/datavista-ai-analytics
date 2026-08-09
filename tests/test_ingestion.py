"""
Tests for ingestion module.
"""
import io
import sys
from pathlib import Path
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

import pandas as pd
from src.ingestion.loader import read_file
from src.ingestion.validators import validate_file_extension, validate_file_size

def test_valid_csv():
    csv_content = b"a,b,c\n1,2,3\n4,5,6"
    result = read_file(csv_content, "test.csv")
    assert result.df.shape == (2,3)
    assert result.metadata['rows'] == 2

def test_invalid_extension():
    ok, msg = validate_file_extension("test.txt")
    assert not ok

def test_empty_file():
    try:
        read_file(b"", "empty.csv")
        assert False, "Should fail on empty"
    except ValueError:
        assert True

def test_excel_sheets():
    # Create simple excel in memory
    import io
    df = pd.DataFrame({"a":[1,2], "b":[3,4]})
    output = io.BytesIO()
    df.to_excel(output, index=False)
    content = output.getvalue()
    result = read_file(content, "test.xlsx")
    assert result.df.shape == (2,2)

def test_json():
    json_content = b'[{"a":1,"b":2},{"a":3,"b":4}]'
    result = read_file(json_content, "test.json")
    assert result.df.shape == (2,2)

if __name__ == "__main__":
    test_valid_csv()
    test_invalid_extension()
    test_empty_file()
    test_excel_sheets()
    test_json()
    print("test_ingestion PASS")
