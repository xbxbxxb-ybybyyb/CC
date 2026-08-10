# -*- coding: utf-8 -*-
"""
@author: ZSJ
   
Use Example

#传入factor_dict 进行单因子检测
start_date,end_date = 20090101,20180109
mkt_file='Q:\DATA\HDF5DATA\ev\CHINA_STOCK\DAILY\HTSC\EV_CHINA_STOCK_DAILY_HTSC.h5'
h5_md = IO.read_data([start_date,end_date],['mkt_cap_ard'],alt=mkt_file)
mkt_cap = h5_md['mkt_cap_ard'].unstack()
factor_dict = mkt_cap.copy()
factor_dict = DataNormalize(factor_dict)
factor_name = 'mkt_cap'
FactorEntryTest(factor_dict,holding_period,factor_name)

"""

import os 
import pandas as pd
import numpy as np
import copy
import statsmodels.api as sm
import scipy.stats as sps
import time
from IO import IO
from IO.IO_enums import *
import datetime as dt
from functools import reduce
#from .ReportGenerator import GeneratePdf 
from backtest.ReportGenerator import GeneratePdf



def align_data(data_dict):
    i=0
    #dat_type = [type(data_dict[factor])for factor in data_dict]
    # get stock list, date list    
    for factor in data_dict:
        if type(data_dict[factor])==pd.DataFrame:
            if i==0:
                stock_list = data_dict[factor].columns.tolist()
                date_list = data_dict[factor].index.tolist()
                i=i+1
            else:
                stock_list = np.intersect1d(stock_list,data_dict[factor].columns.tolist())
                date_list = np.intersect1d(date_list,data_dict[factor].index.tolist())
        elif type(data_dict[factor]) ==pd.Series:
            if i==0:
                date_list = data_dict[factor].index.tolist()
                i=i+1
            else:
                date_list = np.intersect1d(date_list,data_dict[factor].index.tolist())
        elif type(data_dict[factor]) == dict:
            for fac in data_dict[factor]:
                if type(data_dict[factor][fac]) == pd.DataFrame:
                    if i==0:
                        stock_list = data_dict[factor][fac].columns.tolist()
                        date_list = data_dict[factor][fac].index.tolist()
                        i = i+1
                    else:
                        stock_list = np.intersect1d(stock_list,data_dict[factor][fac].columns.tolist())
                        date_list = np.intersect1d(date_list,data_dict[factor][fac].index.tolist())                    
    # align dataframe and series
    data_dict_aligned = {}
    for factor in data_dict:
        #print (factor)
        if type(data_dict[factor])==pd.DataFrame:
            data_dict_aligned[factor] = data_dict[factor][stock_list].loc[date_list]
        elif  type(data_dict[factor]) ==pd.Series:
            data_dict_aligned[factor] = data_dict[factor].loc[date_list]
        elif type(data_dict[factor])== dict:
            data_dict_aligned[factor] = {}
            for fac in data_dict[factor]:
                if type(data_dict[factor][fac])==pd.DataFrame:
                    data_dict_aligned[factor][fac] = data_dict[factor][fac][stock_list].loc[date_list]
                    
                else:
                    data_dict_aligned[factor][fac] = data_dict[factor][fac]
    return data_dict_aligned




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
        fac = index_list[0]
        data_dict = h5_data[fac].unstack()
    return data_dict

def DF2MultiIndex(df_dict):
    """pass in dict of df, get df with multi_index"""
    df_mi = pd.DataFrame()
    for df in df_dict:
        df_dict[df].columns = df_dict[df].columns.astype('object') # as categorical index cannot be extended
        df_dict[df] = df_dict[df].reset_index()
        if df_dict[df].columns[0]=='index':
            df_dict[df] = df_dict[df].rename(index=str, columns={"index": "dt"}) 
        df_dict[df]['FactorName'] = df
        df_dict[df] = df_dict[df].set_index(['dt','FactorName'])
        df_mi = df_mi.append(df_dict[df])
    return df_mi




