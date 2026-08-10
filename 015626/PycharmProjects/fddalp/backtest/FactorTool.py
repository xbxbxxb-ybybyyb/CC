# -*- coding: utf-8 -*-
"""
Factor Process Tools:
    Neutralizer
    Standardizer
    Normalizer
"""


"""
risk_list = ['Size','Momentum']
start_date,end_date = 20090101,20180108
neutral_dict = get_risk_data(start_date,end_date,risk_list)
factor_dict = neutral_dict['Momentum']
neutral_list = ['Size']
factor_resid = factor_neutralize_mat(factor_dict,neutral_dict,neutral_list,Normalize=True)
""" 

import numpy as np
import pandas as pd
import statsmodels.api as sm
from functools import reduce
from scipy import linalg
import scipy.optimize as optimize
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import time
import datetime as dt
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('ggplot')
from multifactor.backtest import FactorTest
import pickle
from sklearn import linear_model
#import pprint
import os

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

    
def mi2df(dat,alpha_ind,norm=None):
    print ('-'*20,'\n1.concat')
    dat_uni = pd.concat([dat,alpha_ind],axis=1)
    print ('2.chop by alpha universe')
    dat_uni = dat_uni[dat_uni['alpha_universe']==True]
    dat_dict = {}
    print ('3. unstack from mi')
    for col in dat.columns:
        print (col)
        dat_dict[col] = dat_uni[col].unstack()
    if norm is not None:
        if norm=='score':
            print ('4. normalizing using score')
            for col in dat.columns:
                dat_dict[col] = NormWinsor(dat_dict[col])
        if norm=='rank':
            print ('4. normalzing using rank')
            for col in dat.columns:
                dat_dict[col] = RankZscore(dat_dict[col])                
    print ('done\n','-'*20)
    return dat_dict



def get_risk_data(start_date,end_date,risk_list=None):
    dat = {}
    #'EarningsYield','Value','Liquidity','NonLinearSize','Volatility','Size','Momentum','Beta','Leverage','Industry'
    
    if risk_list == None:
        style_risk = IO.read_data([start_date,end_date],ftype=FType.RISK,dsource=DSource.STYLEFACTOR,max_workers=1)
    else:
        style_risk = IO.read_data([start_date,end_date],ftype=FType.RISK,dsource=DSource.STYLEFACTOR,columns=risk_list,max_workers=1)
    take_list = style_risk.columns.tolist()
    for name in take_list:
        dat[name] = style_risk[name].unstack()
    dat = align_data(dat)
    return dat


#########################################################################################
"""因子数据处理部分"""

def FactorTypeCheck(factor_dict):
    """ 自动判别因子是否为1，0,-1 的标签矩阵"""
    max_min = [factor_dict.max().max(),factor_dict.min().min()]
    factor_type = 'Categorical' if max_min in [[0,-1],[0,1],[-1,1]] else 'Numerical'
    return factor_type

def DataNormalize(factor_dict):
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)
    return factor_dict



def median_filter(factor_df,mad=3,winsor=False):
    factor_dict = factor_df.copy()
    factor_mat = factor_dict.values
    #dm = np.nanmedian(factor_mat,axis=1)
    dm = factor_dict.median(axis=1)
    dm1 = (factor_dict.subtract(dm,axis=0)).abs().median(axis=1).values
    #dm1 = np.nanmedian(abs((factor_mat.T - dm).T),axis=1)
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
    

def NormWinsor(factor_df,bound=3,winsor=False):
    factor_dict = factor_df.copy()
    factor_dict = median_filter(factor_dict,mad=bound,winsor=winsor)
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)
    return factor_dict


"""
def NormWinsor(factor_dict,bound=3):
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)
    factor_dict[factor_dict>bound] = bound
    factor_dict[factor_dict<-1*bound] = -1*bound
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)    
    return factor_dict
"""               

def RankZscore(factor_dict):
    # rank and take zscore 
    factor_rank = factor_dict.rank(axis=1)
    factor_rank_zscore = factor_rank.subtract(factor_rank.mean(axis=1),axis=0).divide(factor_rank.std(axis=1,ddof=0),axis=0)
    #factor_dict[factor_dict>bound] = bound
    #factor_dict[factor_dict<-1*bound] = -1*bound
    #factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)    
    return factor_rank_zscore



def NormWinsorN(factor_dict,bound=3,max_iter=10):
    """loss of information"""
    factor_dict = NormWinsor(factor_dict,bound=3)
    max_diff = (factor_dict.max(axis=1) - factor_dict.min(axis=1)).max()
    iter_num = 1
    print ('iteration '+str(iter_num)+': max diff '+str(np.round(max_diff,2)))
    while (max_diff > bound*2.2):
        iter_num = iter_num + 1
        if iter_num>max_iter:
            print ('max iteration done')
            break
        else:
            factor_dict = NormWinsor(factor_dict,bound=3)
            print ('iteration '+str(iter_num)+': max diff '+str(np.round(max_diff,2)))
            max_diff = (factor_dict.max(axis=1) - factor_dict.min(axis=1)).max()
    print ('iteration x: max diff '+str(np.round(max_diff,2)))
    return factor_dict



def filter_extreme(factor_dict,std_num=3):
    """
    """
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)
    factor_dict[np.abs(factor_dict)>std_num] = np.nan
    return factor_dict


def normalize_fillna(factor_dict,alpha_universe=None):    
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)
    
    if alpha_universe is not None:
        date_list = list(set(factor_dict.index).intersection(set(alpha_universe.index)))
        stock_list = list(set(factor_dict.columns).intersection(set(alpha_universe.columns)))
        date_list.sort()
        stock_list.sort()
        factor_dict = factor_dict.loc[date_list][stock_list]
        alpha_universe = alpha_universe.loc[date_list][stock_list]
        factor_dict[alpha_universe] = factor_dict[alpha_universe].fillna(0)
    return factor_dict


def Standard_Process(factor_dict,nan_ind=None,stock_industry=None,FillNaN=False):
    """ nan_ind:  可以根据用户输入决定筛选条件 - 比如VOLUME>0
        True： 1. 去除没有收益的日子
        False: 1. 去除没有收益的日子  2. 标准化
    """ 
    factor_type = FactorTypeCheck(factor_dict)
    
    if factor_type =='Categorical':  
        print ('Factor Type: Categorical --> No Processing')        
    
    elif factor_type == 'Numerical':
        if nan_ind != None:
            factor_dict[~nan_ind] = np.nan
            factor_dict[~np.isfinite(factor_dict)] = np.nan #将inf,-inf,nan 取代为nan
            
        print ('Box_skew_plot')
        factor_dict = BoxSkewPlot(factor_dict) #极值处理
        if FillNaN == True and stock_industry != None and nan_ind != None:
            print ('Fill Nan with Industry Median')
            factor_dict = Factor_Fillna(factor_dict,stock_industry,nan_ind)
        print ('Normalize')
        factor_dict = DataNormalize(factor_dict)
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
    return pd_process

    
    
def Factor_Fillna(factor_dict,stock_industry,nan_ind):
    """ 缺失值处理：
    得到新的因子暴露度序列后，将因子暴露度缺失的地方设为行业中位数。
    # 因子暴露度缺失定义为无法获取此因子 而非该股票不可交易  - 用处理过的因子填充
    # nan_ind 为股票停牌信息  1 为真停牌 或者没上市/ 则不填充
    
    """
    fill_ind = np.isnan(factor_dict)[~nan_ind] # 所有NAN * 非停牌的NAN = 缺失数据
    industry_median = pd.DataFrame(index=factor_dict.index,columns=[i for i in range(31)])
    for date in stock_industry.index:
        industry_list = stock_industry.loc[date]
        industry_median.loc[date] = [i[0] for i in pd.DataFrame(factor_dict.loc[date]).groupby(industry_list).median().values]
    Fill_median = factor_dict.copy()
    for i in [i for i in range(31)]:    # loop industry
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

def roll_generator(factor,fac_name,sign_ind=1,roll_list=None,min_data=0.8,func='mean'):
    roll_dict={}
    if roll_list is None:
        if func=='mean':
            roll_list = [1,5,20,40,120]
        if func=='std':
            roll_list = [5,20,40,120]
    for roll_win in roll_list:
        if roll_win ==1:
            roll_dict[fac_name+'_'+str(roll_win)+'d'] = sign_ind*NormWinsor(factor)
        else:
            if func=='mean':
                roll_dict[fac_name+'_'+str(roll_win)+'d'] = sign_ind*NormWinsor(factor.rolling(roll_win,int(min_data*roll_win)).mean())
            if func=='std':
                roll_dict[fac_name+'_'+str(roll_win)+'d'] = sign_ind*NormWinsor(factor.rolling(roll_win,int(min_data*roll_win)).std())
    return roll_dict



##############################################################################
### Regression Related

def np_regression_res(y,x):
    res = np.array([np.nan]*len(y))    
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)==0:
        return res
    ols1  = sm.OLS(y[mask],x[mask]).fit()
    res[mask] = ols1.resid
    return res

def np_wls_res(y,x,weight):
    res = np.array([np.nan]*len(y))    
    #mask = np.isfinite(y) & np.isfinite(x.sum(axis=1))
    mask = np.isfinite(y+x.sum(axis=1)+weight)
    if np.count_nonzero(mask)==0:
        return res
    ols1  = sm.WLS(y[mask],x[mask],weight[[mask]]).fit()
    res[mask] = ols1.resid
    return res

def np_wls_tstat(y,x,w):
    tstat = np.array([np.nan]*x.shape[1])    
    #mask = np.isfinite(y) & np.isfinite(x.sum(axis=1))
    mask = np.isfinite(y+x.sum(axis=1)+w)
    if np.count_nonzero(mask)==0:
        return tstat
    ols1  = sm.WLS(y[mask],x[mask],w[[mask]]).fit()
    tstat = ols1.tvalues
    return tstat


"""
from line_profiler import LineProfiler
lp = LineProfiler()
lp_wrapper = lp(factor_neutralize_mat)
lp_wrapper(neutral_dict['rev_minute'][1],neutral_dict,['rev_20'],Normalize=True)
lp.print_stats()
"""

def factor_neutralize_mat(factor_dict,neutral_dict,neutral_list=None,Normalize=True):
    """
    Generic Version of Neutralizer - but still assume everything aligned
    data_dict: dictionary of dataframe / or dataframe with time series 
    neutral_list: list of variable to be neutralized( dict: dataframe / dataframe: series- reformat to matrix)
    Normalize: Choose to normalize residual cross sectionally
    
    """
    
    print ('-'*5+'   Get Factor Neutralized   '+'-'*5)
    tic = time.time()
    if type(neutral_dict)==pd.DataFrame:
        neutral_dict = {'neu_factor':neutral_dict}
        neutral_list = ['neu_factor']
    comb_tank = align_data({'factor':factor_dict,'neutral_dict':neutral_dict})
    factor_dict = comb_tank['factor']
    neutral_dict = comb_tank['neutral_dict']
    neutral_list = list(neutral_dict.keys()) if neutral_list is None else neutral_list
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

def batch_neutral(dat_dict,style_data,neutral_list=['Size','Industry'],Normalize=True):
    print ('align')
    neutral_dict = align_data({**style_data,**dat_dict})
    dat_dict_neu = {}
    print ('neutralize')
    for col in dat_dict:
        print (col)
        dat_dict_neu[col] = factor_neutralize_mat(neutral_dict[col],neutral_dict,neutral_list)
    return dat_dict_neu



def batch_test(factor_tank,data_dict,holding_period,test_path):
    fail_list = []
    print ('Factor Testing:\n',str(list(factor_tank.keys())))
    print ('holding_period:%d'%(holding_period))
    data_dict['holding_period_ret'] = data_dict['close_adj'].shift(-1*holding_period)/data_dict['close_adj']-1
    for factor_name in factor_tank:
        print (factor_name)
        try:
            FactorTest.FactorEntryTest(factor_tank[factor_name].dropna(axis=0,how='all'),holding_period,factor_name,
                                       provide_data=data_dict,result_folder=test_path)
            print ('done')
        except:
            print ('fail')
            fail_list.append(factor_name)
    print ('All Done.....')
    return fail_list


#test_factor_folder(h5_path=h5_path,holding_period=20,test_pkl_path=factor_test_path,result_folder=report_path)


def test_factor_folder(h5_path,holding_period,fac_list=None,test_pkl_path=None,result_folder=None):
    print ('loading factor data from pickle')
    if test_pkl_path is None:
        save_dict = read_factor_test_pickle()
    else:
        save_dict = read_pickle(test_pkl_path)
    print ('holding_period:%d'%(holding_period))
    save_dict['holding_period_ret'] = save_dict['close_adj'].shift(-1*holding_period)/save_dict['close_adj']-1
    file_list = os.listdir(h5_path)
    fac_list = [i[:-3] for i in file_list if i[-3:]=='.h5'] if fac_list is None else fac_list 
    print ('factor list:\n',str(fac_list))
    for fac in fac_list:
        print (fac)
        try:
            fac_path = h5_path + fac + '.h5'
            print ('loading factor')
            factor_dict = IO.read_data([20090101,20201231],alt=fac_path)
            print ('factor test')
            FactorTest.FactorEntryTest(factor_dict,holding_period,fac,provide_data=save_dict,result_folder=result_folder)
            print ('test done')
        except:
            print ('error')
    print ('all done')
    return 


def batch_normwinsor(factor_tank):
    print ('batch normalize:\n',str(list(factor_tank.keys())))
    factor_dict = {}
    if type(factor_tank) == dict:
        fac_list = list(factor_tank.keys())
    if type(factor_tank) == pd.DataFrame:
        fac_list = factor_tank.columns
    for fac in fac_list:
        print (fac)
        if fac!='alpha_universe':
            try:
                if type(factor_tank) == dict:
                    factor_dict[fac] = NormWinsor(factor_tank[fac])
                else:
                    factor_dict[fac] = NormWinsor(factor_tank[fac].unstack())
            except:
                print ('fail')
    print ('done.....')
    return factor_dict


