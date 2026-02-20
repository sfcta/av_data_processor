'''
'''

from math import isnan
from typing import Any, Annotated, Optional, TypeVar
from datetime import time
from data_models.nhtsa.fields import *
from pydantic import BaseModel, Field, computed_field
from pydantic.functional_validators import BeforeValidator

MMM_YYYY = Field(pattern='(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-\d{4}')
MMM_TO_INT = {'JAN':1,
              'FEB':2,
              'MAR':3,
              'APR':4,
              'MAY':5,
              'JUN':6,
              'JUL':7,
              'AUG':8,
              'SEP':9,
              'OCT':10,
              'NOV':11,
              'DEC':12}

def coerce_nan_to_none(x: Any) -> Any:
    if isinstance(x, float) and isnan(x):
        return None
    return x

T = TypeVar('T')

NoneOrNan = Annotated[Optional[T], BeforeValidator(coerce_nan_to_none)]

class ads_crashes(BaseModel):
# vehicle
    vin: str #partial vin
    make: str
    model: str
    model_year: int = Field(gt=1900)
    same_vehicle_id: str
    operating_entity: str
    # not included in legacy reports
    # vin_decoded: str = Field(pattern='Y|N')
    
    # incident
    same_incident_id: str = Field(min_length=14, max_length=15)
    driver_operator_type: DriverOperatorType
    automation_system_engaged: str = Field(pattern='ADS')
    incident_date: str = MMM_YYYY
    incident_time: time | NoneOrNan
    city: str | NoneOrNan
    state: str | NoneOrNan = Field(min_length=2, max_length=4)
    roadway_type: str = RoadwayType
    highest_injury_severity_alleged: HighestInjurySeverityAlleged | HighestInjurySeverityAllegedLegacy
    crash_with: CrashWith
    # narrative: str

    # engagement_status: EngagementStatus New 

    @computed_field
    @property
    def highest_injury_severity_alleged_legacy(self) -> HighestInjurySeverityAllegedLegacy:
        return self.highest_injury_severity_alleged.to_legacy()
    
    @computed_field
    @property
    def month(self) -> int:
        return MMM_TO_INT[self.incident_date[:3]]
    
    @computed_field
    @property
    def year(self) -> int:
        return int(self.incident_date[-4:])
    
    @computed_field
    @property
    def ym(self) -> str:
        return '{:04d}-{:02d}'.format(self.year, self.month)

class ads_crash_reports(ads_crashes):
    '''
    Model for NHTSA SGO ADS Crashes.  TODO: handle differences in 2025 schema change
    '''
    # report
    report_id: str = Field(pattern='[0-9]+-[0-9]+')
    report_version: int = Field(gt=0)
    reporting_entity: str
    report_type: str
    #report_year: int = Field(gt=2015) # omitted b/c companies are leaving this blank
    report_submission_date: str = MMM_YYYY
    narrative: str