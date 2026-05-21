import re, csv
import pandas as pd
from typing import Any
from math import nan, isnan
from fuzzywuzzy import fuzz
from pathlib import Path
from utils.regex import redacted_re, na_re

def get_aliases(Model, drop_unaliased=True, required_only=False):
    aliases = []
    for field, field_info in Model.model_fields.items():
        if not required_only or (required_only and field_info.is_required()):
            if field_info.alias != None:
                aliases.append(field_info.alias)
            elif not drop_unaliased:
                aliases.append(field)
    return aliases

def get_header(ifile, encoding=None, drop_unnamed=True):
    df = pd.read_csv(ifile, encoding=encoding, nrows=0)
    header = []
    for c in df.columns:
        if not 'Unnamed:' == c[:8]:
            header.append(c)
    return header

def header_model_match_ratio(header, Model, min_header_ratio=0.80, fuzzy=False, min_fuzzy_ratio=0.50, drop_unaliased=True, required_only=True):
    aliases = get_aliases(Model, drop_unaliased, required_only)

    matches = 0
    expected_matches = len(header)

    if expected_matches == 0:
        print('no expected matches')
        return 0
    
    # hack for dmv first-time-filer files
    if (len(aliases) / expected_matches) < min_header_ratio:
        #print('aliases: {}, expected: {}'.format(len(aliases), expected_matches))
        return (len(aliases) / expected_matches)

    for name in header:
        best_r = 0
        best_alias = None
        
        for alias in aliases:
            if name.strip().lower() == alias.strip().lower():
                best_r = 100
                best_alias = alias
                break
            elif fuzzy:
                r = fuzz.ratio(name.lower(), alias.lower())
                if r > best_r and r > min_fuzzy_ratio * 100:
                    best_r = r
                    best_alias = alias
        if best_alias != None:
            matches += 1

    return matches / expected_matches  

def get_header_rename_dict(ifile, Model, fuzzy=False, min_fuzzy_ratio=0.50, drop_unaliased=True, required_only=False, manual={}):
    aliases = get_aliases(Model, drop_unaliased, required_only)
    rename = {}

    columns = pd.read_csv(ifile, nrows=0).columns.tolist()
    header = get_header(ifile)

    for k, v in manual.items():
        if k in header:
            rename[k] = v

    if not fuzzy:
        for name in header:
            for alias in aliases:
                if (
                    (name != alias) and 
                    (name.strip().lower() == alias.strip().lower())
                   ):
                    rename[name] = alias
                    break
    else:
        for name in header:
            best_r = 0
            best_alias = None
        
            for alias in aliases:
                r = fuzz.ratio(name.lower(), alias.lower())
                
                if r > best_r and r > min_fuzzy_ratio * 100:
                    best_r = r
                    best_alias = alias
                    #print(name, alias, r)
                    
            if (
                (name != best_alias) and 
                (best_alias != None) and 
                (best_alias not in rename.values()) and # avoid name collisions
                (best_alias not in header) # avoid name collisions
               ):
                rename[name] = best_alias
    
    return rename

def get_attr_from_path(path):
    meta_re = r'.*(?P<report_period>\d{4}-\d{1,2}-\d{1,2}_\d{4}-\d{1,2}-\d{1,2})[\\/](?P<company>[a-zA-Z0-9\.]*).*[\\/].*.csv'
    compiled_meta_re = re.compile(meta_re)
    
    try:
        meta = compiled_meta_re.match(str(path)).groupdict()
    except:
        raise Exception('No attr match for {}'.format(path))

    if 'driverless' in str(path).lower():
        meta['driver_type'] = 'driverless'
    elif 'drivered' in str(path).lower():
        meta['driver_type'] = 'drivered'
    elif meta['report_period'] < '2023-06-01' and meta['company'].lower() == 'waymo':
        meta['driver_type'] = 'drivered'
    elif meta['report_period'] < '2022-06-01' and meta['company'].lower() == 'cruise':
        meta['driver_type'] = 'drivered'
    else:
        meta['driver_type'] = 'driverless'

    return meta

def get_dmv_attr_from_filepath(path):
    meta_re = r'.*[\\/](?P<year>\d{4})[\\/][a-zA-Z0-9-_\s]*(?P<report_type>([Mm][Ii][Ll][Ee][Aa][Gg][Ee])|([Dd][Ii][Ss][Ee][Nn][Gg][Aa][Gg][Ee][Mm][Ee][Nn][Tt]))[a-zA-Z0-9-_\s\(\)]*.csv'
    compiled_meta_re = re.compile(meta_re)
    
    try:
        meta = compiled_meta_re.match(str(path)).groupdict()
    except:
        raise Exception('No attr match for {}'.format(path))

    if 'driverless' in str(path).lower():
        meta['driver_type'] = 'driverless'
    else:
        meta['driver_type'] = 'drivered'

    if 'first' in str(path).lower():
        meta['first_time'] = 'first_time'
    else:
        meta['first_time'] = 'ongoing'

    return meta

