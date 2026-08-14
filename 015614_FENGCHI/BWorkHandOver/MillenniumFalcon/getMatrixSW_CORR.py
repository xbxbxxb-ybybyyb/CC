# @Time : 2021/9/15 13:24
# @Author : Zhichen Lu
# @File : getMatrix.py
import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python', '/data/user/015664/TriggeredTrading/StrongStockModel', '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master', '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading'])

from StrongStockModel.conf.path_config import root_path
import numpy as np
from dataApi.tradeDate import get_date_range
import pandas as pd
from dataApi.getData import trans_windcode2int, get_minute_1factor
from MillenniumFalcon.basic_conf import _date_list,_cal_date_list,_code_list
from tqdm import tqdm
import numba,os
from scipy.sparse import csc_matrix,find


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
    tail_relation = None
    print('in')
    for year in tqdm(years):
        print(year)
        arr_year_date_list = sorted(list(filter(lambda x: x // 10000 == year, date_list)))
        relation_year_date_list = sorted(list(filter(lambda x: x // 10000 == year, _date_list)))
        arr_start_idx, arr_end_idx = date_list.index(arr_year_date_list[0]), date_list.index(arr_year_date_list[-1])

        relation_arr = np.load(f'{root_path}external_data/Relation/{relation_type}/{year}.npy').astype('float32')
        if tail_relation is None:
            tail_relation = relation_arr[-1, :, :].copy()
        else:
            relation_arr = np.concatenate((tail_relation[None, :, :], relation_arr[1:, :, :]), axis=0)
        relation_arr = relation_arr[relation_year_date_list.index(arr_year_date_list[0]):relation_year_date_list.index(arr_year_date_list[-1]) + 1, :, :]

        factor_arr = arr[arr_start_idx:arr_end_idx + 1, :, :]

        nan_flag = np.isnan(factor_arr)
        factor_arr[nan_flag] = 0
        temp_res = matmul(factor_arr, relation_arr)
        count = matmul((~nan_flag).astype('float32'), (~np.isclose(relation_arr,0)).astype('float32'))
        group_filtered_mean[arr_start_idx:arr_end_idx + 1, :, :] = temp_res / count
        # print(years)
    return group_filtered_mean


fix_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path3/available_factor_list.pkl')
out_path = '/data/group/800442/800319/HFfactor/CrossIndustryCorrDot/data_3d_arr/'
if not os.path.exists(out_path):
    os.makedirs(out_path)
if __name__ == '__main__':
    from xquant.compute.aimr import AIMR
    from dataApi.sendInfo import send_message


    def out_file(factor_name):
        if os.path.exists(f'{out_path}{factor_name}.npy'):
            print(factor_name, 'eixst')
            return
        factor = _load_pickle_frame(factor_name, _cal_date_list, _code_list)
        print('load done')
        norm_factor = normalize_factor(factor)
        print('norm done')
        relationlize_factor = factor_matmul(norm_factor, _date_list, 'SW1')
        np.save(f'{out_path}{factor_name}.npy', relationlize_factor)
        print(factor_name, 'done')
        send_message(['015664'],f'{factor_name}   {out_path}')


    # target_list = list(filter(lambda x: not os.path.exists(f'{out_path}{x}.npy'), fix_factor_list))
    num = 10
    total = len(fix_factor_list)
    i = 0#int(AIMR.getParam())
    target_list = fix_factor_list[total * i // num:total * (i + 1) // num]
    # target_list = target_list[len(target_list)//2:]
    import gc
    for f_name in target_list:
        out_file(f_name)
        gc.collect()


