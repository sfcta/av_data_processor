
import pandas as pd
import csv
from data_models.cpuc_deployment.reports import Trip, Month, Tract
from pathlib import Path
from datetime import datetime

def read_and_validate_dir(directory, rglob_pattern, Model, rglob_exclude=None):
    data = []
    i = 0
    
    start = datetime.now()
    
    for fname in sorted(Path(directory).rglob(rglob_pattern)):
        if isinstance(rglob_exclude, str):
            if rglob_exclude.lower() in str(fname).lower():
                continue
        
        permit_type = 'drivered'
        company = None
        
        for c in companies:
            if c in str(fname):
                if isinstance(company, str):
                    raise Exception('more than one valid company name found: {}, {}'.format(c, company))
                company = c
    
        if 'driverless' in str(fname).lower():
            permit_type = 'driverless'
        
        #print(fname)
        #print('company: {}, permit type: {}'.format(company, permit_type))
        
        with open(fname) as f:
            reader = csv.DictReader(f)        
            for row in reader:        
                # validate
                #trip = Model(**row).model_dump().values()
                #data.append([company, permit_type] + list(trip))
                try:
                    trip = Model(**row).model_dump().values()
                    data.append([company, permit_type] + list(trip))
                except Exception as e:
                    print('WARNING: could not parse {}'.format(fname))
                    print(row)
                    print(e)
                    break

    return (
        pd.DataFrame(columns = ['company','permit_type'] + list(Model.model_fields.keys()) + list(Model.model_computed_fields.keys()),
                     data = data)
    )

if __name__=='__main__':
     INDIR = r'Q:\Data\Regulatory\AV\CPUC\Quarterly Reports\Deployment'
     companies = ['Cruise','Waymo']
     
     month = read_and_validate_dir(
          directory=INDIR, 
          rglob_pattern='*Month*.csv', 
          Model=Month, 
          rglob_exclude='tract'
          )
     
     tract = read_and_validate_dir(
          directory=INDIR, 
          rglob_pattern='*Tract*.csv', 
          Model=Tract, 
          )