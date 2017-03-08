# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 22:20:49 2017

"""
import pandas as pd
from pprint import pprint
import matplotlib.pyplot as plt

def Main():
    bigdf = getdfsfromxls()
    
    onebigdf = mergedfs(bigdf)
    
    eventsum(onebigdf)
    
    
def getdfsfromxls():
    '''(Nonetype) -> dict of dataframes
    
    This reads back match data that my TBA scraper saved and passes it to a
    script to do things with it.
    
    #COOK At some point, set so I can select the file.
    '''
    file = 'week 1.xlsx'
    
    with pd.ExcelFile(file) as xls:
        bulkdfdict = pd.read_excel(xls,sheetname=None)
        
    print('List of events available')
    pprint(bulkdfdict.keys())
    
    print(bulkdfdict['mndu'].keys())

        
    return bulkdfdict
    
def mergedfs(bulkdfdict):
    '''(dict of dataframes) -> dataframe
    
    Takes the dict of dataframes and makes one big dataframe
    '''
   

    bigdf = pd.concat(bulkdfdict)
     
    #pprint(bigdf)
    bigdf.to_excel('all_events.xlsx', sheet_name='data')     
    return bigdf
    
    
    
def eventsum(bulkdict):
    '''(dict of dataframes) -> dataframe
    
    Summarizes events
    '''
    
    #bulkdict.score.plot(kind='hist', bins=[0,40,100,150,200,250,300,350,400,500])
    
    pprint(bulkdict.describe().transpose())
    
    interesting = ['score','autoPoints','teleopPoints','autoMobilityPoints',
                   'autoFuelHigh','autoFuelLow','autoFuelPoints',
                   'autoRotorPoints','teleopFuelHigh', 'teleopFuelLow',
                   'teleopFuelPoints','teleopRotorPoints',
                   'teleopTakeoffPoints','foulCount','foulPoints',
                   'techFoulCount','kPaBonusPoints','rotorBonusPoints']
    
    print('\nautoMobilityPoints')
    pprint(bulkdict.autoMobilityPoints.value_counts())
    
    print('\nautoRotorPoints')
    pprint(bulkdict.autoRotorPoints.value_counts())
    
    print('\nteleopRotorPoints')
    pprint(bulkdict.teleopRotorPoints.value_counts())
    
    print('\nteleopTakeoffPoints')
    pprint(bulkdict.teleopTakeoffPoints.value_counts())
    
    print('\nkPaBonusPoints')
    pprint(bulkdict.kPaBonusPoints.value_counts())
    
    print('\nrotorBonusPoints')
    pprint(bulkdict.rotorBonusPoints.value_counts())
    
    print('\nkPaRankingPointAchieved')
    pprint(bulkdict.kPaRankingPointAchieved.value_counts())

    print('\nrotorRankingPointAchieved')
    pprint(bulkdict.rotorRankingPointAchieved.value_counts())    

    print('\n')
    print('Fuel')
    ahigh = bulkdict.autoFuelHigh.value_counts()
    alow = bulkdict.autoFuelLow.value_counts()
    thigh = bulkdict.teleopFuelHigh.value_counts()
    tlow = bulkdict.teleopFuelLow.value_counts()
    
    graphthisthing(thigh.iloc[1:])
    
    print('\n')
    print('Sum')
    pprint(bulkdict.sum())
    
    print('\n')
    #print('Summary Grouped By WLT')
    
    #pprint(bulkdict.groupby('wlt').decribe())

def graphthisthing(thing):
    print(thing)
    othergraph = thing.plot()