def get_opath_from_ipath(ipath, oroot):
    attr = get_attr_from_path(ipath)
    return Path(oroot) / attr['report_period'] / attr['company'].lower() / attr['driver_type']

def copy_and_rename_headers(ifile, ofile, rename):
    with open(ifile, newline='', encoding="utf-8-sig") as inFile, open(ofile, 'w', newline='') as outfile:
        r = csv.reader(inFile)
        w = csv.writer(outfile)
    
        header_in = next(r, None)  
        header_out = []
        for h in header_in:
            if h.strip() in rename:
                header_out.append(rename[h.strip()])
            else:
                header_out.append(h.strip())
        
        # write new header
        w.writerow(header_out)
    
        # copy the rest
        for row in r:
            w.writerow(row)

def find_name_match(name, candidates):
    for c in candidates:
        if str(name).lower().strip().replace('_','').replace(' ','') == str(c).lower().strip().replace('_','').replace(' ',''):
            if str(name) == str(c):
                return (c, 'exact')
            else:
                return (c, 'approx')
    return (None, None)
    
def fix_field_names(report, data_dict):
    rename = {}
    for c in report.columns.tolist():
        m, t = find_name_match(c, data_dict.index.tolist())
        if m != None:
            rename[c] = m
      
    out = report.rename(columns=rename)
    return out
    
def dtype_mismatch(value, cpuctype):
    if cpuctype in ['Alpha','AlphaNumeric']:
        if not isinstance(value, str):
            return True
    else:
        try:
            value = pd.to_datetime(value)
        except:
            pass
        if isinstance(value, str):
            return True
    return False

def len_mismatch(value, length, precision=None):
    if len(str(value)) != length:
        return True

def lower_and_strip(x):
    if isinstance(x, str):
        return x.lower().strip()
    return x

def coerce_nan_to_none(x: Any) -> Any:
    if isinstance(x, float) and isnan(x):
        return None
    return x

def coerce_nan_to(x: Any, value=None) -> Any:
    if isinstance(x, float) and isnan(x):
        return value
    if isinstance(x, str):
        if x.upper() == 'N/A' or x.upper == 'NOT APPLICABLE':
            return value
    return x

def coerce_str_to_number(x: Any) -> Any:
    if isinstance(x, int) or isinstance(x, float):
        return x
    elif isinstance(x, str):
        try:
            x1 = x.replace(',','')
            if '.' in x:
                return float(x1)
            else:
                return int(x1)
        except:
            return x
    return x

def primary_type_or_na_or_redacted(value, primary_type):
    if isinstance(value, primary_type):
        return value
    value = value.strip()    
    if re.compile(redacted_re).fullmatch(value) or re.compile(na_re).fullmatch(value):
        return value
        
    raise ValueError('{} is not type {} or a match for {} or {}'.format(value, primary_type, redacted_re, na_re))

def primary_type_or_redacted(value, primary_type):
    if isinstance(value, str) and value.upper() == 'REDACTED':
        return value
    elif isinstance(value, primary_type):
        return value
    raise ValueError('{} is not type {} or str `REDACTED`'.format(value, primary_type))

def compare_if_numeric(value, le=None, lt=None, gt=None, ge=None):
    # check inputs
    if not isinstance(value, int) and not isinstance(value, float):
        return value
    
    if le != None:
        if not (isinstance(le, int) or isinstance(le, float)):
            raise ValueError('`le` must be float or int, instead value {} of type {} was passed.'.format(le, type(le)))
        if not value <= le:
            raise ValueError('{} is not le {}'.format(value, le))

    if lt != None:
        if not (isinstance(lt, int) or isinstance(lt, float)):
            raise ValueError('`lt` must be float or int, instead value {} of type {} was passed.'.format(lt, type(lt)))
        if not value < lt:
            raise ValueError('{} is not lt {}'.format(value, lt))

    if gt != None:
        if not (isinstance(gt, int) or isinstance(gt, float)):
            raise ValueError('`gt` must be float or int, instead value {} of type {} was passed.'.format(gt, type(gt)))
        if not value > gt:
            raise ValueError('{} is not gt {}'.format(value, gt))

    if ge != None:
        if not (isinstance(ge, int) or isinstance(ge, float)):
            raise ValueError('`ge` must be float or int, instead value {} of type {} was passed.'.format(ge, type(ge)))
        if not value >= ge:
            raise ValueError('{} is not ge {}'.format(value, ge))
    return value

