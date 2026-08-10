from multifactor.IO import IO
import multifactor.utility.dt as udt
from multiprocessing import Pool
import pandas as pd
import datetime, os, traceback
import bottleneck as bk
import numpy as np

future_universe_path = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/UNIV/CHINA_COMMODITY_MAIN_SECONDMAIN_PERDAY.h5'
commodity_data_rootpath = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD'
index_data_path = '/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_INDEX/MINUTE'

class TaskRunner(object):
    def __init__(self, save_factor = False, factor_root_path = None):
        if factor_root_path is None:
            OUTER_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
            self.factor_root_path = '{}/data_center/factor_data'.format(OUTER_ROOT_PATH)
        else:
            self.factor_root_path = factor_root_path
        self.save_factor = save_factor

    def prepare_data(self, data_center, days_past, date, variety):
        date = str(date)
        assert isinstance(days_past, int) and days_past >= 0, 'Invalid input of days_past!!!'
        prepared_data = data_center.get_continuous_data_dict()[variety][date]
        today_time_index = prepared_data[prepared_data.tday == int(date)].index
        return prepared_data, today_time_index

    def run_factor_single_day(self, factor, date, variety, prepared_data=None, time_index=None, data_center=None):
        date = str(date)
        # print(date)
        if data_center is not None:
            data,index = self.prepare_data(data_center,factor.days_past,date, variety)
        else:
            data = prepared_data
            index = time_index
        data_player = DataPlayer(date, factor.days_past, data, index, factor.required_columns)
        factor_value_list = []
        for _data in data_player.today_data_generator:
            factor_value_list.append(factor.calculate(_data))
        df_factor = pd.DataFrame(factor_value_list, index=index, columns=[factor.factor_name])
        return df_factor

    def run_factor_multi_day(self, factor, variety, data_center, start_date, end_date, parallel_num=24):

        date_list = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(start_date, end_date)]
        pool = Pool(parallel_num)
        tasks = []

        for date in date_list:
            prepared_data, time_index = self.prepare_data(data_center, factor.days_past,date, variety)
            tasks.append([pool.apply_async(self.run_factor_single_day, args=(factor,date,variety,prepared_data,time_index)), factor.factor_name, variety, date])

        pool.close()

        factor_list = []
        for t,n,v,d in tasks:
            try:
                factor_list.append(t.get())
            except Exception as e:
                print(e,traceback.format_exc())

        pool.join()

        df_factor = pd.concat(factor_list)

        assert factor.normalize_type in ['ts_rank','rolling_norm'], 'Invalid normalize type!!!'
        assert isinstance(factor.normalize_size,int), 'The normalized size of factor should be integer!!!'

        df_normalized_factor = None

        if factor.normalize_size in [0, 1]:
            df_normalized_factor = df_factor.copy()
        else:
            if factor.normalize_type == 'ts_rank':
                df_normalized_factor = self.ts_rank(df_factor, factor.normalize_size)
            # elif factor.normalize_type == 'rolling_norm':
            #     df_normalized_factor = self.rolling_norm(df_factor, factor.normalize_size)

        # Save the raw/norm value of the factor
        if self.save_factor:
            self.save_to_h5(df_factor, df_normalized_factor, factor.factor_name)

        return df_factor, df_normalized_factor

    def save_to_h5(self, df_raw, df_norm, name):

        path_raw = os.path.join(self.factor_root_path,'minute_raw')
        path_norm = os.path.join(self.factor_root_path,'minute_norm')

        if not os.path.exists(path_raw):
            os.makedirs(path_raw)
        if not os.path.exists(path_norm):
            os.makedirs(path_norm)

        self.pd_writer(df_raw, path_raw)
        self.pd_writer(df_norm, path_norm)

        # df_raw.to_hdf(os.path.join(path_raw, '%s.h5' % name), 'minute_data')
        # df_norm.to_hdf(os.path.join(path_norm, '%s.h5' % name), 'minute_data')

        print('Factor {} is saved.'.format(name))

    def pd_writer(self, sig, savepath):
        sig_name = sig.columns[0]
        file_name = os.path.join(savepath, sig_name + '.h5')
        if os.path.exists(file_name):
            #sigold = IO.read_data(alt = file_name)
            sigold = pd.read_hdf(file_name)
            sigold = sigold[~sigold.index.isin(sig.index)]
            signew = pd.concat([sigold,sig],axis=0).sort_index()
        else:
            signew = sig
        signew.to_hdf(file_name,key='minute_data')


    def ts_rank(self, df1, d=4800):
        # moving time-series rank for the past d periods
        assert isinstance(df1, pd.Series) or isinstance(df1, pd.DataFrame), 'input is not a dataframe or series'
        if d == 1:
            output = df1
        else:
            if isinstance(df1, pd.DataFrame):
                output = pd.DataFrame(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                      index=df1.index, columns=df1.columns)
            elif isinstance(df1, pd.Series):
                output = pd.Series(bk.move_rank(df1, window=d, min_count=int(d / 2), axis=0),
                                   index=df1.index, name=df1.name)
        return output

class DataPlayer(object):
    def __init__(self, date, days_past, data, today_index, play_columns):
        self.date = date
        self.days_past = days_past
        self.prepared_data = data
        self.today_index = today_index
        self.play_columns = play_columns

    @property
    def today_data_generator(self):
        date_list = np.unique(self.prepared_data.tday)
        if len(date_list) == 1:
            history_data = pd.DataFrame()
        else:
            history_data = self.prepared_data[self.prepared_data.tday < date_list[-1]]
        today_data = self.prepared_data[self.prepared_data.tday == date_list[-1]]
        for i in range(len(self.today_index)):
            play_data = pd.concat([history_data, today_data.iloc[:i + 1]]).reset_index()
            yield {col: play_data[col].values for col in self.play_columns}


def get_universe_contract(variety = 'IC', instrument_type = 'main', date = None):
    assert instrument_type in ['main', 'second_main'], 'instrument type must be in [main, second_main]'
    col_dict = {'main':'contract_main', 'second_main':'contract_second_main'}
    col_name = col_dict[instrument_type]
    univ = IO.read_data([date],columns=[col_name], alt = future_universe_path)
    if len(univ) == 0:
        print('the date maybe is not trading day')
        raise Exception
    return univ.xs('%s' % variety, level = 1)[col_name][0]

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

        self.__trading_days = [x.strftime('%Y%m%d') for x in udt.get_trading_date_range(self.__start_date, self.__end_date)]

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

class FutureFactor(object):

    days_past = 0
    required_columns = ['close', 'volume', 'low']
    instrument_type = 'main'
    normalize_size = 20 * 240
    normalize_type = 'ts_rank'

    def __init__(self):
        self.factor_name = self.__class__.__name__

    def calculate(self, data):

        factor_result = None

        return factor_result
