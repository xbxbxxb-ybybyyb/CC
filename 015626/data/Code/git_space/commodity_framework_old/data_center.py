from multifactor.IO import IO
import multifactor.utility.dt as udt
from multiprocessing import Pool
import pandas as pd
import datetime, os

future_universe_path = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/UNIV/CHINA_COMMODITY_MAIN_SECONDMAIN_PERDAY.h5'
commodity_data_rootpath = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD'
index_data_path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_INDEX/MINUTE'

def get_universe_contract(variety = 'IC', instrument_type = 'main', date = None):
    assert instrument_type in ['main', 'second_main'], 'instrument type must be in [main, second_main]'
    col_dict = {'main':'contract_main', 'second_main':'contract_second_main'}
    col_name = col_dict[instrument_type]
    univ = IO.read_data([date],columns=[col_name], alt = future_universe_path)
    if len(univ) == 0:
        print('the date maybe is not trading day')
        raise Exception
    return univ.xs('%s' % variety, level = 1)[col_name][0]

def get_continuous_df(date, df_list, variety_list, instrument_type):
    # print(date)
    data_list = []
    for i in range(len(variety_list)):
        v = variety_list[i]
        instrument_id = get_universe_contract(v, instrument_type, date)
        df_future_all = df_list[i]
        df_continuous_data = df_future_all[df_future_all['Ticker'] == instrument_id]
        df_continuous_data.columns = ['{}_cont_{}'.format(c, v) for c in df_continuous_data.columns]
        data_list.append(df_continuous_data)

    return pd.concat(data_list, axis=1, join='inner')

class DataCenter(object):

    def __init__(self, variety_list, instrument_type, data_freq, required_columns, start_date, end_date, days_past, parallel_num = 24):
        self.__instrument_type = instrument_type # 'main' or 'second_main'
        self.__data_freq = data_freq
        self.__start_date = str(start_date)
        self.__end_date = str(end_date)
        self.__required_columns = required_columns # data what you need
        self.__days_past = days_past # history days

        self.__variety_list = variety_list # kind IC/IF/IH

        self.__continuous_data_dict = {}

        self.__future_data = None
        self.__index_data = None
        self.__other_instrument_data = None
        self.__other_variety_data = None
        self.__parallel_num = parallel_num

        self.__minute_future_path = os.path.join(commodity_data_rootpath, str.upper(data_freq), 'PER_TICKER_old')

        self.__trading_days = udt.get_trading_date_range(self.__start_date, self.__end_date)

        self.load_data()

    def get_variety_list(self):
        return self.__variety_list
    def get_instrument_type(self):
        return self.__instrument_type
    def get_continuous_data_dict(self):
        return self.__continuous_data_dict

    def load_future_data(self, variety, columns):
        if 'tday' not in columns:
            columns += ['tday']
        future_data = IO.read_data([udt.get_trading_day_offset(self.__start_date, -20)[0].strftime('%Y%m%d'), self.__end_date+'235959'],columns = columns, alt='{}/{}.h5'.format(self.__minute_future_path,variety))
        future_data['tday'] = future_data['tday'].astype('int')
        return future_data

    def get_continus_data_for_variety(self, variety):
        future_data = self.load_future_data(variety, self.__required_columns)
        continuous_dict = {}
        for date in self.__trading_days:
            date_list = udt.get_trading_date_range('20000101', date)[-self.__days_past - 1:]
            dt1 = int(date_list[0].strftime('%Y%m%d'))
            dt2 = int(date_list[-1].strftime('%Y%m%d'))
            contract = get_universe_contract(variety, self.__instrument_type, date)
            select = future_data.xs(contract, level = 1)
            select['contract'] = contract
            continuous_dict[date] = select[(select['tday'] >= dt1) & (select['tday'] <= dt2)]
        return {variety : continuous_dict}

    def load_data(self):
        print('DataCenter initializing')
        with Pool(self.__parallel_num) as pool:
            rlist = pool.map(self.get_continus_data_for_variety, self.__variety_list)
        self.__continuous_data_dict = {k: v for d in rlist for k, v in d.items()}
        print('DataCenter done')
