# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 23:43:46 2017

"""

import pandas
from pprint import pprint

#COOK Import file handling stuff so you can work off an unknown file

def get_data():
    ''' () -> pd.df
    Read in datafile to a pandas dataframe
    '''
    
    filename = 'Scouting doc sample.csv'
    
    data = pandas.read_csv(filename)
    
    pprint(data.keys())
    
    pprint(data.describe())
    
    print('\n\nSingle team\n')
    
    print(data.groupby(' team').describe().loc[1939])
    
    return data
    
def calculate_value(data):
    '''
    Takes scouting data columns and calculates each team's match contribution.
    
    Formula is as follows:
    
    Scoring Contribution = Auto Mobility * 5
        + Auto gears delivered * 20
        + Total gears delivered [1-2@20 pts each,3-6@10 pts each, 7-12@6.67 pts each]
        + Auto fuel high
        + Auto fuel low / 3
        + Tele fuel high / 3
        + Tele trips low * 4       (assuming 36ish fuel go in)
        + Climbs * 50
    
    
    Maybe?
    Sad = Dropped gears * 20 
        + Auto High Miss
        + Dead Bot * 100
        + High Goal Miss (tele) / 3
        
    Index(['match', ' team', ' baseline', ' auto gear', ' auto Gear Attempts',
       ' auto low Goal', ' lowGoalAttempts', ' auto high goal',
       ' auto high goal attempts', ' tele blocks', ' tele gear',
       ' tele gear attempts', ' tele low goal', ' tele low goal attempts',
       ' high goal', 'high goal attempts', ' tele climbing', ' dead bot'],
      dtype='object')
    '''
    
    score = data.apply(lambda row: row[' tele gear'])
    
    pprint(score)