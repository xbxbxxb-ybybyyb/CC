import sys
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/BWorkHandOver')
sys.path.append('/data/user/015614/BWorkHandOver/ensemblemonitor-strategy-python')
sys.path.append('/data/user/015614/BWorkHandOver/StrongStockModel')
# from online_conf import init_conf_path, holding_info_path, vol_info_path, code_list_path, \
#     restrict_list_path, local_config_path, hyper_param_path,model_config_path,path_for_930
from xquant.factordata import FactorData
from Tool.AmtClip import calc_halved_vol

from StrongStockModel.dataApi.tradeDate import trade_minutes, get_date_range, get_pre_trade_date,get_recent_trade_date
from StrongStockModel.dataApi.stockList import trans_int2windcode, trans_windcode2int, clean_stock_list
from StrongStockModel.dataApi.getData import get_minute_1factor, get_daily_1factor


from multiprocessing import Pool,Manager
from dataApi.stockList import get_all_stock_ever_appear
import pandas as pd
import numpy as np
import bottleneck
import configparser
import os
import gc
import requests
import json
import time



def multiprocess(lines, func, iterable, *args):
    pool = Pool(processes=lines)
    print('多进程启动')
    pool_apply_async = {}
    for j in range(lines):
        sub_iter = iterable[j::lines]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args + (j,))
    pool.close()
    print('等待%s个进程全部完成...' % lines)
    pool.join()
    print('多进程结束！')
    return pool_apply_async

def send_message(users, msg):

    token_url = ('http://168.7.124.15:1080/cgi-bin/gettoken?corpid=wwd53282142c96185d&corpsecret='
                 'Pk0ewu3nuo6JhEaBj_EkuCyiALj0RuISWuZeJcoPdhI')
    send_url = "http://168.7.124.15:1080/cgi-bin/message/send?access_token={}"
    con = requests.get(token_url)
    json_text = json.loads(con.text)
    access_token = json_text["access_token"]
    post_url = send_url.format(access_token)

    if isinstance(users, list):
        users = '|'.join(users)

    data = {"touser": users,
            "msgtype": "text",
            "agentid": 1000033,
            "text": {"content": msg}}
    json_data = json.dumps(data)
    requests.post(post_url, json_data)

def _load_pickle_frame(file_name, date_list, code_list):

    factor_address = '/data/group/800002/alpha_factor/lib/x_factor_lib/'
    freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    df_dic = {}
    for time in freq:
        df = pd.read_pickle(factor_address + 'Fix%s_' % time + file_name + '.pkl')
        df.index = df.index.map(int)
        df.columns = df.columns.map(trans_windcode2int)
        df = df.loc[date_list[0]: date_list[-1]]
        df = df.reindex(columns=code_list)
        df_dic[time] = df
    return np.r_['0,3', tuple(df_dic[x].values for x in freq)].transpose(1, 0, 2)

def _add_realtime_frame(file_name, date, code_list):

    factor_address = '/data/group/800002/realtime/alpha/x_day_lib/%s' % date
    freq = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    df_dic = {}
    for time in freq:
        df = pd.read_pickle('%s/%s/Fix%s_%s.pkl' % (factor_address, time, time, file_name))
        df.columns = df.columns.map(trans_windcode2int)
        df = df.reindex(columns=code_list)
        df_dic[time] = df
    return np.r_['0,3', tuple(df_dic[x].values for x in freq)].transpose(1, 0, 2)

def _calc_mv(factor, axis=(0, 1)):

    factor_finite = np.isfinite(factor)
    factor[~ factor_finite] = 0
    factor2 = factor ** 2

    d_cf = factor.sum(axis=axis)
    d_cf2 = factor2.sum(axis=axis)
    d_cn = factor_finite.sum(axis=axis, dtype=float)

    d_cn[d_cn < np.asanyarray(factor.shape)[list(axis)].prod() / 2] = np.nan

    rd_mean = d_cf / d_cn
    rd_std = ((d_cf2 - d_cf ** 2 / d_cn) / (d_cn - 1)) ** 0.5
    rd_std[rd_std == 0] = np.nan
    return rd_mean, rd_std

