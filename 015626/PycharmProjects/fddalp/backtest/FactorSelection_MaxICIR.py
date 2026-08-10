# -*- coding: utf-8 -*-
"""

@author: 012315

MAX ICIR

# Use example

holding_period = 20
mean_length = 20
covariance_length = 120
factor_folder = 'S:\\Quant\\backtest\\test_factor\\'
factor_IC,factor_alpha,IR_optimal,factor_weight,factor_weight_complete = MaxICIR_main(factor_folder,holding_period,mean_length,covariance_length,min_factor=0,combine_factor=True,combine_factor_name=None,IC_positive_only=False)
IR_optimal.plot()


"""


import os
import pandas as pd
import numpy as np
from IO import IO
from IO.IO_enums import *
from scipy import linalg
import scipy.optimize as optimize
from sklearn.covariance import ledoit_wolf, OAS, ShrunkCovariance, GraphLassoCV,empirical_covariance
import numpy as np


def IC_calc(factor_dict,holding_period_ret,holding_period,correlation_type='spearman'):
    """IC Decay Test:
       Correlation: IC(T), Return(T+1:T+1+Holding_Period) 
       Correlation for all days 
    """
    if correlation_type=='spearman':
        factor_rank = factor_dict.rank(axis=1)
        IC_ts = factor_rank.corrwith(holding_period_ret.rank(axis=1),axis=1)
    elif correlation_type=='pearson':
        IC_ts = factor_dict.corrwith(holding_period_ret,axis=1)
    dispersion_ts = holding_period_ret.std(axis=1)
    Alpha_ts  = IC_ts*dispersion_ts/holding_period
    return IC_ts,Alpha_ts



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

def get_zscore(df):
    df_zscore = df.subtract(df.mean(axis=1),axis=0).divide(df.std(axis=1,ddof=0),axis=0) #handle nan    
    return df_zscore


from sklearn.covariance import ledoit_wolf, OAS, ShrunkCovariance, GraphLassoCV,empirical_covariance

def covariance_esitmation(X,cov_type='shrink'):
    """covariance matrix esitmation
    cov_type: sample, shrink, graph_lasso,oas
    X: shape (n_samples, n_features) - date*stock
    
    """
    if cov_type =='shrink':
        cov_lw, shrinkage = ledoit_wolf(X)
    elif cov_type == 'graph_lasso':
        graph_lasso = GraphLassoCV().fit(X)
        cov = graph_lasso.covariance_
    elif cov_type == 'sample':
        cov = empirical_covariance(X)
    elif cov_type =='oas':
        cov = OAS().fit(X).covariance_    
    return cov
    




def get_factor_ic_alpha(factor_folder,holding_period,correlation_type='spearman',factor_list=None):
    print ('-'*30)
    if factor_list==None:
        factor_list = [i.replace(".h5","") for i in os.listdir(factor_folder) if (i[:7]!='factor_' and i[-2:]=='h5')]
    # Pass in one factor dict to get necessary local data for future use
    # Get necessary data for later use - will adjust date_list and stock_list
    factor_name = factor_list[0] 
    with pd.HDFStore(factor_folder+factor_name+'.h5') as factor_store:
        factor_MI = factor_store[factor_name]
        factor_dict = MultiIndex2DF(factor_MI)
    start_date,end_date = 20090101,20171013
    # Get Stock Return  
    print ('Getting stock return')
    h5_md = IO.read_data([start_date,end_date],['close','adjfactor'],dsource=DSource.OPTM,max_workers=1)
    md_dict =  MultiIndex2DF(h5_md)
    md_dict['close_adj'] = md_dict['close']*md_dict['adjfactor']
    holding_period_ret = md_dict['close_adj'].shift(-1*holding_period)/md_dict['close_adj']-1# next 10 days return 
    date_list = factor_dict.index.tolist()
    stock_list = factor_dict.columns.tolist()
    date_num,stock_num = factor_dict.shape    
    factor_IC = pd.DataFrame()
    factor_alpha = pd.DataFrame()
    print ('-'*5+'  Calculating Factor IC and Alpha  '+'-'*5)
    for factor_name in factor_list:
        print (factor_name)
        try:
            with pd.HDFStore(factor_folder+factor_name+'.h5') as factor_store:
                factor_MI = factor_store[factor_name]
            factor_dict = factor_MI.unstack()[factor_name]  
            stock_list_tmp = factor_dict.columns.tolist()
            date_list_tmp = factor_dict.index.tolist()
            stock_list_current = np.intersect1d(stock_list,stock_list_tmp).tolist()
            date_list_current = np.intersect1d(date_list,date_list_tmp).tolist()
            factor_dict = factor_dict[stock_list_current].loc[date_list_current] 
            holding_period_ret_current = holding_period_ret[stock_list_current].loc[date_list_current] 
            factor_IC[factor_name],factor_alpha[factor_name] = IC_calc(factor_dict,holding_period_ret_current,holding_period)
        except:
           print (factor_name+' failed!')
    print ('-'*30)
    return factor_IC,factor_alpha


