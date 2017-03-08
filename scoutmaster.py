# -*- coding: utf-8 -*-
"""
Created on Mon Feb  6 23:43:46 2017

"""

import pandas
from pprint import pprint

#COOK Import file handling stuff so you can work off an unknown file

def scout():
    raw = get_data()
    
    cooked = calculate_value(raw)

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
        + Total gears delivered [1-2@20 pts each,3-6@10 pts each, 7-12@6.7 pts each]
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
    data.columns = ['match','team','baseline','autogear','autoGearAttempts',
                    'autolowGoal','lowGoalAttempts','autohighgoal',
                    'autohighgoalattempts','teleblocks','telegear',
                    'telegearattempts','telelowgoal','telelowgoalattempts',
                    'highgoal','highgoalattempts','teleclimbing','deadbot']


    
    data['autoScore'] = (data.baseline * 5 + data.autogear * 20 + 
                        data.autohighgoal + (data.autolowGoal / 3))
    
    data['gearCount'] = (data.autogear + data.telegear)
    
    scoreGears = pd.Series({0: 0, 1: 20, 2: 40,
                            3: 50, 4: 60, 5: 70, 6: 80,
                            7: 80+6.7, 8: 80+6.7*2, 9: 80+6.7*3,
                            10: 80+6.7*4, 11: 80+6.7*5,12: 120})
    
   
    data['gearScore'] = data.gearCount.map(scoreGears)
    
    data['score'] = (data.autoScore + data.gearScore + data.teleclimbing * 50 +
                     data.highgoal / 3 + data.telelowgoal * 4 )
          
    pprint(data.head())         
    
    return data