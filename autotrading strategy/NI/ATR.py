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

ticker='NI16M_2016-05-24'

def save_data():
    filenames=os.listdir('.')
    filenames.pop()   #this removes the last element 
    for i in range(len(filenames)):
        filenames[i]= str(filenames[i])
# filenames is a list containing all of the data file names.    
    with open("filenames.pickle","wb") as f:
        pickle.dump(filenames, f)

    return filenames

save_data()
"""
with open("filenames.pickle","rb") as f:
            filenames = pickle.load(f)
 """
       
print(filenames)


    
def read_data(ticker):
   datadir ='NI/'
   fn = datadir + ticker + '.csv'
   data=pd.read_csv(fn)
   
   
   return data


def ATR(df,n):
    df['H-L']=df['H']-df['L']
    df['H-PC']=abs(df['H']- df['C'].shift(1))
    df['L-PC']=abs(df['L']- df['C'].shift(1))
    df['TR']=df[['H-L','H-PC','L-PC']].max(axis=1)
    ndf=len(df)
    i=0
    a = np.zeros(ndf, dtype=float)
    for i in range(0,ndf):
        if i+n-1 < ndf:
         df.loc[i+n-1,'ATR']=(df.loc[i:i+n-1,'TR'].sum())/n
         a[i]=df.ATR[i]
    return a,ndf

read_data(ticker)
ATR(data,4)

-----------------------------------

def PandL(ticker, n, m):
    Stock = read_data(ticker) #variable contains all the data 
    Stock = Stock.loc[sdate:edate, :] #variable only contains data edate and sdate 
    
    Stock['ATR'], ns = ATR(Stock, n)
    
    
    
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
            pd.DataFrame({"Price": Stock.loc[Stock["Signal"] == 1, "Close"],
                         "Signal": "Buy"}),
            pd.DataFrame({"Price": Stock.loc[Stock["Signal"] == -1, "Close"],
                         "Signal": "Sell"}),
        ])
    
    Stock_signals.sort_index(inplace = True)
    
    #print(Stock_signals)
        
    


df=read_data(ticker)
ATR(df,14)
print(df)
