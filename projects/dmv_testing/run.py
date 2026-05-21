import re, csv
from pathlib import Path
from shutil import copyfile
from typing import Any, Annotated, Optional, TypeVar, Union, Literal
from datetime import datetime
from data_models.nhtsa.fields import *
from pydantic import BaseModel, Field, computed_field
from pydantic.functional_validators import AfterValidator, BeforeValidator

from math import nan, isnan
import pandas as pd
from fuzzywuzzy import fuzz

#from data_models.dmv_testing.reports import *

from utils.regex import numeric_re, redacted_re, na_re, missing_field_re, not_provided_re
from utils.helpers import (get_dmv_attr_from_filepath, get_aliases, get_header, numeric_str_to_float, header_model_match_ratio, 
                           get_header_rename_dict, copy_and_rename_headers, get_file_model)

from data_models.dmv_testing.reports import VMTWide, VMTWideFirstTime, VMT

def standardize_dmv_vmt(df_or_fname, permit_to_name=None, rename=None):
    if isinstance(df_or_fname, pd.DataFrame):
        df = df_or_fname
    else:
        df = pd.read_csv(df_or_fname)

    df = df.dropna(how='all')
    if isinstance(rename, dict):
        df = df.rename(columns=rename)
        
    df['Permit Number'] = df['Permit Number'].map(lambda x: x.strip())
    df['Permit Number'] = df['Permit Number'].map(lambda x: x.replace('ATV','AVT').replace('AVTD','AVDT'))

    if isinstance(permit_to_name, dict):
        df['Manufacturer'] = df['Permit Number'].map(lambda x: permit_to_name[x])
    return df

def get_dmv_vmt_header_rename_dict(ifile, Model, encoding=None, drop_unnamed=True, drop_unaliased=False):
    header = get_header(ifile, encoding=encoding, drop_unnamed=drop_unnamed)
    aliases = get_aliases(Model, drop_unaliased=drop_unaliased)
    if not len(header) == len(aliases):
        raise Exception("header ({}) does not match aliases ({})\nheader: {}\naliases: {}".format(len(header), len(aliases), header, aliases))

    return dict(zip(header, aliases))

def custom_preprocess():
    fname = r'Q:\Data\Regulatory\AV\DMV\Disengagement Reports\0_extracted\2025\2025 Autonomous Mileage Reports (CSV).csv'
    rename = get_dmv_vmt_header_rename_dict(fname, VMTWide)
    df = standardize_dmv_vmt(fname)
    df.to_csv(r'Q:\Data\Regulatory\AV\DMV\Disengagement Reports\1_preprocessed\2025\2025 Autonomous Mileage Reports (CSV).csv', index=False)

def preprocess_dmv_dir(idir, odir, rglob_pattern, file_pattern='.*', candidate_models=None, rglob_exclude=None, fuzzy=False, permit_to_name=None):
    start = datetime.now()
    c = re.compile(file_pattern)

    custom_preprocess()
    
    for fname in sorted(Path(idir).rglob(rglob_pattern)):
        if isinstance(rglob_exclude, str):
            if rglob_exclude.lower() in str(fname).lower():
                continue

        if c.fullmatch(str(fname)):
            model = get_file_model(fname, candidate_models=candidate_models, fuzzy=fuzzy)
            if model == None:
                print('Did not match file {}'.format(fname))
                continue

            opath = Path(odir) / fname.parts[-2]
            
            rename = get_dmv_vmt_header_rename_dict(fname, model)

            if not opath.exists():
                opath.mkdir(parents=True, exist_ok=True)

            df = standardize_dmv_vmt(
                fname, 
                permit_to_name=permit_to_name,
                rename=rename
                )

            df.to_csv(opath / fname.parts[-1], index=False)