def load_data(factor_dict,holding_period,benchmark_index='zz500',easy_test=False,test_universe=None):  
    """
    index_lookup = {'zz500': '000905.SH', 'zz800': '000906.SH', 'sz50': '000016.SH', 'hs300': '000300.SH'}
    style_list = ['EarningsYield','Value','Liquidity','NonLinearSize','Volatility','Size','Momentum','Beta','Leverage']
    test_universe = ['index_50','index_300','index_500','risk_universe','alpha_universe']
    """
    tic = time.time()
    print ('-'*5+'  Loading data  '+'-'*5)
    if type(factor_dict)==pd.Series:
        factor_dict = pd.DataFrame(factor_dict)
        factor_dict.columns = ['dummy']
        factor_dict = factor_dict.unstack()['dummy'] if len(factor_dict.columns)==1 else factor_dict
    
    if len(factor_dict.columns)==1:
        factor_dict = factor_dict.unstack()[factor_dict.columns.tolist()[0]]            
    #if len(factor_dict.columns)==1:
    #    factor_dict = MultiIndex2DF(factor_dict)

    ### factor data
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0).tolist()

    start_date,end_date = factor_dict.index[0],factor_dict.index[-1]
    prev_start_date = fdate_list_dt[max(fdate_list_dt.index(start_date)-1,0)]
    stock_list_factor = factor_dict.columns.tolist()
    date_list_factor = factor_dict.index.tolist()  
    

    ### market data 
    print('Getting return data')
    h5_md = IO.read_data([prev_start_date,end_date],['close','adjfactor'],ftype=FType.MD,dsource=DSource.WIND,max_workers=1)
    md_dict =  MultiIndex2DF(h5_md)
    md_dict['close_adj'] = md_dict['close']*md_dict['adjfactor']
    return_df = md_dict['close_adj']/md_dict['close_adj'].shift(1)-1
    date_list_md = return_df.index.tolist()
    stock_list_md = return_df.columns.tolist()
    holding_period_ret = md_dict['close_adj'].shift(-1*holding_period)/md_dict['close_adj']-1# next 10 days return 
    
    # Benchmark data    
    print('Getting benchmark data')
    h5_index = IO.read_data([prev_start_date,end_date],['close'],ftype=FType.MD,dtype=DType.INDEX,dsource=DSource.WIND,max_workers=1)
    index_lookup = {'zz500': '000905.SH', 'zz800': '000906.SH', 'sz50': '000016.SH', 'hs300': '000300.SH'}
    bmk_price =  (h5_index.unstack()['close'])[index_lookup[benchmark_index]]
    benchmark_ret = bmk_price/bmk_price.shift(1)-1
    date_list_index = benchmark_ret.index.tolist()

    # SSO List
    print('Getting stock filter data') #!check runtime
    
    h5_filter = IO.read_data([start_date,end_date],ftype=FType.UNIV,dsource=DSource.OPTM,max_workers=1)
    universe_name = 'filter_sso'
    stock_filter= h5_filter[h5_filter[universe_name]][universe_name].unstack()
    stock_filter = stock_filter.fillna(value=False)
    
    
    if test_universe in ['index_50','index_300','index_500','risk_universe','alpha_universe']:
        print ('Getting universe data: '+test_universe.lower())
        test_filter = h5_filter[h5_filter[test_universe]][test_universe].unstack()
        test_filter = test_filter.fillna(value=False)
        temp_stock_list = np.intersect1d(stock_filter.columns,test_filter.columns)
        stock_filter = (stock_filter[temp_stock_list]==True) & (test_filter[temp_stock_list]==True)
        stock_filter = stock_filter.fillna(value=False)
        
    date_list_filter = stock_filter.index.tolist()
    stock_list_filter = stock_filter.columns.tolist()

    if easy_test==False:
        print('Getting style factor and industry data')
        #style_list = ['EarningsYield','Value','Liquidity','NonLinearSize','Volatility','Size','Momentum','Beta','Leverage']
        style_risk = IO.read_data([start_date,end_date],columns=['Size','Industry'],dsource=DSource.STYLEFACTOR,ftype=FType.RISK,max_workers=1)
        StyleFactorDict = {}
        style_name = 'Size'
        StyleFactorDict[style_name] = style_risk[style_name].unstack()
        date_list_style = StyleFactorDict[style_name].index.tolist()
        stock_list_style = StyleFactorDict[style_name].columns.tolist()
        
        stock_industry = style_risk['Industry'].unstack()
        date_list_industry = stock_industry.index.tolist()
        stock_list_industry = stock_industry.columns.tolist()        
        stock_list = reduce(np.intersect1d,(stock_list_factor,stock_list_md,stock_list_filter,stock_list_style,stock_list_industry)).tolist()
        date_list = reduce(np.intersect1d,(date_list_factor,date_list_md,date_list_filter,date_list_style,date_list_industry,date_list_index)).tolist()
    
    else:
        stock_list = reduce(np.intersect1d,(stock_list_factor,stock_list_md,stock_list_filter)).tolist()
        date_list = reduce(np.intersect1d,(date_list_factor,date_list_md,date_list_filter,date_list_index)).tolist()
        
    stock_list.sort()
    date_list.sort()  
    
    print ('Check Stock List & Date List...')
    stock_new_list = list(set(stock_list_factor).difference(set(stock_list_md)))
    stock_new_list.sort()    
    date_new_list = list(set(date_list_factor).difference(set(date_list_md)))
    date_new_list.sort()
    
    # print absent stock list and date list    
    if len(stock_new_list)>0:
        print ('No data for following stock:' + '\n' + str(stock_new_list))
        print ('Count:'+str(len(stock_list)))
    else:
        print ('Stock Universe Complete - Count:'+str(len(stock_list)))
        
    if len(date_new_list)>0:
        print ('No data for following date:' + '\n' + str(date_new_list))
        print ('Count:'+str(len(date_list)))        
    else:
        print ('Date Universe Complete - Count:'+str(len(date_list)))        

    stock_filter = stock_filter[stock_list].loc[date_list]
    nan_ind = stock_filter

    data_dict = {}    
    data_dict['nan_ind'] = nan_ind
    data_dict['stock_filter'] = stock_filter
    data_dict['factor_dict'] = factor_dict[stock_list].loc[date_list]
    data_dict['return_df']   = return_df[stock_list].loc[date_list]
    data_dict['benchmark_ret'] = benchmark_ret.loc[date_list]
    data_dict['holding_period_ret'] = holding_period_ret[stock_list].loc[date_list]
     
    # filter factor data
    
    data_dict['factor_dict'][nan_ind==False] = np.nan
    data_dict['return_df'][nan_ind==False] - np.nan
    if easy_test==False:
        data_dict['stock_industry'] = stock_industry[stock_list].loc[date_list]
        for index in StyleFactorDict:
            StyleFactorDict[index] = StyleFactorDict[index][stock_list].loc[date_list]
        data_dict['StyleFactorDict'] = StyleFactorDict
        
    stock_remain = dict()
    stock_array = np.array(stock_list)
    for date in date_list:
        stock_remain[date] = stock_array[stock_filter.loc[date]==True].tolist()
    data_dict['stock_remain'] = stock_remain
    
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*30)
    
    return data_dict


"""因子数据处理部分"""

def FactorTypeCheck(factor_dict):
    """ 自动判别因子是否为1，0,-1 的标签矩阵"""
    max_min = [factor_dict.max().max(),factor_dict.min().min()]
    factor_type = 'Categorical' if max_min in [[0,-1],[0,1],[-1,1]] else 'Numerical'
    return factor_type


