import sys, os, csv, re
import datetime as dt
import numpy as np
import pandas as pd
import geopandas as gpd
import configparser
from utils.config import string_to_list

from reader.reader import ReportReader
from utils import helpers
from reader.writer import df_to_excel

def get_metrics(path, year, company, data_dict=None,
                completed_trips=True, passengers=True, vmt=True, pmt=True, collisions=True,
                collisions_pudo=True,
                fix_names=True, chunksize=5000000, logfile=None):
                     
    reader = ReportReader(
        indir=path, 
        company=company, 
        year=year,
        data_dict=data_dict
        )
    
    metrics = {} # metric -> report -> value
    
    if completed_trips:
        metrics['completed_trips'] = {}
        metrics['completed_trips']['Trip-Level'] = 0
        metrics['completed_trips']['Month-Level'] = 0
        metrics['completed_trips']['Monthly Tract (orig)'] = 0
        metrics['completed_trips']['Monthly Tract (dest)'] = 0
    if passengers:
        metrics['passengers'] = {}
        metrics['passengers']['Trip-Level'] = 0
        metrics['passengers']['Month-Level'] = 0
    if vmt:
        metrics['vmt'] = {}
        metrics['vmt']['Trip-Level'] = 0
        metrics['vmt']['Month-Level'] = 0
    if pmt:
        metrics['pmt'] = {}
        metrics['pmt']['Trip-Level'] = 0
        metrics['pmt']['Month-Level'] = 0
    if collisions:
        metrics['collisions'] = {}
        metrics['collisions']['Incidents-Complaints'] = 0
        metrics['collisions']['Incidents-Location'] = 0
    if collisions_pudo:
        metrics['collisions_pudo'] = {}
        metrics['collisions_pudo']['Incidents-Complaints'] = 0
        metrics['collisions_pudo']['Incidents-Location'] = 0
            
    if completed_trips or vmt:
        report = 'Trip-Level'
        pax_redactions, vmt_redactions, pmt_redactions, records = 0, 0, 0, 0
        for chunk in reader.read_report(report, fix_names=fix_names, chunksize=chunksize):
            
            records += len(chunk)
            if completed_trips:
                metric = 'completed_trips'
                print(company, report, metric, records)
                metrics[metric][report] += len(chunk.loc[chunk['TripFulfilled'].isin(['Y','y'])])
            if passengers:
                metric = 'passengers'
                print(company, report, metric, records)
                c = 'NumberPassengers'
                if c not in chunk.columns.tolist():
                    pax_redactions += len(chunk)
                else:
                    pax_redactions += (chunk[c].map(lambda x: str(x).lower()).eq('redacted') * 1).sum()
                try:
                    if pax_redactions > 0:
                        #print('Reacted {}%'.format(100.0*vmt_redactions/(3*records)))
                        metrics[metric][report] = 'Reacted {}%'.format(100.0*vmt_redactions/(3*records))
                    else:
                        metrics[metric][report] += chunk[c].sum()
                except:
                    print('failure on pax')
                    metrics[metric][report] = np.nan
            if vmt==True:
                metric = 'vmt'
                print(company, report, metric, records)
                for c in ['VMTP1','VMTP2','VMTP3']:
                    if c not in chunk.columns.tolist():
                        vmt_redactions += len(chunk)
                    else:
                        vmt_redactions += (chunk[c].map(lambda x: str(x).lower()).eq('redacted') * 1).sum()
                try:
                    if vmt_redactions > 0:
                        #print('Reacted {}%'.format(100.0*vmt_redactions/(3*records)))
                        metrics[metric][report] = 'Reacted {}%'.format(100.0*vmt_redactions/(3*records))
                    else:
                        metrics[metric][report] += chunk[['VMTP1','VMTP2','VMTP3']].sum().sum()
                except:
                    print('failure on vmt')
                    metrics[metric][report] = np.nan
            if pmt==True:
                metric = 'pmt'
                c = 'PassengerMilesTraveled'
                print(company, report, metric, records)
                if c not in chunk.columns.tolist():
                    pmt_redactions += len(chunk)
                else:
                    pmt_redactions += (chunk[c].map(lambda x: str(x).lower()).eq('redacted') * 1).sum()
                try:
                    if pmt_redactions > 0:
                        #print('Reacted {}%'.format(100.0*vmt_redactions/(3*records)))
                        metrics[metric][report] = 'Reacted {}%'.format(100.0*vmt_redactions/(3*records))
                    else:
                        metrics[metric][report] += chunk[c].sum()
                except:
                    print('failure on pmt')
                    metrics[metric][report] = np.nan

        report = 'Month-Level'
        for chunk in reader.read_report(report, fix_names=fix_names, chunksize=chunksize):
            for c in ['TotalVMTPeriod1','TotalVMTPeriod2','TotalVMTPeriod3','TotalPMT']:
                if isinstance(chunk[c].iloc[0], str):
                    chunk[c] = chunk[c].map(lambda x: x.replace(',','').replace(' ','')).astype(float)
            for c in ['TotalTrips','TotalPassengersCarried']:
                if isinstance(chunk[c].iloc[0], str):
                    chunk[c] = chunk[c].map(lambda x: x.replace(',','').replace(' ','')).astype(int)
            if completed_trips:
                metric = 'completed_trips'
                print(company, report, metric)
                metrics[metric][report] += chunk['TotalTrips'].sum()
            if passengers:
                metric = 'passengers'
                print(company, report, metric)
                metrics[metric][report] += chunk['TotalPassengersCarried'].sum()
            if vmt:
                metric = 'vmt'
                print(company, report, metric)
                metrics[metric][report] += chunk[['TotalVMTPeriod1','TotalVMTPeriod2','TotalVMTPeriod3']].sum().sum()
            if pmt:
                metric = 'pmt'
                print(company, report, metric)
                metrics[metric][report] += chunk['TotalPMT'].sum()
        
        report = 'Monthly Tract'
        if completed_trips:
            metric = 'completed_trips'
            print(company, report, metric)
            for chunk in reader.read_report(report, fix_names=fix_names, chunksize=chunksize):
                metrics[metric][report+' (orig)'] += chunk['TripsStart'].sum()
                metrics[metric][report+' (dest)'] += chunk['TripsEnd'].sum()
        
    if collisions or collisions_pudo:
        report = 'Incidents-Complaints'
        for chunk in reader.read_report(report, fix_names=fix_names, chunksize=chunksize):
            if collisions:
                metric = 'collisions'
                print(company, report, metric)
                metrics[metric][report] += chunk['CollisionsAll'].sum()
            if collisions_pudo:
                metric='collisions_pudo'
                print(company, report, metric)
                metrics[metric][report] += chunk['CollisionsPUDOAll'].sum()
        report = 'Incidents-Location'
        for chunk in reader.read_report(report, fix_names=fix_names, chunksize=chunksize):
            if collisions:
                metric = 'collisions'
                print(company, report, metric)
                metrics[metric][report] += chunk['CollisionsAll'].sum()
            if collisions_pudo:
                metric='collisions_pudo'
                print(company, report, metric)
                metrics[metric][report] += chunk['CollisionsPUDO'].sum()
    return metrics
    
