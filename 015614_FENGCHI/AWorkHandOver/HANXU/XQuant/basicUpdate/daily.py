import sys
sys.path.append('/data/group/800442/800319/')

import pandas as pd
import numpy as np
import datetime as dt
from itertools import chain
from functools import reduce
from xquant.factordata import FactorData
from dataApi.dividend import getEXRightDividend
from dataApi.tradeDate import get_pre_trade_date, _check_input_date, get_date_range, get_recent_trade_date
from dataApi.stockList import _get_stock_list, _update_bench_exdiv_weight, _get_ind_con, trans_windcode2int, \
    trans_int2windcode, _update_log, _store_ST, _store_limit_range
fd = FactorData()

daily_data_list = [
    'open', 'high', 'low', 'close', 'adjfactor', 'pre_close', 'pre_close_badj', 'open_badj', 'high_badj',
    'low_badj', 'close_badj', 're_ipo_chg_badj', 'rel_ipo_pct_chg_badj', 'vwap', 'pct_chg', 'turn', 'free_turn',
    'volume', 'amt', 'dealnum', 'swing', 're_ipo_chg', 'rel_ipo_pct_chg', 'total_shares',
    'free_float_shares', 'float_a_shares', 'share_totala', 'ev', 'mkt_cap_ard', 'a_mkt_cap', 'pe_ttm',
    'pe_lyr', 's_val_pb_new', 'ps_ttm', 'ps_lyr', 'pcf_ocf_ttm', 'pcf_ncf_ttm', 'pcf_ocflyr', 'pcf_ncflyr',
    'net_assets_today', 's_pq_high_52w_', 's_pq_low_52w_', 's_pq_adjhigh_52w', 's_pq_adjlow_52w',
    'net_profit_parent_comp_ttm', 'net_profit_parent_comp_lyr', 'net_cash_flows_oper_act_ttm',
    'net_cash_flows_oper_act_lyr', 'oper_rev_ttm', 'oper_rev_lyr', 'net_incr_cash_cash_equ_ttm',
    'net_incr_cash_cash_equ_lyr', 'lowest_highest_status', 'ev1', 'ev2', 'ocfps_ttm', 'orps_ttm', 'cfps_ttm',
    'dyr_12', 'beta_100w', 'beta_24m', 'beta_60m', 's_price_div_dps', 'fmarketval']

money_flow_data_list = [
    'buy_value_exlarge_order', 'sell_value_exlarge_order', 'buy_value_large_order', 'sell_value_large_order',
    'buy_value_med_order', 'sell_value_med_order', 'buy_value_small_order', 'sell_value_small_order',
    'buy_volume_exlarge_order', 'sell_volume_exlarge_order', 'buy_volume_large_order', 'sell_volume_large_order',
    'buy_volume_med_order', 'sell_volume_med_order', 'buy_volume_small_order', 'sell_volume_small_order',
    'trades_count', 'buy_trades_exlarge_order', 'sell_trades_exlarge_order', 'buy_trades_large_order',
    'sell_trades_large_order', 'buy_trades_med_order', 'sell_trades_med_order', 'buy_trades_small_order',
    'sell_trades_small_order', 'volume_diff_small_trader', 'volume_diff_small_trader_act',
    'volume_diff_med_trader', 'volume_diff_med_trader_act', 'volume_diff_large_trader',
    'volume_diff_large_trader_act', 'volume_diff_institute', 'volume_diff_institute_act',
    'value_diff_small_trader', 'value_diff_small_trader_act', 'value_diff_med_trader',
    'value_diff_med_trader_act', 'value_diff_large_trader', 'value_diff_large_trader_act',
    'value_diff_institute', 'value_diff_institute_act', 'mfd_inflowvolume', 'net_inflow_rate_volume',
    'mfd_inflow_openvolume', 'open_net_inflow_rate_volume', 'mfd_inflow_closevolume',
    'close_net_inflow_rate_volume', 'mfd_inflow', 'net_inflow_rate_value', 'mfd_inflow_open',
    'open_net_inflow_rate_value', 'mfd_inflow_close', 'close_net_inflow_rate_value', 'tot_volume_bid',
    'tot_volume_ask', 'moneyflow_pct_volume', 'open_moneyflow_pct_volume', 'close_moneyflow_pct_volume',
    'moneyflow_pct_value', 'open_moneyflow_pct_value', 'close_moneyflow_pct_value', 'mfd_inflowvolume_large_order',
    'net_inflow_rate_volume_l', 'mfd_inflow_large_order', 'net_inflow_rate_value_l', 'moneyflow_pct_volume_l',
    'moneyflow_pct_value_l', 'mfd_inflow_openvolume_l', 'open_net_inflow_rate_volume_l',
    'mfd_inflow_open_large_order', 'open_net_inflow_rate_value_l', 'open_moneyflow_pct_volume_l',
    'open_moneyflow_pct_value_l', 'mfd_inflow_closevolume_l', 'close_net_inflow_rate_volume_l',
    'mfd_inflow_close_large_order', 'close_net_inflow_rate_valu_l', 'close_moneyflow_pct_volume_l',
    'close_moneyflow_pct_value_l', 'buy_value_exlarge_order_act', 'sell_value_exlarge_order_act',
    'buy_value_large_order_act', 'sell_value_large_order_act', 'buy_value_med_order_act',
    'sell_value_med_order_act', 'buy_value_small_order_act', 'sell_value_small_order_act',
    'buy_volume_exlarge_order_act', 'sell_volume_exlarge_order_act', 'buy_volume_large_order_act',
    'sell_volume_large_order_act', 'buy_volume_med_order_act', 'sell_volume_med_order_act',
    'buy_volume_small_order_act', 'sell_volume_small_order_act']

