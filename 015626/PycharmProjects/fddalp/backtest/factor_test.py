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

"""
from multifactor.backtest.factor_test import factor_backtest

hp = 'S:\\zsj\\fct_cdba8d547f1da1cf4e41ff84dd8bfbde1351cc008d273b6f72e69fd6197538fc.h5'
factor_dict = IO.read_data([20100226,20180420],alt=hp)['fct_cdba8d547f1da1cf4e41ff84dd8bfbde1351cc008d273b6f72e69fd6197538fc'].unstack()

holding_period = 10 
factor_name = 'fct_cdba8d547f1da1cf4e41ff84dd8bfbde1351cc008d273b6f72e69fd6197538fc'
result_folder = 'S:\\zsj\\test\\'
benchmark_index='zz500'
test_universe=None
easy_test=True

factor_backtest(factor_dict,holding_period,factor_name,use_factor_type='original',
                    benchmark_index='zz500',test_universe=None,provide_data=data_dict,
                    neutral_list=None,easy_test=True,result_folder=result_folder)

from multifactor.backtest.factor_test import factor_backtest

hp = 'S:\\zsj\\high_beta_low_vol_nis.h5'
factor_dict = IO.read_data([20100226,20180420],alt=hp)['high_beta_low_vol_nis'].unstack()

holding_period = 10 
factor_name = 'high_beta_low_vol_nis'
result_folder = 'S:\\zsj\\test\\'




"""


import os 
import pandas as pd
import numpy as np
import statsmodels.api as sm
import scipy.stats as sps
import time
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import datetime as dt
from functools import reduce
#from .ReportGenerator import GeneratePdf 
from multifactor.backtest.ReportGenerator import generate_pdf

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


def get_risk_data(start_date,end_date,neutral_list=None):
    dat = {}
    #'EarningsYield','Value','Liquidity','NonLinearSize','Volatility','Size','Momentum','Beta','Leverage','Industry'
    if neutral_list == None:
        style_risk = IO.read_data([start_date,end_date],ftype=FType.RISK,dsource=DSource.STYLEFACTOR,max_workers=1)
    else:
        style_risk = IO.read_data([start_date,end_date],ftype=FType.RISK,dsource=DSource.STYLEFACTOR,columns=neutral_list,max_workers=1)
    take_list = style_risk.columns.tolist()
    for name in take_list:
        dat[name] = style_risk[name].unstack()
    dat = align_data(dat)
    return dat


def load_data(factor_dict,holding_period,benchmark_index='zz500',easy_test=False,neutral_list=None):  
    """
    index_lookup = {'zz500': '000905.SH', 'zz800': '000906.SH', 'sz50': '000016.SH', 'hs300': '000300.SH'}
    style_list = ['EarningsYield','Value','Liquidity','NonLinearSize','Volatility','Size','Momentum','Beta','Leverage']
    test_universe = ['index_50','index_300','index_500','risk_universe','alpha_universe']
    """
    tic = time.time()
    data_dict = {}  
    print ('-'*5+'  Loading data  '+'-'*5)
    if type(factor_dict)==pd.Series:
        factor_dict = pd.DataFrame(factor_dict)
        factor_dict.columns = ['dummy']
        factor_dict = factor_dict.unstack()['dummy'] if len(factor_dict.columns)==1 else factor_dict
        factor_dict = factor_dict.dropna(how='all')
        
    if len(factor_dict.columns)==1:
        factor_dict = factor_dict.unstack()[factor_dict.columns.tolist()[0]]            
        factor_dict = factor_dict.dropna(how='all')
        
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0).tolist()

    start_date,end_date = factor_dict.index[0],factor_dict.index[-1]
    prev_start_date = fdate_list_dt[max(fdate_list_dt.index(start_date)-1,0)]
    
    ### market data 
    print('Getting return data')
    h5_md = IO.read_data([prev_start_date,end_date],['close','adjfactor'],ftype=FType.MD,dsource=DSource.WIND,max_workers=1)
    h5_md['close_adj'] = h5_md['close']*h5_md['adjfactor']
    stock_close = h5_md['close_adj'].unstack()
    return_df = stock_close/stock_close.shift(1)-1
    holding_period_ret = stock_close.shift(-1*holding_period)/stock_close-1
    
    # Benchmark data    
    print('Getting benchmark data')
    h5_index = IO.read_data([prev_start_date,end_date],['close'],ftype=FType.MD,dtype=DType.INDEX,dsource=DSource.WIND,max_workers=1)
    index_lookup = {'zz500': '000905.SH', 'zz800': '000906.SH', 'sz50': '000016.SH', 'hs300': '000300.SH'}
    bmk_price =  (h5_index.unstack()['close'])[index_lookup[benchmark_index]]
    benchmark_ret = bmk_price/bmk_price.shift(1)-1
    
    # SSO List
    print('Getting stock filter data') #!check runtime
    h5_filter = IO.read_data([start_date,end_date],ftype=FType.UNIV,dsource=DSource.OPTM,max_workers=1)
    universe_name = 'filter_sso'
    stock_filter = h5_filter[universe_name].unstack().fillna(value=False)

    if not easy_test:
        print('Getting style and industry data')
        neutral_list = ['Size','Industry'] if neutral_list is None else neutral_list
        neutral_dict = get_risk_data(start_date,end_date,neutral_list)
        data_dict['neutral_dict'] = neutral_dict 
        
    data_dict['factor_dict'] = factor_dict
    data_dict['stock_filter'] = stock_filter
    data_dict['return_df']   = return_df
    data_dict['benchmark_ret'] = benchmark_ret
    data_dict['holding_period_ret'] = holding_period_ret
    data_dict['bmk_price'] = bmk_price
    data_dict['stock_close'] = stock_close

    
    print ('Align data')
    data_dict = align_data(data_dict)
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*30)
    
    return data_dict


