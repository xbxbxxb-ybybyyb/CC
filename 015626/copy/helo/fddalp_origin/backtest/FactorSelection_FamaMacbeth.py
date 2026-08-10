# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 11:08:27 2017

@author: 012315
"""

import os
import pandas as pd
import numpy as np
import copy
import statsmodels.api as sm
import matplotlib.pyplot as plt 
import scipy.stats as sps
from multifactor.backtest.FactorTest import load_data
from datetime import datetime as dt
from functools import reduce
import gc
gc.collect()


factor_folder = 'S:\\Quant\\data\\factor\\jlhForTest3\\'


"""假设现有5个因子(Alpha 1-5)，想要测试5个新的因子加入(Alpha 6-10)

    1. 建立现有因子 existing_factor
    2. 建立一个临时的HDF (new_factor) 存储OLS1 Residual(与现有因子回归)
    3. 如果新因子有效 将新因子Residual 存入existing_factor
    4. 删除 new_factor

"""

#从备选因子库甄选因子进入待合成因子库
#使用adjusted-R排序，事先滤除了市值因子和行业因子


"""读取所有因子库 考虑用HDF5存储所有因子数据进入一个HDF5文件
   减少IO时间"""
   
#Store Data
reg_window = 120
start_date = 20090101
end_date = 20171013
holding_period = 20
HDF5_Name = 'FactorTest'
factor_list_complete = [i.replace(".h5","") for i in os.listdir(factor_folder) if ((i[:7]!='factor_') and (i[-3:]=='.h5'))]
factor_list = factor_list_complete
#factor_list=os.listdir(factor_folder) 


######################
def combine_h5(factor_folder,h5_name=None,factor_list=None):
    """
       combine all single factor h5 file to one h5 for future slice
       you can pass in a customized factor_list to test only factor in the list
       return name of combined h5
    """      
    h5_path = factor_folder+'FamaMacbeth_result\\'
    if (not os.path.exists(h5_path)):
        os.mkdir(h5_path)
        
    factor_master_file = h5_path +'factor_combine.h5' if h5_name==None else h5_name
    if os.path.exists(factor_master_file):
        print ('Existing h5 removed: '+ factor_master_file)    
        os.remove(factor_master_file)
    else:
        print ('New h5 created: ' + factor_master_file)
    #factor_list = [i.replace(".h5","") for i in os.listdir(factor_folder)] if factor_list == None else factor_list 
    factor_combine_store = pd.HDFStore(factor_master_file)
    with pd.HDFStore(factor_master_file) as factor_combine_store:
        for factor_name in factor_list:
            try:
                print ('Moving to HDF5: '+factor_name)
                with pd.HDFStore(factor_folder+factor_name+'.h5') as factor_store:
                    factor_dict = factor_store[factor_name]
                    factor_dict['FactorName'] = factor_name
                    factor_dict = factor_dict.reset_index()
                    factor_dict = factor_dict.set_index(['dt','FactorName','Ticker'])
                    factor_dict.columns = ['FactorExposure']
                factor_combine_store.append('AlphaFactor',factor_dict,min_itemsize = {'FactorName': 20})
            except:
                print (factor_name + " failed...")
    print ('factor combine complete')
    return factor_master_file
######################

# Slice by date
def get_range_data(start_date,end_date,factor_master_file):
    
    """
    get range data for factor selection
    start_date = 20090615
    end_date = 20100615
    """
    print ('Getting factor data for '+str(start_date)+' - '+str(end_date))
    with pd.HDFStore(factor_master_file) as factor_combine_store:
        factor_dict1 = factor_combine_store.select('AlphaFactor',where=["dt>="+str(start_date)+"& dt<="+str(end_date)])
        factor_use = factor_dict1.unstack(level=1)['FactorExposure']
    return factor_use
######################


          
def pick_one_factor(factor_combine,sub_date_list,holding_period,holding_period_ret,criteria='R2'):
    factor_measure = pd.DataFrame()
    print ('#'*10)
    print ('Picking best factor based on '+criteria.upper())
    holding_period_ret = holding_period_ret.loc[sub_date_list]
    factor_list = factor_combine.columns.tolist()
    for factor_name in factor_list:
        print (factor_name)
        factor_dict = factor_combine[factor_name].unstack()
        factor_measure[factor_name]= factor_evaluation(factor_dict,holding_period_ret,holding_period,criteria)
    if criteria == 'R2':
        first_factor_name = factor_measure.mean().idxmax() # max R2
    elif criteria == 'IC':
        first_factor_name = factor_measure.abs().mean().idxmax()  # max abs(IC)
    #os.system('pause')
    #quit()
    print ("Best factor in terms of "+criteria+": "+str(first_factor_name))        
    print ('#'*10)
    first_factor_dict = pd.DataFrame(factor_combine[first_factor_name],columns=[first_factor_name])
    return factor_measure,first_factor_name,first_factor_dict




            


def factor_evaluation(factor_dict,holding_period_ret,holding_period,criteria='R2'):
    """Find first factor in Fama Macbeth Regression
       Assuming factors are already neutralized
       criteria: 'R2','IC' 
    """
    if criteria.upper() == 'R2':
        factor_stat = cross_sectional_regression(factor_dict,holding_period_ret,stock_remain,holding_period)
        factor_stat = factor_stat['R2']
    elif criteria.upper() == 'IC':
        factor_stat = IC_calculation(factor_dict,holding_period_ret)
    return factor_stat

def cs_reg_t(date,stock_remain,factor_dict,holding_period_ret):
    """OLS 1: Return = Factor*Beta + Resid
       输出: ols1.r2,ols1.beta,ols1.tstat"""
    stock_pool = stock_remain[date]
    e = pd.concat([holding_period_ret.loc[date],factor_dict.loc[date]],axis=1)
    e.columns = ['ret','factor']
    e = e.loc[stock_pool]
    e = e.replace([np.inf,-np.inf],[np.nan,np.nan]).dropna()#剔除也许因子值为正无穷和负无穷的值
    if len(e.values)<5:
        return np.nan
    ols1  = sm.OLS(e['ret'],sm.add_constant(e['factor'])).fit()
    return ols1.tvalues[1],ols1.params[1],ols1.rsquared
    
 
def cross_sectional_regression(factor_dict,holding_period_ret,stock_remain,holding_period):               
    date_num,stock_num = factor_dict.shape
    date_list = factor_dict.index
    rebal_num = int(date_num/holding_period)
    reg_stat = np.zeros([rebal_num,3])
    reg_stat[:] = np.nan
    for rebal_idx in range(rebal_num):
        rebal_date = date_list[rebal_idx*holding_period]
        try:
            reg_stat[rebal_idx,:]= cs_reg_t(rebal_date,stock_remain,factor_dict,holding_period_ret)
        except:
            continue
    factor_stat = pd.DataFrame(reg_stat,columns=['Tstat','Beta','R2'],index=[date_list[i*holding_period] for i in range(rebal_num)])
    return factor_stat
    
def IC_calculation(factor_dict,holding_period_ret):
    IC_ts = factor_dict.corrwith(holding_period_ret,axis=1)
    return IC_ts


def DF2MultiIndex(df_dict):
    """pass in dict of df, get df with multi_index"""
    df_mi = pd.DataFrame()
    for df in df_dict:
        df_dict[df] = df_dict[df].reset_index()
        df_dict[df] = df_dict[df].rename(index=str, columns={"Unnamed: 0": "date"})
        df_dict[df]['FactorName'] = df
        df_dict[df] = df_dict[df].set_index(['date','FactorName'])
        df_mi = df_mi.append(df_dict[df])
    return df_mi
    




def ResidualContainer(residual_dict,factor_name,resid_file_name):
    with pd.HDFStore(resid_file_name) as hdf_store:
        residual_dict.columns = residual_dict.columns.astype('object')
        residual_dict = residual_dict.reset_index()
        residual_dict = residual_dict.rename(index=str, columns={"Unnamed: 0": "date"})
        residual_dict['FactorName'] = factor_name
        residual_dict = residual_dict.set_index(['dt','FactorName'])
        hdf_store.append('AlphaFactor',residual_dict, min_itemsize = {'FactorName': 20})
        #print(str(factor_name)+ ' done...')
    return 




"""计算Ttest值,和IC值  - 每日横截面计算股票池"""
def calculated_Ttest(date,stock_remain,factor_dict,Panel,return_df):
    """默认PANEL  收益与因子同期   
        OLS 1: F(factor_to_be_test) = F(Style)*Beta(Style)+X(Industry)*Beta(Industry)+Resid
        OLS 2: R(stock_ret) = Resid*Beta(factor_to_be_test) + resid
        输出: ols1.residual,ols2.tstats,ols2.adj_rsq"""
    date_num,stock_num = factor_dict.shape
    stock_all_code = factor_dict.columns.values.tolist()
    stock_pool = reduce(np.intersect1d,(stock_remain[date],stock_all_code))
    stock_pool=list(set(stock_pool).intersection(set(factor_dict.columns)))
    stock_pool=list(set(stock_pool).intersection(set(return_df.columns)))
    stock_pool=list(set(Panel.xs(date).index).intersection(set(stock_pool)))
    Stock_dataframe = pd.DataFrame([i for i in range(stock_num)],index = stock_all_code).T 
    res = np.array([np.nan for i in range(stock_num)])
    e = Panel.xs(date).loc[stock_pool,:]  #读取以date为索引的数据
    e['factor'] = factor_dict.loc[date,stock_pool].values #加入因子
    e['ret'] = return_df.loc[date,stock_pool]
    e=e.replace([np.inf,-np.inf],[np.nan,np.nan]).dropna()
    if len(e.values)<5:
        return res,np.nan,np.nan
    ols1  = sm.OLS(e['factor'],sm.add_constant(e.iloc[:,:-2])).fit()
    f = copy.deepcopy(e)
    value = Stock_dataframe[e.index].values[0]
    res[value] = ols1.resid # OLS Residual - cross sectional regression
    f['factor'] = ols1.resid
    ols2 = sm.OLS(f['ret'],sm.add_constant(f.iloc[:,:-1])).fit() 
    print('ols fitting result is: tvalue='+str(ols2.tvalues[-1])+' R2='+str(ols2.rsquared_adj))
    return res,ols2.tvalues[-1],ols2.rsquared_adj


def DataNormalize(factor_dict):
    factor_dict = factor_dict.subtract(factor_dict.mean(axis=1),axis=0).divide(factor_dict.std(axis=1,ddof=0),axis=0)
    return factor_dict


def FamaMacBethReg(Panel,factor_dict,return_df,stock_remain,holding_period):
    #print ('Fama MacBeth Regression')
    date_num,stock_num = factor_dict.shape
    date_list_curr = factor_dict.index.tolist()
    rebal_num = int(date_num/holding_period)
    factor_resid = np.zeros([date_num,stock_num])
    factor_tstat = [np.nan]*rebal_num
    factor_rsq = [np.nan]*rebal_num
    factor_resid[:] = np.nan
    for rebal_idx in range(rebal_num):
        rebal_date_idx = rebal_idx*holding_period
        rebal_date = date_list_curr[rebal_date_idx]
        #try:
        factor_resid[rebal_date_idx,:],factor_tstat[rebal_idx],factor_rsq[rebal_idx] = calculated_Ttest(rebal_date,stock_remain,factor_dict,Panel,return_df)
        #except:
        #    continue
    factor_resid = pd.DataFrame(factor_resid,index=return_df.index,columns=return_df.columns)
    return factor_resid,factor_tstat,factor_rsq

def FamaMacBethCurrentIteration(CurrFacList,NewFacList,Panel,return_df,factor_combine,sub_date_list,stock_remain,holding_period,tstat_min,factor_folder,factor_master_file):
    """ At Iteration i, check all new factors, do fama macbeth regression to pick one new factor.
        Change CurrFacList
        factor_combine is current slice of all factor data
    """
    new_fac_num = len(NewFacList)
    if new_fac_num == 0:
        print ('No New Factor Left')
        return 
    else:
        #print ('New Factor Left: '+ str(new_fac_num))
        resid_file_name =  factor_folder+'NewFacLeft_' + str(new_fac_num)+'.h5'
        os.remove(resid_file_name) if os.path.exists(resid_file_name) else None
        new_fac_tstat = pd.DataFrame()
        new_fac_rsq = pd.DataFrame()
        for fac in NewFacList:            
            print (fac)
            if(fac=='NewFacLeft_17'):
                print('here')
            factor_dict = factor_combine[fac].unstack()
            date_list_curr,stock_list_curr = factor_dict.index.tolist(),factor_dict.columns.tolist()
            stock_list_curr=list(set(stock_list_curr).intersection(set(return_df.columns)))
            factor_dict=factor_dict.loc[:,stock_list_curr]
            return_curr = return_df[stock_list_curr].loc[date_list_curr]
            factor_resid,new_fac_tstat[fac],new_fac_rsq[fac] = FamaMacBethReg(Panel,factor_dict,return_curr,stock_remain,holding_period)
            ResidualContainer(factor_resid,fac,resid_file_name) # save interim result for easier checking
    # check T-stat,AdjRsq
        t_abs_avg = abs(new_fac_tstat).mean()
        rsq_avg = new_fac_rsq.mean()
        t_sig_list = t_abs_avg[t_abs_avg>tstat_min].index.tolist()
        FFB_result= pd.DataFrame([t_abs_avg,rsq_avg],index = ['Tstat_abs_avg','Adj_Rsq_avg']).T
        print (FFB_result)
        if len(t_sig_list)>0:
            #find the significant factor with max adj_rsq
            factor_pick = new_fac_rsq[t_sig_list].mean().sort_values(ascending=False).index[0]
            print ('@@@ New Factor Selected: '+factor_pick + ' @@@')
            # insert selected factor into current factor list and panel
            CurrFacList_new = CurrFacList + [factor_pick]
            # Get residual from hdf5 container and append into current factor list 
            #with pd.read_hdf(resid_file_name) as hdf_read:
            factor_pick_resid = pd.read_hdf(resid_file_name,where=['FactorName=='+factor_pick])
            if(factor_pick=='jlh_alpha_new_1'):
                print('here')
            Panel = Panel.append(factor_pick_resid)
            t_sig_list.remove(factor_pick)
    print ('Factor left for next interation: \n'+str(t_sig_list))            
    os.remove(resid_file_name) if os.path.exists(resid_file_name) else None
    return Panel,CurrFacList_new,t_sig_list,FFB_result



"""1. combine all factor to one hdf5 for easier slice later"""
factor_master_file = factor_folder+'FamaMacbeth_result\\'+'factor_combine.h5'
#factor_master_file = combine_h5(factor_folder,factor_folder+'factor_combine.h5',factor_list)


# Pass in one factor dict to get necessary local data for future use
factor_name = factor_list[0] 
           
with pd.HDFStore(factor_folder+factor_name+'.h5') as factor_store:
    factor_MI = factor_store[factor_name]
    
# Get necessary data for later use - will adjust date_list and stock_list
factor_dict,return_df,StyleFactorDict,stock_remain,stock_industry,benchmark_ret,nan_ind,holding_period_ret = load_data(factor_MI,20,benchmark_index='zz500')
date_list = factor_dict.index.tolist()
stock_list = factor_dict.columns.tolist()
date_num,stock_num = factor_dict.shape


NewFactorList = ['Alpha66', 'Alpha31', 'Alpha78', 'Alpha71']
holding_period = 10
    


def FactorSelection_FamaMacBeth(CurrFacList,NewFacList,return_df,stock_remain,holding_period,tstat_min=1,criteria='R2'):
    """
    逐步回归 +正交化算法
    
    假设总共有 假设总共有 假设总共有 K个备选的 个备选的 alpha因子 F1,F2F1,F2F1,F2 F1,F2….Fk .Fk，
    我们已经从中筛选出了S个因子（初始时）， 第 s+1次筛选流程如下：
    
    """
    # neeed : excessIFMonthlyRet
    """Step1.对于剩余备选的ALPHA因子，每个因子每个月都对F1,F2,...,Fs做多元回归，计算残差项。得到K-S个残差项因子分别为E1，E2,...E(K-S)
        Assuming all factor are neutralized by size factor and industry factor
        For each factor(k)            
        1.ols1 FactorNew(k) = FactorCurr(1..k) + Resid(k)
        2.ols2 Return = FactorCurr(1...k) + Resid(k)
        3.Check T-stat/Resid - Find significant T-stat and pick max Adj_Rsq & remove non-sig ones from new factor list           
       Step2.分别把E1.E2,..,E(K-S)和F1,F2,...Fs一起做自变量，做Fama-MacBeth回归，记录EJ系数的显著性，和每个月横截面回归的Adjusted_R^2平均值
       Step3.把系数不显著|T|<2的因子剔除备选alpha因子库
       Step4.选取系数显著且平均Adjusted_R^2最大的因子，假设为0H，则把该因子作为第S+1个筛选出的因子，进入第S+2次筛选
       Step5.如果所有因子系数都不显著，则停止筛选。
    """
    """Iterate until no factor in NewFactorList"""
    iter_num = 1
    tstat_min = -3
    # Get first factor
    #CurrFacList = []
    #NewFacList  = factor_list.copy()
    #holding_period = 20
    sub_date_list = date_list[500:700]
    start_date = dt.strftime(sub_date_list[0],'%Y%m%d')
    end_date = dt.strftime(sub_date_list[-1],'%Y%m%d')
    factor_combine = get_range_data(start_date,end_date,factor_master_file)
    factor_measure,first_factor,first_factor_dict = pick_one_factor(factor_combine,sub_date_list,holding_period,holding_period_ret,criteria='R2')
    CurrFacList.append(first_factor)
    NewFacList.remove(first_factor)
    Panel = first_factor_dict
    FFB_dict = {}
    while len(NewFacList)>0:
        print ('#'*5+'  Iteration:'+str(iter_num)+'  '+'#'*5)
        print ('Current Factor List: \n'+ str(CurrFacList))
        print ('Numer of New Factor:' + str(len(NewFacList)))
        Panel,CurrFacList,NewFacList,FFB_dict[iter_num] = FamaMacBethCurrentIteration(CurrFacList,NewFacList,Panel,return_df,
                                                                                      factor_combine,sub_date_list,stock_remain,holding_period,
                                                                                      tstat_min,factor_folder,factor_master_file)
        iter_num = iter_num+1

    return 
    
        


    

    
    
"""
Factor Selection:
    Wrapper Method: 

