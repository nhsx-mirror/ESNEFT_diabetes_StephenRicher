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
import seaborn as sns
import matplotlib.pyplot as plt
from pingouin import partial_corr
from esneft_tools import download, visualise
```

### Load ESNEFT tools data

#### Summary of Deprivation, Demographics and Disease Prevalance
* LSOA level
* GP level

```python
# Instantiate data download class.
getData = download.getData(cache='../data/.data-cache')
# Retrieve geo data for choropleth
geoLSOA = getData.fromHost('geoLSOA')
# Get summary by LSOA
LSOAsummary = pd.read_pickle('../data/lsoa-esneft.pkl')
# Get GP registration data
GPreg = pd.read_pickle('../data/gp-reg-filtered.pkl')
# Get processed DC data
DCdata_all = pd.read_parquet('../data/dc-filtered.parquet')
```

```python
diabType = 'all'
assert diabType in ['T1D', 'T2D', 'nonDiabetic', 'all']
if diabType == 'nonDiabetic':
    DCdata = DCdata_all.loc[(~DCdata_all['T2D']) & (~DCdata_all['T1D'])].copy()
elif diabType == 'all':
    DCdata = DCdata_all.copy()
else:
    DCdata = DCdata_all.loc[DCdata_all[diabType]].copy()
```

### Visualisation of Diabetes Centre Cohort by LSOA

* Map too large to render of GitHub at the moment

```python
dc_count = DCdata['LSOA11CD'].value_counts().to_frame().rename({'LSOA11CD': 'LSOA11NM'}, axis=1)
fig = visualise.choroplethLSOA(dc_count, geoLSOA, colour='LSOA11NM', cmap='gray_r')
fig.show(full_html=False)
```

### Deprivation over-representation

#### Rationale
* What is the mean deprivation of the Diabetes Centre cohort?
* How does this compare to the expected deprivation of a random sample.

#### Approach
* This analysis estimates a null distribution by selecting patients at random from each GP.
* Example
  * If the Diabetes Centre has 60 patients from GP A and 40 patients from GP B.
    * Calculate the mean deprivation according to their LSOA
  * Then randomly select 60 patients from GP A and 40 patients for GP B using the GP regristration data.
     * Calculate the mean deprivation of the random selection.
  * Repeat this 10,000 times and create a null distribution.
  * Compre null distribution to observed value.
   
#### Result
* The Diabetes Centre cohort are from more deprived areas than expected, compared to the GP populations they are referred from.

```python
# Remove entries with no Deprivation or GP registration data
sub = DCdata.loc[(DCdata['AdultSkills'].notna()) & (DCdata['Registered.GP.Practice.Code'].notna())]
# Get mean Deprivation of Diabetes Cohort
refIMD = sub['AdultSkills'].mean()
# Get DC patients per GP
# Random samples should have the same number of patients per GP as the Diabetes Centre cohort
codeMap = sub['Registered.GP.Practice.Code'].value_counts().to_dict()
# Ensure only GPs in code map are present in GP registration list
GPreg = GPreg.loc[GPreg['OrganisationCode'].isin(codeMap.keys())]
```

```python
def sampleGP(x, codeMap, val, count='Patient'):
    size = codeMap[x.name]
    return np.random.choice(x[val], size=size, p=(x[count] / x[count].sum()))
```

```python
# Sample a cohort of patient by GP - repeat 10,000 times
sampled = []
for i in range(10_000):
    v = GPreg.groupby('OrganisationCode').apply(sampleGP, codeMap, 'AdultSkills', 'Patient').explode().mean()
    sampled.append(v)
sampled = np.array(sampled)
zRef = (refIMD - sampled.mean()) / sampled.std()
```

```python
fig, ax = plt.subplots()
sns.histplot(data=sampled, stat='probability', ax=ax)
ax.set_xlabel('Mean Expected Deprivation (Adult Skills)')
ax.axvline(refIMD, ls='--', color='red')
ax.set_title(f'Observed vs. Expected Deprivation (z = {zRef:.1f}, n = 10,000)', loc='left')
fig.tight_layout()
fig.savefig(f'../plots/deprivation_vs_standard-{diabType}.png', dpi=300)
```

### Patient Usages and Health Metrics by Deprivation

#### Rationale
* To identify any differences in service usage, waiting times and health outcomes associated with deprivation.

#### Approach
* Diabetes Centre records have been aggregated to patient-level with numerical meausres for various metrics.
* Each metric (e.g. waiting time between BMI check) with be correlated with the deprivation score.
* Here we use __partial correlation__, this allows us to control for confounding factors such as Age, Sex and Ethnicity and isolate the impact attributate to Deprivation.
   
#### Result
* Deprivation is positively correlated with inital measurement of BMI, HbA1C and Urine Microalbumin.
  * Suggests patients from deprived areas are being seen later or their symptoms are developing earlier.
* IP Admissions (all causes) is positively correlated with deprivation.
* GFR is negatively correlated with deprivation.
  * Higher deprivation -> Lower GFR, indicating decline in kidney function.

```python
allDemographics = ['Age', 'Male', 'NonWhite', 'AdultSkills', 'AdultSkills (q5)']
DCdata = DCdata.loc[DCdata[allDemographics].notna().all(axis=1)].copy()
```

```python
refs = ([
    'Did not attend-meanWait', 'IP Admissions', 
    'DaysToReferral', 'DaysBetweenAppointment',
    'BMI-meanWait', 'BMI-change', 'BMI-initial',
    'HbA1c (IFCC)-meanWait', 'HbA1c (IFCC)-change',  'HbA1c (IFCC)-initial',
    'GFR-meanWait', 'GFR-change',  'GFR-initial',
    'Diastolic BP-meanWait', 'Diastolic BP-change',  'Diastolic BP-initial',
    'Urine Microalbumin-meanWait', 'Urine Microalbumin-change',  'Urine Microalbumin-initial',
])

