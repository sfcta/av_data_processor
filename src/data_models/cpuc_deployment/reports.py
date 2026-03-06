'''
'''

from math import nan, isnan
from typing import Any, Annotated, Optional, TypeVar
from datetime import datetime
from data_models.cpuc_deployment.fields import *
from pydantic import BaseModel, Field, computed_field
from pydantic.functional_validators import AfterValidator, BeforeValidator
from utils.helpers import primary_type_or_na_or_redacted, primary_type_or_redacted, coerce_nan_to_none, compare_if_numeric, coerce_nan_to, coerce_str_to_number, numeric_str_to_float
from utils.regex import numeric_re, redacted_re, na_re, missing_field_re, not_provided_re

class Trip(BaseModel):
    __name__ = 'Charger'
    
    tcp_id: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}'+f'|{missing_field_re}')
    ride_id: str = Field(alias='RideID', max_length=150)
    waybill_1: str = Field(alias='Waybill1', max_length=150) 
    waybill_2: Optional[str] = Field(alias='Waybill2', max_length=150, default='')
    waybill_3: Optional[str] = Field(alias='Waybill3', max_length=150, default='')
    waybill_4: Optional[str] = Field(alias='Waybill4', max_length=150, default='')
    waybill_5: Optional[str] = Field(alias='Waybill5', max_length=150, default='')
    waybill_6: Optional[str] = Field(alias='Waybill6', max_length=150, default='')
    waybill_7: Optional[str] = Field(alias='Waybill7', max_length=150, default='')
    start_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='TripStartDate')]
    accept_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='TripAcceptDate')]
    pickup_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='TripPickupDate')]
    dropoff_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='TripDropoffDate')]
    requester_tract: str = Field(alias='TripReqRequesterTract', pattern=r'\d{11,12}|'+f'{redacted_re}|{na_re}')
    pickup_tract: str = Field(alias='PickupTract', pattern=r'\d{11,12}|'+f'{redacted_re}|{na_re}')
    dropoff_tract: str = Field(alias='DropoffTract', pattern=r'\d{11,12}|'+f'{redacted_re}|{na_re}')
    requester_zip: str = Field(alias='TripReqRequesterZip', pattern=r'\d{5}|'+f'{redacted_re}|{na_re}')
    pickup_zip: str = Field(alias='PickupZip', pattern=r'\d{5}|'+f'{redacted_re}|{na_re}')
    dropoff_zip: str = Field(alias='DropoffZip', pattern=r'\d{5}|'+f'{redacted_re}|{na_re}')
    is_trip_fulfilled: str = Field(alias='TripFulfilled', pattern=f'Y|N|{redacted_re}')
    unfulfilled_reason: str = Field(alias='ReasonUnfulfilled')
    vin: str = Field(alias='VIN') 
    fuel_type: str = Field(alias='VehicleFuelType', pattern=f'PHEV|BEV|FCEV|ICE|{redacted_re}|{na_re}')
    is_wav: str = Field(alias='VehicleWav', pattern=f'Y|N|{redacted_re}')
    passengers_str: str = Field(alias='NumberPassengers', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_p1_str: str = Field(alias='VMTP1', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_p2_str: str = Field(alias='VMTP2', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_p3_str: str = Field(alias='VMTP3', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    evmt_str: str = Field(alias='EVMT', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    pmt_str: str = Field(alias='PassengerMilesTraveled', pattern=f'[{numeric_re}|{redacted_re}|{na_re}]?')
    is_wav_request: str = Field(alias='WAVReq', pattern=f'Y|N|{redacted_re}')
    is_pool_request: str = Field(alias='PoolRequest', pattern=f'Y|N|{redacted_re}')
    is_pool_matched: str = Field(alias='SharedProvided', pattern=f'Y|N|{redacted_re}')
    is_fared: str = Field(alias='FaredRide', pattern=f'[Y|N]?|{redacted_re}')
    vmt_pool_p2_p3_str: str = Field(alias='RideIDMilesTraveledP23', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_pool_p3_str: str = Field(alias='RideIDMilesTraveledP3', pattern=f'{numeric_re}|{redacted_re}|{na_re}')

    @computed_field
    @property
    def passengers(self) -> float:
        return numeric_str_to_float(self.passengers_str)

class Month(BaseModel):
    __name__ = 'Month'
    
    tcp_id: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}'+f'|{missing_field_re}')
    year: int = Field(alias='Year', ge=2020)
    month: str = Field(alias='Month', pattern=f'0?[0-9]|10|11|12|{redacted_re}|{na_re}')
    trips_str: str = Field(alias='TotalTrips', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    hours_p1_str: str = Field(alias='TotalWaiting', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_p1_str: str = Field(alias='TotalVMTPeriod1', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_p2_str: str = Field(alias='TotalVMTPeriod2', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_p3_str: str = Field(alias='TotalVMTPeriod3', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    vmt_zev_str: str = Field(alias='TotalVMTZEV', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    pax_str: str = Field(alias='TotalPassengersCarried', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    pmt_str: str = Field(alias='TotalPMT', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    wav_vehs_in_service_str: str = Field(alias='TotalWAVsAvail', pattern=f'{numeric_re}|{redacted_re}|{na_re}|{missing_field_re}')
    wav_requests_str: str = Field(alias='TotalWAVsRequested', pattern=f'{numeric_re}|{redacted_re}|{na_re}|{missing_field_re}')
    wav_unfulfilled_unavailable_str: str = Field(alias='TotalWAVsDeclinedUnavail', pattern=f'{numeric_re}|{redacted_re}|{na_re}|{missing_field_re}')
    wav_trips_str: str = Field(alias='TotalWAVsFulfilled', pattern=f'{numeric_re}|{redacted_re}|{na_re}|{missing_field_re}')

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

class TripTract(BaseModel):
    __name__ = 'TripTract'
    
    tcp_id: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}'+f'|{missing_field_re}')
    year: int = Field(alias='Year', ge=2020)
    month_str: str = Field(alias='Month', pattern=f'0?[0-9]|10|11|12|{redacted_re}|{na_re}')
    tract: str = Field(alias='Tract', pattern=r'\d{10,12}'+f'|{redacted_re}|{na_re}')
    trips_start_str: str = Field(alias='TripsStart', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    trips_end_str: str = Field(alias='TripsEnd', pattern=f'{numeric_re}|{redacted_re}|{na_re}')

    @computed_field
    @property
    def month(self) -> float:
        return numeric_str_to_float(self.month_str)  
        
    @computed_field
    @property
    def trips_start(self) -> float:
        return numeric_str_to_float(self.trips_start_str)

    @computed_field
    @property
    def trips_end(self) -> float:
        return numeric_str_to_float(self.trips_end_str)    
    
class IncidentTract(BaseModel):
    __name__ = 'IncidentTract'
    
    tcp_id: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}'+f'|{missing_field_re}')
    # Individual companies use different year-quarter combinations to describe the same time.  For example, Cruise says reporting period 9/1/2022 - 11/30/2022 is year 2022 quarter 4, while
    # Waymo says it is year 2023 quarter 1.  Additionally, CPUC changed its reporting periods starting 1/1/2025, and Waymo (only company currently reporting) also changes their method for 
    # labeling quarters, resulting in the following: 
    #  9/1/2024 - 11/30/2024, year 2025 quarter 1
    # 12/1/2024 - 12/31/2024, year 2025 quarter <blank>
    #  1/1/2025 -  3/31/2025, year 2025 quarter 1
    year_str: str = Field(alias='Year')
    quarter_str: str = Field(alias='Quarter')
    tract: str = Field(alias='Tract', pattern=r'\d{10,12}|([Rr][Ee][Dd][Aa][Cc][Tt][Ee][Dd])|([Nn]/{0,1}[Aa])')
    collisions_str: str = Field(alias='CollisionsAll', pattern=f'{numeric_re}?|{redacted_re}|{na_re}')
    collisions_pudo_str: str = Field(alias='CollisionsPUDO', pattern=f'{numeric_re}?|{redacted_re}|{na_re}')
    pudo_travel_lane_str: str = Field(alias='PUDOTravelLane', pattern=f'{numeric_re}?|{redacted_re}|{na_re}|Not provided')

    @computed_field
    @property
    def collisions(self) -> float:
        return numeric_str_to_float(self.collisions_str)

    @computed_field
    @property
    def collisions_pudo(self) -> float:
        return numeric_str_to_float(self.collisions_pudo_str)

    @computed_field
    @property
    def pudo_travel_lane(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_str)
    
class Incident(BaseModel):
    __name__ = 'Incident'
    
    tcpid: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}'+f'|{redacted_re}|{missing_field_re}')
    timestamp: Annotated[Optional[datetime] | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='TimeofIncident')]
    lat_str: str = Field(alias='IncLat', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    lon_str: str = Field(alias='IncLong', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    tract_str: str = Field(alias='IncidenceTract', pattern=r'\d{10,12}'+f'|{redacted_re}|{na_re}')
    zip_str: str = Field(alias='IncidenceZip', pattern=r'\d{5}'+f'|{redacted_re}|{na_re}')
    vin: str = Field(alias='VIN')
    collision_occ: str = Field(alias='CollisionOccupant', pattern=f'Y|N|{redacted_re}')
    collision_ped: str = Field(alias='CollisionPedestrian', pattern=f'Y|N|{redacted_re}')
    collision_bike: str = Field(alias='CollisionBicycleScooter', pattern=f'Y|N|{redacted_re}')
    collision_mc: str = Field(alias='CollisionMotorcycles', pattern=f'Y|N|{redacted_re}')
    collision_other: str = Field(alias='CollisionOtherVehicle', pattern=f'Y|N|{redacted_re}')
    collision_rail: str = Field(alias='CollisionRail', pattern=f'Y|N|{redacted_re}')
    collision_property: str = Field(alias='CollisionProperty', pattern=f'Y|N|{redacted_re}')
    collision_pdo: str = Field(alias='CollisionSeverityPropertyDamage', pattern=f'Y|N|{redacted_re}')
    collision_injury_possible: str = Field(alias='CollisionSeverityInjuryPossible', pattern=f'Y|N|{redacted_re}')
    collision_injury_minor: str = Field(alias='CollisionSeverityInjuryMinor', pattern=f'Y|N|{redacted_re}')
    collision_injury_severe: str = Field(alias='CollisionSeverityInjurySevere', pattern=f'Y|N|{redacted_re}')
    collision_fatality: str = Field(alias='CollisionSeverityFatality', pattern=f'Y|N|{redacted_re}')
    collision_pudo_passenger: str = Field(alias='CollisionPUDOPassenger', pattern=f'Y|N|{redacted_re}')
    collision_pudo_ped: str = Field(alias='CollisionPUDOPedestrian', pattern=f'Y|N|{redacted_re}')
    collision_pudo_bike: str = Field(alias='CollisionPUDOBicycleScooter', pattern=f'Y|N|{redacted_re}')
    collision_pudo_mc: str = Field(alias='CollisionPUDOMotorcycles', pattern=f'Y|N|{redacted_re}')
    collision_pudo_other: str = Field(alias='CollisionPUDOOtherVehicle', pattern=f'Y|N|{redacted_re}')
    collision_pudo_rail: str = Field(alias='CollisionPUDORail', pattern=f'Y|N|{redacted_re}')
    collision_pudo_property: str = Field(alias='CollisionPUDOProperty', pattern=f'Y|N|{redacted_re}')
    nhtsa_sgo_ids: str = Field(alias='CollisionReport', pattern=r'(\d+-\d+)?'+f'|NULL|{redacted_re}|{na_re}')
    citation: str = Field(alias='Citation', pattern=f'Y|N|{redacted_re}')
    # note: unclear if this is only reported if it's associated with a trip.  Maybe doesn't matter since it's optional
    violation: str = Field(alias='CitViolation')
    citation_issuer: str = Field(alias='CitIssuer')
    assault_sexual: str = Field(alias='AssaultSexual', pattern=f'Y|N|{redacted_re}')
    assault_nonsexual: str = Field(alias='AssaultNonsexual', pattern=f'Y|N|{redacted_re}')
    assault_passenger_against_passenger: str = Field(alias='AssaultClaimantPassengerPassenger', pattern=f'Y|N|{redacted_re}')
    assault_passenger_against_driver: str = Field(alias='AssaultClaimaintPassengerDriver', pattern=f'Y|N|{redacted_re}')
    assault_driver_against_passenger: str = Field(alias='AssaultClaimaintDriverPassenger', pattern=f'Y|N|{redacted_re}')
    harass_sexual: str = Field(alias='HarassmentSexual', pattern=f'Y|N|{redacted_re}')
    harass_nonsexual: str = Field(alias='HarassmentNonsexual', pattern=f'Y|N|{redacted_re}')
    harass_passenger_against_passenger: str = Field(alias='HarassmentClaimantPassengerPassenger', pattern=f'Y|N|{redacted_re}')
    harass_passenger_against_driver: str = Field(alias='HarassmentClaimantPassengerDriver', pattern=f'Y|N|{redacted_re}')
    harass_driver_against_passenger: str = Field(alias='HarassmentClaimantDriverPassenger', pattern=f'Y|N|{redacted_re}')
    pudo_travel_lane: str = Field(alias='PUDOTravelLane', pattern=f'Y|N|{redacted_re}')
    complaint_safety: str = Field(alias='ComplaintSafety', pattern=f'Y|N|{redacted_re}')
    complaint_pudo: str = Field(alias='ComplaintPUDO', pattern=f'Y|N|{redacted_re}')
    complaint_access: str = Field(alias='ComplaintAccessibility', pattern=f'Y|N|{redacted_re}')
    complaint_wav: str = Field(alias='ComplaintWAV', pattern=f'Y|N|{redacted_re}')
    complaint_customer_service: str = Field(alias='ComplaintCustomerService', pattern=f'Y|N|{redacted_re}')
    complaint_other: str = Field(alias='ComplaintOther', pattern=f'Y|N|{redacted_re}')
    payout_str: str = Field(alias='PayoutTotal', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    citation_pudo: str = Field(alias='CitationPD', pattern=f'Y|N|{redacted_re}')
    citation_pudo_issuer: Optional[str] = Field(alias='CitIssuerPD', default='')

class IncidentLegacy(BaseModel):
    __name__ = 'IncidentLegacy'

    tcpid: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}'+f'|{redacted_re}|{missing_field_re}')
    year_str: str = Field(alias='Year')
    quarter_str: str = Field(alias='Quarter')
    collision_total_str: str = Field(alias='CollisionsAll', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_occ_str: str = Field(alias='CollisionsOccupant', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_ped_str: str = Field(alias='CollisionsPedestrian', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_bike_str: str = Field(alias='CollisionsBicycleScooter', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_mc_str: str = Field(alias='CollisionsMotorcycles', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_other_str: str = Field(alias='CollisionsOtherVehicle', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_rail_str: str = Field(alias='CollisionsRail', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_property_str: str = Field(alias='CollisionsProperty', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_pdo_str: str = Field(alias='CollisionSeverityPropertyDamage', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_injury_possible_str: str = Field(alias='CollisionSeverityInjuryPossible', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_injury_minor_str: str = Field(alias='CollisionSeverityInjuryMinor', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_injury_severe_str: str = Field(alias='CollisionSeverityInjurySevere', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_fatality_str: str = Field(alias='CollisionSeverityFatality', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h00_str: str = Field(alias='CollisionTime00', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h01_str: str = Field(alias='CollisionTime01', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h02_str: str = Field(alias='CollisionTime02', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h03_str: str = Field(alias='CollisionTime03', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h04_str: str = Field(alias='CollisionTime04', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h05_str: str = Field(alias='CollisionTime05', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h06_str: str = Field(alias='CollisionTime06', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h07_str: str = Field(alias='CollisionTime07', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h08_str: str = Field(alias='CollisionTime08', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h09_str: str = Field(alias='CollisionTime09', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h10_str: str = Field(alias='CollisionTime10', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h11_str: str = Field(alias='CollisionTime11', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h12_str: str = Field(alias='CollisionTime12', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h13_str: str = Field(alias='CollisionTime13', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h14_str: str = Field(alias='CollisionTime14', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h15_str: str = Field(alias='CollisionTime15', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h16_str: str = Field(alias='CollisionTime16', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h17_str: str = Field(alias='CollisionTime17', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h18_str: str = Field(alias='CollisionTime18', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h19_str: str = Field(alias='CollisionTime19', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h20_str: str = Field(alias='CollisionTime20', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h21_str: str = Field(alias='CollisionTime21', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h22_str: str = Field(alias='CollisionTime22', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_h23_str: str = Field(alias='CollisionTime23', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_pudo_total_str: str = Field(alias='CollisionsPUDOAll', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_pudo_passenger_str: str = Field(alias='CollisionsPUDOPassenger', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_pudo_ped_str: str = Field(alias='CollisionsPUDOPedestrian', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_pudo_bike_str: str = Field(alias='CollisionsPUDOBicycleScooter', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_pudo_mc_str: str = Field(alias='CollisionsPUDOMotorcycles', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_pudo_other_str: str = Field(alias='CollisionsPUDOOtherVehicle', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_pudo_rail_str: str = Field(alias='CollisionsPUDORail', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collision_pudo_property_str: str = Field(alias='CollisionsPUDOProperty', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h00_str: str = Field(alias='CollisionPUDOTime00', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h01_str: str = Field(alias='CollisionPUDOTime01', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h02_str: str = Field(alias='CollisionPUDOTime02', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h03_str: str = Field(alias='CollisionPUDOTime03', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h04_str: str = Field(alias='CollisionPUDOTime04', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h05_str: str = Field(alias='CollisionPUDOTime05', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h06_str: str = Field(alias='CollisionPUDOTime06', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h07_str: str = Field(alias='CollisionPUDOTime07', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h08_str: str = Field(alias='CollisionPUDOTime08', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h09_str: str = Field(alias='CollisionPUDOTime09', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h10_str: str = Field(alias='CollisionPUDOTime10', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h11_str: str = Field(alias='CollisionPUDOTime11', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h12_str: str = Field(alias='CollisionPUDOTime12', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h13_str: str = Field(alias='CollisionPUDOTime13', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h14_str: str = Field(alias='CollisionPUDOTime14', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h15_str: str = Field(alias='CollisionPUDOTime15', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h16_str: str = Field(alias='CollisionPUDOTime16', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h17_str: str = Field(alias='CollisionPUDOTime17', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h18_str: str = Field(alias='CollisionPUDOTime18', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h19_str: str = Field(alias='CollisionPUDOTime19', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h20_str: str = Field(alias='CollisionPUDOTime20', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h21_str: str = Field(alias='CollisionPUDOTime21', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h22_str: str = Field(alias='CollisionPUDOTime22', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    collission_pudo_h23_str: str = Field(alias='CollisionPUDOTime23', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    law_enforcement_interactions_str: str = Field(alias='LawEnforcementAll', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    citation_moving_str: str = Field(alias='CitationsMoving', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    citation_nonmoving_str: str = Field(alias='CitationsNonmoving', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    traffic_stop_no_citation_str: str = Field(alias='TrafficStops', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    assault_total_str: str = Field(alias='AssaultsAll', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    assault_sexual_str: str = Field(alias='AssaultsSexual', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    assault_nonsexual_str: str = Field(alias='AssaultsNonsexual', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    assault_passenger_against_passenger_str: str = Field(alias='AssaultClaimantPassengerPassenger', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    assault_passenger_against_driver_str: str = Field(alias='AssaultClaimaintPassengerDriver', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    assault_driver_against_passenger_str: str = Field(alias='AssaultClaimaintDriverPassenger', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    harass_total_str:  str = Field(alias='HarassmentAll', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    harass_sexual_str: str = Field(alias='HarassmentSexual', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    harass_nonsexual_str: str = Field(alias='HarassmentNonsexual', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    harass_passenger_against_passenger_str: str = Field(alias='HarassmentClaimantPassengerPassenger', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    harass_passenger_against_driver_str: str = Field(alias='HarassmentClaimantPassengerDriver', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    harass_driver_against_passenger_str: str = Field(alias='HarassmentClaimantDriverPassenger', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    pudo_travel_lane_str: str = Field(alias='PUDOTravelLaneAll', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h00_str: str = Field(alias='PUDOTravelLaneTime00', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h01_str: str = Field(alias='PUDOTravelLaneTime01', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h02_str: str = Field(alias='PUDOTravelLaneTime02', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h03_str: str = Field(alias='PUDOTravelLaneTime03', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h04_str: str = Field(alias='PUDOTravelLaneTime04', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h05_str: str = Field(alias='PUDOTravelLaneTime05', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h06_str: str = Field(alias='PUDOTravelLaneTime06', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h07_str: str = Field(alias='PUDOTravelLaneTime07', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h08_str: str = Field(alias='PUDOTravelLaneTime08', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h09_str: str = Field(alias='PUDOTravelLaneTime09', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h10_str: str = Field(alias='PUDOTravelLaneTime10', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h11_str: str = Field(alias='PUDOTravelLaneTime11', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h12_str: str = Field(alias='PUDOTravelLaneTime12', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h13_str: str = Field(alias='PUDOTravelLaneTime13', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h14_str: str = Field(alias='PUDOTravelLaneTime14', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h15_str: str = Field(alias='PUDOTravelLaneTime15', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h16_str: str = Field(alias='PUDOTravelLaneTime16', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h17_str: str = Field(alias='PUDOTravelLaneTime17', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h18_str: str = Field(alias='PUDOTravelLaneTime18', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h19_str: str = Field(alias='PUDOTravelLaneTime19', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h20_str: str = Field(alias='PUDOTravelLaneTime20', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h21_str: str = Field(alias='PUDOTravelLaneTime21', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h22_str: str = Field(alias='PUDOTravelLaneTime22', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    pudo_travel_lane_h23_str: str = Field(alias='PUDOTravelLaneTime23', pattern=f'{numeric_re}|{redacted_re}|{not_provided_re}|{na_re}')
    complaint_safety_str: str = Field(alias='ComplaintsSafety', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    complaint_pudo_str: str = Field(alias='ComplaintsPUDO', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    complaint_access_str: str = Field(alias='ComplaintsAccessibility', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    complaint_wav_str: str = Field(alias='ComplaintsWAV', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    complaint_customer_service_str: str = Field(alias='ComplaintsCustomerService', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    complaint_other_str: str = Field(alias='ComplaintsOther', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    payout_str_str: str = Field(alias='PayoutsTotal', pattern=f'{numeric_re}|{redacted_re}|{na_re}')

    @computed_field
    @property
    def collision_total(self) -> float:
        return numeric_str_to_float(self.collision_total_str)

    @computed_field
    @property
    def collision_occ(self) -> float:
        return numeric_str_to_float(self.collision_occ_str)

    @computed_field
    @property
    def collision_ped(self) -> float:
        return numeric_str_to_float(self.collision_ped_str)

    @computed_field
    @property
    def collision_bike(self) -> float:
        return numeric_str_to_float(self.collision_bike_str)

    @computed_field
    @property
    def collision_mc(self) -> float:
        return numeric_str_to_float(self.collision_mc_str)

    @computed_field
    @property
    def collision_other(self) -> float:
        return numeric_str_to_float(self.collision_other_str)

    @computed_field
    @property
    def collision_rail(self) -> float:
        return numeric_str_to_float(self.collision_rail_str)

    @computed_field
    @property
    def collision_property(self) -> float:
        return numeric_str_to_float(self.collision_property_str)

    @computed_field
    @property
    def collision_pdo(self) -> float:
        return numeric_str_to_float(self.collision_pdo_str)

    @computed_field
    @property
    def collision_injury_possible(self) -> float:
        return numeric_str_to_float(self.collision_injury_possible_str)

    @computed_field
    @property
    def collision_injury_minor(self) -> float:
        return numeric_str_to_float(self.collision_injury_minor_str)

    @computed_field
    @property
    def collision_injury_sever(self) -> float:
        return numeric_str_to_float(self.collision_injury_severe_str)

    @computed_field
    @property
    def collision_fatality(self) -> float:
        return numeric_str_to_float(self.collision_fatality_str)

    @computed_field
    @property
    def collission_h00(self) -> float:
        return numeric_str_to_float(self.collission_h00_str)

    @computed_field
    @property
    def collission_h01(self) -> float:
        return numeric_str_to_float(self.collission_h01_str)

    @computed_field
    @property
    def collission_h02(self) -> float:
        return numeric_str_to_float(self.collission_h02_str)

    @computed_field
    @property
    def collission_h03(self) -> float:
        return numeric_str_to_float(self.collission_h03_str)

    @computed_field
    @property
    def collission_h04(self) -> float:
        return numeric_str_to_float(self.collission_h04_str)

    @computed_field
    @property
    def collission_h05(self) -> float:
        return numeric_str_to_float(self.collission_h05_str)

    @computed_field
    @property
    def collission_h06(self) -> float:
        return numeric_str_to_float(self.collission_h06_str)

    @computed_field
    @property
    def collission_h07(self) -> float:
        return numeric_str_to_float(self.collission_h07_str)

    @computed_field
    @property
    def collission_h08(self) -> float:
        return numeric_str_to_float(self.collission_h08_str)

    @computed_field
    @property
    def collission_h09(self) -> float:
        return numeric_str_to_float(self.collission_h09_str)

    @computed_field
    @property
    def collission_h10(self) -> float:
        return numeric_str_to_float(self.collission_h10_str)

    @computed_field
    @property
    def collission_h11(self) -> float:
        return numeric_str_to_float(self.collission_h11_str)

    @computed_field
    @property
    def collission_h12(self) -> float:
        return numeric_str_to_float(self.collission_h12_str)

    @computed_field
    @property
    def collission_h13(self) -> float:
        return numeric_str_to_float(self.collission_h13_str)

    @computed_field
    @property
    def collission_h14(self) -> float:
        return numeric_str_to_float(self.collission_h14_str)

    @computed_field
    @property
    def collission_h15(self) -> float:
        return numeric_str_to_float(self.collission_h15_str)

    @computed_field
    @property
    def collission_h16(self) -> float:
        return numeric_str_to_float(self.collission_h16_str)

    @computed_field
    @property
    def collission_h17(self) -> float:
        return numeric_str_to_float(self.collission_h17_str)

    @computed_field
    @property
    def collission_h18(self) -> float:
        return numeric_str_to_float(self.collission_h18_str)

    @computed_field
    @property
    def collission_h19(self) -> float:
        return numeric_str_to_float(self.collission_h19_str)

    @computed_field
    @property
    def collission_h20(self) -> float:
        return numeric_str_to_float(self.collission_h20_str)

    @computed_field
    @property
    def collission_h21(self) -> float:
        return numeric_str_to_float(self.collission_h21_str)

    @computed_field
    @property
    def collission_h22(self) -> float:
        return numeric_str_to_float(self.collission_h22_str)

    @computed_field
    @property
    def collission_h23(self) -> float:
        return numeric_str_to_float(self.collission_h23_str)

    @computed_field
    @property
    def collision_pudo_total(self) -> float:
        return numeric_str_to_float(self.collision_pudo_total_str)

    @computed_field
    @property
    def collision_pudo_passenger(self) -> float:
        return numeric_str_to_float(self.collision_pudo_passenger_str)

    @computed_field
    @property
    def collision_pudo_ped(self) -> float:
        return numeric_str_to_float(self.collision_pudo_ped_str)

    @computed_field
    @property
    def collision_pudo_bike(self) -> float:
        return numeric_str_to_float(self.collision_pudo_bike_str)

    @computed_field
    @property
    def collision_pudo_mc(self) -> float:
        return numeric_str_to_float(self.collision_pudo_mc_str)

    @computed_field
    @property
    def collision_pudo_other(self) -> float:
        return numeric_str_to_float(self.collision_pudo_other_str)

    @computed_field
    @property
    def collision_pudo_rail(self) -> float:
        return numeric_str_to_float(self.collision_pudo_rail_str)

    @computed_field
    @property
    def collision_pudo_property(self) -> float:
        return numeric_str_to_float(self.collision_pudo_property_str)

    @computed_field
    @property
    def collission_pudo_h00(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h00_str)

    @computed_field
    @property
    def collission_pudo_h01(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h01_str)

    @computed_field
    @property
    def collission_pudo_h02(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h02_str)

    @computed_field
    @property
    def collission_pudo_h03(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h03_str)

    @computed_field
    @property
    def collission_pudo_h04(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h04_str)

    @computed_field
    @property
    def collission_pudo_h05(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h05_str)

    @computed_field
    @property
    def collission_pudo_h06(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h06_str)

    @computed_field
    @property
    def collission_pudo_h07(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h07_str)

    @computed_field
    @property
    def collission_pudo_h08(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h08_str)

    @computed_field
    @property
    def collission_pudo_h09(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h09_str)

    @computed_field
    @property
    def collission_pudo_h10(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h10_str)
        
    @computed_field
    @property
    def collission_pudo_h11(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h11_str)

    @computed_field
    @property
    def collission_pudo_h12(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h12_str)

    @computed_field
    @property
    def collission_pudo_h13(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h13_str)

    @computed_field
    @property
    def collission_pudo_h14(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h14_str)

    @computed_field
    @property
    def collission_pudo_h15(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h15_str)

    @computed_field
    @property
    def collission_pudo_h16(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h16_str)

    @computed_field
    @property
    def collission_pudo_h17(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h17_str)

    @computed_field
    @property
    def collission_pudo_h18(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h18_str)

    @computed_field
    @property
    def collission_pudo_h19(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h19_str)

    @computed_field
    @property
    def collission_pudo_h20(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h20_str)

    @computed_field
    @property
    def collission_pudo_h21(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h21_str)

    @computed_field
    @property
    def collission_pudo_h22(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h22_str)

    @computed_field
    @property
    def collission_pudo_h23(self) -> float:
        return numeric_str_to_float(self.collission_pudo_h23_str)

    @computed_field
    @property
    def law_enforcement_interactions(self) -> float:
        return numeric_str_to_float(self.law_enforcement_interactions_str)

    @computed_field
    @property
    def citation_moving(self) -> float:
        return numeric_str_to_float(self.citation_moving_str)

    @computed_field
    @property
    def citation_nonmoving(self) -> float:
        return numeric_str_to_float(self.citation_nonmoving_str)

    @computed_field
    @property
    def traffic_stop_no_citation(self) -> float:
        return numeric_str_to_float(self.traffic_stop_no_citation_str)

    @computed_field
    @property
    def assault_total(self) -> float:
        return numeric_str_to_float(self.assault_total_str)

    @computed_field
    @property
    def assault_sexual(self) -> float:
        return numeric_str_to_float(self.assault_sexual_str)

    @computed_field
    @property
    def assault_nonsexual(self) -> float:
        return numeric_str_to_float(self.assault_nonsexual_str)

    @computed_field
    @property
    def assault_passenger_against_passenger(self) -> float:
        return numeric_str_to_float(self.assault_passenger_against_passenger_str)

    @computed_field
    @property
    def assault_passenger_against_driver(self) -> float:
        return numeric_str_to_float(self.assault_passenger_against_driver_str)

    @computed_field
    @property
    def assault_driver_against_passenger(self) -> float:
        return numeric_str_to_float(self.assault_driver_against_passenger_str)

    @computed_field
    @property
    def harass_total(self) -> float:
        return numeric_str_to_float(self.harass_total_str)

    @computed_field
    @property
    def harass_sexual(self) -> float:
        return numeric_str_to_float(self.harass_sexual_str)

    @computed_field
    @property
    def harass_nonsexual(self) -> float:
        return numeric_str_to_float(self.harass_nonsexual_str)
        
    @computed_field
    @property
    def harass_passenger_against_passenger(self) -> float:
        return numeric_str_to_float(self.harass_passenger_against_passenger_str)

    @computed_field
    @property
    def harass_passenger_against_driver(self) -> float:
        return numeric_str_to_float(self.harass_passenger_against_driver_str)

    @computed_field
    @property
    def harass_driver_against_passenger(self) -> float:
        return numeric_str_to_float(self.harass_driver_against_passenger_str)

    @computed_field
    @property
    def pudo_travel_lane(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_str)

    @computed_field
    @property
    def pudo_travel_lane_h00(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h00_str)

    @computed_field
    @property
    def pudo_travel_lane_h01(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h01_str)

    @computed_field
    @property
    def pudo_travel_lane_h02(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h02_str)

    @computed_field
    @property
    def pudo_travel_lane_h03(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h03_str)

    @computed_field
    @property
    def pudo_travel_lane_h04(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h04_str)

    @computed_field
    @property
    def pudo_travel_lane_h05(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h05_str)

    @computed_field
    @property
    def pudo_travel_lane_h06(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h06_str)

    @computed_field
    @property
    def pudo_travel_lane_h07(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h07_str)

    @computed_field
    @property
    def pudo_travel_lane_h08(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h08_str)

    @computed_field
    @property
    def pudo_travel_lane_h09(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h09_str)

    @computed_field
    @property
    def pudo_travel_lane_h10(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h10_str)
        
    @computed_field
    @property
    def pudo_travel_lane_h11(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h11_str)

    @computed_field
    @property
    def pudo_travel_lane_h12(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h12_str)

    @computed_field
    @property
    def pudo_travel_lane_h13(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h13_str)

    @computed_field
    @property
    def pudo_travel_lane_h14(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h14_str)

    @computed_field
    @property
    def pudo_travel_lane_h15(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h15_str)

    @computed_field
    @property
    def pudo_travel_lane_h16(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h16_str)

    @computed_field
    @property
    def pudo_travel_lane_h17(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h17_str)

    @computed_field
    @property
    def pudo_travel_lane_h18(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h18_str)

    @computed_field
    @property
    def pudo_travel_lane_h19(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h19_str)

    @computed_field
    @property
    def pudo_travel_lane_h20(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h20_str)

    @computed_field
    @property
    def pudo_travel_lane_h21(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h21_str)
        
    @computed_field
    @property
    def pudo_travel_lane_h22(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h22_str)

    @computed_field
    @property
    def pudo_travel_lane_h23(self) -> float:
        return numeric_str_to_float(self.pudo_travel_lane_h23_str)

    @computed_field
    @property
    def complaint_safety(self) -> float:
        return numeric_str_to_float(self.complaint_safety_str)

    @computed_field
    @property
    def complaint_access(self) -> float:
        return numeric_str_to_float(self.complaint_access_str)

    @computed_field
    @property
    def complaint_pudo(self) -> float:
        return numeric_str_to_float(self.complaint_pudo_str)

    @computed_field
    @property
    def complaint_wav(self) -> float:
        return numeric_str_to_float(self.complaint_wav_str)

    @computed_field
    @property
    def complaint_customer_service(self) -> float:
        return numeric_str_to_float(self.complaint_customer_service_str)

    @computed_field
    @property
    def complaint_other(self) -> float:
        return numeric_str_to_float(self.complaint_other_str)

    @computed_field
    @property
    def payout_str(self) -> float:
        return numeric_str_to_float(self.payout_str_str)
    
class Charger(BaseModel):
    __name__ = 'Charger'
    
    tcp_id: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}'+f'|{missing_field_re}')
    # Individual companies use different year-quarter combinations to describe the same time.  For example, Cruise says reporting period 9/1/2022 - 11/30/2022 is year 2022 quarter 4, while
    # Waymo says it is year 2023 quarter 1.  Additionally, CPUC changed its reporting periods starting 1/1/2025, and Waymo (only company currently reporting) also changes their method for 
    # labeling quarters, resulting in the following: 
    #  9/1/2024 - 11/30/2024, year 2025 quarter 1
    # 12/1/2024 - 12/31/2024, year 2025 quarter <blank>
    #  1/1/2025 -  3/31/2025, year 2025 quarter 1
    year_str: str = Field(alias='Year', pattern=r'\d{4}'+f'|{redacted_re}|{na_re}')
    quarter_str: str = Field(alias='Quarter', pattern=f'[1-4]|{redacted_re}|{na_re}')
    charger_id: str = Field(alias='ChargerID')
    tract: str = Field(alias='ChargerTract', pattern=r'\d{10,12}|([Rr][Ee][Dd][Aa][Cc][Tt][Ee][Dd])|([Nn]/{0,1}[Aa])')
    power_str: str = Field(alias='ChargerPower', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    type: str = Field(alias='ChargerType')
    load_serving_entity: str = Field(alias='ChargerLSE')
    rate_name: str = Field(alias='ChargerRate')

    # @computed_field
    # @property
    # def year(self) -> float:
    #     return numeric_str_to_float(self.year_str)

    # @computed_field
    # @property
    # def quarter(self) -> float:
    #     return numeric_str_to_float(self.quarter_str)
    
    @computed_field
    @property
    def power(self) -> float:
        return numeric_str_to_float(self.power_str)
    
class ChargingSession(BaseModel):
    __name__ = 'ChargingSession'
    
    tcp_id: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}'+f'|{redacted_re}|{na_re}|{missing_field_re}')
    # Individual companies use different year-quarter combinations to describe the same time.  For example, Cruise says reporting period 9/1/2022 - 11/30/2022 is year 2022 quarter 4, while
    # Waymo says it is year 2023 quarter 1.  Additionally, CPUC changed its reporting periods starting 1/1/2025, and Waymo (only company currently reporting) also changes their method for 
    # labeling quarters, resulting in the following: 
    #  9/1/2024 - 11/30/2024, year 2025 quarter 1
    # 12/1/2024 - 12/31/2024, year 2025 quarter <blank>
    #  1/1/2025 -  3/31/2025, year 2025 quarter 1
    year_str: str = Field(alias='Year', pattern=r'\d{4}'+f'|{redacted_re}|{na_re}')
    quarter_str: str = Field(alias='Quarter', pattern=f'[1-4]?|{redacted_re}|{na_re}')
    charger_id: str = Field(alias='ChargerID')
    session_id: str = Field(alias='SessionID')
    timestamp: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='SessionDatetime')]
    duration_str: str = Field(alias='SessionDuration', pattern=f'{numeric_re}|{redacted_re}|{na_re}')

    # @computed_field
    # @property
    # def year(self) -> float:
    #     return numeric_str_to_float(self.year_str)

    # @computed_field
    # @property
    # def quarter(self) -> float:
    #     return numeric_str_to_float(self.quarter_str)
        
    @computed_field
    @property
    def duration(self) -> float:
        return numeric_str_to_float(self.duration_str)
    
class Stoppage(BaseModel):
    __name__ = 'Stoppage'
    tcp_id: str = Field(alias='TCPID', pattern=r'[A-Z]{3}\d{7}'+f'|{redacted_re}|{na_re}|{missing_field_re}')
    year_str: str = Field(alias='Year', pattern=r'\d{4}'+f'|{redacted_re}|{na_re}')
    quarter_str: str = Field(alias='Quarter', pattern=r'[1-4]'+f'|{redacted_re}|{na_re}')
    stop_id: str = Field(alias='StopID', max_length=150)
    start_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='DateTime')]
    end_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='TimeResolution')]
    vin: str = Field(alias='VIN', max_length=17)
    lat_str: str = Field(alias='LocLat', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    lon_str: str = Field(alias='LocLong', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    gt_18in_from_curb: str = Field(alias='LocCurb', pattern=f'Y|N|{redacted_re}|{na_re}')
    block_travel_lane: str = Field(alias='LocTravelLane', pattern=f'Y|N|{redacted_re}|{na_re}')
    block_transit_lane: str = Field(alias='LocTransitInf', pattern=f'Y|N|{redacted_re}|{na_re}')
    block_bike_lane: str = Field(alias='LocBikeLane', pattern=f'Y|N|{redacted_re}|{na_re}')
    block_fd_driveway: str = Field(alias='LocDrivewayFD', pattern=f'Y|N|{redacted_re}|{na_re}')
    block_crosswalk: str = Field(alias='LocCrosswalk', pattern=f'Y|N|{redacted_re}|{na_re}')
    block_intersection: str = Field(alias='LocIntersection', pattern=f'Y|N|{redacted_re}|{na_re}')
    lt_90in_rail: str = Field(alias='LocRail', pattern=f'Y|N|{redacted_re}|{na_re}')
    passenger: str = Field(alias='PassengerPresent', pattern=f'Y|N|{redacted_re}|{na_re}')
    ride_complete: str = Field(alias='RideComplete', pattern=f'Y|N|{redacted_re}|{na_re}')
    en_route: str = Field(alias='EnRoute', pattern=f'Y|N|{redacted_re}|{na_re}')
    nhtsa_sgo_id1: str = Field(alias='NHTSAReportID1', pattern=r'\d+-\d+'+f'|NULL|{redacted_re}')
    nhtsa_sgo_id2: str = Field(alias='NHTSAReportID2', pattern=r'\d+-\d+'+f'|NULL|{redacted_re}')
    nhtsa_sgo_id3: str = Field(alias='NHTSAReportID3', pattern=r'\d+-\d+'+f'|NULL|{redacted_re}')
    nhtsa_sgo_id4: str = Field(alias='NHTSAReportID4', pattern=r'\d+-\d+'+f'|NULL|{redacted_re}')
    nhtsa_sgo_id5: str = Field(alias='NHTSAReportID5', pattern=r'\d+-\d+'+f'|NULL|{redacted_re}')
    highest_injury_severity: str = Field(alias='InjurySeverity', pattern=f'Possible|Minor|Severe|Fatality|{redacted_re}|{na_re}')
    resolution: str = Field(alias='Resolution', pattern=f'Manual removal (by carrier)|Manual removal (by first responders)|Manual removal (other)|Resume operations following manual response|Resume operations|Other.*|{redacted_re}|{na_re}')
    manual_dispatch_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='TimeDispatch')]
    manual_arrival_time: Annotated[datetime | str, AfterValidator(lambda x: primary_type_or_na_or_redacted(x, datetime)), Field(alias='TimeArrive')]

class StoppageFleet(BaseModel):
    __name__ = 'StoppageFleet'

    tcp_id: str = Field(alias='TCPID', pattern=f'{redacted_re}|{na_re}'+r'|[A-Z]{3}\d{7}')
    year_str: str = Field(alias='Year', pattern=r'\d{4}'+f'|{redacted_re}|{na_re}')
    month_str: str = Field(alias='Month', pattern=f'0?[0-9]|10|11|12|{redacted_re}|{na_re}')
    manual_assisted_str: str = Field(alias='ManualCount', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    manual_relaunched_str: str = Field(alias='ManualRelaunch', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    manual_response_time_str: str = Field(alias='ManualResponseTime', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    manual_mean_resolve_time_str: str = Field(alias='ManualResolutionTime', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    ge30s_mean_resolve_time_str: str = Field(alias='ResolutionAverage', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    ge30s_median_resolve_time_str: str = Field(alias='ResolutionMedian', pattern=f'{numeric_re}|{redacted_re}|{na_re}')
    ge30s_pct_manual_removal: str = Field(alias='PctManual', pattern=f'{numeric_re}|{redacted_re}|{na_re}')