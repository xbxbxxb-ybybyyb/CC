import os
import shutil
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from function_tools import *


class FactorManager(object):

    def __init__(self):

        OUTER_ROOT_PATH = os.path.dirname(os.path.dirname(__file__))

        self.variety_list = ['IC','IF']
        # self.multi_variety_list = ['IH_IC','IC_IH','IF_IC','IC_IF','IH_IF','IF_IH']

        self.__factor_root_path = '{}/data_center/factor_data'.format(OUTER_ROOT_PATH)
        self.__factor_status_path = '/data/user/012913/IndexFuture/research_data_center/factor_data/factor_status.pkl'
        self.__factor_file_path = '{}/factor_framework/minute_factors'.format(OUTER_ROOT_PATH)

    def get_factor_status(self):
        return pd.read_pickle(self.__factor_status_path)

    def delete_factor(self, factor_name, variety, temp_root_path=''):

        if temp_root_path == '':
            file_path = '{}/{}/{}.py'.format(self.__factor_file_path, variety, factor_name)
        else:
            file_path = '{}/{}/{}.py'.format(temp_root_path, variety, factor_name)

        df_factor_status = self.get_factor_status()

        norm_path = '{}/{}/{}/{}.h5'.format(self.__factor_root_path, 'minute_norm', variety, factor_name)
        raw_path = '{}/{}/{}/{}.h5'.format(self.__factor_root_path, 'minute_raw', variety, factor_name)

        if os.path.exists(norm_path):
            os.remove(norm_path)

        if os.path.exists(raw_path):
            os.remove(raw_path)

        if os.path.exists(file_path):
            os.remove(file_path)

        if (variety,factor_name) in df_factor_status.index:
            df_factor_status.drop(index=(variety,factor_name),inplace=True)

        df_factor_status.to_pickle(self.__factor_status_path)

    def add_factor_info(self, variety, factor_name, start_date, end_date, data_type, is_criteria_1=False, is_criteria_2=False, is_candidate=False):

        assert not (is_criteria_2 == True and is_candidate == True), "A candidate cannot meet criteria 2!!!"
        df_factor_status = self.get_factor_status()
        date_list = self.__get_trading_days(start_date,end_date)

        factor_info_dict = self.__get_factor_info(variety, factor_name, data_type, date_list, is_criteria_1, is_criteria_2, is_candidate)

        if factor_info_dict is None:
            print('{} does not exist, please check again!'.format(factor_name))
            return

        df_new_factor = pd.DataFrame.from_dict(factor_info_dict).set_index(['variety','factor_name'])

        if (variety, factor_name) in df_factor_status.index:
            print('{}_{}_{} already exists! Please rename or check again!'.format(variety,factor_name,data_type))

            return

        df_factor_status = df_factor_status.append(df_new_factor).sort_index()

        df_factor_status.to_pickle(self.__factor_status_path)

        print('{}_{}_{} is passed.'.format(variety,factor_name,data_type))

    def update_factor_info(self, variety, factor_name, data_type, start_date, end_date, is_criteria_1, is_criteria_2, is_candidate):

        df_factor_status = pd.read_pickle(self.__factor_status_path)
        date_list = self.__get_trading_days(start_date, end_date)

        df_new_factor = pd.DataFrame.from_dict(
            self.__get_factor_info(variety, factor_name, data_type, date_list, is_criteria_1, is_criteria_2, is_candidate)).set_index(['variety','factor_name'])

        if (variety, factor_name) in df_factor_status.index:

            df_factor_status.drop(index=(variety, factor_name), inplace=True)

            df_factor_status = df_factor_status.append(df_new_factor).sort_index()

            df_factor_status.to_pickle(self.__factor_status_path)

            print('{}_{}_{} is updated.'.format(variety, factor_name, data_type))
        else:
            print('{}_{}_{} does not exist!'.format(variety, factor_name, data_type))

    def update_factor_status_file(self, start_date, end_date):

        df_factor_status = pd.read_pickle(self.__factor_status_path)
        # date_list = FactorData().tradingday(start_date, end_date)
        date_list = get_trading_days(start_date, end_date)
        df_factor_info_list = []

        for i in df_factor_status.index:
            df_factor_info = pd.DataFrame.from_dict(self.__get_factor_info(i[0], i[1], df_factor_status.loc[i]['data_type'], date_list, df_factor_status.loc[i]['is_criteria_1'], df_factor_status.loc[i]['is_criteria_2'], df_factor_status.loc[i]['is_candidate'])).set_index(['variety','factor_name'])
            if not df_factor_info is None:
                df_factor_info_list.append(df_factor_info)

        df_new_factor_status = pd.concat(df_factor_info_list)

        df_new_factor_status.to_pickle(self.__factor_status_path)
        print('factor_status.pkl is updated.')

    def __get_factor_info(self, variety, factor_name, data_type, date_list, is_criteria_1=True, is_criteria_2=False, is_candidate=False):

        factor_path = '{}/{}/{}/{}.h5'.format(self.__factor_root_path, 'minute_raw', variety, factor_name)
        existed_date_list = []

        if not os.path.exists(factor_path):
            existed_date_list = []
        else:
            df_factor = pd.read_hdf(factor_path)
            existed_date_list = list(np.unique([i.strftime('%Y%m%d') for i in df_factor.index.date]))

        return {'variety':variety,'factor_name':factor_name,'data_type':data_type,'missing_dates':[sorted(set(date_list).difference(set(existed_date_list)))],'is_criteria_1':is_criteria_1, 'is_criteria_2':is_criteria_2,'is_candidate':is_candidate}

    def get_factor_list(self, variety, data_type):

        df_factor_status = pd.read_pickle(self.__factor_status_path)
        df_factor_by_variety = df_factor_status.loc[variety]

        return list(df_factor_by_variety[df_factor_by_variety['data_type'] == data_type].index)

    def get_factor_list_by_candidate(self, variety, data_type, is_candidate):
        df_factor_status = pd.read_pickle(self.__factor_status_path)
        df_factor_by_variety = df_factor_status.loc[variety]
        df_factor_by_data_type = df_factor_by_variety[(df_factor_by_variety['data_type'] == data_type)]

        return list(df_factor_by_data_type[df_factor_by_data_type['is_candidate'] == is_candidate].index)

    def get_factor_list_by_criteria(self, variety, data_type, is_criteria_1=None, is_criteria_2=None):

        df_factor_status = pd.read_pickle(self.__factor_status_path)
        df_factor_by_variety = df_factor_status.loc[variety]

        criteria_condition = pd.Series([True for i in range(len(df_factor_by_variety))],index=df_factor_by_variety.index)

        if not is_criteria_1 is None:
            criteria_condition = criteria_condition & (df_factor_by_variety['is_criteria_1'] == is_criteria_1)

        if not is_criteria_2 is None:
            criteria_condition = criteria_condition & (df_factor_by_variety['is_criteria_2'] == is_criteria_2)


        return list(df_factor_by_variety[(df_factor_by_variety['data_type'] == data_type) & criteria_condition].index)


    def get_missing_dates(self, variety, factor_name, data_type):
        df_factor_status = pd.read_pickle(self.__factor_status_path)
        df_factor = df_factor_status[df_factor_status['data_type'] == data_type].loc[(variety, factor_name)]

        return df_factor['missing_dates']

    def __get_trading_days(self, start_date, end_date):
        # return sorted(FactorData().tradingday(start_date, end_date))
        return sorted(get_trading_days(start_date, end_date))















