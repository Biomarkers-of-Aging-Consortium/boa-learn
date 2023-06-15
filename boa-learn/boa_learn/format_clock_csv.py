# convert clock.tcv to clock.csv with updated column names
import pandas as pd

# Hoannum
df = pd.read_table(
    "/labs/mpsnyder/moqri/bio-learn/boa-learn/boa_learn/data/Hannum2013.tsv"
)
df.columns = ["CpGmarker", "CoefficientTraining"]
df.to_csv(
    "/labs/mpsnyder/moqri/bio-learn/boa-learn/boa_learn/data/hannum.csv", index=False
)

# PhenoAge
df = pd.read_table(
    "/labs/mpsnyder/moqri/bio-learn/boa-learn/boa_learn/data/PhenoAge.tsv"
)
df.columns = ["CpGmarker", "CoefficientTraining"]
df.to_csv(
    "/labs/mpsnyder/moqri/bio-learn/boa-learn/boa_learn/data/phenoage.csv", index=False
)