def Standard_Process(factor_dict,nan_ind=None,stock_industry=None,FillNaN=False):
    """ nan_ind:  可以根据用户输入决定筛选条件 - 比如VOLUME>0
        True： 1. 去除没有收益的日子
        False: 1. 去除没有收益的日子  2. 标准化
    """ 
    print ('-'*5+'  Data Cleaning  '+'-'*5)
    tic = time.time()
    factor_type = FactorTypeCheck(factor_dict)
    if factor_type =='Categorical':  #不进行任何 因子清洗，填充
        print ('Factor Type: Categorical --> No Standardization and FillingNA')        
    elif factor_type =='Numerical':
        if type(nan_ind) == pd.DataFrame:
            factor_dict[nan_ind==False] = np.nan
            factor_dict[~np.isfinite(factor_dict)]=np.nan #将inf,-inf,nan 取代为nan
        print ('BoxSkewPlot Processing')
        factor_dict = BoxSkewPlot(factor_dict) #极值处理
        
        if FillNaN == True:
            print ('Filling NaN with Industry Median...')
            factor_dict = Factor_Fillna(factor_dict,stock_industry,nan_ind)
        else:
            print ('NaN not Filled')
        print ('Normalizing')
        factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0) #handle nan            
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*30)       
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
        pd_process = pd_process.apply(box_skew_algo, axis=axis)
        data = pd_process.values
        s = data.shape[0]
        tmplist = []
        for i in range(s):
            tmplist.append(data[i,])
        pd_process = pd.DataFrame(tmplist,index = pd_raw.index, columns = pd_raw.columns)
    else:
        raise AssertionError 
    return pd_process

   
def Factor_Fillna(factor_dict,stock_industry,nan_ind):
    """ 缺失值处理：
    得到新的因子暴露度序列后，将因子暴露度缺失的地方设为行业中位数。
    # 因子暴露度缺失定义为无法获取此因子 而非该股票不可交易  - 用处理过的因子填充
    # nan_ind 为股票停牌信息  1 为真停牌 或者没上市/ 则不填充
    
    """
    fill_ind = np.isnan(factor_dict)[nan_ind==False] # 所有NAN * 非停牌的NAN = 缺失数据
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

"""计算Ttest值,和IC值  - 每日横截面计算股票池"""



def calculated_Ttest(date,stock_remain,factor_dict,Panel):
    """默认PANEL  收益与因子同期"""        
    """VIF = 1/(1-R2)
        当0<VIF<10，不存在多重共线性；当10≤VIF<100，存在较强的多重共线性；当VIF≥100，存在严重多重共线性
        OLS 1: F(factor_to_be_test) = F(Style)*Beta(Style)+X(Industry)*Beta(Industry)+Resid
        OLS 2: R(stock_ret) = Resid*Beta(factor_to_be_test) + resid
        输出: ols2.tstat, ols2.beta, VIF, IC"""
    stock_pool = stock_remain[date]
    date_num,stock_num = factor_dict.shape
    stock_all_code = factor_dict.columns.tolist()
    Stock_dataframe = pd.DataFrame([i for i in range(stock_num)],index = stock_all_code).T 
    res = np.array([np.nan for i in range(stock_num)])
    e = Panel.xs(date)[stock_pool].T  #读取以date为索引的数据
    e["factor"] = factor_dict[stock_pool].loc[date].values #加入因子
    e=e.replace([np.inf,-np.inf],[np.nan,np.nan])#剔除也许因子值为正无穷和负无穷的值
    #style_factor_list = ['Beta', 'Momentum', 'Size', 'EarningsYield','Volatility', 'Growth', 'Value', 'Leverage', 'Liquidity']
    style_factor_list  = ['Size']#,'Growth']
    e=e.dropna(subset=['holding_period_ret','factor']+style_factor_list) #剔除因子为NAN的股票
    ind_mat = pd.get_dummies(e['industry']) #把行业变成虚拟0-1变量
    e = pd.concat([e,ind_mat],axis=1)
    e = e.drop('industry',axis=1) 
    e=e[ ['holding_period_ret', 'factor'] + style_factor_list + ind_mat.columns.tolist()] # 如果该行业没有也应该删除此行业
    if len(e.values)<5:
        return np.nan,np.nan,np.nan,np.nan,np.nan
    ols1  = sm.OLS(e['factor'],e[e.columns[2:]]).fit()
    f = copy.deepcopy(e)
    value = Stock_dataframe[e.index].values[0]
    res[value] = ols1.resid # OLS Residual - cross sectional regression
    f['factor'] = ols1.resid
    ols2 = sm.OLS(f['holding_period_ret'],f['factor']).fit() 
    VIF = 1/(1-ols1.rsquared) if ols1.rsquared != 1 else 99999
    IC = f[['holding_period_ret','factor']].corr().iat[0,1] # 此处IC为 去除风险因子后的残差与下期的收益 
    return ols2.tvalues[0],ols2.params[0],ols1.rsquared,VIF,IC



def FactorRegressionTest(Panel,factor_dict,stock_remain,holding_period):
    print ('-'*5+'   Regression Test   '+'-'*5)
    date_num = factor_dict.shape[0]
    total_rebal = int(date_num/holding_period)
    collector = np.empty([total_rebal,5]) 
    collector[:] = np.nan
    date_list = factor_dict.index.tolist()
    rebal_date_list = [date_list[i*holding_period] for i in range(total_rebal)]
    for rebal_num in range(total_rebal):
        date = date_list[rebal_num*holding_period]
        try:
            collector[rebal_num,:] = calculated_Ttest(date,stock_remain,factor_dict,Panel)
        except:
            continue
            #print('Data Not Found for '+str(date_rebal))
    RegOutput = pd.DataFrame(collector,columns = ['T-stat','Beta','Rsq','VIF','IC'],index=rebal_date_list)  
    print('Regression Test Done...')      
    print ('-'*30)
    return RegOutput


