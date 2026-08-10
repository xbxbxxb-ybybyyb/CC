import os
import traceback
import pandas as pd
import bottleneck as bk
import numpy as np
from multiprocessing import Pool
from function_tools import *
from data_player import DataPlayer
from factor_manager import FactorManager
from data_center import DataCenter

class TaskRunner(object):

    def __init__(self):
        OUTER_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
        self.factor_root_path = '{}/data_center/factor_data'.format(OUTER_ROOT_PATH)
        self.factor_raw_path = '{}/data_center/factor_data/minute_raw'.format(OUTER_ROOT_PATH)
        self.factor_manager = FactorManager()

    def __get_future_data(self, data_center, date_list, date):

        data_list = []
        if data_center.get_future_data() is not None:
            data_list.append(data_center.get_future_data().loc[date_list[0]:date_list[-1]])
        if data_center.get_index_data() is not None:
            data_list.append(data_center.get_index_data().loc[date_list[0]:date_list[-1]])
        if data_center.get_other_instrument_data() is not None:
            data_list.append(data_center.get_other_instrument_data().loc[date_list[0]:date_list[-1]])
        if data_center.get_other_variety_data() is not None:
            data_list.append(data_center.get_other_variety_data().loc[date_list[0]:date_list[-1]])
        if data_center.get_data_dict().get('Continuous_Data') is not None:
            data_list.append(data_center.get_continuous_data_dict()[date])

        if len(data_list) > 0:
            df_data = pd.concat(data_list, axis=1, join='inner')
        else:
            df_data = None

        return df_data

    def prepare_data(self, data_center, days_past, date):

        assert isinstance(days_past, int) and days_past >= 0, 'Invalid input of days_past!!!'
        assert data_center.get_data_type() in ['Future', 'IndexStock'], 'Invalid input of data type!!!'

        date_list = sorted(get_trading_days('19900101', date)[-days_past - 1:])

        assert len(date_list) > 0, 'No data to prepare!'

        if data_center.get_data_type() == 'IndexStock':
            index_code = data_center.get_index_code()
            stock_list = get_constituent_stock_list(index_code, date)
            stock_dict = data_center.get_stock_data()
            prepared_data = {}

            today_time_index = None

            for i, v in stock_dict.items():
                prepared_data[i] = v.loc[date_list[0]:date_list[-1]][stock_list]
                today_time_index = prepared_data[i].loc[date].index

            df_future = self.__get_future_data(data_center,date_list,date)

            if df_future is not None:
                df_future_dict = {k: df_future[[k]] for k in df_future.columns}
                prepared_data = {**prepared_data, **df_future_dict}

            industry_data_dict = data_center.get_industry_data_dict()
            if industry_data_dict is not None:
                for i,v in industry_data_dict.items():
                    prepared_data.update({i:v.loc[date_list[0]:date_list[-1]]})
                    today_time_index = prepared_data[i].loc[date].index

        elif data_center.get_data_type() == 'Future':
            prepared_data = self.__get_future_data(data_center,date_list,date)
            today_time_index = prepared_data.loc[date].index

        return prepared_data, today_time_index

    def run_factor_single_day(self, f, date, prepared_data=None, time_index=None, data_center=None):
        print(date)
        factor = f.__class__()
        if data_center is not None:
            data,index = self.prepare_data(data_center,factor.days_past,date)
        else:
            data = prepared_data
            index = time_index

        data_player = DataPlayer(date, factor.days_past, factor.data_type, data, index)
        factor_value_list = []

        for _data in data_player.today_data_generator:
            factor_value_list.append(factor.calculate(_data))

        df_factor = pd.DataFrame(factor_value_list, index=index, columns=[factor.factor_name])

        return df_factor

    def run_factor_multi_day(self, factor, variety, data_center, start_date, end_date, ncore=20):

        date_list = get_trading_days(start_date, end_date)
        pool = Pool(ncore)
        tasks = []

        for date in date_list:
            prepared_data, time_index = self.prepare_data(data_center,factor.days_past,date)
            tasks.append([pool.apply_async(self.run_factor_single_day, args=(factor,date,prepared_data,time_index)), factor.factor_name, variety, date])

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

        if factor.normalize_type == 'ts_rank':
            df_normalized_factor = (self.ts_rank(df_factor, factor.normalize_size) + 1) / 2
        elif factor.normalize_type == 'rolling_norm':
            df_normalized_factor = self.rolling_norm(df_factor, factor.normalize_size)

        # Save the raw/norm value of the factor
        self.save_to_h5(df_factor, df_normalized_factor, variety, factor.factor_name)

        return df_factor, df_normalized_factor

    def save_to_h5(self, df_raw, df_norm, variety, name):

        self.__check_folder('{}/minute_raw/{}'.format(self.factor_root_path, variety))
        self.__check_folder('{}/minute_norm/{}'.format(self.factor_root_path, variety))

        path_raw = '{}/minute_raw/{}/{}.h5'.format(self.factor_root_path, variety, name)
        path_norm = '{}/minute_norm/{}/{}.h5'.format(self.factor_root_path, variety, name)

        df_raw.to_hdf(path_raw,'minute_data')
        df_norm.to_hdf(path_norm,'minute_data')

        print('Factor {} is saved.'.format(name))

    def rolling_norm(self, sig, window=1200, method='max_min'):
        assert isinstance(sig, pd.Series) or isinstance(sig,
                                                        pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
        if window == 0:
            return sig
        else:
            if method == 'max_min':
                if isinstance(sig, pd.DataFrame):
                    sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                           index=sig.index, columns=sig.columns)
                    sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                           index=sig.index, columns=sig.columns)
                    temp = sig_max - sig_min
                    temp[abs(temp) < 1e-8] = np.nan
                    signal = (sig - sig_min) / temp
                elif isinstance(sig, pd.Series):
                    sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                        index=sig.index, name=sig.name)
                    sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                        index=sig.index, name=sig.name)
                    temp = sig_max - sig_min
                    temp[abs(temp) < 1e-8] = np.nan
                    signal = (sig - sig_min) / temp
                return 2 * signal - 1
            elif method == 'ts_rank':
                if isinstance(sig, pd.DataFrame):
                    signal = pd.DataFrame(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                          index=sig.index, columns=sig.columns)
                elif isinstance(sig, pd.Series):
                    signal = pd.Series(bk.move_rank(sig, window=window, min_count=int(window / 2), axis=0),
                                       index=sig.index, name=sig.name)
                return signal

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

    def __check_folder(self, folder_path):

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)


    def make_up_factors(self, start_date=None, end_date=None):
        if (not start_date is None) and (not end_date is None):
            self.factor_manager.update_factor_status_file(start_date, end_date)

        df_factor_status = self.factor_manager.get_factor_status()

        for i in set(df_factor_status.reset_index().set_index(['variety', 'data_type']).index):
            # if i[0] != 'IC':
            #     continue
            self.make_up_missing_factors(i[0], i[1])
            # time.sleep(10)

        if (not start_date is None) and (not end_date is None):
            self.factor_manager.update_factor_status_file(start_date, end_date)

    def make_up_factor_multi_day(self, factor, variety, data_center, date_list, ncore=20):
        pool = Pool(ncore)
        tasks = []

        for date in date_list:
            try:
                prepared_data, time_index = self.prepare_data(data_center,factor.days_past,date)
            except Exception as e:
                print(e, traceback.format_exc())
                assert False, 'Invalid prepared data!!!'

            tasks.append([pool.apply_async(self.run_factor_single_day, args=(factor,date,prepared_data,time_index)), factor.factor_name, variety, date])

        pool.close()

        factor_list = []
        for t,n,v,d in tasks:
            try:
                factor_list.append(t.get())
            except Exception as e:
                print(e,traceback.format_exc())

        pool.join()

        df_factor = pd.concat(factor_list)

        return df_factor


    def make_up_missing_factors(self, variety, data_type, ncore=20):
        factor_name_list = self.factor_manager.get_factor_list(variety, data_type)

        for factor_name in factor_name_list:
            print(factor_name, variety, data_type)
            date_list = self.factor_manager.get_missing_dates(variety, factor_name, data_type)
            factor = getattr(__import__('minute_factors.{}.{}'.format(variety, factor_name),
                                        fromlist=[factor_name]), factor_name)()

            if len(date_list) == 0: continue

            start_date = sorted(date_list)[0]
            end_date = sorted(date_list)[-1]

            data_center = DataCenter(variety, factor.data_type, factor.instrument_type, factor.data_dict, start_date, end_date,
                                     factor.days_past)

            try:
                df_factor_raw = pd.read_hdf('{}/{}/{}.h5'.format(self.factor_raw_path, variety, factor_name))
                df_factor_missing = self.make_up_factor_multi_day(factor,variety,data_center,date_list,ncore)

                df_factor_new = pd.concat([df_factor_raw,df_factor_missing],join='outer')
                df_factor_new = df_factor_new.loc[~df_factor_new.index.duplicated()].sort_index()

                if factor.normalize_type == 'ts_rank':
                    df_normalized_factor = (self.ts_rank(df_factor_new, factor.normalize_size) + 1) / 2
                elif factor.normalize_type == 'rolling_norm':
                    df_normalized_factor = self.rolling_norm(df_factor_new, factor.normalize_size)

                self.save_to_h5(df_factor_new, df_normalized_factor, variety, factor_name)

            except Exception as e:
                print(e, traceback.format_exc())

            return data_center