"""因子数据处理部分"""

def DataNormalize(factor_dict):
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)
    return factor_dict

def median_filter(factor_dict,mad=3,winsor=False):
    factor_mat = factor_dict.values
    dm = np.nanmedian(factor_mat,axis=1)
    dm1 = np.nanmedian(abs((factor_mat.T - dm).T),axis=1)
    date_num,stock_num = factor_mat.shape
    fac_ub = pd.DataFrame(np.tile(dm + mad * dm1,[stock_num,1]).T,index=factor_dict.index,columns=factor_dict.columns)
    fac_lb = pd.DataFrame(np.tile(dm - mad * dm1,[stock_num,1]).T,index=factor_dict.index,columns=factor_dict.columns)
    if winsor:
        factor_dict[factor_dict>fac_ub] = np.nan
        factor_dict[factor_dict<fac_lb] = np.nan
    else:
        factor_dict[factor_dict>fac_ub] = fac_ub
        factor_dict[factor_dict<fac_lb] = fac_lb
    return factor_dict
    
def NormWinsor(factor_dict,bound=3,winsor=False):
    
    factor_dict = median_filter(factor_dict,mad=bound)
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)
    return factor_dict
#########################################################################################


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
    #tic = time.time()
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
    easy_seg_return = pd.DataFrame(easy_seg_return,columns=name_pool_mat,index =date_list )
    name_pool = ['Q'+str(i+1) for i in range(int(segment_num))]
    easy_seg_return = easy_seg_return[name_pool] # sort it back to Q1-Q5 
    start_ind = easy_seg_return.any(axis=1)
    easy_seg_return['Benchmark'] = bmk_hpr_daily
    easy_seg_return['Benchmark'][~start_ind] = np.nan 
    max_q = easy_seg_return[[name_pool[0],name_pool[-1]]].mean().argmax()
    min_q = easy_seg_return[[name_pool[0],name_pool[-1]]].mean().argmin()
    ls_type =  max_q +'-'+min_q
    easy_seg_return[ls_type] = easy_seg_return[max_q]-easy_seg_return[min_q]
    #toc = time.time()
    #print (str((round((toc-tic),2)))+'s ellapsed')
    return easy_seg_return



#########################################################################################

def max_drawdown(capital_line):
    """输入: 1. date_line: 日期序列   2.capital_line: 账户价值序列
       输出: 最大回撤及开始日期和结束日期            """
    mdd_end = np.argmax(np.maximum.accumulate(capital_line) - capital_line) # end of the period
    if mdd_end==0:  # 假如累计收益序列为1，则退出
        return np.nan
    mdd_start = np.argmax(capital_line[:mdd_end]) # start of period    
    mdd  = 1- capital_line[mdd_end]/capital_line[mdd_start]
    return mdd    