def metric_dict_to_df(metrics):
    data = []
    for company, d1 in metrics.items():
        for metric, d2 in d1.items():
            for report, value in d2.items():
                data.append([company,metric,report,value])
                
    return pd.DataFrame(data, columns=['company','metric','report','value'])
    
def title_case(s):
    s = s.strip()
    return s[0].upper() + s[1:].lower()
    
def get_table_name(company, metric):
    parts = metric.split('_')
    table_name = title_case(company)
    for p in parts:
        table_name = table_name + '_' + title_case(p)
    return table_name + ' by Report'
    
def metric_dict_to_summary_df(metrics, company, metric):
    m = metrics[company][metric]
    
    if metric == 'completed_trips':
        index=['Trip-Level', 'Month-Level',
               'Monthly Tract (orig)', 'Monthly Tract (dest)']
        columns=['Completed Trips']
        data = [m[i] for i in index]
    elif metric == 'passengers':
        index=['Trip-Level', 'Month-Level']
        columns=['Passengers']
        data = [m[i] for i in index]
    elif metric == 'vmt':
        index=['Trip-Level', 'Month-Level']
        columns=['VMT']
        data = [m[i] for i in index]
    elif metric == 'pmt':
        index=['Trip-Level', 'Month-Level']
        columns=['PMT']
        data = [m[i] for i in index]
    elif metric == 'collisions':
        index=['Incidents-Complaints','Incidents-Location']
        columns=['Collisions']
        data = [m[i] for i in index]
    elif metric == 'collisions_pudo':
        index=['Incidents-Complaints','Incidents-Location']
        columns=['Collisions (PUDO)']
        data = [m[i] for i in index]
    else:
        raise Exception('unknown metric {}'.format(metric))

    df = pd.DataFrame(data, index=index, columns=columns)
    df['Difference'] = np.nan
    df['Pct Difference'] = np.nan
    
    if isinstance(df.iloc[0,0], str):
        df['Difference'] = 'Unknown'
        df['Pct Difference'] = 'Unknown'
    else:
        df['Difference'] = df[columns[0]] - df.iloc[0,0]
        df['Pct Difference'] = df['Difference'] / df.iloc[0,0]
        #df.iloc[0, 1] = '-'
        #df.iloc[0, 2] = '-'
    return df
    
    
if __name__=='__main__':
    args = sys.argv[1:]
    configpath = args[0]
    combined = {}
    
    cp = configparser.ConfigParser()
    f = open(configpath, 'r')
    cp.read_file(f)
    
    indir = cp.get('consistency','indir')
    outdir = cp.get('consistency','outdir')
    ddpath = cp.get('consistency','data_dict')
    year = cp.getint('consistency','year')
    ofile = cp.get('consistency','summary_ofile')
    
    completed_trips = cp.getboolean('consistency','completed_trips')
    passengers = cp.getboolean('consistency','passengers')
    vmt = cp.getboolean('consistency','vmt')
    pmt = cp.getboolean('consistency','pmt')
    collisions = cp.getboolean('consistency','collisions')
    collisions_pudo = cp.getboolean('consistency','collisions_pudo')
    
    companies = string_to_list(cp.get('consistency','companies'))
    
    dd = helpers.read_data_dictionary(path=ddpath, sheet_names=None)
    
    for company in companies:
        print('getting metrics for {}'.format(company))
        path = r'{}\{}'.format(indir,company)
        metrics = get_metrics(path, year, company, dd, 
                              completed_trips, passengers,
                              vmt, pmt,
                              collisions, collisions_pudo,
                              fix_names=True,
                              )
        combined[company] = metrics
        print('done with metrics for {}'.format(company))
    
    #df = metric_dict_to_df(metrics)
    writer = pd.ExcelWriter(os.path.join(outdir,ofile))
    row, col = 0, 0
    
    for company, d1 in combined.items():
        print(company)
        for metric, d2 in d1.items():
            print(metric)
            df = metric_dict_to_summary_df(combined, company, metric)
            table_name = get_table_name(company, metric)
            
            row, col = df_to_excel(
                writer, 
                sheet_name='Consistency',
                table_name=table_name,
                df=df,
                startrow=row,
                startcol=col,
                row_buffer=2,
                offset_rows=True,
                index=True)
        row, col = 0, 5
        
    writer.save()
    
    