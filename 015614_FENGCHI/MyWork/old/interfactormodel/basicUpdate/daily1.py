import os
import pandas as pd
import numpy as np
import datetime as dt
from itertools import chain
from functools import reduce
from xquant.factordata import FactorData
from dataApi.dividend import getEXRightDividend
from dataApi.tradeDate import get_pre_trade_date, _check_input_date, get_date_range, get_recent_trade_date, trans_datetime2int
from dataApi.stockList import _get_stock_list, _update_bench_exdiv_weight, _get_ind_con, trans_windcode2int, trans_int2windcode, _update_log
fd = FactorData()

daily_data_list = ['pre_close', 'open', 'high', 'low', 'close', 'pre_close_badj', 'open_badj', 'high_badj', 'low_badj',
                   'close_badj', 're_ipo_chg_badj', 'rel_ipo_pct_chg_badj', 'vwap', 'pct_chg', 'turn', 'free_turn',
                   'volume', 'amt', 'dealnum', 'swing', 're_ipo_chg', 'rel_ipo_pct_chg', 'adjfactor', 'total_shares',
                   'free_float_shares', 'float_a_shares', 'share_totala', 'ev', 'mkt_cap_ard', 'a_mkt_cap', 'pe_ttm',
                   'pe_lyr', 's_val_pb_new', 'ps_ttm', 'ps_lyr', 'pcf_ocf_ttm', 'pcf_ncf_ttm', 'pcf_ocflyr', 'pcf_ncflyr',
                   'net_assets_today', 's_pq_high_52w_', 's_pq_low_52w_', 's_pq_adjhigh_52w', 's_pq_adjlow_52w',
                   'net_profit_parent_comp_ttm', 'net_profit_parent_comp_lyr', 'net_cash_flows_oper_act_ttm',
                   'net_cash_flows_oper_act_lyr', 'oper_rev_ttm', 'oper_rev_lyr', 'net_incr_cash_cash_equ_ttm',
                   'net_incr_cash_cash_equ_lyr', 'lowest_highest_status', 'ev1', 'ev2', 'ocfps_ttm', 'orps_ttm', 'cfps_ttm',
                   'dyr_12', 'beta_100w', 'beta_24m', 'beta_60m', 's_price_div_dps']

#EXCEPT: cfc3cs_cgb, cfc3cs_cgpb, eps_deviation5, eps_deviation25, eps_deviation75, ni_deviation5, ni_deviation25
#ni_deviation75, eps_stdev5, eps_stdev25, eps_stdev75, ni_stdev5, ni_stdev25, ni_stdev75, csd_pe_deviation5,
#csd_pe_deviation25, csd_pe_deviation75, csd_pb_deviation5, csd_pb_deviation25, csd_pb_deviation75, degree,
#stock_diversity, consensus_confidence5, consensus_confidence10, consensus_confidence15, consensus_confidence25,
#consensus_confidence75,

con_data_list = [
    'cfs_target_price', 'cfs_score', 'cfc2s_c2', 'cfc2s_c13', 'cfc2s_c9', 'cfc3s_cgb', 'cfc3s_cgpb', 'cfc3s_cgg',
    'cfc3s_cgpeg', 'cfs_c1', 'cfs_c3', 'cfs_c4', 'cfs_c5', 'cfs_c6', 'cfs_c7', 'cfs_c80', 'cfs_c81',
    'cfs_c82', 'cfs_c83', 'cfs_c84', 'cfs_c12', 'cfs_cb', 'cfs_cpb', 'rating_up_number7', 'rating_up_number30',
    'rating_up_number90', 'rating_down_number7', 'rating_down_number30', 'rating_down_number90', 'report_number7',
    'report_number30', 'report_number90', 'author_number7', 'author_number30', 'author_number90', 'organ_number7',
    'organ_number30', 'organ_number90', 'buy_number7', 'buy_number30', 'buy_number90', 'overweight_number7',
    'overweight_number30', 'overweight_number90', 'neutral_number7', 'neutral_number30', 'neutral_number90',
    'underweight_number7', 'underweight_number30', 'underweight_number90', 'sell_number7', 'sell_number30',
    'sell_number90', 'csd_forward_pe_deviation5', 'csd_forward_pe_deviation25', 'csd_forward_pe_deviation75',
    'csd_forward_pb_deviation5', 'csd_forward_pb_deviation25', 'csd_forward_pb_deviation75', 'relative_report_number10',
    'relative_report_number25', 'relative_report_number75', 'organ_number10', 'organ_number25', 'organ_number75',
    'tcap', 'up_number7', 'up_number30', 'up_number90', 'down_number7', 'down_number30', 'down_number90',
    'eps_deviation5', 'eps_deviation25', 'eps_deviation75', 'ni_deviation5', 'ni_deviation25', 'ni_deviation75',
    'eps_stdev5', 'eps_stdev25', 'eps_stdev75', 'ni_stdev5', 'ni_stdev25', 'ni_stdev75', 'csd_pe_deviation5',
    'csd_pe_deviation25', 'csd_pe_deviation75', 'csd_pb_deviation5', 'csd_pb_deviation25', 'csd_pb_deviation75',
    'degree', 'stock_diversity', 'consensus_confidence5', 'consensus_confidence10', 'consensus_confidence15',
    'consensus_confidence25', 'consensus_confidence75', 'optimism_confidence5', 'optimism_confidence10',
    'optimism_confidence15', 'optimism_confidence25', 'optimism_confidence75', 'pessimism_confidence5',
    'pessimism_confidence10', 'pessimism_confidence15', 'pessimism_confidence25', 'pessimism_confidence75',
]

