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
from dataApi.LoadingTool import trans_df2arr
import itertools
from dataApi.tradeDate import get_date_range, get_pre_trade_date, get_recent_trade_date
from dataApi.stockList import get_all_stock_ever_appear
from dataApi.FixFactorRollPrepare import loadFixTensorize
import itertools

def _load_pickle_frame(file_name, date_list, code_list, add='/arch1/group/800442/800319/MinFactorSuper/FactorFixData/Factor/'):
    factor, labl, nolimit_pool, _date_list, _time_list, _code_list =\
        loadFixTensorize(start=date_list[0],end=date_list[-1],factor_list=[file_name],limit=1.1,
                         nolimit_type='df', return_type='dict',address=add,swap_head_tail_axis=False)
    index = pd.MultiIndex.from_tuples(list(itertools.product(date_list,_time_list)))
    factor = factor[file_name].reindex(code_list, axis=1).reindex(index, axis=0)
    nolimit_pool = nolimit_pool.reindex(code_list, axis=1).reindex(index, axis=0)
    return factor.values.reshape(len(date_list),len(_time_list),len(code_list)),\
    nolimit_pool.values.reshape(len(date_list), len(_time_list), len(code_list)),


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
def factor_matmul(arr, date_list, relation_type,shift,code_list):
    arr = arr.astype('float32')
    if arr.shape[0] != len(date_list):
        raise Exception('array length and date list are not match')
    if not os.path.exists(f'{root_path}external_data/Relation/{relation_type}/'):
        raise Exception('Unexpected relation type')
    years = sorted(list(set([x // 10000 for x in date_list])))

    group_filtered_mean = np.empty_like(arr)
    # tail_relation = np.zeros((1,len(_code_list),len(_code_list))).astype('float32')
    sw1 = get_daily_1factor('SW1')
    sw1 = sw1.reindex(code_list,axis=1)
    for year in tqdm(years):
        arr_year_date_list = sorted(list(filter(lambda x: x // 10000 == year, date_list)))
        relation_year_date_list = sorted(list(filter(lambda x: x // 10000 == year, date_list)))
        arr_start_idx, arr_end_idx = date_list.index(arr_year_date_list[0]), date_list.index(arr_year_date_list[-1])

        # relation_arr = np.load(f'{root_path}external_data/Relation/{relation_type}/{year}.npy')
        if shift:
            relation_arr = get_historical_matrix(sw1.loc[[get_pre_trade_date(arr_year_date_list[0])]+arr_year_date_list[:-1]],return_type='3d_arr')
        else:
            relation_arr = get_historical_matrix(sw1.loc[arr_year_date_list],return_type='3d_arr')
        relation_arr = relation_arr.astype('float32')
        factor_arr = arr[arr_start_idx:arr_end_idx + 1, :, :]
        nan_flag = np.isnan(factor_arr)
        factor_arr[nan_flag] = 0
        temp_res = matmul(factor_arr, relation_arr)
        count = matmul((~nan_flag).astype('float32'), relation_arr)
        group_filtered_mean[arr_start_idx:arr_end_idx + 1, :, :] = temp_res / count
        # print(years)
    return group_filtered_mean

def out_file(factor_name,shift,out_path_io,all_date_list,code_list):
    idx_date = np.load('/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/idx_date.npy')
    idx_time = np.load('/data/group/800442/800319/HFfactor/RealTimeFixRollRobust/data/idx_time.npy')
    time_len = idx_time.shape[0]
    if not os.path.exists(f'{out_path_io}{factor_name}.npy'):
        date_list = all_date_list.copy()
    else:
        exist_data = np.memmap(f'{out_path_io}{factor_name}.npy',dtype='float32',offset=128,mode='r')
        exist_date_list = sorted(list(set(idx_date[:exist_data.shape[0]//time_len])))
        date_list = all_date_list[all_date_list.index(exist_date_list[-1])+1:]
    if not date_list:
        print(f'{factor_name} are already update to latest day')
        return
    date_list = get_date_range(get_pre_trade_date(date_list[0],1),date_list[-1])
    # _cal_date_list = get_date_range(get_pre_trade_date(date_list[0],40),date_list[-1])
    factor,_ = _load_pickle_frame(factor_name, date_list, code_list=code_list)
    # norm_factor = normalize_factor(factor)
    relationlize_factor = factor_matmul(factor, date_list, 'SW1',shift=shift,code_list=code_list)

    loaded_factor = pd.DataFrame(relationlize_factor.reshape((relationlize_factor.shape[0]*7,relationlize_factor.shape[-1])),
                                 index=pd.MultiIndex.from_tuples(list(itertools.product(date_list,bar_list))),
                                 columns=code_list)
    if not os.path.exists(f'{out_path_io}{factor_name}.npy'):
        start_date = 20140801
    else:
        start_date = date_list[1]

    factor_arr = trans_df2arr(loaded_factor, start_date=start_date, end_date=all_date_list[-1], roll=True)
    factor_arr = factor_arr.astype('float32')
    factor_arr = np.ascontiguousarray(factor_arr)
    if not os.path.exists(f'{out_path_io}{factor_name}.npy'):
        np.save(f'{out_path_io}{factor_name}.npy', factor_arr)
    else:
        if idx_date[:exist_data.shape[0]//time_len+factor_arr.shape[0]].max()!=all_date_list[-1]:
            raise Exception('Not Match')
        fp = np.memmap(f'{out_path_io}{factor_name}.npy',dtype='float32',mode='r+',
                       offset=128+exist_data.shape[0]*4,shape=factor_arr.shape)
        fp[:] = factor_arr
        del fp



bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]

def main(out_path_io):
    fix_factor_list = list(map(lambda x: x.replace('.npy', ''),
                               os.listdir(
                                   '/arch1/group/800442/800319/MinFactorSuper/FactorFixData/Factor/')))  # pd.read_pickle('/data/group/800319/strategy_local_path_file/available_factor_list.pkl')
    fix_factor_list = list(set(fix_factor_list) - set(['idx_date', 'idx_code', 'idx_time', 'nolimit', 'future']))
    fix_factor_list = list(filter(lambda x: x.startswith('M5'), fix_factor_list))
    fix_factor_list = list(filter(lambda x: not os.path.exists(f'{out_path_io}/{x}.npy'), fix_factor_list))

    from xquant.compute.aimr import AIMR
    import datetime
    today = 20211106#get_recent_trade_date()
    # today = get_pre_trade_date(today)
    _code_list = get_all_stock_ever_appear(today)
    _all_date_list = get_date_range(20140701, today)
    # out_file('M520201207125811515',shift=True,out_path_io=out_path_io,all_date_list=_all_date_list,code_list=_code_list)

    if not os.path.exists(out_path_io):
        os.makedirs(out_path_io)
    num = 1
    total = len(fix_factor_list)
    i =  0#int(AIMR.getParam())
    target_list = fix_factor_list[total * i // num:total * (i + 1) // num]
    # target_list = target_list[len(target_list)//2:]
    import gc
    print(f'{len(target_list)} target list len')
    for f_name in tqdm(target_list):
#        if datetime.datetime.now()>=datetime.datetime(2021, 11, 30, 6, 9, 10, 224050):
#            break
        print(f_name)
        out_file(f_name,shift=True,out_path_io=out_path_io,all_date_list=_all_date_list,code_list=_code_list)
        gc.collect()


if __name__ == '__main__':
    main('/data/group/800442/800319/HFfactor/CrossIndutryMeanShift5min/data/')



