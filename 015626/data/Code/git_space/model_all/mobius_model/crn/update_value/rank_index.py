import sys

sys.path.insert(0, '/data/user/020529/mobius_product/code')

import os
import time
import pickle
import datetime
import warnings
import traceback
import pandas as pd
from toolkit.multifactor.data.utils import get_current_date
from toolkit.multifactor.utility.dt import get_trading_day_offset
from toolkit.multifactor.utility.dt import get_trading_date_range
from toolkit.multifactor.IO.IO import read_data
from xquant.xqutils.helper import link


def main():
    YMD = '%Y%m%d'
    YMD_HMS = '%Y-%m-%d %H:%M:%S'
    curr_date = str(get_current_date(new_date_time=18))
    next_date = get_trading_day_offset(curr_date, 1)[0].strftime(YMD)

    now = datetime.datetime.now().strftime(YMD_HMS)
    print(f'[{now}] Check flags', flush=True)
    counter = 0
    while True:
        if check_flags(curr_date):
            break
        elif counter < 60 * 24:
            time.sleep(60)
            counter += 1
        else:
            raise RuntimeError('Timeout')
    now = datetime.datetime.now().strftime(YMD_HMS)
    print(f'[{now}] Flags ready', flush=True)

    # ****************************************************************************************************

    trade_date_list = get_trading_date_range(start_date='20190101', end_date=next_date)
    trade_date_list = [x.strftime(YMD) for x in trade_date_list]
    trade_date_list = trade_date_list[-5:]

    num_samples = 60000
    min_quantile = 0.25
    max_quantile = 0.75

    output_root = f'/data/user/020529/share/mobius_prod/model_update/rank_index'
    os.makedirs(output_root, exist_ok=True)

    for ticker_type in ['IH', 'IF', 'IC', 'IM']:
        if ticker_type == 'IM':
            price = get_price_from_market_data_im(ticker_type)
        else:
            price = get_price_from_market_data(ticker_type)

        minute_ret = price.groupby(price.index.date).apply(lambda x: x.pct_change(5, fill_method=None).shift(-6))
        minute_std = price.groupby(price.index.date).apply(lambda x: x.pct_change(1, fill_method=None).rolling(30, min_periods=30, center=True).std())

        for trade_date in trade_date_list:
            end_date = get_trading_day_offset(trade_date, -1)[0].strftime(YMD)
            index_list = get_index_list(minute_ret, minute_std, end_date, num_samples, min_quantile, max_quantile)

            output_name = f'{ticker_type.lower()}_{num_samples}_{int(min_quantile * 100)}_{int(max_quantile * 100)}'
            output_path = f'{output_root}/{output_name}/{trade_date}.pkl'
            os.makedirs(f'{output_root}/{output_name}', exist_ok=True)
            print(output_path, flush=True)
            with open(output_path, mode='wb') as file:
                pickle.dump(index_list, file)

    # ****************************************************************************************************

    generate_flags(next_date)
    return None


def get_price_from_market_data_im(ticker_type):
    im_sim_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/future_twap_im_interpolation.h5'
    price_fake = pd.read_hdf(im_sim_path)
    assert isinstance(price_fake, pd.Series)
    price_fake = price_fake[:'20220721']  # launch date = 20220722
    price_fake = price_fake.between_time(start_time='09:30', end_time='14:56')

    price_type = 'twap'
    univ = read_data(alt='/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
    data = read_data(columns=[price_type], alt=f'/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/{ticker_type}_MINUTE.h5')

    index = univ.xs(f'{ticker_type}.CFE', level=1)['contract_00']
    index.name = 'Ticker'
    price_real = data[price_type]

    date_list = price_real.index.get_level_values(0).date
    index = index.loc[date_list[0]:date_list[-1]]
    index = index.reset_index()
    index['date'] = [x.date() for x in index['dt']]
    index = index.set_index(['date', 'Ticker'])

    price_real = price_real.reset_index()
    price_real['date'] = [x.date() for x in price_real['dt']]
    price_real = price_real.set_index(['date', 'Ticker'])
    price_real = price_real.loc[index.index]
    price_real = price_real.set_index('dt')
    price_real = price_real[price_type]
    price_real = price_real['20220722':]  # launch date = 20220722
    price_real = price_real.between_time(start_time='09:30', end_time='14:56')

    price = pd.concat([price_fake, price_real], axis=0)
    price = price.between_time(start_time='09:30', end_time='14:56')
    return price


def get_price_from_market_data(ticker_type):
    price_type = 'close'
    univ = read_data(alt='/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
    data = read_data(columns=[price_type], alt=f'/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/{ticker_type}_MINUTE.h5')

    index = univ.xs(f'{ticker_type}.CFE', level=1)['contract_00']
    index.name = 'Ticker'
    price = data[price_type]

    date_list = price.index.get_level_values(0).date
    index = index.loc[date_list[0]:date_list[-1]]
    index = index.reset_index()
    index['date'] = [x.date() for x in index['dt']]
    index = index.set_index(['date', 'Ticker'])

    price = price.reset_index()
    price['date'] = [x.date() for x in price['dt']]
    price = price.set_index(['date', 'Ticker'])
    price = price.loc[index.index]
    price = price.set_index('dt')
    price = price[price_type]
    price = price.between_time(start_time='09:30', end_time='14:56')
    return price


def get_index_list(minute_ret, minute_std, end_date, num_samples, min_quantile, max_quantile):
    assert len(minute_ret[:end_date]) >= num_samples
    assert len(minute_std[:end_date]) >= num_samples
    minute_ret = minute_ret[:end_date].tail(num_samples)
    minute_std = minute_std[:end_date].tail(num_samples)

    min_std = minute_std.quantile(min_quantile)
    max_std = minute_std.quantile(max_quantile)

    select_pos = (minute_ret > 0) & (minute_std > min_std) & (minute_std < max_std)
    select_neg = (minute_ret < 0) & (minute_std > min_std) & (minute_std < max_std)
    select_num = min(select_pos.sum(), select_neg.sum())
    select_pos = select_pos[select_pos].tail(select_num)
    select_neg = select_neg[select_neg].tail(select_num)

    index_list = select_pos.index.to_list() + select_neg.index.to_list()
    index_list.sort()
    return index_list


def check_flags(date):
    flag1 = os.path.exists(f'/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/{date}/{date}_stock_index_future_universe.success')
    flag2 = os.path.exists(f'/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/{date}/{date}_tick_concat.success')
    ready = flag1 and flag2
    return ready


def generate_flags(date):
    flag_path = f'/data/user/020529/share/flag/{date}/rank_index.success'
    flag_root = os.path.dirname(flag_path)
    os.makedirs(flag_root, exist_ok=True)
    file = open(flag_path, mode='w')
    file.close()
    return None


if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    try:
        main()
    except:
        traceback.print_exc()
        link.LinkMessage().sendMessage('Error: rank_index')
