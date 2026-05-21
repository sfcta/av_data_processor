import sys, argparse, tomllib
import numpy as np
import pandas as pd
from pathlib import Path
from data_models.nhtsa.reports import ads_crashes, ads_crash_reports
from utils.helpers import map_similar_strings

def normalize_company(name):
    if isinstance(name, str):
        return (name
                .replace('.','')
                .replace(',','')
                .replace('Research and Development NA','')
                .replace('Research and Development North America','')
                .replace('RD NA','')
                .replace('Corporation','')
                .replace('Corp','')
                .replace('INC.','')
                .replace('Inc.','')
                .replace('inc.','')
                .replace('INC','')
                .replace('Inc','')
                .replace('inc','')
                .replace('LLC','')
                .replace('LLc','')
                .replace('Llc','')
                .replace('llc','')
                #.split(' ')[0]
                )
    return name

def nan_to_str(x):
    if pd.isna(x):
        return 'None'
    return x

def empty_str_to_value(x, value, coerce_integer=True):
    if isinstance(x, str):
        if len(x.strip()) == 0:
            return value
    if coerce_integer:
        try:
            return int(x)
        except:
            return x

def format_hhmm(x):
    if isinstance(x, str):
        if ':' in x:
            return '{:02d}:{:02d}'.format(
                    int(x.split(':')[0]), 
                    int(x.split(':')[1])
                    )
        else:
            return None
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
    df_renamed['incident_time'] = df_renamed['incident_time_(24:00)'].map(lambda x: format_hhmm(x))
    
    # deal with typos
    df_renamed['city'], city_mapping = map_similar_strings(df_renamed['city'])
    df_renamed['state'], state_mapping = map_similar_strings(df_renamed['state'])
    df_renamed['operating_entity'] = df_renamed['operating_entity'].map(normalize_company)
    df_renamed['operating_entity'], operating_entity_mapping = map_similar_strings(df_renamed['operating_entity'])

    # deal with missing state
    df_renamed.loc[df_renamed['state'].map(lambda x: len(x.strip()) == 0),'state'] = 'XX'

    # drop non-ADS records
    print('dropping {} records w/out ADS engaged'.format(
        len(df_renamed.loc[df_renamed['automation_system_engaged'].ne('ADS')])
    ))
    df_renamed = df_renamed.loc[df_renamed['automation_system_engaged'].eq('ADS')]

    # fill in missing incident ids with psuedo ids
    blank_same_incident_id_indices = list(df_renamed.loc[df_renamed['same_incident_id'].map(lambda x: len(x.strip()) == 0)].index)
    print('generating psuedo `same_incident_ids` for: {}'.format(blank_same_incident_id_indices))
    new_ids = ['{:015d}'.format(x) for x in blank_same_incident_id_indices]
    df_renamed.loc[blank_same_incident_id_indices, 'same_incident_id'] = new_ids

    # 
    df_renamed['model_year'] = df_renamed['model_year'].map(lambda x: empty_str_to_value(x, 1901))
    '''print('dropping {} records with blank incident_time'.format(
        len(df_renamed.loc[pd.isna(df_renamed['incident_time'])])
    ))
    df_renamed = df_renamed.loc[pd.notnull(df_renamed['incident_time'])]'''

    return df_renamed, city_mapping, state_mapping, operating_entity_mapping

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

def read_and_validate(config, write_mapping_files=True):
    _df, city_map_latest, state_map_latest, oe_map_latest = preprocess(
        pd.read_csv(Path(config['indir']) / config['crash_report_latest'], keep_default_na=False)
    )
    df_latest = get_validated(_df, ads_crash_reports)

    _df, city_map_legacy, state_map_legacy, oe_map_legacy = preprocess(
        pd.read_csv(Path(config['indir']) / config['crash_report_legacy'], keep_default_na=False)
    )
    df_legacy = get_validated(_df, ads_crash_reports)
    df_merged = pd.concat([df_legacy, df_latest], ignore_index=True)

    city_map = pd.concat([city_map_latest,city_map_legacy]).groupby(['left','right','ratio']).sum()
    state_map = pd.concat([state_map_latest,state_map_legacy]).groupby(['left','right','ratio']).sum()
    oe_map = pd.concat([oe_map_latest,oe_map_legacy]).groupby(['left','right','ratio']).sum()

    city_map.to_csv(Path(config['outdir']) / config['city_map_file'])
    state_map.to_csv(Path(config['outdir']) / config['state_map_file'])
    oe_map.to_csv(Path(config['outdir']) / config['operating_entity_map_file'])

    return df_merged
    
def distill_incident_records(df, key='same_incident_id', allow_severity_downgrade=True):

    data = []
    grouped = df.groupby(key)
    fields = list(ads_crashes.model_fields.keys()) + list(ads_crashes.model_computed_fields.keys())

    for _id, _ind in grouped.indices.items():
        indices = list(_ind)
        s = None
        while len(indices) > 0:
            i = indices.pop()
            if not isinstance(s, pd.Series):
                s = df.loc[i].loc[fields]
            else:
                u = df.loc[i].loc[fields]

                '''s_inj = s.loc['highest_injury_severity_alleged']
                u_inj = u.loc['highest_injury_severity_alleged']

                if s_inj < u_inj:
                    print('downgrade in injury severity for {}: from {} to {}'.format(_id, s_inj, u_inj))
                    
                    if allow_severity_downgrade: 
                        u.loc['highest_injury_severity_alleged'] = np.nan

                qc_flag = s.ne(u) & ~s.isna() & ~u.isna() & ~s.index.isin(['highest_injury_severity_alleged', 'narrative'])
                if (len(s.loc[qc_flag]) > 0) and (len(u.loc[qc_flag]) > 0):
                    pass'''
                s.update(u)
        data.append(s)
    return pd.DataFrame(data)

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Process TOML configuration file for validation.")
    parser.add_argument("config_path", type=str, help="Path to the TOML configuration file.")
    
    # Check if the script is running in an interactive environment or not
    if len(sys.argv) > 1:
        # Running from command line, use the provided argument
        args = parser.parse_args()
        
        # Load the TOML configuration file
        with open(args.config_path, 'rb') as f:
            config = tomllib.load(f)['nhtsa']
    else:
        print("Please supply a config file.")
        sys.exit()

    df = read_and_validate(config, write_mapping_files=True)
    df_distilled = distill_incident_records(
        df
        )
    df_distilled.to_csv(
        Path(config['outdir']) / config['ads_crash_file'], 
        index=False
        )
    print('Done.')

    