To construct a multi-factor portfolio, investors can construct a combined rank for each of the factors by weighting measures
such as performance (Sharpe ratio), diversification and tail risk ranks.


"""    

###########old function




#store_list = Save2HDF5(FactorFolder,HDF5_Name)   
def Save2HDF5(FactorFolder,HDF5_Name):    
    print ('Data Migration Start')
    store_list = [] # store factor list 
    factor_file_list = os.listdir(FactorFolder)
    factor_list = [fac.replace(".csv","") for fac in factor_file_list]
    hdf_store = pd.HDFStore(FactorFolder+HDF5_Name+'.h5')
    for fac in factor_list:
        try:
            tmp_df = pd.read_csv(FactorFolder+str(fac)+'.csv').set_index('Unnamed: 0').iloc[:50,:60]
            tmp_df['FactorName'] = fac
            hdf_store.append('AlphaFactor',tmp_df, min_itemsize = {'FactorName': 20})
            print(str(fac)+ ' dumped into HDF5...')
            store_list.append(fac)
        except:
            print (str(fac)+' failed!!!')
    hdf_store.close()
    print ('Data Migration End')
    return store_list   




def HDF5_Storage_Management(ExistingFactor,NewFactor):
    """ If new factor pass the test:
            push new factor residual to exisitng factor file
        else:
            keep the exsting factor file unchanged
        
        Delete the new factor file for K'th iteration
        
        Loop untill new factor exhausted 
    """
    return 

aaa=FactorSelection_FamaMacBeth(CurrFacList=[],NewFacList=factor_list,return_df=return_df,stock_remain=stock_remain,holding_period=20)