def validate_dmv_dir(idir, odir, rglob_pattern, file_pattern='.*', candidate_models=None, rglob_exclude=None, fuzzy=False, attach_path_attributes=True):
    start = datetime.now()
    i = 0
    c = re.compile(file_pattern)

    for fname in sorted(Path(idir).rglob(rglob_pattern)):
        data = []
        
        if isinstance(rglob_exclude, str):
            if rglob_exclude.lower() in str(fname).lower():
                continue

        if c.fullmatch(str(fname)):
            model = get_file_model(fname, candidate_models=candidate_models, fuzzy=fuzzy)
            if model == None:
                print('Did not match file {}'.format(fname))
                continue
            else:
                print('Matched type {}: {}'.format(model.__name__, fname.parts[-1]))

            columns =  list(model.model_fields.keys()) + list(model.model_computed_fields.keys())
            
            if attach_path_attributes:
                columns = ['year','report_type','first_time'] + columns
                attr = get_dmv_attr_from_filepath(fname)
                
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
                    #trip = Model(**row).model_dump().values()
                    
                    try:
                        valid = model(**row).model_dump().values()
                    except Exception as e:
                        print('NOT A VALID {}: {}'.format(model.__name__, fname))
                        print(e)
                        valid = None
    
                    if valid == None:
                        break
                        
                    row_out = list(valid)
                    if attach_path_attributes:
                        row_out = [attr['year'],attr['report_type'],attr['first_time']] + row_out
                    data.append(row_out)
            
            if valid == None:
                continue
    
            opath = Path(odir) / attr['year']
                
            if not opath.exists():
                opath.mkdir(parents=True, exist_ok=True)
                
            df = pd.DataFrame(columns=columns, data=data)
            df.to_csv(opath /  '{}_{}_{}.csv'.format(model.__name__, attr['report_type'], attr['driver_type']), index=False)

def read_and_rename_dmv_vmt(fname, model, fuzzy=False):
    rename = {}
    for key, field in model.model_fields.items():
        if field.alias == None:
            continue
        rename[field.alias] = key

    df = pd.read_csv(fname)
    df = df.rename(columns=rename)
    return df

def vmt_wide_to_long(df, model, year):
    val_cols = []
    id_cols = ['company', 'permit', 'vin']
    drop_cols = ['annual_disengagements', 'annual_vmt_str', 'total_vmt_str']
    
    for c in list(model.model_fields.keys()):
        if c in id_cols:
            continue
        if c in drop_cols:
            continue
    
        val_cols.append(c)

    melted = df.melt(
        id_vars=id_cols,
        value_vars=val_cols,
        var_name='month_name',
        value_name='vmt'
    )

    melted['vmt'] = melted['vmt'].map(lambda x: numeric_str_to_float(x)).fillna(0)
    melted.insert(4, 'year', int(year))
    melted.loc[melted['month_name'].map(lambda x: '_n1' in x),'year'] = int(year) - 1
    melted['month_name'] = melted['month_name'].map(lambda x: x.split('_')[0])
    melted['month'] = melted['month_name'].map(lambda x: {'january':1,
                                                      'february':2,
                                                      'march':3,
                                                      'april':4,
                                                      'may':5,
                                                      'june':6,
                                                      'july':7,
                                                      'august':8,
                                                      'september':9,
                                                      'october':10,
                                                      'november':11,
                                                      'december':12}[x.lower()])
    
    return melted

def process_dmv_vmt_wide_to_long(idir, odir, rglob_pattern, file_pattern='.*', candidate_models=None, fuzzy=False, rglob_exclude=None):
    start = datetime.now()
    i = 0
    c = re.compile(file_pattern)

    for fname in sorted(Path(idir).rglob(rglob_pattern)):
        data = []
        
        if isinstance(rglob_exclude, str):
            if rglob_exclude.lower() in str(fname).lower():
                continue

        if c.fullmatch(str(fname)):
            model = get_file_model(fname, candidate_models=candidate_models, fuzzy=fuzzy)
            if model == None:
                print('Did not match file {}'.format(fname))
                continue
            else:
                print('Matched type {}: {}'.format(model.__name__, fname.parts[-1]))

        df = read_and_rename_dmv_vmt(fname, model)
        attr = get_dmv_attr_from_filepath(fname)
        long = vmt_wide_to_long(df, model, int(attr['year']))

        opath = Path(odir) / attr['year']
                
        if not opath.exists():
            opath.mkdir(parents=True, exist_ok=True)
        
        long.to_csv(opath /  'vmt_{}{}.csv'.format(attr['driver_type'],attr['first_time']), index=False)

