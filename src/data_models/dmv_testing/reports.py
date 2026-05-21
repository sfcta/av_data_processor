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
from utils.helpers import (get_dmv_attr_from_filepath, get_aliases, get_header, numeric_str_to_float, header_model_match_ratio, get_header_rename_dict, copy_and_rename_headers,
get_opath_from_ipath)

class VMTWide(BaseModel):
    __name__ = 'VMTWide'
    
    company: str = Field(alias='Manufacturer')
    permit: str = Field(alias='Permit Number')
    vin: str = Field(alias='VIN NUMBER') 
    annual_disengagements: int = Field(alias='Annual Total of Disengagements')
    december_n1_str: str = Field(alias='DEC_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    january_str: str = Field(alias='JAN_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    february_str: str = Field(alias='FEB_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    march_str: str = Field(alias='MAR_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    april_str: str = Field(alias='APR_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    may_str: str = Field(alias='MAY_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    june_str: str = Field(alias='JUN_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    july_str: str = Field(alias='JUL_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    august_str: str = Field(alias='AUG_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    september_str: str = Field(alias='SEP_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    october_str: str = Field(alias='OCT_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    november_str: str = Field(alias='NOV_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    annual_vmt_str: str = Field(alias='ANNUAL TOTAL', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')

    @computed_field
    @property
    def december_n1(self) -> float:
        return numeric_str_to_float(self.december_n1_str)

    @computed_field
    @property
    def january(self) -> float:
        return numeric_str_to_float(self.january_str)

    @computed_field
    @property
    def february(self) -> float:
        return numeric_str_to_float(self.february_str)

    @computed_field
    @property
    def march(self) -> float:
        return numeric_str_to_float(self.march_str)

    @computed_field
    @property
    def april(self) -> float:
        return numeric_str_to_float(self.april_str)

    @computed_field
    @property
    def may(self) -> float:
        return numeric_str_to_float(self.may_str)

    @computed_field
    @property
    def june(self) -> float:
        return numeric_str_to_float(self.june_str)

    @computed_field
    @property
    def july(self) -> float:
        return numeric_str_to_float(self.july_str)

    @computed_field
    @property
    def august(self) -> float:
        return numeric_str_to_float(self.august_str)

    @computed_field
    @property
    def september(self) -> float:
        return numeric_str_to_float(self.september_str)

    @computed_field
    @property
    def october(self) -> float:
        return numeric_str_to_float(self.october_str)

    @computed_field
    @property
    def november(self) -> float:
        return numeric_str_to_float(self.november_str)

    @computed_field
    @property
    def annual_vmt(self) -> float:
        return numeric_str_to_float(self.annual_vmt_str)


class VMTWideFirstTime(BaseModel):
    __name__ = 'VMTWideFirstTime'
    
    company: str = Field(alias='Manufacturer')
    permit: str = Field(alias='Permit Number')
    vin: str = Field(alias='VIN NUMBER') 
    annual_disengagements: int = Field(alias='Annual Total of Disengagements')
    january_n1_str: str = Field(alias='JAN_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    february_n1_str: str = Field(alias='FEB_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    march_n1_str: str = Field(alias='MAR_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    april_n1_str: str = Field(alias='APR_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    may_n1_str: str = Field(alias='MAY_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    june_n1_str: str = Field(alias='JUN_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    july_n1_str: str = Field(alias='JUL_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    august_n1_str: str = Field(alias='AUG_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    september_n1_str: str = Field(alias='SEP_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    october_n1_str: str = Field(alias='OCT_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    november_n1_str: str = Field(alias='NOV_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    december_n1_str: str = Field(alias='DEC_Y-1', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    january_str: str = Field(alias='JAN_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    february_str: str = Field(alias='FEB_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    march_str: str = Field(alias='MAR_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    april_str: str = Field(alias='APR_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    may_str: str = Field(alias='MAY_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    june_str: str = Field(alias='JUN_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    july_str: str = Field(alias='JUL_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    august_str: str = Field(alias='AUG_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    september_str: str = Field(alias='SEP_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    october_str: str = Field(alias='OCT_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    november_str: str = Field(alias='NOV_Y0', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')
    total_vmt_str: str = Field(alias='ANNUAL TOTAL', pattern=f'({numeric_re}|{redacted_re}|{na_re})?')

    @computed_field
    @property
    def january_n1(self) -> float:
        return numeric_str_to_float(self.january_n1_str)

    @computed_field
    @property
    def february_n1(self) -> float:
        return numeric_str_to_float(self.february_n1_str)

    @computed_field
    @property
    def march_n1(self) -> float:
        return numeric_str_to_float(self.march_n1_str)

    @computed_field
    @property
    def april_n1(self) -> float:
        return numeric_str_to_float(self.april_n1_str)

    @computed_field
    @property
    def may_n1(self) -> float:
        return numeric_str_to_float(self.may_n1_str)

    @computed_field
    @property
    def june_n1(self) -> float:
        return numeric_str_to_float(self.june_n1_str)

    @computed_field
    @property
    def july_n1(self) -> float:
        return numeric_str_to_float(self.july_n1_str)

    @computed_field
    @property
    def august_n1(self) -> float:
        return numeric_str_to_float(self.august_n1_str)

    @computed_field
    @property
    def september_n1(self) -> float:
        return numeric_str_to_float(self.september_n1_str)

    @computed_field
    @property
    def october_n1(self) -> float:
        return numeric_str_to_float(self.october_n1_str)

    @computed_field
    @property
    def november_n1(self) -> float:
        return numeric_str_to_float(self.november_n1_str)
    
    @computed_field
    @property
    def december_n1(self) -> float:
        return numeric_str_to_float(self.december_n1_str)

    @computed_field
    @property
    def january(self) -> float:
        return numeric_str_to_float(self.january_str)

    @computed_field
    @property
    def february(self) -> float:
        return numeric_str_to_float(self.february_str)

    @computed_field
    @property
    def march(self) -> float:
        return numeric_str_to_float(self.march_str)

    @computed_field
    @property
    def april(self) -> float:
        return numeric_str_to_float(self.april_str)

    @computed_field
    @property
    def may(self) -> float:
        return numeric_str_to_float(self.may_str)

    @computed_field
    @property
    def june(self) -> float:
        return numeric_str_to_float(self.june_str)

    @computed_field
    @property
    def july(self) -> float:
        return numeric_str_to_float(self.july_str)

    @computed_field
    @property
    def august(self) -> float:
        return numeric_str_to_float(self.august_str)

    @computed_field
    @property
    def september(self) -> float:
        return numeric_str_to_float(self.september_str)

    @computed_field
    @property
    def october(self) -> float:
        return numeric_str_to_float(self.october_str)

    @computed_field
    @property
    def november(self) -> float:
        return numeric_str_to_float(self.november_str)

    @computed_field
    @property
    def total_vmt(self) -> float:
        return numeric_str_to_float(self.total_vmt_str)
    
class VMT(BaseModel):
    __name__ = 'VMT'
    
    company: str 
    permit: str = Field(pattern=f'(AVT|AVDT){numeric_re}')
    vin: str
    year: int 
    month: int
    month_name: str = Field(pattern='[Jj][Aa][Nn][Uu][Aa][Rr][Yy]|[Ff][Ee][Bb][Rr][Uu][Aa][Rr][Yy]|[Mm][Aa][Rr][Cc][Hh]|[Aa][Pp][Rr][Ii][Ll]|[Mm][Aa][Yy]|[Jj][Uu][Nn][Ee]|[Jj][Uu][Ll][Yy]|[Aa][Uu][Gg][Uu][Ss][Tt]|[Ss][Ee][Pp][Tt][Ee][Mm][Bb][Ee][Rr]|[Oo][Cc][Tt][Oo][Bb][Ee][Rr]|[Nn][Oo][Vv][Ee][Mm][Bb][Ee][Rr]|[Dd][Ee][Cc][Ee][Mm][Bb][Ee][Rr]')
    vmt: float