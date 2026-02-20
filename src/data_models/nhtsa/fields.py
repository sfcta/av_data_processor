from enum import Enum
from datetime import time

'''
Docstring for data_model.fields.nhtsa
'''


class DriverOperatorType(str, Enum):
    CONSUMER = 'Consumer'
    IN_VEHICLE = 'In-Vehicle (Commercial / Test)'
    REMOTE = 'Remote (Commercial / Test)'
    IN_VEHICLE_AND_REMOTE = 'In-Vehicle and Remote (Commercial / Test)'
    NONE = 'None'
    OTHER = 'Other'
    UNKNOWN = 'Unknown'

class EngagementStatus(str, Enum):
    VERIFIED = 'Verified Engaged'
    ALLEGED = 'Alleged Engaged'
    VERIFIED_NOT = 'Verified Not Engaged'
    UNKNOWN = 'Unknown - See Narrative'

class RoadwayType(str, Enum):
    HIGHWAY_FREEWAY = 'Highway / Freeway'
    INTERSECTION = 'Intersection'
    STREET = 'Street'
    PARKINT_LOT = 'Parking Lot'

class HighestInjurySeverityAlleged(str, Enum):
    FATALITY = 'Fatality'
    SERIOUS_HOSPITALIZATION = 'Serious W/ Hospitalization'
    SERIOUS_NO_HOSPITALIZATION = 'Serious W/O Hospitalization'
    MODERATE_HOSPITALIZATION = 'Moderate W/ Hospitalization'
    MODERATE_NO_HOSPITALIZATION = 'Moderate W/O Hospitalization'
    MINOR_HOSPITALIZATION = 'Minor W/ Hospitalization'
    MINOR_NO_HOSPITALIZATION = 'Minor W/O Hospitalization'
    PROPERTY_DAMAGE_ONLY = 'Property Damage. No Injured Reported'
    NONE_REPORTED = 'No Injured Reported'
    UKNNOWN = 'Unknown'

    def to_legacy(self):
        '''
        in legacy reports, anything resulting in hospitalization was serious
        '''
        if self == self.FATALITY:
            return HighestInjurySeverityAllegedLegacy('Fatality')
        elif self in [self.SERIOUS_HOSPITALIZATION,
                      self.SERIOUS_NO_HOSPITALIZATION,
                      self.MODERATE_HOSPITALIZATION,
                      self.MINOR_HOSPITALIZATION]:
            return HighestInjurySeverityAllegedLegacy('Serious')
        elif self == self.MODERATE_NO_HOSPITALIZATION:
            return HighestInjurySeverityAllegedLegacy('Moderate')
        elif self == self.MINOR_NO_HOSPITALIZATION:
            return HighestInjurySeverityAllegedLegacy('Minor')
        elif self in [self.NONE_REPORTED, self.PROPERTY_DAMAGE_ONLY]:
            return HighestInjurySeverityAllegedLegacy('No Injuries Reported')
        return HighestInjurySeverityAllegedLegacy('Unknown')

class HighestInjurySeverityAllegedLegacy(str, Enum):
    FATALITY = 'Fatality'
    SERIOUS = 'Serious'
    MODERATE = 'Moderate'
    MINOR = 'Minor'
    NONE_REPORTED = 'No Injuries Reported'
    UKNNOWN = 'Unknown'

    def to_legacy(self):
        return self
    
class CrashWith(str, Enum):
    PASSENGER_CAR = 'Passenger Car'
    SUV = 'SUV'
    VAN = 'Van'
    PICKUP_TRUCK = 'Pickup Truck'
    MOTORCYCLE = 'Motorcycle'
    BUS = 'Bus'
    HEAVY_TRUCK = 'Heavy Truck'
    EMERGENCY_VEHICLE = 'First Responder Vehicle'
    PEDESTRIAN = 'Non-Motorist: Pedestrian'
    CYCLIST = 'Non-Motorist: Cyclist'
    SCOOTER_SKATEBOARD = 'Non-Motorist: Scooter - Skateboard'
    OTHER_NONMOTORIST = 'Non-Motorist: Other'
    POLE_TREE = 'Pole / Tree'
    OTHER_FIXED_OBJECT = 'Other Fixed Object'
    ANIMAL = 'Animal'
    OTHER = 'Other, see Narrative'
    UNKNOWN = 'Unknown'
