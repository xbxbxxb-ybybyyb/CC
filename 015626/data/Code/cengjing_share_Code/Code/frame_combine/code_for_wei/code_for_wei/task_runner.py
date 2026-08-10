from data_center import DataCenter
from data_center_store import DataCenterStore
from factor_manager import FactorManager

from xquant.futuredata import FutureData
import os
import traceback
import pandas as pd
import time

import bottleneck as bk

from multiprocessing import Pool
from get_data import *

from data_player import DataPlayer

class TaskRunner(object):

    def __init__(self):

        OUTER_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))
        # OUTER_ROOT_PATH = '/data/user/015615/IndexFuture'

        self.__factor_root_path = '{}/data_center/factor_data/temp_pickles'.format(OUTER_ROOT_PATH)
        self.__factor_name_path = '{}/factor_framework/factor_name_files/factor_name_list.csv'.format(OUTER_ROOT_PATH)
        self.__minute_factor_root_path = '{}/data_center/factor_data/minute_pickles'.format(OUTER_ROOT_PATH)
        self.__minute_factor_name_path = '{}/factor_framework/factor_name_files/minute_factor_name_list.xlsx'.format(OUTER_ROOT_PATH)
        self.__10s_factor_root_path = '{}/data_center/factor_data/10s_pickles'.format(OUTER_ROOT_PATH)
        self.__10s_factor_name_path = '{}/factor_framework/factor_name_files/10s_factor_name_list.xlsx'.format(OUTER_ROOT_PATH)
        self.__minute_index_stock_root_path = '{}/data_center/factor_data/minute_index_pickles'.format(OUTER_ROOT_PATH)
        self.__minute_index_stock_factor_name_path = '{}/factor_framework/factor_name_files/minute_index_factor_name_list.xlsx'.format(OUTER_ROOT_PATH)
        self.__minute_multi_factor_root_path = '{}/data_center/factor_data/multi_minute_pickles'.format(OUTER_ROOT_PATH)

        self.__factordata_folder_path = '{}/data_center/factor_data/'.format(OUTER_ROOT_PATH,)


        self.factor_manager = FactorManager()
        self.data_type_dict = {'1T': 'minute_pickles',
                       'minute_index': 'minute_index_pickles',
                       'multi_minute': 'multi_minute_pickles',
                       '10s': '10s_pickles',
                       'tick': 'temp_pickles'}


    def update_daily_factors(self, variety, date, ncore=20):
        factor_name_list = pd.read_csv(self.__factor_name_path)['factor_name'].tolist()[-17:]
        print(factor_name_list)

        pool = Pool(ncore)
        tasks = []

        for i in factor_name_list:
            tasks.append([pool.apply_async(self.run_factor_single_day,args=(i,variety,date,)),i,variety,date])

        pool.close()

        for t,n,v,d in tasks:
            try:
                self.save_factor_single_day(t.get(),n,v,d)
            except Exception as e:
                print(e,traceback.format_exc())

        pool.join()

        return

    def update_multi_day_factors(self, variety, start_date, end_date, freq, ncore=20, tsrank_start_date = None):

        if tsrank_start_date is None:
            tsrank_start_date= '20180201'

        if freq == '1T':
            # factor_name_list = pd.read_excel(self.__minute_factor_name_path)['factor_name'].tolist()
            factor_name_list = self.factor_manager.get_factor_list(variety, freq)
        elif freq == 'tick':
            factor_name_list = pd.read_csv(self.__factor_name_path)['factor_name'].tolist()
        elif freq == '10s':
            # factor_name_list = pd.read_excel(self.__10s_factor_name_path)['factor_name'].tolist()
            factor_name_list = ['TenSecTreasureReturn3Ma','TenSecTreasureReturn10Ma','TenSecTreasureReturn20Ma','TenSecTreasureReturn40Ma','TenSecTreasureReturn100Ma',\
                                'TenSecVolGrowth3Ma','TenSecVolGrowth10Ma','TenSecVolGrowth20Ma','TenSecVolGrowth40Ma','TenSecVolGrowth100Ma']
        # factor_name_list = ['Treasure20Return','Treasure40Return','Treasure100Return','Treasure200Return']
        elif freq == 'minute_index':
            # factor_name_list = pd.read_excel(self.__minute_index_stock_factor_name_path)['factor_name'].tolist()
            factor_name_list = self.factor_manager.get_factor_list(variety, freq)
            # factor_name_list = ['MinuteIndexCloseVolCorr10Mean','MinuteIndexCloseVolCorr10WeightedMean',
            #                     'MinuteIndexRtnVolCorr10Mean','MinuteIndexRtnVolCorr10WeightedMean',
            #                     'MinuteIndexRtnSharpe10WeightedMean','MinuteIndexRtnSkew10WeightedMean',
            #                     'MinuteIndexVolGrowthSharpeDiff10WeightedMean','MinuteIndexWeightedSkew']
            # factor_name_list = ['MinuteIndexRtnSharpe10WeightedMean']
        elif freq == 'multi_minute':
            factor_name_list = self.factor_manager.get_factor_list(variety, freq)

        print(factor_name_list)
        tasks = []
        
        date_list = self.__get_available_dates(start_date, end_date)
        pool = Pool(ncore)
        
        for name in factor_name_list:
            for date in date_list:
                tasks.append([pool.apply_async(self.run_factor_single_day,args=(name,variety,date,freq)),name,variety,date])
        
        pool.close()
        
        for t, n, v, d in tasks:
            try:
                self.save_factor_single_day(t.get(), n, v, d, freq)
            except Exception as e:
                print(e, traceback.format_exc())
        
        pool.join()

        tasks = []
        with Pool(ncore) as pool:
            for factor_name in factor_name_list:
                tasks.append(pool.apply_async(self.calc_factor_tsrank, args=(factor_name, freq, variety, end_date)))
            for t in tasks:
                t.get()
        # for factor_name in factor_name_list:
        #     self.calc_factor_tsrank(factor_name,freq,variety,end_date)
            # self.generate_tsrank_df_by_date(factor_name,variety,end_date,freq)

        return

    def prepare_data(self, data_center, days_past, date):

        assert isinstance(days_past, int) and days_past >= 0, 'Invalid input of days_past!!!'
        assert data_center.get_data_type() in ['Future', 'IndexStock'], 'Invalid input of data type!!!'

        date_list = sorted(get_trading_days('19900101', date)[-days_past - 1:])

        assert len(date_list) > 0, 'No data to prepare!'

        if data_center.get_data_type() == 'IndexStock':
            index_code = data_center.get_index_code()
            stock_list = list(get_stock_weights(index_code, date_list[-1]).index)
            stock_dict = data_center.get_stock_data()
            prepared_data = {}

            for i, v in stock_dict.items():
                prepared_data[i] = v.loc[date_list[0]:date_list[-1]][stock_list]
                today_time_index = prepared_data[i].loc[date].index

        elif data_center.get_data_type() == 'Future':
            data_list = []
            if data_center.get_future_data() is not None:
                data_list.append(data_center.get_future_data().loc[date_list[0]:date_list[-1]])
            if data_center.get_index_data() is not None:
                data_list.append(data_center.get_index_data().loc[date_list[0]:date_list[-1]])
            if data_center.get_other_instrument_data() is not None:
                data_list.append(data_center.get_other_instrument_data().loc[date_list[0]:date_list[-1]])
            if data_center.get_other_variety_data() is not None:
                data_list.append(data_center.get_other_variety_data().loc[date_list[0]:date_list[-1]])

            prepared_data = pd.concat(data_list, axis=1)
            today_time_index = prepared_data.loc[date].index

        return prepared_data, today_time_index

    def run_factor_single_day(self, factor, date, prepared_data=None, time_index=None, data_center=None):
        print(date)
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

        # if tsrank_start_date is None:
        #     tsrank_start_date = '20180201'

        date_list = self.__get_available_dates(start_date, end_date)
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

        assert factor.normalize_type in ['ts_rank','XXX']
        assert isinstance(factor.normalize_size,int), 'The normalized size of factor should be integer!!!'

        df_normalized_factor = None

        if factor.normalize_type == 'ts_rank':
            # try:
            df_normalized_factor = self.normalize_by_tsrank(df_factor, factor.normalize_size)
            # except:
            #     pass

        return df_factor, df_normalized_factor

    def normalize_by_tsrank(self, df_result, normalize_size):
        print('{} Tsrank Lookback Period: {}'.format(df_result.columns[0], normalize_size))
        df_result.fillna(method='ffill')
        df_factor_tsrank = pd.DataFrame((bk.move_rank(df_result[df_result.columns[0]].values,normalize_size) + 1) / 2, columns=df_result.columns,index=df_result.index)
        return df_factor_tsrank

    def __check_folder(self, folder_path):

        if not os.path.exists(folder_path):
            os.mkdir(folder_path)

    def __get_available_dates(self, start_date, end_date):

        # return FactorData().tradingday(start_date, end_date)
        return get_trading_days(start_date, end_date)




