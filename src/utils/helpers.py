import re
import pandas as pd

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