alpha = 0.01

checks = ({
    'AdultSkills': ['Age', 'Male', 'NonWhite'],
    'Age': ['AdultSkills', 'Male', 'NonWhite'],
    'Male': ['Age', 'AdultSkills', 'NonWhite'],
    'NonWhite': ['Age', 'Male', 'AdultSkills'],
})
allData = {}
for x, covars in checks.items():
    for ref in refs:
        parcorr = partial_corr(data=DCdata, x=x, y=ref, covar=covars, method='spearman')
        allData[(x, ref)] = parcorr[['r', 'p-val']].values.flatten()
allData = (
    pd.DataFrame(allData).T
    .reset_index()
    .rename({
        'level_0': 'x', 'level_1': 
        'metric', 0: 'r', 1: 'p-val'}, axis=1)
    .sort_values('r', ascending=False)
)
allData[f'Sig. (p < {alpha})'] = allData['p-val'] < alpha
allData['metric'] = allData['metric'].replace({
    'recordSpan': 'Time At Centre',
    'DaysBetweenAppointment': 'Days Between',
    'DaysToReferral': 'Days To Referral',
    'Urine Microalbumin-initial': 'Urine Albumin-initial',
    'Urine Microalbumin-change': 'Urine Albumin-change',
    'Urine Microalbumin-meanWait': 'Urine Albumin-meanWait'
})
```

```python
allData.loc[allData['metric'] == 'Did not attend-meanWait', 'metric'] = 'DNA Frequency'
```

```python
data = allData.loc[allData['x'] == 'AdultSkills']
order = ['BMI', 'HbA1c (IFCC)', 'Urine Albumin', 'Diastolic BP', 'GFR']
```

```python
fig, axes = plt.subplots(2, 2, figsize=(12, 9))
axes = axes.flatten()

measures = ({
    'initial': 'Initial Measure', 
    'meanWait': 'Mean Wait Between Check', 
    'change': 'Measure Change'
})
for i, (measure, label) in enumerate(measures.items()):
    subdata = data.loc[data['metric'].apply(lambda x: x.split('-')[-1] == measure)].copy()
    subdata['metric'] = subdata['metric'].apply(lambda x: x.split('-')[0])
    sns.barplot(
        data=subdata, x='r', y='metric', hue=f'Sig. (p < {alpha})', 
        order=order, dodge=False, ax=axes[i])
    axes[i].set_title(label, loc='left')

subdata = data.loc[data['metric'].apply(lambda x: x.split('-')[-1] not in measures)].copy()
subdata['metric'] = subdata['metric'].apply(lambda x: x.split('-')[0])
sns.barplot(data=subdata, x='r', y='metric', hue=f'Sig. (p < {alpha})', dodge=False, ax=axes[3])
axes[3].set_title('Other Metrics', loc='left')

for ax in axes:
    ax.set_ylabel('')
    ax.axvline(0, color='black')
    ax.set_xlim(-0.2, 0.2)
    ax.set_xlabel('Rho (partial correlation)')

fig.tight_layout()
fig.savefig(f'../plots/DC-by-AdultSkills-{diabType}.png', transparent=False, dpi=300)
```

```python
metrics = ['BMI-initial', 'HbA1c (IFCC)-initial', 'Urine Microalbumin-initial', 'IP Admissions']

fig, axes = plt.subplots(2, 2, figsize=(12, 7))
axes = axes.flatten()
for i, metric in enumerate(metrics):
    name = metric.split('-')[0]
    sns.pointplot(data=DCdata, y=metric, x='AdultSkills (q5)', ax=axes[i])
    axes[i].set_xlabel('Adult Skills Deprivation Quintile (1 = Most Deprived)')
    axes[i].set_ylabel(name)
    if name != 'IP Admissions':
        axes[i].set_title(
            f'Initial {name}', loc='left')
    else:
        axes[i].set_title('Total Inpatient Admissions', loc='left')
fig.tight_layout()
fig.savefig(f'../plots/AdultSkills-by-Initial-{diabType}.png', transparent=False, dpi=300)
```

```python

```
