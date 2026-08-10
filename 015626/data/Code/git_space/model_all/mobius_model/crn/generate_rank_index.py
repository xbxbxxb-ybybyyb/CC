import os
import pickle
import pandas as pd
from multifactor.IO import IO
from multifactor.utility import dt


def main():
    # set ticker, start_date, end_date
    ticker = 'IC' 
    sample_date_list = [x.strftime('%Y%m%d') for x in dt.get_trading_date_range(start_date='20200101', end_date='20230412')]

    # sample parameters
    num_samples = 60000
    min_quantile = 0.25
    max_quantile = 0.75

    # set output path
    output_root = f'/data/user/020529/share/model_update/rank_index/{ticker.lower()}_{num_samples}_{int(min_quantile * 100)}_{int(max_quantile * 100)}'
    os.makedirs(output_root, exist_ok=True)

    # **************************************************

    price = get_price_from_market_data(ticker)

    minute_ret = price.groupby(price.index.date).apply(lambda x: x.pct_change(5, fill_method=None).shift(-6))
    minute_std = price.groupby(price.index.date).apply(lambda x: x.pct_change(1, fill_method=None).rolling(30, min_periods=30, center=True).std())

    for sample_date in sample_date_list:
        data_end_date = (pd.Timestamp(sample_date) - pd.Timedelta(days=1)).strftime('%Y%m%d')
        index_list = get_index_list(minute_ret, minute_std, data_end_date, num_samples, min_quantile, max_quantile)
        output_path = f'{output_root}/{sample_date}.pkl'
        print(f'save index to {output_path}', flush=True)
        with open(output_path, mode='wb') as file:
            pickle.dump(index_list, file)
    return None


def get_price_from_market_data(ticker):
    univ = IO.read_data(alt='/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
    data = IO.read_data(columns=['close'], alt=f'/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/{ticker}_MINUTE.h5')

    index = univ.xs(f'{ticker}.CFE', level=1)['contract_00']
    index.name = 'Ticker'
    price = data['close']

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
    price = price['close']
    price = price.between_time(start_time='09:30', end_time='14:56')
    return price


def get_index_list(minute_ret, minute_std, data_end_date, num_samples, min_quantile, max_quantile):
    assert len(minute_ret[:data_end_date]) >= num_samples
    assert len(minute_std[:data_end_date]) >= num_samples
    minute_ret = minute_ret[:data_end_date].tail(num_samples)
    minute_std = minute_std[:data_end_date].tail(num_samples)

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


if __name__ == '__main__':
    main()
