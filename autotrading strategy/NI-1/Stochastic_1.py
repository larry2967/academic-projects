"""
Date:   2018-03-06
Author: Christopher
Constraint: Must take a long position first
"""


from __future__ import  division, print_function, unicode_literals,absolute_import
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

filenames=os.listdir('.')
filenames.remove('OF_1.py')
for i in range(len(filenames)):
    filenames[i]= str(filenames[i])
# filenames is a list containing all of the data file names.    


def read_data(filename):
    data = pd.read_csv(filename)
    time=data.iloc[:,0]
    time.rename('Time',inplace=True)
    data.index = pd.to_datetime(time)
    data=data.loc[:,('eB','eA','C','H','L')]
   
    for c in range(len(data)):
        if ((data['eA'][c]) == 0):
            j=c+1
            while (1 <= j <= (len(data)-1)):
                data['eA'][j] != 0
                break
                j+=1
            neweA=float(data['eA'][j])    
            data.iloc[c,1]=neweA
    for d in range(len(data)):
        if ((data['eB'][c]) == 0):
            j=c+1
            while (1 <= j <= (len(data)-1)):
                data['eB'][j] != 0
                break
                j+=1
            neweB=float(data['eB'][j])
            data[c,0]=neweB
    return data, time


def moving_average(x, n, type='simple'):
    
   # compute an n period moving average.
   # type is 'simple' | 'exponential'

    x = np.asarray(x)
    if type == 'simple':
       weights = np.ones(n)
    else:
       weights = np.exp(np.linspace(-1., 0., n))
    weights /= weights.sum()
    np.reshape(x, len(x))
    abc = np.convolve(x, weights, mode='full')[:len(x)]
    abc[:n] = abc[n]
    for i in range(n-1):
        abc[i]=0
    return abc

def stochastic_oscillator(s, n):
    ns = len(s)
    a = np.zeros(ns, dtype=float)
    for i in range(n-1, ns):
       hh = s['H'][i-n+1:i+1].max()
       ll = s['L'][i-n+1:i+1].min()
       a[i] = 100*(s['C'][i]-ll)/(hh-ll)
    return a, ns
def stochastic_oscillator_df(s,n):
    a,ns = stochastic_oscillator(s,n)
    a=pd.DataFrame(a)
    a.index=s.index
    return a,ns
#########################################################################################
# Filter the signals to conform to long-first, and no-open-position before year end 
#########################################################################################

def filter_signals(Trading_signals):

    nss = len(Trading_signals)
   # Assign a value to trade_direction
    trade_direction = np.zeros(nss, dtype=int)
    for i in range(nss):
       if  Trading_signals.Signal[i] == 'Buy':
          trade_direction[i] = 1
       else:
          trade_direction[i] = -1

   # Filter out consecutive sell and buy
    for i in range(nss):
       if trade_direction[i] == -1:
          j = i+1
          while j < nss:
             if trade_direction[j] == 1:
                break
             else:
                trade_direction[j] = 0
             j += 1
       elif trade_direction[i]==1:
           j=i+1
           while j < nss:
               if trade_direction[j]==1:
                   break
               else:
                   trade_direction[j]=0
           j+=1    
    print(trade_direction)
   # Carry out the filtering decisions.
    for i in range(nss):
       if trade_direction[i] == 0:
          Trading_signals.loc[Trading_signals.index[i] ,'Signal'] = Trading_signals.Signal[i][0]           
    return Trading_signals 



#########################################################################################

def trading_signals(filename, n, m):
    

    data, time = read_data(filename)

    data['%K'], ns = stochastic_oscillator_df(data, n)
    data['%D'] = moving_average(data['%K'], m, type='simple')

#   lastdate = str(data.tail(1).index[0])
    data['Signal'] = np.zeros(len(data), dtype = float)

    c = n + m -1
    while data.index[c] < data.index[-1]:

        if data['%K'][c] < 10 and data['%K'][c] < data['%D'][c] and c+1 < ns:
            data.loc[data.index[c] ,'Signal'] = 1

        if data['%K'][c] > 95 and data['%D'][c] > 95 \
            and data['%K'][c] > data['%D'][c] and c+1 < ns:
            data.loc[data.index[c] ,'Signal'] = -1
        c += 1      
  #filter out the signals that make position size increase  
        for h in range(len(data)):
            if data['Signal'][h] == -1:
                j = h+1
                while j < len(data):
                    if data['Signal'][j] == 1:
                        break
                    else:
                        data['Signal'][j] = 0
                    j += 1
            elif data['Signal'][h]==1:
                j = h+1
                while j < len(data):
                    if data['Signal'][j] == -1:
                        break
                    else:
                        data['Signal'][j] = 0
                    j += 1      
    
    
   # Create a DataFrame with trades, including the price at the trade 
    Trading_signals = pd.concat([
         pd.DataFrame({"Price": data.loc[data["Signal"] == 1, "eA"],
                      "Signal": "Buy"}),
         pd.DataFrame({"Price": data.loc[data["Signal"] == -1, "eB"],
                      "Signal": "Sell"}),
        ])

    Trading_signals.sort_index(inplace = True)
    return Trading_signals
   # Implement the risk management strategy 
   # to close out an open position by the end of period.         
    if str(Trading_signals.loc[:,'Signal'][-1])=='Buy':
        if str(Trading_signals['Signal'][0])=='Buy':
            b=pd.DataFrame(data[-1:]['eB'])
            b['Signal']='Sell'
            b.rename(index=str, columns={'eB':'Price'},inplace=True)
            b.index=pd.to_datetime(b.index)
            frames=[Trading_signals,b]
            Trading_signals=pd.concat(frames)
        else:
            Trading_signals=Trading_signals
    elif str(Trading_signals.loc[:,'Signal'][-1])=='Sell':
        if str(Trading_signals['Signal'][0])=='Sell':
            b=pd.DataFrame(data[-1:]['eA'])
            b['Signal']='Buy'
            b.rename(index=str, columns={'eA':'Price'},inplace=True)
            b.index=pd.to_datetime(b.index)
            frames=[Trading_signals,b]
            Trading_signals=pd.concat(frames)
        else:
            Trading_signals=Trading_signals
   
    Full_Trading_signals = filter_signals(Trading_signals)
    return Full_Trading_signals

##########################################################################################

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
for n in range(5,15):
    for m in range(3,6):
        lpnl=[]
        nc=ni=0
        print('-----------',n,m,'------------------')
        for filename in filenames:
            fts=trading_signals(filename,n,m)
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
        PoWW.append(((m,n),round((nc/(nc+ni)),4)))     # prob. of winning 
        PoW.append(round((nc/(nc+ni)),4))
        mn=np.mean(flat_lpnl)
        std=np.std(flat_lpnl)
        nn=len(flat_lpnl)
        tstat=mn*(np.sqrt(nn))/std
        TT.append(((m,n), round(tstat,4)))
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
