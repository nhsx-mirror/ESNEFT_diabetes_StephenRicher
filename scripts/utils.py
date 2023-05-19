import numpy as np
import pandas as pd
import networkx as nx
import seaborn as sns
import matplotlib.pyplot as plt


def get_inpatient_count(
        path: str,
        patientID: str = 'ï..Pseudonym',
        encoding: str = 'latin-1'):
    """ Count inpatient events per patient """
    return (
        pd.read_csv(path, encoding=encoding)
        .rename({patientID: 'patientID'}, axis=1)
        .set_index('patientID')
        .index
        .value_counts()
        .rename('IP Admissions')
    )


def get_outpatient_demographics(
        path: str,
        patientID: str = 'ï..Pseudonym',
        appointmentDate: str = 'Appointment.Date',
        ageAtAppointment: str = 'Age.at.Appt',
        patientGender: str = 'ï..Patient_Gender',
        patientEthnicity: str = 'Patient_Ethnicity',
        patientPostcode: str = 'Patient_Postcode',
        gpCode: str = 'Registered.GP.Code',
        gpPractiseCode: str = 'Registered.GP.Practice.Code',
        dateFormat: str = '%Y%m%d',
        encoding: str = 'latin-1'):
    """ Count inpatient events per patient """
    rename = ({
        patientID: 'patientID',
        patientGender: 'Patient_Gender',
        patientEthnicity: 'Patient_Ethnicity',
        patientPostcode: 'Patient_Postcode',
        gpCode: 'Registered.GP.Code',
        gpPractiseCode: 'Registered.GP.Practice.Code',
        appointmentDate: 'Appointment.Date',
        ageAtAppointment: 'Age.at.Appt'
    })
    # Open data and rename as requested, set patient ID as index
    data = (
        pd.read_csv(path, encoding=encoding)
        .rename(rename, axis=1)[list(rename.values())]
        .set_index('patientID')
    )
    # Remove missing IDs
    data = data.loc[data.index.notna()]
    # Convert appointment date to datetime
    data[appointmentDate] = pd.to_datetime(data[appointmentDate], format=dateFormat)
    year = pd.Timedelta('365.25D') # Define a year (approximately)
    # Estimate patient DoB
    patientDoB = data[appointmentDate] - (data[ageAtAppointment] * year)
    drop = [appointmentDate, ageAtAppointment]
    # Get demographics per patient (use mode to minimise errors)
    demographics = data.drop(drop, axis=1).groupby(data.index).agg(pd.Series.mode)
    # Add mean data of birth
    demographics['patientDoB'] = patientDoB.groupby(patientDoB.index).mean()
    demographics = demographics.fillna('Unknown').applymap(_fixMode)

    assert not (set(data['Patient_Gender'].dropna()) - set(['Male', 'Female']))
    demographics['NonWhite'] = demographics['Patient_Ethnicity'].apply(
        _processDemo, args=('White',))
    demographics['Male'] = demographics['Patient_Gender'].apply(
        _processDemo, args=('Male',))

    return demographics


# Convert Ethnicity and Sex to 0 / 1 numeric feature
def _processDemo(x, val):
    if str(x) == 'Unknown':
        return np.nan
    try:
        return int(str(x).startswith(val))
    except:
        return np.nan


def _fixMode(x):
    if isinstance(x, np.ndarray):
        if len(x) == 0:
            return ''
        else:
            return x[0]
    else:
        return x


CTV3Desc_rename = ({
    'Haemoglobin A1c level': 'HbA1c',
    'Body mass index - observation': 'BMI',
    'Haemoglobin A1c level - IFCC standardised': 'HbA1c (IFCC)',
    'GFR calculated abbreviated MDRD': 'GFR',
    'O/E - Diastolic BP reading': 'Diastolic BP',
    'Urine microalbumin level': 'Urine Microalbumin',
    'Never smoked tobacco': 'Never Smoked',
    'Type II diabetes mellitus': 'Type 2 Diabetes',
    'Haemoglobin concentration': 'Hemoglobin',
    'Type I diabetes mellitus': 'Type 1 Diabetes',
    'GFR calculated Cockcroft-Gault formula': 'GFR-Cockcroft'
})


