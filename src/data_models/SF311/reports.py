from math import nan, isnan
from typing import Any, Annotated, Optional, TypeVar
from datetime import datetime
from data_models.SF311.fields import *
from pydantic import BaseModel, Field, computed_field
from pydantic.functional_validators import AfterValidator, BeforeValidator
from utils.helpers import primary_type_or_na_or_redacted, primary_type_or_redacted, coerce_nan_to_none, compare_if_numeric, coerce_nan_to, coerce_str_to_number, numeric_str_to_float
from utils.regex import numeric_re, redacted_re, na_re, missing_field_re, not_provided_re

class Cases(BaseModel):
    case_id: int = Field(alias='CaseID') # str = Field(alias='CaseID', pattern='\d+')
    opened: datetime = Field(alias='Opened')
    closed: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='Closed')]
    updated: datetime = Field(alias='Updated')
    status: Status = Field(alias='Status')
    status_note: str = Field(alias='Status Notes')