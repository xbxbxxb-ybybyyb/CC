import os
import numpy as np
import pandas as pd
from config.base import fmt, root, factor_root_dict, factor_list_dict


# ******************** fetch return ********************


def fetch_spot_data(ticker_type, columns=None):
    data_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5'
    data = pd.read_hdf(data_path)
    assert isinstance(data, pd.DataFrame)
    data = data.xs(f'{ticker_type}.CFE', level=1)
    if columns is not None:
        data = data[columns]
    data = data.between_time(start_time='09:30', end_time='14:56')
    return data


def fetch_spot_twap(ticker_type, columns=None):
    data_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/TWAP_SPOT.h5'
    data = pd.read_hdf(data_path)
    assert isinstance(data, pd.DataFrame)
    data = data.xs(f'{ticker_type}.CFE', level=1)
    if columns is not None:
        data = data[columns]
    data = data.between_time(start_time='09:30', end_time='14:56')
    return data


def fetch_recent_month_data(ticker_type, columns=None):
    data_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/XQUANT_MINUTE/MD_SIF_TICK_TO_MINUTE_RECENT_MONTH.h5'
    data = pd.read_hdf(data_path)
    assert isinstance(data, pd.DataFrame)
    data = data.xs(f'{ticker_type}.CFE', level=1)
    if columns is not None:
        data = data[columns]
    data = data.between_time(start_time='09:30', end_time='14:56')
    return data


def fetch_im_twap():
    im_twap_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/future_twap_im_interpolation.h5'
    price_fake = pd.read_hdf(im_twap_path)
    assert isinstance(price_fake, pd.Series)
    price_fake = price_fake.between_time(start_time='09:30', end_time='14:56')
    price_fake = price_fake.loc[:'20220721']  # start date = 20220722
    price_real = fetch_recent_month_data(ticker_type='IM', columns='twap')
    price_real = price_real.loc['20220722':]  # start date = 20220722
    price = pd.concat([price_fake, price_real], axis=0)
    return price


def fetch_return(ticker_type, str_date, end_date):
    assert ticker_type in {'IH', 'IF', 'IC', 'IM'}
    assert pd.Timestamp(str_date) < pd.Timestamp(end_date)

    if ticker_type in {'IH', 'IF', 'IC'}:
        price = fetch_recent_month_data(ticker_type, columns='vwap')
    else:
        price = fetch_im_twap()
    price = price.loc[str_date:end_date]
    return_all = {}
    for t in [1, 5, 10, 20, 30, 40, 50, 60]:
        return_all[t] = price.groupby(price.index.date).apply(lambda x: x.pct_change(t, fill_method=None).shift(-1 - t))
    return_all = pd.DataFrame(return_all)

    assert np.all(np.array(return_all.groupby(return_all.index.date).size() == 237))
    print('fetch return: {} -- {}, {}'.format(return_all.index[0].strftime(fmt), return_all.index[-1].strftime(fmt), return_all.shape), flush=True)
    return return_all


def fetch_return_spot(ticker_type, str_date, end_date):
    assert ticker_type in {'IH', 'IF', 'IC', 'IM'}
    assert pd.Timestamp(str_date) < pd.Timestamp(end_date)

    price = fetch_spot_twap(ticker_type, columns='twap_spot')
    price = price.loc[str_date:end_date]
    return_all = {}
    for t in [1, 5, 10, 20, 30, 40, 50, 60]:
        return_all[t] = price.groupby(price.index.date).apply(lambda x: x.pct_change(t, fill_method=None).shift(-1 - t))
    return_all = pd.DataFrame(return_all)

    assert np.all(np.array(return_all.groupby(return_all.index.date).size() == 237))
    print('fetch return: {} -- {}, {}'.format(return_all.index[0].strftime(fmt), return_all.index[-1].strftime(fmt), return_all.shape), flush=True)
    return return_all


def fetch_return_wr(ticker_type, str_date, end_date, weight):
    assert ticker_type in {'IH', 'IF', 'IC', 'IM'}
    assert pd.Timestamp(str_date) < pd.Timestamp(end_date)

    ref_str_date = '20190101'
    ref_end_date = '20231231'
    assert pd.Timestamp(ref_str_date) >= pd.Timestamp(str_date)
    assert pd.Timestamp(ref_end_date) <= pd.Timestamp(end_date)

    c = fetch_spot_data(ticker_type, columns='close_spot')
    c = c.loc[str_date:end_date]
    h = c.rolling(30).max()
    l = c.rolling(30).min()
    wr = (2 * c - h - l) / (h - l)
    mom = wr.rolling(30).mean()

    if ticker_type in {'IH', 'IF', 'IC'}:
        price = fetch_recent_month_data(ticker_type, columns='vwap')
    else:
        price = fetch_im_twap()
    price = price.loc[str_date:end_date]
    return_all = {}
    for t in [1, 5, 10, 20, 30, 40, 50, 60]:
        ret = price.groupby(price.index.date).apply(lambda x: x.pct_change(t, fill_method=None).shift(-1 - t))
        ret_abs = ret.loc[ref_str_date:ref_end_date].abs().mean()
        mom_abs = mom.loc[ref_str_date:ref_end_date].abs().mean()
        return_all[t] = ret + mom / mom_abs * ret_abs * weight
    return_all = pd.DataFrame(return_all)

    assert np.all(np.array(return_all.groupby(return_all.index.date).size() == 237))
    print('fetch return: {} -- {}, {}'.format(return_all.index[0].strftime(fmt), return_all.index[-1].strftime(fmt), return_all.shape), flush=True)
    return return_all


