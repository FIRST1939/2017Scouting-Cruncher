# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 23:12:28 2016

"""

import urllib.request
import json
from pprint import pprint
from tkinter import filedialog as fd
import csv
import os.path
from time import sleep
import pandas as pd

URL = 'http://www.thebluealliance.com/api/v2/'

THISYEAR = 2017

'''
X-TBA-App-Id is required by the blue alliance api for tracking
Default User-Agent value causes 403 Forbidden so I pretend to be a browser.
'''
REQHEADERS = {'X-TBA-App-Id': 'vhcook-frc1939:scouting:2',
              'User-Agent': 'Mozilla/5.0'}
              
DEFENSES = ['A_Portcullis','A_ChevalDeFrise','B_Ramparts','B_Moat',
            'C_Drawbridge','C_SallyPort','D_RoughTerrain', 'D_RockWall',
            'E_LowBar', 'NotSpecified']    
            
DONE = ['scmb','casd','mndu','mndu2','onto2','mike2','misou','mista','miwat',
        'waamv','waspo','ctwat','ncmcl','nhgrs','njfla','pahat','vahay'
        ]
              
def get_request(fullurl):
    request = urllib.request.Request(fullurl, headers = REQHEADERS)
    response = urllib.request.urlopen(request)
    jsonified = json.loads(response.read().decode("utf-8"))
    return jsonified


def get_team(team_num):
    fullurl = URL + 'team/frc' + str(team_num)
    result = get_request(fullurl)
    return result
   
    
def get_team_bots(team_num):
    fullurl = URL + 'team/frc' + str(team_num) + '/history/robots'
    print(fullurl)
    result = get_request(fullurl)
    return result
    
def get_team_history(team_num):
    fullurl = URL + 'team/frc' + str(team_num) + '/history/events'
    print(fullurl)
    result = get_request(fullurl)
    print('tick')
    return result


def get_award_history(team_num):    
    fullurl = URL + 'team/frc' + str(team_num) + '/history/awards'
    print(fullurl)
    result = get_request(fullurl)
    print('tick')
    return result

def get_team_year(team_num, year):
    fullurl = URL + 'team/frc' + str(team_num) + '/' + str(year) + '/events'
    print(fullurl)
    result = get_request(fullurl)
    return result
    
def get_event_list(year=THISYEAR):
    fullurl = URL + 'events/' + str(year)
    print(fullurl)
    result = get_request(fullurl)
    return result

def get_event_teams(event, year=THISYEAR):
    event_key = str(year) + event
    fullurl = URL + 'event/' + event_key + '/teams'
    print(fullurl)
    result = get_request(fullurl)
    return result

def get_event_matches(event, year=THISYEAR):
    event_key = str(year) + event
    fullurl = URL + 'event/' + event_key + '/matches'
    print(fullurl)
    result = get_request(fullurl)
    return result
    
def get_one_match(key):
    fullurl = URL + 'match/' + key
    print(fullurl)
    result = get_request(fullurl)
    return result
    
def get_event_stats(event, year=THISYEAR):
    #OPR, DPR, CCWM
    event_key = str(year) + event
    fullurl = URL + 'event/' + event_key + '/stats'
    print(fullurl)
    result = get_request(fullurl)
    return result    
    
def get_event_awards(event, year=THISYEAR):
    # www.thebluealliance.com/api/v2/event/<event key>/awards
    event_key = str(year) + event
    fullurl = URL + 'event/' + event_key + '/awards'
    print(fullurl)
    result = get_request(fullurl)
    return result    

def getauto(match):
    '''(dict) -> list of int
    
    Takes the dict of one match result and returns a list containing the 
    autonomous instances of 
    [scored high boulders, scored low boulders, crossings, reaches]
    
    For error-checking, crossings + reaches must be no greater than 6
    '''

    high = 0
    low = 0
    cross = 0
    reach = 0
    
    for al in ('red', 'blue'):
        high += match['score_breakdown'][al]['autoBouldersHigh']
        low += match['score_breakdown'][al]['autoBouldersLow']
        for bot in ['robot1Auto', 'robot2Auto', 'robot3Auto']:
            if match['score_breakdown'][al][bot] == 'Crossed':
                cross += 1
            elif match['score_breakdown'][al][bot] == 'Reached':
                reach += 1
    
    assert (cross + reach) <= 6
        
    return [match['key'], high, low, cross, reach]        
    
def gettele(match):
    '''(dict) -> list of int
    
    Takes the match dictionary and returns a list of these teleop scores:
    [high goals, low goals, robots challenging, robots scaling,
     number of breaches, number of towers captured]
   
    '''
    
    high = 0
    low = 0
    chal = 0
    scale = 0
    breach = 0
    cap = 0
    
    sb = match['score_breakdown']
    
    for al in ('red', 'blue'):
        high += sb[al]['teleopBouldersHigh']
        low += sb[al]['teleopBouldersLow']

        for face in ('towerFaceA', 'towerFaceB', 'towerFaceC'):
            if sb[al][face] == 'Challenged':
                chal += 1
            elif sb[al][face] == 'Scaled':
                scale += 1
        
        if sb[al]['teleopDefensesBreached']:
            breach += 1
        
        if sb[al]['teleopTowerCaptured']:
            cap += 1
            
    assert (scale + chal) <= 6

    return [high, low, chal, scale, breach, cap]
    
def getcode(keys):
    '''(list of str)-> list of str
    
    Takes match keys like 'THISYEARvahay_f1m1' and 'THISYEARmokc_f1m3', and returns a
    list coding the match type.
    
    'qm' Qualifying Match
    'qf' Quarterfinals
    'sf' Semifinals
    'f1' Finals
    '''
    
    outlist = []
    
    for item in keys:
        idx = item.find('_') + 1
        mt = item[idx:idx+2]
        
        outlist.append(mt)
    
    return outlist
    

def analyze_matches(event, year=THISYEAR):
    '''
    Take match data for event and find things
    
    Crossings per defense
    Crossings per position
    Crossings per defense in position
    '''
    
    data = get_event_matches(event, year)
    print('Analyzing', event, '\n')    
    
    #pprint(data[0])
    dcrossed={}
    dpositions={}
    keys = []
    autohigh=[]
    autolow=[]
    autocross=[]
    autoreach=[]
    thigh=[]
    tlow=[]
    tchallenge=[]
    tscale=[]
    tbreachct=[]
    tcapct=[]
    
    
    if len(data) == 0:
        print('\nSomething is horribly wrong with', event, year)
        autovectors = {}
        televectors = {}
    
    for match in data:
      
        if match['alliances']['blue']['score'] == -1:
            #print('Defect in',match['match_number'])
            continue
        for alliance in ['red', 'blue']:
            #Do the defenses
            if 'E_LowBar' not in dcrossed:
                dcrossed['E_LowBar'] = []
            dcrossed['E_LowBar'].append(match['score_breakdown'][alliance]['position1crossings'])
            for pos in range(2, 6):
                spot = str(pos)
                d = match['score_breakdown'][alliance]['position'+spot]
                if d not in dpositions:
                    dpositions[d] = []
                    dcrossed[d] = []
                dpositions[d].append(spot)
                dcrossed[d].append(match['score_breakdown'][alliance]['position'+spot+'crossings'])
                
                if d == 'NotSpecified':
                    print('Missing Defense Info:', match['match_number'], alliance, pos)
            
        # Do auton
        autons = getauto(match)
        keys.append(autons[0])
        autohigh.append(autons[1])
        autolow.append(autons[2])
        autocross.append(autons[3])
        autoreach.append(autons[4])

        
        # Do Teleop
        teles = gettele(match)
        thigh.append(teles[0])
        tlow.append(teles[1])
        tchallenge.append(teles[2])
        tscale.append(teles[3])
        tbreachct.append(teles[4])
        tcapct.append(teles[5])


    matchtype = getcode(keys)

        
        
    autovectors = {'keys': keys, 'mt': matchtype,
                   'high': autohigh, 'low': autolow,
                   'cross': autocross, 'reach': autoreach}
    
    televectors = {'keys': keys, 'mt': matchtype,
                   'high': thigh, 'low': tlow,
                   'challenges': tchallenge, 'scales': tscale,
                   'breaches': tbreachct, 'captures': tcapct}
        
    return (dpositions, dcrossed, autovectors, televectors)    
 
def defposit(positions, event, week, year=THISYEAR, write=None):
    '''
    Determine times each defense is in each position at an event
    '''
    
    dpos = {}
    cksum = [0,0,0,0]
    
    if write != None:
        filename = open(write, mode='a')

    for defense in DEFENSES:
        if defense not in positions:
            continue
        if defense not in dpos:
            dpos[defense] = [0,0,0,0,0]
            
        if defense != 'E_LowBar':
            for spot in positions[defense]:
                dpos[defense][int(spot) - 1] += 1
            
            total = 0
            for i in dpos[defense]:
                total += i
            #print(defense, total)
            if defense[0] == 'A':
                cksum[0] += total
            elif defense[0] == 'B':
                cksum[1] += total
            elif defense[0] == 'C':
                cksum[2] += total
            elif defense[0] == 'D':
                cksum[3] += total
            else:
                print(defense, 'Category not found')
                
        if write != None:
            outtext = week + ',' + event + ',usage,' +defense + ',' + str(dpos[defense]).strip('[]') + '\n'
            filename.write(outtext)
    
    if write != None:
        filename.close()
            
    #pprint(dpos)
    print('Category checksums', cksum)
    
def defcrossings(crossings, positions, event, week, write=None)            :
    '''
    Take crossing data for an event, and determine defense durability
    '''
    print('\nEvaluating Crossings\n')
    dcross = {}
    dbreach = {}
    
    if write != None:
        filename = open(write, mode='a')    
    
    for defense in DEFENSES:
        if defense not in crossings:
            continue
        
        if defense not in dcross:
            dcross[defense] = [0,0,0,0,0]
            dbreach[defense] = [0,0,0,0,0]
            
        if defense == 'E_LowBar':
            for i in range(len(crossings[defense])):
                dcross[defense][0] += crossings[defense][i]
                if crossings[defense][i] == 2:
                    dbreach[defense][0] += 1
        else:
            assert len(crossings[defense]) == len(positions[defense])
            for i in range(len(crossings[defense])):
                pos = int(positions[defense][i]) - 1
                dcross[defense][pos] += crossings[defense][i]
                if crossings[defense][i] == 2:
                    dbreach[defense][pos] += 1
        #print(defense, dcross[defense])

        if write != None:
            outtext = week + ',' + event + ',crossing,' +defense + ',' + str(dcross[defense]).strip('[]') + '\n'
            filename.write(outtext)
            outtext = week + ',' + event + ',breach,' +defense + ',' + str(dbreach[defense]).strip('[]') + '\n'
            filename.write(outtext)
    
    if write != None:
        filename.close()
        
def quickevents():        
    eventlist = get_event_list()
    outfilename = 'THISYEAR Events.csv'
    outkeys = ['name', 'event_code', 'start_date', 'end_date',
               'event_type_string']
               
    with open(outfilename, 'w', newline='') as outfile:
        outwriter = csv.writer(outfile, delimiter='|')
        
        outwriter.writerow(outkeys)
    
        for event in eventlist:
            print(event['short_name'], event['event_code'], event['start_date'])
            outwriter.writerow([event['name'], event['event_code'],
                               event['start_date'], event['end_date'],
                               event['event_type_string']])
        
def autofun(autons, event, week, outfile=None):
    '''(dict of lists of int, str, str)--> None
    
    Take the lists of auton performance, clean up and append a parseable file.
    '''
    
    if outfile != None:
        if not os.path.isfile(outfile):
            #print headers
            file = open(outfile, 'w')
            file.write('Week,Event,Match,Type,High,Low,Crossing,Reach\n')
            file.close()
    
        file = open(outfile, 'a')
        for i in range(len(autons['keys'])):
            goals = [str(autons['high'][i]),str(autons['low'][i]),
                     str(autons['cross'][i]),str(autons['reach'][i])]
            line = week + ',' + event + ',' 
            line = line + autons['keys'][i] + ',' + autons['mt'][i]
            line = line + ',' + str(goals).strip('[]') +'\n'
            line = line.replace('\'','')
            file.write(line)
        file.close
        
def dumptele(teles, event, week, outfile=None):
    '''(dict of lists of int, str, str)--> None
    
    Take the lists of teleop performance, clean up and append a parseable file.
    
        televectors = {'keys': keys, 'mt': matchtype,
                   'high': thigh, 'low': tlow,
                   'challenges': tchallenge, 'scales': tscale,
                   'breaches': tbreachct, 'captures': tcapct}
    '''
    if outfile != None:
        if not os.path.isfile(outfile):
            #print headers
            file = open(outfile, 'w')
            file.write('Week,Event,Match,Type,High,Low,Challenges,Scales,Breaches,Captures\n')
            file.close()
    
        file = open(outfile, 'a')
        for i in range(len(teles['keys'])):
            goals = [str(teles['high'][i]),str(teles['low'][i]),
                     str(teles['challenges'][i]),str(teles['scales'][i]),
                     str(teles['breaches'][i]),str(teles['captures'][i])]
            line = week + ',' + event + ','
            line = line + teles['keys'][i] + ',' + teles['mt'][i]
            line = line + ',' + str(goals).strip('[]') +'\n'
            line = line.replace('\'','')
            file.write(line)
        file.close
    
def weekanalysis(week):
    eventfilename = fd.askopenfilename(title='Event List')

    writefile = fd.asksaveasfilename(title='Base Output Filename')  

    deffile = writefile + '-def.csv'
    autofile = writefile + '-auto.csv'
    telefile = writefile + '-tele.csv'
    
    weekevents = []
    
    with open(eventfilename, mode='r', newline='') as eventfile:
        eventreader = csv.reader(eventfile, delimiter='|')
        for row in eventreader:
            if row[5] == str(week):
                weekevents.append(row[1])
  
    for item in weekevents:
        positions, crossings, autons, teleops = analyze_matches(item)
        defposit(positions, item, str(week), write=deffile)
        defcrossings(crossings, positions, item, str(week), write=deffile)
        autofun(autons, item, str(week), autofile)
        dumptele(teleops, item, str(week), telefile)
        
    print('\nAll Done Now\n')

def d2cevents(teamlist):
    '''
    Take the team event list 
    
     {5931: [(5931, 'Bots of Prey'),
         {'key': 'THISYEARcars',
          'name': 'Carson Division',
          'start_date': 'THISYEAR-04-27'},
         {'key': 'THISYEARidbo',
          'name': 'Idaho Regional',
          'start_date': 'THISYEAR-03-30'}]},
          
    reformat it like this
    
    [[5931, 'Bots of Prey', 'THISYEARcars', 'Carson Division','THISYEAR-04-27']]
    '''

    d2clist = []
    d2clist.append('Team, Nick, ECode, EventName, StartDate')

    
    for oneteam in teamlist:
        pprint(oneteam)
        header = [oneteam[0][0], oneteam[0][1]]
        
        
        for curevent in oneteam[1:]:
            thisone = header[:]
            thisone.append(curevent['key'])
            thisone.append(curevent['name'])
            thisone.append(curevent['start_date'])
            
            d2clist.append(thisone)
    
    return d2clist
    
def awdclean(awdname):
    '''
    Takes award name and returns standardized short spelling.
    '''
   
    if 'Gracious' in awdname:
        newawd = 'Gracious Professionalism'
    elif 'Star' in awdname:
        newawd = 'Rookie All-Star'
    elif 'Subdivision' in awdname:
        newawd = awdname
    elif 'Division' in awdname:
        if 'Finalist' in awdname:
            newawd = 'Division Finalist'
        elif 'Winner' in awdname or 'Champion' in awdname:
            newawd = 'Division Winner'
    elif 'Imagery' in awdname:
        newawd = 'Imagery'
    elif 'Quality' in awdname:
        newawd = 'Quality'
    elif 'Chairman' in awdname:
        if 'District' in awdname:
            newawd = 'District Chairmans Award'
        elif 'Regional' in awdname:
            newawd = 'Regional Chairmans Award'
        else:
            newawd = awdname
            print('WTF:', awdname)
    elif 'Inspiration' in awdname:
        if 'Rookie' in awdname:
            newawd = 'Rookie Inspiration'
        elif 'District' in awdname:
            newawd = 'District Engineering Inspiration'
        elif 'Regional' in awdname:
            newawd = 'Regional Engineering Inspiration'
        else:
            newawd = 'Regional Engineering Inspiration?'
            #Note this will screw up champs EIs
    elif 'Entrepreneurship' in awdname or 'Kleiner' in awdname:
        newawd = 'Entrepreneurship'
    elif 'Safety' in awdname:
        newawd = 'Safety'
    elif 'Sportsmanship' in awdname:
        newawd = 'Gracious Professionalism'
    elif 'Control' in awdname:
        newawd = 'Innovation in Controls'
    elif 'Creativity' in awdname:
        newawd = 'Creativity'
    elif 'Finalist' in awdname:
        if 'Dean' in awdname:
            newawd = 'Deans List Finalist'
        elif 'Woodie' in awdname:
            newawd = 'Woodie Flowers Finalist'
        elif 'Subdivision' in awdname:
            newawd = 'Subdivision Finalist'
        elif 'Championship' in awdname:
            if 'District' in awdname:
                newawd = 'District Championship Finalist'
            elif 'State' in awdname:
                newawd = 'State Championship Finalist'
            else:
                newawd = 'Championship Finalist'
        elif 'District' in awdname:
            newawd = 'District Finalist'
        else:
            newawd = 'Regional Finalist'
    elif 'Winners' in awdname:
        newawd = awdname[:-1]
    elif 'Industrial Design' in awdname:
        newawd = 'GM Industrial Design'
    elif 'Spirit' in awdname:
        newawd = 'Team Spirit'
    elif 'Autodesk' in awdname:
        newawd = 'Autodesk Award'
    elif 'Delphi' in awdname:
        newawd = 'Delphi Excellence in Engineering'
    elif 'Judge' in awdname:
        newawd = 'Judges Award'
    
    else:
        newawd = awdname
        
    
    return newawd
        
def d2ca(teamlist):
    
    awdlist = []
    awdlist.append(['Team,EventKey,Award'])
    for team in teamlist:
        #pprint(teamlist[team])
        for ekey in teamlist[team]:
            for award in teamlist[team][ekey]:
                awdlist.append([team, ekey, awdclean(award)])    

    return awdlist
    
def andy(event='mokc'):
    teamdetails = get_event_teams(event)
    #print(teamdetails[0])
    teamlist=[]
    nicks= {}
    
    for team in teamdetails:
        teamlist.append(team['team_number'])
        nicks[team['team_number']] = team['nickname']
        
    teamlist.sort()
    print(teamlist)

    teamhistory=[]
    team2017=[]
    team2016=[]
    teamawards={}

    for team in teamlist:
        history = get_team_history(team)
        print('Slow down')
        sleep(5)
        teamhistory.append(history)
        thisyear = []
        lastyear = []
        for anevent in history:
            if anevent['end_date'] == None:
                pass
            elif anevent['end_date'][0:4] == '2017':
                #pprint(event)
                thisyear.append(anevent)
            elif anevent['end_date'][0:4] == '2016':
                #pprint(event)
                lastyear.append(anevent)

        thisyearshort = []
        thisyearshort.append((team, nicks[team]))
        lastyearshort = []
        for thisevent in thisyear:
            summary = {'name': thisevent['name'], 'start_date': thisevent['start_date'],
                       'key': thisevent['key']}
            thisyearshort.append(summary)

        for thisevent in lastyear:
            summary = {'name': thisevent['name'], 'start_date': thisevent['start_date'],
                       'key': thisevent['key']}
            lastyearshort.append(summary)
        
        team2017.append(thisyearshort)
        team2016.append(lastyearshort)

        awards = get_award_history(team)
        print('Slow down')
        sleep(5)
        #pprint(awards)
        shortawards = {}
        for award in awards:
            if award['event_key'] not in shortawards:            
                shortawards[award['event_key']] = []
            shortawards[award['event_key']].append(award['name'])
        teamawards[team] = shortawards
        
   # writefile = fd.asksaveasfile(title='Save Andy\'s stuff', mode = 'w')   
   # writefile.write('\nTHISYEAR events:\n')
   # writefile.write(str(teamTHISYEAR))
   # writefile.write('\n\nAward histories\n')
   # writefile.write(str(teamawards))
    
    print('\n', event, '\n')                                        
    outfilename = event + '2017events.csv'
    outfile = open(outfilename, 'w')
    
    print('\nTHISYEAR events:')
    currentevents = d2cevents(team2017)
    for line in currentevents:
        outstr = str(line).replace('[','')
        outstr = outstr.replace(']','').replace('\'','').replace('"','')+'\n'
        outfile.write(outstr)
    
    outfile.close()
    outfilename = event+'Histories.csv'
    outfile = open(outfilename, 'w')
    
    print('\nAward histories')
    ehist = d2ca(teamawards)
    
    for line in ehist:
        outstr = str(line).replace('[','')
        outstr = outstr.replace(']','').replace('\'','').replace('"','')+'\n'
        outfile.write(outstr)
    
    outfile.close()
        
    
    print('\n', event ,'2016 Awards')
    pprint(get_event_awards(event, 2016))
    
def tbaTHISYEARDefPosition(event):
    '''(str) -> None
    Makes a defense position file in the same format as the DefenseTracker
    code using TBA data.
    '''
    matchlist = get_event_matches(event)
    
    outlist = []
    
    for match in matchlist:
        #Match#,Zone3Shared,Blue2,Blue4,Blue5,Red2,Red4,Red5
        if match['comp_level'] != 'qm':
            print(match['comp_level'])
        else:
            
            temp = []
        
            temp.append(match['match_number'])
            
            #assert match['score_breakdown']['blue']['position3'] == match['score_breakdown']['red']['position3']
            
            temp.append(match['score_breakdown']['blue']['position3'])
            temp.append(match['score_breakdown']['blue']['position2'])
            temp.append(match['score_breakdown']['blue']['position4'])
            temp.append(match['score_breakdown']['blue']['position5'])
            temp.append(match['score_breakdown']['red']['position2'])
            temp.append(match['score_breakdown']['red']['position4'])
            temp.append(match['score_breakdown']['red']['position5'])
            
            print(str(temp))
            outlist.append(temp)    
    
    writefile = fd.asksaveasfile(title='Base Output Filename',
                                     initialfile='tba-'+event+'defenses.csv')  
        
    writefile.write('Match#,Zone3Shared,Blue2,Blue4,Blue5,Red2,Red4,Red5\n')
    for line in outlist:
        outstr = str(line)+'\n'
            
        outstr=outstr.replace('[','').replace(']','')
        writefile.write(outstr)
            
    writefile.close()
    
def scoutMatchList(event):
    '''(str) -> None
    
    Pulls the match list from TBA and formats it in a way that will be helpful
    in analyzing the scout data
    '''
    outfilename='scoutmaster-matches-'+event+'.csv'
    
    prepfilename='system-matches'+event+'.csv'
    
    biglist = []
    biglist.append(['Match','Alliance','Team'])
    
    
    scoutlist = []
    
    matchlist = get_event_matches(event)
    
    for match in matchlist:
        if match['comp_level'] == 'qm':
            temp = []
        
            matchnum = match['match_number']
            blues = match['alliances']['blue']['teams']
            reds = match['alliances']['red']['teams']
                            
            for team in reds:
                entry = [matchnum, 'red', team[3:]]
                biglist.append(entry)
                temp.append(team[3:])
                
            for team in blues:
                entry = [matchnum, 'blue', team[3:]]
                biglist.append(entry)
                temp.append(team[3:])
                
            scoutlist.append(temp)

    
    outfile = open(outfilename,mode='w')
    
    for line in biglist:
        outstr = str(line).replace('\'','').replace(' ','').strip('[]') + '\n'
        outfile.write(outstr)
        
    outfile.close()
    
    prepfile = open(prepfilename,mode='w')
    
    for line in scoutlist:
        outstr = str(line).replace('\'','').replace(' ','').strip('[]') + ',\n'
        prepfile.write(outstr)
        
    prepfile.close()
    
def gethof():
    hoflist = [191,7,151,144,47,23,120,16,22,175,103,254,67,
               111,365,842,236,341,359,1114,1538,27]

    hoflist = [597]               
               
    hofhist = {}    
    for team in hoflist:
        hofhist[team] = get_award_history(team)


    awdlist = []        
    for team in hofhist:
        for award in hofhist[team]:
            awdlist.append([team, award['event_key'], award['name']])

    outfilename = 'hof.csv'
    outfile = open(outfilename,'a')
    
    for line in awdlist:
        print(line[0])
        if line[2][0:8] == 'Gracious':
            line[2] = 'Gracious Professionalism sponsored by Johnson & Johnson'
        outstr = str(line).replace('[','')
        outstr = outstr.replace(']','').replace('\'','').replace('"','')+'\n'
        outfile.write(outstr)
        
    outfile.close()
    
def eventresult2pd(pdwriter, event, year=THISYEAR):
    '''(pandas excelwriter object, str, number) -> string
    Pull match results, flatten the dataframe, put them in a pandas dataframe, 
    and dump to an open excel file.
    '''

    eventjson = get_event_matches(event, year)
    
    flatterevent = []
    for match in eventjson:
        red = {'alliance': 'red'}
        blue = {'alliance': 'blue'}
        for field in match:
            if field not in ['alliances', 'score_breakdown']:
                red[field] = match[field]
                blue[field] = match[field]
            elif field == 'alliances':
                for alliance in match['alliances']:
                    for item in match['alliances'][alliance]:
                        if alliance == 'red':
                            red[item] = match['alliances'][alliance][item]
                        else:
                            blue[item] = match['alliances'][alliance][item]
            elif field == 'score_breakdown' and match['score_breakdown'] != None:
                #None will occur when match is unplayed
                
                for alliance in match['score_breakdown']:
                    for item in match['score_breakdown'][alliance]:
                        if alliance == 'red':
                            red[item] = match['score_breakdown'][alliance][item]
                        else:
                            blue[item] = match['score_breakdown'][alliance][item]
            
        flatterevent.append(red)
        flatterevent.append(blue)
        
    resultsdf = pd.DataFrame(flatterevent)
    
    print(event, 'saved')
    resultsdf.to_excel(pdwriter, sheet_name=event)

def pullmultieventresults(weekevents):
    '''(list) -> 
    
    >>> writer = ExcelWriter('output.xlsx')
>>> df1.to_excel(writer,'Sheet1')
>>> df2.to_excel(writer,'Sheet2')
>>> writer.save()
    '''
    outfile = 'week 1.xlsx'  
    
    writer = pd.ExcelWriter(outfile)
    
    for item in weekevents:
        eventresult2pd(writer, item)
    
    writer.save()