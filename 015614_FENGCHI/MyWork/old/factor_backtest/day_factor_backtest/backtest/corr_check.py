import os
import numpy as np
import pandas as pd
import pickle
from day_factor_backtest.backtest.test_data_loader import *
from day_factor_backtest.backtest.normalization import Normalization2
from day_factor_backtest.backtest.factor_test_helper import update_neu_factor

is_day_factor = True
price_type = 'vwap'
real_price_type = 'vwap'
neutralize = True
rho = 4e-4
top_range = 0.1
neutralize = True
turnover_mode = True
ret_weight = False


def weight_descending_mapping(x):
    if x <= 0:
        return 0
    elif x <= 0.05:
        return 4.
    elif x <= 0.10:
        return 3.
    elif x <= 0.15:
        return 2.
    elif x <= 0.20:
        return 1.


def get_neu_factor(factor_df):
    factor_start_date = factor_df.index[0]
    factor_end_date = factor_df.index[-1]

    industry_code_all = get_industry_code_all(factor_start_date, factor_end_date)
    industry_list = industry_code_all.stack().unique()
    industry_list = industry_list[industry_list != 0]

    industry_mark = {}
    for industry in industry_list:
        tmp = pd.DataFrame(0., index=industry_code_all.index, columns=industry_code_all.columns)
        tmp[industry_code_all == industry] = 1
        industry_mark[industry] = tmp
    industry_mark_df = pd.concat(industry_mark)

    size = get_mkt_cap_ard(factor_start_date, factor_end_date)
    size = np.log(size)

    norm_size = Normalization2(size, axis=0)
    norm_size = norm_size.norm_dataframe()

    if industry_code_all.index[-1] != norm_size.index[-1]:
        assert False
    if industry_code_all.index[0] != norm_size.index[0]:
        assert False
    try:
        dates_need_update = factor_df.index.tolist()
        factor_neu_update = update_neu_factor(factor_df, norm_size, industry_mark_df, dates_need_update)
        factor_neu_all = factor_neu_update
        factor_neu_all = factor_neu_all.sort_index()
        return factor_neu_all
    except:
        raise AssertionError("factor data has some problem in neutralization, please check your data.")


def get_excess_return(factor_df, start_date, end_date):
    price_adj = get_price_data(real_price_type)

    if is_day_factor:
        if price_type == 'vwap':
            re_1d = price_adj.pct_change(1).shift(-2).iloc[:-2]
        elif price_type == 'close':
            re_1d = price_adj.pct_change(1).shift(-1).iloc[:-1]
        else:
            print('warning: price_type only is vwap or close.')
    else:
        re_1d = price_adj.pct_change(1).shift(-1).iloc[:-1]

    is_valid = get_is_universe()
    is_valid_raw = get_is_valid_raw()
    if is_day_factor:
        if price_type == 'vwap':
            is_valid = is_valid[np.logical_and(is_valid_raw.shift(-2) == 1, is_valid_raw.shift(-1) == 1)]
        elif price_type == 'close':
            is_valid = is_valid[is_valid_raw.shift(-1) == 1]
    else:
        is_valid = is_valid[is_valid_raw.shift(-1) == 1]

    is_valid01 = (is_valid == 1).loc[start_date:end_date]
    re_1d = re_1d[is_valid01].loc[start_date:end_date]

    excess_return = re_1d.subtract(re_1d.mean(axis=1), axis=0)

    if neutralize:
        factor_df = get_neu_factor(factor_df)
    factor_df = factor_df[is_valid01]

    update_date_list_end = factor_df.index[-2]
    factor_ranker_pct_descending = factor_df.rank(pct=True, axis=1, method='first', ascending=False)

    turnover_rate = 0
    wi_descending_01 = ((factor_ranker_pct_descending <= top_range) * 1).fillna(0)
    wi_descending = factor_ranker_pct_descending.fillna(0) * wi_descending_01

    # weighted
    if ret_weight:
        wi_descending = wi_descending.applymap(weight_descending_mapping)
        wi_descending = wi_descending.astype(float)
    else:
        wi_descending = wi_descending_01

    if turnover_mode:
        wi_turnover = (wi_descending - wi_descending.shift(1)).applymap(abs) / 2
        turnover_rate = wi_turnover.sum(axis=1) / wi_descending.sum(axis=1)
        turnover_rate[np.isinf(turnover_rate)] = np.nan

    wi_descending = wi_descending.divide(wi_descending.sum(axis=1), axis=0)

    ########################
    excess_descending = ((wi_descending * excess_return).sum(axis=1))[start_date:update_date_list_end]
    excess_descending = excess_descending - rho * turnover_rate

    save_factor_excess = excess_descending.to_frame()
    save_factor_excess.columns = ['excess_return']

    return save_factor_excess.loc[start_date:end_date]