def _update_check(new, factor_type, factor, recent_trade_date):

    if (new.iloc[-1].isnull().all()) | (int(new.index[-1]) != recent_trade_date):
        _update_log('ERROR', factor_type, factor, 'update', 'New data has not arrived')
        raise Exception("New data has not arrived")

def _error_check(new, old, factor_type, factor, accept_error=0., file='/data/group/800319/junkData/updateLog.txt'):

    _new = new.iloc[0].dropna().sort_index()
    _old = old.iloc[-1].dropna().sort_index()
    if _new.name != _old.name:
        _update_log('ERROR', factor_type, factor, 'update', 'Time confusion')
        return 2
    else:
        error_ratio = abs(len(_new) - len(_old)) / len(_new)
        _old = _old.reindex(_new.index)
        try:
            close_num = np.isclose(_old, _new).sum()
        except TypeError:
            close_num = (_old == _new).sum()
        error_ratio += abs(len(_new) - close_num) / len(_new)
        if error_ratio > accept_error:
            _update_log('ERROR', factor_type, factor, 'update',
                        'Error ratio %.4f%% exceeds accept level %.4f%%' % (error_ratio * 100, accept_error * 100),
                        file=file)
            return 1
        else:
            _update_log('SUCCEED', factor_type, factor, 'update', file=file)
            return 0

def _store_daily_data(item='all', address='/data/group/800319/junkData/daily'):

    date = get_date_range(20100101)
    _date = _check_input_date(date)
    stock_list = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list')
    if item == 'all':
        item_list = daily_data_list
    else:
        item_list = [item]
    for item in item_list:
        df = fd.get_factor_value('Basic_factor', mddate=_date, factor_names=[item]).iloc[:, 0].unstack()
        df.index = df.index.map(int)
        df.columns = df.columns.map(trans_windcode2int)
        df = df.reindex_like(stock_list)
        df = df.convert_objects()
        df.to_hdf('%s/%s.h5' % (address, item), item, format='t')
        _update_log('SUCCEED', 'daily', item, 'store', 'time range %s~%s' % (date[0], date[-1]))

def _store_con_data(item='all', address='/data/group/800319/junkData/daily'):

    date = get_date_range(20100101)
    _date = _check_input_date(date)
    parts = round(len(_date) / 300)
    stock_list = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list')
    if item == 'all':
        item_list = con_data_list
    else:
        item_list = [item]
    for item in item_list:
        df = pd.concat([fd.get_factor_value('Basic_factor', mddate=_date[x::parts], factor_names=[item])
                        for x in range(parts)]).sort_index()
        df = df.drop('stock_type', axis=1) if 'stock_type' in df.columns else df
        df = df.reset_index().rename(columns={'mddate': 'date', 'stock': 'code'})
        df['date'] = df['date'].map(trans_datetime2int)
        df['code'] = df['code'].map(trans_windcode2int)
        if 'rpt_date' in df.columns:
            df[1::4].pivot('date', 'code', item).reindex_like(stock_list).to_hdf(
                '%s/%s_f0.h5' % (address, item), item + '_f0', format='t')
            df[2::4].pivot('date', 'code', item).reindex_like(stock_list).to_hdf(
                '%s/%s_f1.h5' % (address, item), item + '_f1', format='t')
            df[3::4].pivot('date', 'code', item).reindex_like(stock_list).to_hdf(
                '%s/%s_f2.h5' % (address, item), item + '_f2', format='t')
        else:
            df.pivot('date', 'code', item).reindex_like(stock_list).to_hdf(
                '%s/%s.h5' % (address, item), item, format='t')
        _update_log('SUCCEED', 'daily', item, 'store', 'time range %s~%s' % (date[0], date[-1]))