def batch_read(fac_path,sdate=None,edate=None,fac_list=None,dat_type='matrix'):
    fac_list = [i[:-3] for i in os.listdir(fac_path) if i[-2:]=='h5'] if fac_list is None else fac_list
    sdate = 20090101 if sdate is None else sdate
    edate = 20201231 if edate is None else edate
    fac_dict = {}
    print ('loading factor:\n',str(fac_list))
    for fac in fac_list:
        print (str(fac_list.index(fac)+1)+'/'+str(len(fac_list))+' --- '+ fac)
        try:
            if dat_type=='matrix':
                fac_dict[fac] = IO.read_data([sdate,edate],alt=fac_path+fac+'.h5')[fac].unstack()
            elif dat_type=='mi':
                fac_dict[fac] = IO.read_data([sdate,edate],alt=fac_path+fac+'.h5')[fac]
        except:
            print ('error')
    print ('done')
    return fac_dict




def factor_neutralize_mat2(factor_dict,neutral_dict,neutral_list,Normalize=True):
    """
    Generic Version of Neutralizer - but still assume everything aligned
    data_dict: dictionary of dataframe
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
    for neu_name in neutral_list:
        if neu_name.lower() != 'industry':
            i=i+1 # leave the first place for intercept
            x_mat[i,:,:] = neutral_dict[neu_name].values
    
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
    factor_residual = RankZscore(factor_residual) if Normalize==True else factor_residual
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*20)
    return factor_residual

"""
def Factor_Neutralize_mat(factor_dict,data_dict,Normalize=True):
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
"""


"""Beta and Hsigma"""
def reg_beta_resvol(y,x,min_size=0):
    mask = np.isfinite(y) & np.isfinite(x.sum(axis=1))
    if sum(mask) <= min_size:
        return [np.nan]*x.shape[1],np.nan
    ols1  = sm.OLS(y[mask],x[mask]).fit()
    beta = ols1.params
    res_vol = np.std(ols1.resid)
    return beta,res_vol


def rolling_regression(y,x,reg_list,reg_period=None,min_size=None,normalize=False):
    reg_period =240 if reg_period==None else reg_period
    min_size = int(reg_period/4) if min_size == None else min_size
    stock_list,date_list = y.columns.tolist(),y.index.tolist()
    date_num,stock_num = y.shape    
    factor_num = len(reg_list)
    beta_mat,resvol_mat = np.zeros([factor_num+1,date_num,stock_num]),np.zeros([date_num,stock_num])
    beta_mat[:],resvol_mat[:] = np.nan, np.nan
    iter_num = date_num - reg_period + 1
    print ('Rolling Regression on: ', str(reg_list))
    y_mat = y.values
    x_mat = np.ones([factor_num+1,date_num,stock_num]) # including intercept
    i=0
    if type(x)==dict:
        print ('Pass in dictionary')
        for reg_name in reg_list:
            i=i+1 # leave the first place for intercept
            x_mat[i,:,:] = x[reg_name].values
    elif type(x)==pd.DataFrame:
        print ('Pass in dataframe... will repeat n-times')
        for reg_name in reg_list:
            i=i+1 # leave the first place for intercept
            x_mat[i,:,:] = np.tile(x[reg_name].values,[stock_num,1]).T
    print ('-'*5)
    for iter_n in range(iter_num):
        try:
            iter_idx = iter_n+reg_period
            print ('Iteration ',iter_n,'/',iter_num,' ',str(date_list[iter_idx]))
            Y = y_mat[iter_n:iter_idx,:]
            X = x_mat[:,iter_n:iter_idx,:]
            #if half_life is not None:
            #    X = (X.T*w).T
            #    Y = (Y.T*w).T
            for i in range(stock_num):
                #print (i)
                beta_mat[:,iter_idx,i],resvol_mat[iter_idx,i] = reg_beta_resvol(Y[:,i],X[:,:,i].T,min_size) # report as end of rolling period
        except:
            print ('Not enough data')
    if factor_num>1:
        beta = {}
        for reg_name in reg_list:
            beta[reg_name]= pd.DataFrame(beta_mat[reg_list.index(reg_name)+1,:,:],index=date_list,columns=stock_list)#.dropna(axis=0,how='all')
    else:
        beta = pd.DataFrame(beta_mat[1,:,:],index=date_list,columns=stock_list)
        
    resid_vol = pd.DataFrame(resvol_mat,index=date_list,columns=stock_list)#.dropna(axis=0,how='all')  
    
    if normalize:
        print ('Normalizing')
        if factor_num>1:
            for fac_name in beta:
                beta[fac_name] = NormWinsor(beta[fac_name])
        else:
            beta = NormWinsor(beta)
        resid_vol = NormWinsor(resid_vol)
    return beta,resid_vol



###########################################################

def calc_bab(stock_close,bmk_price,vol_win=60,corr_win=60,non_sync_win=3,min_pct=0.8):
    print ('calcing bab: vol_win=%d corr_win=%d non_sync_win=%d'%(vol_win,corr_win,non_sync_win))
    stk_ret = stock_close/stock_close.shift(1)-1
    mkt_ret = bmk_price/bmk_price.shift(1)-1
    stk_vol = stk_ret.rolling(window=vol_win,min_periods=int(vol_win*min_pct)).std()
    mkt_vol = mkt_ret.rolling(window=vol_win,min_periods=int(vol_win*min_pct)).std()
    if non_sync_win>1:
        stk_ret_roll = stk_ret.rolling(window=non_sync_win,min_periods=max(1,non_sync_win-1)).mean() # overlapping 3-day log returns for correlation 
        mkt_ret_roll = mkt_ret.rolling(window=non_sync_win,min_periods=max(1,non_sync_win-1)).mean()
    elif non_sync_win==1:
        stk_ret_roll = stk_ret
        mkt_ret_roll = mkt_ret
    print ('calc roll corr')
    corr_stk_mkt = stk_ret_roll.rolling(window=corr_win,min_periods=int(vol_win*min_pct)).corr(mkt_ret_roll)
    print ('calc bab = std_stk/std_mkt*corr(stk,mkt)')
    bab = stk_vol.divide(mkt_vol,axis=0)*corr_stk_mkt    
    print ('done')
    return bab


###########################################################
############## Rolling Regression 


def reg_res_r2_beta_multiple(y,x,min_size=0):
    res = np.zeros(len(y))
    res[:] = np.nan
    r2,beta = np.nan,np.nan
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)<min_size:
        return res,r2,beta
    ols1  = sm.OLS(y[mask],x[mask]).fit()
    res[mask] = ols1.resid
    r2 = ols1.rsquared
    beta = ols1.params[1:]
    return res,r2,beta


def calc_res_std_r2_beta_day(y,x,min_size=10):
    result_set = np.zeros(1+x.shape[1])
    result_set[:] = np.nan
    res,r2,beta = reg_res_r2_beta_multiple(y,x,min_size)
    mask = np.isfinite(res)
    res_take = res[mask]
    if len(res_take)<min_size:
        return result_set
    res_std = np.nanstd(res_take)
    result_set[:2] = [res_std,r2]
    result_set[2:] = beta
    return result_set




def reg_res_r2_beta_sm(y,x,min_size=0):
    res = np.zeros(len(y))
    res[:] = np.nan
    r2,beta = np.nan,np.nan
    #res = np.array([np.nan]*len(y))    
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)<min_size:
        return res,r2,beta
    ols1  = sm.OLS(y[mask],x[mask]).fit()
    res[mask] = ols1.resid
    r2 = ols1.rsquared
    beta = ols1.params[1]
    return res,r2,beta

def reg_res_r2_beta_np(y,x,min_size=0):
    res = np.zeros(len(y))
    res[:] = np.nan   
    r2,beta = np.nan,np.nan
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)<min_size:
        return res,r2,beta
    ols_result = np.linalg.lstsq(x[mask],y[mask])
    ols_resid = y[mask] - np.dot(ols_result[0],x[mask].T)
    res[mask] = ols_resid
    r2 = (1- ols_result[1]/(y[mask].size*y[mask].var()))[0]
    beta = ols_result[0][1]
    return res,r2,beta 


def calc_stk_coskew(stk,mkt):
    stk_skew = np.mean(stk**3)/np.std(stk)**3
    coskew1 = np.mean(stk*mkt**2)/(np.sqrt(np.mean(stk**2))*(np.mean(mkt**2)))
    coskew2 = np.mean(stk*mkt**2)/(np.std(mkt)**3)
    return stk_skew,coskew1,coskew2

def calc_kurtosis(stk):
    stk_demean = stk - np.mean(stk)     
    stk_kurtosis = np.sum(stk_demean**4)/np.sum(stk_demean**2)**2
    return stk_kurtosis


def calc_beta_skew_kurt_day(y,x,min_size=10):
    # assume x 2nd colums are numbers 
    result_set = np.zeros(7)
    result_set[:] = np.nan
    #res,r2,beta = reg_res_r2_beta_sm(y,x,min_size)
    res,r2,beta = reg_res_r2_beta_np(y,x,min_size)
    mask = np.isfinite(res)
    res_take = res[mask]
    mkt_take = x[mask,1] - np.mean(x[mask,1])
    b = len(res_take)
    if b<min_size:
        return result_set
    res_std = np.nanstd(res_take)
    resid_skew,resid_coskew1,resid_coskew2 = calc_stk_coskew(res_take,mkt_take)
    stk_kurtosis = calc_kurtosis(y[mask])
    result_set = [res_std,r2,beta,resid_skew,resid_coskew1,resid_coskew2,stk_kurtosis]
    return result_set


def calc_stk_roll_wrapper(func,col_name,stk_name,stock_return,x_df,reg_period,min_size):
    y_mat = stock_return[stk_name].values
    x_mat = x_df.values
    date_list = stock_return.index
    date_num  = len(date_list)
    collector_mat = np.ones([date_num,len(col_name)])
    collector_mat[:] = np.nan
    iter_num = date_num - reg_period + 1
    fail_list = []
    for iter_start in range(iter_num):
        try:
            iter_end = iter_start + reg_period
            #print ('Iteration ',iter_start+1,'/',iter_num,' ',str(date_list[iter_end-1]))
            Y = y_mat[iter_start:iter_end]
            X = x_mat[iter_start:iter_end,:]
            if np.count_nonzero(np.isfinite(Y+X.sum(axis=1)))>=min_size:
                collector_mat[iter_end-1,:] = calc_beta_skew_kurt_day(Y,X,min_size) 
        except:
            fail_date = date_list[iter_end-1]
            print (str(fail_date),'failed...')
            fail_list.append(iter_end)
    index_tuple = [date_list,[stk_name]*len(date_list)]
    mi_index = pd.MultiIndex.from_tuples(list(zip(*index_tuple)),names=['dt', 'Ticker'])         
    result_mi = pd.DataFrame(collector_mat,columns=col_name,index=mi_index )
    return result_mi

def calc_stk_wrapper(func,col_name,stock_close,mkt_ret,stock_list=None,reg_period=60,min_size=30):
    tic = time.time()
    result_list = []
    stock_list = list(stock_close.columns) if stock_list is None else stock_list
    stock_num = len(stock_list)
    stock_return = stock_close/stock_close.shift(1)-1
    x_ret = mkt_ret.copy()
    x_ret.columns=['mkt']
    x_ret['intcp'] = 1
    x_ret = x_ret[['intcp','mkt']]
    date_list = list(set(mkt_ret.index).intersection(set(stock_return.index)))
    date_list.sort()
    x_ret = x_ret.loc[date_list] 
    stock_return = stock_return.loc[date_list]
    for stk_name in stock_list:
        print (stock_list.index(stk_name)+1, '/',stock_num,'-' ,stk_name)
        result_mi = calc_stk_roll_wrapper(func,col_name,stk_name,stock_return,x_ret,reg_period,min_size)
        result_list.append(result_mi)
    result = pd.concat(result_list,axis=0)
    print(time.time()-tic)
    print ('reg_period: %d \nmin_size: %d'%(reg_period,min_size))
    return result 











#################################################################

########################################
"""For Consensus Data"""


def get_forecast_year(forecast_date,div_month=3):
    # check data time
    """ input forecast_date ( type could be timestamp/int/float)
        output focaste_year by divide month - assume to be 3"""
    f_month = forecast_date.month
    f_year = forecast_date.year
    forecast_year = f_year if f_month>=div_month else f_year-1
    return forecast_year


def remove_dulicate(df,unique_group,time_record,keep='last'):
    """ keep='last': take newest entrytime one
        keep='first': take oldest entrytime one
        """
    sort_time_option = False if keep == 'last' else True #  sort time in ascending order         
    print ('Sort within '+str(unique_group)+'\nBy '+str(time_record)+'\nKeep '+keep)
    df_unique = df.copy()
    df_unique['dt1'] = df_unique.index.get_level_values(0)
    df_unique['Ticker1'] = df_unique.index.get_level_values(1)
    df_unique = df_unique.sort_values(by=['dt1','Ticker1']+unique_group+time_record,ascending=True) # sort within group - based on entry time - latest in the end
    duplicate_idx = df_unique.groupby(['dt1','Ticker1']+unique_group).cumcount(ascending=sort_time_option) # take last one based on entrytime
    df_unique = df_unique[duplicate_idx==0] 
    df_unique = df_unique.drop(['dt1','Ticker1'],axis=1)
    new_len,old_len = len(df_unique),len(df)
    pct_remove = round((1-new_len/old_len)*100,3)
    print ('Remove duplicate: %d/%d (%s'%(old_len-new_len,old_len,pct_remove)+'%)')
    return df_unique

def find_dulicate(df,unique_group,time_record):
    df_duplicate = df.copy()
    df_duplicate['dt1'] = df_duplicate.index.get_level_values(0)
    df_duplicate['Ticker1'] = df_duplicate.index.get_level_values(1)
    print ('sort')
    df_duplicate = df_duplicate.sort_values(by=['dt1','Ticker1']+unique_group+time_record,ascending=True) # sort first
    df_duplicate['duplicate_idx'] = df_duplicate.groupby(['dt1','Ticker1']+unique_group).cumcount(ascending=False) # take last one based on entrytime
    df_duplicate = df_duplicate.drop(['dt1','Ticker1'],axis=1)
    df_duplicate = df_duplicate[df_duplicate['duplicate_idx']>0]
    return df_duplicate


def get_FY(df,year_column='RPTDATE',forward_year=1):
    df['forecast_time'] = df.index.get_level_values(0)
    df['take_year'] = df['forecast_time'].apply(get_forecast_year)
    if forward_year==1:
        df_FY = df[df['take_year']==df[year_column]]
    if forward_year==2:
        df_FY = df[df['take_year']==(df[year_column]-1)]
    df_FY = df_FY.drop(['forecast_time','take_year'],axis=1)
    return df_FY


##########################################
"""IC Tester"""
def IC_by_month(IC_ts,plot=True):
    year_list = list(set(IC_ts.index.year))
    year_list.sort(reverse=False)
    IC_month = pd.DataFrame(index=[i for i in range(1,13)])
    for year in year_list:
        IC_yr = IC_ts.loc[str(year)]
        IC_month[year] = IC_yr.groupby(IC_yr.index.month).mean()
        IC_ts.groupby(IC_ts.index.month).mean()
    if plot==True:
        """
        IC_month_year =  IC_ts.groupby(pd.TimeGrouper("M")).mean()#.dropna()
        IC_month_year.index = [i.strftime('%y-%m') for i in IC_month_year.index]
        ax2 = IC_month_year.plot(kind='bar',figsize=[13,3])#,rot=80)
        #plt.xticks([])
        plt.show()
        """
        IC_month.fillna(0).plot(kind='bar',figsize=[11.0,2],title='IC by month')
        plt.legend(bbox_to_anchor=(1,1), loc=2, borderaxespad=0.)
        #IC_ts.groupby(IC_ts.index.month).mean().plot(kind='bar',figsize=[11,2],title='IC All Time')
        plt.show()
    return IC_month



def factor_score_correlation(factor_dict,holding_period,corr_type='pearson'):
    """ correlation_type = 'spearman','pearson'
    """
    factor_auto_correlation = pd.DataFrame()
    if corr_type=='pearson':
        factor_auto_correlation['Pearson_linear_'+str(holding_period)+'d'] = factor_dict.corrwith(factor_dict.shift(holding_period),axis=1).T
    if corr_type =='spearman':
        factor_rank = factor_dict.rank(axis=1)
        factor_auto_correlation['Spearman_rank_'+str(holding_period)+'d'] = factor_rank.corrwith(factor_rank.shift(holding_period),axis=1).T
    return factor_auto_correlation



def factor_distribution_test(factor_df):
    factor_df.max(axis=1).plot(title='max',figsize=[11,3])
    factor_df.quantile(q=0.99,axis=1).plot(title='top 1 pct',figsize=[11,3])
    factor_df.median(axis=1).plot(title='median',figsize=[11,3])
    factor_df.quantile(q=0.01,axis=1).plot(title='bottom 1 pct',figsize=[11,3])
    factor_df.min(axis=1).plot(title='max',figsize=[11,3])
    return 


def IC_decay_test(factor_dict,holding_period_ret,holding_period,max_lag=3):
    """IC Decay Test:
       max_lag:(int) number of holding period after factor data was observed
       Correlation: IC(T), Return(T+1:T+1+Holding_Period) 
       Correlation for all days 
    """
    total_rebal = int(factor_dict.shape[0]/holding_period)
    max_lag = total_rebal if max_lag>total_rebal else max_lag # control for input error
    lag_list = [(i)*holding_period for i in range(max_lag+1)]
    IC_ts = np.empty([len(factor_dict),len(lag_list)])
    for i in range(len(lag_list)):
        lag_ret = holding_period_ret.shift(-1*lag_list[i]) #  
        IC_ts[:,i] = factor_dict.corrwith(lag_ret,axis=1)
    lag_list_name = [str(i+holding_period)+'d' for i in lag_list]
    IC_Decay = pd.DataFrame(np.nanmean(IC_ts,axis=0),index = lag_list_name,columns=['IC Decay'])   
    return IC_Decay

def IC_duration_test(factor_dict,stock_close,plot=True):
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
    IC_Duration = pd.DataFrame(np.nanmean(IC_ts,axis=0),index=lag_list_name,columns=['IC Duration'])
    if plot:
        plot_bar_with_label(IC_Duration,title='IC Duration Test')    
    return IC_Duration


def plot_bar_with_label(dat_plot,title=None,num_format=None):
    num_format='decimal' if num_format is None else 'pct'
    title='plt' if None else title
    ax2 = dat_plot.plot(kind='bar',figsize=[11,3],title=title)
    rects = ax2.patches
    if num_format == 'decimal':
        labels = [str(np.round(i[0],3)) for i in dat_plot.values.tolist()]
    elif num_format == 'pct':
        labels = [str(np.round(i[0]*100,3))+'%' for i in dat_plot.values.tolist()]
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax2.text(rect.get_x() + rect.get_width()/2, height, label, ha='center', va='bottom',fontsize=8)
    plt.show()
    return 


def IC_stats_calc(IC_ts):
    IC_mean = IC_ts.mean()
    IC_std = IC_ts.std()
    ICIR = IC_mean/IC_std#*np.sqrt(240)
    IC_stats = pd.DataFrame([IC_mean,IC_std,ICIR],index=['IC_mean','IC_std','ICIR'])
    return IC_stats
    

def IC_test(factor_dict,holding_period_ret,holding_period=20,plot=True,easy_test=False):
    date_list = list(set(factor_dict.index).intersection(set(holding_period_ret.index)))
    date_list.sort()    
    factor_dict = factor_dict.loc[date_list]
    holding_period_ret = holding_period_ret.loc[date_list]
    IC_ts = factor_dict.corrwith(holding_period_ret,axis=1)
    IC_stats = IC_stats_calc(IC_ts)
    if easy_test:
        print (IC_stats)
        IC_dict ={'ts':IC_ts,'stats':IC_stats}
        return IC_dict
    IC_year = IC_ts.groupby(IC_ts.index.year).mean()
    factor_coverage = np.isfinite(factor_dict).sum(axis=1)
    factor_auto_correlation = factor_score_correlation(factor_dict,holding_period)
    IC_Decay = IC_decay_test(factor_dict,holding_period_ret,holding_period,max_lag=3)    
    if plot:
        factor_coverage.plot(title='Factor Coverage',figsize=[12,1.5])
        plt.show()
        factor_auto_correlation.plot(title='Factor Auto Correlation - lag %dd'%holding_period,figsize=[12.1,1.5])
        plt.show()
        IC_Decay.plot(kind='bar',title='Factor Decay Test',figsize=[11.95,1.5])
        plt.show()
        roll_freq = 60
        ax1 = IC_ts.cumsum().plot(figsize=[11.7,2],title='IC Cumsum(LHS) & IC Roll %dd Mean(RHS)'%(roll_freq),label='2')
        ax1 = IC_ts.rolling(roll_freq).mean().plot(figsize=[11.6,2],secondary_y=True,label='1')
        #IC_year.plot(kind='bar',figsize=[11,2],title='IC by Year')    
        #plt.show()
    IC_month = IC_by_month(IC_ts,plot=plot)
    #IC_month = None
    IC_dict = {'ts':IC_ts,'month':IC_month,'year':IC_year,'stats':IC_stats,'decay':IC_Decay,'auto_corr':factor_coverage}
    print (IC_stats)
    return IC_dict


def batch_IC_test(dat_dict,holding_period_ret,holding_period=20,show_list=None,plot=True,easy_test=False):
    dat_type = type(dat_dict)
    IC_tank = {}
    if dat_type == dict:
        show_list = show_list if show_list is not None else list(dat_dict.keys())
        print ('IC Test for:\n',str(show_list))
        for col in show_list:
            print ('-'*50,'\n',col)
            IC_tank[col] = IC_test(dat_dict[col],holding_period_ret,holding_period,plot,easy_test)
            print ('-'*50)
    elif dat_type == pd.DataFrame:
        IC_tank = IC_test(dat_dict,holding_period_ret,holding_period,plot,easy_test)
    return IC_tank


    

#########################################################################################
"""简单版本  分层测试"""

def PerformanceMeasure(seg_return,compound_type='cumsum'):
    date_num, segment_num = seg_return.shape
    take_list = (np.isnan(seg_return).sum(axis=1)==segment_num).index
    seg_return = seg_return.loc[take_list]
    date_1yr = 240
    if compound_type=='cumsum':
        seg_return_cum = seg_return.fillna(0).cumsum() + 1
        Ret_Annual = seg_return.mean()*date_1yr
    elif compound_type=='cumprod':
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

"""
def portfolio_return_stats();
    # kurtosis / skew / 95 pct var / hit rate / 
    1+1
    return np.nan
