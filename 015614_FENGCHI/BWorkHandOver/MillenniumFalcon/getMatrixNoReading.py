# @Time : 2021/9/15 13:24
# @Author : Zhichen Lu
# @File : getMatrix.py
import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

from StrongStockModel.conf.path_config import root_path
import numpy as np
from dataApi.tradeDate import get_date_range
import pandas as pd
from dataApi.getData import trans_windcode2int, get_minute_1factor,get_daily_1factor
# from MillenniumFalcon.basic_conf import _date_list,_cal_date_list,_code_list
from tqdm import tqdm
import numba,os
from MillenniumFalcon.IndustryMatrixDaily import get_historical_matrix
from scipy.sparse import csc_matrix,find
from dataApi.usefulTools import delay


def _load_pickle_frame(file_name, date_list, code_list):
    factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
    freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    df_dic = {}
    for time in freq:
        df = pd.read_pickle(factor_address + 'Fix%s_' % time + file_name + '.pkl')
        df.index = df.index.map(int)
        df.columns = df.columns.map(trans_windcode2int)
        df = df.reindex(date_list, code_list)
        df_dic[time] = df
    return np.r_['0,3', tuple(df_dic[x].values for x in freq)].transpose(1, 0, 2)


@numba.jit(nogil=True, nopython=True)
def matmul(dcn, dnn):
    res = np.empty_like(dcn)
    for d in range(dcn.shape[0]):
        res[d] = dcn[d] @ dnn[d]
    return res