def update_morning_data(address='/data/group/800442/800319/junkData/daily'):

    date = get_recent_trade_date(dividing_point=7)
    pre_date = get_recent_trade_date(dividing_point=23)

    _stock_list = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list')
    _adjfactor = pd.read_hdf('%s/adjfactor.h5' % address, 'adjfactor')
    # _pause = pd.read_hdf('%s/pause.h5' % address, 'pause')
    _pre_close = pd.read_hdf('%s/pre_close.h5' % address, 'pre_close')

    # df = pd.concat([fd.get_factor_value('Wind_vip', None, [str(date)], ['trade_status'])['trade_status'
    #                ].dropna().rename('pause').reset_index().set_index('stock').drop('mddate', axis=1),
    #                fd.get_factor_value('Basic_factor', None, [str(date)], ['mdc_pre_close'])['mdc_pre_close'
    #                ].dropna().rename('pre_close').reset_index().set_index('stock').drop('mddate', axis=1)],
    #               axis=1).dropna()

    df = fd.get_factor_value('Basic_factor', None, [str(date)], ['mdc_pre_close'])['mdc_pre_close'].dropna().rename(
        'pre_close').reset_index().set_index('stock').drop('mddate', axis=1)

    if len(df) == 0:
        raise Exception("new data has not arrived.")

    df.index = df.index.map(trans_windcode2int)
    # df['pause'] = df['pause'] != '交易'
    df['close'] = pd.read_hdf('%s/close.h5' % address, 'close', start=-1).loc[pre_date]
    df['preadj'] = _adjfactor.loc[pre_date]
    df['adjfactor'] = df['close'] * df['preadj'] / df['pre_close']
    df['true'] = True

    stock_list = pd.concat([_stock_list.loc[:pre_date], pd.DataFrame(df['true'].rename(date)).T]) > 0.5
    stock_list = stock_list.convert_objects()
    stock_list.to_hdf('%s/stock_list.h5' % address, 'stock_list', format='t')

    # pause = pd.concat([_pause.loc[:pre_date], pd.DataFrame(df['pause'].rename(date)).T]) > 0.5
    # pause = pause.convert_objects()
    # pause.to_hdf('%s/pause.h5' % address, 'pause', format='t')

    adjfactor = pd.concat([_adjfactor.loc[:pre_date], pd.DataFrame(df['adjfactor'].rename(date)).T])
    adjfactor = adjfactor.convert_objects()
    adjfactor.to_hdf('%s/adjfactor.h5' % address, 'adjfactor', format='t')

    pre_close = pd.concat([_pre_close.loc[:pre_date], pd.DataFrame(df['pre_close'].rename(date)).T])
    pre_close = pre_close.convert_objects()
    pre_close.to_hdf('%s/pre_close.h5' % address, 'pre_close', format='t')