def map_similar_strings(series):
    match = get_similar_string_mapping(
        series.map(lambda x: x.strip())
    )

    match_dict = match.set_index('right')['left'].to_dict()
    return (
        series.map(lambda x: match_dict[x.strip()]),
        match
    )
    

def get_similar_string_mapping(series):
    match = pd.DataFrame(columns=['left','right','ratio','count_right'])

    #df['company'] = df['Operating Entity'].map(lambda x: x.lower())

    for idx, row in series.items():
        right = row
        if right in match['right'].map(lambda x: x).tolist():
            match.loc[match['right'].eq(right),'count_right'] += 1
        else:
            left = right
            ratio = 100
            
            if len(match) > 0:
                ratios = match['left'].map(lambda x: fuzz.token_sort_ratio(x, right))

                if ratios.max() >= 85:
                    ratio = ratios.max()
                    left = match.loc[ratios.idxmax(),'left']
                    print('Matched       {} - {} at {}'.format(right, left, ratio))
                elif ratios.max() >= 60:
                    #print('Did not match {} to any of {}.'.format(right, match['left'].tolist()))
                    print('Did not match {} - {} at {}'.format(right, match.loc[ratios.idxmax(),'left'], ratios.max()))
            match = pd.concat([
                match, 
                pd.DataFrame.from_records({'left':[left],
                                        'right':[right],
                                        'ratio':[ratio],
                                        'count_right':[1] 
                                        })],
                            ignore_index=True
            )
    return match

def numeric_str_to_float(s, convert_errors_to_na=True):
    numeric_re = r'\d+|(\d+(,\d{3})*(\.\d+)?)'
    if isinstance(s, float):
        return s
    if isinstance(s, int):
        return float(s)
    if re.compile(numeric_re).match(s):
        return float(s.replace(',',''))
    else:
        if convert_errors_to_na:
            return nan
        return s

def read_data_dictionary(path, sheet_names=None):
    '''
    Read the data dictionary (dd) into a dict of name -> data dictionary
    '''
    # 
    # skip the first row.  Cell A1 has a report description, all others are blank
    dd_in = pd.read_excel(path, sheet_name=sheet_names, index_col=0)
    dd_out = {}
    name_re = '(?P<name>Trip-Level|Month-Level|Monthly Tract|Incidents-Complaints|Incidents-Location|Chargers|Charging-Sessions)'
    type_re = '(?P<type>Dictionary|Template)'
    tab_re = re.compile(name_re + '[ (Data)]+' + type_re)
    for sheet, df in dd_in.items():
        m = tab_re.match(sheet)
        if m != None:
            if m.groupdict()['type'] == 'Dictionary':
                dd_out[m.groupdict()['name']] = df
    return dd_out

def get_file_model(ifile, min_header_ratio=0.80, drop_unaliased=True, fuzzy=False, min_fuzzy_ratio=0.50, candidate_models=None, orientation='rows'):
    '''
    read in a file header, compare it to each model's aliases, and return the one that matches
    '''
    if candidate_models == None:
        candidate_models = [Trip, Month, TripTract, IncidentTract, Incident, IncidentLegacy, Charger, ChargingSession, Stoppage, StoppageFleet]
    elif isinstance(candidate_models, BaseModel):
        candidate_models = [candidate_models]

    if orientation == 'rows':
        header = get_header(ifile, encoding='cp1252') 
    elif orientation == 'columns':
        header = get_header(ifile, encoding='cp1252', orientation=orientation) 
    else:
        raise Exception('unknown orientation `{}`, expected `rows` or `columns`')
        

    best_r = 0
    best_M = None
    for M in candidate_models:
        r = header_model_match_ratio(header, 
                                     M, 
                                     drop_unaliased=drop_unaliased,
                                     min_header_ratio=min_header_ratio,
                                     fuzzy=fuzzy,
                                     min_fuzzy_ratio=min_fuzzy_ratio
                                    )
        print(M.__name__, r)
        if r == 1:
            return M

        elif r > best_r and r > min_header_ratio:
            best_r = r
            best_M = M

    return best_M
'''    
def get_report_descriptions(path, sheet_names=None):
    # read the first row only to get the report description
    tmp = pd.read_excel(path, sheet_name=sheet_names, nrows=0)
    desc = {}
    for k, v in tmp.items():
        print(k)
        desc[k] = v.columns[0]
    return desc
'''