def FactorTIC_Test(Ttest,FacBeta,Rsq,VIF,IC):
    """因子评价方法：
                    a) t 值序列绝对值平均值——因子显著性的重要判据；
                    b) t 值序列绝对值大于2 的占比——判断因子的显著性是否稳定；
                    c) 因子收益率序列平均值，以及该均值零假设检验的t 值——判断因子收益率序列是否方向一致，并且显著不为零；
                    d) t 值序列均值的绝对值除以t 值序列的标准差——结合显著性和波动性，辅助判断因子是否有效、稳健。        
    """
    Ttest,FacBeta,Rsq,VIF,IC = Ttest[~np.isnan(Ttest)],FacBeta[~np.isnan(FacBeta)],Rsq[~np.isnan(Rsq)],VIF[~np.isnan(VIF)],IC[~np.isnan(IC)]
    Ttest_avg = np.average(Ttest)
    Ttest_abs_avg = np.average(np.abs(Ttest))   #T值绝对值平均
    TtestG2Pct = sum(np.abs(Ttest)>2)/len(Ttest) if len(Ttest)>0 else np.nan#T值大于2所占的比例
    mean_div_std =Ttest_avg/np.std(Ttest) if  np.isfinite(np.std(Ttest)) else np.nan #t 均值/t标准差
    FacBeta_mean = np.average(FacBeta) #因子收益率的均值
    Factor_T = sps.ttest_1samp(FacBeta,popmean =0).statistic#因子收益率序列t检验
    IC_avg = np.average(IC) #IC序列均值
    IC_std = np.std(IC) #IC序列标准差
    IR =IC_avg/IC_std #IR比率（IC 值序列均值与标准差的比值）
    IC_pos = sum(np.array(IC)>0)/len(IC) if len(IC)>0 else np.nan#IC>0占比 
    IC_absG2bp = sum(np.abs(IC)>0.02)/len(IC) if len(IC)>0 else np.nan #|IC|>0.02占比
    VIF_avg = np.average(VIF)
    VIF_max = np.max(VIF)
    #VIF_min = np.min(VIF)
    VIF_IR = np.average(VIF)/(np.std(VIF)+0.000000001)
    Rsq_Avg = np.average(Rsq)    
    Reg_Dict={
                 'Neutralized Factor - Tstat_abs Avg':Ttest_abs_avg,
                 'Neutralized Factor - T>2 Percentage':TtestG2Pct,
                 'Neutralized Factor - Tstat_Avg/Tstat_Std':mean_div_std,
                 'Neutralized Factor - FactorReturn Avg':FacBeta_mean,
                 'Neutralized Factor - FactorReturn T-Test':Factor_T,
                 'Neutralized Factor - IC Avg':IC_avg,
                 'Neutralized Factor - IC Std':IC_std,
                 'Neutralized Factor - ICIR':IR,
                 'Neutralized Factor - IC>0 Percentage':IC_pos,
                 'Neutralized Factor - IC_abs>0.02 Percentage':IC_absG2bp,
                 'VIF Avg':VIF_avg,
                 'VIF Max':VIF_max,
                 'VIF IR':VIF_IR,
                 'R Sqaured (% explained by style and industry)':Rsq_Avg
                 }    
    RegStat =  pd.DataFrame(Reg_Dict,index=['TestFactor']).T
    return RegStat


#########################################################################################

"""分层测试"""
       
def divide_stock(stock_code,factor_dict,date_idx,segment_num):
    '''输入：股票池代码、日期、因子、划分数量
       输出：按照组数,股票代码,每组个股权重'''
    segment_label = copy.deepcopy(factor_dict.iloc[date_idx])
    factor_list = factor_dict[stock_code].iloc[date_idx].dropna()   #读取第date天的值并drop掉NAN
    rank_num = len(factor_list) #剩下多少只股票,
    segment_pool={i:[] for i in range(1,segment_num+1)} #pool形成股票池过程 - 股票数可能差1  所以DICT
    if rank_num < segment_num*1:
        return segment_pool,[np.nan]*segment_num,segment_label #没有股票了
    segment_pct = [100-100.0/segment_num*i for i in range(segment_num+1)]
    factor_pct = [np.percentile(factor_list,i) for i in segment_pct]
    factor_pct[-1] = factor_pct[-1]-1  # 包含所有股票    
    stock_wgt_per_pool = [np.nan]*segment_num
    for i in range(1,segment_num+1):
        segment_pool[i] = factor_list[(factor_list<=factor_pct[i-1]) & (factor_list>factor_pct[i])].index.tolist()  
        stock_num_pool = len(segment_pool[i])
        stock_wgt_per_pool[i-1] = 1 if stock_num_pool == 0 else 1.0/len(segment_pool[i])     
        segment_label[segment_pool[i]] = i              
    return segment_pool, stock_wgt_per_pool,segment_label


#########################################################################################
"""简单版本  分层测试"""

def easy_segment_ret_day_mat(factor_dict_mat,holding_period_ret_one_day_mat,date,segment_num):
    '''输入：股票池代码、日期、因子、划分数量
       输出：按照组数,股票代码,每组个股权重'''
    fac_ret = np.stack([factor_dict_mat[date,:],holding_period_ret_one_day_mat[date,:]],axis=1)
    fac_ret_sort = fac_ret[fac_ret[:,0].argsort()] # sort by factor score - small to large
    rank_num = sum(np.isfinite(fac_ret_sort[:,0])) #剩下多少只股票,
    if rank_num < segment_num*1:
        return [np.nan]*segment_num 
    stock_num_q = int(rank_num/segment_num)
    order_cut = np.arange(0,rank_num,stock_num_q) if segment_num>1 else [0]  
    order_cut = order_cut[:segment_num] if segment_num>1 else [0] # there may be stock left due to rounding error
    seg_ret_reverse = [np.nanmean(fac_ret_sort[i:i+stock_num_q,1]) for i in order_cut] # take nan mean based on cut 
    return seg_ret_reverse

