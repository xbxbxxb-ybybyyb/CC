"""utility tools for factor survey"""


import pandas as pd
import numpy as np
import datetime
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
import pickle
import datetime as dt
import os
from functools import partial
from concurrent.futures import ProcessPoolExecutor as Pool
from concurrent.futures import as_completed

from multifactor.backtest.factor_test import SingleFactorTest
from multifactor.backtest.survey_report_generator import generate_pdf
from multifactor.IO import IO
from multifactor.IO.IO_enums import *



def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x: abs(x - current_date) if x <= current_date else 100)
    if current_hour < new_date_time and nearest_date == current_date:
        print('Not till refresh time ' + str(new_date_time) + ':00')
        current_date = fdate_list[fdate_list.index(current_date) - 1]
        print('Use previous trading date: ' + str(current_date))
    elif nearest_date < current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date == current_date:
        print('Right on time: ' + str(current_date))
    return current_date


def date_period_handler(sdate=None, edate=None,new_date_time=18):
    last_day = get_current_date(new_date_time)
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        print('update for one day: ' + str(sdate))
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i <= min(edate, last_day) and i >= sdate]
        sdate, edate = cdate_list[0], cdate_list[-1]
    return sdate, edate


def check_update_date(sdate=None, edate=None, use_len=None,new_date_time=18):
    # check_update_date(sdate=None,edate=None)
    use_len = 0 if use_len is None else use_len
    sdate, edate = date_period_handler(sdate, edate,new_date_time)
    fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i >= sdate and i <= edate]
    idx = max(0, fdate_list.index(cdate_list[0]) - use_len)
    sdate_prev = fdate_list[idx]
    print('-' * 20, '\ndata used: %d - %d ' % (sdate_prev, edate))
    print('factor data: %d - %d \ntotal count: %d' % (sdate_prev, edate, len(cdate_list)))
    print('-' * 20)
    return sdate_prev, edate, cdate_list


def factor_read_test(fac_path,sft,sdate,edate,result_folder):
    tic = time.time()
    test_fac = IO.read_data([sdate,edate],alt = fac_path)
    sft.load_factor(factor_data=test_fac,name=test_fac.columns[0])
    sft.shoot(result_folder=result_folder)   # call function 
    toc = time.time()
    return toc-tic

def multiprocess_wrapper(func,iter_list=None,logger=None,max_process=None,collect_output=False,**kwargs):
    max_process = os.cpu_count() if max_process==None else max_process
    task_number = len(iter_list) if iter_list is not None else len(func)
    tic1 = time.time()
    print_func_info = print if logger is None else logger.info
    print_func_warning = print if logger is None else logger.warning
    
    print_func_info('*'*20)
    start_info = 'start multiprocess -  max process number: %d - task number: %d'%(max_process,task_number)
    print_func_info(start_info)
    if collect_output:
        manager_dict = Manager().dict()
        if iter_list is None:
            if len(func) - len(set(func)) != 0:
                print_func_warning('not unique func input for collecting output')
                raise Exception
        else:
            if len(iter_list) - len(set(iter_list)) != 0:
                print_func_warning('not unique iter list input for collecting output')
                raise Exception
    else:
        manager_dict = None
    with Pool(max_process) as executor:
        print_func_info('*** task initialization ***')
        future_tasks = {}
        init_idx,ex_idx = 0,0
        if iter_list is not None:
            for itr in iter_list:
                init_idx = init_idx + 1
                try:
                    print_func_info('* init %d/%d : %s *'%(init_idx,task_number,itr))
                    future_tasks[executor.submit(func,itr,**kwargs)] = itr
                except Exception as e:
                    print_func_warning('iter task initialization failed: %s - %s'%(itr,s))
        elif iter_list is None:
            for fc in func:
                #print (fc)
                #import pdb
                #pdb.set_trace()
                init_idx = init_idx+1
                try:
                    print_func_info('* init %d/%d : %s'%(init_idx,task_number,fc))
                    future_tasks[executor.submit(fc,**kwargs)] = fc
                except Exception as e:
                    print_func_warning('func task init failed: %s - %s'%(fc,e))
        print_func_info('*** task execution ***')
        key_list = []
        for f in as_completed(future_tasks):
            key = future_tasks[f]
            key_list.append(key)
            ex_idx = ex_idx + 1
            try:
                done_ind = f.done()
            except Exception as e:
                print_func_warning('task execution failed - %s'%(e))
                f.cancel()
            if done_ind:
                try:
                    ts = f.result()
                    if manager_dict is not None:
                        manager_dict[key] = ts
                except Exception as e:
                    print_func_warning('%s'%(e))												
                    ts = None
                    done_ind = None
            else:
                ts = None
            if isinstance(ts,np.float) or isinstance(ts,np.int) :
                print_str = str((round((ts),2)))+'s'
            elif isinstance(ts,str):
                print_str = ts
            else:
                print_str = ''
            done_str = 'done' if done_ind == True else 'fail'
            itr_info = '* %d/%d - %s -%s  %s *'%(ex_idx,task_number,done_str,key,print_str)
            if done_ind:
                print_func_info(itr_info) 
            else:
                print_func_warning(itr_info)
            done_ind = None
                
    toc1 = time.time()
    time_str1 = str((round((toc1-tic1)/60,2)))+'minutes'
    end_info = '***** multiprocess end - %s ***'%(time_str1) + '\n' + '*'*20
						  
    print_func_info(end_info)
    if collect_output:
        return dict(zip(key_list, manager_dict.values()))
    else:
						
        return 

 

