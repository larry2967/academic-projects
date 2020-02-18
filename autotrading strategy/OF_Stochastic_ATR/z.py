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
    filenames.pop()   #this removes the last element 
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

def moving_average(x, n, type='exp'):
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
   data = pd.read_csv(filename)
   time=data.iloc[:,0]
   time.rename('Time',inplace=True)
   data.index = pd.to_datetime(time)
   data=data.loc[:,('eB','eA','O','C','V','H','L')]
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


def ATR(filename):
    data,t = read_data(filename) #variable contains all the data 
    #Stock = Stock.loc[: , :] #variable only contains data edate and sdate 
    data['H-L']=data['H']-data['L']
    data['H-PC'] = abs(data['H']- data['C'].shift(1))
    data['L-PC'] = abs(data['L']- data['C'].shift(1))
    data['TR'] = data[['H-L','H-PC','L-PC']].max(axis=1)
    ndf=len(data)
    data['ATR']=np.zeros(ndf)
    for i in range(ndf):
        if i+14-1 < ndf:
            data['ATR'][i+14-1]= (data['TR'][i+14-2]*(14-1)+data['TR'][i+14-1])/14
    data.index=data.index
    return data

#y="NI16M_2016-05-24.csv"
#print(ATR(y,10))


#data, time = read_data(filenames[1])
#print(data.head())

#m = the long term period
def Long_run_ema(filename,m, data):
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

def Trading_Sig(filename, n, m, data):   # n>=14, m>n  
    data = ATR(filename)
    longEma = Long_run_ema(filename, m, data)
  #  print(len(longEma))
    shorEma = Short_run_ema(filename, n, data)
   # print(len(shorEma))
    ns = len(data)
   # print(len(data))
    sig = np.zeros(ns)
  #  print(len(sig))
    #print(comp) 
    b=data['ATR']
   
    for i in range(m-1+5, ns):
        if longEma[i] < shorEma[i]:  # compare it with those of within 5 days look-back period
            past1=0
            past=[]
            for g in range(1,6):
                past.append(abs(b[i-g]))
            for h in range(len(past)):
                if b[i]>past[h]:
                    past1+=1
            if past1==5:
                sig[i] = 1
            else:
                sig[i] = 0
            #print(sig[i])
        elif longEma[i] > shorEma[i]:
            past1=0
            past=[]
            for g in range(1,6):
                past.append(abs(b[i-g]))
            for h in range(len(past)):
                if b[i]>past[h]:
                    past1+=1
            if past1==5:
                sig[i] = -1
            else:
                sig[i] = 0    
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
            pd.DataFrame({'Price': data.loc[comp['Signal']==-1,'eB'],  # WHEN 1, SELL!!!!!
                          'Signal':'Sell'})
           ])
    signal1.sort_index(inplace=True)
    
    return signal1, comp, sig


## changing the last signal. If its an open position then sell or buy. 
    # if redundant then remove by making 0 

def full_trading_signals(filename,n,m):
    data =ATR(filename)
    signal1,comp,sig=Trading_Sig(filename,n, m, data)
    if str(signal1.loc[:,'Signal'][-1])=='Buy':
        if str(signal1['Signal'][0])=='Buy':
            b=pd.DataFrame(data[-1:]['eB'])
            b['Signal']='Sell'
            b.rename(index=str, columns={'eB':'Price'},inplace=True)
            b.index=pd.to_datetime(b.index)
            frames=[signal1,b]
            Full_Trading_signals=pd.concat(frames)
        else:
            Full_Trading_signals=signal1
    elif str(signal1.loc[:,'Signal'][-1])=='Sell':
        if str(signal1['Signal'][0])=='Sell':
            b=pd.DataFrame(data[-1:]['eA'])
            b['Signal']='Buy'
            b.rename(index=str, columns={'eA':'Price'},inplace=True)
            b.index=pd.to_datetime(b.index)
            frames=[signal1,b]
            Full_Trading_signals=pd.concat(frames)
        else:
            Full_Trading_signals=signal1
    return Full_Trading_signals

#    comp['Signal'] = sig
#    signals = pd.concat([
#            pd.DataFrame({'Price': data.loc[comp['Signal']==1,'eA'],
 #                         'Signal':'Buy'}),
  #          pd.DataFrame({'Price': data.loc[comp['Signal']==-1,'eB'],
   #                       'Signal':'Sell'})
   #         ])
   # signals.sort_index(inplace=True)
    
    
    #print(lastDataPt.eB)
    #print(lastSignal1pt)
    #print(signal1.tail(2))
   # return signals, comp
  

#check, check2 = full_trading_signals(filenames[0],3,4) 
#print(check)     
#print(check2)

#print (check.dtype())
#print (data.dtypes())

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


"""
ema =Long_run_ema(filenames[0], 2)
print(ema[7])
dataidk = pd.DataFrame({"ema": ema})
print(filenames[0])
print(dataidk['ema'][1])

"""