def easy_segment_test(factor_dict,holding_period_ret,holding_period,segment_num,benchmark_ret):
    print ('-'*5 +'   Segment Test - '+str(segment_num)+'   '+'-'*5)
    tic = time.time()
    holding_period_ret_one_day = (holding_period_ret+1)**(1/holding_period)-1
    holding_period_ret_one_day_mat = holding_period_ret_one_day.values
    bmk_hpr_daily = ((benchmark_ret+1).rolling(holding_period).apply(np.prod)**(1/holding_period)-1).shift(-1*holding_period)
    factor_dict_mat = factor_dict.values
    date_num = factor_dict.shape[0]
    easy_seg_return = np.zeros([date_num,segment_num])
    name_pool_mat = ['Q'+str(segment_num-i) for i in range(int(segment_num))]
    date_list = factor_dict.index
    for i in range(date_num):
        #easy_seg_return[i,:]= easy_segment_ret_day(factor_dict,holding_period_ret_one_day,i,segment_num)
        easy_seg_return[i,:]= easy_segment_ret_day_mat(factor_dict_mat,holding_period_ret_one_day_mat,i,segment_num)
    easy_seg_return = pd.DataFrame(easy_seg_return,columns=name_pool_mat,index=date_list)
    name_pool = ['Q'+str(i+1) for i in range(int(segment_num))]
    easy_seg_return = easy_seg_return[name_pool] # sort it back to Q1-Q5 
    start_ind = easy_seg_return.any(axis=1)
    easy_seg_return['Benchmark'] = bmk_hpr_daily
    easy_seg_return['Benchmark'][~start_ind] = np.nan 
    max_q = easy_seg_return[[name_pool[0],name_pool[-1]]].mean().argmax()
    min_q = easy_seg_return[[name_pool[0],name_pool[-1]]].mean().argmin()
    ls_type =  max_q +'-'+min_q
    easy_seg_return[ls_type] = easy_seg_return[max_q]-easy_seg_return[min_q]
    print ('Segment Done')  
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*30)
    return easy_seg_return

#########################################################################################

def PerformanceMeasure(seg_return):
    date_num, segment_num = seg_return.shape
    take_list = (np.isnan(seg_return).sum(axis=1)==segment_num).index
    seg_return = seg_return.loc[take_list]
    date_1yr = 240
    seg_return_cum = (seg_return.fillna(0)+1).cumprod()
    Ret_Annual = (seg_return_cum.iloc[-1,:]**(date_1yr/date_num)-1)
    Ret_Excess = Ret_Annual-Ret_Annual['Benchmark']
    Vol_Annual = seg_return.fillna(0).std()*np.sqrt(date_1yr)
    MDD = pd.DataFrame(list(map(max_drawdown,seg_return_cum.T.values)),index = seg_return_cum.columns)
    Tracking_Error = (seg_return.T-seg_return['Benchmark']).T.std(axis=0)*np.sqrt(date_1yr)
    SharpeRatio = Ret_Annual/Vol_Annual
    InfoRatio = Ret_Excess/Tracking_Error
    PerfMeasure = pd.concat([Ret_Annual,Vol_Annual,SharpeRatio,Ret_Excess,Tracking_Error,InfoRatio,MDD],axis=1)
    PerfMeasure.columns = ['Return(Ann.)','Vol(Ann.)','Sharpe Ratio','Excess Return','Tracking Error','IR','MaxDD']
    return PerfMeasure

def max_drawdown(capital_line):
    """输入: 1. date_line: 日期序列   2.capital_line: 账户价值序列
       输出: 最大回撤及开始日期和结束日期            """
    mdd_end = np.argmax(np.maximum.accumulate(capital_line) - capital_line) # end of the period
    if mdd_end==0:  # 假如累计收益序列为1，则退出
        return np.nan
    mdd_start = np.argmax(capital_line[:mdd_end]) # start of period    
    mdd  = 1- capital_line[mdd_end]/capital_line[mdd_start]
    return mdd    


#########################################################################################

"""Tunrover Related Calculation"""
def turnover_calc(factor_dict,segment_num,holding_period,stock_remain):
    """Turnover: Calculate the pct of stock changed within each pool
                 Simple average of percentage changed in each pool - get a time series of turnover rate
    """
    date_num,stock_num = factor_dict.shape
    total_rebal = int(date_num/holding_period)
    stock_changed = np.zeros([total_rebal,segment_num])
    stock_changed[:] = np.nan
    segment_pool_previous = {i:[] for i in range(1,segment_num+1)}
    date_list = factor_dict.index.tolist()
    rebal_date_list = [date_list[i*holding_period] for i in range(total_rebal)]
    segment_label = np.array(np.zeros([total_rebal,stock_num]))
    label_corr = [np.nan]*total_rebal
    for rebal_num in range(total_rebal):
        day_rebal = rebal_num*holding_period+1 # T+1 调仓
        stock_code = stock_remain[date_list[day_rebal]]
        segment_pool,stock_wgt_per_pool,segment_label[rebal_num,:] = divide_stock(stock_code,factor_dict,day_rebal,segment_num)
        segment_label[rebal_num,:][np.isnan(segment_label[rebal_num,:])] = 0
        if rebal_num>1 and len(segment_pool_previous[1])>0 and len(segment_pool[1])>0:
            for i in range(segment_num):
                if len(segment_pool[i+1])>0:
                    stock_changed[rebal_num,i] = 1-len(set(segment_pool_previous[i+1]).intersection(segment_pool[i+1]))/len(segment_pool[i+1])
            label_corr[rebal_num] = np.corrcoef(segment_label[rebal_num,:],segment_label[rebal_num-1,:])[0,1]
        segment_pool_previous = segment_pool
    turnover = pd.DataFrame(stock_changed,index = rebal_date_list,columns=['Q'+str(i+1) for i in range(segment_num)])
    turnover['Correlation'] = label_corr
    return turnover

def factor_score_correlation(factor_dict,holding_period):
    """ correlation_type = 'spearman','pearson'
    """
    factor_auto_correlation = pd.DataFrame()
    factor_auto_correlation['Pearson_linear_'+str(holding_period)+'d'] = factor_dict.corrwith(factor_dict.shift(holding_period),axis=1).T
    factor_rank = factor_dict.rank(axis=1)
    factor_auto_correlation['Spearman_rank_'+str(holding_period)+'d'] = factor_rank.corrwith(factor_rank.shift(holding_period),axis=1).T
    return factor_auto_correlation


#########################################################################################
"""因子原始数据统计"""
def FactorDist(factor_dict,nan_ind):
    """nan_ind: account for stock not trading only"""
    factor_val1 = factor_dict.values.flatten()
    factor_val = factor_val1[~np.isnan(factor_val1)]
    fac_min = np.min(factor_val)
    fac_max = np.max(factor_val)
    fac_mean = np.mean(factor_val)
    fac_median = np.median(factor_val)
    fac_skew = sps.skew(factor_val)
    fac_kurtosis = sps.kurtosis(factor_val)
    fac_complete = len(factor_val)/nan_ind.sum().sum()#len(factor_val1)
    fac_complete = min(1,fac_complete)
    colname = ['Skew','Kurtosis','Complete%','Median','Mean','Max','Min']
    fac_dist = pd.DataFrame([fac_skew,fac_kurtosis,fac_complete,fac_median,fac_mean,fac_max,fac_min],index = colname)
    return fac_dist