def _update_check(new, factor_type, factor, recent_trade_date):

    if (new.iloc[-1].isnull().all()) | (int(new.index[-1]) != recent_trade_date):
        _update_log('ERROR', factor_type, factor, 'update', 'New data has not arrived')
        raise Exception("New data has not arrived")

def _error_check(new, old, factor_type, factor, accept_error=0., file='/data/group/800442/800319/junkData/updateLog.txt'):

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

def _store_daily_data(item='all', address='/data/group/800442/800319/junkData/daily'):

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
        df = df.reindex(columns=stock_list.columns)
        df = df.convert_objects()
        df.to_hdf('%s/%s.h5' % (address, item), item, format='t')
        _update_log('SUCCEED', 'daily', item, 'store', 'time range %s~%s' % (date[0], date[-1]))

def update_stock_list(address='/data/group/800442/800319/junkData/daily'):

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

def update_ind_con(address='/data/group/800442/800319/junkData/daily'):

    for ind_type in ['CITICS', 'SW', 'SW2021']:
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

def update_daily_data(item='all', address='/data/group/800442/800319/junkData/daily'):

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

def update_pause(address='/data/group/800442/800319/junkData/daily'):

    recent_trade_date = get_recent_trade_date()
    amt = pd.read_hdf('%s/amt.h5' % address, 'amt')
    _update_check(amt, 'daily', 'amt', recent_trade_date)
    pause = amt.fillna(0) <= 1
    pause = pause.convert_objects()
    pause.to_hdf('%s/pause.h5' % address, 'pause', format='t')
    _update_log('SUCCEED', 'daily', 'pause', 'update')

def update_live_days(address='/data/group/800442/800319/junkData/daily'):

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

def update_normal_days(address='/data/group/800442/800319/junkData/daily'):
    _normal_days = pd.read_hdf('%s/normal_days.h5' % address, 'normal_days')
    date = get_date_range(_normal_days.index[-1])
    amt = pd.read_hdf('%s/amt.h5' % address, 'amt').loc[date]
    opn = pd.read_hdf('%s/open.h5' % address, 'open').loc[date]
    high = pd.read_hdf('%s/high.h5' % address, 'high').loc[date]
    low = pd.read_hdf('%s/low.h5' % address, 'low').loc[date]
    close = pd.read_hdf('%s/close.h5' % address, 'close').loc[date]
    pre_close = pd.read_hdf('%s/pre_close.h5' % address, 'pre_close').loc[date]
    _update_check(amt, 'daily', 'amt', date[-1])
    _update_check(amt, 'daily', 'open', date[-1])
    _update_check(amt, 'daily', 'high', date[-1])
    _update_check(amt, 'daily', 'low', date[-1])
    _update_check(amt, 'daily', 'close', date[-1])
    _update_check(amt, 'daily', 'pre_close', date[-1])
    normal_days = ((opn == high) & (high == low) & (low == close) & (close > pre_close)) | (close / pre_close > 1.4)
    normal_days = normal_days * 1.0
    normal_days[amt.isnull()] = np.nan
    normal_days = normal_days.cumprod() < 0.5
    df = pd.concat([_normal_days.loc[[get_pre_trade_date(date[0])]], normal_days]).fillna(0).cumsum()
    df = pd.concat([_normal_days.loc[:get_pre_trade_date(date[0], 2)], df]).fillna(0)
    df = df.convert_objects()
    df.to_hdf('%s/normal_days.h5' % address, 'normal_days', format='t')
    _update_log('SUCCEED', 'daily', 'normal_days', 'update')

def update_price_get_limit(address='/data/group/800442/800319/junkData/daily'):

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

def update_bench_exdiv_weight(address='/data/group/800442/800319/junkData/daily'):

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