def update_stock_list(address='/data/group/800319/junkData/daily'):

    old = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list')
    date = get_date_range(old.index[-1])
    new = _get_stock_list(date)
    new['true'] = True
    new = new.pivot('date', 'code', 'true').fillna(False)
    _update_check(new, 'daily', 'stock_list', date[-1])

    check = _error_check(new, old, 'daily', 'stock_list', accept_error=0.05)
    df = pd.concat([old.iloc[:-1], new]) == True
    if check == 2:
        df = df.drop_duplicates()
    df = df.convert_objects()
    df.to_hdf('%s/stock_list.h5' % address, 'stock_list', format='t')

def update_ind_con(address='/data/group/800319/junkData/daily'):

    for ind_type in ['CITICS', 'SW']:
        for level in [1, 2, 3]:
            old = pd.read_hdf('%s/%s%s.h5' % (address, ind_type, level), '%s%s' % (ind_type, level))
            date = get_date_range(old.index[-1])
            code = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list', start=-1).columns.to_list()
            new = _get_ind_con(date, code, ind_type=ind_type, level=level).pivot('date', 'code', 'ind')
            _update_check(new, 'daily', '%s%s' % (ind_type, level), date[-1])
            check = _error_check(new, old, 'daily', '%s%s' % (ind_type, level), accept_error=0.03)
            df = pd.concat([old.iloc[:-1], new])
            if check == 2:
                df = df.drop_duplicates()
            df = df.convert_objects()
            df.to_hdf('%s/%s%s.h5' % (address, ind_type, level), '%s%s' % (ind_type, level), format='t')

def update_daily_data(item='all', address='/data/group/800319/junkData/daily'):

    if item == 'all':
        item_list = daily_data_list
    else:
        item_list = [item]
    for item in item_list:
        old = pd.read_hdf('%s/%s.h5' % (address, item), item)
        date = get_date_range(old.index[-1])
        _date = _check_input_date(date)
        code = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list', start=-1).columns.to_list()
        code = [trans_int2windcode(x) for x in code]
        new = fd.get_factor_value('Basic_factor', mddate=_date, stock=code, factor_names=[item]).iloc[:, 0].unstack()
        new.index = new.index.map(int)
        new.columns = new.columns.map(trans_windcode2int)
        _update_check(new, 'daily', item, int(_date[-1]))
        check = _error_check(new, old, 'daily', item)
        df = pd.concat([old.iloc[:-1], new])
        if check == 2:
            df = df.drop_duplicates()
        df = df.convert_objects()
        df.to_hdf('%s/%s.h5' % (address, item), item, format='t')

def update_con_data(item='all', address='/data/group/800319/junkData/daily'):

    if item == 'all':
        item_list = con_data_list
    else:
        item_list = [item]
    for item in item_list[-1:]:
        print(item)
        if item + '.h5' in os.listdir(address):
            old = pd.read_hdf('%s/%s.h5' % (address, item), item)
            date = get_date_range(old.index[-1])
            _date = _check_input_date(date)
            code = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list', start=-1).columns.to_list()
            code = [trans_int2windcode(x) for x in code]
            new = fd.get_factor_value('Basic_factor', mddate=_date, stock=code, factor_names=[item]
                                      ).loc[:, item].unstack()
            new.index = new.index.map(int)
            new.columns = new.columns.map(trans_windcode2int)
            _update_check(new, 'daily', item, int(_date[-1]))
            check = _error_check(new, old, 'daily', item)
            df = pd.concat([old.iloc[:-1], new])
            if check == 2:
                df = df.drop_duplicates()
            df = df.convert_objects()
            df.to_hdf('%s/%s.h5' % (address, item), item, format='t')

        else:
            for f in range(3):
                old = pd.read_hdf('%s/%s_f%s.h5' % (address, item, f), '%s_f%s' % (item, f))
                date = get_date_range(old.index[-1])
                _date = _check_input_date(date)
                code = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list', start=-1).columns.to_list()
                code = [trans_int2windcode(x) for x in code]
                new = fd.get_factor_value('Basic_factor', mddate=_date, stock=code, factor_names=[item]
                                          ).iloc[f+1::4].loc[:, item].unstack()
                new.index = new.index.map(int)
                new.columns = new.columns.map(trans_windcode2int)
                _update_check(new, 'daily', item, int(_date[-1]))
                check = _error_check(new, old, 'daily', item)
                df = pd.concat([old.iloc[:-1], new])
                if check == 2:
                    df = df.drop_duplicates()
                df = df.convert_objects()
                df.to_hdf('%s/%s_f%s.h5' % (address, item, f), '%s_f%s' % (item, f), format='t')

