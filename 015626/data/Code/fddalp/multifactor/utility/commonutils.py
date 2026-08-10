# -*- coding: utf-8 -*-
import os
from IO import IO, IO_enums
import pandas as pd

def name2value(fwdNames):
 # fwd name seems like fwd_Ret_Daily_5, bwd_Ret_Daily_5    
    valueDict = {'fwd':[],'var':[],'freq':[],'value':[]}
    for fwdName in fwdNames:
        fwdList = fwdName.split('_')
        valueDict['fwd'] = valueDict['fwd'] + [fwdList[0]]
        valueDict['var'] = valueDict['var'] + [fwdList[1]]
        valueDict['freq'] = valueDict['freq'] + [fwdList[2]]
        if fwdList[0] == 'fwd':
            valueDict['value'] = valueDict['value'] + [int(fwdList[3])]
        else:
            valueDict['value'] = valueDict['value'] + [-int(fwdList[3])]
                
    return valueDict

def value2name(period, var = 'Ret', freq = 'Daily'):
    fwdNames = []
    for p in period:
        if p >= 0:
            fwdNames = fwdNames + ['_'.join(['fwd',var,freq,str(p)])]
        else:
            fwdNames = fwdNames + ['_'.join(['bwd',var,freq,str(-p)])]
    
    return fwdNames
"""
def MultiIndex2DF(data):
    colNames = data.columns
    df = {}
    for col in colNames:
        df[col] = data[col].unstack()
    return df


def get_fwdret(stDate, edDate, n):
    data = IO.read_data([stDate, edDate], columns = ['close','adjfactor'])
    df = MultiIndex2DF(data)
    
    closePrice = df['close']
    adjFactor = df['adjfactor']
    
    if n > 0:
        closePrice_n = closePrice.shift(-n)
        adjFactor_n = adjFactor.shift(-n)
    else:
        closePrice_n = closePrice.shift(n)
        adjFactor_n = adjFactor.shift(n)
    
    fwd = (closePrice_n*adjFactor_n)/(closePrice*adjFactor)-1
    
    if n >=0:
        colName = '_'.join(['fwd','Ret','Daily',str(n)])
    else:
        colName = '_'.join(['bwd','Ret','Daily',str(-n)])
        
    mdf = pd.DataFrame(fwd.stack(),columns = [colName])
    mdf = mdf.dropna(axis = 0, how = 'all')
    if n > 0:
        filePath = os.path.join('S:/Quant/data','fwd'+str(n),'CHINA_STOCK','DAILY','WIND')
    else:
        filePath = os.path.join('S:/Quant/data','bwd'+str(-n),'CHINA_STOCK','DAILY','WIND')
    
    if not os.path.exists(filePath):
        os.makedirs(filePath)
    if n > 0:
        fileName = os.path.join(filePath, 'FWD'+str(n)+'_CHINA_STOCK_DAILY_WIND.h5')
    else:
        fileName = os.path.join(filePath, 'BWD'+str(-n)+'_CHINA_STOCK_DAILY_WIND.h5')
            
#    import pdb;pdb.set_trace()
    if n > 0:
        IO.pd_hdf5_writer(mdf, fileName, 'fwd' + str(n), append = True)
    else:
        IO.pd_hdf5_writer(mdf, fileName, 'bwd' + str(-n), append = True)
        
    return mdf

"""
    


