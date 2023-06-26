# Diabetes Prevalence Management and Health Inequalities

## NHS England Data Science Internship Programme

### Stephen Richer & Paul Carroll, June 2022 - Dec 2022

#### Overview
Socioeconomic inequality of diabetes prevalence and access to diabetes treatment is well-documented [Barnard-Kelly and Cherñavvsky, 2020](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC7136366/).
In both Type 1 Diabetes Mellitus (T1D) and Type 2 Diabetes Mellitus (T2D), deprived individuals are significantly less likely to receive all NICE recommended care processes.
Similarly, deprived individuals are less likely to meet treatment targets for Hemoglobin A1C (HbA1C), Body Mass Index (BMI) and cholesterol.
Lifestyle risk factors of T2D, including smoking, obesity and lack of physical activity are all more prevalent in deprived households.
Together this can contribute to a 77% increased risk of developing T2D among the most deprived individuals compared to the least deprived [Roper et al., 2001](https://pubmed.ncbi.nlm.nih.gov/11397742/).
Ultimately, a comprehensive understanding of the underlying factors associated with this inequality is critical for addressing these
issues.

This work explores how indicators of deprivation are associated with the prevalence of diabetes across England.
In addition, this work also investigates patterns of deprivation associated with utilisation of the Ipswich Diabetes Centre within East Suffolk and North Essex NHS Foundation Trust (ESNEFT).
Patients from deprived backgrounds were found to have significantly worse health metrics, including higher BMI, HbA1C and
Urine Microalbumin upon initial referral to the centre.
While this works highlights potential health inequalities associated with diabetes, it also indicates that these inequalities may be modifiable and could lead to improvements in population health.


#### Walkthrough

The project began with Public Health England and ESNEFT trust stakeholders keen to explore links between Diabetes and Inequalities.
The approach taken in this project was to look at Diabetes as a condition. This isn't a common approach taken within the NHS, as most metrics within the Health Service look at Primary Care treatment, or Secondary Care treatment, and take a service-based approach to patterns, identification of conditions, and treatments. In order to be able to assess this approach, and develop hypotheses, the accumulation of patient data was necessary, and necessary across the different patient touch points. 
Data for Diabetes patients exists in different locations. This project focused on patient data in the following four locations: Primary Care (General Practice) Data, Secondary Care (Referral to Hospital specialists), Accident & Emergency Data, and Diabetes Centre data. One of the initial steps of this project was to request this data, and attempt to join the data for a full, holistic picture of condition specific pathways. In linking primary and secondary care, how would this help outline and identify disease specific pathways. The first aim of the project was to build this pathway as best possible, and put together a timeline of patients with Diabetes, within the ESNEFT area, across the available data sources. Using this data, the Stakeholders raised the following questions; could Diabetes be predicted? What are the associated conditions/ diseases, and can we identify when these might take place. 
The second strand of data within this project was around inequalities. Confounders around inequalities were similarly laid out; should we approach inequalities from a Geospatial (LSOA) perspective; How do we quantify an individual in a certain socio-economic group without their individual data. Are there demographic data points that can be viewed from the hospital data, or is the data inferred, e.g. from LSOA.


The first repo in the project (https://github.com/nhsx/morbidity_network_analysis) was designed from investigating the preliminary hospital dataset for the diabetes patients. This mainly involved Secondary care data, but was also joined with Accident and Emergency Data. From this data, analysis was undertaken to identify comorbidities. What other conditions or diseases were apparent alongside the onset of diabetes. Were these conditions linked before, during, and to what severity. The code within the repo produces a network table that identifies conditions and their connections. The size of the circles denotes prevalence. The code within this repo can be reused on other datasets, the parameters need adjusting, and some exploratory data analysis and refinement before running the main body of code. 


Exploration of the data at the first stage of this project, was mainly about getting to know the data. This involved taking one of the available datasets, the hospital data, A&E and Secondary Care, and looking into patterns within the data. The Secondary Care dataset was the dataset used for the DNAattend repo (https://github.com/nhsx/dna-risk-predict). The aim of this repo was to see if attendance / non-attendance could be predicted using the historic attendance of patients. Whilst this was the experimented repo based on the dataset, the published repo contains no real data and is a simulation using randomised false data, so not based at all on the Secondary Care Data. Important to note from this is the range of simulation data. This was taken from a general age range and distribution of the underlying data, but in no way can be connected back to the real data. 


There existed an underlying thesis and a question around inequalities and attendance. Could attendance to Secondary Care appointments have anything to do with how diabetes developed within patients. This developed further into a question around when Diabetes was picked up, how different groups within the inequalities spectrum were identified with Diabetes, and furthermore what their blood sugar readings were when Diabetes was picked up. In order to carry out these analyses, one would need to identify at which medical intervention Diabetes was picked up. From the data, there could be three examples of this, although the vast majority would occur within the following two areas, GP Practices, and Accident & Emergency. The third was potentially the Diabetes Centre. 
LSOA analysis was then used to identify patients using their GP Practice locations. This method was chosen given the alternative was patient addresses. With the aim of being able to identify whether GP Practices picked up Diabetes more quickly, perhaps if they had a diabetes specialist, or diabetes nurse present, the method of the GP LSOA was chosen, as for the vast majority of patients, their GP practice was within a walkable distance in urban locations, and within a short drivable distance in rural areas. One assumption put forward within a hypothesis was access to healthcare being correlated to wealth via LSOA. A conclusion that did come out of the joined data, was that patients from the more deprived LSOAs generally had to wait longer for diabetes specialist appointments, were seen later post their first diagnosis, and had higher HbA1c readings when they were tested post diagnosis. These findings are shown within the slide pack. 


Drawing all the different data sources together, the project progressed attempting to identify and draw conclusions from the underlying patient pathway data. Primary care had been joined to secondary care data where possible, and in turn, added to A & E data, and Diabetes Centre data. The patient cohort was around 10000 patients. But this was by no means comprehensive. Even within this data, it was commonplace to find a patient with their opening data from year 2006 for example, and have their data for two years. Often we then found a gap in their data, e.g. up to 2018 where the patient reappeared within the dataset. This didn't mean that their data didn't exist, it just wasn't searchable within the ESNEFT data. How to deal with this missingness, and to still draw conclusions, presented a different set of issues. In the end, a decision was made not to impute or infer anything from missingness, and to just go ahead with the data available. With this pathway data now availble, the inequalities analysis via GP LSOA was joined to this data to investigate links between conditions, mainly Diabetes, and inequalites/ deprivation. The deprivation analysis via LSOA was not perfect, but was a best fits approach. 
The analysis from this piece of work is visible within part 1 of the slides. Several of the slides show heatmaps, with the prevalent conditions identified within the population, and correlation examination between these conditions and the seven factors of LSOA analyis. These heatmaps allow for interpretations and conclusions to be drawn from the data. Two main conclusions were drawn from the data; Health deprivation is most strongly associated with disease prevalance, Education deprivation is second most strongly associated with disease prevalance. In particular, Diabetes is highly associated with Education deprivation. The education part is one of seven indicators within LSOA analysis. But the education part is made up of two underlying indicators, Adult Skills, and Youth Skills. Adult Skills was identified as the predominant underlying indicator most strongly associated with Diabetes prevalence. The analysis was repeated again with a further breakdown of Adult Skills into Adult Education and English Language Proficiency. Of the two, Adult Education was identified as the predominant underlying indicator most strongly associated with Diabetes prevalence. English Language Proficiency shows minimal association with disease prevalence. 


These conclusions we hope could lead to further work, and perhaps direct further investigation by PHE for possible intervention based modeling or analysis within the education for younger adults either with Diabetes or with a higher likelihood of getting diabetes. 
In conclusion, there were several areas of research that this work explored but for which was unable to produce significant conclusions. Some of the questions posed by stakeholders remain unanswered, e.g. Can you predict Diabetes? Without full patient pathway data, we were unable to successfully pursue this question. Comorbidities were able to be found, but the exact timing, and what came when, or what condition led to another condition, was again unable to be resolved without a complete patient data pathway. Several of the questions were partially answered, how did inequalities affect diagnosis of, and treatment of diabetes. These were partially answered with the Hb1Ac reading levels and timings of patient appointments from more deprived areas. Again, the assumptions present with LSOA being used as the main factor here for assessment of deprivation level is extremely generalised, and presents a certain view of patient that may not be accurate. We would hope with this generalisation, within the assessment of patients' levels of deprivation, that given the LSOA level, there would be a certain balancing out of the patients, that would correspond to the LSOA deprivation level. Perhaps further analysis of deprivation could be undertaken using patient survey data, or another financial level assessment of their income and outgoings. This certainly opens the scope for further analysis, but as yet remains the best practice approach taken here. 
Questions that this research project was able to provide some answers for, were the questions asked around inequalities and diabetes and what learnings are visible from this connection. There is definitely a correlation between adult education level and prevalence of diabetes. And the prevalence of diabetes is associated with poor health and a variety of other conditions, for which age does not make a difference to the most deprived demographic group. This pattern isn't visible in the other 4 deprivation groups from second most deprived onward, and is another area that could suggest further study especially for PHE and for any intervention-based approaches.  

 
 

#### Resources
- [Project report](./stephen-richer-report.pdf)
- [Diabetes Centre Analysis Scripts](./scripts/)

#### Project Repositories
A number of additional tools were built to complement the analysis conducted in this work.
In addition, these projects can function as standalone utilities independent of the diabetes work.
Note that the tools presented here are still experimental and are not currently deployed in real-world clinical settings.
- **ESNEFT Tools** - Python Suite for Demographic and Health Inequality Analysis.
  - Available at: [https://github.com/nhsx/p24-diabetes-inequal](https://github.com/nhsx/p24-diabetes-inequal)
- **DNAttend** - AutoML framework for predicting patient non-attendance.
  - Available at: [https://github.com/nhsx/dna-risk-predict](https://github.com/nhsx/dna-risk-predict)
- **MultiNet** - Build and visualise multi-morbidity networks to discover significant disease associations.
  - Available at: [https://github.com/nhsx/morbidity_network_analysis](https://github.com/nhsx/morbidity_network_analysis)
  
#### How to Run the scripts in this Repo, you will need to carry out installations from other repos in order to run the scripts in this one. 

- Deprivation-analysis.md (main external dependency is ESNEFT_Tools)
Clone the repo and install in a location of your choice. 
In order to run this script you will need to install esneft_tools on your machine first. 
ESNEFT_TOOLS and instructions are located here....https://github.com/nhsx/p24-diabetes-inequal
Run this command in your terminal. python3 -m pip install esneft_tools
After this open the notebook or vscode notebook in the same location as the utils.py file within scripts for this repo.
Then you should be able to run this repo. 




#### Bibliography
- Katharine D. Barnard-Kelly and Daniel Cherñavvsky. Social Inequality and Diabetes: A Commentary, 2020. ISSN 18696961.
- N. A. Roper, R. W. Bilous, W. F. Kelly, N. C. Unwin, and V. M. Connolly. Excess mortality in a population with diabetes and the impact of material deprivation: Longitudinal, population based study. British Medical Journal, 322(7299), 2001. ISSN 09598146. doi: 10.1136/bmj.322.7299.1389.