def update_dividend(address='/data/group/800442/800319/junkData/daily'):

    getEXRightDividend().convert_objects().to_hdf('%s/ex_right_dividend.h5' % address, 'ex_right_dividend', format='t')
    _update_log('SUCCEED', 'daily', 'ex_right_dividend', 'update')

def update_common_stock_list(address='/data/group/800442/800319/junkData/daily'):

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

def update_limit_price(address='/data/group/800442/800319/junkData/daily'):

    code = pd.read_hdf('%s/stock_list.h5' % address, 'stock_list', start=-1).columns.to_list()

    _limit_max = pd.read_hdf('%s/%s.h5' % (address, 'limit_max'), 'limit_max')
    last_date = ['>' + str(_limit_max.index[-1])]
    try:
        limit_max = fd.get_factor_value(
            "WIND_AShareEODPrices",
            factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_LIMIT'],
            TRADE_DT=last_date,
        )
    except:
        pass
    else:
        limit_max = limit_max.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_LIMIT')
        limit_max.index = limit_max.index.map(int)
        limit_max.columns = limit_max.columns.map(trans_windcode2int)
        limit_max = pd.concat([_limit_max, limit_max]).reindex(columns=code)
        limit_max = limit_max.convert_objects()
        limit_max.to_hdf('%s/%s.h5' % (address, 'limit_max'), 'limit_max', format='t')

    _limit_min = pd.read_hdf('%s/%s.h5' % (address, 'limit_min'), 'limit_min')
    last_date = ['>' + str(_limit_min.index[-1])]
    try:
        limit_min = fd.get_factor_value(
            "WIND_AShareEODPrices",
            factors=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_STOPPING'],
            TRADE_DT=last_date,
        )
    except:
        pass
    else:
        limit_min = limit_min.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_STOPPING')
        limit_min.index = limit_min.index.map(int)
        limit_min.columns = limit_min.columns.map(trans_windcode2int)
        limit_min = pd.concat([_limit_min, limit_min]).reindex(columns=code)
        limit_min = limit_min.convert_objects()
        limit_min.to_hdf('%s/%s.h5' % (address, 'limit_min'), 'limit_min', format='t')

def amend_daily_data(address='/data/group/800442/800319/junkData/daily'):
    free_float_shares = pd.read_hdf(f'{address}/free_float_shares.h5', 'free_float_shares')
    free_float_shares[free_float_shares <= 0] = np.nan
    free_float_shares = free_float_shares.ffill(limit=20)
    free_float_shares.to_hdf(f'{address}/free_float_shares.h5', 'free_float_shares', format='t')

if __name__ == '__main__':

    address = '/data/group/800442/800319/junkData/daily'

    update_stock_list(address='/data/group/800442/800319/junkData/daily')

    update_ind_con(address='/data/group/800442/800319/junkData/daily')

    for i in range(len(daily_data_list)):
        try:
            update_daily_data(daily_data_list[i], address='/data/group/800442/800319/junkData/daily')
        except Exception:
            if dt.datetime.now().hour < 18:
                print(daily_data_list[i])
            else:
                print(daily_data_list[i])
                raise Exception

    for i in range(len(money_flow_data_list)):
        try:
            _store_daily_data(money_flow_data_list[i], address='/data/group/800442/800319/junkData/daily')
        except Exception:
            if dt.datetime.now().hour < 18:
                print(money_flow_data_list[i])
            else:
                print(money_flow_data_list[i])
                raise Exception

    update_pause(address='/data/group/800442/800319/junkData/daily')

    update_live_days(address='/data/group/800442/800319/junkData/daily')

    update_normal_days(address='/data/group/800442/800319/junkData/daily')

    update_price_get_limit(address='/data/group/800442/800319/junkData/daily')

    update_dividend(address='/data/group/800442/800319/junkData/daily')

    update_bench_exdiv_weight(address='/data/group/800442/800319/junkData/daily')

    update_common_stock_list(address='/data/group/800442/800319/junkData/daily')

    _store_ST()

    _store_limit_range()

    amend_daily_data(address='/data/group/800442/800319/junkData/daily')