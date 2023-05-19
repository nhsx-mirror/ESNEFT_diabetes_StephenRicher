---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.0
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
import numpy as np
import pandas as pd
from itertools import chain
from esneft_tools import download, process
from utils import (
    get_inpatient_count, get_outpatient_demographics, 
    readDC, removeOutlier, summariseByPatient,
    merge_ip_demo_dc, computePath, computePath
)
```

```python
# Data path not stored in git repo
diabetes_centre_data = '../../../data/DC-DiabetesCentre-extended.csv'
inpatient_data = '../../../data/DC-Inpatients.csv'
outpatient_data = '../../../data/DC-OutPatient.csv'
```

```python
dc = readDC(diabetes_centre_data)
dc = removeOutlier(dc)
summary_by_patient = summariseByPatient(dc)
summary_by_patient.replace([np.inf, -np.inf], np.nan, inplace=True)
```

```python
ip_count = get_inpatient_count(inpatient_data)
```

```python
op_demo = get_outpatient_demographics(outpatient_data)
```

```python
# Get single median timepoint for Diabetes Centre data
median_date = pd.to_datetime(dc['CodeEventDate']).median()

data = merge_ip_demo_dc(
    summary_by_patient, ip_count, op_demo, median_date)
```

```python
# Instantiate data download class.
getData = download.getData(cache='../data/.data-cache')

# Retrieve all data as dictionary
publicData = getData.fromHost('all')
```

```python
deprivationCols = ([
    'IMD', 'Income', 'Employment', 'Education', 'Health', 
    'Crime', 'Barriers (H&S)', 'Environment', 'IDACI', 
    'IDAOPI', 'YouthSubDomain', 'AdultSkills', 'Barriers (Geo)', 
    'Barriers (Wider)', 'IndoorsSubDomain', 'OutdoorSubDomain'
])

GPsummary = process.getGPsummary(**publicData, iod_cols=deprivationCols)
LSOAsummary = process.getLSOAsummary(**publicData, iod_cols=deprivationCols)
```

```python
# Get Node associated with patient postcode
data = (pd.merge(
    data, publicData['postcodeLSOA'][['LSOA11CD', 'Node']], 
    left_on='Patient_Postcode', right_index=True, how='left')
    .rename({'Node': 'Patient_Node'}, axis=1))
```

```python
# Get GP postcode associated with GP practice
data = (pd.merge(
    data, publicData['gpPractice'][['PCDS']],
    left_on='Registered.GP.Practice.Code', right_index=True, how='left')
    .rename({'PCDS': 'GP_Postcode'}, axis=1))
```

```python
# Get Node associated with GP postcode
data = (pd.merge(
    data, publicData['postcodeLSOA'][['Node']], 
    left_on='GP_Postcode', right_index=True, how='left')
    .rename({'Node': 'GP_Node'}, axis=1))
```

```python
# Get deprivation cols with quantiles
deprivationCols = list(
    chain.from_iterable((col, f'{col} (q5)') for col in deprivationCols)
)

# Get IoD statistics associated with patient LSOA
data = pd.merge(
    data, LSOAsummary[deprivationCols], 
    left_on='LSOA11CD', right_index=True, how='left')
```

```python
ipswichHospital = publicData['postcodeLSOA'].loc[
    publicData['postcodeLSOA'].index == 'IP4 5PD', 'Node'][0]

# Compute distance between patient postcode and ipswich hosptial
data.loc[data['Patient_Node'].notna(), 'patient2site'] = (
     data.loc[data['Patient_Node'].notna()].apply(
         computePath, args=(publicData['esneftOSM'], ipswichHospital), axis=1)
)
```

```python
# Compute distance between patient postcode and gp postcode
valid = (data['Patient_Node'].notna() & data['GP_Node'].notna())
data.loc[valid, 'patient2GP'] = (
     data.loc[valid].apply(
         computePath, args=(publicData['esneftOSM'],), axis=1)
)
```

```python
LSOAsummary = LSOAsummary.loc[LSOAsummary['ESNEFT']]
```

```python
GPreg = pd.merge(
    publicData['gpRegistration'], 
    LSOAsummary[deprivationCols + ['DM-prevalance']], 
    left_on='LSOA11CD', right_index=True, how='right')
```

```python
populationLSOA = publicData['populationLSOA']
valid = populationLSOA['LSOA11CD'].isin(data['LSOA11CD'])
populationLSOA = populationLSOA.loc[valid].copy()
populationLSOA = pd.merge(
    populationLSOA, LSOAsummary[deprivationCols], 
    left_on='LSOA11CD', right_index=True, how='right')
```

```python
data.to_parquet('../data/dc-filtered.parquet')
populationLSOA.to_pickle('../data/population-filtered.pkl')
GPreg.to_pickle('../data/gp-reg-filtered.pkl')
LSOAsummary.to_pickle('../data/lsoa-esneft.pkl')
GPsummary.to_pickle('../data/gp-summary.pkl')
```
