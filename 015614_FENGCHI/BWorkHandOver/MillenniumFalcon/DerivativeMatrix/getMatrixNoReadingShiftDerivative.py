# @Time : 2021/9/15 13:24
# @Author : Zhichen Lu
# @File : getMatrix.py
import sys; print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])
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

def get_group_by_barra(factor_name,group_nums=30):
    factor = pd.read_hdf('/data/group/800002/basic_data/full/financial_data/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5',factor_name)[factor_name].unstack()
    factor.columns = factor.columns.map(trans_windcode2int)
    factor.index = factor.index.map(lambda x : int(x.strftime('%Y%m%d')))

    factor_rank = factor.rank(axis=1,pct=True)
    factor_rank = factor_rank//(1./group_nums)
    return factor_rank


def get_group_df(factor_name,group_nums=30):
    # barra = pd.read_hdf('/data/group/800002/basic_data/full/financial_data/RISK/CHINA_STOCK/DAILY/STYLEFACTOR/RISK_CHINA_STOCK_DAILY_STYLEFACTOR.h5','Beta')
    barra_factor = ['Beta', 'BookToPrice', 'DividendYield', 'EarningsQuality', 'EarningsVariability', 'EarningsYield', 'Growth', 'Industry', 'InvestmentQuality',
     'Leverage','Liquidity', 'LongTermReversal', 'MidCapitalization', 'Momentum', 'Profitability', 'ResidualVolatility', 'Size']
    if factor_name in barra_factor:
        factor = get_group_by_barra(factor_name,group_nums)
    else:
        factor = get_daily_1factor(factor_name)
    return factor


# @numba.jit(nogil=True, nopython=True)
def factor_matmul(arr, date_list, relation_type,shift,code_list):
    arr = arr.astype('float32')
    if arr.shape[0] != len(date_list):
        raise Exception('array length and date list are not match')
    years = sorted(list(set([x // 10000 for x in date_list])))

    group_filtered_mean = np.empty_like(arr)
    # tail_relation = np.zeros((1,len(_code_list),len(_code_list))).astype('float32')
    group_info_df = get_group_df(relation_type)
    group_info_df = group_info_df.reindex(code_list,axis=1)
    for year in tqdm(years):
        arr_year_date_list = sorted(list(filter(lambda x: x // 10000 == year, date_list)))
        relation_year_date_list = sorted(list(filter(lambda x: x // 10000 == year, date_list)))
        arr_start_idx, arr_end_idx = date_list.index(arr_year_date_list[0]), date_list.index(arr_year_date_list[-1])

        # relation_arr = np.load(f'{root_path}external_data/Relation/{relation_type}/{year}.npy')
        if shift:
            relation_arr = get_historical_matrix(group_info_df.loc[[get_pre_trade_date(arr_year_date_list[0])]+arr_year_date_list[:-1]],return_type='3d_arr')
        else:
            relation_arr = get_historical_matrix(group_info_df.loc[arr_year_date_list],return_type='3d_arr')
        relation_arr = relation_arr.astype('float32')
        factor_arr = arr[arr_start_idx:arr_end_idx + 1, :, :]
        nan_flag = np.isnan(factor_arr)
        factor_arr[nan_flag] = 0
        temp_res = matmul(factor_arr, relation_arr)
        count = matmul((~nan_flag).astype('float32'), relation_arr)
        group_filtered_mean[arr_start_idx:arr_end_idx + 1, :, :] = temp_res / count
        # print(years)
    return group_filtered_mean

def out_file(factor_name,shift,out_path_io,all_date_list,code_list,relation_type):
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
    _cal_date_list = get_date_range(get_pre_trade_date(date_list[0],40),date_list[-1])
    factor = _load_pickle_frame(factor_name, _cal_date_list, code_list)
    norm_factor = normalize_factor(factor)
    relationlize_factor = factor_matmul(norm_factor, date_list, relation_type,shift=shift,code_list=code_list)

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

fix_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path_file/available_factor_list.pkl')
bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]

def main(out_path_io,relation_type):

    from xquant.compute.aimr import AIMR
    import datetime
    today = 20220117#get_recent_trade_date()
    # today = get_pre_trade_date(today)
    _code_list = get_all_stock_ever_appear(today)
    _all_date_list = get_date_range(20140701, today)
    # out_file('zhy_fix_5',shift=False)
    if not os.path.exists(out_path_io):
        os.makedirs(out_path_io)
    # num = 1
    total = len(fix_factor_list)
    i,num =  eval(AIMR.getParam())
    target_list = fix_factor_list[total * i // num:total * (i + 1) // num]
    # target_list = target_list[len(target_list)//2:]
    import gc
    for f_name in tqdm(target_list[::-1]):
        import datetime
        now = datetime.datetime.now()
        from dataApi.tradeDate import get_recent_trade_date

        if now.strftime('%H%M') > '0610' and now.strftime('%H%M') < '0920' and get_recent_trade_date(int(now.strftime('%Y%m%d'))) == int(now.strftime('%Y%m%d')):
            break
        out_file(f_name,shift=True,out_path_io=out_path_io,all_date_list=_all_date_list,code_list=_code_list,relation_type=relation_type)
        gc.collect()

if __name__ == '__main__':
    base_factor_list = ['Growth','BookToPrice', 'DividendYield', 'EarningsQuality', 'EarningsVariability', 'EarningsYield', 'Growth', 'Industry', 'InvestmentQuality',
     'Leverage','Liquidity', 'LongTermReversal', 'MidCapitalization', 'Momentum', 'Profitability', 'ResidualVolatility', 'Size','Beta']
    for each in base_factor_list:
        main(f'/data/group/800442/800319/HFfactor/BarraCrosslize/{each}/data/',each)
#    main('/data/group/800442/800319/HFfactor/BarraCrosslize/Liquidity/data/','Liquidity')



