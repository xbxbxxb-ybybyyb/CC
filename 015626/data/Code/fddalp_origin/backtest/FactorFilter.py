# -*- coding: utf-8 -*-
"""
FactorFilter 
Summary Factor Statistics
@zsj

"""


import os
import pandas as pd
import numpy as np
import copy
import statsmodels.api as sm
import matplotlib.pyplot as plt 
import scipy.stats as sps
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import datetime as dt






def get_file(result_folder,suffix=None):
    factor_location = {}
    suffix='xlsx' if suffix is None else suffix
    for dirname, dirnames, filenames in os.walk(result_folder):
        for subdirname in dirnames:
            subdirpath = os.path.join(dirname, subdirname)
            excel_name = [file_name for file_name in os.listdir(subdirpath) if file_name.endswith('xlsx')]
            if len(excel_name)>0:
                file_path  = subdirpath+"\\"+excel_name[0]
                factor_name= excel_name[0].replace("FactorBacktest_","").replace(".xlsx","")
            #factor_list.append(factor_name)
            #factor_path.append(file_path)
                factor_location[factor_name] = file_path
    print ('factor count: %d'%(len(factor_location.keys())))
    return factor_location

result_folder = 'S:\\Quant\\backtest\\backtest_output\\zsj\\zsj_pv\\'
factor_location = get_file(result_folder)

excel_name = factor_location['res_std_zz500_nis']

def get_excel_data2(excel_name,factor_type=None):
    fac_summary = pd.read_excel(excel_name,sheetname='因子信息')
    IC_stats =  pd.read_excel(excel_name,sheetname='因子IC序列统计')
    [factor_name,test_period,universe,stock_count,date_count,holding_period] = fac_summary['Summary'].values.tolist()
    [IC_mean,IC_std,ICIR] = IC_stats['IC_original'].values.tolist()
    start_date,end_date = test_period[:10],test_period[-10:]
    if factor_type is None:
        if int(holding_period)<=10:
            factor_type=='PV'
        else:
            factor_type=='Fundamental'
    Is_Neutral = 'Y' if 'nis' in factor_name else 'N'
    location = excel_name[:excel_name.rfind('\\')+1]
    factor_data_list = [factor_name,factor_type,universe,start_date,end_date,holding_period,IC_mean,ICIR,Is_Neutral,location]
    return factor_data_list


def get_factor_summary2(result_folder,save_location=None):
    header_list = ['factor_name','factor_type','universe','start_date','end_date','holding_period','IC_mean','ICIR','Is_Neutral','location']
    print ('1. traversing folder:\n%s'%(result_folder))    
    factor_location = get_file(result_folder)
    factor_data_contain = []
    factor_name_contain = []
    factor_list = list(factor_location.keys())
    #excel_list = list(factor_location.values())
    print ('2. collecting factor stats')
    for i in range(len(factor_list)):   
        factor_name = factor_list[i]
        print ('Checking %d/%d: %s'%(i,len(factor_list),factor_name))
        try:
            factor_data_list = get_excel_data2(factor_location[factor_name])     
            factor_data_contain.append(factor_data_list)
            factor_name_contain.append(factor_name)
        except:
            print("No data")            
    factor_master = pd.DataFrame(factor_data_contain,index=factor_name_contain,columns=header_list)
    
    now=dt.datetime.today()
    file_date=now.strftime("%Y%m%d_%H%M%S")    
    
    save_location = result_folder+'factor_summary_'+file_date+'.xlsx' if save_location is None else save_location
    print ('3. factor summary saved in:\n%s'%(save_location))    
    factor_master.to_excel(save_location)
    print ('done')
    return factor_master



def get_excel_data(excel_name,factor_name):  
    fac_stat = pd.read_excel(excel_name,sheetname='因子原始统计')
    seg_ret_performance = pd.read_excel(excel_name,sheetname='分层测试_组合表现')
    fac_TIC_Test =  pd.read_excel(excel_name,sheetname='T值与IC检验')
    IC_decay =  pd.read_excel(excel_name,sheetname='因子IC有效期')
    fac_stat.columns = [factor_name]
    best_long_short.columns = [factor_name]
    fac_TIC_Test.columns = [factor_name]
    seg_ret_ls.columns = [factor_name]
    IC_stat.columns = [factor_name]
    turnoverstat.columns = [factor_name]    
    factor_collect = pd.concat([fac_stat,best_long_short,seg_ret_ls,fac_TIC_Test,IC_stat,turnoverstat],axis=0)
    return factor_collect


def get_factor_summary(result_folder):
    suffix = 'xlsx'
    factor_list,factor_path = get_file(result_folder,suffix)
    factor_master = pd.DataFrame()
    for i in range(len(factor_list)):   
        print ('Checking '+str(i+1)+"   "+ factor_list[i])
        try:
            factor_stat = get_excel_data(factor_path[i],factor_list[i])     
            factor_master = pd.concat([factor_master,factor_stat],axis=1)           
        except:
            print("No data")            
    factor_master.to_excel("S:\\Quant\\backtest\\"+'factor_summary.xlsx')
    return factor_master




result_folder ='W:/xudy/prod/md/norm_ii/keg'
factor_master = get_factor_summary2(result_folder)

















































































