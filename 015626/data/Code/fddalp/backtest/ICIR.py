#历史ICIR半衰期加权组合因子

from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.backtest import CommonUtility
from multifactor.backtest import FactorTest
import os
from multifactor.utility import dt
import numpy as np
import copy
import pandas as pd


def calcIC(factor, returnData, holding_period,trading_dates):
    ICs = pd.DataFrame()
    for i in range(holding_period, len(trading_dates)):
        factorSample = factor.loc[trading_dates[i - holding_period]]
        returnSample = returnData.loc[trading_dates[(i - holding_period):(i - 1)].values]
        returnMat = returnSample.unstack()
        returnMat = 1 + (returnMat / 100)
        cumReturn = returnMat.prod(axis=0)
        # stocks = list(set(h5_data.loc[].index.get_level_values(level=1)))
        stocks = list(set(cumReturn.index.get_level_values(level=1)).intersection(set(factorSample.index.values)))
        sample = pd.concat([cumReturn.loc['pct_chg'].loc[stocks], factorSample.loc[stocks]], axis=1)

        sampleAvailable = sample.dropna(axis=0)
        if sampleAvailable.shape[0] < 5:
            ic = float('nan')
            ICRow = pd.DataFrame([ic])
            ICRow.index = [trading_dates[i]]
            ICs = pd.concat([ICs, ICRow], axis=0)
            continue
        ic = sampleAvailable.corr('spearman').iat[0, 1]
        # ICs.append(ic)
        ICRow = pd.DataFrame([ic])
        ICRow.index = [trading_dates[i]]
        ICs = pd.concat([ICs, ICRow], axis=0)
        # data_dict = MultiIndex2DF(h5_data)
    return ICs

def calcICIR(res_name,factor_path=None,factor_data=None,start_date='20170106',end_date='20170901',holding_period=20,histroy_length=60):
    #import datetime.datetime as datetime
    if(pd.isnull(factor_path)):
       factor_path='S:/Quant/data/factor/jlhForTest4'
    os.chdir(factor_path)
    factor_file_list = os.listdir(factor_path)
    #factor_list = [fac.replace(".h5","") for fac in factor_file_list]
    #start_date='20170106'
    #end_date='20170901'
    trading_dates=dt.get_trading_date_range(start_date, end_date)
    if factor_data is not None:
        trading_dates=factor_data.index.get_level_values(level=0).drop_duplicates()
    start_date=trading_dates[0]
    end_date=trading_dates[-1]
    #holding_period=20
    #histroy_length=60
    index_list =['pct_chg']
    h5_data = IO.read_data([start_date,end_date], index_list, ftype=FType.MD, dsource=DSource.OPTM)
    #stocks = list(set(h5_data.index.get_level_values(level=1)))
    #data_dict = CommonUtility.MultiIndex2DF(h5_data)
    #计算历史IC序列并keep

    factorICDF=pd.DataFrame()
    if factor_data is not None:
        allFactors = factor_data
        factor_file_list=allFactors.columns.values
    else:
        allFactors=pd.DataFrame()
    for factorFileName in factor_file_list:
        if factor_data is None:
            factor_dict = IO.read_data([start_date, end_date], alt=factorFileName)
            allFactors=pd.concat([allFactors,factor_dict],axis=1)
        else:
            factor_dict=allFactors.loc[:,factorFileName]
        factorIC=calcIC(factor_dict,h5_data,holding_period,trading_dates)
        factorICDF=pd.concat([factorICDF,factorIC],axis=1)
    print('end')
    factorICIR=pd.DataFrame()
    for i in range(histroy_length,factorICDF.shape[0]):
        factorICSample=factorICDF.iloc[(i-histroy_length):i,:]
        factorICstd=factorICSample.std(axis=0)
        factorICmean=factorICSample.mean(axis=0)
        factorRowICIR=pd.DataFrame(factorICmean/factorICstd).T
        factorRowICIR.index = [factorICDF.index[i]]
        factorICIR=pd.concat([factorICIR,factorRowICIR],axis=0)
        #tradingDay=factorICDF.index[i]
    print('end')
    factorRes=pd.DataFrame()
    factorICIR=factorICIR.fillna(0)
    for i in range(factorICIR.shape[0]):
        factorSample=allFactors.loc[factorICIR.index[i]]
        ICIRcoff=factorICIR.iloc[i,:]
        factorIntge=pd.DataFrame(np.dot(factorSample,ICIRcoff)).T
        factorIntge.columns=[factorSample.index]
        factorIntge.index=[factorICIR.index[i]]
        factorRes=pd.concat([factorRes,factorIntge],axis=0)
    print('end')
    # factorResDict=factorRes.unstack()
    factorResDict=factorRes.stack(level=0)
    factorResDict=pd.DataFrame(factorResDict)
    factorResDict.columns=['multiAlpha0']
    factorResDict.index.names=['dt','Ticker']
    #factorResDict=factorResDict.rename_axis('dt', axis=1)
    # factorResDict=factorResDict.reset_index()
    # factorResDict=factorResDict.rename(index=str,columns={'level_1':'dt'})
    # factorResDict=factorResDict.set_index(['dt','Ticker'])
    # factorResDict=factorResDict.sort_index(level=0)
    # factorResDict=factorResDict.rename(index=str,columns={0:'multiAlpha0'})
    #IO.pd_hdf5_writer(factorResDict,hdf5='jlhMultiAlphaTest_0.h5',dataset='multiAlpha0')
    #IO.pd_hdf5_writer(factorResDict, hdf5=res_name+'.h5', dataset=res_name)
    return factorResDict

