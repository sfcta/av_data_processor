'''
'''

from math import nan, isnan
from typing import Any, Annotated, Optional, TypeVar
from datetime import datetime
from data_models.cpuc_deployment.fields import *
from pydantic import BaseModel, Field, computed_field
from pydantic.functional_validators import AfterValidator, BeforeValidator
from utils.helpers import primary_type_or_na_or_redacted, primary_type_or_redacted, coerce_nan_to_none, compare_if_numeric, coerce_nan_to, coerce_str_to_number, numeric_str_to_float

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

class Month(BaseModel):
    tcp_id: Optional[str] = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}', default=None)
    year: int = Field(alias='Year', ge=2020)
    month: int = Field(alias='Month', ge=1, le=12)
    trips_str: str = Field(alias='TotalTrips', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    hours_p1_str: str = Field(alias='TotalWaiting', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_p1_str: str = Field(alias='TotalVMTPeriod1', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_p2_str: str = Field(alias='TotalVMTPeriod2', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_p3_str: str = Field(alias='TotalVMTPeriod3', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_zev_str: Field(alias='TotalVMTZEV', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    pax_str: str = Field(alias='TotalPassengersCarried', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    pmt_str: str = Field(alias='TotalPMT', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    wav_vehs_in_service_str: Optional[str] = Field(alias='TotalWAVsAvail', pattern=f'{numeric_re}|{redacted_re}|{na_re}', default='0')
    wav_requests_str: Optional[str] = Field(alias='TotalWAVsRequested', pattern=f'{numeric_re}|{redacted_re}|{na_re}', default='0')
    wav_unfulfilled_unavailable_str: Optional[str] = Field(alias='TotalWAVsDeclinedUnavail', pattern=f'{numeric_re}|{redacted_re}|{na_re}', default='0')
    wav_trips_str: Optional[str] = Field(alias='TotalWAVsFulfilled', pattern=f'{numeric_re}|{redacted_re}|{na_re}', default='0')

    @computed_field
    @property
    def trips(self) -> float:
        return numeric_str_to_float(self.trips_str)

    @computed_field
    @property
    def hours_p1(self) -> float:
        return numeric_str_to_float(self.hours_p1_str)

    @computed_field
    @property
    def vmt_p1(self) -> float:
        return numeric_str_to_float(self.vmt_p1_str)

    @computed_field
    @property
    def vmt_p2(self) -> float:
        return numeric_str_to_float(self.vmt_p2_str)

    @computed_field
    @property
    def vmt_p3(self) -> float:
        return numeric_str_to_float(self.vmt_p3_str)

    @computed_field
    @property
    def pax(self) -> float:
        return numeric_str_to_float(self.pax_str)

    @computed_field
    @property
    def pmt(self) -> float:
        return numeric_str_to_float(self.pmt_str)

    @computed_field
    @property
    def wav_vehs_in_service(self) -> float:
        return numeric_str_to_float(self.wav_vehs_in_service_str)

    @computed_field
    @property
    def wav_requests(self) -> float:
        return numeric_str_to_float(self.wav_requests_str)

    @computed_field
    @property
    def wav_unfulfilled_unavailable(self) -> float:
        return numeric_str_to_float(self.wav_unfulfilled_unavailable_str)

    @computed_field
    @property
    def wav_trips(self) -> float:
        return numeric_str_to_float(self.wav_trips_str)
    
    @computed_field
    @property
    def vmt(self) -> float:
        return self.vmt_p1 + self.vmt_p2 + self.vmt_p3
        
    @computed_field
    @property
    def deadhead_rate(self) -> float:
        if self.vmt > 0:
            return self.vmt_p3 / (self.vmt)    
        else:
            return nan

    @computed_field
    @property
    def pmt_over_vmt(self) -> float:
        if self.vmt > 0:
            return self.pmt / self.vmt
        else:
            return nan

class Tract(BaseModel):
    tcp_id: Optional[str] = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}', default=None)
    year: int = Field(alias='Year', ge=2020)
    month: int = Field(alias='Month', ge=1, le=12)
    tract: str = Field(alias='Tract', pattern=r'\d{10,12}|([Rr][Ee][Dd][Aa][Cc][Tt][Ee][Dd])|([Nn]/{0,1}[Aa])')
    trips_start_str: str = Field(alias='TripsStart', pattern=numeric_re+r'|([Rr][Ee][Dd][Aa][Cc][Tt][Ee][Dd])|([Nn]/{0,1}[Aa])')
    trips_end_str: str = Field(alias='TripsEnd', pattern=numeric_re+r'|([Rr][Ee][Dd][Aa][Cc][Tt][Ee][Dd])|([Nn]/{0,1}[Aa])')

    @computed_field
    @property
    def trips_start(self) -> float:
        return numeric_str_to_float(self.trips_start_str)

    @computed_field
    @property
    def trips_end(self) -> float:
        return numeric_str_to_float(self.trips_end_str)