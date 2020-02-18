#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  1 01:23:12 2018

@author: tsailarry

Date:   2018-03-15
Author: Christopher
Constraint: Must take a long position first
"""

from __future__ import division, print_function, unicode_literals

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
import pickle


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

#print(filenames)

def read_data(filename):
   data = pd.read_csv(filename)
   #time=data.iloc[:,0]
   #time.rename('Date',inplace=True)
   #data.index = pd.to_datetime(time)
   #data.index.name='Date'
   #data.index = pd.to_datetime(data.iloc[:,0])
   data.rename(columns = {'Unnamed: 0':'Date'}, inplace = True)
   
   
   data=data.loc[:,('Date','H','L', 'C')]
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
# Filter the signals to conform to long-first, and no-open-position before year end 
#########################################################################################

def filter_signals(Stock_signals):

   nss = len(Stock_signals)

   # Assign a value to trade_direction
   flag =  0
   trade_direction = np.zeros(nss, dtype=int)
   for i in range(nss):
      if  Stock_signals.Signal[i] == 'Buy':
         trade_direction[i] = 1
      else:
         trade_direction[i] = -1

  

   # Set the first sell signal to 0
   for i in range(nss):
      if trade_direction[i] == -1:
         trade_direction[i] = 0
      else:
         break
          
   # Filter out consecutive sell 
   for i in range(nss):
      if trade_direction[i] == -1:
         j = i+1
         while j < nss:
            if trade_direction[j] == 1:
               break
            else:
               trade_direction[j] = 0
            j += 1
         
   #print(trade_direction)

   # Carry out the filtering decisions.
   for i in range(nss):
      if trade_direction[i] == 0:
         Stock_signals.loc[Stock_signals.index[i] ,'Signal'] = Stock_signals.Signal[i][0]

   return Stock_signals 

#########################################################################################
# Compute the P&L 
#########################################################################################

def cal_PandL (Stock_signals):

   Long_First = pd.concat([
      pd.DataFrame({"Price": Stock_signals.loc[Stock_signals["Signal"] == 'Buy', "Price"],
                   "Signal": "Buy"}),
      pd.DataFrame({"Price": Stock_signals.loc[Stock_signals["Signal"] == 'Sell', "Price"],
                     "Signal": "Sell"}),
      ])

   Long_First.sort_index(inplace = True)

   # Compute the profitability of long trades
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
    })


   return Stock_long_profits

#########################################################################################

def trading_signals(filename, n, m):

   Stock = read_data(filename)

   Stock['%K'], ns = stochastic_oscillator(Stock, n)
   Stock['%D'] = moving_average(Stock['%K'], m, type='simple')

   lastdate = str(Stock.tail(1).Date[0])
   Stock['Signal'] = np.zeros(len(Stock), dtype = float)

   c = n + m -1
   while Stock.Date[c] < Stock.Date.loc[lastdate]:
      """
      Though the signal is for day c, for the purpose of calculating the P&L later, 
      the signal is ascribed to day c+1
      """
      if Stock['%K'][c] < 10 and Stock['%K'][c] < Stock['%D'][c] and c+1 < ns:
         Stock.loc[Stock.Date[c+1] ,'Signal'] = 1

      if Stock['%K'][c] > 95 and Stock['%D'][c] > 95 \
         and Stock['%K'][c] > Stock['%D'][c] and c+1 < ns:
         Stock.loc[Stock.Date[c+1] ,'Signal'] = -1
     
      c += 1      

   # Create a DataFrame with trades, including the price at the trade 
   Stock_signals = pd.concat([
        pd.DataFrame({"Price": Stock.loc[Stock["Signal"] == 1, "C"],
                     "Signal": "Buy"}),
        pd.DataFrame({"Price": Stock.loc[Stock["Signal"] == -1, "C"],
                     "Signal": "Sell"}),
       ])

   Stock_signals.sort_index(inplace = True)

   # Implement the risk management strategy 
   # to close out an open position by the end of period.
   last_day = Stock.index[-1]
   last_price = Stock.C[-1]
   if Stock_signals.index[-1] < last_day:
      df = pd.DataFrame(data = {'Price': [last_price], 'Signal':['Sell']}, \
                                index = [last_day])
      Stock_signals = Stock_signals.append(df)

   # It could be the signal of the last sample day is a buy
   if Stock_signals.Signal[-1] == 'Buy':
      Stock_signals.loc[Stock_signals.index[-1] ,'Signal'] = 'Sell'

   Stock_signals = filter_signals(Stock_signals)

   return Stock_signals

##########################################################################################

def process_results(A):
   n = len(A) 
   Mn = np.mean(A)          # Average P&L
   Sn = np.std(A, ddof=1)   # Unbiased Standard Deviation of P&L 
   t = np.sqrt(n) * Mn/Sn   # t stat

   Nc, Ni, AAc, AAi, = 0, 0, 0, 0
   for i in range(n):
      if A[i] > 0:          # Correct signal
         Nc += 1
         AAc += A[i]
      else:
         Ni += 1
         AAi += -A[i]
        
   Ac, Ai = AAc/Nc, AAi/Ni
   p = Nc/n                # Probability of correct signal (win)
   r = Ac/Ai               # Reward-to-risk ratio

   return n, p, r, t


#########################################################################################


print('Back-testing has started. It may take a few minutes to see the first print.')

""" Obtain the list of csv data files from datadir, which is a global variable """ 

samples = [f for f in filenames ]
nsamples = len(samples)

""" Write the results to a file  """
fileoutput = 'outcome'+ '_' + '.csv'
fd = open(fileoutput, 'w')
fd.write('n,m,Number of Trades,Total PL,Probability of Win,Reward-to-Risk Ratio,t stat\n')


for n in range(5,14+1):
   for m in range(3,5+1):
      #if m >= n:
         #continue
      A = []
      for i in range(nsamples):
          filename = samples[i]
          #filename = filename.replace('.csv', '')
          #print(n, m, filename)
          Stock_signals = trading_signals(filename, n, m)
          result =  cal_PandL (Stock_signals)
          profit = result.Profit.values
          num = len(profit)
          for j in range(num):
             A.append(profit[j])
      
      N, p, r, t = process_results(A)
      print('(%d %d), N=%d, total=%0.2f, p=%0.2f, r=%0.2f, t=%0.2f' 
            % (n, m, N, np.sum(A), p*100, r, t))
      s  = '%d,%d,%d,%0.2f,%0.2f,%0.2f,%0.2f\n' % (n, m, N, np.sum(A), p*100, r, t)
      fd.write(s)

fd.close()


