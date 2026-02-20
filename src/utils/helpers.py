import re
import pandas as pd
from typing import Any
from math import nan, isnan
from fuzzywuzzy import fuzz


numeric_re = r'\d+|(\d+(,\d{3})*(\.\d+)?)'
redacted_re = r'([Rr][Ee][Dd][Aa][Cc][Tt][Ee][Dd])'
na_re = r'([Nn]/{0,1}[Aa])'


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
    elif isinstance(value, str) and (value.upper() == 'REDACTED' or value.upper() == 'NOT APPLICABLE'):
        return value
    raise ValueError('{} is not type {} or str `REDACTED`'.format(value, primary_type))

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