def CollinearTest(factor_dict,StyleFactorDict):
    fac_corr = {}
    factor_val1 = factor_dict.values.flatten()
    for item in StyleFactorDict.keys():
        style_val1 = StyleFactorDict[item].values.flatten()
        fac_combine = np.vstack([factor_val1,style_val1])
        fac_slice = fac_combine[:,~np.isnan(np.sum(fac_combine,axis=0))]
        fac_corr[item] = np.corrcoef(fac_slice)[0,1]
    fac_corr = pd.DataFrame.from_dict(fac_corr, orient='index')
    return fac_corr


def AlphaDecayTest(factor_dict,holding_period_ret,holding_period,max_lag):
    """IC Decay Test:
       max_lag:(int) number of holding period after factor data was observed
       Correlation: IC(T), Return(T+1:T+1+Holding_Period) 
       Correlation for all days 
    """
    print ('-'*5+'   Factor IC Decay Test   '+'-'*5)
    total_rebal = int(factor_dict.shape[0]/holding_period)
    max_lag = total_rebal if max_lag>total_rebal else max_lag # control for input error
    lag_list = [(i)*holding_period for i in range(max_lag+1)]
    IC_ts = np.empty([len(factor_dict),len(lag_list)])
    for i in range(len(lag_list)):
        lag_ret = holding_period_ret.shift(-1*lag_list[i]) #  
        IC_ts[:,i] = factor_dict.corrwith(lag_ret,axis=1)
    IC_Decay = pd.DataFrame(np.nanmean(IC_ts,axis=0),index = lag_list,columns=['IC Decay'])   
    Alpha_ts = factor_dict.corrwith(holding_period_ret,axis=1)*holding_period_ret.std(axis=1)/holding_period
    Alpha_cumsum = pd.DataFrame(Alpha_ts.cumsum(),columns=['Alpha (IC*Dispersion)'])
    print ('-'*30)
    return IC_Decay,Alpha_cumsum


#########################################################################################

"""因子中性化"""

def calculated_Ttest_ols1(date,stock_remain,factor_dict,Panel):
    """OLS 1: F(factor_to_be_test) = F(Style)*Beta(Style)+X(Industry)*Beta(Industry)+Resid
       输出: ols1.res"""
    stock_pool = stock_remain[date]
    date_num,stock_num = factor_dict.shape
    stock_all_code = factor_dict.columns.tolist()
    Stock_dataframe = pd.DataFrame([i for i in range(stock_num)],index = stock_all_code).T 
    res = np.array([np.nan]*stock_num)
    e = Panel.xs(date)[stock_pool].T  #读取以date为索引的数据
    e["factor"] = factor_dict[stock_pool].loc[date].values #加入因子
    e=e.replace([np.inf,-np.inf],[np.nan,np.nan])#剔除也许因子值为正无穷和负无穷的值
    #style_factor_list = ['Beta', 'Momentum', 'Size', 'EarningsYield','Volatility', 'Growth', 'Value', 'Leverage', 'Liquidity']
    style_factor_list  = ['Size']
    e=e.dropna(subset=['factor']+style_factor_list) #剔除因子为NAN的股票
    ind_mat = pd.get_dummies(e['industry']) #把行业变成虚拟0-1变量
    e = pd.concat([e,ind_mat],axis=1)
    e = e.drop('industry',axis=1) 
    e=e[ ['factor'] + style_factor_list + ind_mat.columns.tolist()] # 如果该行业没有也应该删除此行业
    if len(e.values)<5:
        return np.nan,np.nan,np.nan,np.nan,np.nan
    ols1  = sm.OLS(e['factor'],e[e.columns[1:]]).fit()
    value = Stock_dataframe[e.index].values[0]
    res[value] = ols1.resid # OLS Residual - cross sectional regression
    return res


def np_regression_res(x,y,nan_list):
    res = np.array([np.nan]*len(x))    
    mask = np.isfinite(x) & np.isfinite(y.sum(axis=1)) & nan_list
    if len(mask)==0:
        return res
    ols1  = sm.OLS(x[mask],y[mask]).fit()
    res[mask] = ols1.resid
    return res


def Factor_Neutralize_mat(factor_dict,data_dict,Normalize=True):
    """
    Remove Effect From Industry and Style Factor, Get residual
    Normalize: Choose to normalize residual cross sectionally
    
    """
    tic = time.time()
    size_mat = data_dict['StyleFactorDict']['Size'].values
    factor_mat = factor_dict.values
    industry_mat = data_dict['stock_industry'].values
    nan_mat = data_dict['stock_filter'].values

    print ('-'*5+'   Get Factor Neutralized   '+'-'*5)
    date_num,stock_num = factor_dict.shape
    res = np.empty([date_num,stock_num])
    res[:] = np.nan
    date_list = factor_dict.index.tolist()
    for date_idx in range(date_num):
        try:
            y1 = size_mat[date_idx,:]
            y2_dum = pd.get_dummies(industry_mat[date_idx,:])
            y0 = np.zeros(len(y1))
            y = np.column_stack([y0,y1,y2_dum])
            res[date_idx,:] = np_regression_res(factor_mat[date_idx,:],y,nan_mat[date_idx,:])
        except:
            continue
    factor_residual = pd.DataFrame(res,columns = factor_dict.columns,index=date_list)
    factor_residual = DataNormalize(factor_residual) if Normalize==True else factor_residual
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*20)
    return factor_residual


