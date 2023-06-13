import pandas as pd
import os
import hashlib
import requests
import shutil
from urllib.parse import urlparse
import appdirs

MG_PER_DL_TO_MMOL_PER_L = 0.05551


def cached_dowload(url):
    """Downloads the file at a URL and saves it locally. If called again with the same URL it will use the saved file. Returns the local filepath"""
    # Hash the URL to create a unique filename
    url_path = urlparse(url).path
    ext = os.path.splitext(url_path)[1]
    filename = hashlib.sha256(url.encode()).hexdigest() + ext

    app_name = "bio-learn"
    download_path = appdirs.user_cache_dir(app_name)

    # Ensure download path exists
    os.makedirs(download_path, exist_ok=True)

    filepath = os.path.join(download_path, filename)

    if os.path.exists(filepath):
        # If the file is already downloaded, return the file path
        return filepath
    else:
        # Try to download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Raise an HTTPError if one occurred

        # If the file is not downloaded yet, download and save it
        with open(filepath, "wb") as out_file:
            shutil.copyfileobj(response.raw, out_file)

        # Return the file path
        return filepath


def load_fhs():
    """Loads data from the Framingham Heart Study"""
    public_link = (
        "https://raw.githubusercontent.com/singator/bdah/master/data/frmgham2.csv"
    )
    df = pd.read_csv(
        public_link,
        index_col=0,
        usecols=["RANDID", "PERIOD", "AGE", "SEX", "DEATH", "TIMEDTH", "GLUCOSE"],
    )
    df = df[df["PERIOD"] == 1].drop("PERIOD", axis=1)
    df["TIMEDTH"] = df["TIMEDTH"] / 30.437  # days to months
    df.index.name = "id"

    df = df.rename(
        {
            "AGE": "age",
            "SEX": "sex",
            "GLUCOSE": "glucose",
            "DEATH": "is_dead",
            "TIMEDTH": "months_until_death",
        },
        axis=1,
    )

    # standardize glucose units
    df["glucose"] = df["glucose"].apply(lambda g: g * MG_PER_DL_TO_MMOL_PER_L)

    return df


def load_nhanes(year):
    """Loads data from the National Health and Nutrition Examination Survey"""
    cbc_sub = [
        "LBXRDW",
        "LBXWBCSI",
        "LBXLYPCT",
        "LBXMCVSI",
        "LBDLYMNO",
        "LBXRBCSI",
        "LBXHGB",
        "LBXPLTSI",
    ]
    known_nhanes_year_suffix = {2010: "F", 2012: "G"}
    if not known_nhanes_year_suffix[year]:
        raise ValueError(
            f"Unknown year {year}. Can only load for known available years {known_nhanes_year_suffix.keys}"
        )
    suffix = known_nhanes_year_suffix[year]
    dem_file = cached_dowload(
        f"https://wwwn.cdc.gov/Nchs/Nhanes/{year-1}-{year}/DEMO_{suffix}.XPT"
    )
    gluc_file = cached_dowload(
        f"https://wwwn.cdc.gov/Nchs/Nhanes/{year-1}-{year}/GLU_{suffix}.XPT"
    )
    cbc_file = cached_dowload(
        f"https://wwwn.cdc.gov/Nchs/Nhanes/{year-1}-{year}/CBC_{suffix}.XPT"
    )
    bioc_file = cached_dowload(
        f"https://wwwn.cdc.gov/Nchs/Nhanes/{year-1}-{year}/BIOPRO_{suffix}.XPT"
    )
    mortality_file = cached_dowload(
        f"https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/NHANES_{year-1}_{year}_MORT_2019_PUBLIC.dat"
    )
    crp_file = cached_dowload(
        f"https://wwwn.cdc.gov/Nchs/Nhanes/{year-1}-{year}/CRP_{suffix}.XPT"
    )
    dem = pd.read_sas(dem_file, index="SEQN")[["RIAGENDR", "RIDAGEYR"]]
    dem.index = dem.index.astype(int)
    gluc = pd.read_sas(gluc_file, index="SEQN")["LBDGLUSI"]
    gluc.index = gluc.index.astype(int)
    cbc = pd.read_sas(cbc_file, index="SEQN")[cbc_sub]
    cbc.index = cbc.index.astype(int)
    # clumsy hack since 2012 doesn't have the CRP data. Will remove pending refactor of loading code
    if year == 2010:
        crp = pd.read_sas(crp_file, index="SEQN")["LBXCRP"]
        crp.index = crp.index.astype(int)
    bioc = pd.read_sas(bioc_file, index="SEQN")[["LBDSALSI", "LBDSCRSI", "LBXSAPSI"]]
    bioc.index = bioc.index.astype(int)
    mort = pd.read_fwf(
        mortality_file,
        index_col=0,
        header=None,
        widths=[14, 1, 1, 3, 1, 1, 1, 4, 8, 8, 3, 3],
    )
    mort.index = mort.index.rename("SEQN")
    dead = mort[mort[1] == 1][[2, 10]].astype(int)
    dead.columns = ["MORTSTAT", "PERMTH_EXM"]
    # clumsy hack since 2012 doesn't have the CRP data. Will remove pending refactor of loading code
    if year == 2010:
        df = pd.concat([dem, gluc, cbc, crp, bioc, dead], axis=1).dropna()
    else:
        df = pd.concat([dem, gluc, cbc, bioc, dead], axis=1).dropna()
    df.index.name = "id"
    df = df.rename(
        {
            "RIDAGEYR": "age",
            "RIAGENDR": "sex",
            "LBDGLUSI": "glucose",
            "MORTSTAT": "is_dead",
            "PERMTH_EXM": "months_until_death",
        },
        axis=1,
    )
    df = df.rename({"LB2RDW": "LBXRDW", "LB2WBCSI": "LBXWBCSI"}, axis=1)
    return df


def load_dnam():
    dnam_file = cached_dowload(
        "https://ftp.ncbi.nlm.nih.gov/geo/series/GSE19nnn/GSE19711/matrix/GSE19711_series_matrix.txt.gz"
    )
    # Row 31 contains IDs, row 41 contains age
    ages = pd.read_table(
        dnam_file, index_col=0, skiprows=lambda x: x != 40 and x != 30
    ).transpose()
    # Each row should be a person
    dnam = pd.read_table(dnam_file, index_col=0, skiprows=74).transpose()
    # Age data is in the form "ageatrecruitment: 61" need to extract numberical age
    dnam["age"] = ages["!Sample_characteristics_ch1"].str[-2:].astype(int)
    dnam = dnam.drop(["!series_matrix_table_end"], axis=1)
    # Ensure all data columns are correctly numeric
    # data_columns = dnam.columns[dnam.columns != 'index']
    # dnam[data_columns] = dnam[data_columns].apply(pd.to_numeric, errors='coerce')
    dnam.index.name = "id"
    return dnam