def _calc_mv2(factor):

    factor_finite = np.isfinite(factor)
    factor[~ factor_finite] = 0
    factor2 = factor ** 2

    standardize_days = 40
    freq = factor.shape[1]

    d_cf = factor.sum(axis=1)
    d_cf2 = factor2.sum(axis=1)
    d_cn = factor_finite.sum(axis=1)

    weight = np.ones(standardize_days)

    rd_cf = np.apply_along_axis(np.convolve, 0, d_cf, weight, 'valid')[-1]
    rd_cf2 = np.apply_along_axis(np.convolve, 0, d_cf2, weight, 'valid')[-1]
    rd_cn = np.apply_along_axis(np.convolve, 0, d_cn, weight, 'valid')[-1]

    rd_cn[rd_cn < standardize_days * freq / 2] = np.nan

    rd_mean = rd_cf / rd_cn
    rd_std = ((rd_cf2 - rd_cf ** 2 / rd_cn) / (rd_cn - 1)) ** 0.5
    rd_std[np.isclose(rd_std, 0)] = np.nan

    return rd_mean, rd_std

def _forward_fill(arr, axis, zero_fill=True):

    arr = arr.swapaxes(axis, -1)
    if zero_fill:
        mask = arr == 0
    else:
        mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[-1]), 0)
    np.maximum.accumulate(idx, axis=-1, out=idx)
    out = arr[tuple(np.arange(idx.shape[x])[(None, ) * x + (slice(None), ) + (None, ) * (idx.ndim - x - 1)]
                    for x in range(idx.ndim - 1)) + (idx, )]
    out = out.swapaxes(axis, -1)
    return out

def get_core(df, freq=242):

    if len(str(df.index[0])) > 8:
        arr = df.values.reshape(df.shape[0] // freq, freq, df.shape[1]).transpose(1, 0, 2)
    else:
        arr = df.values
    return arr

def find_trade_min(sign_min, delay_min=1, order_keep_min=30):

    sign_min = sign_min if sign_min < 242 else trade_minutes.index(sign_min)
    trade_min = [sign_min + delay_min + x for x in range(order_keep_min)]
    if trade_min[0] >= 241:
        trade_min = [242]
    elif trade_min[-1] >= 238:
        trade_min = list(range(min(trade_min[0], 238), 242))
    if len(trade_min) > order_keep_min:
        trade_min = trade_min[:order_keep_min - 1] + [241]
    elif trade_min == [242]:
        trade_min = [242] * order_keep_min
    elif len(trade_min) < order_keep_min:
        trade_min = trade_min + [241] * (order_keep_min - len(trade_min))
    return trade_min

def roll_mean(x, w, window=5, minutes=30, axis=1):

    x[~ np.isfinite(x)] = 0
    valid = bottleneck.move_sum(w, window=window, axis=axis) / minutes
    valid[valid < window / 2] = np.nan
    arr = bottleneck.move_sum(x, window=window, axis=axis) / valid
    arr[~ np.isfinite(arr)] = np.nan
    arr = _forward_fill(arr, axis=axis, zero_fill=False)
    return arr

def get_code_list(target_day,T_plus_1_day):

    stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, trade_mode=False,
                                  start_date=target_day, end_date=target_day)
    stock_pool = stock_pool.iloc[0][stock_pool.iloc[0]].index.to_list()

    restrict_list = pd.read_pickle(f'{non_fix_in_path}{T_plus_1_day}/restrict_list{target_day}.pkl')
    code_list = sorted(list(set(stock_pool) - set([int(x[:-3]) for x in restrict_list])))
    code_list = [trans_int2windcode(x) for x in code_list]
    return code_list

