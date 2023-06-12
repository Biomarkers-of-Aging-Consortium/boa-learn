from boa_learn import load
from boa_learn.model import load_columns
import pytest


def test_fhs_columns():
    df = load.load_fhs()
    verify_expected_columns(df)


def test_nhanes_columns():
    df = load.load_nhanes(2010)
    verify_expected_columns(df)


def test_can_load_nhanes_2012():
    df = load.load_nhanes(2012)

def test_can_load_dnam():
    df = load.load_dnam()
    #Verify data set is of known size 
    assert(df.shape == (27579, 540))

def verify_expected_columns(df):
    actual_columns = set(df.columns.to_list())
    missing_columns = set(load_columns) - actual_columns
    extra_columns = actual_columns - set(load_columns)
    assert (
        len(missing_columns) == 0
    ), f"Missing expected columns: {missing_columns} \n Found extra columns: {extra_columns}"


# Run the test
if __name__ == "__main__":
    pytest.main([__file__])