"""

def max_drawdown(capital_line):
    """输入: 1. date_line: 日期序列   2.capital_line: 账户价值序列
       输出: 最大回撤及开始日期和结束日期            """
    mdd_end = np.argmax(np.maximum.accumulate(capital_line) - capital_line) # end of the period
    if mdd_end==0:  # 假如累计收益序列为1，则退出
        return np.nan
    mdd_start = np.argmax(capital_line[:mdd_end]) # start of period    
    mdd  = 1- capital_line[mdd_end]/capital_line[mdd_start]
    return mdd    


def max_drawdown_ts(capital_line):
    """输入: 1. date_line: 日期序列   2.capital_line: 账户价值序列
       输出: 最大回撤及开始日期和结束日期            """
    mdd_ts = (capital_line - np.maximum.accumulate(capital_line))/capital_line
    return mdd_ts    



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
    print ('1. Align data')
    stock_list = reduce(np.intersect1d,(factor_dict.columns,holding_period_ret.columns))#.tolist()
    date_list = reduce(np.intersect1d,(factor_dict.index,holding_period_ret.index,benchmark_ret.index))#.tolist()
    factor_dict,holding_period_ret = factor_dict[stock_list].loc[date_list],holding_period_ret[stock_list].loc[date_list]
    benchmark_ret = benchmark_ret.loc[date_list]
    holding_period_ret_one_day = (holding_period_ret+1)**(1/holding_period)-1
    
    print ('2. Perform segment')
    date_num = factor_dict.shape[0]
    date_list = factor_dict.index    
    holding_period_ret_one_day_mat = holding_period_ret_one_day.values
    factor_dict_mat = factor_dict.values
    easy_seg_return = np.zeros([date_num,segment_num])
    name_pool_mat = ['Q'+str(segment_num-i) for i in range(int(segment_num))]
    
    for i in range(date_num):
        #easy_seg_return[i,:]= easy_segment_ret_day(factor_dict,holding_period_ret_one_day,i,segment_num)
        easy_seg_return[i,:]= easy_segment_ret_day_mat(factor_dict_mat,holding_period_ret_one_day_mat,i,segment_num)
    easy_seg_return = pd.DataFrame(easy_seg_return,columns=name_pool_mat,index =date_list )
    name_pool = ['Q'+str(i+1) for i in range(int(segment_num))]
    easy_seg_return = easy_seg_return[name_pool] # sort it back to Q1-Q5 
    
    
    start_ind = easy_seg_return.any(axis=1)
    easy_seg_return['Benchmark'] = benchmark_ret
    easy_seg_return['Benchmark'][~start_ind] = np.nan 
    max_q = easy_seg_return[[name_pool[0],name_pool[-1]]].mean().argmax()
    min_q = easy_seg_return[[name_pool[0],name_pool[-1]]].mean().argmin()
    ls_type =  max_q +'-'+min_q
    easy_seg_return[ls_type] = easy_seg_return[max_q]-easy_seg_return[min_q]
    print ('3. Calculate performance measure')  

    print ('-'*30)
    #easy_seg_return_cum['L-index'] = easy_seg_return_cum[max_q] - easy_seg_return_cum['Benchmark'] + 1
    easy_seg_return['L-index'] = easy_seg_return[max_q] - easy_seg_return['Benchmark']
    seg_perf = PerformanceMeasure(easy_seg_return)
    print (seg_perf)
    easy_seg_return_cum = (easy_seg_return.fillna(0)+1).cumprod()
    easy_seg_return_cum['MDD_L-index'] = max_drawdown_ts(easy_seg_return_cum['L-index'])
    easy_seg_return_cum['MDD_L/S'] = max_drawdown_ts(easy_seg_return_cum[ls_type])
    mdd_ls = easy_seg_return_cum['MDD_L/S'].min()
    
    
    ax2 = seg_perf['Return(Ann.)'].plot(kind='bar',figsize=[11,3],title='Segment Annual Return')
    rects = ax2.patches
    labels = [str(np.round(i*100,1))+'%' for i in seg_perf['Return(Ann.)'].values.tolist()]
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax2.text(rect.get_x() + rect.get_width()/2, height, label, ha='center', va='bottom',fontsize=8)
    plt.show()

    ax = easy_seg_return_cum[ls_type].plot(figsize=[11,3],title='Cummulative Return L/S (Max Drawdown: '+str(np.round(mdd_ls*100,1))+'%)')
    ax1 = easy_seg_return_cum['MDD_L/S'].plot(secondary_y=True)
    plt.ylim([0,-1])
    ax.set_ylabel('Cum Ret')
    ax1.set_ylabel('Max DD')
    plt.gca().invert_yaxis()
    plt.show()
    
    #sns.regplot(benchmark,easy_seg_return[ls_type])
    """
    ax3 = easy_seg_return_cum['L-index'].plot(figsize=[11,3],title='Cummulative Return L-index (Max Drawdown: '+str(np.round(mdd_ls*100,1))+'%)')
    ax4 = easy_seg_return_cum['MDD_L-index'].plot(secondary_y=True)
    plt.ylim([0,-1])
    ax3.set_ylabel('Cum Ret')
    ax4.set_ylabel('Max DD')
    plt.gca().invert_yaxis()
    plt.show()
    """
    #seg_perf.plot(kind='bar',subplots=True,figsize=[11,14])
    easy_seg_return[ls_type].rolling(window=220).sum().plot(title='12 Month Rolling Return L/S('+ls_type+') ',figsize=[11,3])
    plt.show()
    
    #pprint.pprint(seg_perf)
    result_dict = {'seg_ret':easy_seg_return,'seg_ret_cum':easy_seg_return_cum,'performance':seg_perf}
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    return result_dict


def get_portfolio_spread(factor_dict,stock_return,segment_num):
    # Note: for handling top and bottom quntile with a lot of identical number - add some random noise
    np.random.seed(0)
    rand_int = pd.DataFrame(np.random.rand(stock_return.shape[0],stock_return.shape[1])/10**5,index=factor_dict.index,columns=factor_dict.columns)
    mask = np.isfinite(factor_dict+stock_return)
    factor_rank = (factor_dict[mask]+rand_int[mask]).rank(axis=1) # factor score higher with rank number higher 
    q_cut = [1-i/segment_num for i in range(segment_num+1)]
    portfolio_spread = pd.DataFrame()
    for q_num in range(segment_num): 
        factor_q_top = factor_rank.quantile(q=q_cut[q_num],axis=1) # q higher with higher score 
        factor_q_low = factor_rank.quantile(q=q_cut[q_num+1],axis=1) # q higher with higher score 
        if q_num+1 <segment_num:
            q_ind = (factor_rank.subtract(factor_q_top,axis=0)<=0) & (factor_rank.subtract(factor_q_low,axis=0)>0)
        else:
            q_ind = factor_rank.subtract(factor_q_top,axis=0)<=0
        portfolio_spread['Q'+str(q_num+1)] = stock_return[mask][q_ind].mean(axis=1)
    return portfolio_spread

def plot_segment_ret_year(seg_perf_year,col_name='Return(Ann.)'):    
    seg_perf_year = seg_perf_year[col_name]
    seg_perf_year = seg_perf_year.rename(index={'Benchmark': 'Index'})
    year_list = list(set(seg_perf_year.index.get_level_values(0)))
    year_list.sort(reverse=True)
    year_num = len(year_list)
    plt_rows = int(np.ceil(year_num/2))
    plt_y = plt_rows*2.5
    plt.figure(figsize=(13,plt_y))
    for i in range(year_num):
        plt.subplot(plt_rows,2,i+1)
        seg_perf_year.loc[year_list[i]].plot(kind='bar',fontsize=8)
        plt.title(col_name+' - '+str(year_list[i]),fontsize=8, fontweight='bold')
    return 


def plot_segment_test(easy_seg_return,seg_perf):
    easy_seg_return_cum = (easy_seg_return.fillna(0)+1).cumprod()
    easy_seg_return_cum['MDD_L-index'] = max_drawdown_ts(easy_seg_return_cum['L-index'])
    mdd_l_index = easy_seg_return_cum['MDD_L-index'].min()
    ax2 = seg_perf['Return(Ann.)'].plot(kind='bar',figsize=[13,2],title='Segment Annual Return')
    rects = ax2.patches
    labels = [str(np.round(i*100,1))+'%' for i in seg_perf['Return(Ann.)'].values.tolist()]
    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax2.text(rect.get_x() + rect.get_width()/2, height, label, ha='center', va='bottom',fontsize=8)
    plt.show()
    ax = np.log(easy_seg_return_cum['L-index']).plot(figsize=[12,2],title='Excess CumRet(log) (Max Drawdown: '+str(np.round(mdd_l_index*100,1))+'%)')
    ax1 = easy_seg_return_cum['MDD_L-index'].plot(secondary_y=True)
    plt.ylim([0,easy_seg_return_cum['MDD_L-index'].min()-0.01])
    ax.set_ylabel('Cum Ret(log)')
    ax1.set_ylabel('Max DD')
    plt.gca().invert_yaxis()
    plt.show()
    easy_seg_return['L-index'].rolling(60).sum().plot(figsize=[13,2],title='Excess Return(Q1-Index) - roll 60 days')
    plt.show()
    """
    [ls_type] = [i for i in easy_seg_return.columns if len(i)>4 and i.find('Q')==0]
    l_q,s_q = ls_type[0:ls_type.find('-')],ls_type[ls_type.find('-')+1:]
    q_list = [i for i in easy_seg_return.columns if len(i)<4 and i.find('Q')==0]
    ret_contribution = (easy_seg_return[l_q] - easy_seg_return[q_list].median(axis=1))/(easy_seg_return[l_q] - easy_seg_return[s_q])
    ret_contribution.rolling(100).mean().plot()
    """
    return 


def segment_test(factor_dict,holding_period_ret,holding_period,segment_num,benchmark_ret,plot=True):
    #result_dict = segment_test(factor_dict,holding_period_ret,holding_period,segment_num,benchmark_ret,plot=True)
    print ('-'*5 +'   Segment Test - '+str(segment_num)+'   '+'-'*5)
    tic = time.time()
    print ('1. Align data')
    stock_list = reduce(np.intersect1d,(factor_dict.columns,holding_period_ret.columns))#.tolist()
    date_list = reduce(np.intersect1d,(factor_dict.index,holding_period_ret.index,benchmark_ret.index))#.tolist()
    factor_dict,holding_period_ret = factor_dict[stock_list].loc[date_list],holding_period_ret[stock_list].loc[date_list]
    benchmark_ret = benchmark_ret.loc[date_list]
    bmk_hpr_daily = ((benchmark_ret+1).rolling(holding_period).apply(np.prod)**(1/holding_period)-1).shift(-1*holding_period)
    holding_period_ret_one_day = (holding_period_ret+1)**(1/holding_period)-1
    
    print ('2. Perform segment - eta ',str(np.ceil(0.8*segment_num)),'s')
    easy_seg_return = get_portfolio_spread(factor_dict,holding_period_ret_one_day,segment_num)
    
    start_ind = easy_seg_return.any(axis=1)# combine with benchmark
    easy_seg_return['Benchmark'] = bmk_hpr_daily
    easy_seg_return['Benchmark'][~start_ind] = np.nan 
    name_pool = ['Q'+str(i+1) for i in range(int(segment_num))]
    max_q = easy_seg_return[[name_pool[0],name_pool[-1]]].mean().argmax()
    easy_seg_return['L-index'] = easy_seg_return[max_q] - easy_seg_return['Benchmark']
    
    print ('3. Calculate performance measure')  
    seg_perf = PerformanceMeasure(easy_seg_return)
    seg_perf_year = easy_seg_return.groupby(easy_seg_return.index.year).apply(PerformanceMeasure)
    
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    
    if plot:
        print ('4. Plot')
        plot_segment_test(easy_seg_return,seg_perf)
        plot_segment_ret_year(seg_perf_year)
    
    result_dict = {'seg_ret':easy_seg_return,'performance':seg_perf,'perf_year':seg_perf_year}
    return result_dict

"""
# should sort by test factor first then sort by size factor
def segment_test_group(factor_dict,group_dict,holding_period_ret,holding_period,segment_num,benchmark_ret,plot=True):
    result_dict_master = {}
    group_rank = group_dict.rank(axis=0)  # rank number higher - factor score higher 
    group_num = 3
    group_ind = group_rank.copy()
    q1 = group_rank.max(axis=1)*(1/3)
    q2 = group_rank.max(axis=1)*(2/3)
    group_ind[(group_rank.subtract(q2,axis=0)>0)] = 1
    group_ind[(group_rank.subtract(q2,axis=0)<=0) & (group_rank.subtract(q1,axis=0)>0)] = 2
    group_ind[(group_rank.subtract(q1,axis=0)<=0)] = 3
    for i in range(1,group_num+1):
        print ('-'*20,'Group ',str(i),'-'*20)
        result_dict_master[i] = segment_test(factor_dict[group_ind==i],holding_period_ret,holding_period,segment_num,benchmark_ret,plot=True)
        print ('-'*52)
    return result_dict_master
