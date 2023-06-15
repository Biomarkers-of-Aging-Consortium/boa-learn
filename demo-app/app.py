import streamlit as st
import pandas as pd
import plotly.express as px

from boa_learn import plot

# Predefined data sources
datasets = {
    "National Health and Nutrition Examination Survey": {"file": "nhanes-2010.csv"},
    "Framingham Heart Study": {"file": "fhs-2010.csv"},
}

# Streamlit selectbox inputs
dataset = st.selectbox("Dataset", datasets.keys())
measure = st.selectbox("Category", plot.measure_parameters.keys())

# Load DataFrame
data_frame = pd.read_csv(datasets[dataset]["file"], index_col=0)

# Update figure based on chosen measure
survival_df = plot.build_plot(data_frame, plot.measure_parameters[measure])

# Create and display plot
fig = px.line(
    survival_df,
    x="Time (months)",
    y="Survival",
    color="Category",
    hover_name="Survival",
    range_y=[0, 1],
)
st.plotly_chart(fig, theme="streamlit", use_container_width=True)
