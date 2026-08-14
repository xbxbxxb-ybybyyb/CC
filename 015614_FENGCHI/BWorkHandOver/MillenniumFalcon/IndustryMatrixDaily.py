# @Time : 2021/9/6 14:33
# @Author : Zhichen Lu
# @File : IndustryMatrix.py

import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])

import pandas as pd
import numpy as np
from StrongStockModel.conf.path_config import root_path
from dataApi.getData import get_minute_1factor
from dataApi.getData import get_daily_1factor,trans_windcode2int,trans_int2windcode
from tqdm import tqdm
import os,gc,re,time

from MillenniumFalcon.basic_conf import _date_list,_code_list,_cal_date_list



def get_relation_matrix(arr,ignore_trace=False):
    group_num = np.unique(arr[np.isfinite(arr)])
    group_matrix = np.zeros((len(arr),len(arr)),dtype='float32')
    for group_val in group_num:
        group = np.argwhere(arr==group_val).flatten()
        for item in group:
            group_matrix[item,group] = 1
    if ignore_trace:
        for idx in range(group_matrix.shape[0]):
            group_matrix[idx,idx] = 0
    return group_matrix.astype('float32')

def get_historical_matrix(df,code_list=None,date_list=None,return_type='arr',use_bar = False):
    if code_list:
        df = df.reindex(code_list,axis=1)
    else:
        code_list = df.columns.tolist()
    if date_list:
        df = df.reindex(date_list,axis=0)
    else:
        date_list = df.index.tolist()


    if return_type=='3d_arr':
        relation_matrix = np.empty((len(date_list),len(code_list),len(code_list)))
        pre_idx = 0
        bar = list(enumerate(date_list))
        if use_bar:
            bar = tqdm(bar)

        for idx,date in bar:
            if pre_idx is None:
                pre_idx = idx
            # arr = df.values[idx]
            both_nan = np.isnan(df.values[idx]) & np.isnan(df.values[pre_idx])
            not_equal = df.values[idx] != df.values[pre_idx]
            not_equal[both_nan] = False
            if not_equal.sum() or idx==0:
                relation_matrix[idx,:,:] = get_relation_matrix(df.values[idx],ignore_trace=True)
                pre_idx = idx
            else:
                relation_matrix[idx, :, :] = relation_matrix[pre_idx,:,:]
        return relation_matrix
    else:
        pre_arr = df.values[0]
        relation_matrix = {}
        relation_matrix[date_list[0]] = get_relation_matrix(pre_arr,ignore_trace=True)
        for idx,date in enumerate(date_list[1:]):
            arr = df.values[idx]
            both_nan = np.isnan(arr) & np.isnan(pre_arr)
            not_equal = pre_arr!=arr
            not_equal[both_nan] = False

            if not_equal.sum():
                pre_arr = arr
                relation_matrix[date] = get_relation_matrix(arr,ignore_trace=True)
                print(date)
            else:
                continue

    if return_type=='arr':
        return relation_matrix
    elif return_type=='df':
        return {x:pd.DataFrame(relation_matrix[x],index=code_list,columns=code_list)  for x in relation_matrix}
    else:
        raise Exception('Wrong type')


def get_fix_factor_list(restore=False, factor_address='/data/group/800442/800319/HFfactor/RealTimeFixRollCrosslize/data/'):

    if restore:
        factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
        freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
        factor_list = sorted(list({x[8:-4] for x in os.listdir(
            factor_address) if re.match('^Fix1[0134][03]0_', x)}))
        factor_list = [x for x in factor_list if len([y for y in os.listdir(
            factor_address) if x in y and len(x) == len(y) - 12]) == len(freq)]
    else:
        remove_list = ['idx_date', 'idx_time', 'idx_code', 'nolimit', 'future', 'raw_idx_date', 'raw_idx_code']
        factor_list = sorted(
            [x[:-4] for x in os.listdir(factor_address) if (x[:-4] not in remove_list) & (x[0] != '_')])
    return factor_list

def get_corr_matrix(date_list,code_list):
    minute_close = get_minute_1factor('close',start_datetime=date_list[0],end_datetime=date_list[-1])
    minute_close = minute_close.reindex(code_list,axis=1)
    corr = np.empty((len(date_list),len(code_list),len(code_list)))
    for idx,date in tqdm(list(enumerate(date_list))):
        corr[idx,:,:] = minute_close.loc[date].corr().values
    return corr

if __name__ == '__main__':

    # date = 20210406
    # sw = get_daily_1factor('SW1')
    # relation_arr_dict = get_historical_matrix(sw.loc[[date]], return_type='df')
    # relation_df = relation_arr_dict[date].reindex(_code_list,axis=0).reindex(_code_list,axis=1)
    # relation_df.index = relation_df.index.map(trans_int2windcode)
    # relation_df.columns = relation_df.columns.map(trans_int2windcode)
    # from ExtraTools import get_path_conf
    # path_conf = get_path_conf('/data/group/800319/strategy_local_path3_ForMatrix/')
    # pd.to_pickle(relation_df,path_conf['matrix_conf']+f'{get_pre}.pkl')

    # out_path = f'{root_path}external_data/Relation/SW1/'
    # for year in tqdm(range(2014, 2022)):
    #     sw_relation = np.load(f'{root_path}external_data/Relation/SW1/{year}.npy').astype('float32')
    #     corr_matric = np.load(f'{root_path}external_data/Relation/CORR/{year}.npy').astype('float32')
    #     sw_relation[np.isnan(sw_relation)] = 0
    #     corr_matric[np.isnan(corr_matric)] = 0
    #     sw_corr = sw_relation*corr_matric
    #     np.save(f'{root_path}external_data/Relation/SW1_CORR/{year}.npy',sw_corr)

    # if not os.path.exists(out_path):
    #     os.makedirs(out_path)
    # for year in range(2014,2022):
    #     temp_date_list = sorted(list(filter(lambda x: x // 10000 == year, _date_list)))
    #     corr_arr = get_corr_matrix(temp_date_list,_code_list)
    #     np.save(f'{out_path}{year}.npy',corr_arr)
    #     del corr_arr
    #     gc.collect()


    from dataApi.tradeDate import get_date_range
    _date_list = get_date_range(20140701,20211112)
    e = time.time()
    sw1 = get_daily_1factor('SW1').loc[_date_list]#loc[20140701:20210531]
    sw1 = sw1.reindex(_code_list,axis=1)
    out_path = f'{root_path}external_data/Relation/SW1_daily/'
    if not os.path.exists(out_path):
        os.makedirs(out_path)
    for year in range(2015,2022):


        temp_date_list = sorted(list(filter(lambda x : x//10000==year,_date_list)))

        e = time.time()
        relation_arr = get_historical_matrix(sw1.loc[temp_date_list],return_type='3d_arr')
        total_calc = time.time() - e

        e = time.time()
        relation_arr_read = np.load(f'/data/group/800442/800319/junkData/StrongStock/external_data/Relation/SW1/{year}.npy',mmap_mode='r')
        total_read = time.time() - e

        day1_matrix = get_relation_matrix(sw1.loc[temp_date_list].iloc[0],True)
        (day1_matrix - relation_arr_read[0]).sum()







