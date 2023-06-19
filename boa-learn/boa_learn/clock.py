import os
import pandas as pd


def horvath_function(mult_sum):
    const = 0.695507258
    BA = (mult_sum + const) * 21 + 20
    return BA


def phenoage_function(mult_sum):
    const = 60.664
    BA = mult_sum + const
    return BA

def no_transform(_):
    return _


def horvath_clock(dataframe):
    script_dir = os.path.dirname(__file__)  # get the directory of the current script
    data_file_path = os.path.join(
        script_dir, "data", "horvath.csv"
    )  # build the path to the data file

    coefficients = pd.read_csv(data_file_path, index_col=0)
    methylation_df = coefficients.merge(
        dataframe.transpose(), left_index=True, right_index=True
    )
    for c in methylation_df.columns[1:]:
        methylation_df[c] = methylation_df["CoefficientTraining"] * methylation_df[c]
    df_sum = methylation_df.drop("CoefficientTraining", axis=1).sum()
    return df_sum.apply(horvath_function).to_frame(name="biological_age")


def hannum_clock(dataframe):
    script_dir = os.path.dirname(__file__)  # get the directory of the current script
    data_file_path = os.path.join(
        script_dir, "data", "hannum.csv"
    )  # build the path to the data file

    coefficients = pd.read_csv(data_file_path, index_col=0)
    methylation_df = coefficients.merge(
        dataframe.transpose(), left_index=True, right_index=True
    )
    for c in methylation_df.columns[1:]:
        methylation_df[c] = methylation_df["CoefficientTraining"] * methylation_df[c]
    df_sum = methylation_df.drop("CoefficientTraining", axis=1).sum()
    return df_sum.to_frame(name="biological_age")


def phenoage_clock(dataframe):
    script_dir = os.path.dirname(__file__)  # get the directory of the current script
    data_file_path = os.path.join(
        script_dir, "data", "phenoage.csv"
    )  # build the path to the data file

    coefficients = pd.read_csv(data_file_path, index_col=0)
    methylation_df = coefficients.merge(
        dataframe.transpose(), left_index=True, right_index=True
    )
    for c in methylation_df.columns[1:]:
        methylation_df[c] = methylation_df["CoefficientTraining"] * methylation_df[c]
    df_sum = methylation_df.drop("CoefficientTraining", axis=1).sum()
    return df_sum.apply(phenoage_function).to_frame(name="biological_age")

def single_sample_clock(clock_function, data):
    return clock_function(data).iloc[0,0]