def solve_weight(IC_mean,IC_cov,solve_type='optmize'):
    factor_num = len(IC_cov)
    # analytical solution
    if solve_type =='equation':
        IC_weight = np.dot(linalg.inv(IC_cov),IC_mean)
        weight_scale = IC_weight.sum()
        IC_weight_optimal = IC_weight/weight_scale
    # optimizer            
    elif solve_type =='optmize':
        objective_function = lambda w: -1 * np.dot(w,IC_mean)/np.sqrt(np.dot(np.dot(w,IC_cov),w.T))
        w0 = [1.0/factor_num]*factor_num
        bnds = [(0, 1,) for i in range(factor_num)] # w [0,1]
        cons = ({'type': 'eq','fun': lambda x: np.sum(x) - 1}) # sum(w)=1
        # method = 'L-BFGS-B','TNC ','SLSQP'  - use SLSQP
        opt_result = optimize.minimize(objective_function,w0,bounds=bnds,constraints=cons)
        IC_weight_optimal = opt_result.x
    IR_optimal = np.dot(IC_weight_optimal,IC_mean)/np.sqrt(np.dot(np.dot(IC_weight_optimal,IC_cov),IC_weight_optimal.T))
    return IR_optimal,IC_weight_optimal.tolist()


def max_ICIR_iteration(factor_IC,mean_date_list,cov_date_list,min_factor=0,IC_positive_only=False):
    # check list all factor has data
    """ mean_date_list - time window for factor IC mean
        cov_date_list - time window for factor covariance matrix
    """
    factor_weight = [np.nan]*factor_IC.shape[1]
    IC_current = factor_IC.loc[cov_date_list]
    IC_complete_list = np.isnan(IC_current).sum(axis=0)==0
    if sum(IC_complete_list)<min_factor:
        return np.nan,factor_weight
    IC_take_list = IC_complete_list[IC_complete_list==True].index.tolist()
    IC_take = IC_current[IC_take_list]
    if IC_positive_only == True:
        IC_take_mean = IC_take.loc[mean_date_list].mean(axis=0)  
        IC_take_list =  IC_take_mean[IC_take_mean>0].index.tolist()
        IC_take = IC_current[IC_take_list]
    if len(IC_take_list)<min_factor:
        #print ('Number of factor with complete data < '+ str(min_factor))
        return np.nan,factor_weight
    else:
        #covariance_length = len(cov_date_list)
        IC_mean = IC_take.loc[mean_date_list].mean(axis=0)  
        IC_cov = np.cov(IC_take.T)
        IR_optimal,IC_weight_optimal = solve_weight(IC_mean,IC_cov,solve_type ='optmize')
        #IR_optimal = IR_optimal_orig/(np.sqrt(240.0/covariance_length))
        factor_weight = pd.DataFrame([np.nan]*factor_IC.shape[1],index = factor_IC.columns).T
        factor_weight[IC_take_list] = IC_weight_optimal
    return IR_optimal,factor_weight.values

    