def readDC(
        path: str,
        patientID: str = 'Pseudonym',
        event_col: str = 'CTV3Desc',
        value_col: str = 'RecordingValue',
        event_date_col: str = 'CodeEventDate',
        referral_date_col: str = 'ReferralDate',
        encoding: str = 'utf-8',
        date_cols: list = None):
    rename = ({
        patientID: 'patientID',
        event_col: 'CTV3Desc',
        value_col: 'RecordingValue',
        event_date_col: 'CodeEventDate',
        referral_date_col: 'ReferralDate'
    })
    data = (
        pd.read_csv(path, encoding=encoding)
        .rename(rename, axis=1)
        .set_index('patientID')
    )
    for col in [event_date_col, referral_date_col]:
        data[col] = pd.to_datetime(data[col])
        if col == 'CodeEventDate':
            data['CodeEventTime'] = data[col].dt.time
        data[col] = data[col].dt.date
    # Simplify event names
    data['CTV3Desc'] = data['CTV3Desc'].replace(CTV3Desc_rename)
    # Remove missing IDs
    data = data.loc[data.index.notna()]
    return data


def removeOutlier(
        data: pd.DataFrame,
        threshold: float = 3,
        measures: list = None):
    """ Remove outliers using IQR method """
    if measures is None:
        measures = ([
            'HbA1c', 'BMI', 'HbA1c (IFCC)', 'GFR',
            'Diastolic BP', 'Urine Microalbumin',
            'Hemoglobin', 'GFR-Cockcroft'
        ])
    data = data.copy()
    for measure in measures:
        valid = data['CTV3Desc'] == measure
        values = data.loc[valid, 'RecordingValue']
        Q1, Q3 = np.percentile(values , [25,75])
        IQR = Q3 - Q1
        lower = Q1 - (IQR * 3)
        upper = Q3 + (IQR * 3)
        outlier = (data['RecordingValue'] < lower) | (data['RecordingValue'] > upper)
        data.loc[valid & outlier, 'RecordingValue'] = np.nan
    return data


type1_default = ([
    'Type 1 Diabetes',
    'Type I diabetic dietary review',
    'Type I diabetes mellitus without complication',
    'Type I diabetes mellitus - poor control',
    'Type I diabetes mellitus with retinopathy'
])


type2_default = ([
    'Type 2 Diabetes',
    'Type II diabetic dietary review',
    'Type II diabetes mellitus with persistent proteinuria',
    'Type II diabetes mellitus - poor control',
    'Type II diabetes mellitus with retinopathy'
])


def summariseByPatient(
        data: pd.DataFrame, type1: list = None,
        type2: list = None):
    events = data['CTV3Desc'].unique()
    type1 = type1_default if type1 is None else type1
    type2 = type2_default if type2 is None else type2
    summary = (
        data.groupby('patientID')
        .apply(_summarise, events=events, type1=type1, type2=type2)
        .apply(lambda x: pd.Series(x))
    )
    return summary


def _summarise(x, events, type1, type2):
    day = pd.Timedelta('1d')
    summary = {}
    for event in events:
        if event == 'Date of diagnosis':
            continue
        sub = x.loc[x['CTV3Desc'] == event, 'CodeEventDate'].dropna()
        if (len(sub) < 2) or (sub.max() - sub.min() == 0):
            summary[f'{event}-meanWait'] = np.nan
        else:
            span = (sub.max() - sub.min()) / day
            summary[f'{event}-meanWait'] = span / len(sub)
    summary['T1D'] = (x['CTV3Desc'].isin(type1)).any()
    summary['T2D'] = (x['CTV3Desc'].isin(type2)).any()
    sub = x.loc[(x['CTV3Desc'] != 'Date of diagnosis')]
    summary['firstReferral'] = sub['ReferralDate'].dropna().min()
    diagnosis = x.loc[(x['CTV3Desc'] == 'Date of diagnosis'), 'CodeEventDate']
    if diagnosis.empty:
        summary['DateOfDiagnosis'] = pd.NaT
        summary['DaysToReferral'] = np.nan
    else:
        summary['DateOfDiagnosis'] = diagnosis.values[0]
        if pd.isna(summary['firstReferral']):
             summary['DaysToReferral'] = np.nan
        else:
            summary['DaysToReferral'] = (
                summary['firstReferral'] - summary['DateOfDiagnosis']) / day
            # Negative dates likely entry error
            if summary['DaysToReferral'] < 0:
                summary['DaysToReferral'] = np.nan
    codeEvents = sub['CodeEventDate'].dropna()
    totalAppointments = len(codeEvents.unique())
    recordSpan = codeEvents.max() - codeEvents.min()
    if (totalAppointments < 2) or (recordSpan == 0):
        summary['TimeAtCentre'] = np.nan
        summary['DaysBetweenAppointment'] = np.nan
    else:
        summary['TimeAtCentre'] = recordSpan / day
        summary['DaysBetweenAppointment'] = (
            summary['TimeAtCentre'] / totalAppointments
        )
    measures = ([
        'BMI', 'HbA1c (IFCC)', 'GFR', 'HbA1c',
        'Diastolic BP', 'Urine Microalbumin'
    ])
    for measure in measures:
        byMeasure = sub.loc[
              (sub['CTV3Desc'] == measure)
            & (sub['RecodingLabel'] != 'None')
            & (sub['RecordingValue'].notna())
        ].sort_values('CodeEventDate')
        if byMeasure.empty:
            summary[f'{measure}-change'] = np.nan
            summary[f'{measure}-mean'] = np.nan
            summary[f'{measure}-initial'] = np.nan
            summary[f'{measure}-final'] = np.nan
        else:
            span = byMeasure['CodeEventDate'].max() - byMeasure['CodeEventDate'].min()
            span = span / day
            summary[f'{measure}-mean'] = byMeasure['RecordingValue'].mean()
            summary[f'{measure}-initial'] = byMeasure['RecordingValue'].head(1)[0]
            summary[f'{measure}-final'] = byMeasure['RecordingValue'].tail(1)[0]
            # Only compute change for records over 3 months old
            if span > 90:
                summary[f'{measure}-change'] = (
                    (summary[f'{measure}-final'] - summary[f'{measure}-initial']) / span
            )
            else:
                summary[f'{measure}-change'] = np.nan
    return summary