def read_and_validate(fname, model):
    columns =  list(model.model_fields.keys()) + list(model.model_computed_fields.keys())
    data = []
    
    with open(fname, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)        
        for row in reader:        
            is_empty = True
            for value in row.values():
                if value.strip() != '':
                    is_empty = False
            if is_empty:
                continue
            
            try:
                valid = model(**row).model_dump().values()
            except Exception as e:
                print('NOT A VALID {}: {}'.format(model.__name__, fname))
                print(e)
                valid = None
    
            if valid == None:
                break
                
            row_out = list(valid)

            data.append(row_out)
    df = pd.DataFrame(columns=columns, data=data)
    return df

def validate_and_combine(idir, odir, rglob_pattern, file_pattern='.*', model=VMT, fuzzy=False, rglob_exclude=None):
    start = datetime.now()
    i = 0
    c = re.compile(file_pattern)

    dfs = []
    
    for fname in sorted(Path(idir).rglob(rglob_pattern)):    
        if isinstance(rglob_exclude, str):
            if rglob_exclude.lower() in str(fname).lower():
                continue

        if c.fullmatch(str(fname)):
            model = get_file_model(
                fname, 
                candidate_models=[model], 
                drop_unaliased=False,
                fuzzy=fuzzy
            )
            if model == None:
                print('Did not match file {}'.format(fname))
                continue
            else:
                print('Matched type {}: {}'.format(model.__name__, fname.parts[-1]))

        df = read_and_validate(fname, model)
        dfs.append(df)

    return pd.concat(dfs)

if __name__=='__main__':
    EXTRACTED = r'Q:\Data\Regulatory\AV\DMV\Disengagement Reports\0_extracted'
    PREPROCESSED = r'Q:\Data\Regulatory\AV\DMV\Disengagement Reports\1_preprocessed'
    VALIDATED = r'Q:\Data\Regulatory\AV\DMV\Disengagement Reports\2_validated'
    MELTED = r'Q:\Data\Regulatory\AV\DMV\Disengagement Reports\3_melted'
    COMBINED = r'Q:\Data\Regulatory\AV\DMV\Disengagement Reports\4_combined_and_validated'
    PERMIT_LOOKUP = r'Q:\Data\Regulatory\AV\DMV\Permit Numbers.xlsx'
    permit_lookup = pd.read_excel(PERMIT_LOOKUP)
    permit_to_name = permit_lookup.set_index('Permit Number').to_dict()['Simple Name']

    preprocess_dmv_dir(
        idir=EXTRACTED, 
        odir=PREPROCESSED,
        rglob_pattern='*.csv', 
        candidate_models=[VMTWide,VMTWideFirstTime],
        fuzzy=True,
        permit_to_name=permit_to_name
    )

    validate_dmv_dir(
        idir=PREPROCESSED, 
        odir=VALIDATED,
        rglob_pattern='*.csv', 
        candidate_models=[VMTWide,VMTWideFirstTime],
    )

    process_dmv_vmt_wide_to_long(
        idir=PREPROCESSED,
        odir=MELTED,
        rglob_pattern='*.csv',
        candidate_models=[VMTWide, VMTWideFirstTime]
    )

    df = validate_and_combine(
        idir=MELTED,
        odir=COMBINED,
        rglob_pattern='*.csv',
        model=VMT
    )

    df.to_csv(Path(COMBINED) / 'dmv_vmt.csv', index=False)