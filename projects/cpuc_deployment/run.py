
import pandas as pd
import sys, csv, re, argparse, tomllib
from shutil import copyfile
from data_models.cpuc_deployment.reports import (Trip, Month, TripTract, IncidentTract, Incident, IncidentLegacy, 
                                                 Charger, ChargingSession, Stoppage, StoppageFleet)
from pathlib import Path
from datetime import datetime
from utils.helpers import (get_opath_from_ipath, get_header_rename_dict, copy_and_rename_headers, 
                           get_attr_from_path, get_header, header_model_match_ratio)

def get_file_model(ifile, min_header_ratio=0.80, drop_unaliased=True, fuzzy=False, min_fuzzy_ratio=0.50):
    '''
    read in a file header, compare it to each model's aliases, and return the one that matches
    '''
    header = get_header(ifile) 

    best_r = 0
    best_M = None
    for M in [Trip, TripTract, Month, Incident, IncidentTract, IncidentLegacy, Charger, ChargingSession, Stoppage, StoppageFleet]:
        r = header_model_match_ratio(header, 
                                     M, 
                                     drop_unaliased=drop_unaliased,
                                     min_header_ratio=min_header_ratio,
                                     fuzzy=fuzzy,
                                     min_fuzzy_ratio=min_fuzzy_ratio
                                    )
        if r == 1:
            return M

        elif r > best_r and r > min_header_ratio:
            best_r = r
            best_M = M

    return best_M

def custom_preprocess(root):
    # This is missing TCPID, insert it and fill it with 'MISSING FIELD'
    f = Path(root) / '2023-09-01_2023-11-30/waymo/driverless/Month.csv'
    df = pd.read_csv(f)
    df.insert(0, 'TCPID', 'MISSING FIELD')
    df['TotalWAVsAvail'] = 'MISSING FIELD'
    df['TotalWAVsRequested'] = 'MISSING FIELD'
    df['TotalWAVsDeclinedUnavail'] = 'MISSING FIELD'
    df['TotalWAVsFulfilled'] = 'MISSING FIELD'
    df.to_csv(f, index=False)

    f = Path(root) / '2023-09-01_2023-11-30/cruise/driverless/IncidentLegacy.csv'
    df = pd.read_csv(f)
    df = df.iloc[0:1]
    df.to_csv(f, index=False)

    # TCP is unlabeled in the header, label it
    f = Path(root) / '2022-09-01_2022-11-30/waymo/drivered/IncidentTract.csv'
    df = pd.read_csv(f)
    df.rename(columns={'Unnamed: 0':'TCPID'}, inplace=True)
    df.to_csv(f, index=False)

def preprocess_dir(idir, odir, rglob_pattern, file_pattern='.*', rglob_exclude=None, fuzzy=False):
    start = datetime.now()
    c = re.compile(file_pattern)
    
    for fname in sorted(Path(idir).rglob(rglob_pattern)):
        if isinstance(rglob_exclude, str):
            if rglob_exclude.lower() in str(fname).lower():
                continue

        if c.fullmatch(str(fname)):
            model = get_file_model(fname, fuzzy=fuzzy)
            if model == None:
                print('Did not match file {}'.format(fname))
                continue

            opath = get_opath_from_ipath(fname, odir)
            rename = get_header_rename_dict(fname, model, fuzzy=fuzzy, manual={'redacted_VIN':'VIN'})

            if not opath.exists():
                opath.mkdir(parents=True, exist_ok=True)
            
            if len(rename) > 0:
                print(fname.parts[-1], model.__name__)
                print('rename: {}'.format(rename))
                copy_and_rename_headers(fname, opath / '{}.csv'.format(model.__name__), rename)
            else:
                
                copyfile(fname, opath / '{}.csv'.format(model.__name__))