def get_recent_vol_info(target_day, rolling_window, bar_list, order_keep_min=30, delay_min=1):

    date_list = get_date_range(get_pre_trade_date(target_day, rolling_window * 2 - 1), target_day)
    _adjfactor = get_daily_1factor('adjfactor', date_list)
    code_list = _adjfactor.columns.to_list()
    _adjfactor = get_core(_adjfactor)

    _high = get_core(get_daily_1factor('high', date_list, code_list))
    _low = get_core(get_daily_1factor('low', date_list, code_list))
    _pre_close = get_core(get_daily_1factor('pre_close', date_list, code_list))

    vol = get_core(get_minute_1factor('vol', date_list[0], date_list[-1], code_list=code_list)) / _adjfactor
    close = get_core(get_minute_1factor('close', date_list[0], date_list[-1], code_list=code_list))

    limitup = (close / _pre_close > 1.098) & (_high == close)
    limitup = np.r_[limitup[[0]], limitup[:-1]]
    limitdown = (close / _pre_close < 0.902) & (_low == close)
    limitdown = np.r_[limitdown[[0]], limitdown[:-1]]
    nolimit = ~ (limitup | limitdown)

    idx = np.asanyarray([find_trade_min(x, delay_min, order_keep_min) for x in bar_list])
    idx[idx == idx.max()] -= 1

    vol = (vol * nolimit)[idx].sum(axis=1)
    nolimit = nolimit[idx].sum(axis=1)
    vol_roll = roll_mean(vol, nolimit, rolling_window, order_keep_min)
    vol_roll = pd.DataFrame(vol_roll[:, -1], index=bar_list, columns=code_list)
    vol_roll.columns = vol_roll.columns.map(trans_int2windcode)
    return vol_roll

def get_mv(target_day,file_name,date_list,code_list,rd_mean,rd_std):
    factor = _load_pickle_frame(file_name, date_list, code_list)
    if factor.shape[0] == len(date_list) - 1:
        print("Add last day [%s] factor [%s] by realtime data instead." % (target_day, file_name))
        factor = np.r_[factor, _add_realtime_frame(file_name, date_list[-1], code_list)]
    elif factor.shape[0] < len(date_list) - 1:
        raise Exception("Exception on data loading.")
    mean, std = _calc_mv(factor)
    rd_mean[file_name] = pd.Series(mean,index=code_list)
    rd_std[file_name] = pd.Series(std,index=code_list)
    del factor
    gc.collect()
    # return mean,std


def get_factor_mv(target_day, factor_list, code_list, standard_days=40,n_threads=10):
    code_list = [trans_windcode2int(x) for x in code_list]
    date_list = get_date_range(get_pre_trade_date(target_day, standard_days - 1), target_day)
    # rd_mean = pd.DataFrame(np.nan, index=factor_list, columns=code_list)
    # rd_std = pd.DataFrame(np.nan, index=factor_list, columns=code_list)

    rd_mean = Manager().dict()
    rd_std = Manager().dict()

    from tqdm import tqdm
    bar = tqdm(total=len(factor_list),desc='calculating mv')
    def update(*p):
        if bar.last_print_n<=bar.total:
            bar.update()
        else:
            bar.close()

    pool = Pool(n_threads)
    print(n_threads)
    for file_name in factor_list:
        # print(time.strftime('%Y%m%d %H:%M:%S'), file_name)
        # m,v = get_mv(target_day,file_name,date_list,code_list,rd_mean,rd_std)
        pool.apply_async(get_mv,(target_day,file_name,date_list,code_list,rd_mean,rd_std),callback=update)
    pool.close()
    pool.join()
    rd_mean,rd_std = rd_mean._getvalue(),rd_std._getvalue()
    rd_mean,rd_std = pd.DataFrame(rd_mean).T,pd.DataFrame(rd_std).T

    rd_mean.columns = rd_mean.columns.map(trans_int2windcode)
    rd_std.columns = rd_std.columns.map(trans_int2windcode)
    return rd_mean, rd_std

