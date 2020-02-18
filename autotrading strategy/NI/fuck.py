#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 04:24:55 2018

@author: tsailarry
Created on Tue Mar  6 18:56:20 2018

# explainations 
## my additions 
###### section change 

@author: Shivani Aggarwal 
"""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import pickle 
import os
from collections import OrderedDict

def save_data():
    filenames=os.listdir('.')
    filenames.sort()
    #filenames.pop()   #this removes the last element 
    for i in range(len(filenames)):
        filenames[i]= str(filenames[i])
# filenames is a list containing all of the data file names.    
    with open("filenamesosos.pickle","wb") as f:
             pickle.dump(filenames, f)
             return filenames
#-----------------------------------------      
#save_data()

with open("filenamesosos.pickle","rb") as f:
           filenames = pickle.load(f)
filenames.remove('.DS_Store')

def read_data(ticker):
   fn = ticker + '.csv'
   data = pd.read_csv(fn)
   data.rename(columns = {'Unnamed: 0':'Date'}, inplace = True) #here we have made dates the index 
   return data

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

def stochastic_oscillator(s, n):

   ns = len(s)
   a = np.zeros(ns, dtype=float)
   for i in range(n-1, ns):
      hh = s['H'][i-n+1:i+1].max()
      ll = s['L'][i-n+1:i+1].min()
      a[i] = 100*(s['C'][i]-ll)/(hh-ll)
   return a, ns

######################################################################################### 
"""   
ticker = 'SPY'
sdate, edate = '2011-01-01', '2011-12-31'
n, m = 14, 3
"""

def PandL(ticker, n, m):
    Stock = read_data(ticker) #variable contains all the data 
     #variable only contains data edate and sdate 
    
    Stock['%K'], ns = stochastic_oscillator(Stock, n)
    Stock['%D'] = moving_average(Stock['%K'], m, type='simple')
    
    
    # extract date from tail 1, that is the last record 
    lastdate = str(Stock.tail(1).Date[0]) 
    
   
    Stock['Signal'] = np.zeros(len(Stock), dtype = float) #defining the array, default value is 0  
    c = n + m -1
    
    while Stock.Date[c] < Stock.Date.loc[lastdate]:
       """
       Though the signal is for day c, 
       for the purpose of calculating the P&L later, 
       the signal is ascribed to day c+1
       """
       if Stock['%K'][c] < 10 and Stock['%K'][c] < Stock['%D'][c] and c+1 < ns:

          #print('Buy, %s' % Stock.Date[c+1])
          Stock.loc[Stock.Date[c+1] ,'Signal'] = 1
    
       if Stock['%K'][c] > 95 and Stock['%D'][c] > 95 and \
          Stock['%K'][c] > Stock['%D'][c] and c+1 < ns:
    
          #print('Sell, %s' % Stock.Date[c+1])
          Stock.loc[Stock.Date[c+1] ,'Signal'] = -1
         
       c += 1  
    
    ## set the last day signal to sell irrespective 
    ## even if there is a buy signal on the last day, we dont want to buy 
    Stock.loc[Stock.Date[lastdate] ,'Signal'] = -1
    #print('Sell, %s' % Stock.Date[lastdate])
    #print('check last date signal %s' % Stock.Signal[lastdate])

    
    #print('\n')
    #print(Stock.tail(6))
    #print('\n')

# Create a DataFrame with trades, including the price at the trade 
# Stock_signals in now combining the two signal arrays using a data frame 
    Stock_signals = pd.concat([
            pd.DataFrame({"Price": Stock.loc[Stock["Signal"] == 1, "eA"],
                         "Signal": "Buy"}),
            pd.DataFrame({"Price": Stock.loc[Stock["Signal"] == -1, "eB"],
                         "Signal": "Sell"}),
        ])
    
    Stock_signals.sort_index(inplace = True)
    
    #print(Stock_signals)
#########################################################################################
# Filter the signals to conform to long-first, and no-open-position before year end 
#########################################################################################

# Find the first 'Buy' in Stock_signals
    
    nss = len(Stock_signals)
    #print(nss)
    
    for i in range(nss):
       if Stock_signals.Signal[i] == 'Buy':
          break
       else:
          #this [i][0] command is setting the signal to S (which is the first letter of Sell)
          # we do this cause things with S and B dont get executed 
          Stock_signals.loc[Stock_signals.index[i] ,'Signal'] = Stock_signals.Signal[i][0]
          
          # Disregard the next Buys that occur before the Sell signal
    # so as not to increase the existing (current) Buy positon
    bi = i
    
    for i in range(bi,nss):
       if Stock_signals.Signal[i] == 'Buy':
          for j in range(i+1,nss):
             if Stock_signals.Signal[j] == 'Buy':
                Stock_signals.loc[Stock_signals.index[j] ,'Signal'] = 'B'
             else:
                break
    # Disregard the next Sells that occur before the Buy signal
    # so as not to increase the existing (current) Sell positon
    for i in range(nss):
       if Stock_signals.Signal[i] == 'Sell':
          for j in range(i+1,nss):
             if Stock_signals.Signal[j] == 'Sell':
                Stock_signals.loc[Stock_signals.index[j] ,'Signal'] = 'S'
             else:
                break
    #print(Stock_signals)
    #print('you might wanna delete this table CHECK')
    
    # you are again removing all the S and B from the data and keeping only buy and sell 
    Long_First = pd.concat([
        pd.DataFrame({"Price": Stock_signals.loc[Stock_signals["Signal"] == 'Buy', "Price"],
                     "Signal": "Buy"}),
        pd.DataFrame({"Price": Stock_signals.loc[Stock_signals["Signal"] == 'Sell', "Price"],
                     "Signal": "Sell"}),
    ])

    Long_First.sort_index(inplace = True)
    #print(Long_First)
    #print('you might wanna delete this table CHECK')
    
    #Compute the profitability of long trades
    #Added n and m to keep track of the data might have to delete it tho and add it later in append (SUM,tstats part)
    Stock_long_profits = pd.DataFrame({
            "Price": Long_First.loc[(Long_First["Signal"] == "Buy"), "Price"],
            "Profit": pd.Series(Long_First["Price"] - Long_First["Price"].shift(1)).loc[
                Long_First.loc[(Long_First["Signal"].shift(1) == "Buy") 
                ].index
            ].tolist(),
            "End Date": Long_First["Price"].loc[
            Long_First.loc[(Long_First["Signal"].shift(1) == "Buy") 
            ].index
        ].index
           # "M": m,
           # "N": n
        })

    #print('\n')
    #print(Stock_long_profits)
    #print('\n')
    
    return Stock_long_profits
    
    #total = Stock_long_profits.Profit.sum()
    #print('Total Profit from %s through %s = %0.2f' % (sdate, edate, total))

###########################################################################################################################
    #Running the function in a loop
###########################################################################################################################
 #Run = PandL('AEE', 13, 3, '2011-01-01', '2011-12-31')
   
 
#testList = ['ABT', 'ADBE', 'AET', 'A', 'APD', 'AKAM', 'AMZN', 'AEE', 'AXP', 'AIG', 'AMT', 'AMP', 'ABC', 'AMGN', 'APH', 'ANDV', 'AAPL', 'ADM', 'ARNC', 'AIZ', 'T', 'ADSK', 'ADP', 'AVB', 'AVY', 'BLL', 'BAC', 'BAX', 'BDX', 'BBY', 'HRB', 'BXP', 'BSX','CHRW', 'CA', 'COG', 'CBS', 'CELG', 'CNP', 'CF', 'CI', 'CTAS', 'CSCO', 'C', 'CLX', 'CTSH', 'CAG', 'STZ', 'COST', 'CSX', 'CMI', 'DVA', 'XRAY', 'DVN', 'DFS', 'DOV', 'DPS']


#n = 13
#m = 3
#sdate, edate = '2011-01-01', '2011-12-31'
#nst = len(tickersList)
nst = len(filenames)

print('Number of stocks in the portfolio are %s' % nst)

pW = []
"""
for i in range(nst):
    Tick = tickersList.ticker[i]
    pW.append(Tick)
