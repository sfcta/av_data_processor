from enum import Enum
from datetime import time

'''
Docstring for data_model.fields.nhtsa
'''

class ReasonUnfulfilled(str, Enum):
    NOT_ACCEPTED = 'not accepted' 
    CANCELLED_COMPANY = 'cancelled by av company'
    CANCELLED_PASSENGER = 'cancelled by passenger'
    PASSENGER_NO_SHOW = 'passenger no-show'