def update_pause(address='/data/group/800319/junkData/daily'):

    recent_trade_date = get_recent_trade_date()
    amt = pd.read_hdf('%s/amt.h5' % address, 'amt')
    _update_check(amt, 'daily', 'amt', recent_trade_date)
    pause = amt.fillna(0) <= 1
    pause = pause.convert_objects()
    pause.to_hdf('%s/pause.h5' % address, 'pause', format='t')
    _update_log('SUCCEED', 'daily', 'pause', 'update')

def update_live_days(address='/data/group/800319/junkData/daily'):

    live_days = pd.read_hdf('%s/live_days.h5' % address, 'live_days')
    date = get_date_range(live_days.index[-1])
    amt = pd.read_hdf('%s/amt.h5' % address, 'amt').loc[date]
    _update_check(amt, 'daily', 'amt', date[-1])
    amt = amt > 1
    df = pd.concat([live_days.loc[[get_pre_trade_date(date[0])]], amt]).fillna(0).cumsum()
    df = pd.concat([live_days.loc[:get_pre_trade_date(date[0], 2)], df]).fillna(0)
    df = df.convert_objects()
    df.to_hdf('%s/live_days.h5' % address, 'live_days', format='t')
    _update_log('SUCCEED', 'daily', 'live_days', 'update')

def update_price_get_limit(address='/data/group/800319/junkData/daily'):

    date = get_date_range(pd.read_hdf('%s/limit_up.h5' % address, 'limit_up', start=-1).index[0])
    _date = _check_input_date(date)

    code = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list', start=-1).columns.to_list()
    code = [trans_int2windcode(x) for x in code]
    maxupordown = fd.get_factor_value('Basic_factor', mddate=_date, stock=code, factor_names=['maxupordown'])
    maxupordown = maxupordown.iloc[:, 0].unstack()
    maxupordown.index = maxupordown.index.map(int)
    maxupordown.columns = maxupordown.columns.map(trans_windcode2int)
    _update_check(maxupordown, 'daily', 'maxupordown', int(_date[-1]))

    new = maxupordown > 0.5
    old = pd.read_hdf('%s/limit_up.h5' % address, 'limit_up')
    check = _error_check(new, old, 'daily', 'limit_up', accept_error=0.002)
    df = pd.concat([old.iloc[:-1], new])
    if check == 2:
        df = df.drop_duplicates()
    df = (df > 0.5).convert_objects()
    df.to_hdf('%s/limit_up.h5' % address, 'limit_up', format='t')

    new = maxupordown < -0.5
    old = pd.read_hdf('%s/limit_down.h5' % address, 'limit_down')
    check = _error_check(new, old, 'daily', 'limit_down', accept_error=0.002)
    df = pd.concat([old.iloc[:-1], new])
    if check == 2:
        df = df.drop_duplicates()
    df = (df > 0.5).convert_objects()
    df.to_hdf('%s/limit_down.h5' % address, 'limit_down', format='t')

def update_bench_exdiv_weight(address='/data/group/800319/junkData/daily'):

    for bench in ['HS300', 'ZZ500', 'SZ50']:
        old = pd.read_hdf('%s/%s_exdiv_weight.h5' % (address, bench), '%s_exdiv_weight' % bench)
        date = get_date_range(old.index[-1])
        new = _update_bench_exdiv_weight(date, bench).pivot('date', 'code', 'weight')
        _update_check(new, 'daily', bench, date[-1])
        check = _error_check(new, old, 'daily', '%s_exdiv_weight' % bench)
        df = pd.concat([old.iloc[:-1], new])
        if check == 2:
            df = df.drop_duplicates()
        df = df.convert_objects()
        df.to_hdf('%s/%s_exdiv_weight.h5' % (address, bench), '%s_exdiv_weight' % bench, format='t')