"""
#print (pW)
#print (len(pW))
    
def portfolioAnalysis (n, m, ):
    
    Allpandl = pd.DataFrame() 

    for i in range(nst):
        for f in filenames:
          data1 = PandL(f[i], n, m )
        #print(data1)
          Allpandl = Allpandl.append(data1, ignore_index=False)
        
    Sno = len(Allpandl)
    
    
    Allpandl['new_index'] = range(1, Sno+1, 1)
    Allpandl.set_index('new_index')
    
    #print(Allpandl.tail())
        
    def WinProb (Allpandl):
            nWin = 0
            nLoss = 0
            for i in range (len(Allpandl.Profit)):
                if Allpandl.Profit[i] >= 0:
                    nWin = nWin + 1
                elif Allpandl.Profit[i] < 0: 
                    nLoss = nLoss + 1
                else: 
                    print("there is a null value problem")
                
            WinP = nWin/(nWin+nLoss)
           # print ("winprop function")
            #print (WinP, nWin, nLoss)
            return WinP
          
    def RtoR (Allpandl): 
        nWin = 0 
        nLoss = 0
        Twin = 0 
        Tloss = 0 
        for i in range (len(Allpandl.Profit)):
            if Allpandl.Profit[i] >= 0:
                nWin = nWin + 1
                Twin = Twin + Allpandl.Profit[i]
            elif Allpandl.Profit[i] < 0: 
                nLoss = nLoss + 1
                Tloss = Tloss + Allpandl.Profit[i]
            else: 
                print("there is a null value problem")
        
        avgWin = Twin/nWin
        avgLoss = abs(Tloss/nLoss)
        rtr = avgWin/avgLoss
        #print ("Rtor function")
        #print (rtr, avgWin, avgLoss)
        return rtr, avgWin, avgLoss
            
    def tStat(Allpandl):
        count = len(Allpandl)
        avgPl = Allpandl.Profit.mean()
        stdPl = Allpandl.Profit.std()
        tstat = math.sqrt(count)*(avgPl/stdPl)
        #print (tstat, count, avgPl, stdPl)
        #print ("above tstat function")
        return tstat    
    
    
    rtr = []
    avgWin = []
    avgLoss = []
    WinP = [WinProb(Allpandl)]
    rtr, avgWin, avgLoss = RtoR(Allpandl)
    tstat = [tStat (Allpandl)]
    totalpl = Allpandl.Profit.sum()
    countT = Allpandl.Profit.count()
        
    listAll = pd.DataFrame( OrderedDict ( {"n": n, "m": m, "No. Transactions":
        countT, "Total P&L": totalpl, "Avg Gain": avgWin, 
        "Avg Loss" : avgLoss, "Prob of win": WinP, 
        "Risk to Return": rtr, "tstats": tstat}))
    listAll.sort_index(inplace = True)

    return listAll


    
listAll = pd.DataFrame()


for n in range(5,15):  
    
    for m in range(3,6):
        
        listM = portfolioAnalysis (n, m)
        print (listM)
        listAll = listAll.append(listM, ignore_index = True)
        listAll.index = listAll.index + 1

listAll.to_pickle('fuckkkkk.pkl')

print (listAll.head(9))

print (listAll)
'''
################## Find max from picke ############### 

df1 = pd.read_pickle('2011_data_final.pkl') #to load 2011_data_final 
print (df1.loc[df1['tstats'].idxmax()])

######################################################
######## for 2012 ####################################

listNew = portfolioAnalysis (12, 4, '2012-01-01', '2012-12-31')
listNew.index = listNew.index + 1
print(listNew)
'''
   

        

