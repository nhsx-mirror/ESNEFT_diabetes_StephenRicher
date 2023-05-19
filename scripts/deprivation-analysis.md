---
jupyter:
  jupytext:
    formats: ipynb,md
    text_representation:
      extension: .md
      format_name: markdown
      format_version: '1.3'
      jupytext_version: 1.14.1
  kernelspec:
    display_name: Python 3 (ipykernel)
    language: python
    name: python3
---

```python
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
from pingouin import partial_corr
```
Here make sure have ESNEFT_TOOLS installed. 
It is located here https://github.com/nhsx/p24-diabetes-inequal
and can be installed by running the following 
```
python3 -m pip install esneft_tools
```
```
from esneft_tools.utils import formatP
from esneft_tools import download, process, visualise
import utils
from utils import (
    plot_deprivation_heatmap, load_adult_skills, 
    load_english_language)
```

### Load ESNEFT tools data

#### Summary of Deprivation, Demographics and Disease Prevalance
* LSOA level
* GP level

```python
# Instantiate data download class.
getData = download.getData(cache='../data/.data-cache')
# Retrieve all data as dictionary
publicData = getData.fromHost('all')
# Get nation-wide summary by LSOA
LSOAsummary = process.getLSOAsummary(**publicData)
# Get nation-wide summary by GP
GPsummary = process.getGPsummary(**publicData)
```

### Load additional public (not part of ESNEFT tools)

#### Underlying indicators of Adult Skills Deprivation sub-domain
* English Language Proficiency
* Higher Education

```python
rename = ({
    'EthnicMinority': 'Non-white',
    'Income': 'Income',
    'Employment': 'Employment',
    'Education': 'Education',
    'Health': 'Health',
    'Crime': 'Crime',
    'Barriers (H&S)': 'Barriers (H&S)',
    'Environment': 'Environment'
})
LSOAsummary['Adult Education'] = load_adult_skills('../data/HigherEducation-LSOA11.csv')
LSOAsummary['English Proficiency'] = load_english_language('../data/EnglishLanguage-LSOA11.csv')
LSOAsummary = LSOAsummary.dropna().rename(rename, axis=1).copy()
```

### Prepare partial correlation analysis
* Set esneftOnly to True to run this analysis only on ESNEFT area
* Define the main deprivation domains, sub-domains and sub-subdomains we are interested in.
  * These features must all be present in the LSOAsummary data.
* Re-label the disease abbreviations for readability on the heatmap plots.

```python
esneftOnly = False # Set True to run analysis only os ESNEFT LSOA
if esneftOnly:
    LSOAsummary = LSOAsummary.loc[LSOAsummary['ESNEFT']].copy()
prefix = '-ESNEFT' if esneftOnly else ''
```

```python
# D
mainDeprivationDomains = ([
    'Income', 'Employment', 
    'Education', 'Health', 
    'Crime', 'Barriers (H&S)', 
    'Environment',
])

subDeprivationDomains = ([
    'YouthSubDomain', 'AdultSkills'
])

subsubDeprivationDomains = ([
    'Adult Education', 'English Proficiency'
])
```

### Perform partial correlation analysis

* Partial correlation attempts to compute a correlation coefficient while controlling for confounding factors.
* Demographic data and Domains of Deprivation are **not independent**,
  * Areas with high education deprivation are correlated with other areas of deprivation.
  * Partial correlation helps to isolate the impact of a **single domain of deprivation**.
* The below code simply loops through each disease and each domain of deprivation.
  * For each analysis we compute the correlation controlling for all other sub-domains + demographic data.

```python
demographics = ['Age (median)', 'Non-white', 'MaleProp']
allData = []
diseases = [i for i in LSOAsummary.columns if i.endswith('prevalance')]
allFeatures = mainDeprivationDomains + demographics
for disease in diseases:
    parcorr = []
    for target in allFeatures + subDeprivationDomains + subsubDeprivationDomains:
        if target in subDeprivationDomains + subsubDeprivationDomains:
            covars = [i for i in allFeatures if i != 'Education']
        else:
            covars = [i for i in allFeatures if i != target]
        corr = partial_corr(
            data=LSOAsummary, x=target, y=disease, 
            covar=covars, method='spearman')
        corr.index = [target]
        parcorr.append(corr)
    parcorr = pd.concat(parcorr).sort_values('r', ascending=False)['r'].rename(disease.split('-')[0])
    allData.append(parcorr)
allData = pd.concat(allData, axis=1)
order = allData.abs().mean(axis=1).sort_values(ascending=False)
allData = allData.reindex(order.index)
```

### Plot Deprivation - Disease Correlation Heatmaps

