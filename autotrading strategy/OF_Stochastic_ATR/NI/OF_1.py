# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 20:56:18 2018
order flow trading strategy on Nikkei 225 index futures
@author: janicelin
"""

from __future__ import  division, print_function, unicode_literals

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
import os


# read in all of the file names
#path='documents/exchange/SMU/QF206 trading/project/NI/'
filenames=os.listdir('.')
#filenames.pop()
for i in range(len(filenames)):
    filenames[i]= str(filenames[i])
# filenames is a list containing all of the data file names.    


#read in the price and volume data 
def read_data(filename):
   data = pd.read_csv(filename)
   time=data.iloc[:,0]
   time.rename('Time',inplace=True)
   data.index = pd.to_datetime(time)
   data=data.loc[:,('eB','eA','O','C','V','OF')]
   return data, time

# when order flow > (100,150,200,250), I should put market buy order,
# so I should take the eA price as my buying price, 
#as I can only buy at the next second.
# when order flow < (-50, -100, -150,-200, -250),
# I should put market sell order, so taking the eB as my selling price.

# risk management policy: not increasing the position
# and not holding the position overnight, which means closing position before
# the end of the trading day.
# index futures, selling first is possible.

#cp=100
#cn=-100

def trading_signals(filename, cp, cn):
    a, t= read_data(filename)
    a.index=pd.to_datetime(t)
   # lastdate=a.index[-1]   # t.iloc[-1]
#    of=a.loc[:,'OF']     # only order flow
    off=a.loc[:,('OF','eB','eA')]    # order flow, prices
    signals=np.zeros(len(off))
    for i in range(len(off)):
        if off['OF'][i]>=cp:
            signals[i]=1
        elif off['OF'][i]<=cn:
            signals[i]=-1 
        else:
            signals[i]=0
            
    # filter and delete the signals making position increase.
    for k in range(len(off)):
        if signals[k] == -1:
            j = k+1
            while j < len(off):
                if signals[j] == 1:
                    break
                else:
                    signals[j] = 0
                j += 1
        elif signals[k]==1:
            j = k+1
            while j < len(off):
                if signals[j] == -1:
                    break
                else:
                    signals[j] = 0
                j += 1
    off['Signals']=signals

    Trading_signals=pd.concat([
            pd.DataFrame({'Price': off.loc[off['Signals']==1,'eA'],
                          'Signal':'Buy'}),
            pd.DataFrame({'Price': off.loc[off['Signals']==-1,'eB'],
                          'Signal':'Sell'})
            ])
    Trading_signals.sort_index(inplace=True)
    return Trading_signals
# now, dealing with the position closing problem
# if the last signal is a sell, 
    # then check the first one, if it's a sell, then append a buy at the end.
    # but if it's a buy, then done!
# elif the last signals is a buy,
    # then check the first signal, if it's a buy, then append a sell
    # buy if it's a sell, then done!    
## to avoid liquidity problem,instead of doing the last trade in the last minute, 
## we use the last timestamp in the data
def full_trading_signals(Trading_signals, filename):
    a,t =read_data(filename)
    a.index=pd.to_datetime(t)
    if str(Trading_signals.loc[:,'Signal'][-1])=='Buy':
        if str(Trading_signals['Signal'][0])=='Buy':
            b=pd.DataFrame(a[-1:]['eB'])
            b['Signal']='Sell'
            b.rename(index=str, columns={'eB':'Price'},inplace=True)
            b.index=pd.to_datetime(b.index)
            frames=[Trading_signals,b]
            Full_Trading_signals=pd.concat(frames)
        else:
            Full_Trading_signals=Trading_signals
    elif str(Trading_signals.loc[:,'Signal'][-1])=='Sell':
        if str(Trading_signals['Signal'][0])=='Sell':
            b=pd.DataFrame(a[-1:]['eA'])
            b['Signal']='Buy'
            b.rename(index=str, columns={'eA':'Price'},inplace=True)
            b.index=pd.to_datetime(b.index)
            frames=[Trading_signals,b]
            Full_Trading_signals=pd.concat(frames)
        else:
            Full_Trading_signals=Trading_signals
    return Full_Trading_signals
    


#calculate P&L, prob of winning, t statistics

def gross_profits(Full_Trading_signals):
    profits=[]
    if str(Full_Trading_signals['Signal'][0])=='Sell':
        for i in range(1,len(Full_Trading_signals)+1,2):
            profits.append(Full_Trading_signals['Price'][i-1]-Full_Trading_signals['Price'][i])
        Gross_profits=pd.DataFrame({
         'Price': Full_Trading_signals.loc[(Full_Trading_signals['Signal']=='Buy'),'Price'],
         'Profit': profits,   
                })
    elif str(Full_Trading_signals['Signal'][0])=='Buy':
        for i in range(1,len(Full_Trading_signals)+1,2):
            profits.append(Full_Trading_signals['Price'][i]-Full_Trading_signals['Price'][i-1])
        Gross_profits=pd.DataFrame({
         'Price': Full_Trading_signals.loc[(Full_Trading_signals['Signal']=='Sell'),'Price'],
         'Profit': profits,   
                })
    return Gross_profits


# next, take commision into consideration
# and also price multiplier 
def net_profits(Gross_profits):

    

# calculate t stat and back test on the optimal value of cp and cn

    

    
    
    
    