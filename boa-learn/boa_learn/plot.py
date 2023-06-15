import pandas as pd
from lifelines import KaplanMeierFitter

# Initialize Kaplan Meier Fitter
kmf = KaplanMeierFitter()

# Predefined measures
measure_parameters = {
    "None": {
        "column": None,
        "group_condition": lambda df: slice(None),
        "labels": ["None"],
    },
    "Gender": {
        "column": "sex",
        "group_condition": lambda df: df["sex"] == 1,
        "labels": ["Male", "Female"],
    },
    "Blood glucose": {
        "column": "glucose",
        "group_condition": lambda df: df["glucose"] < 5.5,
        "labels": ["Low Glucose", "High Glucose"],
    },
    "Biological Age": {
        "column": "biologically_older",
        "group_condition": lambda df: df["biologically_older"] == 0,
        "labels": ["Biologically younger", "Biologically older"],
    },
}


def prepare_survival_dataframe(df, group_condition, label):
    """Prepares a survival function DataFrame based on a group condition and a label."""
    time_to_event = df.months_until_death
    event_occurred = df.is_dead
    kmf.fit(
        time_to_event[group_condition], event_occurred[group_condition], label=label
    )
    survival_function = kmf.survival_function_
    survival_function.columns = ["Survival"]
    survival_function["Category"] = label
    survival_function["Time (months)"] = survival_function.index
    return survival_function


def build_plot(df, measure_params):
    """Updates the figure based on the chosen measure parameters."""
    group_condition = measure_params["group_condition"](df)
    labels = measure_params["labels"]

    if len(labels) == 1:
        survival_df = prepare_survival_dataframe(df, group_condition, labels[0])
    else:
        survival_df_group1 = prepare_survival_dataframe(df, group_condition, labels[0])
        survival_df_group2 = prepare_survival_dataframe(df, ~group_condition, labels[1])
        survival_df = pd.concat([survival_df_group1, survival_df_group2])
    return survival_df
