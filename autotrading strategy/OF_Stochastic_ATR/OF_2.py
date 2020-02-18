# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 16:41:53 2018

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
filenames.pop()
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


def trading_signals(filename, m):
    a, t= read_data(filename)
    a.index=pd.to_datetime(t)
   # lastdate=a.index[-1]   # t.iloc[-1]
#    of=a.loc[:,'OF']     # only order flow
    off=a.loc[:,('OF','eB','eA')]    # order flow, prices
    signals=np.zeros(len(off))
    
    for i in range(m,len(off)):
        past=[]
        past1=0
        for j in range(0,m):
            past.append(abs(off['OF'][i-m+j]))
        for k in range(len(past)):
            if abs(off['OF'][i])>=past[k]:
                past1+=1     # if it's greater than the past values, then plus one.
            else:
                past1=past1    
        if past1==m and off['OF'][i]>0 :         # if it equals m, which means the current order flow is greater 
            signals[i]=1     # than all of the OF in look-back periods, so generating a signal.
        elif past1==m and off['OF'][i]<0 :
            signals[i]=-1
        else:
            signals[i]=0
# filter out the signals making position increasing.
    for h in range(len(off)):
        if signals[h] == -1:
            j = h+1
            while j < len(off):
                if signals[j] == 1:
                    break
                else:
                    signals[j] = 0
                j += 1
        elif signals[h]==1:
            j = h+1
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


# next, take commision into consideration (225 yen for one trade, 450 for a round-trip)
# and also price multiplier (500 yen)
def net_profits(Gross_profits):
    comsn=225
    mtplr=500
    Net_profits=Gross_profits
    g=Gross_profits['Profit']
    netp=[]
    for i in range(len(g)):
        netp.append(g[i]*mtplr-comsn*2)
    Net_profits['NP&L']=netp
    return Net_profits
    
# calculate t stat and back test on the optimal value of cp and cn
#calculate P&L, prob of winning, t statistics
T=[]
TT=[]    # t statistics 
PoW=[]   #probability of winning 
PoWW=[]
for m in range(1,21): 
    lpnl=[]
    nc=ni=0
    for filename in filenames:
        ts=trading_signals(filename,m)
        fts=full_trading_signals(ts, filename)
        npnl=net_profits(gross_profits(fts))['NP&L']
        lpnl.append(list(npnl))
    flat_lpnl=[]
    for sublist in lpnl:
        for item in sublist:
            flat_lpnl.append(item)
    for ss in flat_lpnl:
        if ss>=0:
            nc+=1
        elif ss<0:
            ni+=1
    PoWW.append((m,round((nc/(nc+ni)),4)))     # prob. of winning 
    PoW.append(round((nc/(nc+ni)),4))
    mn=np.mean(flat_lpnl)
    std=np.std(flat_lpnl)
    n=len(flat_lpnl)
    tstat=mn*(np.sqrt(n))/std
    TT.append((m, round(tstat,4)))
    T.append(round(tstat,4))
t_best=max(T)
p_best=max(PoW)
print("-----------------------------------")
print(TT)
print("-----------------------------------")
print('the best look-back period and its t stat are  ', TT[T.index(t_best)])
print("-----------------------------------")
print(PoWW)
print("-----------------------------------")
print('the best look-back period based on prob. of winning is ', PoWW[PoW.index(p_best)])

from pandas import DataFrame
dff=DataFrame(TT)
dff.to_excel('Tstat_OFSample.xlsx')
df=DataFrame(PoWW)
df.to_excel('PoW_OFSample.xlsx')


        
        
    