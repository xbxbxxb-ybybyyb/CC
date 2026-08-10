# -*- coding: utf-8 -*-
"""
Commond Utility to Use
"""


import os 
import pandas as pd
import numpy as np
import copy
import statsmodels.api as sm
#import matplotlib.pyplot as plt 
import scipy.stats as sps
import warnings
import time
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import datetime as dt
#import htsc.quantAPI as QAPI
#from htsc.quantEnum import *
import matplotlib.pyplot as plt
import seaborn as sns


#########################################################################################
"""H5处理相关"""

def MultiIndex2DF(h5_data):
    """
    if input has mulitple columns -> output - dict
    if input has only one column -> output - dataframe
    Input: H5 data: date/stock/[factor list]
    Ouput: Dictionary containing multiple dataframe as matrix format (date*stock)
    
    """
    index_list = h5_data.columns
    if len(index_list)>1:
        data_dict = {}
        for fac in index_list:
            data_dict[fac]= h5_data[fac].unstack()
            #data_dict[fac].columns = [i[1] for i in data_dict[fac]] # remove the extra level
    elif len(index_list)==1:
        data_dict = h5_data[index_list[0]].unstack()
    return data_dict


def DF2MultiIndex(df_dict):
    """pass in dict of df, get df with multi_index"""
    df_mi = pd.DataFrame()
    for df in df_dict:
        df_dict[df] = df_dict[df].reset_index()
        if df_dict[df].columns[0]=='index':
            df_dict[df] = df_dict[df].rename(index=str, columns={"index": "dt"}) 
        df_dict[df]['FactorName'] = df
        df_dict[df] = df_dict[df].set_index(['dt','FactorName'])
        df_mi = df_mi.append(df_dict[df])
    return df_mi




#########################################################################################

    
"""查询停复牌 + 上市日期筛选 """



def get_stock_pool(start_date,end_date,universe_type,output_type='dict',filter_type=None,year_after_listing=None):
    """Input:
             start_date,end_date = 20090101, 20171013
             universe_type = 'risk_universe','alpha_universe','index_50','index_300','index_500','index_800','NA'
             index_type = ''
             year_after_listing(float): unit in year = [0.5,1,3]
             filter_type(str):['stps',['suspend','openuplimit','opendownlimit','sso']
       Output:
           If universe_type=='NA': return complete dataset to slice
           output_type = 'dict'/'dataframe'
                Dictionary: key: date, value: stock_list
                Dataframe(date*stock) matrix of 1,0                 
    """    
    print ('loading data')
    stock_universe = IO.read_data([start_date,end_date],ftype=FType.UNIV,dsource=DSource.OPTM)
    print ('process data')
    
    if universe_type !='NA':
        filter_universe = stock_universe[universe_type].unstack()
     
        """
        if filter_type == 'volume':
            h5_md = IO.read_data([start_date,end_date],['volume'],dsource=DSource.WIND)
            md_dict =  MultiIndex2DF(h5_md)
            finalremain = md_dict>0
            date_list = finalremain.index.tolist()
        """    
        date_list = filter_universe.index.tolist()
        stock_list = np.array(filter_universe.columns.tolist())
        if output_type == 'dict':
            stock_remain = dict()
            for date in date_list:
                stock_remain[date]  = stock_list[filter_universe.loc[date]].tolist()
        if output_type =='dataframe':
            stock_remain = filter_universe
    if universe_type =='NA':    
        stock_remain = stock_universe
    return stock_remain

"""
start_date = 20090101
end_date = 20171013
stock_remain = get_stock_pool(start_date,end_date,universe_type='risk_universe',output_type='dict')
"""

"""

def GetNewsReportDay(stock_list,date_list):
    #output: report_date
    return report_date
"""




#########################################################################################



#########################################################################################
"""因子数据处理部分"""



