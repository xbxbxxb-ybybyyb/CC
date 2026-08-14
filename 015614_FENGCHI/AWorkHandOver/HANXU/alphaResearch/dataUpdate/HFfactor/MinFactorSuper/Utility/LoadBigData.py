import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from HFfactor.MinFactorSuper.Utility.ExtendNumpy import search_index
from HFfactor.MinFactorSuper.RealTime.UsefulList import \
    MaterialList, ResearchMinuteList
from dataApi.tradeDate import get_date_range, get_pre_trade_date, \
    get_trade_date_interval, get_recent_trade_date
from dataApi.stockList import trans_windcode2int, trans_int2windcode
from xquant.factordata import FactorData
from collections import Counter
import pandas as pd
import numpy as np
import time
import os


def get_minute_data(factor, date_list, code_list=None,
                    address='/data/group/800080/PanelMinDataForZT/stock/', ignore_error=False):
    start_date = date_list[0]
    end_date = date_list[-1]
    row = 242 * len(date_list)

    month_list = sorted(list(set(get_date_range(start_date, end_date, 'M') + [end_date])))
    short_month_list = sorted(list({x // 100 for x in month_list}))
    month_dates = Counter([x // 100 for x in date_list])
    month_start = get_recent_trade_date(short_month_list[0] * 100)
    month_end = get_recent_trade_date(short_month_list[-1] * 100)

    start_keep = get_trade_date_interval(start_date, month_start) * 242
    end_keep = (get_trade_date_interval(end_date, month_end) + 1) * 242

    df = pd.read_pickle('%s/%s/%s_%s.pkl' % (address, factor, short_month_list[-1], factor))
    df = df.iloc[:end_keep] if len(month_list) > 1 else df.iloc[start_keep: end_keep]
    use_code_list = [trans_int2windcode(x) for x in code_list] if code_list else df.columns.to_list()
    col = len(use_code_list)

    arr = np.empty((row, col), dtype=np.float64)
    r_num = row
    pre_r_num = r_num - month_dates[short_month_list[-1]] * 242
    error_len = r_num - pre_r_num - len(df)
    if error_len != 0:
        if ignore_error:
            print(f'ERROR: {factor}_{short_month_list[-1]} minute data incomplete, lack {error_len / 242} days.')
            df = df.head(r_num - pre_r_num)
            r_num = pre_r_num + len(df)
        else:
            raise ValueError(f'{factor}_{short_month_list[-1]} minute data incomplete, lack {error_len / 242} days.')

    if code_list:
        code_index = search_index(use_code_list, df.columns.to_list())
        used_codes = code_index.data[~code_index.mask]
        unused_codes = sorted(list(set(range(col)) - set(used_codes)))
        arr[pre_r_num: r_num, code_index.data[~code_index.mask]] = df.values[:, ~code_index.mask]
        arr[pre_r_num: r_num, unused_codes] = np.nan
    else:
        arr[pre_r_num: r_num] = df.values

    for j in reversed(range(len(month_list) - 1)):
        df = pd.read_pickle('%s/%s/%s_%s.pkl' % (address, factor, short_month_list[j], factor))
        if not j:
            df = df.iloc[start_keep:]
        r_num = pre_r_num
        pre_r_num = r_num - month_dates[short_month_list[j]] * 242

        error_len = r_num - pre_r_num - len(df)
        if error_len != 0:
            if ignore_error:
                print(f'ERROR: {factor}_{short_month_list[j]} minute data incomplete, lack {error_len / 242} days.')
                df = df.head(r_num - pre_r_num)
                r_num = pre_r_num + len(df)
            else:
                raise ValueError(f'{factor}_{short_month_list[j]} minute data incomplete, lack {error_len / 242} days.')

        code_index = search_index(use_code_list, df.columns.to_list())
        used_codes = code_index.data[~code_index.mask]
        unused_codes = sorted(list(set(range(col)) - set(used_codes)))
        arr[pre_r_num: r_num, used_codes] = df.values[:, ~code_index.mask]
        arr[pre_r_num: r_num, unused_codes] = np.nan
    arr = arr.reshape(-1, 242, col)
    if code_list:
        return arr
    else:
        use_code_list = [trans_windcode2int(x) for x in use_code_list]
        return arr, use_code_list


def get_daily_data(factor, date_list, code_list=None, lag=True, ffill=True,
                   address='/data/group/800080/Apollo/AlphaDataBase/', ignore_error=False):
    start_date = get_pre_trade_date(date_list[0]) if lag else date_list[0]
    end_date = date_list[-1]
    row = len(get_date_range(start_date, end_date))
    df = pd.read_pickle(f'{address}/{factor}.pkl')
    if ffill:
        df = df.ffill()
    df = df.loc[str(start_date): str(end_date)]
    error_len = row - len(df)
    if error_len != 0:
        if ignore_error:
            print(f'ERROR: {factor}_{start_date}:{end_date} daily data incomplete, lack {error_len} days.')
            _date_list = [str(x) for x in get_date_range(start_date, end_date)]
            df = df[~ df.index.duplicated(keep='last')].reindex(_date_list)
        else:
            raise ValueError(f'{factor}_{start_date}:{end_date} daily data incomplete, lack {error_len} days.')
    if code_list:
        use_code_list = [trans_int2windcode(x) for x in code_list]
        col = len(use_code_list)
        arr = np.empty((row, col), dtype=np.float64)
        code_index = search_index(use_code_list, df.columns.to_list())
        used_codes = code_index.data[~code_index.mask]
        unused_codes = sorted(list(set(range(col)) - set(used_codes)))
        arr[:, used_codes] = df.values[:, ~code_index.mask]
        arr[:, unused_codes] = np.nan
        if lag:
            return arr[:-1, None, :], arr[[-1]]
        else:
            return arr[:, None, :]
    else:
        arr = df.values
        use_code_list = [trans_windcode2int(x) for x in df.columns]
        if lag:
            return arr[:-1, None, :], arr[[-1]], use_code_list
        else:
            return arr[:, None, :], use_code_list


def get_con_data(factor, date_list, code_list=None, pred_year=-2, lag=True, ffill=True, ignore_error=False):
    start_date = get_pre_trade_date(date_list[0]) if lag else date_list[0]
    end_date = date_list[-1]
    row = len(get_date_range(start_date, end_date))
    month_list = sorted(list(set(get_date_range(20131101, end_date, 'M') + [end_date])))
    df_dic = {}
    fd = FactorData()
    for j in range(len(month_list) - 1):
        start = get_pre_trade_date(month_list[j], -1)
        end = month_list[j + 1]
        df_dic[end] = fd.get_factor_value('Basic_factor',
                                          mddate=[str(x) for x in get_date_range(start, end)],
                                          factor_names=[factor])
    del fd
    df = pd.concat([df_dic[x] for x in month_list[1:]])
    if pred_year > -2:
        df = df.iloc[pred_year + 1:: 4]
    df = df[factor].unstack()
    df.index = df.index.map(int)
    df.columns = df.columns.map(int)
    if ffill:
        df = df.ffill()

    df = df.loc[str(start_date): str(end_date)]
    error_len = row - len(df)
    if error_len != 0:
        if ignore_error:
            print(f'ERROR: {factor}_{start_date}:{end_date} daily data incomplete, lack {error_len} days.')
            _date_list = [str(x) for x in get_date_range(start_date, end_date)]
            df = df[~ df.index.duplicated(keep='last')].reindex(_date_list)
        else:
            raise ValueError(f'{factor}_{start_date}:{end_date} daily data incomplete, lack {error_len} days.')
    if code_list:
        use_code_list = code_list.copy()
        col = len(use_code_list)
        arr = np.empty((row, col), dtype=np.float64)
        code_index = search_index(use_code_list, df.columns.to_list())
        used_codes = code_index.data[~code_index.mask]
        unused_codes = sorted(list(set(range(col)) - set(used_codes)))
        arr[:, used_codes] = df.values[:, ~code_index.mask]
        arr[:, unused_codes] = np.nan
        if lag:
            return arr[:-1, None, :], arr[[-1]]
        else:
            return arr[:, None, :]
    else:
        arr = df.values
        use_code_list = df.columns.to_list()
        if lag:
            return arr[:-1, None, :], arr[[-1]], use_code_list
        else:
            return arr[:, None, :], use_code_list


def get_all_stock(end_date, address='/arch1/group/800442/800319/MinFactorSuper/'):
    fd = FactorData()
    code_list = fd.get_factor_value('WIND_AShareDescription',
                                    factors=['S_INFO_WINDCODE', 'S_INFO_LISTDATE', 'S_INFO_DELISTDATE'])
    code_list = code_list[code_list['S_INFO_LISTDATE'].notnull()]
    code_list = code_list[code_list['S_INFO_WINDCODE'].map(lambda x: x[0] in ['0', '3', '6'])]
    code_list['S_INFO_DELISTDATE'] = code_list['S_INFO_DELISTDATE'].map(float)
    code_list = code_list[~ (code_list['S_INFO_DELISTDATE'] < 20140101)]
    code_list = code_list.sort_values(
        ['S_INFO_LISTDATE', 'S_INFO_WINDCODE']).drop_duplicates(['S_INFO_WINDCODE'], keep='first')
    code_list = code_list.set_index('S_INFO_WINDCODE')['S_INFO_LISTDATE'].map(int)
    code_list1 = fd.get_factor_value('WIND_AShareST', factors=['S_INFO_WINDCODE', 'ENTRY_DT'])
    code_list1 = code_list1.drop_duplicates(['S_INFO_WINDCODE'], keep='first')
    code_list1 = code_list1.set_index('S_INFO_WINDCODE').reindex(
        code_list.index)['ENTRY_DT'].fillna('99999999').map(int)
    code_list = np.fmin(code_list, code_list1).reset_index()
    code_list = code_list[code_list['S_INFO_LISTDATE'] <= end_date]
    code_list = code_list.sort_values(['S_INFO_LISTDATE', 'S_INFO_WINDCODE'])
    code_list = code_list['S_INFO_WINDCODE'].map(trans_windcode2int).to_list()
    pd.to_pickle(code_list,
                 f"{address}/MaterialUpdateLog/code_list{end_date}_{time.strftime('%Y%m%d%H')}.pkl")
    return code_list


def load_stock_list(end_date, address='/arch1/group/800442/800319/MinFactorSuper/'):
    cll = sorted(os.listdir(f'{address}/MaterialUpdateLog/'))
    cll = [x for x in cll if int(x.split('_')[1][-8:]) == end_date]
    code_list = pd.read_pickle(f'{address}/MaterialUpdateLog/{cll[-1]}') if cll else get_all_stock(end_date)
    return code_list


def load_material(name, start_date, end_date, reduce=False, address='/arch1/group/800442/800319/MinFactorSuper/'):
    suffix = 'Reduce' if reduce else ''
    middle_name = 'Material' if name in MaterialList else 'Label'
    middle_len = 1 if 'stock_pool' in name else (48 if reduce else 242)
    unit_size = 1 if ('stock_pool' in name) or (name == 'limit_status') else 4
    dtype = 'bool' if ('stock_pool' in name) or (name == 'limit_status') else 'float32'
    date_list = get_date_range(start_date, end_date)
    start_date, end_date = date_list[0], date_list[-1]
    date_offset = get_trade_date_interval(start_date, 20140101)
    code_list = load_stock_list(end_date, address)
    code_list_rank = np.argsort(code_list)
    offset = 128 + date_offset * 6000 * middle_len * unit_size
    shape = (len(date_list), middle_len, 6000)
    arr = np.empty((len(date_list), middle_len, len(code_list)), dtype=dtype)
    fp = np.memmap(f'{address}/{suffix}{middle_name}/{name}.npy', mode='r', dtype=dtype, offset=offset, shape=shape)
    arr[:] = fp[:, :, code_list_rank]
    del fp
    return arr


def make_idx(model_times=232, stock_pool='stock_pool', fold='FactorData',
             address='/arch1/group/800442/800319/MinFactorSuper/'):
    if not os.path.exists(f'{address}/{fold}/Label/'):
        os.makedirs(f'{address}/{fold}/Label/')
    stock_pool = np.load(f'{address}/Label/{stock_pool}.npy')
    date_num = stock_pool.shape[0]
    start_date = 20140801
    end_date = get_pre_trade_date(20140101, -date_num)
    date_list = get_date_range(start_date, end_date)
    date_num = len(date_list)
    code_list = load_stock_list(end_date, address)
    rank_code_list = np.argsort(code_list)
    stock_pool = stock_pool[-date_num:, 0, rank_code_list]
    idx_date = np.asarray(date_list, dtype='int32')[:, None].repeat(len(code_list), axis=1)[stock_pool]
    idx_code = np.asarray(code_list, dtype='int32')[None, rank_code_list].repeat(len(date_list), axis=0)[stock_pool]
    np.save(f'{address}/{fold}/Label/idx_date.npy', np.ascontiguousarray(idx_date))
    np.save(f'{address}/{fold}/Label/idx_code.npy', np.ascontiguousarray(idx_code))
    if model_times == 13:
        idx_time = [1030, 1100, 1300, 1330, 1400, 1430, 1000, 1030, 1100, 1300, 1330, 1400, 1430]
    elif model_times == 47:
        idx_time = ResearchMinuteList[6:-1:5]
    elif model_times == 232:
        idx_time = ResearchMinuteList[5:-5]
    else:
        raise ValueError("idx_time must be 13, 47 or 232.")
    idx_time = np.ascontiguousarray(idx_time, dtype='int32')
    np.save(f'{address}/{fold}/Label/idx_time.npy', idx_time)


def make_label(stock_pool='stock_pool', fold='FactorData',
               address='/arch1/group/800442/800319/MinFactorSuper/'):
    idx_date = np.load(f'{address}/{fold}/Label/idx_date.npy')
    idx_time = np.load(f'{address}/{fold}/Label/idx_time.npy')
    idx_time = [231 if x not in ResearchMinuteList[5: -5] else
                ResearchMinuteList[5: -5].index(x) for x in idx_time]
    idx_time_diff = np.arange(len(idx_time) - 1)[np.diff(np.array(idx_time)) < 0]
    if idx_time_diff.shape[0]:
        pre_idx_time = idx_time[: idx_time_diff[0] + 1]
        idx_time = idx_time[idx_time_diff[0] + 1:]
        start_date = get_pre_trade_date(idx_date[0])
    else:
        start_date = idx_date[0]
    end_date = get_pre_trade_date(idx_date[-1], 2)
    stock_pool = load_material(stock_pool, start_date, end_date, address=address)
    limit_status = load_material('limit_status', start_date, end_date, address=address)[:, 5: -5]
    if idx_time_diff.shape[0]:
        limit_status = np.concatenate([limit_status[:-1, pre_idx_time], limit_status[1:, idx_time]], axis=1)
        limit_status = limit_status.transpose(0, 2, 1)[stock_pool[1:, 0]]
    else:
        limit_status = limit_status[:, idx_time].transpose(0, 2, 1)[stock_pool[:, 0]]
    np.save(f'{address}/{fold}/Label/nolimit.npy', np.ascontiguousarray(limit_status))
    future = load_material('future', start_date, end_date, address=address)[:, 5: -5]
    if idx_time_diff.shape[0]:
        future = np.concatenate([future[:-1, pre_idx_time], future[1:, idx_time]], axis=1)
        future = future.transpose(0, 2, 1)[stock_pool[1:, 0]]
    else:
        future = future[:, idx_time].transpose(0, 2, 1)[stock_pool[:, 0]]
    np.save(f'{address}/{fold}/Label/future.npy', np.ascontiguousarray(future))
