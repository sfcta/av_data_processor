import sys, os
import numpy as np
import pandas as pd
from data_models.nhtsa.reports import ads_crashes, ads_crash_reports

INDIR = r'Q:\Data\Regulatory\AV\NHTSA'
CRASH_REPORT = r'Q:\Data\Regulatory\AV\NHTSA\Downloads\20260204\SGO-2021-01_Incident_Reports_ADS.csv'
CRASH_REPORT_LEGACY = r'Q:\Data\Regulatory\AV\NHTSA\Downloads\20250819\SGO-2021-01_Incident_Reports_ADS - 20210701-20250615.csv'
REPORTING_END_DATE = '20251215'
OUTDIR = r'O:\InterOrg Coordination\New Mobility\AV\NHTSA'

def normalize_company(name):
    if isinstance(name, str):
        return (name.lower()
                .replace('.','')
                .replace(',','')
                .split(' ')[0]
                )
    return name

def nan_to_str(x):
    if pd.isna(x):
        return 'None'
    return x

def format_hhmm(x):
    if isinstance(x, str):
        return '{:02d}:{:02d}'.format(
                int(x.split(':')[0]), 
                int(x.split(':')[1])
                )
    return x
                                      

def preprocess(df):
    '''
    Docstring for preprocess
    
    :param df: Description
    '''
    df_renamed = df.rename(
        columns={x: (x.lower()
                    .replace(' / ','_')
                    .replace(' - ','_')
                    .replace(' ','_')
                    .replace('?','')) 
                for x in df.columns}
    )

    df_renamed['driver_operator_type'] = df_renamed['driver_operator_type'].replace(np.nan, 'None')
    df_renamed['driver_operator_type'] = df_renamed['driver_operator_type'].replace('Other, see Narrative','Other')
    #df_renamed['engagement_status'] = df_renamed['engagement_status'].replace('Unknown - see Narrative','Unknown - See Narrative')
    df_renamed['city'] = df_renamed['city'].replace(np.nan, 'None')
    df_renamed['state'] = df_renamed['state'].replace(np.nan, 'None')
    df_renamed['incident_time'] = df_renamed['incident_time_(24:00)'].map(lambda x: format_hhmm(x))
    df_renamed['operating_entity'] = df_renamed['operating_entity'].map(lambda x: normalize_company(x))

    print('dropping {} records w/out ADS engaged'.format(
        len(df_renamed.loc[df_renamed['automation_system_engaged'].ne('ADS')])
    ))

    df_renamed = df_renamed.loc[df_renamed['automation_system_engaged'].eq('ADS')]

    print('dropping {} records with blank same_incident_id'.format(
        len(df_renamed.loc[df_renamed['same_incident_id'].map(lambda x: len(x.strip()) == 0)])
    ))
    df_renamed = df_renamed.loc[df_renamed['same_incident_id'].map(lambda x: len(x.strip()) > 0)]

    print('dropping {} records with blank model_year'.format(
        len(df_renamed.loc[pd.isna(df_renamed['model_year'])])
    ))
    df_renamed = df_renamed.loc[pd.notnull(df_renamed['model_year'])]

    print('dropping {} records with blank incident_time'.format(
        len(df_renamed.loc[pd.isna(df_renamed['incident_time'])])
    ))
    df_renamed = df_renamed.loc[pd.notnull(df_renamed['incident_time'])]

    df_renamed = df_renamed.fillna('None')
    return df_renamed

def get_validated(df, model):
    '''
    Docstring for get_validated
    
    :param df: Description
    '''
    data = []

    for idx, row in df.iterrows():
        d = row.to_dict()
        d1 = model(**d)
        data.append(d1.model_dump().values())

    df_valid = pd.DataFrame(columns = list(model.model_fields.keys()) + list(model.model_computed_fields.keys()),
                            data = data)
    return df_valid

def read_and_validate(filepath):
    df = get_validated(
        preprocess(
            pd.read_csv(filepath)
        ), 
        ads_crash_reports
    )
    return df
    
def distill_groups(df, key='same_incident_id'):

    data = []
    grouped = df.groupby(key)
    for _id, _ind in grouped.indices.items():
        indices = list(_ind)
        s = None
        while len(indices) > 0:
            i = indices.pop()
            if not isinstance(s, pd.Series):
                s = df.loc[i].loc[ads_crashes.model_fields.keys()]
            else:
                u = df.loc[i].loc[ads_crashes.model_fields.keys()]

                s_inj, u_inj = s.loc['highest_injury_severity_alleged'], u.loc['highest_injury_severity_alleged']
                if s_inj < u_inj:
                    print('overriding downgrade in injury severity for {}: from {} to {}'.format(_id, s_inj, u_inj))
                    u.loc['highest_injury_severity_alleged'] = np.nan

                qc_flag = s.ne(u) & ~s.isna() & ~u.isna() & ~s.index.isin(['highest_injury_severity_alleged', 'narrative'])
                if (len(s.loc[qc_flag].dropna()) > 0) and (len(u.loc[qc_flag].dropna()) > 0):
                    
                    print(s.loc[qc_flag].dropna())
                    print(u.loc[qc_flag].dropna())
                s.update(u)
        data.append(s)
    return pd.DataFrame(data)

if __name__=='__main__':
    df_latest = read_and_validate(CRASH_REPORT)
    df_legacy = read_and_validate(CRASH_REPORT_LEGACY)

    df_merged = pd.concat([df_legacy, df_latest], ignore_index=True)
    print(df_merged.loc[480:])
    df_distilled = distill_groups(
        df_merged
        )
    
    df_distilled.to_csv(os.path.join(OUTDIR, 'crashes_ads_clean_{}.csv'.format(REPORTING_END_DATE)), index=False)
    

    