def Standard_Process(factor_dict,nan_ind,stock_industry,FillNaN=False):
    """
        True： 1. 去除没有收益的日子
        False: 1. 去除没有收益的日子  2. 标准化
    """ 
    print ('#'*20+'  Data Cleaning  '+'#'*20)
    tic = time.time()
    factor_type = FactorTypeCheck(factor_dict)
    if factor_type =='Categorical':  #不进行任何 因子清洗，填充
        print ('           Factor Type: Categorical --> No Standardization and FillingNA')        
    elif factor_type =='Numerical':
        factor_dict[~nan_ind] = np.nan
        factor_dict[~np.isfinite(factor_dict)]=np.nan #将inf,-inf,nan 取代为nan
        print ('           BoxSkewPlot Processing')
        factor_dict = BoxSkewPlot(factor_dict) #极值处理
        print ('           Normalizing')
        factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0) #handle nan
        if FillNaN == True:
            print ('           Filling NaN with Industry Median...')
            factor_dict = Factor_Fillna(factor_dict,stock_industry,nan_ind)
        else:
            print ('           NaN not Filled')
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('#'*20 + '  Done  '+'#'*20)       
    return factor_dict

def DataNormalize(factor_dict):
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)
    return factor_dict


def box_skew_algo(x):
    y = np.array(x)
    x = y[~np.isnan(y)]
    if len(np.unique(x)) < 10:
        return y
    x = np.sort(x)
    md = np.median(x)
    q3 = np.percentile(x,75)
    q1 = np.percentile(x,25)
    iqr = q3 - q1
    rx = np.flip(x, axis=0)
    x, rx = zip(*[(i, j) for i, j in zip(x, rx) if i!=j])
    x = np.split(np.array(x), 2)[1]
    rx = np.split(np.array(rx), 2)[1]
    if len(x) < 5:
        return y
    mc = np.median((x + rx - 2.0 * md) / (x - rx))
    a, b= (3.5, 4) if mc >= 0 else (4, 3.5)
    L = q1 - 1.5 * np.exp(-a * mc) * iqr
    U = q3 + 1.5 * np.exp( b * mc) * iqr
    y[np.array([item < L if not np.isnan(item) else False for item in y])] = L
    y[np.array([item > U if not np.isnan(item) else False for item in y])] = U
    return y

def BoxSkewPlot(pd_raw, axis=1):
    if type(pd_raw) == pd.DataFrame:
        # Return copy instead of original
        pd_process = pd_raw.copy()
        return pd_process.apply(box_skew_algo, axis=axis)
    else:
        raise AssertionError 
        
    
def Factor_Fillna(factor_dict,stock_industry,nan_ind):
    """ 缺失值处理：
    得到新的因子暴露度序列后，将因子暴露度缺失的地方设为行业中位数。
    # 因子暴露度缺失定义为无法获取此因子 而非该股票不可交易  - 用处理过的因子填充
    # nan_ind 为股票停牌信息  1 为真停牌 或者没上市/ 则不填充
    
    """
    fill_ind = np.isnan(factor_dict)[~nan_ind] # 所有NAN * 非停牌的NAN = 缺失数据
    industry_median = pd.DataFrame(index=factor_dict.index,columns=[i for i in range(32)])
    for date in stock_industry.index:
        industry_list = stock_industry.loc[date]
        industry_median.loc[date] = [i[0] for i in pd.DataFrame(factor_dict.loc[date]).groupby(industry_list).median().values]
    Fill_median = copy.deepcopy(factor_dict)
    for i in set(industry_list):    # loop industry
        stock_in_industry  = industry_list[industry_list==i].index.tolist()
        Fill_median[stock_in_industry] = pd.DataFrame([industry_median[i].tolist()]*len(stock_in_industry)).T
    factor_dict[fill_ind==1]  =  Fill_median[fill_ind==1]    
    return factor_dict      

def Factor_Fillna_TS(factor_dict,holding_peiord):
    """如果数据不齐，则往回看多少天区间 取均值
       用于稀疏的财报数据矩阵
    """
    factor_fill = factor_dict.rolling(window=holding_peiord,min_periods=1).mean()
    return factor_fill

#########################################################################################
def weight_decay(half_life,total_len):  #其中n是半衰期，m是序列长度
    return [0.5**((total_len-i)/half_life) for i in range(total_len)]

#########################################################################################

