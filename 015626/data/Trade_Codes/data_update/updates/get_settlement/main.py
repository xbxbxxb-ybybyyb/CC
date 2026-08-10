import pandas as pd
from insight_base import *
from xquant.futuredata import FutureData
fd = FutureData()


def get_future_codes(date=None, ticker_list=('IC', 'IF', 'IH', 'IM')):
    if date is None:
        date = int(pd.Timestamp.now().strftime('%Y%m%d'))
    result_list = list()
    for ticker in ticker_list:
        result_list += fd.get_instrument_all(ticker, date, date)
    return result_list


def retrieve_misc_minute_helper(release_resource=True):
    today = pd.Timestamp.now().strftime('%Y%m%d')
#    contract_info = pd.read_hdf(futures_contract_info_path)
    tickers = get_future_codes()
    data = job_wrapper(play_back_oneday, OnRecvKLine, postprocess_playback, release_resource=release_resource, stock_list=tickers,
                       start_time=today+'135900', stop_time=today+'150000', marketdata_type=EMarketDataType.MD_KLINE_1MIN)
    data_need = data.groupby('Ticker')['TotalValueTrade'].sum() / data.groupby('Ticker')['TotalVolumeTrade'].sum()
    data_need = data_need / (data_need.index.str.startswith(('IF', 'IH')) + 2) / 100
    data_need = data_need.to_frame()
    data_need.columns = ['settle']
    data_need['date'] = today
    data_need.index.name = ''
    data_need['Ticker'] = data_need.index
    data_need['Ticker'] = data_need['Ticker'].apply(lambda x: x.replace('.CF', ''))
    data_need = data_need.set_index('Ticker')
    data_need.to_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/settlements/%s.pkl'%today)
    return data_need


if __name__ == '__main__':
    data = retrieve_misc_minute_helper()
    print(data)