def merge_ip_demo_dc(
        dc_summary: pd.DataFrame, ip_count: pd.Series,
        demo: pd.DataFrame, date):
    data = pd.concat([demo, ip_count], axis=1)
    data = pd.merge(
        dc_summary, data,
        left_index=True, right_index=True, how='left')
    data['IP Admissions'] = data['IP Admissions'].fillna(0)
    data['Demographics'] = data.index.isin(demo.index)
    year = pd.Timedelta('365.25D')
    data['Age'] = (date - data['patientDoB']) / year
    data = data.drop(['patientDoB'], axis=1)
    data.loc[data['Age'] < 0, 'Age'] = np.nan
    return data


def computePath(x, osm, ref=None):
    """ Compute path from GP to patient Postcode """
    if ref is None:
        ref = x['GP_Node']
    try:
        return nx.shortest_path_length(
            osm, x['Patient_Node'], ref,
            weight='length', method='dijkstra')
    except:
        return -1


def load_english_language(path: str):
    """ Load and process English Language proficiency.
        Returns proportion of population who cannot speak
        English or cannot speak it well, by LSOA11. """
    dtype = ({'LSOA11CD': str, 0: int, 1: int, 2: int, 3: int, 4: int})
    englishLanguage = pd.read_csv(
        path, names=dtype.keys(),
        dtype=dtype, skiprows=11, nrows=34753)
    englishLanguage['LSOA11CD'] = englishLanguage['LSOA11CD'].apply(
        lambda x: x.split(':')[1].strip())
    englishLanguage = englishLanguage.set_index('LSOA11CD')
    englishLanguage = englishLanguage.apply(
        lambda x: x[[3,4]].sum() / x.sum(), axis=1)
    return englishLanguage


def load_adult_skills(path: str):
    """ Load and process Adult Skills data.
        Returns proportion of adult population with
        low or no formal qualifications, by LSOA11. """
    dtype = ({
        'LSOA11CD': str, 0: int, 1: int, 2: int,
        3: int, 4: int, 5: int, 6:int
    })
    higherEducation = pd.read_csv(
        path, names=dtype.keys(),
        dtype=dtype, skiprows=11, nrows=34753)
    higherEducation['LSOA11CD'] = higherEducation['LSOA11CD'].apply(
        lambda x: x.split(':')[1].strip())
    higherEducation = higherEducation.set_index('LSOA11CD')
    higherEducation = higherEducation.apply(
        lambda x: x[[0,1]].sum() / x.sum(), axis=1)
    return higherEducation


def plot_deprivation_heatmap(
        data, vmin: float = -1, vmax: float = 1,
        label: str = "Partial Spearman's Correlation Coefficient",
        rotate_x: bool = False, figsize: tuple = (12, 7)):
    """ Wrapper function defining seaborn heatmap parameters """
    fig, ax = plt.subplots(figsize=figsize)
    g = sns.heatmap(
        data=data, yticklabels=1, xticklabels=1, cmap='bwr',
        vmin=vmin, vmax=vmax, center=0,
        cbar_kws={'label': label}, ax=ax)
    if rotate_x:
        ax.set_xticklabels(
            g.get_xticklabels(), rotation=45,
            ha='right', rotation_mode='anchor')
    fig.tight_layout()
    return fig, ax
