import os
import json
import time
import numpy as np
import pandas as pd
from overnight.utility import get_current_date
from overnight.naming_config import TRADING_PLAN
import bottleneck as bk
import pickle

def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict 
    
def read_json(path):
    with open(path, 'r') as fin:
        try:
            data = json.load(fin)
        except json.JSONDecodeError:
            data = None
    return data

def ts_rank(df1, d = 1200):
    # moving time-series rank for the past d periods
    assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
    if d == 1:
        output = df1
    else:
        if isinstance(df1, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                  index=df1.index, columns=df1.columns)
        elif isinstance(df1, pd.Series):
            output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                               index=df1.index, name=df1.name)
    return output

def factor_aggregation(factor_path='/data/user/017024/share/overnight/alpha/Diamond_2_0_20210713/'):
    """
    read factors form the specified folder and aggregate the factors into a dataframe
    :param factor_path: str
        factor storage path
    :return: pd.DataFrame
        aggregated factor matrix, each column is a factor
    """
    factors = sorted([i for i in os.listdir(factor_path) if i.endswith('h5')])
    factors_list = [os.path.join(factor_path, i) for i in factors]
    factor_agg_list = list()
    for i, i_name in enumerate(factors_list):
        factor_temp = pd.read_hdf(i_name)
        factor_agg_list.append(factor_temp)
    factor_agg_df = pd.concat(factor_agg_list, axis=1)
    factor_agg_df.index.name = 'dt'
    return factor_agg_df


def factor_aggregation_csv(factor_path='/data/group/800466/trade/overnight/factor_proof/',
                           trade_time='1449', kind='norm'):
    trading_days = [i for i in sorted(os.listdir(factor_path)) if i.endswith(trade_time)]
    detail_path = [os.path.join(factor_path, i, i) + '.csv' for i in trading_days]
    factor_prod = None
    for i_path in detail_path:
        factor_temp = pd.read_csv(i_path, index_col=0)
        if kind in factor_temp.columns:
            factor_temp = factor_temp[kind]
            factor_temp.name = pd.to_datetime(i_path.split('/')[-2][:8])
            factor_prod = factor_temp if factor_prod is None else pd.concat([factor_prod, factor_temp], axis=1,
                                                                            sort=False)
    factor_prod = factor_prod.T
    factor_prod = factor_prod.sort_index()
    factor_prod.index.name = 'dt'
    return factor_prod
    
    
def minute_flag_check(date):
    path1 = '/data/group/800466/trade/overnight/flag/' + str(date) + '/' + str(date) + '_Diamond_factors_afterday.success'
    path2 = '/data/group/800466/trade/overnight/flag/' + str(date) + '/' + str(date) + '_overnight_factors_hf.success'
    return os.path.exists(path1) and os.path.exists(path2)


def get_signal_df(factor_df):
    factor_mask = factor_df.ge(0.75)
    signal_raw = factor_mask.sum(axis=1) / factor_df.shape[1]
    adj_coef = pd.Series(
        np.searchsorted([0.75, 0.8, 0.85, 0.9, 0.95, 1], factor_df[factor_mask].mean(axis=1)) * 0.2 + 0.4,
        index=signal_raw.index)
    signal_final = signal_raw * adj_coef
    return signal_final


def get_signal_final_Diamond_1_0(factor_df):
    signal = get_signal_df(factor_df[TRADING_PLAN['Diamond_1_0']])
    return signal


def get_signal_final_Diamond_2_0(factor_df):
    future_ic = get_signal_df(factor_df[TRADING_PLAN['future_ic']])
    spot_ic = get_signal_df(factor_df[TRADING_PLAN['spot_ic']])
    future_if = get_signal_df(factor_df[TRADING_PLAN['future_if']])
    spot_if = get_signal_df(factor_df[TRADING_PLAN['spot_if']])
    future_ih = get_signal_df(factor_df[TRADING_PLAN['future_ih']])
    spot_ih = get_signal_df(factor_df[TRADING_PLAN['spot_ih']])
    signal_ic = (future_ic + spot_ic) / 2
    signal_if = (future_if + spot_if) / 2
    signal_ih = (future_ih + spot_ih) / 2
    signal = (signal_ic + signal_if + signal_ih) / 3
    return signal


