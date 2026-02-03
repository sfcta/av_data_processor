# 2020
import sys, os, re
import pandas as pd

from utils.helpers import read_data_dictionary, find_name_match, fix_field_names

class ReportReader:
    def __init__(self, indir='', company='uber', year=2022, data_dict=None):
        
        # TODO: put this dict into the config instead
        YEAR_TNAME_FNAME = {2022: {'Trip-Level':'Trips',
                           'Month-Level': 'Month',
                           'Monthly Tract': 'Monthly_Tract',
                           'Incidents-Complaints': 'Incidents_Complaints',
                           'Incidents-Location': 'Incidents_Location',
                           'Chargers': 'Chargers',
                           'Charging-Sessions': 'Charging_Sessions',
                                        
                          },
                          
                   }
        
        self.indir = indir
        self.company = company.lower()
        self.year = year
        
        self.tname_to_fname = YEAR_TNAME_FNAME[self.year]
        self.tnames = self.tname_to_fname.keys()
        self.fname_to_tname = {v: k for k, v in self.tname_to_fname.items()}
        self.fnames = self.fname_to_tname.keys()
        
        if isinstance(data_dict, str):
            self.data_dict = read_data_dictionary(data_dict)
        elif isinstance(data_dict, dict):
            self.data_dict = data_dict
        elif data_dict==None:
            self.data_dict = None
        else:
            raise Exception('Unknown data dict type {}.  Must be string path to data dictionary or a dictionary of pandas DataFrames.'.format(type(data_dict)))
            
        
    def get_report_file_attrs(self, f):
        c = re.compile('(?P<resub>Resubmission_){0,1}(?P<cc>[a-zA-Z0-9]+)_(?P<date>\d{8}|\d{4}_\d{2}_\d{2}|\d{4}_\d{2}|\d{6})_AV_(?P<name>[a-zA-Z0-9_]+)_[pP]art(?P<part>[0-9]+)[ _-]*(?P<redacted>redacted|Redacted|REDACTED){0,1}\.csv')
        d = c.match(f)
        
        if d == None:
            return {'resub':'','cc':'','date':'','name':'','part':'','redacted':''}
        return d.groupdict()
        
    def get_report_fnames(self, table_name):
        fname_root = self.tname_to_fname[table_name]
        
        fnames = []
        for f in os.listdir(self.indir):
            d = self.get_report_file_attrs(f)
            if d['name'] == fname_root:
                fnames.append(f)
        return fnames
        
    def read_report(self, table_name, chunksize=None, nrows=None, simplify_names=False, fix_names=False, groupby=None, agg_args=None, agg_piecewise=False):
        '''
        Read a TNC annual report
        '''
        files = self.get_report_fnames(table_name)
        
        dfs = []
        if chunksize==None:
            for f in files:
                df = pd.read_csv(os.path.join(self.indir,f))
                if simplify_names:
                    df.rename(columns={c:c.lower().replace(' ','').replace('_','').replace('-','') for c in df.columns}, inplace=True)
                if (isinstance(groupby, list) or isinstance(groupby, str)) and isinstance(agg_args, dict):
                    df = df.groupby(groupby, as_index=False).agg(agg_args)
                dfs.append(df)
                
            df = pd.concat(dfs)
            
            if fix_names and isinstance(self.data_dict, dict):
                df = fix_field_names(df, self.data_dict[table_name])
                
            if (isinstance(groupby, list) or isinstance(groupby, str)) and isinstance(agg_args, dict):
                df = df.groupby(groupby).agg(agg_args)
            yield df
        else:
            for f in files:
                for chunk in pd.read_csv(os.path.join(self.indir, f), chunksize=chunksize, nrows=nrows, encoding='cp1252'):
                    if fix_names and isinstance(self.data_dict, dict):
                        chunk = fix_field_names(chunk, self.data_dict[table_name])
                    yield chunk
                
        