def Factor_Neutralize(Panel,factor_dict,stock_remain,Normalize=True):
    """
    Remove Effect From Industry and Style Factor, Get residual
    Normalize: Choose to normalize residual cross sectionally
    
    """
    print ('-'*5+'   Get Factor Neutralized   '+'-'*5)
    tic = time.time()
    date_num,stock_num = factor_dict.shape
    res = np.empty([date_num,stock_num])
    res[:] = np.nan
    date_list = factor_dict.index.tolist()    
    for date_idx in range(date_num):
        try:
            res[date_idx,:] = calculated_Ttest_ols1(date_list[date_idx],stock_remain,factor_dict,Panel)
        except:
            continue
    factor_residual = pd.DataFrame(res,columns = factor_dict.columns,index=date_list)
    factor_residual = DataNormalize(factor_residual) if Normalize==True else factor_residual
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*20)
    return factor_residual
###########################################################################################

def SummaryTable(factor_name,factor_dict,holding_period,Universe=None):
    fac_date_list = factor_dict.index.tolist()
    start_date = fac_date_list[0].strftime("%Y-%m-%d") if type(fac_date_list[0]) !=int else fac_date_list[0]
    end_date = fac_date_list[-1].strftime("%Y-%m-%d") if type(fac_date_list[-1]) !=int else fac_date_list[-1]
    test_date = str(start_date) + ' - ' + str(end_date)
    Uni = 'A Shares' if Universe==None else Universe 
    date_num,stock_num = factor_dict.shape
    sum_index = ['Factor Name','Test Period','Stock Universe','Stock Count','Date Count','Holding Period']
    sum_val_str = [str(i) for i in [factor_name,test_date,Uni,stock_num,date_num,holding_period]]
    sum_df = pd.DataFrame(sum_val_str,index = sum_index)
    sum_df.columns = ['Summary']
    return sum_df

def DF2H5(df,factor_name,save_path,save_name):
    """save dataframe matrix to multiindex h5"""
    tic = time.time()
    data_MI = df.stack().reset_index()
    data_MI.columns = ['dt','Ticker',factor_name]
    data_MI.Ticker = data_MI.Ticker.astype('object')
    data_MI = data_MI.set_index(['dt','Ticker'])
    os.remove(save_path+save_name) if os.path.exists(save_path+save_name) else None
    IO.pd_hdf5_writer(data_MI,save_path+save_name,dataset='factor_data')    
    print ('Saved to :'+save_name)
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    return     

def factor_coverage(factor_dict):
    #full_ts = nan_ind.sum(axis=1) # exist total
    date_num,stock_num = factor_dict.shape
    stock_ts = pd.DataFrame([stock_num-np.isnan(factor_dict).sum(axis=1)],index=['stock number']).T
    return stock_ts

def IC_stats(IC_combined):
    ICIR = IC_combined.mean()/IC_combined.std()#*np.sqrt(240)
    IC_combined_stats = pd.DataFrame([IC_combined.mean(),IC_combined.std(),ICIR])
    IC_combined_stats.index = ['IC_mean','IC_std','ICIR']
    return IC_combined_stats
###########################################################################################


###########################################################################################




"""Main Function"""

