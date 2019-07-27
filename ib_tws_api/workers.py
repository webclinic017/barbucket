from time import sleep, strftime
from datetime import datetime
import pickle
import os
from multiprocessing import Pool

import workers

import pandas as pd
import numpy as np

from tinydb import TinyDB, Query



def pick_to_csv(filename):
    
    if filename.startswith('xxx'):
        return
    
    with (open('data/pickles/'+filename, 'rb')) as openfile:
        datalist = pickle.load(openfile)
    
    # Merge collected data into dataframe
    df = pd.DataFrame(columns=('date', 'open', 'high', 'low', 'close', 'volume'))
    for bar in datalist:
        row = {'date': bar.date, 'open': bar.open, 'high': bar.high, 'low': bar.low, 'close': bar.close, 'volume': bar.volume}
        df = df.append(row, ignore_index=True)
    df.loc[:, 'date'] = pd.to_datetime(df.date, format='%Y%m%d') #'%Y%m%d  %H:%M:%S'
    df = df.set_index('date')
    
    # Write dataframe to csv file
    df.to_csv('data/' + filename + '.csv')
    
    # Rename pickle file for delting
    os.rename('data/pickles/' + filename, 'data/pickles/' + 'xxx' + filename)