def normalize_factor(factor, standardize_days=40,freq=7):
    factor_finite = np.isfinite(factor)

    if standardize_days:
        factor[~ factor_finite] = 0
        factor2 = factor ** 2

        d_cf = factor.sum(axis=1)
        d_cf2 = factor2.sum(axis=1)
        d_cn = factor_finite.sum(axis=1)

        rd_cf = np.lib.stride_tricks.as_strided(d_cf, shape=(
            d_cf.shape[0] - standardize_days + 1, standardize_days, d_cf.shape[1]), strides=(
            d_cf.strides[0], d_cf.strides[0], d_cf.strides[1])).sum(axis=1)

        rd_cf2 = np.lib.stride_tricks.as_strided(d_cf2, shape=(
            d_cf2.shape[0] - standardize_days + 1, standardize_days, d_cf2.shape[1]), strides=(
            d_cf2.strides[0], d_cf2.strides[0], d_cf2.strides[1])).sum(axis=1)

        rd_cn = np.lib.stride_tricks.as_strided(d_cn, shape=(
            d_cn.shape[0] - standardize_days + 1, standardize_days, d_cn.shape[1]), strides=(
            d_cn.strides[0], d_cn.strides[0], d_cn.strides[1])).sum(axis=1).astype(float)

        rd_cn[rd_cn < standardize_days * freq / 2] = np.nan
        factor[~ factor_finite] = np.nan

        rd_mean = (rd_cf / rd_cn)[0: -1]
        rd_std = (((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5)[0: -1]
        rd_std[rd_std == 0] = np.nan

        factor = (factor[standardize_days:] - rd_mean[:, None]) / rd_std[:, None]
        factor = factor.clip(-6, 6)
        factor_finite = np.isfinite(factor)
        factor[~ factor_finite] = 0
        del d_cf, d_cf2, rd_cf, rd_cf2, rd_cn
        return factor
    else:
        return factor


# @numba.jit(nogil=True, nopython=True)
def factor_matmul(arr, date_list, relation_type):
    arr = arr.astype('float32')
    if arr.shape[0] != len(date_list):
        raise Exception('array length and date list are not match')
    if not os.path.exists(f'{root_path}external_data/Relation/{relation_type}/'):
        raise Exception('Unexpected relation type')
    years = sorted(list(set([x // 10000 for x in date_list])))

    group_filtered_mean = np.empty_like(arr)
    # tail_relation = np.zeros((1,len(_code_list),len(_code_list))).astype('float32')
    sw1 = get_daily_1factor('SW1')
    sw1 = sw1.reindex(_code_list,axis=1)
    for year in tqdm(years):
        arr_year_date_list = sorted(list(filter(lambda x: x // 10000 == year, date_list)))
        relation_year_date_list = sorted(list(filter(lambda x: x // 10000 == year, date_list)))
        arr_start_idx, arr_end_idx = date_list.index(arr_year_date_list[0]), date_list.index(arr_year_date_list[-1])

        # relation_arr = np.load(f'{root_path}external_data/Relation/{relation_type}/{year}.npy')

        relation_arr = get_historical_matrix(sw1.loc[[get_pre_trade_date(arr_year_date_list[0])]+arr_year_date_list[:-1]],return_type='3d_arr')
        relation_arr = relation_arr.astype('float32')
        factor_arr = arr[arr_start_idx:arr_end_idx + 1, :, :]
        nan_flag = np.isnan(factor_arr)
        factor_arr[nan_flag] = 0
        temp_res = matmul(factor_arr, relation_arr)
        count = matmul((~nan_flag).astype('float32'), relation_arr)
        group_filtered_mean[arr_start_idx:arr_end_idx + 1, :, :] = temp_res / count
        # print(years)
    return group_filtered_mean

"""
matrix_0406 = pd.read_pickle('/data/group/800319/strategy_local_path3_ForMatrix/relation_matrix/20210402.pkl')['sw1']
factor_0406 = pd.read_pickle('/data/group/800319/strategy_local_path3_ForMatrix/daily_output/20210406/all_factor_1000.pkl').T
factor_0406.columns = factor_0406.columns.map(trans_windcode2int)
matrix_0406.index = matrix_0406.index.map(trans_windcode2int)
matrix_0406.columns = matrix_0406.columns.map(trans_windcode2int)
factor_0406 = factor_0406.reindex(_code_list,axis=1)#.fillna(0)
factor_0406.loc[factor_name]

offline = temp_res[60][0]
offline_count = count[60][0]
online = factor_0406.loc[factor_name].fillna(0) @ matrix_0406.fillna(0)
online_count = np.isfinite(factor_0406.loc[factor_name].fillna(0).values).astype('float32') @ matrix_0406.fillna(0)

compare = pd.DataFrame({'offline':offline/offline_count,'online':online/online_count},index=_code_list)

"""

fix_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path_file/available_factor_list.pkl')
out_path_2 = '/data/group/800442/800319/HFfactor/CrossIndutryMeanSimDailyUpdate20211116/data_3d_arr/'
out_path_2_io = '/data/group/800442/800319/HFfactor/CrossIndutryMeanSimDailyUpdate20211116/data/'
out_path = '/data/group/800442/800319/HFfactor/CrossIndutryMean20211104/data_3d_arr/'
# fix_factor_list = list(filter(lambda x : not os.path.exists(f'{out_path_2_io}{x}.npy'),fix_factor_list))
if not os.path.exists(out_path_2):
    os.makedirs(out_path_2)
if not os.path.exists(out_path_2_io):
    os.makedirs(out_path_2_io)
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
if __name__ == '__main__':
    from xquant.compute.aimr import AIMR
    from dataApi.sendInfo import send_message
    import itertools
    from dataApi.LoadingTool import trans_df2arr
    from dataApi.tradeDate import get_date_range, get_pre_trade_date,get_recent_trade_date
    from dataApi.stockList import get_all_stock_ever_appear

    today = get_recent_trade_date()
    _code_list = get_all_stock_ever_appear(20210531)
    all_date_list = get_date_range(20140701, get_recent_trade_date())
    # _cal_date_list = get_date_range(get_pre_trade_date(_date_list[0], 40), _date_list[-1])

    def out_io_formation(factor,target_path,facotr_name):

        factor_arr = trans_df2arr(factor, start_date=20140801, end_date=all_date_list[-1], roll=True)
        factor_arr = factor_arr.astype('float32')
        factor_arr = np.ascontiguousarray(factor_arr)
        np.save(f'{target_path}{facotr_name}.npy', factor_arr)
        print(facotr_name, 'done')

    def out_file(factor_name):
        exist_date_list = np.load(f'{out_path}date_list.npy')
        loaded_factor = np.load(f'{out_path}{factor_name}.npy',mmap_mode='r')
        """
        loaded_factor = np.memmap(f'{out_path}{factor_name}.npy',dtype='float32',mode='r')
        date_len = loaded_factor.shape[0]/(7*len(_code_list))
        loaded_factor = np.memmap(f'{out_path}{factor_name}.npy',dtype='float32',mode='r',shape=(int(date_len),7,len(_code_list)))
        """
        if loaded_factor.shape[0]==len(all_date_list):
            print(f'{factor_name} exist')
            return
        if len(exist_date_list)!=loaded_factor.shape[0]:
            exist_date_list = all_date_list[:loaded_factor.shape[0]]

        calc_date_list = sorted(list(set(all_date_list) - set(exist_date_list)))
        calc_date_list = get_date_range(get_pre_trade_date(calc_date_list[0],1),calc_date_list[-1])
        _cal_date_list = get_date_range(get_pre_trade_date(calc_date_list[0],40),calc_date_list[-1])
        factor = _load_pickle_frame(factor_name, _cal_date_list, _code_list)
        norm_factor = normalize_factor(factor)
        relationlize_factor = factor_matmul(norm_factor, calc_date_list, 'SW1')

        load_tail = loaded_factor[-1].copy()
        calc_head = relationlize_factor[0].copy()
        load_tail [~np.isfinite(load_tail)] = 0
        calc_head[~np.isfinite(calc_head)] = 0

        if (~np.isclose(load_tail,calc_head)).sum()>0:
            raise Exception(f'{factor_name} exist tail are not match calc head')
        loaded_factor = np.concatenate([loaded_factor,relationlize_factor[1:]],axis=0)
        # np.save(f'{out_path_2}{factor_name}.npy',loaded_factor)

        loaded_factor = pd.DataFrame(loaded_factor.reshape((loaded_factor.shape[0]*7,loaded_factor.shape[-1])),
                                     index=pd.MultiIndex.from_tuples(list(itertools.product(all_date_list,bar_list))),
                                     columns=_code_list)
        out_io_formation(loaded_factor,out_path_2_io,factor_name)



    # target_list = list(filter(lambda x: not os.path.exists(f'{out_path_2_io}{x}.npy'), fix_factor_list))
    # out_file('zhy_fix_5')
    num = 20
    total = len(fix_factor_list)
    i = int(AIMR.getParam())
    target_list = fix_factor_list[total * i // num:total * (i + 1) // num]
    # target_list = target_list[len(target_list)//2:]
    import gc
    import datetime
    for f_name in tqdm(target_list):
        # if datetime.datetime.now()>=datetime.datetime(2021, 11, 5, 6, 9, 10, 224050):
        #     break
        out_file(f_name)
        gc.collect()