def get_signal_final_Diamond_2_1(factor_df):
    future_ic = get_signal_df(factor_df[TRADING_PLAN['future_ic_2_1']])
    spot_ic = get_signal_df(factor_df[TRADING_PLAN['spot_ic_2_1']])
    future_if = get_signal_df(factor_df[TRADING_PLAN['future_if_2_1']])
    spot_if = get_signal_df(factor_df[TRADING_PLAN['spot_if_2_1']])
    future_ih = get_signal_df(factor_df[TRADING_PLAN['future_ih_2_1']])
    spot_ih = get_signal_df(factor_df[TRADING_PLAN['spot_ih_2_1']])
    signal_ic = (future_ic + spot_ic) / 2
    signal_if = (future_if + spot_if) / 2
    signal_ih = (future_ih + spot_ih) / 2
    signal = (signal_ic + signal_if + signal_ih) / 3
    return signal


def get_signal_final_Diamond_2_2(factor_df):
    signal = get_signal_df(factor_df[TRADING_PLAN['Diamond_2_2']])
    return signal


def get_signal_final_Diamond_2_3(factor_df):
    signal = get_signal_df(factor_df[TRADING_PLAN['Diamond_2_3']])
    return signal


def get_signal_final_Diamond_3_0(factor_df):
    signal = get_signal_df(factor_df[TRADING_PLAN['Diamond_3_0']])
    return signal


def get_signal_final_Diamond_2_3_1429(factor_df):
    signal = get_signal_df(factor_df[TRADING_PLAN['Diamond_2_3_1429']])
    return signal

def get_sigadj(fac_df):
    print('update_diamond_sig_final')
    fts_ins = read_pickle('/dfs/group/800466/warehouse/prod/MD/CHINA_FUTURES/MINUTE/pre_history/FUTURE_DATA_120101_200901.pkl')
    fts_oos = read_pickle('/data/user/015626/data/warehouse/prod/MD/CHINA_FUTURES/MINUTE/OUTSAMPLE/FUTURE_DATA_2020.pkl')
    cls = fts_ins['close']
    rt = cls/cls.shift(1)-1
    rt_std = rt.rolling(30,min_periods=15).std()
    vol_30_ic = rt_std[fts_ins['recent_month_mask']].sum(axis=1)

    cls = fts_ins['close_if']
    rt = cls/cls.shift(1)-1
    rt_std = rt.rolling(30,min_periods=15).std()
    vol_30_if = rt_std[fts_ins['recent_month_mask']].sum(axis=1)

    vol_ins = pd.concat([vol_30_ic,vol_30_if],axis=1).mean(axis=1).between_time('9:30','14:49')
    vol_ins = vol_ins.groupby(vol_ins.index.date).mean()
    vol_ins.index = [pd.Timestamp(i.year,i.month,i.day) for i in vol_ins.index]
    vol_ins = vol_ins.loc['2012':'2019']
    
    cls = fts_oos['close']
    rt = cls/cls.shift(1)-1
    rt_std = rt.rolling(30,min_periods=15).std()
    vol_30_ic = rt_std[fts_oos['recent_month_mask']].sum(axis=1)

    cls = fts_oos['close_if']
    rt = cls/cls.shift(1)-1
    rt_std = rt.rolling(30,min_periods=15).std()
    vol_30_if = rt_std[fts_oos['recent_month_mask']].sum(axis=1)
    vol_oos = pd.concat([vol_30_ic,vol_30_if],axis=1).mean(axis=1).between_time('9:30','14:49')
    vol_oos = vol_oos.groupby(vol_oos.index.date).mean()
    vol_oos.index = [pd.Timestamp(i.year,i.month,i.day) for i in vol_oos.index]
    vol_oos = vol_oos.loc['2020':]
    
    vol = vol_ins.append(vol_oos)
    vol = (ts_rank(vol,60))
    vollong = vol.copy()
    vollong[vollong < 0] = 0
    
    fac_df[fac_df >= 0.75] = 1
    fac_df[fac_df < 0.75] = 0
    sig = fac_df.sum(axis=1)/190*2
    sig1 = sig.copy()
    sig[sig1 < 0.3] = 0
    sigadj = sig * vollong
    sigadj[sigadj < 0.1] = 0    
    return sigadj, vol
    
