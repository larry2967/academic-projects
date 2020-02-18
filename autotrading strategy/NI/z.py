"""
Date:   2018-03-25
Author: Larry Tsai
topic:ATR
"""
from __future__ import  division, print_function, unicode_literals
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import pickle


def save_data():
    filenames=os.listdir('.')
    filenames.sort()
   # filenames.pop()   #this removes the last element 
    for i in range(len(filenames)):
        filenames[i]= str(filenames[i])
# filenames is a list containing all of the data file names.    
    with open("filenames.pickle","wb") as f:
             pickle.dump(filenames, f)
             return filenames
#-----------------------------------------      
save_data()

with open("filenames.pickle","rb") as f:
    filenames = pickle.load(f)
filenames.remove('OF_1.py')

print(filenames)
#-----------------------------------------

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
       

def read_data(filename):
   data = pd.read_csv(filename,index_col=0)
   time=data.iloc[:,0]
   time.rename('Date',inplace=True)
   data.index = pd.to_datetime(time)
   data.index = pd.to_datetime(data.iloc[:,0])
   data=data.loc[:,('H','L', 'C','eA','eB','bB','bA', 'OF')]
   data.index.rename('Time', inplace=True)
   data.index = pd.to_datetime(data.index)

   ##Replacing and removing 0 values from the data 
   
   data = data.replace(0, np.nan)
   data = data.dropna(axis=0, how='any')
   data=data.replace(np.nan,0)
   return data, time


   
   #print(data.tail(40))
   """
   data=data.loc[:,('bB','bA','eB','eA', 'C', 'OF')]
   data.columns = ['bB','bA','eB','eA', 'C', 'OF']
   """
 

#datas, times = read_data(filename)


def ATR(filename, n):
    data,t = read_data(filename) #variable contains all the data 
    #Stock = Stock.loc[: , :] #variable only contains data edate and sdate 
    data['H-L']=data['H']-data['L']
    data['H-PC'] = abs(data['H']- data['C'].shift(1))
    data['L-PC'] = abs(data['L']- data['C'].shift(1))
    data['TR'] = data[['H-L','H-PC','L-PC']].max(axis=1)
    ndf=len(data)
    data['ATR']=np.zeros(ndf)
    for i in range(ndf):
        if i+n-1 < ndf:
            data['ATR'][i+n-1]= (data['TR'][i+n-2]*(n-1)+data['TR'][i+n-1])/n
    return data

#y="NI16M_2016-05-24.csv"
#print(ATR(y,10))


#data, time = read_data(filenames[1])
#print(data.head())

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
    data,b = ATR(filename,n)
    longEma = Long_run_ema(filename, m, data)
  #  print(len(longEma))
    shorEma = Short_run_ema(filename, n, data)
   # print(len(shorEma))
    ns = len(data)
   # print(len(data))
    sig = np.zeros(ns)
  #  print(len(sig))
    #print(comp) 
    for i in range(m-1, ns):
        if longEma[i] < shorEma[i] and b[i] > b[i-5,i]:
            sig[i] = 1
            #print(sig[i])
        elif longEma[i] > shorEma[i]and b[i] > b[i-5,i]:
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
    
    signal1 = pd.concat([
            pd.DataFrame({'Price': data.loc[comp['Signal']==1,'eA'],
                          'Signal':'Buy'}),
            pd.DataFrame({'Price': data.loc[comp['Signal']==-1,'eB'],
                          'Signal':'Sell'})
            ])
    signal1.sort_index(inplace=True)
    
    return signal1, comp, sig


## changing the last signal. If its an open position then sell or buy. 
    # if redundant then remove by making 0 

def full_trading_signals(filename,n,m):
    data =ATR(filename,n)
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
                print (sig[i])
                for j in range(i-1, 0, -1):
                    if sig[j] == -1:
                        counter2 = -1
                        print (sig[j])
                        j = 0
                        break
                    elif sig[j] == 1:
                        counter2= 1
                        print (sig[j])
                        j = 0
                        break
                    elif sig[j] == 0:
                        counter2 =0
                i = 0
                break
            elif sig[i] == 1:
                counter1 = 1
                print (sig[i])
                for k in range(i-1, 0, -1):
                    if sig[k] == -1:
                        counter2 = -1
                        print (sig[k])
                        k = 0
                        break
                    elif sig[k] == 1:
                        counter2= 1
                        print (sig[k])
                        k = 0
                        break
                    elif sig[k] ==0:
                        counter2 = 0 
                i = 0
                break
            elif sig[i] == 0:
                counter1 = 0
        
    print ("countercheck", counter1, counter2)
    
    
    if (counter1 == 1) and (counter2 == 1):
        sig[ns-1] = -1
    elif (counter1 == -1) and (counter2 == -1):
        sig[ns-1] = 1
    else:
        sig[ns-1] = 0
    
    print ("what is changed to", sig[ns-1])
                       
    comp['Signal'] = sig
    signals = pd.concat([
            pd.DataFrame({'Price': data.loc[comp['Signal']==1,'eA'],
                          'Signal':'Buy'}),
            pd.DataFrame({'Price': data.loc[comp['Signal']==-1,'eB'],
                          'Signal':'Sell'})
            ])
    signals.sort_index(inplace=True)
    
    
    #print(lastDataPt.eB)
    #print(lastSignal1pt)
    #print(signal1.tail(2))
    return signals, comp
  

check, check2 = full_trading_signals(filenames[0],3,4) 
print(check)     
print(check2)

#print (check.dtype())
#print (data.dtypes())







"""
ema =Long_run_ema(filenames[0], 2)
print(ema[7])
dataidk = pd.DataFrame({"ema": ema})
print(filenames[0])
print(dataidk['ema'][1])

"""