def PerformanceMeasure(seg_return,holding_period=1,compound_type='cumsum'):
    segment_num = seg_return.shape[1]
    check_ind = np.isfinite(seg_return).sum(axis=1)==segment_num
    complete_ind =  check_ind[check_ind].index
    seg_return = seg_return.loc[complete_ind]
    date_num = seg_return.shape[0]
    date_1yr = 240
    if compound_type=='cumsum':
        seg_return_cum = seg_return.cumsum()
        Ret_Annual = seg_return.mean()*date_1yr
    elif compound_type=='cumprod':
        seg_return_cum = (seg_return+1).cumprod() - 1
        Ret_Annual = ((seg_return_cum.iloc[-1,:]+1)**(date_1yr/date_num)-1)
    Ret_Excess = Ret_Annual-Ret_Annual['Benchmark']
    vol_take_ind = [i%holding_period==0 for i in range(date_num)]
    Vol_Annual = seg_return[vol_take_ind].std()*np.sqrt(date_1yr)
    Tracking_Error = seg_return[vol_take_ind].subtract(seg_return[vol_take_ind]['Benchmark'],axis=0).std(axis=0)*np.sqrt(date_1yr)
    MDD = pd.DataFrame(list(map(max_drawdown,(seg_return_cum+1).T.values)),index = seg_return_cum.columns)
    SharpeRatio = Ret_Annual/Vol_Annual
    InfoRatio = Ret_Excess/Tracking_Error
    PerfMeasure = pd.concat([Ret_Annual,Vol_Annual,SharpeRatio,Ret_Excess,Tracking_Error,InfoRatio,MDD],axis=1)
    PerfMeasure.columns = ['Return(Ann.)','Vol(Ann.)','Sharpe Ratio','Excess Return','Tracking Error','IR','MaxDD']
    return PerfMeasure



#########################################################################################


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

def factor_corr_with_style(factor_dict,neutral_dict):
    factor_corr = pd.DataFrame()
    for fac in neutral_dict:
        if fac != 'Industry':
            factor_corr[fac] = factor_dict.corrwith(neutral_dict[fac],axis=1)
    return factor_corr


def IC_decay_test(factor_dict,holding_period_ret,holding_period,max_lag=3):
    """IC Decay Test:
       max_lag:(int) number of holding period after factor data was observed
       Correlation: IC(T), Return(T+1:T+1+Holding_Period) 
       Correlation for all days 
    """
    total_rebal = int(factor_dict.shape[0]/holding_period)
    max_lag = total_rebal if max_lag>total_rebal else max_lag # control for input error
    lag_list = [(i)*holding_period for i in range(-3,max_lag+1)]
    IC_ts = np.empty([len(factor_dict),len(lag_list)])
    for i in range(len(lag_list)):
        lag_ret = holding_period_ret.shift(-1*lag_list[i]) #  
        IC_ts[:,i] = factor_dict.corrwith(lag_ret,axis=1)
    lag_list_name = []
    for i in lag_list:
        if i<0:
            lag_list_name.append(str(i)+'d')
        elif i>=0:
            lag_list_name.append(str(i+holding_period)+'d')
    IC_Decay = pd.DataFrame(np.nanmean(IC_ts,axis=0),index=lag_list_name,columns=['IC Decay'])   
    Alpha_ts = factor_dict.corrwith(holding_period_ret,axis=1)*holding_period_ret.std(axis=1)/holding_period
    Alpha_cumsum = pd.DataFrame(Alpha_ts.cumsum(),columns=['Alpha (IC*Dispersion)'])
    return IC_Decay,Alpha_cumsum

def IC_duration_test(factor_dict,stock_close):
    duration_list = [-20,-10,-5,-3,-1,1,3,5,10,20]
    ret_dict = {}
    for i in duration_list:
        if i<0:
            ret_dict[i] = stock_close/stock_close.shift(-1*i)-1
        if i>0:
            ret_dict[i] = stock_close.shift(-1*i)/stock_close-1
    IC_ts = pd.DataFrame()
    for i in duration_list:
        IC_ts[i] = factor_dict.corrwith(ret_dict[i],axis=1)
    lag_list_name = [str(i)+'d' for i in duration_list]
    IC_Duration = pd.DataFrame(np.nanmean(IC_ts,axis=0),index=lag_list_name,columns=['IC Decay'])   
    return IC_Duration


#########################################################################################

"""因子中性化"""


def np_regression_res(y,x):
    res = np.array([np.nan]*len(y))    
    mask = np.isfinite(y) & np.isfinite(x.sum(axis=1))
    if sum(mask)==0:
        return res
    ols1  = sm.OLS(y[mask],x[mask]).fit()
    res[mask] = ols1.resid
    return res