"""
######################################################################################

""" factor combine"""
    

def universe_scale(factor_dict,alpha_uni):
    date_list = list(set(factor_dict.index).intersection(set(alpha_uni.index)))
    stock_list = list(set(factor_dict.columns).intersection(set(alpha_uni.columns)))
    factor_dict_uni = factor_dict[stock_list].loc[date_list]
    factor_dict_uni = factor_dict_uni[alpha_uni[stock_list].loc[date_list]] 
    return factor_dict_uni


def factor_combine(combine_dict,weight_dict,must_have=None,min_fac=1,min_weight=0):
    """
    combine factor based on weight
    must_have: if factor not exist - no value in composite
    min_fac: minimum factor number when combining
    combine_list = ['upside_to_tp','EarningRevision90d_neu','report_num_75d_neu','dpEPS_F1Y_lvl_chg','dpEPS_F2Y_lvl_chg']
    combine_weight = [0.4,0.1,0.1,0.2,0.2]
    weight_dict = dict(zip(combine_list,combine_weight))
    must_have = ['upside_to_tp','dpEPS_F1Y_lvl_chg']
    q_score = factor_combine(combine_dict,weight_dict,must_have=None,min_fac=1)
    """
    #print ('get max date and stock list')    
    stock_list,date_list = [],[]
    combine_list = list(weight_dict.keys())
    for key in combine_list:
        stock_list =list(set(stock_list).union(set(combine_dict[key].columns)))
        date_list = list(set(date_list).union(set(combine_dict[key].index)))
    stock_list.sort()
    date_list.sort()
    
    #print ('get factor universe')
    combine_df = pd.DataFrame(np.zeros([len(date_list),len(stock_list)]),columns=stock_list,index=date_list)
    cum_df = combine_df.copy()
    weight_cum = combine_df.copy()
    ind_dict = {}
    for key in combine_list:
        combine_dict[key] = combine_df + combine_dict[key] # scale to big one
        ind_dict[key] = np.isfinite(combine_dict[key])
        cum_df = cum_df + ind_dict[key]
        weight_cum = weight_cum + ind_dict[key]*weight_dict[key]
    factor_univ = cum_df>=min_fac
    if must_have is not None:
        #print ('coersing must have factor')
        for fac_must in must_have:
            factor_univ = factor_univ & ind_dict[fac_must]
    if min_weight is not None:
        #print ('filtering by min_weight')
        factor_univ = factor_univ & (weight_cum>=min_weight)
    print ('combining factor by weight')
    flist = list(weight_dict.keys())
    composite_factor = weight_dict[flist[0]]*normalize_fillna(combine_dict[flist[0]],factor_univ)
    for fname in flist[1:]:
        fac_std = normalize_fillna(combine_dict[fname],factor_univ)
        composite_factor = composite_factor + weight_dict[fname]*fac_std
    composite_factor = NormWinsor(composite_factor)
    return composite_factor


def solve_weight(IC_mean,IC_cov,solve_type='optimize'):
    factor_num = len(IC_cov)
    # analytical solution
    if solve_type =='equation':
        IC_weight = np.dot(linalg.inv(IC_cov),IC_mean)
        IC_weight_optimal = IC_weight/IC_weight.sum()
    # optimizer            
    elif solve_type =='optimize':
        objective_function = lambda w: -1 * np.dot(w,IC_mean)/np.sqrt(np.dot(np.dot(w,IC_cov),w.T))
        w0 = [1.0/factor_num]*factor_num
        bnds = [(0, 1,) for i in range(factor_num)] # w [0,1]
        cons = ({'type': 'eq','fun': lambda x: np.sum(x) - 1}) # sum(w)=1
        # method = 'L-BFGS-B','TNC ','SLSQP'  - use SLSQP
        opt_result = optimize.minimize(objective_function,w0,bounds=bnds,constraints=cons)
        IC_weight_optimal = opt_result.x
    IR_optimal = np.dot(IC_weight_optimal,IC_mean)/np.sqrt(np.dot(np.dot(IC_weight_optimal,IC_cov),IC_weight_optimal.T))
    return IR_optimal,IC_weight_optimal.tolist()


################################################################################################################
"""Max ICIR for static weight"""

from sklearn.covariance import ledoit_wolf, OAS, ShrunkCovariance, GraphLassoCV,empirical_covariance


def calc_covariance(X,cov_type='shrink'):
    """covariance matrix esitmation
    cov_type: sample, shrink, graph_lasso,oas
    X: shape (n_samples, n_features) - date*stock
    # request full length
    """
    if type(X) == pd.DataFrame:
        x_mat = X.values
        col_list = X.columns.tolist()
    else:
        x_mat = X
    num = x_mat.shape[1]
    mask = np.isfinite(np.sum(x_mat,axis=0))
    x_use = x_mat[:,mask]
    cov_mat = np.zeros([num,num])
    cov_mat[:] = np.nan
    mask_cov = np.zeros([num,num])
    mask_cov[:,~mask] = np.nan
    mask_cov[~mask,:] = np.nan
    mask_cov_final = np.isfinite(mask_cov)
    if x_use.shape[1]>1:
        if cov_type =='shrink':
            cov, shrinkage = ledoit_wolf(x_use)
        elif cov_type == 'graph_lasso':
            graph_lasso = GraphLassoCV().fit(x_use)
            cov = graph_lasso.covariance_
        elif cov_type == 'sample':
            cov = empirical_covariance(x_use)
        elif cov_type =='oas':
            cov = OAS().fit(x_use).covariance_ 
        cov_mat[mask_cov_final] = cov.flatten()
        if type(X) == pd.DataFrame:
            cov_mat = pd.DataFrame(cov_mat,index=col_list,columns=col_list)
    else:
        cov_mat[:] = np.nan
    return cov_mat




def calc_covariance_roll(X,roll_win,cov_type='shrink'):
    print ('cov_type=%s'%(cov_type))
    date_list,col_list = list(X.index),list(X.columns)
    date_num,col_num = len(date_list),len(col_list)
    rebal_num = date_num - roll_win
    cov_matr = np.zeros([date_num*col_num,col_num])
    cov_matr[:] = np.nan
    X_mat = X.values
    for i in range(rebal_num):
        cov_start,cov_end = i*col_num,(i+1)*col_num
        cov_matr[cov_start:cov_end,:] = calc_covariance(X_mat[i:i+roll_win,:],cov_type)
    index_tuple = [np.repeat(date_list,len(col_list)),col_list*len(date_list)]
    mi_index = pd.MultiIndex.from_tuples(list(zip(*index_tuple)),names=['dt', None])         
    cov_roll = pd.DataFrame(cov_matr,columns=col_list,index=mi_index)
    return cov_roll


def factor_combine_max_ICIR(factor_tank,holding_period_ret,ctype='join',test_year=None,must_have=None,min_fac=1,min_weight=0,plot=True,solve_type='optimize'):
    """
    # use example
    combine_tank = dict((name,eval(name)) for name in ['holistic_value_neu_ind','roe_neu_ind_size'])
    value_minus_trash_opt,IC_stats,IC_ts = factor_combine_max_ICIR(combine_tank,holding_period_ret,ctype='join')
    IC_tank['value_minus_trash_opt']  = IC_test(value_minus_trash_opt,holding_period_ret)
    """
    pd.options.display.float_format = '{:,.3f}'.format
    fac_list = list(factor_tank.keys())
    print ('-'*20+' Factor Combine '+'-'*20)
    print ('Combine List: ',str(fac_list))
    IC_ts_single = pd.DataFrame()
    
    print ('Calculating IC')
    for fac in factor_tank:
        IC_ts_single[fac] = factor_tank[fac].corrwith(holding_period_ret,axis=1)

    start_ind = np.isfinite(IC_ts_single).sum(axis=1)==IC_ts_single.shape[1]
    IC_ts_single = IC_ts_single[start_ind] # chop for same starting date
    IC_mean,IC_cov = IC_ts_single.mean(),IC_ts_single.cov()
    year_min,year_max = IC_ts_single.index.year.min(),IC_ts_single.index.year.max()
    
    if test_year is not None:
        print ('Out of Sample Period: ',str(test_year),'-',str(max(IC_ts_single.index.year)))
        use_date = IC_ts_single.index.year<test_year
        last_date_idx = use_date.cumsum().argmax()
        IC_ts_single_train = IC_ts_single[use_date]
        IC_mean,IC_cov = IC_ts_single_train.mean(),IC_ts_single_train.cov()
        IC_ts_single_test = IC_ts_single[~use_date]
        IC_mean_test,IC_cov_test= IC_ts_single_test.mean(),IC_ts_single_test.cov()
    
    print ('\n1. Optimize for Max ICIR')
    IR_optimal,IC_weight_optimal = solve_weight(IC_mean,IC_cov,solve_type)
    weight_dict = dict(zip(list(factor_tank.keys()),IC_weight_optimal))
    
    print ('\n2. Factor Combine: '+ctype)
    if ctype=='join':
        factor_composite = weight_dict[fac_list[0]]*factor_tank[fac_list[0]]
        for fac in fac_list[1:]:
            factor_composite  = factor_composite + weight_dict[fac]*factor_tank[fac]
        factor_composite = NormWinsor(factor_composite)
    elif ctype=='union':
        factor_composite = factor_combine(factor_tank,weight_dict,must_have,min_fac,min_weight)
    IC_combine = pd.DataFrame(factor_composite.corrwith(holding_period_ret,axis=1),columns=['combine'])
    IC_ts = pd.concat([IC_combine,IC_ts_single],axis=1).loc[start_ind.index][start_ind]
    IC_stats = IC_stats_calc(IC_ts)
    
    IC_weight = pd.DataFrame([sum(IC_weight_optimal)]+IC_weight_optimal,index=['combine']+fac_list,columns=['weight'] )
    IC_stats_wgt = pd.concat([IC_stats,IC_weight.T],axis=0)
    
    if test_year is not None:
        IC_stats_train,IC_stats_test = IC_stats_calc(IC_ts[use_date]),IC_stats_calc(IC_ts[~use_date])
        IR_optimal_test,IC_weight_optimal_test = solve_weight(IC_mean_test,IC_cov_test,solve_type)
        IC_weight_test = pd.DataFrame([sum(IC_weight_optimal_test)]+IC_weight_optimal_test,index=['combine']+fac_list,columns=['weight'] )
        IC_stats_wgt_train = pd.concat([IC_stats_train,IC_weight.T],axis=0)
        IC_stats_wgt_test = pd.concat([IC_stats_test,IC_weight_test.T],axis=0)
        print ('\nTrain Peiord: ',str(year_min),'-',str(test_year-1))
        print (IC_stats_wgt_train.T.sort_values(by='weight',ascending=False))
        IC_stats_train = IC_stats_calc(IC_ts[use_date])
        print ('\nTest Peiord: ',str(test_year),'-',str(year_max))
        print (IC_stats_wgt_test.T.sort_values(by='weight',ascending=False))
        
    if plot:
        plt_name = 'IC Cummulative (Test Peiord: '+str(test_year)+'-'+str(year_max)+')' if test_year is not None else 'IC Cummulative'
        IC_ts.cumsum().plot(title = plt_name,figsize=[13,5])
        #plt.legend(bbox_to_anchor=(1,1), loc=5, borderaxespad=0.)
        #plt.show()
        if test_year is not None:
            plt.axvspan(IC_ts.index[last_date_idx],IC_ts.index[-1], color='b', alpha=0.1, lw=0)
        plt.show()
    IC_stats_wgt = IC_stats_wgt.T.sort_values(by='weight',ascending=False)
    print ('\n3. Optimized Result: ',str(year_min),'-',str(year_max)+'\n',IC_stats_wgt)
    print ('-'*60)
    return factor_composite,IC_stats_wgt,IC_ts


def max_icir_rolling(factor_tank,stock_close,holding_period,ic_win=20,weight_roll=None,solve_type='optimize',cov_type='sample',plot=True):
    print ('-'*20,'rolling max icir','-'*20)
    print ('paramter set: ic_win=%d, weight_roll=%d, holding_period=%d'%(ic_win,1 if weight_roll is None else weight_roll,holding_period))
    print ('solve type = %s\ncov_type = %s'%(solve_type,cov_type)) #'equation'
    fac_list = list(factor_tank.keys())
    
    #fac_comb_max_icir_roll = max_icir_rolling(factor_tank,stock_close,holding_period,ic_win=20,weight_roll=None)
    holding_period_ret = stock_close.shift(-1*holding_period)/stock_close - 1
    dat_alg = align_data({'factor_tank':factor_tank,'holding_period_ret':holding_period_ret})    
    holding_period_ret,factor_tank = dat_alg['holding_period_ret'],dat_alg['factor_tank']
    print ('-'*20,'\ncalc ic')
    ic_df = batch_ic(holding_period_ret,factor_tank)
    print ('cacl rolling ic mean and ic covariance')
    ic_mean = ic_df.rolling(ic_win).mean()
    if cov_type=='sample':
        ic_cov = ic_df.rolling(ic_win).cov()
    else:
        ic_cov = calc_covariance_roll(ic_df,ic_win,cov_type)
    date_list = list(holding_period_ret.index)
    date_num,fac_num = len(date_list),len(fac_list)
    ir_list = np.zeros(date_num)
    weight_mat = np.zeros([date_num,fac_num])
    ic_mat = ic_mean.values
    ic_cov_mat = ic_cov.values
    rebal_num = date_num - holding_period
    print ('-'*20,'\nrolling optimize for %d days'%(rebal_num))
    print ('factor list:',str(fac_list))
    for idx in range(rebal_num):
        if idx%100==0:
            print (idx)#print ('block:%d-%d'%(idx,(idx+100)))
        
        idx_cov_start,idx_cov_end = idx*fac_num,(idx+1)*fac_num
        try:
            ir_list[idx+holding_period],weight_mat[idx+holding_period,:] = solve_weight(ic_mat[idx,:],ic_cov_mat[idx_cov_start:idx_cov_end,:],solve_type)
        except:
            continue
    #icir_in_sample = pd.DataFrame(ir_list,index=date_list)
    combine_weight = pd.DataFrame(weight_mat,index=date_list,columns=fac_list)
    print ('-'*20)
    fac_comb_max_icir_roll = factor_combine_regression(factor_tank,combine_weight,rolling_win=weight_roll,normalize=True,plot=plot)
    ic_df['combine'] = fac_comb_max_icir_roll.corrwith(holding_period_ret,axis=1)
    IC_stats = IC_stats_calc(ic_df)
    IC_weight_mean = pd.DataFrame(combine_weight.mean(axis=0),columns=['weight']).T
    IC_weight_mean = IC_weight_mean/IC_weight_mean.sum(axis=1).values[0]
    IC_weight_mean['combine'] = 1
    IC_stats_wgt = pd.concat([IC_stats,IC_weight_mean],axis=0)
    IC_stats_wgt = IC_stats_wgt.T.sort_values(by='weight',ascending=False)
    print ('rolling optimized result: ','\n',IC_stats_wgt)
    
    if plot:
        ic_df.cumsum().plot(title='ic cumsum',figsize=[11,3])
        plt.show()

    print ('-'*60)
    return fac_comb_max_icir_roll




#fac_comb_max_icir_roll = max_icir_rolling(factor_tank,stock_close.iloc[:300,:],holding_period,ic_win=20,weight_roll=None)
"""
from line_profiler import LineProfiler
lp = LineProfiler()
lp_wrapper = lp(read_minute_mat_quick)
lp_wrapper(file_path)
lp.print_stats()
"""

def plot_stacked_bar(combine_weight,freq=None,title=None):
    date_num = len(combine_weight)
    if freq is None:
        if date_num>=1000:
            freq = 'q'
        if date_num>=50:
            freq = 'm'
        else:
            freq = 'd'
    title = 'By '+freq if title is None else title + ' by '+freq
    combine_weight_mean = combine_weight.resample(freq).mean()
    combine_weight_mean.plot(figsize=[11,3],kind='bar',stacked=True,title=title)
    return combine_weight_mean


######################################################################################

################################################################################################################
""" factor combine: regression rolling"""





################################################################################################################


########### 
"""factor update"""

def get_start_date(cdate_list,data_length):
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    idx = fdate_list.index(cdate_list[0])-data_length
    min_index= max(0,idx)
    start_date = fdate_list[min_index]
    if idx<0:
        print ('Not enough data: will use first available date:',str(start_date))
    return start_date


def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day 
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print ('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x:abs(x-current_date) if x<=current_date else 100)
    if current_hour < new_date_time and nearest_date==current_date:
        print ('Not till refresh time '+str(new_date_time)+':00')
        current_date = fdate_list[fdate_list.index(current_date)-1]
        print ('Use previous trading date: '+str(current_date))
    elif nearest_date<current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date==current_date:
        print ('Right on time: '+str(current_date))
    return current_date



def date_period_handler(sdate=None,edate=None):
    last_day = get_current_date()
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        print ('update for one day: '+str(sdate))
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i<=min(edate,last_day) and i>=sdate]
        sdate,edate = cdate_list[0],cdate_list[-1]
    return sdate,edate


def check_update_date(sdate=None,edate=None,use_len=None):
    #check_update_date(sdate=None,edate=None)
    use_len = 0 if use_len is None else use_len
    sdate,edate = date_period_handler(sdate,edate)
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i>=sdate and i<=edate]
    idx = max(0,fdate_list.index(cdate_list[0])-use_len)
    sdate_prev = fdate_list[idx]
    print ('-'*20,'\ndata used: %d - %d '%(sdate_prev,edate))
    print ('factor data: %d - %d \ntotal count: %d'%(sdate_prev,edate,len(cdate_list)))
    print ('-'*20)
    return sdate_prev,edate,cdate_list



def cdate_list_checker(cdate_list=None,use_date=None):
    if cdate_list == None:
        cdate_list = [get_current_date(new_date_time=18)]
    else:
        cdate_list = [int(cdate_list)] if type(cdate_list) !=list else cdate_list
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    if not set(cdate_list).issubset(set(fdate_list)):
        print ('Not a valid trading day')
        raise AssertionError
    #cdate_list = fdate_list[-475:-468]
    if use_date==None:
        start_date = cdate_list[0]
    else:
        start_date = get_start_date(cdate_list,use_date)
    end_date= cdate_list[-1]
    print ('start_date:',str(start_date),'\nend_date:',str(end_date))
    return start_date,end_date



def df_formatter(dataframe,factor_name):
    data_MI = pd.DataFrame(dataframe.stack(),columns=[factor_name])
    data_MI.index.names = ['dt','Ticker']
    data_MI = data_MI.dropna()
    return data_MI


def rename_dictionary(dict_orig,suffix='',prefix=''):
    dict_new = {}
    for col in dict_orig:
        col_new = str(prefix)+col+str(suffix)
        print (col,'---',col_new)
        dict_new[col_new] = dict_orig[col]
    return dict_new
    

def factor_tank_date_slice(factor_tank,cdate_list):
    print ('Date check:',str(cdate_list[0]),'-',str(cdate_list[-1]))
    date_num = len(cdate_list)    
    cdate_list_dt = [dt.datetime.strptime(str(i),'%Y%m%d') for i in cdate_list]
    factor_tank_sliced = {}
    for fac in factor_tank:
        factor_tank_sliced[fac] = factor_tank[fac].loc[cdate_list_dt]
        factor_tank_sliced[fac] = factor_tank_sliced[fac].dropna(how='all')
        if len(factor_tank_sliced[fac])<date_num:
            raise Exception
    return factor_tank_sliced


def factor_tank_save(factor_tank,h5_path=None,operation='append',cdate_list=None):
    print ('-'*40,'factor save start','-'*40)
    print (factor_tank.keys())
    # factor_tank_save(factor_tank,h5_path=None,operation='append',cdate_list=None)
    opt_type=True if operation=='append' else None
    if cdate_list is not None and operation=='append':
        print ('slice factor based on date range: %d - %d'%(cdate_list[0],cdate_list[-1]))
        try:
            factor_tank = factor_tank_date_slice(factor_tank,cdate_list)
        except:
            print ('date error...')

    fail_list = []    
    h5_path = 'S:\\Quant\\data\\factor\\' if h5_path==None else h5_path
    os.mkdir(h5_path) if not os.path.exists(h5_path) else None
    fac_list = list(factor_tank.keys())
    fac_num = len(fac_list)
    for factor_name in fac_list:#fail_list:
        save_name = h5_path + factor_name + '.h5'
        pos = str(fac_list.index(factor_name)+1)+'/'+str(fac_num)
        print ('-'*20,operation,'-'*20,'\n',pos,' saving to: ',save_name)
        try:
            print ('reformat')
            factor_dict_MI = df_formatter(factor_tank[factor_name],factor_name)
            if opt_type is None and os.path.exists(save_name):
                print ('already exist - remove first: ',save_name)
                os.remove(save_name)
            print ('writing')
            IO.pd_hdf5_writer(factor_dict_MI,save_name,factor_name,append=opt_type)
            print ('done')
        except:
            print ('failed...')
            fail_list.append(factor_name)
    print ('-'*40,'factor save complete','-'*40)
    return fail_list


####################################################################################################################
"""simple factor tool"""

def factor_seg(factor_x,factor_y):
    data = pd.concat([factor_x.stack(),factor_y.stack()],axis=1)
    data=data.dropna()
    data.columns = ['x','y']
    data['decile']=pd.qcut(data['x'],10,labels=False)+1
    quantile_averages=data.groupby('decile')['y'].apply(lambda x: x.mean())
    quantile_averages.plot(kind='bar')
    plt.xlabel('x_basket')
    plt.ylabel('y_avg')
    return quantile_averages

def industry_sector_demean(factor_df,stock_industry):
    #industry = style_data['Industry']
    #factor = dat_dict['S_QFA_ROE']
    dat = align_data({'factor':factor_df,'industry':stock_industry})
    factor,industry = dat['factor'],dat['industry']
    industry = industry.fillna(99)
    zscore = lambda x: (x - x.mean()) / x.std()
    factor_demean = factor_df.copy()
    mean_list = []
    for date in factor.index:
        #print (date)
        industry_list = industry.loc[date]
        mean_list.append(factor.loc[date].groupby(industry_list).transform(zscore))
    factor_demean = pd.concat(mean_list,axis=1).T
    return factor_demean



def correlation_test(factor_tank,fix_factor=None,plot=True,roll_num=None):
    fac_list = list(factor_tank.keys()) 
    fac_num = len(fac_list)
    factor_corr = pd.DataFrame()
    fac_corr_mat = np.zeros([fac_num,fac_num])
    if fix_factor is None:
        for i in range(fac_num-1):
            for j in range(i+1,fac_num):
                fac_x,fac_y = fac_list[i],fac_list[j]
                factor_corr[str(fac_x)+'&&'+str(fac_y)] = factor_tank[fac_x].corrwith(factor_tank[fac_y],axis=1)
                fac_corr_mat[i,j] = factor_corr[str(fac_x)+'&&'+str(fac_y)].mean()
        factor_corr_mat = pd.DataFrame(fac_corr_mat,index=fac_list,columns=fac_list)
    elif type(fix_factor)==pd.DataFrame:
        for fac_y in fac_list:
            factor_corr[fac_y] = fix_factor.corrwith(factor_tank[fac_y],axis=1)  
            
    elif type(fix_factor)==str and fix_factor in fac_list:
        fac_list.remove(fix_factor)
        for fac_y in fac_list:
            factor_corr[str(fix_factor)+'&&'+str(fac_y)] = factor_tank[fix_factor].corrwith(factor_tank[fac_y],axis=1) 
    
    if plot:
        roll_num = 20 if roll_num is None else roll_num
        yh = len(factor_corr.columns)*2
        factor_corr.rolling(roll_num).mean().plot(subplots=True,figsize=[11,yh])
        plt.show()
        factor_corr.plot(kind='box',figsize=[11,3],rot=90)
        plt.show()
        if fix_factor is None:
            sns.heatmap(factor_corr_mat)
            plt.show()
    # add rolling correlation for past 36 month / C_ab = mean(corr_ab)/std(corr_ab) 
    return factor_corr



def get_factor_return(factor_tank,stock_close,holding_period,segment_num=3):
    print ('getting factor long short return')
    # record return at the end of holding period
    segment_num = 3 if segment_num is None else segment_num
    hpr_1d = stock_close.shift(-1*holding_period)/stock_close - 1 # recrod at start
    seg_ret_tank = {}
    ls_q = 'Q1-Q'+str(segment_num)
    if type(factor_tank)==dict:
        for fac in factor_tank:
            print (fac)
            seg_ret_tank[fac] = get_portfolio_spread(factor_tank[fac],hpr_1d,segment_num).shift(holding_period) # take return at start of holding period
            seg_ret_tank[fac][ls_q] = seg_ret_tank[fac]['Q1']-seg_ret_tank[fac]['Q'+str(segment_num)]
    elif type(factor_tank)==pd.DataFrame:
        seg_ret_tank = get_portfolio_spread(factor_tank[fac],hpr_1d,segment_num).shift(holding_period)
        seg_ret_tank[ls_q] = seg_ret_tank[fac]['Q1']-seg_ret_tank[fac]['Q'+str(segment_num)]
    return seg_ret_tank

def double_sort(factor_x,factor_y):
    
    sort_result =[]
    return sort_result



####################################################################################################################







####################################################################################################################
""" Factor Rolling Regression """

def ts_acf(ts_data,max_lag=60):
    for col in ts_data:
        print (col)
        try:
            fig = plt.figure(figsize=(11,3))
            ax1 = fig.add_subplot(211)
            fig = sm.graphics.tsa.plot_acf(ts_data[col].dropna(),lags=max_lag,title='ACF - '+col, ax=ax1)
            ax2 = fig.add_subplot(212)
            fig = sm.graphics.tsa.plot_pacf(ts_data[col].dropna(),lags=max_lag,title='PACF - '+col, ax=ax2)
        except:
            print ('error')
    return 

def ols_regression_beta(y,x,min_size=0):
    fac_num = int(np.size(x)/x.shape[0])
    beta = np.array([np.nan]*fac_num)   
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)<min_size:
        return beta
    ols1  = sm.OLS(y[mask],x[mask]).fit()
    beta = ols1.params
    return beta



def np_reg_beta_quick(y,x,min_size=0):
    #res = np.array([np.nan]*len(y)) 
    fac_num = int(np.size(x)/x.shape[0])
    beta = np.array([np.nan]*fac_num)   
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)<min_size:
        return beta
    ols_result = np.linalg.lstsq(x[mask],y[mask])
    #ols_resid = y[mask] - np.dot(ols_result[0],x[mask].T)
    #res[mask] = ols_resid
    #r2 = 1- ols_result[1]/(y[mask].size*y[mask].var())
    beta = ols_result[0]
    return beta




def np_reg_beta_r2_quick(y,x,min_size=0):
    #res = np.array([np.nan]*len(y)) 
    beta,r2 = np.nan,np.nan
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)<min_size:
        return beta,r2
    ols_result = np.linalg.lstsq(x[mask],y[mask])
    #ols_resid = y[mask] - np.dot(ols_result[0],x[mask].T)
    #res[mask] = ols_resid
    r2 = 1- ols_result[1]/(y[mask].size*y[mask].var())
    beta = ols_result[0]
    return beta,r2


def ols_regression_tstat(y,x,min_size=0):
    fac_num = int(np.size(x)/x.shape[0])
    tstat = np.array([np.nan]*fac_num)   
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)<min_size:
        return tstat
    ols1  = sm.OLS(y[mask],x[mask]).fit()
    tstat = ols1.tvalues
    return tstat


def lasso_regression_beta(y,x,min_size=0):
    fac_num = int(np.size(x)/x.shape[0])
    beta = np.array([np.nan]*fac_num)    
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)<min_size:
        return beta
    clf = linear_model.Lasso(alpha=0.05,positive=True).fit(x[mask],y[mask])
    beta = clf.coef_
    return beta


def get_factor_beta(holding_period_ret,holding_period,reg_dict,reg_list=None,normalize=False,plot=True,reg_model='ols',pos_only=False):
    print ('-'*5+'   Get Factor Beta   '+'-'*5)
    tic = time.time()
    reg_list = list(reg_dict.keys()) if reg_list is None else reg_list
    date_num, stock_num = holding_period_ret.shape
    factor_num = len(reg_list) #len(reg_list)-1 if ind_neu else len(reg_list)
    min_size_ts = [int(i) for i in (np.isfinite(holding_period_ret).sum(axis=1)/4).values]
    print ('Regression on: ', str(reg_list))
    x_mat = np.ones([factor_num+1,date_num,stock_num]) # including intercept
    #return_mat = NormWinsor(holding_period_ret.copy()).values # note: python pass by value
    return_mat = (holding_period_ret.copy()).values     
    beta = np.empty([date_num,factor_num+1])
    beta[:] = np.nan
    i=0 
    for fac in reg_list:
        i=i+1 # leave first spot for intercept
        if fac.lower() != 'industry':
            x_mat[i,:,:] = reg_dict[fac].values
    for date_idx in range(date_num):
        try:
            if reg_model=='ols':
                beta[date_idx,:] = ols_regression_beta(return_mat[date_idx,:],x_mat[:,date_idx,:].T,min_size_ts[date_idx])
            elif reg_model=='lasso':
                beta[date_idx,:] = lasso_regression_beta(return_mat[date_idx,:],x_mat[:,date_idx,:].T,min_size_ts[date_idx])
        except:
            continue
    factor_beta_lead = pd.DataFrame(beta,columns=['intcp']+reg_list,index=holding_period_ret.index)
    if pos_only:
        print ('forcing negative beta to be zero')
        factor_beta_lead[factor_beta_lead<0] = 0
    factor_beta_lead = NormWinsor(factor_beta_lead) if normalize==True else factor_beta_lead
    factor_beta = factor_beta_lead.shift(holding_period) # important for not using out of sample information 
    # factor_dict at t, holding period t - represnt return from t to t+hp,
    # thus beta loading should be recorded at t+h - accounting for holding period return used 
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*20)    
    if plot:
        factor_beta.mean().plot(kind='bar',figsize=[11,2],title='Factor Beta Average')
        factor_beta.plot.box(title='Beta Distribution',figsize=[11,2],rot=90)
        factor_beta.rolling(20).mean().plot(subplots=True,figsize=[11,1.5*len(factor_beta.columns)],title='Factor Beta Rolling 20 days Average')
        ts_acf(factor_beta)
    return factor_beta



def get_regression_beta(factor_y,reg_dict,reg_list=None,plot=True):
    print ('-'*5+'   Get Factor Beta   '+'-'*5)
    tic = time.time()
    neutral_dict = align_data({'factor_y':factor_y,'reg_dict':reg_dict})
    factor_y = neutral_dict['factor_y']
    reg_dict = neutral_dict['reg_dict']
    if type(reg_dict)==pd.DataFrame:
        reg_dict = {'x':reg_dict}
    reg_list = list(reg_dict.keys()) if reg_list is None else reg_list
    date_num, stock_num = factor_y.shape
    factor_num = len(reg_list) #len(reg_list)-1 if ind_neu else len(reg_list)
    min_size_ts = [int(i) for i in (np.isfinite(factor_y).sum(axis=1)/4).values]
    x_mat = np.ones([factor_num+1,date_num,stock_num]) # including intercept
    return_mat = (factor_y.copy()).values     
    beta = np.empty([date_num,factor_num+1])
    beta[:] = np.nan
    i=0 
    for fac in reg_list:
        i=i+1 # leave first spot for intercept
        if fac.lower() != 'industry':
            x_mat[i,:,:] = reg_dict[fac].values
    print ('Regression on: ', str(reg_list))
    for date_idx in range(date_num):
        try:
            beta[date_idx,:] = ols_regression_beta(return_mat[date_idx,:],x_mat[:,date_idx,:].T,min_size_ts[date_idx])
        except:
            continue
    factor_beta= pd.DataFrame(beta,columns=['intcp']+reg_list,index=factor_y.index)
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*20)    
    if plot:
        factor_beta.plot(subplots=True,figsize=[11,3*len(factor_beta.columns)])
    return factor_beta


def reg_beta_r2_res_tstats(y,x,min_size=0):
    res = np.zeros(len(y))
    res[:] = np.nan
    r2,beta = np.nan,np.nan
    #res = np.array([np.nan]*len(y))    
    mask = np.isfinite(y+x.sum(axis=1))
    if np.count_nonzero(mask)<min_size:
        return res,r2,beta
    ols1  = sm.OLS(y[mask],x[mask]).fit()
    res[mask] = ols1.resid
    r2 = ols1.rsquared
    beta = ols1.params
    tstat = ols1.tvalues
    return beta,r2,res,tstat


def tstat_summary(factor_tstat,tstat_cut=2,plot=True):
    mask = np.isfinite(factor_tstat)
    factor_tstat_abs = np.abs(factor_tstat)
    tstat_abs_above = factor_tstat_abs>=tstat_cut
    tstat_abs_above_pct = tstat_abs_above.sum(axis=0)/mask.sum(axis=0)
    tstat_above = factor_tstat>=tstat_cut
    tstat_above_pct = tstat_above.sum(axis=0)/mask.sum(axis=0)
    
    tstat_dict = {'tstat_mean':factor_tstat.mean(axis=0),
                  'tstat_above_pct':tstat_above_pct,
                  'tstat_abs_mean':factor_tstat_abs.mean(axis=0),
                  'tstat_abs_above_pct':tstat_abs_above_pct}
    if plot:
        tstat_dict['tstat_mean'].plot(kind='bar',figsize=[11,2],title='T-statistics average')
        plt.show()
        tstat_above_pct.plot(kind='bar',figsize=[11,2],title='Percentage of time T-statistics above '+str(tstat_cut))
        plt.show()
        #tstat_dict['tstat_abs_mean'].plot(kind='bar',figsize=[11,2],title='Absolute T-statistics average')
        #plt.show()
        #tstat_abs_above_pct.plot(kind='bar',figsize=[11,2],title='Percentage of time absolute T-statistics above '+str(tstat_cut))
        #plt.show()
    return tstat_dict 
    
def batch_ic(holding_period_ret,reg_dict,reg_list=None):
    #ic_df = batch_ic(holding_period_ret,ma_dict_norm1)
    reg_list = list(reg_dict.keys()) if reg_list is None else reg_list
    ic_list = []
    for fac in reg_dict:
        ic_list.append(reg_dict[fac].corrwith(holding_period_ret,axis=1))
    ic_df = pd.concat(ic_list,axis=1)
    ic_df.columns = reg_list
    return ic_df



def batch_calc_loss(y_pred,y_true,loss_type='r2'):
    #y_true,y_pred = ic_df,beta_ma
    col_list = list(set(y_true.columns).intersection(set(y_pred.columns)))
    col_list.sort()
    print ('check loss:\n',str(col_list))
    loss_dict = {}
    loss_cat = {}
    for col in col_list:
         loss_dict[col] = calc_loss(y_true[col],y_pred[col],loss_type='r2')
         loss_cat[col] = pd.DataFrame([y_true[col],y_pred[col]],index=['true_'+str(col),'pred_'+str(col)]).T
         loss_cat[col].rolling(20).mean().plot(figsize=[11,2],title=col)
         plt.show()
    loss_df = pd.DataFrame(list(loss_dict.values()),index=list(loss_dict.keys()),columns=[loss_type])
    return loss_df 

def get_factor_beta_r2_res_tstat(holding_period_ret,holding_period,reg_dict,reg_list=None,normalize=False,plot=True,reg_model='ols',tstat_cut=2,check_ic=True):
    print ('-'*20+' CS Regression '+'-'*20)
    tic = time.time()
    print ('align')
    dat_alg = {'holding_period_ret':holding_period_ret,'reg_dict':reg_dict}
    if normalize:
        print ('normalize x and y')
        dat_alg['holding_period_ret'] = DataNormalize(dat_alg['holding_period_ret'])
        dat_alg['reg_dict'] = batch_normwinsor(dat_alg['reg_dict'])
    
    reg_list = list(dat_alg['reg_dict'].keys()) if reg_list is None else reg_list
    date_num,stock_num = dat_alg['holding_period_ret'].shape
    date_list,stock_list = dat_alg['holding_period_ret'].index,dat_alg['holding_period_ret'].columns
    factor_num = len(reg_list) #len(reg_list)-1 if ind_neu else len(reg_list)
    min_size_ts = [int(i) for i in (np.isfinite(dat_alg['holding_period_ret']).sum(axis=1)/4).values]
    print ('Regression on: ', str(reg_list))
    x_mat = np.ones([factor_num+1,date_num,stock_num]) # including intercept
    #return_mat = NormWinsor(holding_period_ret.copy()).values # note: python pass by value
    return_mat = (dat_alg['holding_period_ret']).values     
    beta_mat = np.empty([date_num,factor_num+1])
    beta_mat[:] = np.nan
    tstat_mat = np.empty([date_num,factor_num+1])
    tstat_mat[:] = np.nan
    r2_mat = np.empty([date_num,1])
    r2_mat[:] = np.nan
    res_mat = np.zeros([date_num,stock_num])
    res_mat[:] = np.nan
    i=0 
    for fac in reg_list:
        i=i+1 # leave first spot for intercept
        if str(fac).lower() != 'industry':
            x_mat[i,:,:] = dat_alg['reg_dict'][fac].values
    for date_idx in range(date_num):
        try:
            if reg_model=='ols':
                beta_mat[date_idx,:],r2_mat[date_idx],res_mat[date_idx,:],tstat_mat[date_idx,:] = reg_beta_r2_res_tstats(return_mat[date_idx,:],x_mat[:,date_idx,:].T,min_size_ts[date_idx])
        except:
            continue
    print ('shift beta for %d days'%(holding_period))
    factor_beta = pd.DataFrame(beta_mat,columns=['intcp']+reg_list,index=date_list).shift(holding_period)
    factor_r2 = pd.DataFrame(r2_mat,index=date_list).shift(holding_period)
    factor_res = pd.DataFrame(res_mat,index=date_list,columns=stock_list).shift(holding_period)
    factor_tstat = pd.DataFrame(tstat_mat,columns=['intcp']+reg_list,index=date_list).shift(holding_period)
    stat_dict = {}
    r2_avg = factor_r2.mean()
    # factor_dict at t, holding period t - represnt return from t to t+hp,
    # thus beta loading should be recorded at t+h - accounting for holding period return used 
    if plot:
        #factor_beta.mean().plot(kind='bar',figsize=[11,2],title='Factor Beta Average')
        #plt.show()
        stat_dict['tstat_dict'] = tstat_summary(factor_tstat,tstat_cut=2,plot=True)
        plt.show()
        #factor_beta.plot.box(title='Beta Distribution',figsize=[11,2],rot=90)
        #factor_beta.rolling(20).mean().plot(subplots=True,figsize=[11,1.5*len(factor_beta.columns)],title='Factor Beta Rolling 20 days Average')
        factor_tstat.rolling(20).mean().plot(subplots=True,figsize=[11,1.5*len(factor_tstat.columns)],title='Factor Tstats Rolling 20 days Average')
        #ts_acf(factor_beta)
        factor_r2.rolling(20).mean().plot(figsize=[11,2],title='R-squared  (average '+str(round(r2_avg.values[0],3))+')')
    if check_ic:
        print ('loss between Beta and IC')        
        ic_df = batch_ic(holding_period_ret,dat_alg['reg_dict'])
        loss_df = batch_calc_loss(factor_beta,ic_df,loss_type='r2')
        stat_dict['loss_df'] = loss_df.sort_index()
        print (stat_dict['loss_df'])
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    print ('-'*20+' Done '+'-'*20)
    return factor_beta,factor_r2,factor_res,factor_tstat,stat_dict


                
def factor_combine_regression(reg_dict,factor_beta,rolling_win=None,normalize=True,plot=True):
    print ('factor combine based on weight:')
    if 'intcp' in factor_beta.columns:
        print ('drop intercept term')
        factor_beta = factor_beta.drop('intcp',axis=1)
    fig_title = 'factor weight by time'
    if rolling_win is not None:
        print ('rolling weight by:',rolling_win,'days')
        factor_beta = factor_beta.rolling(rolling_win).mean()
        fig_title = fig_title + ' (rolling ' + str(rolling_win) + ' days)'
    if plot:
        factor_beta_mean = plot_stacked_bar(factor_beta,title='factor weight')
        plt.show()
    reg_list = list(reg_dict.keys())
    take_df = reg_dict[reg_list[0]]
    date_num, stock_num = take_df.shape
    factor_num = len(reg_list)
    x_mat = np.ones([factor_num,date_num,stock_num])
    combine_mat = np.ones([date_num,stock_num]) 
    combine_mat[:] = np.nan
    beta_mat = factor_beta.values if rolling_win is None else factor_beta.rolling(rolling_win).mean().values
    i=0
    for fac in reg_list:
        x_mat[i,:,:] = reg_dict[fac].values
        i=i+1
    for date_idx in range(date_num):
        try:
            combine_mat[date_idx,:] = np.dot(beta_mat[date_idx,:],x_mat[:,date_idx,:])    
        except:
            continue    
    combine_score = pd.DataFrame(combine_mat,index=take_df.index,columns=take_df.columns)
    combine_score = NormWinsor(combine_score) if normalize==True else combine_score
    return combine_score 


def lasso_fit(y,x,min_size=0):
    mask = np.isfinite(y+x.sum(axis=1))
    if sum(mask)<min_size:
        return np.nan
    clf = linear_model.Lasso(alpha=0.05,positive=True).fit(x[mask],y[mask])
    #clf = linear_model.Lasso().fit(x[mask],y[mask])
    return clf

def factor_combine_lasso(stock_close,holding_period,reg_dict):
    tic = time.time()
    holding_period_ret = stock_close.shift(-1*holding_period)/stock_close-1 
    date_num, stock_num = holding_period_ret.shape
    iter_num = date_num - holding_period
    reg_list = list(reg_dict.keys())
    factor_num = len(reg_list) 
    print ('factor combine lasso on: ', str(reg_list))
    x_mat = np.ones([factor_num+1,date_num,stock_num]) # including intercept
    return_mat = (holding_period_ret.copy()).values     
    factor_mat = np.empty([date_num,stock_num])
    factor_mat[:] = np.nan
    r2 = [np.nan]*date_num
    i=0 
    for fac in reg_list:
        i=i+1 # leave first spot for intercept
        if fac.lower() != 'industry':
            x_mat[i,:,:] = reg_dict[fac].values
    for date_idx in range(iter_num):
        try:
            y_train,x_train = return_mat[date_idx,:],x_mat[:,date_idx,:].T
            y_test,x_test = return_mat[date_idx+holding_period,:],x_mat[:,date_idx+holding_period,:].T
            x_mask = np.isfinite(x_test.sum(axis=1))
            factor_mat[date_idx+holding_period,:][x_mask] = lasso_fit(y_train,x_train).predict(x_test[x_mask])
            score_mask = np.isfinite(y_test+x_test.sum(axis=1))
            r2[date_idx+holding_period] = clf.score(x_test[score_mask],y_test[score_mask])
        except:
            continue
    factor_combine = pd.DataFrame(factor_mat,columns=holding_period_ret.columns,index=holding_period_ret.index)
    rsq = pd.DataFrame(r2,index=holding_period_ret.index)
    toc = time.time()
    print (str((round((toc-tic),2)))+'s ellapsed')
    return factor_combine,rsq 




####################################################################################################################



####################################################################################################################
""" stock minute data handler"""


from line_profiler import LineProfiler
import numba
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
import scipy.io as sio  


def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

def str2minute(time_string):
    dt_year,dt_month,dt_date = int(time_string[:4]),int(time_string[4:6]),int(time_string[6:8])
    dt_time = int(time_string[8:])
    dt_hour = int(dt_time/3600)
    dt_minute = int((dt_time - dt_hour*3600)/60)
    time_obj = dt.datetime(dt_year,dt_month,dt_date,dt_hour,dt_minute)
    return time_obj

def dt_parser(date):
    date_obj = dt.datetime.strptime(str(int(date)),'%Y%m%d')
    return date_obj

@numba.jit
def minute_reformat_jit(dt_time):
    dt_hour = int(dt_time/3600)
    dt_minute = int((dt_time - dt_hour*3600)/60)
    time_use = dt_hour*100+dt_minute
    return time_use 

"""
from line_profiler import LineProfiler
lp = LineProfiler()
lp_wrapper = lp(read_minute_mat_quick)
lp_wrapper(file_path)
lp.print_stats()
"""



def str2time(time_string):
    if type(time_string) == float:
        #time_obj = time_string
        time_obj = datetime.strptime(str(int(time_string)),'%Y%m%d')
    elif type(time_string) == str:
        time_obj = datetime.strptime(time_string,"%Y-%m-%d %H:%M:%S")
    return time_obj


def read_minute_mat(file_path):
    id_pos = file_path.rfind('\\')
    fname = file_path[id_pos+1:]
    header_list = ['date','time','open','high','low','close','volume','amt']
    data_config = {'type_date_time':    ['date','time'],
                   'type_float':        ['open','high','low','close','volume','amt']}
    dat1 = sio.loadmat(file_path)  # 做多
    dat = pd.DataFrame(dat1[fname[:-4]],columns=header_list)
    dat['Ticker'] = int(fname[-10:-4])
    dat['Ticker'] = dat['Ticker'].astype('int32')
    dat[data_config['type_float']] =  dat[data_config['type_float']].astype('float32')
    dat[data_config['type_date_time']] =  dat[data_config['type_date_time']].astype('int32')
    dat[data_config['type_date_time']] =  dat[data_config['type_date_time']].astype('str')
    dat['date_time_str'] = dat['date']+dat['time']
    dat['dt'] = dat['date_time_str'].apply(str2minute)
    dat = dat.drop(['date','time','date_time_str'],axis=1)
    dat = dat.set_index(['dt','Ticker'])
    return dat

def read_minute_mat_quick(file_path):
    id_pos = file_path.rfind('\\')
    fname = file_path[id_pos+1:]
    header_list = ['dt','minute','open','high','low','close','volume','amt']
    dat1 = sio.loadmat(file_path)  
    dat = pd.DataFrame(dat1[fname[:-4]],columns=header_list)
    dat['Ticker'] = int(fname[-10:-4])
    dat['dt'] = dat['dt'].astype('int32')
    dat['minute'] = dat['minute'].apply(minute_reformat_jit)    
    dat = dat.set_index(['dt','Ticker'])
    return dat

def read_minute_mat_ultra(file_path):
    id_pos = file_path.rfind('\\')
    fname = file_path[id_pos+1:]
    header_list = ['dt','minute','open','high','low','close','volume','amt']
    dat1 = sio.loadmat(file_path)  
    dat = pd.DataFrame(dat1[fname[:-4]],columns=header_list)
    dat['Ticker'] = int(fname[-10:-4])
    dat['dt'] = dat['dt'].astype('int32')
    dat = dat.set_index(['dt','Ticker'])
    return dat

def minute2raw(minute_read):
    dt_hour=int(minute_read/100)
    dt_min = int(str(minute_read)[-2:])
    minute_raw = dt_hour*3600+dt_min*60
    return minute_raw

def get_minute_block(minute_num,seg_num=4):
    # 925:bidding / 930: 930-931  / ignore 1500
    minute_mat = minute_num.values
    minute_block = np.array([np.nan]*len(minute_num))
    minute_type = 'raw' if minute_mat[0:2].mean()>2000 else 'process'
    if minute_type=='raw':
        if seg_num==4:
            seg = [[34200,37740],[37800,41340],[46800,50340],[50400,53940]]
        if seg_num==2:
            seg = [[34200,41340],[46800,53940]]          
    elif minute_type=='process':
        if seg_num==4:
            seg = [[930,1029],[1030,1129],[1300,1359],[1400,1459]]
        if seg_num==2:
            seg = [[930,1129],[13001459]]
    for i in range(seg_num):
        minute_block[(minute_mat>=seg[i][0]) & (minute_mat<=seg[i][1])] = i+1
    return minute_block


def minute_block_intraday(minute_num):
    # 925:bidding / 930: 930-931  / ignore 1500
    minute_mat = minute_num.values
    minute_block = np.array([np.nan]*len(minute_num))
    seg = [925,1459]
    #minute_block[(minute_mat<=seg[0])] = 1
    #minute_block[(minute_mat>=seg[1])] = 2
    minute_block[minute_mat==seg[0]] = 1
    minute_block[minute_mat==seg[1]] = 2
    return minute_block

def dt_ticker_reformat(dat,dtype='df'):
    if dtype=='mi':
        dat = dat.reset_index()
        dat['Ticker'] = dat['Ticker'].apply(ticker_match)
        dat['dt'] = dat['dt'].apply(dt_parser)
        dat = dat.set_index(['dt','Ticker'])    
    elif dtype=='df':
        dat.columns = [ticker_match(i) for i in dat.columns]
        dat.index = [dt_parser(i) for i in dat.index]
    return dat


#dat['block_intrday'] = minute_block_intraday(dat['minute'])
#pm_block_intraday = dat[dat['block_intrday']==1]['close'] / dat[dat['block_intrday']==2]['close'].shift(1)

def calc_stk_pm(dat):
    dat['block'] = get_minute_block(dat['minute'])
    block_last = dat[['close','block']].groupby(['dt','Ticker','block']).last()
    block_first = dat[['close','block']].groupby(['dt','Ticker','block']).first()
    pm_block = block_last/block_first-1
    return pm_block


def calc_pm(file_list):
    pm_contain = pd.DataFrame()    
    stock_num = len(file_list) if type(file_list)==list else 1
    for i in range(stock_num):
        try:
            if stock_num>1:
                file_path = file_list[i] 
                print (i,'/',stock_num,'---',file_path[-10:-4])    
            else:
                file_path = file_list
            dat = read_minute_mat_ultra(file_path)
            pm_block = calc_stk_pm(dat)
            pm_contain = pm_contain.append(pm_block)
        except:
            print ('fail!!!!!!!')
    return pm_contain

################ For mutli thread - faster read and compute ########################################
def calc_wrapper(read_func,compute_func,file_path):
    try:
        dat = read_func(file_path)
    except:
        print ('read fail')
    try:
        dat_result = compute_func(dat)
    except:
        print ('calc fail')
    return dat_result


def func_parallel(func,input_list,max_workers=10):
    # estimation time: 8 min for 3500 stocks
    tic = time.time()
    total_job = len(input_list)
    print ('-'*20,' Start ','-'*20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file_list = {executor.submit(func, file_path): file_path for file_path in input_list}
        #future_to_file_list = {executor.submit(func, sdate=sdate,edate=edate,stockcode=stockcode):stockcode for stockcode in stocklist}
        list_collector = []
        for future in concurrent.futures.as_completed(future_to_file_list):
            file_path = future_to_file_list[future]
            try:
                data = future.result()
                list_collector.append(data)
            except Exception as exc:
                print('%r generated an exception: %s' % (file_path, exc))
            else:
                print('%d/%d - %r has %d rows' % (input_list.index(file_path)+1,total_job,file_path, len(data)))
        print ('concating results')
        data_collector = pd.concat(list_collector,axis=0)
    toc = time.time()
    print (toc-tic)
    print ('-'*20,' End ','-'*20)
    return data_collector


"""
# use example
source_path = 'S:\\Quant\\StockUnAdjstedMinuteMatData\\'
mat_list = [i for i in os.listdir(source_path)]
file_list = [source_path+i for i in mat_list]
pm_contain = func_parallel(calc_pm,file_list[:5])

