from factor_manager import FactorManager
from task_runner import TaskRunner
from data_center import DataCenter
from factor_evaluator import FactorEvaluator
from function_tools import *

import datetime as dt
import pandas as pd
import os
import shutil

class FactorVerification(object):

    def __init__(self):

        self.author_list = ['liudy','liuz','shentq','hefj','lixr','jinpx','All']
        self.variety_list = ['IC','IF']

        self.ROOT_PATH = os.path.dirname(os.path.dirname(__file__))

        self.factor_root_path = '{}/data_center/factor_data/minute_norm'.format(self.ROOT_PATH)
        self.submitted_path = '{}/factor_framework/factors_submitted'.format(self.ROOT_PATH)

        self.factor_start_date = '20180201'
        self.factor_end_date = '20200630'

        self.data_center_start_date = '20180101'
        self.data_center_end_date = '20200630'

        self.init_date = '20160201'

        self.task_runner = TaskRunner()
        self.factor_manager = FactorManager()
        self.factor_evaluator = FactorEvaluator()

    def calc_factors_by_author(self, author_name, ncore=20):

        assert author_name in self.author_list, 'Invalid author!!!'

        for v in self.variety_list:
            factor_name_list = [i.split('.')[0] for i in os.listdir('{}/{}/{}'.format(self.submitted_path,author_name,v)) if not '__' in i]

            if len(factor_name_list) == 0: continue

            for factor_name in factor_name_list:
                print('Start calculating {} {} ...'.format(factor_name,v))
                factor = getattr(__import__('{}.{}.{}.{}'.format('factors_submitted',author_name,v,factor_name), fromlist=[factor_name]), factor_name)()
                data_center = DataCenter(v, factor.data_type, factor.instrument_type, factor.data_dict, self.data_center_start_date, self.data_center_end_date, factor.days_past)

                df_factor, df_normalized_factor = self.task_runner.run_factor_multi_day(factor, v, data_center, self.factor_start_date, self.factor_end_date)


    def verify_factors_by_author(self, author_name, variety):

        assert author_name in self.author_list, 'Invalid author!!!'

        print("Start verifying factors' stats...")

        factor_name_list = [i.split('.')[0] for i in os.listdir('{}/{}/{}'.format(self.submitted_path,author_name,variety)) if not '__' in i]

        result_dict = dict()

        for factor_name in factor_name_list:
            flag,sharpe,ppd = self.factor_evaluator.calc_statistic_by_factor_name(factor_name, variety, self.factor_start_date, self.factor_end_date, groupnum=10)
            factor = getattr(__import__('{}.{}.{}.{}'.format('factors_submitted',author_name,variety,factor_name), fromlist=[factor_name]), factor_name)()
            result_dict[factor_name] = {'data_type':factor.data_type,'flag':flag,'sharpe':sharpe,'profit_per_deal':ppd}

        df_max_corr = self.factor_evaluator.calc_tsrank_max_corr_by_name_list(factor_name_list, variety, self.factor_start_date, self.factor_end_date)

        # if not all(df_max_corr.values):
        #     is_passed = False

        df_passed = pd.concat([pd.DataFrame.from_dict(result_dict).T, df_max_corr], axis=1)

        is_passed = all(df_passed['flag']) and all(df_passed['is_corr_passed'])

        # for i in df_passed.index:
        #     self.update_factor_passed_info(author_name,i,df_passed.loc[i]['data_type'],df_passed.loc[i]['stats'],df_passed.loc[i]['max_corr'])

        if is_passed:
            print('All factors submitted are passed!!!')
        else:
            print('Some factors submitted are not passed!!!')

        return df_passed

    def delete_factors_by_factor_name_list(self, author_name, delete_name_list, variety):

        assert author_name in self.author_list, 'Invalid author!!!'

        for factor_name in delete_name_list:
            self.factor_manager.delete_factor(self, factor_name, variety, temp_root_path='{}/{}'.format(self.submitted_path, author_name))
            print('{} has been deleted'.format(factor_name))

    def add_factors_by_author(self, author_name, variety, is_criteria_1, is_criteria_2):

        assert author_name in self.author_list, 'Invalid author!!!'
        factor_name_list = [i.split('.')[0] for i in os.listdir('{}/{}/{}'.format(self.submitted_path,author_name,variety)) if not '__' in i]

        for factor_name in factor_name_list:
            factor = getattr(__import__('{}.{}.{}.{}'.format('factors_submitted', author_name, variety, factor_name),
                                        fromlist=[factor_name]), factor_name)()
            self.factor_manager.add_factor_info(variety, factor, factor.data_type, self.factor_start_date, self.factor_end_date, is_criteria_1, is_criteria_2)

    # def add_verified_factors_into_store_by_author(self, author_name, standard_variety=['IC','IC_IH']):
    #
    #     self.calc_factors_by_author(author_name)
    #
    #     if not self.verify_factors_by_author(author_name,standard_variety):
    #         # self.delete_factors_by_author(author_name)
    #         return
    #     else:
    #         self.add_factors_by_author(author_name)
    #         self.move_factor_file_by_author(author_name)

    # def clear_weekly_submitted_folders(self):
    #     for user in os.listdir(self.submitted_path):
    #         for data_type_folder in os.listdir('{}/{}'.format(self.submitted_path,user)):
    #             for factor_file in os.listdir('{}/{}/{}'.format(self.submitted_path,user,data_type_folder)):
    #                 if os.path.isfile('{}/{}/{}/{}'.format(self.submitted_path,user,data_type_folder,factor_file)):
    #                     os.remove('{}/{}/{}/{}'.format(self.submitted_path,user,data_type_folder,factor_file))
    #     for user in os.listdir(self.root_path):
    #         for data_type_folder in os.listdir('{}/{}'.format(self.root_path,user)):
    #             for factor_file in os.listdir('{}/{}/{}'.format(self.root_path,user,data_type_folder)):
    #                 if os.path.isfile('{}/{}/{}/{}'.format(self.root_path,user,data_type_folder,factor_file)):
    #                     os.remove('{}/{}/{}/{}'.format(self.root_path,user,data_type_folder,factor_file))

    def update_new_factors_data(self):
        today = dt.datetime.today()
        oneday = dt.timedelta(days=1)
        yesterday = today - oneday

        end_date = yesterday.strftime(format='%Y%m%d')

        self.task_runner.make_up_factors(self.init_date, end_date)

    # def move_factor_file_by_author(self, author_name):
    #
    #     assert author_name in self.author_list, 'Invalid author!!!'
    #
    #     for folder in self.data_type_dict.keys():
    #         for i in os.listdir('{}/{}/{}'.format(self.root_path, author_name, folder)):
    #             current_file = '{}/{}/{}/{}'.format(self.root_path, author_name, folder, i)
    #             destiantion_file = '{}/{}/{}'.format(self.destination_root_path, folder, i)
    #             if os.path.isfile(current_file):
    #                 shutil.move(current_file, destiantion_file)
    #                 print('{} has been moved.'.format(i))