def factor_neutralize_mat(factor_dict,neutral_dict,neutral_list,Normalize=True):
    """
    Generic Version of Neutralizer - but still assume everything aligned
    data_dict: dictionary of dataframe / or dataframe with time series 
    neutral_list: list of variable to be neutralized( dict: dataframe / dataframe: series- reformat to matrix)
    Normalize: Choose to normalize residual cross sectionally
    
    """
    print ('-'*5+'   Get Factor Neutralized   '+'-'*5)
    tic = time.time()
    date_num, stock_num = factor_dict.shape
    ind_neu = True if 'industry' in [i.lower() for i in neutral_list] else False
    factor_num = len(neutral_list)-1 if ind_neu else len(neutral_list)
    print ('Neutralize on: ', str(neutral_list))
    x_mat = np.ones([factor_num+1,date_num,stock_num]) # including intercept
    factor_mat = factor_dict.values
    i=0
    if type(neutral_dict)==dict:
        for neu_name in neutral_list:
            if neu_name.lower() != 'industry':
                i=i+1 # leave the first place for intercept
                x_mat[i,:,:] = neutral_dict[neu_name].values
    elif type(neutral_dict)==pd.DataFrame:
        print ('Pass in dataframe')
        for neu_name in neutral_list:
            if neu_name.lower() != 'industry':
                i=i+1 # leave the first place for intercept
                x_mat[i,:,:] = np.tile(neutral_dict[neu_name].values,[factor_dict.shape[1],1]).T
    res = np.empty([date_num,stock_num])
    res[:] = np.nan
    if ind_neu == False:
        for date_idx in range(date_num):
            try:
                res[date_idx,:] = np_regression_res(factor_mat[date_idx,:],x_mat[:,date_idx,:].T)
            except:
                continue
    elif ind_neu == True:   
        print ('Neutralize with industry take some time')
        ind_mat = neutral_dict['Industry'].values
        ind_min_num = 3
        for date_idx in range(date_num):
            try:
                ind_dum = pd.get_dummies(ind_mat[date_idx,:]).values
                ind_take = np.sum(ind_dum,axis=0)>=ind_min_num
                ind_dum_take = ind_dum[:,ind_take]
                x = np.column_stack([x_mat[:,date_idx,:].T,ind_dum_take])
                res[date_idx,:] = np_regression_res(factor_mat[date_idx,:],x)
            except:
                continue
    factor_residual = pd.DataFrame(res,columns = factor_dict.columns,index=factor_dict.index)
    factor_residual = NormWinsor(factor_residual) if Normalize==True else factor_residual
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
    date_num,stock_num = factor_dict.shape
    stock_ts = np.isfinite(factor_dict).sum(axis=1)
    return stock_ts

def IC_stats(IC_combined):
    ICIR = IC_combined.mean()/IC_combined.std()#*np.sqrt(240)
    IC_combined_stats = pd.DataFrame([IC_combined.mean(),IC_combined.std(),ICIR])
    IC_combined_stats.index = ['IC_mean','IC_std','ICIR']
    return IC_combined_stats



def excel_saver(output_dict,excel_name):
    writer = pd.ExcelWriter(excel_name,engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer,sheet_name=key)
    writer.save()
    return 


###########################################################################################

"""Main Function"""