def max_ICIR(factor_IC,mean_length,covariance_length,holding_period,optimize_period=None,min_factor=0,IC_positive_only=False):
    """
    Time Label
    holiding period return - index at start of holding period
    IC - index at start of holding period
    IC mean / IC cov used past information but forward 10 days return
    Thus factor weight should be indexed at the [index + holding period + 1 ]
    for factor at t = 0, weight is marked at t+optimize_period+1;t+optimize_period*2+1
    """
    print ("-"*5+'   Getting Max ICIR Factor Weight   '+"-"*5)
    date_num,factor_num = factor_IC.shape
    date_list = factor_IC.index.tolist()
    window_length = max(mean_length,covariance_length)
    rebal_num = int((date_num-window_length-holding_period-optimize_period-1)/optimize_period)
    rebal_date_list = [date_list[(i)*optimize_period+window_length+holding_period] for i in range(rebal_num)] # account for holding period 
    IR_optimal = [np.nan]*rebal_num
    factor_weight = np.zeros([rebal_num,factor_num])
    factor_weight[:] = np.nan
    factor_weight_complete = np.zeros([date_num,factor_num])
    factor_weight_complete[:] = np.nan
    for i in range(rebal_num):
        idx_start_cov,idx_end = i*optimize_period,i*optimize_period+covariance_length
        idx_start_mean = idx_end - mean_length
        mean_date_list = date_list[idx_start_mean:idx_end]
        cov_date_list = date_list[idx_start_cov:idx_end]
        IR_optimal[i],factor_weight[i,:] = max_ICIR_iteration(factor_IC,mean_date_list,cov_date_list,min_factor,IC_positive_only=False)
        factor_weight_complete[idx_end+holding_period+1:idx_end+holding_period+optimize_period+1,:] = np.tile(factor_weight[i,:],(optimize_period,1))
        #print (i,date_list[idx_end],date_list[idx_end+holding_period])
    IR_optimal = pd.DataFrame(IR_optimal,index=rebal_date_list)    
    factor_weight = pd.DataFrame(factor_weight,index=rebal_date_list,columns=factor_IC.columns)
    factor_weight_complete = pd.DataFrame(factor_weight_complete,index= date_list,columns = factor_IC.columns)
    return IR_optimal,factor_weight,factor_weight_complete

def save2excel(factor_folder,factor_IC,factor_alpha,IR_optimal,factor_weight,factor_weight_complete):
    """Save to excel"""
    excel_path = factor_folder+'result\\'
    if (not os.path.exists(excel_path)):
        os.mkdir(excel_path)
    excel_name = excel_path+'FactorBacktest_IC_Alpha.xlsx'
    print ('Save results to '+ excel_name)
    writer = pd.ExcelWriter(excel_name,engine='xlsxwriter')
    factor_IC.to_excel(writer,sheet_name='IC')
    factor_alpha.to_excel(writer,sheet_name='alpha')
    IR_optimal.to_excel(writer,sheet_name='IR_optimal')
    factor_weight.to_excel(writer,sheet_name='factor_weight')
    factor_weight_complete.to_excel(writer,sheet_name='factor_weight_complete')
    writer.save()  
    return 

def get_weighted_factor(factor_folder,factor_weight_complete):
    """combine factor based on factor_weight"""
    print ("-"*5+"  Combine factor based on optimal weight  "+"-"*5)
    factor_use = factor_weight_complete.sum(axis=0)
    factor_use_list = factor_use.index[factor_use>0].tolist() # only open factor that is used 
    factor_weight_fill = factor_weight_complete.fillna(0)
    for factor_name in factor_use_list:
        print (factor_name)
        with pd.HDFStore(factor_folder+factor_name+'.h5') as factor_store:
            factor_current = factor_store[factor_name].unstack()[factor_name]
        factor_current_weighted = factor_current.fillna(0).multiply(factor_weight_fill[factor_name],axis=0).fillna(0)
        # initialized the first one
        if factor_use_list.index(factor_name)==0:
            factor_combine = factor_current_weighted
        # add the follow on one with weight
        factor_combine = factor_combine.add(factor_current_weighted,fill_value=0)                
    factor_combine_MI = pd.DataFrame(factor_combine.stack(),columns=['factor_MaxICIR'])                                             
    return factor_combine_MI


