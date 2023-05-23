import pandas as pd

MG_PER_DL_TO_MMOL_PER_L=0.05551

def load_fhs():
    """Loads data from the Framingham Heart Study"""
    public_link='https://raw.githubusercontent.com/singator/bdah/master/data/frmgham2.csv'
    df = pd.read_csv(public_link,index_col=0,usecols=['RANDID','PERIOD','AGE','SEX','DEATH','TIMEDTH','GLUCOSE'])
    df=df[df['PERIOD']==1].drop('PERIOD',axis=1)
    df['TIMEDTH']=df['TIMEDTH']/30.437 # days to months
    df.index.name = 'id'

    df=df.rename({
        'AGE': 'age',
        'SEX': 'sex',
        'GLUCOSE': 'glucose',
        'DEATH': 'is_dead',
        'TIMEDTH': 'months_until_death'
    },axis=1)
    
    #standardize glucose units
    df['glucose'] = df['glucose'].apply(lambda g: g * MG_PER_DL_TO_MMOL_PER_L)
    
    return df

def load_nhanes(year):
    """Loads data from the National Health and Nutrition Examination Survey"""
    cbc_sub=['LBXRDW','LBXWBCSI','LBXLYPCT','LBDLYMNO','LBXRBCSI','LBXHGB','LBXPLTSI']
    known_nhanes_year_suffix = {2010 : 'F', 2012 : 'G'}
    if not known_nhanes_year_suffix[year]:
        raise ValueError(f'Unknown year {year}. Can only load for known available years {known_nhanes_year_suffix.keys}')
    suffix=known_nhanes_year_suffix[year]
    dem_path=f'https://wwwn.cdc.gov/Nchs/Nhanes/{year-1}-{year}/DEMO_{suffix}.XPT'
    gluc_path=f'https://wwwn.cdc.gov/Nchs/Nhanes/{year-1}-{year}/GLU_{suffix}.XPT'
    cbc_path=f'https://wwwn.cdc.gov/Nchs/Nhanes/{year-1}-{year}/CBC_{suffix}.XPT'
    mortality_path=f'https://ftp.cdc.gov/pub/Health_Statistics/NCHS/datalinkage/linked_mortality/NHANES_{year-1}_{year}_MORT_2019_PUBLIC.dat'
    dem=pd.read_sas(dem_path,index='SEQN')[['RIAGENDR','RIDAGEYR']]
    dem.index=dem.index.astype(int)
    gluc=pd.read_sas(gluc_path,index='SEQN')['LBDGLUSI']
    gluc.index=gluc.index.astype(int)
    cbc=pd.read_sas(cbc_path,index='SEQN')[cbc_sub]
    cbc.index=cbc.index.astype(int)
    mort=pd.read_fwf(mortality_path,index_col=0,header=None,widths=[14,1,1,3,1,1,1,4,8,8,3,3])
    mort.index=mort.index.rename('SEQN')
    dead=mort[mort[1]==1][[2,10]].astype(int)
    dead.columns=['MORTSTAT','PERMTH_EXM']
    df=pd.concat([dem,gluc,cbc,dead],axis=1).dropna()
    df.index.name = 'id'
    df=df.rename({
        'RIDAGEYR': 'age',
        'RIAGENDR': 'sex',
        'LBDGLUSI': 'glucose',
        'MORTSTAT': 'is_dead',
        'PERMTH_EXM': 'months_until_death'
    },axis=1)
    df=df.rename({'LB2RDW':'LBXRDW','LB2WBCSI':'LBXWBCSI'},axis=1)
    return df