'''
'''

from math import nan, isnan
from typing import Any, Annotated, Optional, TypeVar
from datetime import datetime
from data_models.cpuc_deployment.fields import *
from pydantic import BaseModel, Field, computed_field
from pydantic.functional_validators import AfterValidator, BeforeValidator
from utils.helpers import lower_and_strip, primary_type_or_na_or_redacted, primary_type_or_redacted, coerce_nan_to_none, compare_if_numeric

class Trip(BaseModel):
    tcp_id: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}')
    ride_id: str = Field(alias='RideID', max_length=150)
    waybill_1: str = Field(alias='Waybill1', max_length=150) 
    waybill_2: Annotated[Optional[str], AfterValidator(lambda x: primary_type_or_na_or_redacted(x, str)), Field(alias='Waybill1', max_length=150)]
    waybill_3: Annotated[Optional[str], AfterValidator(lambda x: primary_type_or_na_or_redacted(x, str)), Field(alias='Waybill2', max_length=150)]
    waybill_4: Annotated[Optional[str], AfterValidator(lambda x: primary_type_or_na_or_redacted(x, str)), Field(alias='Waybill3', max_length=150)]
    waybill_5: Annotated[Optional[str], AfterValidator(lambda x: primary_type_or_na_or_redacted(x, str)), Field(alias='Waybill4', max_length=150)]
    waybill_6: Annotated[Optional[str], AfterValidator(lambda x: primary_type_or_na_or_redacted(x, str)), Field(alias='Waybill5', max_length=150)]
    waybill_7: Annotated[Optional[str], AfterValidator(lambda x: primary_type_or_na_or_redacted(x, str)), Field(alias='Waybill6', max_length=150)]
    start_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_redacted(x, datetime)), Field(alias='TripStartDate')]
    accept_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_redacted(x, datetime)), Field(alias='TripAcceptDate')]
    pickup_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_redacted(x, datetime)), Field(alias='TripPickupDate')]
    dropoff_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_redacted(x, datetime)), Field(alias='TripDropoffDate')]
    requester_tract: Annotated[int | str, AfterValidator(lambda x: primary_type_or_redacted(x, int)), AfterValidator(lambda x: compare_if_numeric(x, lt=100000000000)), Field(alias='TripReqRequesterTract')]
    pickup_tract: Annotated[int | str, AfterValidator(lambda x: primary_type_or_redacted(x, int)), AfterValidator(lambda x: compare_if_numeric(x, lt=100000000000)), Field(alias='PickupTract')]
    dropoff_tract: Annotated[int | str, AfterValidator(lambda x: primary_type_or_redacted(x, int)), AfterValidator(lambda x: compare_if_numeric(x, lt=100000000000)), Field(alias='DropoffTract')]
    requester_zip: Annotated[int| str, AfterValidator(lambda x: primary_type_or_redacted(x, int))] = Field(alias='TripReqRequesterZip')
    pickup_zip: Annotated[int| str, AfterValidator(lambda x: primary_type_or_redacted(x, int))] = Field(alias='PickupZip')
    dropoff_zip: Annotated[int| str, AfterValidator(lambda x: primary_type_or_redacted(x, int))] = Field(alias='DropoffZip')
    is_trip_fulfilled: str = Field(alias='TripFulfilled', pattern='Y|N|REDACTED|redacted|Redacted')
    unfulfilled_reason: Annotated[None | ReasonUnfulfilled, BeforeValidator(coerce_nan_to_none), Field(alias='ReasonUnfulfilled')]
    vin: Annotated[str, AfterValidator(lambda x: primary_type_or_redacted(x, str)), Field(alias='VIN')]
    fuel_type: str = Field(alias='VehicleFuelType', pattern='PHEV|BEV|FCEV|ICE|REDACTED|redacted|Redacted')
    is_wav: str = Field(alias='VehicleWav', pattern='Y|N|REDACTED|redacted|Redacted')
    passengers: int = Field(alias='NumberPassengers', ge=0)
    vmt_p1: Annotated[float | str, AfterValidator(lambda x: primary_type_or_redacted(x, str)), Field(alias='VMTP1')]
    vmt_p2: Annotated[float | str, AfterValidator(lambda x: primary_type_or_redacted(x, str)), Field(alias='VMTP2')]
    vmt_p3: Annotated[float | str, AfterValidator(lambda x: primary_type_or_redacted(x, str)), Field(alias='VMTP3')]
    evmt: Annotated[float | str, AfterValidator(lambda x: primary_type_or_redacted(x, str)), Field(alias='EVMT')]
    pmt: Annotated[float | str, AfterValidator(lambda x: primary_type_or_redacted(x, str)), Field(alias='PassengerMilesTraveled')]
    is_wav_request: str = Field(alias='WAVReq', pattern='Y|N|REDACTED|redacted|Redacted')
    is_pool_request: str = Field(alias='PoolRequest', pattern='Y|N|REDACTED|redacted|Redacted')
    is_pool_matched: str = Field(alias='SharedProvided', pattern='Y|N|REDACTED|redacted|Redacted')
    is_fared: str = Field(alias='FaredRide', pattern='Y|N|REDACTED|redacted|Redacted')
    vmt_pool_p2_p3: Annotated[float | str, AfterValidator(lambda x: primary_type_or_redacted(x, str)), Field(alias='RideIDMilesTraveledP23')]
    vmt_pool_p3: Annotated[float | str, AfterValidator(lambda x: primary_type_or_redacted(x, str)), Field(alias='RideIDMilesTraveledP3')]