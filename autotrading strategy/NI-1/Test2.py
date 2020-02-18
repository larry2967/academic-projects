# -*- coding: utf-8 -*-
"""
Created on Sat Mar 31 15:51:43 2018
Wrighted movig average 
@author: shivani
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import pickle 
from collections import OrderedDict
#from matplotlib.finance import candlestick_ohlc
import matplotlib.dates as mdates
import os
from pandas import DataFrame
from numpy import nan



def moving_average(x, n, type='simple'):
   # compute an n period moving average.
   # type is 'simple' | 'exponential'

   x = np.asarray(x)
   if type == 'simple':
      weights = np.ones(n)
   else:
      weights = np.exp(np.linspace(-1., 0., n))
   weights /= weights.sum()

   a = np.convolve(x, weights, mode='full')[:len(x)]
   a[:n] = a[n]
   return a



#Saving all the file names as a PICKLE file
# read in all of the file names
#path='C:\Users\shivani\Google Drive\AY4_2\QF\Project\NI'
#filenames=os.listdir('.')
#filenames.pop()   #this removes the last element 
#for i in range(len(filenames)):
    #filenames[i]= str(filenames[i])
# filenames is a list containing all of the data file names.    
#with open("filenames.pickle","wb") as f:
    #pickle.dump(filenames, f)




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
   
   ##Replacing and removing 0 values from the data 
   data = data.replace(0,nan)
   data = data.dropna(axis=0, how='any')
   data=data.replace(nan,0)
   
   #print(data.tail(40))
   """
   data=data.loc[:,('bB','bA','eB','eA', 'C', 'OF')]
   data.columns = ['bB','bA','eB','eA', 'C', 'OF']
   """
 
   return data 


#data = read_data(filenames[1])
#rint(data.head())

#m = the long term period
def Long_run_ema(filename, m , data):
    #ns= len(filename)
    #data, time = read_data(filename)  
    ema = moving_average(data['C'], m, type='exp')
    return ema 

#n = the short term period
def Short_run_ema(filename, n, data):
    #ns= len(filename)
    #data, time = read_data(filename)   
    ema = moving_average(data['C'], n, type='exp')
    return ema 

def Trading_Sig(filename, n, m, data):
    
    longEma = Long_run_ema(filename, m, data)
   # print(len(longEma))
    shorEma = Short_run_ema(filename, n, data)
    
    #print(len(shorEma))
    ns = len(data)
    #print(len(data))
    sig = np.zeros(ns)
  #  print(len(sig))
    #print(comp) 
    for i in range(m-1, ns):
        if longEma[i] < shorEma[i]:
            sig[i] = +1
            #print(sig[i])
        elif longEma[i] > shorEma[i]:
            sig[i] = -1
            #print(sig[i])
        else:
            sig[i] = 0
            #print(sig[i])
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

        
    comp = pd.DataFrame({"LEMA": longEma, "SEMA": shorEma, "Signal": sig})
    comp.index = pd.to_datetime(data.index)
    #might have to change my strategy and accordingly the eA ans eB is I change the signal direction
    signal1 = pd.concat([
            pd.DataFrame({'Price': data.loc[comp['Signal']==+1,'eA'],
                          'Signal':'Buy'}),
            pd.DataFrame({'Price': data.loc[comp['Signal']==-1,'eB'],
                          'Signal':'Sell'})
            ])
    signal1.sort_index(inplace=True)
    #print("this is the count initial")
    #print(signal1)
    return signal1, comp, sig


## changing the last signal. If its an open position then sell or buy. 
    # if redundant then remove by making 0 

def full_trading_signals(filename,n,m):
    data = read_data(filename) 
    signal1,comp, sig =Trading_Sig (filename,n, m, data)
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
    #print (comp)
    #print(signal1)
    #print(lastDataPt.eB)
    #print(lastSignal1pt)
    #print(signals)
    return signals
  
def gross_profits (filename, m, n):
    profits =[]
    signal = full_trading_signals(filename, m, n)
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
    #print(Gross_profits)
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
    nWin = 0
    nLoss = 0
    for i in range (len(netp)):
        if Net_profits['NP&L'][i] >= 0:
            nWin = nWin + 1
        elif Net_profits['NP&L'][i] < 0: 
            nLoss = nLoss + 1
        else: 
            print("there is a null value problem")
                
    WinP = nWin/(nWin+nLoss)
           # print ("winprop function")
            #print (WinP, nWin, nLoss)
    count = len(netp)
    print(count)
    avgPl = Net_profits['NP&L'].mean()
    stdPl = Net_profits['NP&L'].std()
    tstat = math.sqrt(count)*(avgPl/stdPl)
    #print ("above tstat function")
    
    listAll = pd.DataFrame( OrderedDict ( {"m": [m], "n": [n], "No. Transactions (net)":
        [count], "net P&L": [totalprofit], "Avg Gain":[avgPl],
        "Prob of win": [WinP],"tstats": [tstat]}))
    listAll.sort_index(inplace = True)

    return listAll  
    
"""    
check = gross_profits(filenames[0],10,18) 
check3 = net_profits(check)
check4, check5 = stat_func(check3)

print(check, check3) 
print (check4, check5)
"""
listAll = pd.DataFrame()

for i in range (len(filenames)):
    check = gross_profits(filenames[i],10,18) 
    listAll = listAll.append(check)
    print (check)
print(listAll)


"""
    for a in range (4,6):
        for b in range (3,5):
"""     














"""
ema =Long_run_ema(filenames[0], 2)
print(ema[7])
dataidk = pd.DataFrame({"ema": ema})
print(filenames[0])
print(dataidk['ema'][1])

"""





#############RANDOM TEST ###################################
#a, b = read_data(filenames[2])
#print(a.head())
#buy at a and sell at b 
#araa = ['this', 'is', 'mad', 'test', 'why','you', 'do', 'such']
#ns = len(araa)
#for i in range(3, ns):
    #print (araa[i])
"""
    dfd =len(signal1)+1
    print (signal1.iloc[::dfd, :])
    
    if lastDataPt.index == lastSignal1pt.index:
        print ('wooooooorrrkksss')
        if lastSignal1pt['Signal'].item() == 'Buy':
            print('thissss tooo')
            signal1.at[::dfd, ['Signal']] = 'Sell' ##check wth is this row
        else:
            signal1.tail(1)['Signal'] = 'Buy'
    else:
        if signal1.tail(1)['Signal'] == 'Buy':
             a = [lastDataPt.index, lastDataPt.eB, 'Sell']
             signal1.append(a)
        elif signal1.tail(1)['Signal'] == 'Sell':
             b = [lastDataPt.index, lastDataPt.eA, 'Buy']
             signal1.append(b)
"""  
