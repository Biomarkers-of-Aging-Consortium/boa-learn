from src import load
from src.model import load_columns
import pytest

def test_fhs_columns():
    df = load.load_fhs()
    verify_expected_columns(df)

def test_nhanes_columns():
    df = load.load_nhanes(2010)
    verify_expected_columns(df)


def verify_expected_columns(df):
    actual_columns = set(df.columns.to_list())
    missing_columns = set(load_columns) - actual_columns
    extra_columns = actual_columns - set(load_columns)
    assert len(missing_columns) == 0, f"Missing expected columns: {missing_columns} \n Found extra columns: {extra_columns}"


# Run the test
if __name__ == '__main__':
    pytest.main([__file__])