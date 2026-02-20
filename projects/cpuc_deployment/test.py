
import pandas as pd
import csv
from data_models.cpuc_deployment.reports import Trip
from pathlib import Path

def lower_and_strip(x):
    if isinstance(x, str):
        return x.lower().strip()
    return x

if __name__=='__main__':
     INDIR = r'Q:\Data\Regulatory\AV\CPUC\Quarterly Reports\Deployment\2025-01-01_2025-03-31\Waymo'
     df = pd.read_csv(Path(INDIR, 'PSG0038152_2025_05_AV_Trips_Part0-Public.csv'))
     df['ReasonUnfulfilled'] = df['ReasonUnfulfilled'].map(lower_and_strip)

     data = []

     for idx, row in df.iterrows():
          d = row.to_dict()
          try:
               d1 = Trip(**d)
               data.append(d1.model_dump().values())
          except Exception as e:
               print(e)
               print('Index: {}'.format(idx))
               print(row)

     df_valid = pd.DataFrame(
          columns = list(Trip.model_fields.keys()) + list(Trip.model_computed_fields.keys()),
          data = data
          )