if __name__ == '__main__':
    date = get_current_date()
    print(date)
    flag_root = '/data/group/800466/trade/overnight/flag/' + str(date) + '/'
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)
    flag_path_start = flag_root + str(date) + '_Diamond_sig.start'
    with open(flag_path_start, 'w') as file:
        pass
        
    print('------wait minute flag')
    while True:
        if minute_flag_check(date):
            break
        time.sleep(60)
    print('flag check finished!')


    '''因子值导入'''
    factor_prod_1449 = factor_aggregation_csv()['2016':]
    blacklist = ['JPY_AUD_CC','wsc_pv_32_modify','SHIBOR_Overnight_return_CC','wsc25_overnight_cfg_fix','wsc11_overnight_future_modify',
                'wyc_if_2hour_return_nr_as_cfg_fix','wsc28_overnight_cfg_fix','wsc40_overnight_cfg_modify','wsc40_overnight_cfg_fix']
    for i_name in factor_prod_1449.columns:
        if i_name in blacklist:
            continue
        factor_temp = factor_prod_1449[[i_name]]
        factor_temp.index.name = 'dt'
        factor_temp.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/1449/' + i_name + '.h5', key=i_name)
    factor_prod_1449 = factor_aggregation('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/1449/')['2016':]

    factor_prod_1429 = factor_aggregation_csv(trade_time='1429')['2016':]
    for i_name in factor_prod_1429.columns:
        factor_temp = factor_prod_1429[[i_name]]
        factor_temp.index.name = 'dt'
        factor_temp.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/1429/' + i_name + '.h5', key=i_name)
    factor_prod_1429 = factor_aggregation(factor_path='/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/1429/')['2016':]

    '''信号值计算'''    
    
    Diamond_sig_1_0 = get_signal_final_Diamond_1_0(factor_prod_1449)
    Diamond_sig_1_0.name = 'Diamond_sig_1_0'

    Diamond_sig_2_0 = get_signal_final_Diamond_2_0(factor_prod_1449)
    Diamond_sig_2_0.name = 'Diamond_sig_2_0'

    Diamond_sig_2_1 = get_signal_final_Diamond_2_1(factor_prod_1449)
    Diamond_sig_2_1.name = 'Diamond_sig_2_1'

    Diamond_sig_2_2 = get_signal_final_Diamond_2_2(factor_prod_1449)
    Diamond_sig_2_2.name = 'Diamond_sig_2_2'

    Diamond_sig_2_3 = get_signal_final_Diamond_2_3(factor_prod_1449)
    Diamond_sig_2_3.name = 'Diamond_sig_2_3'

    Diamond_sig_3_0 = get_signal_final_Diamond_3_0(factor_prod_1449)
    Diamond_sig_3_0.name = 'Diamond_sig_3_0'

    Diamond_sig_2_3_1429 = get_signal_final_Diamond_2_3_1429(factor_prod_1429)
    Diamond_sig_2_3_1429.name = 'Diamond_sig_2_3_1429'

    Diamond_sigadj,volsig = get_sigadj(factor_prod_1449)
    
    d_1_0 = Diamond_sig_1_0.copy()
    d_1_0[d_1_0<0.16] = 0
    d_1_0 = d_1_0 * 2
    
    Diamond_sig_final = ((Diamond_sigadj + d_1_0)/2).dropna()
    Diamond_sig_final[Diamond_sig_final > 1] = 1
    
    Diamond_sig_1_0.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_1_0_sig.h5', key='Diamond_1_0_sig')
    Diamond_sig_2_0.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_2_0_sig.h5', key='Diamond_2_0_sig')
    Diamond_sig_2_1.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_2_1_sig.h5', key='Diamond_2_1_sig')
    Diamond_sig_2_2.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_2_2_sig.h5', key='Diamond_2_2_sig')
    Diamond_sig_2_3.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_2_3_sig.h5', key='Diamond_2_3_sig')
    Diamond_sig_3_0.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_3_0_sig.h5', key='Diamond_3_0_sig')
    Diamond_sig_2_3_1429.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_2_3_1429_sig.h5', key='Diamond_2_3_1429_sig')
    
    Diamond_sigadj.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_sigadj.h5', key='Diamond_sigadj')
    volsig.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_volsig.h5', key='Diamond_volsig')
    Diamond_sig_final.to_hdf('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/OVERNIGHT/signal/Diamond_sig_final.h5', key='Diamond_sig_final')
    
    flag_path_success = flag_root + str(date) + '_Diamond_sig.success'
    with open(flag_path_success, 'w') as file:
        pass