def fetch_return_swr(ticker_type, str_date, end_date, weight):
    assert ticker_type in {'IH', 'IF', 'IC', 'IM'}
    assert pd.Timestamp(str_date) < pd.Timestamp(end_date)

    c = fetch_spot_data(ticker_type, columns='close_spot')
    c = c.loc[str_date:end_date]
    mom = {}
    for n in [30, 40, 50, 60, 70, 80, 90, 100, 110, 120]:
        h = c.rolling(n).max()
        l = c.rolling(n).min()
        r = (2 * c - h - l) / (h - l)
        mom[n] = r.rolling(10).mean()
    mom = pd.concat(mom, axis=1).mean(axis=1)

    price = fetch_spot_twap(ticker_type, columns='twap_spot')
    price = price.loc[str_date:end_date]
    return_all = {}
    for t in [1, 5, 10, 20, 30, 40, 50, 60]:
        ret = price.groupby(price.index.date).apply(lambda x: x.pct_change(t, fill_method=None).shift(-1 - t))
        mom_abs = mom.abs().expanding(min_periods=10000).mean()
        ret_abs = ret.abs().expanding(min_periods=10000).mean()
        return_all[t] = ret + mom / mom_abs * ret_abs * weight
    return_all = pd.DataFrame(return_all)

    assert np.all(np.array(return_all.groupby(return_all.index.date).size() == 237))
    print('fetch return: {} -- {}, {}'.format(return_all.index[0].strftime(fmt), return_all.index[-1].strftime(fmt), return_all.shape), flush=True)
    return return_all


# ******************** fetch factor ********************


def fetch_factor_from_root(factor_root_name, str_date, end_date):
    assert factor_root_name in factor_root_dict
    assert pd.Timestamp(str_date) < pd.Timestamp(end_date)

    factor_root_path = factor_root_dict[factor_root_name]
    factor_list = []
    file_list = os.listdir(factor_root_path)
    for file_name in file_list:
        factor_path = os.path.join(factor_root_path, file_name)
        factor = pd.read_hdf(factor_path)
        assert isinstance(factor, pd.DataFrame)
        factor = factor.loc[str_date:end_date]
        factor = factor.between_time(start_time='09:30', end_time='14:56')
        factor_list.append(factor)
    factor_all = pd.concat(factor_list, axis=1, join='outer')
    factor_all = factor_all.sort_index(axis=1, ascending=True)
    assert factor_all.columns.is_unique

    assert np.all(np.array(factor_all.groupby(factor_all.index.date).size() == 237))
    print('fetch factor: {} -- {}, {}'.format(factor_all.index[0].strftime(fmt), factor_all.index[-1].strftime(fmt), factor_all.shape), flush=True)
    return factor_all


def fetch_factor_from_list(factor_root_name, factor_list_name, str_date, end_date):
    assert factor_root_name in factor_root_dict
    assert factor_list_name in factor_list_dict
    assert pd.Timestamp(str_date) < pd.Timestamp(end_date)

    factor_root_path = factor_root_dict[factor_root_name]
    factor_list_path = factor_list_dict[factor_list_name]
    factor_list = []
    file_list = pd.read_pickle(factor_list_path)
    for file_name in file_list:
        factor_path = os.path.join(factor_root_path, file_name)
        factor = pd.read_hdf(factor_path)
        assert isinstance(factor, pd.DataFrame)
        factor = factor.loc[str_date:end_date]
        factor = factor.between_time(start_time='09:30', end_time='14:56')
        factor_list.append(factor)
    factor_all = pd.concat(factor_list, axis=1, join='outer')
    factor_all = factor_all.sort_index(axis=1, ascending=True)
    assert factor_all.columns.is_unique

    assert np.all(np.array(factor_all.groupby(factor_all.index.date).size() == 237))
    print('fetch factor: {} -- {}, {}'.format(factor_all.index[0].strftime(fmt), factor_all.index[-1].strftime(fmt), factor_all.shape), flush=True)
    return factor_all


# ******************** save data ********************


def save_return(ticker_type, return_data):
    data_path = os.path.join(root, 'data', 'return', '{}.h5'.format(ticker_type))
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    return_data = return_data.astype('float32')
    return_data.to_hdf(data_path, key='df')
    print('save return to {}'.format(data_path), flush=True)
    return None


def save_factor(factor_base, factor_data):
    data_path = os.path.join(root, 'data', 'factor', '{}.h5'.format(factor_base))
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    factor_data = factor_data.astype('float32')
    factor_data.to_hdf(data_path, key='df')
    print('save factor to {}'.format(data_path), flush=True)
    return None


def backup_return(ticker_type, backup_date, return_data):
    data_path = os.path.join(root, 'data', 'backup', '{}_{}.h5'.format(ticker_type, backup_date))
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    return_data = return_data.astype('float32')
    return_data.to_hdf(data_path, key='df')
    print('save return to {}'.format(data_path), flush=True)
    return None


def backup_factor(factor_base, backup_date, factor_data):
    data_path = os.path.join(root, 'data', 'backup', '{}_{}.h5'.format(factor_base, backup_date))
    os.makedirs(os.path.dirname(data_path), exist_ok=True)
    factor_data = factor_data.astype('float32')
    factor_data.to_hdf(data_path, key='df')
    print('save factor to {}'.format(data_path), flush=True)
    return None
