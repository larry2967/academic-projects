# -*- coding: utf-8 -*-
"""
Created on Tue Apr  3 17:36:14 2018

@author: shivani
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import pickle 
from collections import OrderedDict
import matplotlib.dates as mdates
import os
from numpy import nan
from functools import wraps
from pandas import DataFrame, Series
from pandas.stats import moments


# ocilator: up - down, also if +90 or -90 shows signs of reversal, n starts form 25


def aroon(high, low, date, tf):
    AroonUp = []
    AroonDown = []
    AroonDate = []
    AroonOscillator = []
    for i in range(tf):
        AroonOscillator.append(0)
    
    x = tf
    
    while x < len(date): 
        Aroon_Up = (((high[x-tf:x].index(max(high[x-tf:x])))+1)/float(tf))*100
        Aroon_Down = (((low[x-tf:x].index(min(low[x-tf:x])))+1)/float(tf))*100
        Aroon_Oscillator = Aroon_Up - Aroon_Down
        
        AroonUp.append(Aroon_Up)
        AroonDown.append(Aroon_Down)
        AroonOscillator.append(Aroon_Oscillator)
        AroonDate.append(date[x])
        
        #print(date[x])
        #print ("#####")
        #print(high[x])
        #print(max(high[x-tf:x]))
        #print((high[x-tf:x].index(max(high[x-tf:x])))+1)
        #print(Aroon_Up)

        #print ("------")
        #print (low[x])
        #print (Aroon_Down)
        
        #print("*********")
        #print(Aroon_Oscillator)
        #print("********")
        
        x = x+1
        
    return AroonDate, AroonOscillator

with open("filenames.pickle","rb") as f:
    filenames = pickle.load(f)
        
#print(filenames)

#read in the price and volume data 

def read_data(filename):
   data = pd.read_csv(filename, index_col=0)
   #time=data.iloc[:,0]
   #print (data.head())
   data.index.rename('Time', inplace=True)
   data.index = pd.to_datetime(data.index)
   
   for c in range (len(data)-1):
        if ((data['eA'][c]) == 0):
            data['eA'][c] = data['eA'][c+1]
            if(data['eA'][c+1] == 0): 
               data['eA'][c+1] = data['eA'][c+2]
               data['eA'][c] = data['eA'][c+2]

   for d in range (len(data)-1):
        if (data['eB'][d] == 0):
            data['eB'][d] = data['eB'][d+1]
            if(data['eB'][d+1] == 0): 
               data['eB'][d+1] = data['eB'][d+2]
               data['eB'][d] = data['eB'][d+2]
   
   #data['eA']=data['eA'].replace(0,[data['eA'].get_loc([0]+1)])
   #data['eB']=data['eB'].replace(0,[data['eB'].get_loc([0]+1)])

   ##Replacing and removing 0 values from the data 
   #data = data.replace(0,nan)
   #data = data.dropna(axis=0, how='any')
   #data=data.replace(nan,0)
   #print(data.tail(40))
   return data

def Trading_Sig(filename, tf):
    data = read_data(filename)
    high = data.H.tolist()
    low = data.L.tolist()
    date = data.index.tolist()
    
    date, aroon1 = aroon(high,low,date,tf)
    #print ((aroon1))
    ns = len(data)
    #print(len(data))
    sig = np.zeros(ns)
    
    for i in range(tf, ns):
        if aroon1[i] in range (-100,-50):
            #print("this works1", aroon1[i])
            sig[i] = -1
            #print(sig[i])
        #elif aroon1[i] in range (-10, 0):
            #print("this works2", aroon1[i])
            #sig[i] = -1
            #print(sig[i])
        elif aroon1[i] in range (50, 100):
            #print("this works3", aroon1[i])
            sig[i] = +1
        #elif aroon1[i] in range (0,11):
            #print("this works4", aroon1[i])
            #sig[i] = +1
        else:
            #print("this works5", aroon1[i])
            sig[i] = 0
            
            #print("why")
    #print(sig)
    
    # filter and delete the signals making position increase.
    for k in range(len(data)):
        if sig[k] == -1:
            j = k+1
            while j < len(data):
                if sig[j] == 1:
                    break
                else:
                    sig[j] = 0
                j += 1
        elif sig[k]==1:
            j = k+1
            while j < len(data):
                if sig[j] == -1:
                    break
                else:
                    sig[j] = 0
                j += 1
      
        #maybe insert the signal thing here 
        #range(10, 0, -1)
   
    comp = pd.DataFrame({"Aroon Oscillator": aroon1, "Signal": sig})
    comp.index = pd.to_datetime(data.index)
    

    #print(data['eA'])
    #print(data['eB'])
                
    signal1 = pd.concat([
            pd.DataFrame({'Price': data.loc[comp['Signal']==+1,'eA'],
                          'Signal':'Buy'}),
            pd.DataFrame({'Price': data.loc[comp['Signal']==-1,'eB'],
                          'Signal':'Sell'})
            ])
    signal1.sort_index(inplace=True)
    #print("this is the count initial")
    print(signal1)
    return signal1, comp, sig
    
def full_trading_signals(filename,tf):
    data = read_data(filename) 
    signal1,comp, sig =Trading_Sig (filename,tf)
    ns = len(comp)
    #lastDataPt = data.tail(1)
    #lastSignal1pt = signal1.tail(1)
    counter1 = 0 
    counter2 = 0
    while (counter1 == 0) & (counter2 ==0): 
        for i in range (ns-2, 0, -1):
            if sig[i] == -1:
                counter1 = -1
                #print (sig[i])
                for j in range(i-1, 0, -1):
                    if sig[j] == -1:
                        counter2 = -1
                        #print (sig[j])
                        j = 0
                        break
                    elif sig[j] == 1:
                        counter2= 1
                        #print (sig[j])
                        j = 0
                        break
                    elif sig[j] == 0:
                        counter2 =0
                i = 0
                break
            elif sig[i] == 1:
                counter1 = 1
                #print (sig[i])
                for k in range(i-1, 0, -1):
                    if sig[k] == -1:
                        counter2 = -1
                        #print (sig[k])
                        k = 0
                        break
                    elif sig[k] == 1:
                        counter2= 1
                       # print (sig[k])
                        k = 0
                        break
                    elif sig[k] ==0:
                        counter2 = 0 
                i = 0
                break
            elif sig[i] == 0:
                counter1 = 0
        
    #print ("countercheck", counter1, counter2)
    
    remainVal = (sum(sig))
    #print ("this is the sum method", remainVal)

    if (remainVal != 0) and (sig[ns-1] !=0):
        sig[ns-1] = 0
    elif (remainVal !=0) and (counter1 == 1):
        sig[ns-1] =-1
    elif (remainVal !=0) and (counter1 == -1):
        sig[ns-1] =1
        
    #print ("what is changed to", sig[ns-1])
                       
    comp['Signal'] = sig
    signals = pd.concat([
            pd.DataFrame({'Price': data.loc[comp['Signal']==+1,'eA'],
                          'Signal':'Buy'}),
            pd.DataFrame({'Price': data.loc[comp['Signal']==-1,'eB'],
                          'Signal':'Sell'})
            ])
    signals.sort_index(inplace=True)
    return signals

def gross_profits (filename, tf):
    profits =[]
    signal = full_trading_signals(filename, tf)
    if str(signal['Signal'][0])=='Sell':
        for i in range(1,len(signal)+1,2):
            profits.append(signal['Price'][i-1]-signal['Price'][i])
        Gross_profits=pd.DataFrame({
         'Price': signal.loc[(signal['Signal']=='Buy'),'Price'],
         'Profit': profits,   
                })
    elif str(signal['Signal'][0])=='Buy':
        #print("it is on buy side")
        for i in range(1,len(signal)+1,2):
            profits.append(signal['Price'][i]-signal['Price'][i-1])
        Gross_profits=pd.DataFrame({
         'Price': signal.loc[(signal['Signal']=='Sell'),'Price'],
         'Profit': profits,   
                })
    print(Gross_profits)
    #print("this is profit")
    #print(totalprofit)
    #print(sum(profits))    
    #print (check.dtype())
    #print (data.dtypes())
    comsn=225
    mtplr=500
    Net_profits=Gross_profits
    g=Gross_profits['Profit']
    netp=[]
    for i in range(len(g)):
        netp.append(g[i]*mtplr-comsn*2)
    Net_profits['NP&L']=netp
    #print ("profit part 2")
    #print (sum(netp))
    
    totalprofit = sum(netp)
    
    return totalprofit
#print(date)
def calcAll (tf):
    totalprofit = []
    for i in range (len(filenames)):
        totalp = gross_profits (filenames[i], tf)
        totalprofit.append(totalp)
    ProfitAll = pd.DataFrame({"TotalNetProfit": totalprofit})
    
    return ProfitAll

def statfunc (tf):
    ProfitAll = calcAll(tf)
    tnp = ProfitAll['TotalNetProfit']
    nWin = 0
    nLoss = 0
    for i in range (len(tnp)):
        if ProfitAll['TotalNetProfit'][i] >= 0:
            nWin = nWin + 1
        elif ProfitAll['TotalNetProfit'][i] < 0: 
            nLoss = nLoss + 1
        else: 
            print("there is a null value problem")
                
    WinP = nWin/(nWin+nLoss)
           # print ("winprop function")
            #print (WinP, nWin, nLoss)
    count = len(tnp)
    #print(count)
    avgPl = ProfitAll['TotalNetProfit'].mean()
    stdPl = ProfitAll['TotalNetProfit'].std()
    tstat = math.sqrt(count)*(avgPl/stdPl)
    totalprofit = sum(tnp)
    #print ("above tstat function")
    
    listAll = pd.DataFrame( OrderedDict ( {"tf": [tf], "No. Transactions (net)":
        [count], "net P&L": [totalprofit], "Avg Gain":[avgPl],
        "Prob of win": [WinP],"tstats": [tstat]}))
    listAll.sort_index(inplace = True)

    return listAll  

listAll = pd.DataFrame()
for j in range(20,31,5):
    add = statfunc(j)
    listAll = listAll.append(add)
        #print(add)
print(listAll)

#listAll = statfunc(25)
#print(listAll)

#bad = calcAll(25)
#print(bad)
#print(sum(bad['TotalNetProfit']))


#art = aroon(filenames[0],25)
#print(art)