def read_and_validate_dir(directory, rglob_pattern, Model, rglob_exclude=None, attach_path_attributes=True):
    data = []
    i = 0
    
    start = datetime.now()
    
    columns =  list(Model.model_fields.keys()) + list(Model.model_computed_fields.keys())
    if attach_path_attributes:
        columns = ['company','report_period','driver_type']+columns

    for fname in sorted(Path(directory).rglob(rglob_pattern)):
        if isinstance(rglob_exclude, str):
            if rglob_exclude.lower() in str(fname).lower():
                continue
        
        if attach_path_attributes:
            attr = get_attr_from_path(fname)
            
        with open(fname, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)        
            for row in reader:        
                is_empty = True
                for value in row.values():
                    if value.strip() != '':
                        is_empty = False
                if is_empty:
                    continue
                # validate
                trip = Model(**row).model_dump().values()
                row_out = list(trip)
                if attach_path_attributes:
                    row_out = [attr['company'],attr['report_period'],attr['driver_type']] + row_out
                data.append(row_out)

    return (pd.DataFrame(columns=columns, data=data))

if __name__=='__main__':
    parser = argparse.ArgumentParser(description="Process TOML configuration file for validation.")
    parser.add_argument("config_path", type=str, help="Path to the TOML configuration file.")
    
    # Check if the script is running in an interactive environment or not
    if len(sys.argv) > 1:
        # Running from command line, use the provided argument
        args = parser.parse_args()
        
        # Load the TOML configuration file
        with open(args.config_path, 'rb') as f:
            config = tomllib.load(f)['cpuc_deployment']
    else:
        print("Please supply a config file.")
        sys.exit()

    EXTRACTED = Path(config['root']) / config['extracted_subdir']
    INTERIM = Path(config['root']) / config['preprocessed_subdir']
    VALIDATED = Path(config['root']) / config['validated_subdir']

    preprocess_dir(
        idir=EXTRACTED, 
        odir=INTERIM,
        rglob_pattern='*.csv', 
        fuzzy=True,
        rglob_exclude='reference',
        )
    
    custom_preprocess(INTERIM) # includes hard-coded paths

    trip = read_and_validate_dir(
        directory=INTERIM, 
        rglob_pattern='Trip.csv',
        Model=Trip, 
        )
    trip.to_csv(VALIDATED / 'Trip.csv', index=False)

    trip_tract = read_and_validate_dir(
        directory=INTERIM, 
        rglob_pattern='TripTract.csv', 
        Model=TripTract, 
        )
    trip_tract.to_csv(VALIDATED / 'TripTract.csv', index=False)
    
    month = read_and_validate_dir(
        directory=INTERIM, 
        rglob_pattern='Month.csv', 
        Model=Month, 
        )
    month.to_csv(VALIDATED / 'Month.csv', index=False)
    
    incident_tract = read_and_validate_dir(
        directory=INTERIM, 
        rglob_pattern='Location.csv', 
        Model=IncidentTract, 
        )
    incident_tract.to_csv(VALIDATED / 'IncidentTract.csv', index=False)

    incident = read_and_validate_dir(
        directory=INTERIM, 
        rglob_pattern='Incident.csv', 
        Model=Incident,
        )
    incident.to_csv(VALIDATED / 'Incident.csv', index=False)

    incident_legacy = read_and_validate_dir(
        directory=INTERIM, 
        rglob_pattern='IncidentLegacy.csv', 
        Model=IncidentLegacy,
        )
    incident_legacy.to_csv(VALIDATED / 'IncidentLegacy.csv', index=False)

    charger = read_and_validate_dir(
        directory=INTERIM, 
        rglob_pattern='Charger.csv', 
        Model=Charger, 
        )
    charger.to_csv(VALIDATED / 'Charger.csv', index=False)

    charging_session = read_and_validate_dir(
        directory=INTERIM, 
        rglob_pattern='ChargingSession.csv', 
        Model=ChargingSession, 
        )
    charging_session.to_csv(VALIDATED / 'ChargingSession.csv', index=False)