def save_pickle(save_dict,save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 
def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict

def calc_trailing_stats(ret_ts,trail_list=[5,10,20,60,120,240],show_type='sum',skip_tail=None):
    trail_list = [i for i in trail_list if i<len(ret_ts)]
    trail_stats = pd.DataFrame()
    for trail_day in trail_list:
        if skip_tail is None:
            ret_sliced = ret_ts.iloc[-trail_day:,:]
        elif isinstance(skip_tail,int):   
            ret_sliced = ret_ts.iloc[-1*skip_tail-trail_day:-1*skip_tail,:]    
        if show_type=='sum':
            use_ret = ret_sliced.sum(axis=0)
        elif show_type=='mean':
            use_ret = ret_sliced.mean(axis=0)
        elif show_type=='annual':
            use_ret = ret_sliced.mean(axis=0)*240
        else:
            print ('show type error: %s'%show_type)
            raise Exception
        trail_stats['last '+str(trail_day)+' days'] = use_ret
    return trail_stats

def get_top_by_time(df,top_num=10,sample_freq='M',agg='sum',index_reformat=True):
    if sample_freq not in ['M','W','A']:
        raise AssertionError
    df_rs = df.resample(sample_freq)
    if agg =='sum':
        df_resample = df_rs.sum()
    elif agg == 'mean':
        df_resample = df_rs.mean()
    elif agg == 'sharpe':
        df_resample = df_rs.sum()/df_rs.std()
    df_resample = pd.DataFrame(df_resample.stack(),columns=['score'])
    df_resample.index.names = ['dt','factor']
    df_resample_sort = df_resample.reset_index().sort_values(['dt','score'],ascending=[True,False]).set_index(['dt','factor'])
    if top_num is not None:
        df_sample_top = df_resample_sort.groupby(['dt']).head(top_num)
    else:
        df_sample_top = df_resample_sort
    if index_reformat:
        if sample_freq=='A':
            str_format = '%Y'
        elif sample_freq=='M':
            str_format = '%Y-%m'
        df_sample_top = df_sample_top.reset_index()
        df_sample_top['dt'] = [datetime.datetime.strftime(i,str_format) for i in df_sample_top['dt']]
        df_sample_top = df_sample_top.set_index(['dt','factor'])
    return df_sample_top 


def get_ts_idea(df,q_cut=[1,0.9,0.5,0.1,0],sample_freq='M'):
    q_list = ['top %d'%(round(1-q,2)*100)+'%' for q in q_cut]
    ts_idea = pd.DataFrame(columns=q_cut)
    for q in q_cut:
        ts_idea[q] = df.quantile(q=q,axis=1)
    if sample_freq in ['M','W','A']:
        ts_idea = ts_idea.resample(sample_freq).mean()
    ts_idea.columns =q_list
    return ts_idea



        
def get_dist_pct(df,range_list=None):
    if range_list is None:
        range_list = [-0.15] + [round(-0.05+0.025*i,3) for i in range(5)] + [0.15] 
    dist = pd.DataFrame(columns=range_list[1:])    
    for i in range(1,len(range_list)):
        dist[range_list[i]] = ((range_list[i-1]<df) & (df<=range_list[i])).sum(axis=1)
    dist.columns = ['(%0.3f,%0.3f]'%(range_list[i-1],range_list[i]) for i in range(1,len(range_list))]
    dist_pct = dist.divide(dist.sum(axis=1),axis=0).dropna(axis=1)
    return dist_pct

def pairwise_correlation(df,method='pearson',min_pct=0.5,remove_diag=True):
    #{‘pearson’, ‘kendall’, ‘spearman’}
    pw_corr = df.corr(method=method,min_periods=int(min_pct*len(df)))
    if remove_diag:
        np.fill_diagonal(pw_corr.values,np.nan)
    return pw_corr
    



################ For mutli thread - faster read and compute ########################################


def func_parallel(func,input_list,output_name_list=None,concat_axis=0,max_workers=10):
    tic = time.time()
    total_job = len(input_list)
    if output_name_list is not None:
        list_collector_dict = {k:[] for k in output_name_list}  
    else:
        list_collector = []
    print ('-'*20,' Start ','-'*20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file_list = {executor.submit(func, file_path): file_path for file_path in input_list}
        #future_to_file_list = {executor.submit(func, sdate=sdate,edate=edate,stockcode=stockcode):stockcode for stockcode in stocklist}
        for future in concurrent.futures.as_completed(future_to_file_list):
            file_path = future_to_file_list[future]
            try:
                data = future.result()
                if output_name_list is None:
                    list_collector.append(data)
                else:
                    for key in output_name_list:
                        list_collector_dict[key].append(data[output_name_list.index(key)])
            except Exception as exc:
                print('%r generated an exception: %s' % (file_path, exc))
            else:
                #print('%d/%d - %r' % (input_list.index(file_path)+1,total_job,file_path))
                print('%d/%d' % (input_list.index(file_path)+1,total_job))
        print ('concating results')
        if output_name_list is None:
            data_collector = pd.concat(list_collector,axis=concat_axis)
        else:
            data_collector = {}
            for key in output_name_list:
                data_collector[key] = pd.concat(list_collector_dict[key],axis=concat_axis)
    toc = time.time()
    print (toc-tic)
    print ('-'*20,' End ','-'*20)
    return data_collector


def extract_excel(excel_name,ic_type):
    with pd.ExcelFile(excel_name) as xls_handle:
        sum_df = pd.read_excel(xls_handle, sheetname='summary_info')
        seg_ret = pd.read_excel(xls_handle, sheetname='seg_return', index_col=0)
        seg_ret_after_cost = pd.read_excel(xls_handle, sheetname='seg_return_after_cost')
        bucket_ic_30 = pd.read_excel(xls_handle, sheetname='bucket_ic_30', index_col=0)
        IC_ts = pd.read_excel(xls_handle, sheetname='IC_ts', index_col=0)
        stock_count = pd.read_excel(xls_handle, sheetname='stock_count', index_col=0)

    factor_name = sum_df.loc['Factor Name'].values[0]
    q_num = 'Q'+ str(seg_ret.shape[1] - 2)
    fac_sign = 1 if (seg_ret['Q1'] - seg_ret[q_num]).mean()>=0 else - 1
    q_max = q_num if fac_sign == -1 else 'Q1'
    ic_ts = pd.DataFrame(IC_ts[ic_type])*fac_sign
    bucket_ic_30.columns,stock_count.columns,ic_ts.columns= [factor_name],[factor_name],[factor_name]
    max_q_ts = pd.DataFrame(seg_ret[q_max] - seg_ret['Index'],columns=[factor_name])
    max_q_ts_after_cost = pd.DataFrame(seg_ret_after_cost[q_max] - seg_ret_after_cost['Index'],columns=[factor_name])
    factor_sign = pd.DataFrame([fac_sign],columns=[factor_name],index=['factor_sign'])
    return ic_ts,max_q_ts,max_q_ts_after_cost,bucket_ic_30,stock_count,factor_sign

def extract_pickle(pickle_name,ic_type):
    """
    pickle_name = r'A:\zhisj\public\factor_status\zhisj2\factor_report\bac_nis\FactorBacktest_bac_nis.pkl'
    ic_type = 'IC Neutralized'
    """
    output_dict = read_pickle(pickle_name)
    sum_df = output_dict['summary_info']
    seg_ret = output_dict['seg_return']
    seg_ret_after_cost = output_dict['seg_return_after_cost']
    bucket_ic_30 = output_dict['bucket_ic_30']
    IC_ts = output_dict['IC_ts']
    factor_name = sum_df.loc['Factor Name'].values[0]
    stock_count = output_dict['stock_count']
    q_num = 'Q'+ str(seg_ret.shape[1] - 2)
    fac_sign = 1 if (seg_ret['Q1'] - seg_ret[q_num]).mean()>=0 else - 1
    q_max = q_num if fac_sign == -1 else 'Q1'
    ic_ts = pd.DataFrame(IC_ts[ic_type])*fac_sign
    bucket_ic_30.columns,stock_count.columns,ic_ts.columns= [factor_name],[factor_name],[factor_name]
    max_q_ts = pd.DataFrame(seg_ret[q_max] - seg_ret['Index'],columns=[factor_name])
    max_q_ts_after_cost = pd.DataFrame(seg_ret_after_cost[q_max] - seg_ret_after_cost['Index'],columns=[factor_name])
    factor_sign = pd.DataFrame([fac_sign],columns=[factor_name],index=['factor_sign'])
    return ic_ts,max_q_ts,max_q_ts_after_cost,bucket_ic_30,stock_count,factor_sign


def calc_seg_performance(max_q_df):
    days_in_year = 240
    excess_ret = max_q_df.mean()*days_in_year
    track_error = max_q_df.std()*(days_in_year**0.5)
    max_q_stats =  pd.concat([excess_ret,track_error,excess_ret/track_error],axis=1)
    max_q_stats.columns = ['excess_ret','track_error','info_ratio']
    max_q_stats = max_q_stats.sort_values('excess_ret',ascending=False)
    return max_q_stats

def calc_ic_performance(ic_ts_df):
    ic_stats = pd.concat([ic_ts_df.mean(),ic_ts_df.std(),ic_ts_df.mean()/ic_ts_df.std()],axis=1)
    ic_stats.columns = ['ic_mean','ic_std','icir']
    ic_stats = ic_stats.sort_values('icir',ascending=False)
    return ic_stats

def excel_saver(output_dict,excel_name):
    writer = pd.ExcelWriter(excel_name,engine='xlsxwriter')
    for key in output_dict:
        output_dict[key].to_excel(writer,sheet_name=key)
    writer.save()
    return 

def excel_reader(excel_name,index_col=0):
    output_dict = {}
    with pd.ExcelFile(excel_name) as xls_handle:
        tab_list = xls_handle.sheet_names
        for tab in tab_list:
            output_dict[tab] = xls_handle.parse(tab,index_col=index_col)
    return output_dict


def max_drawdown(capital_line, interest_type='SIMPLE'):
    # return max draw down in decimal
    mdd_end = np.argmax(np.maximum.accumulate(capital_line) - capital_line)
    if mdd_end == 0:
        return np.nan
    mdd_start = np.argmax(capital_line[:mdd_end])
    if interest_type == 'SIMPLE':
        mdd = capital_line[mdd_start] - capital_line[mdd_end]
    else:
        mdd = 1 - capital_line[mdd_end] / capital_line[mdd_start]
    return -mdd

def dict_slicer(dict_total,sdate,edate):
    sdate_dt,edate_dt = dt.datetime.strptime(str(sdate),'%Y%m%d'), dt.datetime.strptime(str(edate),'%Y%m%d')
    dict_sliced = {}
    for fac in dict_total:
        if isinstance(dict_total[fac].index[0],pd.Timestamp):
            dict_sliced[fac] = dict_total[fac].loc[sdate_dt:edate_dt]
        else:
            dict_sliced[fac] = dict_total[fac]
    return dict_sliced


def calc_factor_score(data_dict):
    ic_sliced = data_dict['ic_ts_df']
    bucket_ic = data_dict['bucket_ic_30_df']
    max_q_after_cost = data_dict['max_q_after_cost_df']
    stock_count = data_dict['stock_count_df']
    ic_mean,ic_std  = ic_sliced.mean(), ic_sliced.std()
    ic_ir = ic_mean/ic_std
    excess_ret_after_cost = max_q_after_cost.mean()*240
    tracking_error_after_cost = max_q_after_cost.std()*np.sqrt(240)
    info_ratio_after_cost = excess_ret_after_cost/tracking_error_after_cost
    bucket_ic_mean = bucket_ic.mean()
    factor_len = (stock_count>0).sum()
    hit_rate = (max_q_after_cost>0).sum(axis=0)/factor_len
    remove_top_mask = max_q_after_cost<max_q_after_cost.quantile(q=0.95,axis=0)
    excess_ret_after_cost_remove_top = max_q_after_cost[remove_top_mask].mean()*240
    max_q_after_cost_cumsum = (max_q_after_cost.fillna(0)+1).cumprod()
    mdd = pd.Series(list(map(max_drawdown,max_q_after_cost_cumsum.T.values)),index = max_q_after_cost_cumsum.columns)
    return2mdd = excess_ret_after_cost/mdd
    factor_score = pd.concat([ic_mean,ic_ir,bucket_ic_mean,excess_ret_after_cost,info_ratio_after_cost,hit_rate,
                  excess_ret_after_cost_remove_top,mdd,return2mdd],axis=1)
    factor_score.columns =['ic_mean','ic_ir','bucket_ic','excess_ret_after_cost','info_ratio_after_cost','hit_rate',
                           'excess_ret_after_cost_remove_top','mdd','return2mdd']        
    return factor_score

    
def evaluate_factor(output_dict,in_sample,out_of_sample):
        #in_sample = [20140101,20161231]
        #out_of_sample = [20170101,20180914]
    [sdate_in,edate_in] = in_sample
    [sdate_ots,edate_ots] = out_of_sample
        
    dict_in = dict_slicer(output_dict,sdate_in,edate_in)
    dict_ots = dict_slicer(output_dict,sdate_ots,edate_ots)
    factor_score_in = calc_factor_score(dict_in)
    factor_score_ots = calc_factor_score(dict_ots)
    return factor_score_in,factor_score_ots

def calc_factor_score_ranking(factor_score_in,factor_score_ots):
    reverse_list = [i for i in factor_score_in.columns if i!='mdd']
    in_rank = factor_score_in.rank(axis=0)/len(factor_score_in)
    ots_rank = factor_score_in.rank(axis=0)/len(factor_score_in)
    
    in_rank[reverse_list] = 1- in_rank[reverse_list] 
    ots_rank[reverse_list] = 1- ots_rank[reverse_list] 
    
    in_rank_overall = in_rank.mean(axis=1)
    ots_rank_overall = ots_rank.mean(axis=1)
    overall_rank = (in_rank_overall + ots_rank_overall)/2
    score_rank = pd.concat([overall_rank,in_rank_overall,ots_rank_overall],axis=1)    
    score_rank.columns = ['overall_rank','in_rank_overall','ots_rank_overall']
    return score_rank











def collect_factor_test_stats(base_path,sdate,edate,holding_period=10,
                              ic_type='IC Neutralized',analyst_name='NA',
                              in_sample=None,out_of_sample=None):
    print('collecting stats')
    edate_dt = pd.Timestamp(dt.datetime.strptime(str(edate), '%Y%m%d'))
    factor_name_list = os.listdir(base_path)
    print ('%d/%d collected')
    try:
        print('fecth single factor test result from pickle')
        input_list2 = [os.path.join(base_path,factor_name,'FactorBacktest_'+factor_name+'.pkl') for factor_name in factor_name_list]
        func2 = partial(extract_pickle_v2,ic_type=ic_type)
        #output_dict = func_parallel_v2(func2,input_list2,output_name_list=['max_q','ic','stock_count'],concat_axis=1,max_workers=10)
        output_dict = func_parallel_v2(func2,input_list2,
                                       output_name_list=['ic_ts','max_q_ts','max_q_ts_after_cost','bucket_ic_30','stock_count'],
                                       concat_axis=1,max_workers=10)
        
    except:
        print('failed to fetch result from pickle')
        raise Exception
        
    output_dict = dict_slicer(output_dict,sdate,edate)
    
    max_q_df,ic_ts_df,stock_count_df = output_dict['max_q_ts'],output_dict['ic_ts'],output_dict['stock_count']
    max_q_after_cost_df, bucket_ic_30_df = output_dict['max_q_ts_after_cost'],output_dict['bucket_ic_30']
    # drop duplicates
    max_q_df = max_q_df.T.groupby(level=0).first().T
    ic_ts_df = ic_ts_df.T.groupby(level=0).first().T
    max_q_stats = calc_seg_performance(max_q_df)
    max_q_stats_by_year = max_q_df.groupby(max_q_df.index.year).apply(calc_seg_performance)
    ic_stats = calc_ic_performance(ic_ts_df)
    ic_stats_by_year = ic_ts_df.groupby(ic_ts_df.index.year).apply(calc_ic_performance)
    
    max_q_sort_measure = 'excess_ret'
    trail_list = [5,10,20,60,120,240]
    show_top_num_per_time = 20

    max_q_stats_by_year.index.names = ['dt', 'year']
    ic_stats_by_year.index.names = ['dt', 'year']
    max_q_stats_by_year_sorted = max_q_stats_by_year.reset_index().sort_values(['dt',max_q_sort_measure],ascending=False).set_index(['dt','year'])
    max_q_stats_by_year_top = max_q_stats_by_year_sorted.groupby('dt').head(show_top_num_per_time)
    trail_max_q = calc_trailing_stats(max_q_df,trail_list=trail_list,show_type='sum',skip_tail=holding_period) 
    trail_ic = calc_trailing_stats(ic_ts_df,trail_list=[5,10,20,60,120,240],show_type='mean',skip_tail=holding_period) 
    
    max_q_per_month = get_top_by_time(max_q_df,top_num=show_top_num_per_time,sample_freq='M',agg='sum',index_reformat=True)
    max_q_per_year = get_top_by_time(max_q_df,top_num=show_top_num_per_time,sample_freq='A',agg='sum',index_reformat=True)
    ic_per_month = get_top_by_time(ic_ts_df,top_num=show_top_num_per_time,sample_freq='M',agg='mean',index_reformat=True)
    ic_per_year = get_top_by_time(ic_ts_df,top_num=show_top_num_per_time,sample_freq='A',agg='mean',index_reformat=True)
    
    max_q_per_month_total = get_top_by_time(max_q_df,top_num=None,sample_freq='M',agg='sum',index_reformat=True)
    max_q_monthly = max_q_per_month_total['score'].unstack()
    ic_per_month_total = get_top_by_time(ic_ts_df,top_num=None,sample_freq='M',agg='mean',index_reformat=True)
    ic_monthly = ic_per_month_total['score'].unstack()
    
    factor_count_ts = np.isfinite(max_q_df).sum(axis=1)
    
    max_q_cut_list = [-0.15] + [round(-0.05+0.025*i,3) for i in range(5)] + [0.15] 
    ic_cut_list = [-0.2] + [round(-0.05+0.025*i,3) for i in range(5)] + [0.2] 
    max_q_ret_dist_pct = get_dist_pct(max_q_monthly,range_list=max_q_cut_list)
    ic_dist_pct = get_dist_pct(ic_monthly,range_list=ic_cut_list)
    
    positive_excess_ret_roll = (max_q_df.resample('M').mean()>0).sum(axis=1)
    positive_excess_ret_roll = positive_excess_ret_roll.reset_index()
    positive_excess_ret_roll.columns=['dt','# of factor with positive return']
    positive_excess_ret_roll['dt'] = [datetime.datetime.strftime(i,'%Y-%m') for i in positive_excess_ret_roll['dt']]
    positive_excess_ret_roll = positive_excess_ret_roll.set_index('dt').reindex(max_q_ret_dist_pct.index)
    
    # calc factor correlation
    max_q_corr = pairwise_correlation(max_q_df,method='pearson',min_pct=0.5,remove_diag=True)
    ic_corr = pairwise_correlation(ic_ts_df,method='pearson',min_pct=0.5,remove_diag=True)
    
    ic_summary = ic_stats.describe().drop('std',axis=0)
    max_q_summary = max_q_stats.describe().drop('std',axis=0)
    
    # correlation 
    correlation_stats = pd.concat([max_q_corr.mean().describe(),ic_corr.mean().describe()],axis=1)
    correlation_stats.columns = ['Excess Return','IC']
    
    ic_mean,icir_mean = ic_stats['ic_mean'].mean(),ic_stats['icir'].mean()
    er_mean,ir_mean = max_q_stats['excess_ret'].mean(),max_q_stats['info_ratio'].mean()
    #analyst = 'zhisj'
    val_list = [analyst_name,'%d-%d'%(sdate,edate),len(ic_ts_df.columns),ic_mean,icir_mean,er_mean,ir_mean]
    key_list = ['Analyst','Period','Count','IC','ICIR','ER','IR']
    summary = pd.DataFrame(val_list,index=key_list,columns=['summary_stats'])

    analyst_factor_stats_path = os.path.join(base_path,'analyst_factor_stats.csv')
    if os.path.exists(analyst_factor_stats_path):
        factor_path_directory = pd.read_csv(os.path.join(base_path,'analyst_factor_stats.csv'),index_col=0,parse_dates=[1,2])
        factor_path_directory = factor_path_directory.sort_values('last date',ascending=False)
    else:
        factor_path_directory = pd.DataFrame()
        
    output_dict = {'summary':summary,'path':factor_path_directory,'max_q_summary':max_q_summary,'ic_summary':ic_summary,
                        'correlation_stats':correlation_stats,
                        'ic_corr':ic_corr,
                        'max_q_corr':max_q_corr,'positive_excess_ret_roll':positive_excess_ret_roll,'ic_dist_pct':ic_dist_pct,
                        'max_q_ret_dist_pct':max_q_ret_dist_pct,'factor_count_ts':factor_count_ts,
                        'ic_per_year':ic_per_year,'ic_per_month':ic_per_month,
                        'max_q_per_year':max_q_per_year,'max_q_per_month':max_q_per_month,
                        'trail_ic':trail_ic,'trail_max_q':trail_max_q,
                        'max_q_stats_by_year_top':max_q_stats_by_year_top,
                        'max_q_stats':max_q_stats,'ic_stats':ic_stats,'max_q_stats_by_year':max_q_stats_by_year,
                        'ic_stats_by_year':ic_stats_by_year,'max_q_df':max_q_df,'ic_ts_df':ic_ts_df,
                        'stock_count_df':stock_count_df,'max_q_after_cost_df':max_q_after_cost_df, 
                        'bucket_ic_30_df':bucket_ic_30_df
                        }
    
    if in_sample is not None and out_of_sample is not None:
        print('evaluting factors for in sample and out of sample')
        factor_score_in,factor_score_ots = evaluate_factor(output_dict,in_sample,out_of_sample)
        output_dict['factor_score_in_sample'] = factor_score_in
        output_dict['factor_score_out_of_sample'] = factor_score_ots
        
    output_path_excel = os.path.join(base_path,'factor_summary.xlsx')
    output_path_pkl = os.path.join(base_path,'factor_summary.pkl')
    print('saving collected stats to:%s'%base_path)
    excel_saver(output_dict, output_path_excel)
    save_pickle(output_dict, output_path_pkl)
    print('generating pdf')
    generate_pdf(excel_name=output_path_excel,output_folder=base_path)
    print('***** all done ******')
    return     
    