def daily_update(date, T_plus_1_date):
    """
    用于T日收盘后统计持仓市值计算下一个交易日每只次信号下单金额及每个Bar最大下单数量
    :param date:当前交易日
    :param T_plus_1_date: T+1交易日
    :return:
    """

    bar_list = [1000, 1030, 1100, 1300, 1330, 1400, 1430]
    rolling_window = 5
    model_conf_list = sorted(list(filter(lambda x: x <= str(date) and x.isdigit() and os.path.isdir(f'{non_fix_model_conf_path}/{x}'),
                                         os.listdir(non_fix_model_conf_path))))
    model_update_date = model_conf_list[-1]
    print(f'using factor update in {model_update_date}')
    factor_list = pd.read_pickle(f'{non_fix_model_conf_path}/{model_update_date}/using_fix_list.pkl')
    code_list = get_all_stock_ever_appear(date)#get_code_list(date, restrict_list_path)#get_code_list(date,T_plus_1_date)
        # pd.to_pickle(code_list, code_list_path + '%d.pkl' % date)
    # vol_info = get_recent_vol_info(date, rolling_window, bar_list)
    # pd.to_pickle(vol_info.fillna(0), f'{non_fix_in_path}{T_plus_1_date}/vol_info{date}.pkl')


    # pd.to_pickle(code_list, code_list_path + '%d.pkl' % date)
    print('vol done')
    rd_mean, rd_std = get_factor_mv(date, factor_list, code_list)
    # pd.to_pickle(rd_mean, hyper_param_path + 'mean%d.pkl' % date)
    # pd.to_pickle(rd_std, hyper_param_path + 'std%d.pkl' % date)

    pd.to_pickle(rd_mean, f'{non_fix_in_path}{T_plus_1_date}/mean{date}.pkl')
    pd.to_pickle(rd_std, f'{non_fix_in_path}{T_plus_1_date}/std{date}.pkl')

# from online_conf import non_fix_in_path,non_fix_model_conf_path

# non_fix_path = '/data/group/800319/strategy_local_path_nonfixCondition/'
non_fix_path = '/data/group/800319/strategy_local_path3/'
non_fix_in_path = f'{non_fix_path}daily_input/'
non_fix_model_conf_path = f'{non_fix_path}model_conf/'

if __name__ == '__main__':

    # today = 20220113
    # for today in get_date_range(20220113,20220127):
    from xquant.compute.aimr import AIMR
    import datetime
    date = int(datetime.date.today().strftime('%Y%m%d'))#get_pre_trade_date(int(date),-1)#int(AIMR.getParam())
    # for today in [get_pre_trade_date(get_recent_trade_date(),-1)]:
    for today in [date]:
        pre_date = get_pre_trade_date(today)
        print(pre_date, today)
        # holding_info_update(20210219,20210222)
        send_message(['015614'], 'daily_update start %d' % pre_date)
        daily_update(pre_date, today)
        send_message(['015614'], 'daily_update done')

"""


if not os.path.exists(f'{local_config_path}half_stk/{today}.pkl'):
    send_message(['015664'], '减半股票未提前准备')
target_list = pd.read_pickle(f'{local_config_path}half_stk/{today}.pkl')
calc_halved_vol(today, replace=True, extra_stk_list=[], target_stk=set(target_list))
send_message(['015664'], 'clip done')
"""




###########持仓MV 空


"""
from online_conf import holding_info_path,hyper_param_path
import pandas as pd
import numpy as np
import os,shutil
date = get_pre_trade_date(today)
holding = pd.read_pickle(f'{holding_info_path}{date}.pkl')
holding = pd.Series(holding).drop('cash')
if not os.path.exists(f'{hyper_param_path}mean{date}_backup.pkl'):
    shutil.copy(f'{hyper_param_path}mean{date}.pkl',f'{hyper_param_path}mean{date}_backup.pkl')

if not os.path.exists(f'{hyper_param_path}std{date}_backup.pkl'):
    shutil.copy(f'{hyper_param_path}std{date}.pkl',f'{hyper_param_path}std{date}_backup.pkl')

mean = pd.read_pickle(f'{hyper_param_path}mean{date}.pkl')
std = pd.read_pickle(f'{hyper_param_path}std{date}.pkl')

mean[holding.index] = np.nan
std[holding.index] = np.nan

pd.to_pickle(mean,f'{hyper_param_path}mean{date}.pkl')
pd.to_pickle(std,f'{hyper_param_path}std{date}.pkl')

send_message(['015664'],'Mean Std已换空')
"""