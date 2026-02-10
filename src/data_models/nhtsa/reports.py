'''
'''

import sys, os
import numpy as np
import pandas as pd
from datetime import time
from data_models.nhtsa.fields import *
from pydantic import BaseModel, Field, computed_field
from enum import Enum

MMM_YYYY = Field(pattern='(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)-\d{4}')

class ads_crashes(BaseModel):
# vehicle
    vin: str #partial vin
    # vin_decoded: str = Field(pattern='Y|N')
    make: str
    model: str
    model_year: int = Field(gt=1900)
    same_vehicle_id: str
    operating_entity: str
    
    # incident
    same_incident_id: str = Field(min_length=14, max_length=15)
    driver_operator_type: DriverOperatorType
    automation_system_engaged: str = Field(pattern='ADS')
    # engagement_status: EngagementStatus
    incident_date: str = MMM_YYYY
    incident_time: time | None
    city: str
    state: str = Field(min_length=2, max_length=4)
    roadway_type: str = RoadwayType
    highest_injury_severity_alleged: HighestInjurySeverityAlleged | HighestInjurySeverityAllegedLegacy
    narrative: str

    @computed_field
    @property
    def highest_injury_severity_alleged_legacy(self) -> HighestInjurySeverityAllegedLegacy:
        return self.highest_injury_severity_alleged.to_legacy()

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
    