def FactorEntryTest(factor_dict,holding_period,factor_name,use_factor_type='original',easy_test=False,
                    segment_num=5,benchmark_index='zz500',test_universe=None,provide_data=None,
                    Standardization=True,FillNaN=False,FactorFillTS=False,RegTest=True,
                    SegmentTest=True,DecayTest=True,GetFactorNeutralized=True,save2h5=False,result_folder=None):
    """ Factotr Backtest
        Input：
        provide_data: dictionary of dataframe used in factor test - save time for reloading 
                      - return_df.benchmark_ret,nan_ind,holding_period_ret,StyleFactorDict(dict),stock_remain,stock_industry
        easy_test: quick factor test
        factor_dict:    (dataframe) factor exposure - support MultiIndex and Matrix
        hodling_period: (int)   
        factor_name:    (str) 因子名称
        segment_num：   (int) 分层数 - 默认5层 / 如果因子为{1,0} 则分层自动变为2
        holding_period: (int) 持仓周期  
        benchmark_ret:  (str) 'zz500','zz800','sz50','hs300'
        factor_format:   (str) 默认为MultiIndex  - 'MultiIndex','Matrix'
        test_factor_type: 'Original','Neutralized','Standardized'
        
        
        Output：
        GetFactorNeutralized: 是否输出因子中性化结果 + 标准化结果
        result_folder：       指定因子报告输出地址
        
        Note: assume to use standardized factor to do all the test
        
    benchmark_index(str) = lookuptable {'zz500': '000905.SH', 'zz800': '000906.SH', 'sz50': '000016.SH', 'hs300': '000300.SH'}
    style_list = ['EarningsYield','Value','Liquidity','NonLinearSize','Volatility','Size','Momentum','Beta','Leverage']
    """
    print ('-'*40)
    print ('Factor Backtest  -  '+str(factor_name))
    
    if provide_data is not None:
        if 1==1:
            print ('Align proivded data')
            dummy = provide_data.pop('factor_dict',None)
            if type(factor_dict)==pd.Series:
                factor_dict = pd.DataFrame(factor_dict)
                factor_dict.columns = [factor_name]
            factor_df = factor_dict.unstack()[factor_name] if len(factor_dict.columns)==1 else factor_dict
            data_dict = align_data({**provide_data,**{'factor_dict':factor_df}})
        else:
            print ('Wrong input, reload data...')
            data_dict = load_data(factor_dict,holding_period,benchmark_index,easy_test,test_universe)
    else:
        data_dict = load_data(factor_dict,holding_period,benchmark_index,easy_test,test_universe)
        
    factor_dict,return_df,benchmark_ret = data_dict['factor_dict'],data_dict['return_df'],data_dict['benchmark_ret']
    nan_ind,holding_period_ret = data_dict['nan_ind'],data_dict['holding_period_ret']
    if easy_test==False:
        StyleFactorDict,stock_remain,stock_industry = data_dict['StyleFactorDict'],data_dict['stock_remain'],data_dict['stock_industry']    
    sum_df = SummaryTable(factor_name,factor_dict,holding_period,test_universe)
    factor_ts = factor_coverage(factor_dict)
    fac_dist = FactorDist(factor_dict,nan_ind)
    
    IC_combined = pd.DataFrame()
    IC_combined['IC_original'] = factor_dict.corrwith(holding_period_ret,axis=1)

    """Create Test Factor Folder"""
    if result_folder == None:
        result_folder = 'S:\\Quant\\backtest\\backtest_output\\'
    factor_name = 'TestFactor' if factor_name==None else factor_name
    output_folder = result_folder + factor_name + '\\'    
    if (not os.path.exists(output_folder)):
        print("Output Location: " + output_folder)
        os.mkdir(output_folder)        
    
    # overwrite from easy_test:
    if easy_test == True:
        [Standardization,FactorFillTS,RegTest,GetFactorNeutralized] = [False]*4
        
        
    """Data Cleaning"""
    if Standardization ==  True:
        FillNaN=False
        factor_dict_std = Standard_Process(factor_dict,nan_ind,stock_industry,FillNaN)
        IC_combined['IC_standardized'] = factor_dict_std.corrwith(holding_period_ret,axis=1)
        if use_factor_type == 'standardized':
            factor_dict = factor_dict_std
            
    if FactorFillTS == True:
       factor_dict = Factor_Fillna_TS(factor_dict,holding_period)
       
    if RegTest==True:
        tic = time.time()
        fac_corr = CollinearTest(factor_dict,StyleFactorDict)        
        com_dict = dict({'ret':return_df,'holding_period_ret':holding_period_ret,'industry':stock_industry},**StyleFactorDict)
        Panel = DF2MultiIndex(com_dict)    
        RegOutput = FactorRegressionTest(Panel,factor_dict,stock_remain,holding_period)
        RegStat = FactorTIC_Test(RegOutput['T-stat'],RegOutput['Beta'],RegOutput['Rsq'],RegOutput['VIF'],RegOutput['IC'])
        toc = time.time()
        print (str((round((toc-tic),2)))+'s ellapsed')

    
    if GetFactorNeutralized == True:
        factor_neutralized = Factor_Neutralize_mat(factor_dict,data_dict,Normalize=True)
        IC_combined['IC_neutralized'] = factor_neutralized.corrwith(holding_period_ret,axis=1)
        
        if use_factor_type=='neutralized':
            factor_dict = factor_neutralized
            
        if save2h5 == True:
            print ('Saving neutralized results to H5')
            save_name_neu = factor_name+'_neutralized.h5' # Save neutralized factor
            DF2H5(factor_neutralized,factor_name,output_folder,save_name_neu) # save neutralized result to h5c
            save_name_std = factor_name+'_standardized.h5' # Save standardized factor 
            DF2H5(factor_dict_std,factor_name,output_folder,save_name_std) # save neutralized result to h5c        
        
        
    if SegmentTest == True:
        # 判定因子类别
        tic = time.time()
        segment_num = 2 if FactorTypeCheck(factor_dict)=='Categorical' else segment_num
        seg_return = easy_segment_test(factor_dict,holding_period_ret,holding_period,segment_num,benchmark_ret)
        seg_return_30 = easy_segment_test(factor_dict,holding_period_ret,holding_period,30,benchmark_ret)
        seg_return_stat = PerformanceMeasure(seg_return)
        seg_return_30_stat = PerformanceMeasure(seg_return_30)
        seg_return_stat_year = seg_return.groupby(seg_return.index.year).apply(PerformanceMeasure)
        seg_return_30_stat_year = seg_return_30.groupby(seg_return.index.year).apply(PerformanceMeasure)
        #turnover = turnover_calc(factor_dict,segment_num,holding_period,stock_remain)
        factor_auto_correlation = factor_score_correlation(factor_dict,holding_period)
        toc = time.time()
        print (str((round((toc-tic),2)))+'s ellapsed')    
        
    if DecayTest == True:
        tic = time.time()
        max_lag = 10   
        IC_Decay,Alpha_cumsum = AlphaDecayTest(factor_dict,holding_period_ret,holding_period,max_lag)
        toc = time.time()
        print (str((round((toc-tic),2)))+'s ellapsed')
    
    IC_combined_stats = IC_stats(IC_combined)
    
    """Write to Excel"""
    print ('-'*5 + '   Saving Results to Excel   '+'-'*5)
    excel_name = output_folder+'FactorBacktest_'+str(factor_name)+'.xlsx'
    writer = pd.ExcelWriter(excel_name,engine='xlsxwriter')
    sum_df.to_excel(writer,sheet_name='因子信息')
    fac_dist.to_excel(writer,sheet_name='因子原始统计')
    fac_corr.to_excel(writer,sheet_name='因子共线性') if RegTest==True else None
    RegOutput.to_excel(writer,sheet_name='T值与IC') if RegTest==True else None
    RegStat.to_excel(writer,sheet_name='T值与IC检验') if RegTest==True else None
    seg_return.to_excel(writer,sheet_name='分层测试_日收益率') if SegmentTest == True else None
    seg_return_30.to_excel(writer,sheet_name='分层测试30_日收益率') if SegmentTest == True else None
    seg_return_stat.to_excel(writer,sheet_name='分层测试_组合表现') if SegmentTest == True else None
    seg_return_30_stat.to_excel(writer,sheet_name='分层测试_30组合表现') if SegmentTest == True else None
    seg_return_30_stat_year.to_excel(writer,sheet_name='分层30组合年度') if SegmentTest == True else None
    seg_return_stat_year.to_excel(writer,sheet_name='分层测试_组合年度') if SegmentTest == True else None
    #turnover.to_excel(writer,sheet_name='分层测试_换手率') if SegmentTest == True else None
    factor_auto_correlation.to_excel(writer,sheet_name='因子自相关性')
    IC_Decay.to_excel(writer,sheet_name='因子IC有效期') if DecayTest == True else None
    Alpha_cumsum.to_excel(writer,sheet_name='因子Alpha') if DecayTest == True else None
    IC_combined.to_excel(writer,sheet_name='因子IC序列')
    IC_combined_stats.to_excel(writer,sheet_name='因子IC序列统计')
    factor_ts.to_excel(writer,sheet_name='因子完整度')
    writer.save()    
    print ('-'*30)
        
    GeneratePdf(excel_name,factor_name,output_folder,easy_test)
        
    print ('Factor Backtest Done')    
    print ('-'*40)
        
    return 
     