```python
# Rename disease prevalance labels for readability on heatmaps
labels = ({
    'DM': 'Diabetes mellitus',
    'CAN': 'Cancer',
    'CKD': 'Chronic Kidney Disease',
    'NDH': 'Hyperglycaemia (ND)',
    'PC': 'Palliative care',
    'AF': 'Atrial fibrillation',
    'CHD': 'Coronary Heart Disease',
    'HF': 'Heart Failure',
    'HYP': 'Hypertension',
    'LVSD': 'LV Systolic Dysfunction',
    'PAD': 'Peripheral Arterial Disease',
    'STIA': 'Stroke & TIA', # Stroke & Transient Ischaemic Attack
    'AST': 'Asthma',
    'COPD': 'COPD', # Chronic Obstructive Pulmonary Disease
    'OB': 'Obesity',
    'SMOK': 'Smoking',
    'DEM': 'Dementia',
    'DEP': 'Depression',
    'EP': 'Epilepsy',
    'LD': 'Learning Disability',
    'MH': 'Mental Health'  
})

allData = allData.rename(labels, axis=1)
```

```python
# Get global min/max to fix colour scale across heatmaps
vmax = allData.max().max()
vmin = allData.min().min()

# Set plot resolution
dpi = 300

# Set heatmap size
figsize = (7, 7)
```

#### 7 Domains of Deprivation

* Here we first look at all 7 main domains.
  * **Education** is identified as a strong determinant of Diabetes.

```python
fig, ax = plot_deprivation_heatmap(
    data=allData.loc[allData.index.isin(mainDeprivationDomains)].T,
    vmin=vmin, vmax=vmax, rotate_x=True, figsize=figsize,
    label="Partial Spearman's Correlation Coefficient")
ax.set_xlabel('Deprivation Domains')
fig.tight_layout()
fig.savefig(f'../plots/deprivation-vs-prevalence{prefix}.png', dpi=dpi)
```

#### Sub-domains of Education Deprivation (Youth Skills and Adult Skills)

* So we study the 2 sub-domains of Education (Youth Skills and Adult Skills)
  * **Adult Skills** is identified as a strong determinant of Diabetes.

```python
fig, ax = plot_deprivation_heatmap(
    data=allData.loc[allData.index.isin(subDeprivationDomains)].T,
    vmin=vmin, vmax=vmax, figsize=figsize,
    label="Partial Spearman's Correlation Coefficient")
ax.set_xticklabels(['Adult Skills', 'Youth Skills'])
ax.set_xlabel('Education Deprivation Sub-domains')
fig.tight_layout()
fig.savefig(f'../plots/deprivation-vs-prevalence-subdomain{prefix}.png', dpi=dpi)
```

#### Sub-subdomains of Adult Skills (Adult Education and English Language Proficiency)

* So we study the 2 sub-subdomains of Adult Skills (Adult Education and English Language Proficiency)
  * **Adult Education** is identified as a strong determinant of Diabetes.

```python
fig, ax = plot_deprivation_heatmap(
    data=allData.loc[allData.index.isin(subsubDeprivationDomains)].T,
    vmin=vmin, vmax=vmax, figsize=figsize,
    label="Partial Spearman's Correlation Coefficient")
ax.set_xticklabels(['Adult Education', 'English Language Proficiency'])
ax.set_xlabel('Adult Skills Deprivation Indicators')
fig.tight_layout()
fig.savefig(f'../plots/deprivation-vs-prevalence-subAdultSkills{prefix}.png', dpi=dpi)
```

```python
fig, ax = plt.subplots()
sns.kdeplot(data=GPsummary, x='AdultSkills', y='DM-prevalance', fill=True, ax=ax)
sns.regplot(data=GPsummary, x='AdultSkills', y='DM-prevalance', order=1, scatter=False, ax=ax)
ax.set_ylim(0, 0.15)
ax.set_ylabel('Diabetes prevalance')
fig.tight_layout()
fig.savefig(f'../plots/national_prevalance_by_AdultSkills.png', dpi=300)
```

```python
metrics = ({'DM019-BP': 'BP < 140/80 mmHg', 'DM020-HbA1c': 'IFCC-HbA1c < 58 mmol/mol'})
fig, axes = plt.subplots(1, 2, figsize=(12, 7), sharex=True, sharey=True)
axes = axes.flatten()
for i, (metric, label) in enumerate(metrics.items()):
    rho, p = spearmanr(GPsummary[['AdultSkills', metric]].dropna())
    sns.kdeplot(data=GPsummary, x='AdultSkills', y=metric, fill=True, ax=axes[i])
    sns.regplot(data=GPsummary, x='AdultSkills', y=metric, scatter=False, ax=axes[i])
    axes[i].set_title(f"{label} (Rho  = {rho:.2f}, {formatP(p)})", loc='left')
    axes[i].set_ylim(0.2, 0.9)
    axes[i].set_xlabel('Adult Skills Deprivation')
axes[0].set_ylabel('Proportion of patients meeting treatment target')
fig.tight_layout()
fig.savefig(f'../plots/dm-metrics-by-AdultSkills.png', dpi=300)
```

```python
prev_by_imd = sns.lmplot(
    data=LSOAsummary, x='Age (median)', 
    y='DM-prevalance', hue='AdultSkills (q5)', 
    legend=False, scatter=False)
prev_by_imd.set(ylabel='Diabetes prevalance')
prev_by_imd.fig.get_axes()[0].legend(
    loc='lower right', title='Adult Skills\nDeprivation\n  (quintile)')
prev_by_imd.savefig(f'../plots/prevalance-age-by-AdultSkills.png', dpi=300)
```

```python

```
