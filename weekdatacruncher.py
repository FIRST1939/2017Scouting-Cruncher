# -*- coding: utf-8 -*-
"""
Created on Sat Mar  4 22:20:49 2017

"""
import pandas as pd
from pprint import pprint


def getdfsfromxls():
    file = 'week 1.xlsx'
    
    with pd.ExcelFile(file) as xls:
        bulkdfdict = pd.read_excel(xls,sheetname=None)
        
    print('List of events available')
    pprint(bulkdfdict.keys())
        
    return bulkdfdict
    