def factor_backtest(factor_dict,holding_period,factor_name,use_factor_type='original',
                    benchmark_index='zz500',test_universe=None,provide_data=None,
                    neutral_list=None,easy_test=True,result_folder=None):

    print ('-'*60)
    print ('Factor Backtest  -  '+str(factor_name))
    
    if result_folder == None:
        result_folder = 'S:\\Quant\\backtest\\backtest_output\\'
    factor_name = 'TestFactor' if factor_name==None else factor_name
    output_folder = result_folder + factor_name + '\\'    
    if (not os.path.exists(output_folder)):
        os.mkdir(output_folder)     
    print("Test Result Saved in: " + output_folder)
        
    if provide_data is not None:
        try:
            print ('Align proivded data')
            dummy = provide_data.pop('factor_dict',None)
            if type(factor_dict)==pd.Series:
                factor_dict = pd.DataFrame(factor_dict)
                factor_dict.columns = [factor_name]
            factor_df = factor_dict.unstack()[factor_name] if len(factor_dict.columns)==1 else factor_dict
            data_dict = align_data({**provide_data,**{'factor_dict':factor_df}})
        except:
            print ('Wrong input, reload data...')
            data_dict = load_data(factor_dict,holding_period,benchmark_index,easy_test,test_universe)
    else:
        data_dict = load_data(factor_dict,holding_period,benchmark_index,easy_test,test_universe)
        
    factor_dict,benchmark_ret = data_dict['factor_dict'],data_dict['benchmark_ret']
    stock_filter,holding_period_ret = data_dict['stock_filter'],data_dict['holding_period_ret']
    stock_close,bmk_price = data_dict['stock_close'],data_dict['bmk_price']
    
    IC_ts = pd.DataFrame()
    IC_ts['IC_original'] = factor_dict.corrwith(holding_period_ret,axis=1)
        
    """Data Cleaning"""
    #factor_dict_std = NormWinsor(factor_dict)
    #IC_ts['IC_standardized'] = factor_dict_std.corrwith(holding_period_ret,axis=1)

    if not easy_test:
        neutral_dict = data_dict['neutral_dict']
        neutral_list = ['Size','Industry'] if neutral_list is None else neutral_list
        factor_neutralized = factor_neutralize_mat(factor_dict,neutral_dict,neutral_list,Normalize=True)
        IC_ts['IC_neutralized'] = factor_neutralized.corrwith(holding_period_ret,axis=1)
        #factor_corr = factor_corr_with_style(factor_dict,neutral_dict)
    """    
    if save2h5 == True:
        print ('Saving neutralized results to H5')
        save_name_neu = factor_name+'_neutralized.h5' # Save neutralized factor
        DF2H5(factor_neutralized,factor_name,output_folder,save_name_neu) # save neutralized result to h5c
        save_name_std = factor_name+'_standardized.h5' # Save standardized factor 
        DF2H5(factor_dict_std,factor_name,output_folder,save_name_std) # save neutralized result to h5c 
    """    
    if use_factor_type == 'standardized':
        factor_dict = factor_dict_std
 
    if use_factor_type=='neutralized':
        factor_dict = factor_neutralized

    sum_df = SummaryTable(factor_name,factor_dict,holding_period,test_universe)
    stock_count = factor_coverage(factor_dict)
    fac_dist = FactorDist(factor_dict,stock_filter)
        
    print ('Segment Test')
    tic = time.time()
    seg_return_30 = easy_segment_test(factor_dict,holding_period_ret,holding_period,30,benchmark_ret)
    seg_return_30_stat = PerformanceMeasure(seg_return_30)
    seg_return_30_stat_year = seg_return_30.groupby(seg_return_30.index.year).apply(PerformanceMeasure)
    factor_auto_correlation = factor_score_correlation(factor_dict,holding_period)
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')    
        
    print ('IC Decay Test')
    tic = time.time()
    IC_Decay,Alpha_cumsum = IC_decay_test(factor_dict,holding_period_ret,holding_period,max_lag=5)
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')

    IC_ts_stats = IC_stats(IC_ts)
    
    output_dict = {'summary_info':sum_df,'distribution':fac_dist,'stock_count':stock_count,
                   'seg_return_30':seg_return_30,'seg_return_30_stat':seg_return_30_stat,
                   'seg_return_30_stat_year':seg_return_30_stat_year,
                   'factor_auto_correlation':factor_auto_correlation,
                   'IC_ts':IC_ts,'IC_ts_stats':IC_ts_stats ,'IC_Decay':IC_Decay,'Alpha_cumsum':Alpha_cumsum}
    
    #if not easy_test:                   
    #    output_dict['factor_corr'] = factor_corr 
            
    """Write to Excel"""
    excel_name = output_folder+'FactorBacktest_'+str(factor_name)+'.xlsx'
    print ('Saving Results to Excel\n',excel_name)
    excel_saver(output_dict,excel_name)
        
    generate_pdf(excel_name,output_folder,easy_test)
        
    print ('Factor Backtest Done')    
    print ('-'*40)
        
    return 


     
"""
from multifactor.backtest.factor_test import factor_backtest
factor_dict = IO.read_data([20160101,20180329],alt='S:\\Quant\\data\\factor\\zsj\\fundamental\\quality\\quality_minus_junk.h5')
holding_period,factor_name = 10, 'quality_minus_junk'
factor_backtest(factor_dict,holding_period,factor_name)


lp = LineProfiler()
lp_wrapper = lp(factor_backtest)
lp_wrapper(factor_dict,holding_period,factor_name)
lp.print_stats()




"""