"""



####################################################################################################################

def excel_saver(output_dict,excel_name):
    writer = pd.ExcelWriter(excel_name,engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer,sheet_name=key)
    writer.save()
    return 


####################################################################################################################
"""save data """
def save_pickle(save_dict,save_path=None):
    import pickle
    save_path = 'D:\\basic_data.pkl' if save_path is None else save_path
    print ('saving data to:\n',save_path)
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 


def read_pickle(save_path=None):
    save_path = 'D:\\basic_data.pkl' if save_path is None else save_path
    print ('loading data from:\n',save_path)
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)  
    return save_dict

#create_factor_test_pickle()
#create_style_pickle()
#create_md_pickle()

def create_factor_test_pickle(save_path=None):
    from multifactor.backtest import FactorTest
    root_path = 'S:\\Quant\\backtest\\misc\\quant_data\\'
    save_path = root_path+'factor_test.pkl' if save_path is None else save_path
    sdate,edate = 20090101,get_current_date()
    md_raw = IO.read_data([sdate,edate],columns=['close','adjfactor'],ftype=FType.MD,dsource=DSource.WIND,max_workers=1)    
    close_adj = (md_raw['close']*md_raw['adjfactor']).unstack()
    factor_save_dict = FactorTest.load_data(close_adj,10)
    factor_save_dict['close_adj'] = close_adj
    with open(save_path, 'wb') as input:
        pickle.dump(factor_save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 

def create_style_pickle(save_path=None):
    root_path = 'S:\\Quant\\backtest\\misc\\quant_data\\'
    save_path = root_path+'style.pkl' if save_path is None else save_path
    sdate,edate = 20090101,get_current_date()
    print ('Getting style & industry data')
    style_data = IO.read_data([sdate,edate],ftype=FType.RISK,dsource=DSource.STYLEFACTOR,max_workers=1)
    style_dict = {}
    print ('Unstacking')
    for col in style_data:
        print (col)
        style_dict[col] = style_data[col].unstack()
    print ('Saving')
    with open(save_path, 'wb') as input:
        pickle.dump(style_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    print ('Done')
    return 
    
def create_md_pickle(save_path=None):
    root_path = 'S:\\Quant\\backtest\\misc\\quant_data\\'
    save_path = root_path+'md.pkl' if save_path is None else save_path
    sdate,edate = 20090101,get_current_date()
    # MD - return
    print ('Getting MD Data')
    dat_md = IO.read_data([sdate,edate],columns=['close','adjfactor','volume','turn','amt','mkt_cap_ard'],ftype=FType.MD,dsource=DSource.WIND,max_workers=1)
    
    print ('Getting Alpha Universe')
    alpha_ind = IO.read_data([sdate,edate],ftype=FType.UNIV,dsource=DSource.OPTM,columns=['alpha_universe'])
    #alpha_uni = alpha_ind['alpha_universe'].unstack().fillna(False)
    
    print ('Getting style & industry data')
    style_data = get_risk_data(sdate,edate,risk_list=['Beta','Size','Value','Industry'])
    
    """filter factor by alpha universe"""
    print ('Aligning data')
    dat_md['adj_close'] = dat_md['close']*dat_md['adjfactor']
    dat_uni = pd.concat([dat_md,alpha_ind],axis=1)
    dat_uni = dat_uni[dat_uni['alpha_universe']==True]
    stock_close = dat_uni['adj_close'].unstack()
        
    print ('Getting Index data')
    h5_index = IO.read_data([sdate,edate],['close'],ftype=FType.MD,dtype=DType.INDEX,dsource=DSource.WIND,max_workers=1)
    index_lookup = {'zz500': '000905.SH', 'zz800': '000906.SH', 'sz50': '000016.SH', 'hs300': '000300.SH'}
    bmk_price =  (h5_index.unstack()['close'])[index_lookup['zz500']]
    benchmark_ret = bmk_price/bmk_price.shift(1)-1

    md_dict = {'md':dat_md,'dat_uni':dat_uni,'stock_close':stock_close,'style_data':style_data,
               'index':h5_index,'bmk_price':bmk_price,'benchmark_ret':benchmark_ret}
    print ('saving md_dict:\n',str(list(md_dict.keys())))
    with open(save_path, 'wb') as input:
        pickle.dump(md_dict,input,protocol=pickle.HIGHEST_PROTOCOL)    
    return 

def read_factor_test_pickle(save_path=None):
    root_path = 'S:\\Quant\\backtest\\misc\\quant_data\\factor_test.pkl'
    save_path = root_path+'factor_test.pkl' if save_path is None else save_path
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)  
    return save_dict

def read_pickle_master(data_type='md',save_path=None):
    root_path =  'S:\\Quant\\backtest\\misc\\quant_data\\'
    type_list = ['md','style','factor_test']
    if data_type is not None:
        if type(data_type)==list:
            save_dict = {}
            for dtype in data_type:
                if dtype in type_list:
                    save_path = root_path + dtype + '.pkl'
                    print ('getting data from ',str(save_path))
                    with open(save_path, 'rb') as input:
                        save_dict[dtype] = pickle.load(input)
        if type(data_type)==str:
            save_path = root_path + data_type + '.pkl'
            print ('getting data from ',str(save_path))
            with open(save_path, 'rb') as input:
                save_dict = pickle.load(input)              
    else:
        if save_path is not None:
            print ('getting data from ',str(save_path))
            with open(save_path, 'rb') as input:
                save_dict = pickle.load(input)  
    return save_dict


#create_factor_test_pickle()
#read_factor_test_pickle()

####################################################################################################################
""" earning calendar"""

def latest_issue_date(qtr):
    if type(qtr)==int:
        qtr=str(qtr)
    if type(qtr)==pd._libs.tsliroll_generateb.Timestamp:
        qtr = dt.datetime.strftime(qtr,'%Y%m%d')
    year,month = qtr[:4],qtr[4:]
    lookup_dict = {'0331':'0430','0630':'0831','0930':'1031','1231':'0430'}
    #lookup_dict = {'0331':'0505','0630':'0905','0930':'1105','1231':'0505'}
    if month =='1231':
        lastest_int = int(str(int(year)+1)+lookup_dict[month])
    else:
        lastest_int = int(year+lookup_dict[month])
    last_day = dt.datetime.strptime(str(lastest_int),'%Y%m%d') 
    return last_day


def get_days_since_earning(sdate=None,edate=None,day=20):
    sdate = 20090101 if sdate is None else sdate
    edate = get_current_date() if edate is None else edate
    print ('Get stm issuing date')
    issue_date = IO.read_data([sdate,edate],ftype=FType.FDD,dsource=DSource.WIND,dfreq=DFreq.QUARTERLY,columns=['stm_issuingdate'])
    issue_date_mat = issue_date['stm_issuingdate'].unstack()
    issue_date_mat = issue_date_mat.dropna(axis=1,how='all')  #drop stock with all nan c
    issue_date_mat = issue_date_mat.fillna('1899-12-30')
    issue_date_mat = issue_date_mat.applymap(lambda x: dt.datetime.strptime(x,'%Y-%m-%d'))
    issue_date_diff = (issue_date_mat - issue_date_mat.shift(1)).applymap(lambda x: x.days) # check if report date same - annual report and quarterly report 
    issue_date_mat[issue_date_diff==0] = issue_date_mat[issue_date_diff==0].applymap(lambda x: x+dt.timedelta(days=1)) # if same day - add one date
    last_day_dt = [latest_issue_date(i) for i in issue_date_mat.index]
    report_date_diff = issue_date_mat.subtract(last_day_dt,axis=0).applymap(lambda x:x.days) # negative day means early release of data 
    use_ind = (report_date_diff>-100) & (report_date_diff<30) & (issue_date_diff>0)
    issue_date_mat[~use_ind] = np.nan

    print ('Back fill...')
    fdate_list_dt = IO.read_data([20090101,20990101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    date_list_int = [i for i in fdate_list if i<=edate and i>=sdate]
    date_list = [dt.datetime.strptime(str(i),'%Y%m%d') for i in date_list_int]
    date_list_full = pd.date_range(IO.str_date_parser(sdate),IO.str_date_parser(edate))
    common_stock_list = issue_date_mat.columns
    is_list = []
    val_x = np.zeros(len(issue_date_mat.index))
    for stock_name in common_stock_list:
        #data_by_issue_date = pd.DataFrame([factor_dict[stock_name].values,issue_date_mat[stock_name]]).T.dropna().set_index(1)
        date_x = issue_date_mat[stock_name]
        date_mask = [str(i)!='NaT' for i in date_x]
        data_by_issue_date = pd.Series(val_x[date_mask],index=date_x[date_mask])
        data_by_issue_date.name = stock_name
        is_list.append(data_by_issue_date)
        #data_final[stock_name] = data_by_issue_date.reindex(date_list,method='ffill')
    print ('Count days since earning')    
    is_df = pd.concat(is_list,axis=1)
    data_final = is_df.reindex(date_list_full)
    td = pd.DatetimeIndex(date_list)
    data_use = data_final.groupby(td[td.searchsorted(data_final.index)]).sum()
    roll_date = data_use.fillna(method='ffill',limit=day)
    days_since_earning = roll_date.rolling(window=day).count()
    days_since_earning[np.isnan(roll_date)] = np.nan
    print ('Done')
    return days_since_earning


def filler_post_earning(factor_df,days_since_earning,avoid=True):
    earning_mask = np.isfinite(days_since_earning) if avoid else np.isnan(days_since_earning)
    factor_filtered  = factor_df[~earning_mask]
    return factor_filtered




####################################################################################################################

####################################################################################################################
""" time series"""
def bayesian_shrinkage(ts):
    
    return

def rolling_zscore(factor,roll_win):
    
    return 

def get_inflection_points(factor):
    
    return 



#################################################################################################
"""misc operator"""

def get_top_mean(dat,top_n=5,min_size=5):
    #from functools import partial
    #get_top_mean_x = partial(get_top_mean, top_n=int(max_n/4))
    top_mean = np.nan
    mask = np.isfinite(dat)
    dat_use = dat[mask]
    if len(dat_use)<min_size:
        return top_mean
    else:
        dat_use.sort()
        top_mean = np.mean(dat_use[-1*top_n:])
    return top_mean



##################################################################################################
"""Plotter"""


##########################################
"""IC Tester"""
def plot_ts_by_month(IC_ts,plot=True):
    year_list = list(set(IC_ts.index.year))
    year_list.sort(reverse=False)
    IC_month = pd.DataFrame(index=[i for i in range(1,13)])
    for year in year_list:
        IC_yr = IC_ts.loc[str(year)]
        IC_month[year] = IC_yr.groupby(IC_yr.index.month).mean()
        IC_month_only = IC_ts.groupby(IC_ts.index.month).mean()
        IC_year_only = IC_ts.groupby(IC_ts.index.year).mean()
    if plot==True:
        roll_freq = 60
        ax1 = IC_ts.cumsum().plot(figsize=[11,2],title='ts Cumsum(LHS) & ts Roll %dd Mean(RHS)'%(roll_freq),label='2')
        ax1 = IC_ts.rolling(roll_freq).mean().plot(figsize=[11.6,2],secondary_y=True,label='1')
        plt.show()
        IC_month.fillna(0).plot(kind='bar',figsize=[11.0,2],title='ts by month')
        plt.legend(bbox_to_anchor=(1,1), loc=2, borderaxespad=0.)
        plt.show()
        IC_month_only.plot(kind='bar',figsize=[11,2],title='ts by month only')
        plt.show()
        IC_year_only.plot(kind='bar',figsize=[11,2],title='ts by year only')
        plt.show()
        ts_month = IC_ts.resample('M',label='right').mean()
        ts_month.plot(kind='bar',figsize=[11,2],title='ts by time')
        plt.show()
    print (IC_ts.describe())
    return IC_month



################################################
"""data checker"""

def error_checker(left, right, threshold=0.0001, sample_num=20):
    left_ps = left.dropna()
    right_ps = right.dropna()
    # Error rate check
    mutual_idx = left_ps.index.intersection(right_ps.index)
    # Data look back effect removal
    mutual_idx = mutual_idx[int(mutual_idx.size / 2):]
    left_mut_ps = left_ps.reindex(mutual_idx)
    right_mut_ps = right_ps.reindex(mutual_idx)
    deviation_ps = ((left_mut_ps - right_mut_ps) / (left_mut_ps + right_mut_ps) * 2).abs()
    error_ps = deviation_ps.loc[deviation_ps >= threshold]
    error_rate = len(error_ps) / len(mutual_idx)
    max_error = error_ps.max()
    # Fill rate check
    common_dates = mutual_idx.get_level_values(level=0)
    fill_rate_lst = []
    # Downsampling needed to save time
    common_num = len(common_dates)
    sample_lst = list(set([np.random.randint(0, common_num) for i in range(sample_num)]))
    for item in sample_lst:
        sample_date = common_dates[item]
        fill_rate_lst.append(len(left_ps.loc[sample_date]) / len(right_ps.loc[sample_date]))
    fill_rate_ratio = np.mean(fill_rate_lst)
    return error_rate, max_error, fill_rate_ratio


######################################################
""" calc loss"""
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def calc_loss(y_true,y_pred,loss_type='r2'):
    if len(y_true)!=len(y_pred):
        raise Exception
    mask = np.isfinite(y_true+y_pred)
    if loss_type=='r2':
        model_eval = r2_score(y_true[mask],y_pred[mask])
    return model_eval