def DF2H5(df,factor_name,save_path,save_name,df_format='MultiIndex'):
    """save dataframe matrix/MI to multiindex h5"""
    print ('Save location :'+save_path+save_name+'.h5')
    if df_format == 'Matrix':
        data_MI = df.stack().reset_index()
    if df_format == 'MultiIndex':
        data_MI = df.reset_index()
    data_MI.columns = ['dt','Ticker',factor_name]
    data_MI.Ticker = data_MI.Ticker.astype('category')
    data_MI = data_MI.set_index(['dt','Ticker'])
    os.remove(save_path+save_name) if os.path.exists(save_path+save_name) else None
    IO.pd_hdf5_writer(data_MI,save_path+save_name+'.h5',dataset=factor_name)    
    return   



def MaxICIR_main(factor_folder,holding_period,mean_length,covariance_length,optimize_period=None,correlation_type='spearman',min_factor=0,combine_factor=True,combine_factor_name=None,IC_positive_only=True):     
    """ input:
                factor_folder: folder that has all factors' H5 file
                holding_period: time to compute holding period return
                optimize_period: frequency to calculate factor weight
                correlation_type: 'spearman', 'pearson'
                mean_length: look back window for IC average
                covariance_length: look back window for IC covariance matrix
                min_factor: minimum number of factor for each 
                
    """     
    """Calculate IC for all factors"""    
    print ("-"*40)
    print ("-"*5+"   Factor Selection - Max ICIR   "+"-"*5)
    factor_IC,factor_alpha = get_factor_ic_alpha(factor_folder,holding_period,correlation_type='spearman')
    
    """
    #if there existing results of IC,Alpha already
    excel_name = factor_folder+'result\\FactorBacktest_IC_Alpha.xlsx'
    factor_IC = pd.read_excel(excel_name,sheet_name='IC',index_col=0)
    factor_alpha = pd.read_excel(excel_name,sheet_name='alpha',index_col=0)
    """
    """Optimize factor weight by Max ICIR"""
    if optimize_period==None:
        optimize_period = holding_period 
    elif optimize_period>holding_period:
        print ('Warning: optimize_period>holding_period, changed to holding_period.')
        optimize_period = holding_period
    IR_optimal,factor_weight,factor_weight_complete = max_ICIR(factor_IC[f_list],mean_length,covariance_length,holding_period,optimize_period,min_factor=0,IC_positive_only=False)
    
    """Save to excel"""
    save2excel(factor_folder,factor_IC,factor_alpha,IR_optimal,factor_weight,factor_weight_complete)
    
    """Combine Factor"""    
    if combine_factor==True:
        factor_combine_MI = get_weighted_factor(factor_folder,factor_weight_complete)
        save_path = factor_folder+'result\\'
        combine_factor_name = "factor_MaxICIR" if combine_factor_name==None else combine_factor_name
        save_name = combine_factor_name
        DF2H5(factor_combine_MI,combine_factor_name,save_path,save_name,df_format='MultiIndex')
    
    print ('Done')
    print ("-"*40)
    return factor_IC,factor_alpha,IR_optimal,factor_weight,factor_weight_complete

#f_list = ['alp16_zz500_zf','alp14_zz500_zf','z1_zz500_zf','alp10_zz500_zf','size']
#factor_IC_use = factor_IC[f_list].loc[factor_weight.index]
#factor_weight.plot(kind='bar',stacked=True,figsize=(10,8))


# Use example
"""
from backtest.FactorSelection_MaxICIR import MaxICIR_main
holding_period = 20
mean_length = 20
covariance_length = 120
factor_folder = 'W:/zhangf/data/alpha/CHINA_STOCK/DAILY/test/'
factor_IC,factor_alpha,IR_optimal,factor_weight,factor_weight_complete = MaxICIR_main(factor_folder,holding_period,mean_length,covariance_length,min_factor=0,combine_factor=True,combine_factor_name=None,IC_positive_only=False)
IR_optimal.plot()

#
"""

