def update_dividend(address='/data/group/800319/junkData/daily'):

    getEXRightDividend().convert_objects().to_hdf('%s/ex_right_dividend.h5' % address, 'ex_right_dividend', format='t')
    _update_log('SUCCEED', 'daily', 'ex_right_dividend', 'update')

def update_common_stock_list(address='/data/group/800319/junkData/daily'):

    bench_dic = {'000300.SH': 'HS300', '000905.SH': 'ZZ500', '000852.SH': 'ZZ1000', '000016.SH': 'SZ50'}
    df = fd.get_factor_value(
        'WIND_AIndexMembers',
        factors=['S_CON_INDATE', 'S_CON_OUTDATE', 'S_INFO_WINDCODE', 'S_CON_WINDCODE'],
        S_INFO_WINDCODE=['000300.SH', '000905.SH', '000852.SH', '000016.SH'],
    )
    df.columns = ['dateIn', 'dateOut', 'bench', 'code']
    df = df[df['code'] != 'T00018.SH']
    df['code'] = df['code'].map(trans_windcode2int)
    df['bench'] = df['bench'].map(bench_dic)
    df.loc[df['dateOut'].notnull(), 'dateOut'] = df.loc[df['dateOut'].notnull(), 'dateOut'].map(
        lambda x: (dt.datetime.strptime(x, '%Y%m%d') + dt.timedelta(1)).strftime('%Y%m%d'))
    df = df[(~df[['dateIn', 'code', 'bench']].duplicated(keep=False)) | (df['dateOut'].notnull())]

    df_dic = {}
    for bench in bench_dic.values():
        df1 = df.loc[df['bench'] == bench, ['dateIn', 'dateOut', 'code']]
        df1['key'] = 1
        df1 = df1.pivot('dateIn', 'code', 'key').sub(df1.dropna().pivot('dateOut', 'code', 'key') * 0, fill_value=0)
        df1.index = df1.index.map(int)
        date = sorted(list(set(get_date_range(df1.index[0])) | set(df1.index)))
        df1 = df1.reindex(date).ffill().reindex(get_date_range(20100101)) > 0.5
        df1.to_hdf('%s/common_stock_list.h5' % address, bench, format='t')
        if bench != 'SZ50':
            df_dic[bench] = df1

    columns = sorted(list(set(chain(*[df_dic[bench].columns.to_list() for bench in df_dic.keys()]))))
    index = sorted(list(set(chain(*[df_dic[bench].index.to_list() for bench in df_dic.keys()]))))
    df = reduce(lambda x, y: x | y, [df_dic[z].reindex(index=index, columns=columns) > 0.5 for z in df_dic.keys()])
    df.to_hdf('%s/common_stock_list.h5' % address, 'common_stock_list', format='t')
    _update_log('SUCCEED', 'daily', 'common_stock_list', 'update')


if __name__ == '__main__':

    address = '/data/group/800319/junkData/daily'

    update_stock_list(address='/data/group/800319/junkData/daily')

    update_ind_con(address='/data/group/800319/junkData/daily')

    for i in range(len(daily_data_list)):
        try:
            update_daily_data(daily_data_list[i], address='/data/group/800319/junkData/daily')
        except Exception:
            pass

    update_pause(address='/data/group/800319/junkData/daily')

    update_live_days(address='/data/group/800319/junkData/daily')

    update_price_get_limit(address='/data/group/800319/junkData/daily')

    update_dividend(address='/data/group/800319/junkData/daily')

    update_bench_exdiv_weight(address='/data/group/800319/junkData/daily')

    update_common_stock_list(address='/data/group/800319/junkData/daily')

    os.listdir('/data/user/015518/quant_data/qualified_factor/x_day_lib/20181231')
    import os
    import re
    import pandas as pd
    date = 20140102
    temp_path = '/data/user/015518/quant_data/qualified_factor/x_day_lib/20181231/mddate=' + str(date)
    file_name = os.listdir(temp_path)[0]
    aaa = pd.read_parquet('%s/%s' % (temp_path, file_name), columns=ccc)
    ccc = aaa.columns.to_list()
    ccc = [x for x in ccc if re.match('^Fix1[0134][03]0_', x) is None]
    pd.Series(bbb).to_excel('/data/user/015836/factor_list.xlsx')

    df = fd.get_factor_value('Wind_vip', None, ['20200610'], ['trade_status'])