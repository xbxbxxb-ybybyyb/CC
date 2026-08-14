# @Time : 2020/12/29 9:54
# @Author : Zhichen Lu
# @File : ModelNewLoading.py

from StrongStockModel.model.ModelBase.ModelBase import ModelBase
from dataApi.FixFactorRollPrepare import load_fix_data, feature_engineering
import os, time, gc
import pandas as pd
from StrongStockModel.conf.path_config import root_path
import numpy as np
from dataApi.tradeDate import get_date_range, get_recent_trade_date, get_pre_trade_date
import datetime


class ModelNewLoading(ModelBase):

    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=400):
        super().__init__(start, end, stock_pool, feature_address)
        # self.using_factor_list = pd.read_csv('/data/group/800319/junkData/StrongStock/external_data/实盘可支持Fix因子列表.csv').T.reset_index().T[0].tolist()
        # self.using_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')
        self.using_factor_list = pd.read_pickle('/data/group/800442/800319/strategy_local_path/available_factor_list.pkl')
        import shutil
        # shutil.copy('/data/group/800319/strategy_local_path3/实盘可支持Fix因子列表.csv','/data/group/800319/junkData/StrongStock/external_data/实盘可支持Fix因子列表.csv')
        self.eval_indicator = factor_eval_indicator
        # if factor_eval_indicator in ['ic_all_d','ic_all_t','ic_all_c']:
        #     self.factor_list = pd.read_pickle('/data/group/800319/strategy_local_path2/%s_400_factor_list.pkl'%factor_eval_indicator)
        #     self.factor_list.remove('HF_ForecastEPDelta40d')
        # else:
        #     self.factor_list = self.get_fix_factor_evaluation(factor_num)
        # self.factor_list = self.get_fix_factor_evaluation(self.eval_indicator)
        self.feature_address = feature_address
        self.date_list = get_date_range(start, end)
        # pd.to_pickle(self.factor_list, '/data/group/800319/strategy_local_path/%s_%d_factor_list.pkl'%(self.eval_indicator,factor_num))

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        # self.dp = FixFactorRollPrepare(start_date=train_idx[0], end_date=test_idx[-1], freq=7, model_time_len=1, factor_list=fix_factor_list,
        #                                load_address=self.feature_address)
        gc.collect()
        e = time.time()
        if train_idx[1] <= 20210812:

            factor_direction = pd.read_pickle('/data/group/800442/800319/strategy_local_path/factor_direction_before20210813.pkl')[fix_factor_list].values
            print('using factor direction old part neg')
        else:
            factor_direction = pd.read_pickle('/data/group/800442/800319/strategy_local_path/factor_direction.pkl')[fix_factor_list].values
            print('using factor direction all pos')
        print(f'min direction {factor_direction.min()}')
        # if train_idx[-1] <= self.dp.date_list[-1]:
        #     train_feature, train_label, nolimit_train, train_idx_date, train_idx_time, train_idx_code = self.dp.load_data(start_date=train_idx[0], end_date=train_idx[-1],
        #                                                                                                                   return_idx=True)
        # else:
        #     train_feature, train_label, nolimit_train, train_idx_date, train_idx_time, train_idx_code = self.dp.load_data(start_date=train_idx[0], end_date=self.dp.date_list[-1],
        #                                                                                                                   return_idx=True)
        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(train_idx[0], get_pre_trade_date(train_idx[-1]),
                                                                                                                      fix_factor_list)
        else:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(train_idx[0], train_idx[-1], fix_factor_list)
        train_feature, train_label, train_idx_date, train_idx_time, train_idx_code = feature_engineering(train_feature, train_label, nolimit_train, train_idx_date,
                                                                                                         train_idx_time, train_idx_code)
        train_feature = train_feature * factor_direction
        index_train = pd.MultiIndex.from_tuples(list(zip(train_idx_date.tolist(), train_idx_time.tolist(), train_idx_code.tolist())))
        train_feature, train_label = pd.DataFrame(train_feature, index=index_train, columns=fix_factor_list), pd.DataFrame({'actual_label': train_label}, index=index_train)

        # test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time = load_fix_data(test_idx[0], test_idx[-1], fix_factor_list)
        # test_feature, test_label, test_idx_date, test_idx_time, test_idx_code = feature_engineering(test_feature, test_label, test_nolimit, test_idx_date,
        #                                                                                             test_idx_time,
        #                                                                                             test_idx_code)

        today = int(datetime.date.today().strftime('%Y%m%d'))
        today = get_recent_trade_date(today)
        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            test_feature, test_label = pd.DataFrame(columns=fix_factor_list), pd.DataFrame(columns=fix_factor_list)
        else:
            if test_idx[-1] >= today:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time = load_fix_data(start_date=test_idx[0], end_date=get_pre_trade_date(today),
                                                                                                                    factor_list=fix_factor_list, return_idx=True)
            else:
                test_feature, test_label, test_nolimit, test_idx_date, test_idx_code, test_idx_time = load_fix_data(start_date=test_idx[0], end_date=test_idx[-1],
                                                                                                                    factor_list=fix_factor_list, return_idx=True)
            # test_label = np.concatenate((test_label, np.zeros((test_feature.shape[1] - test_label.shape[0], 7))))
            test_nolimit[np.isnan(test_label)] = True
            test_label[np.isnan(test_label)] = 0
            # test_nolimit = np.concatenate((test_nolimit, np.ones((test_feature.shape[1] - test_nolimit.shape[0], 7)) > 0))
            test_feature, test_label, test_idx_date, test_idx_time, test_idx_code = feature_engineering(test_feature, test_label, test_nolimit, test_idx_date,
                                                                                                        test_idx_time,
                                                                                                        test_idx_code)

            test_feature = test_feature * factor_direction
            index_test = pd.MultiIndex.from_tuples(list(zip(test_idx_date.tolist(), test_idx_time.tolist(), test_idx_code.tolist())))

            test_feature, test_label = pd.DataFrame(test_feature, index=index_test, columns=fix_factor_list), pd.DataFrame({'actual_label': test_label}, index=index_test)

        return train_feature, train_label, test_feature, test_label, time.time() - e

    def get_fix_factor_evaluation(self, num):
        if self.eval_indicator == 'intersection':
            return self.get_fix_factor_evaluation_intersection(num)
        elif self.eval_indicator == 'union':
            return self.get_fix_factor_evaluation_union(num)
        elif self.eval_indicator == 'std_adjusted':
            return self.get_factor_std()
        factor_evaluation = pd.read_excel(root_path + '/external_data/后疫情时代的因子选择.xlsx').set_index('name')
        inter_col = list(set(factor_evaluation.index).intersection(set(self.using_factor_list)))
        factor_list = factor_evaluation.loc[inter_col, self.eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:num]
        return sorted(factor_list)

    def get_factor_std(self):
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_eval_path = '/data/group/800319/FixFactorTestResult/'
        eval_res_list = os.listdir(factor_eval_path)
        eval_res_list = list(set(eval_res_list).intersection(set(sample.columns)))
        barly_ret = []
        for each in eval_res_list:
            temp_res = pd.read_pickle(factor_eval_path + each)
            barly_ret.append([each] + temp_res['dc_t_all_ret'].tolist())
        check = pd.DataFrame(barly_ret).set_index(0)
        check['std'], check['mean'] = check.std(axis=1), check.mean(axis=1)
        check['adjusted_std'] = (check['std'] / check['mean']).apply(abs)
        factor_evaluation = pd.read_excel(root_path + '/external_data/后疫情时代的因子选择.xlsx').set_index('name')
        check[['ic_all_t', 'ic_all_d', 'ic_all_c', 'ic_all_dtc']] = abs(factor_evaluation[['ic_all_t', 'ic_all_d', 'ic_all_c', 'ic_all_dtc']])
        check['t_to_std'] = check['ic_all_t'] / check['adjusted_std']
        check['c_to_std'] = check['ic_all_c'] / check['adjusted_std']
        check['d_to_std'] = check['ic_all_d'] / check['adjusted_std']
        check['score'] = check[['t_to_std', 'c_to_std', 'd_to_std']].mean(axis=1)

        selected = check.sort_values('score', ascending=False)[:500]
        selected = selected[((selected['ic_all_t'] > check['ic_all_t'].quantile(0.8)) +
                             (selected['ic_all_c'] > check['ic_all_c'].quantile(0.8)) +
                             (selected['ic_all_d'] > check['ic_all_d'].quantile(0.8))) > 0]
        return selected.index.tolist()

    def get_fix_factor_evaluation_union(self, num):
        factor_evaluation = pd.read_excel(root_path + '/external_data/后疫情时代的因子选择.xlsx').set_index('name')
        inter_col = list(set(factor_evaluation.index).intersection(set(self.using_factor_list)))
        for individual_num in range(10, num + 1):
            factor_list = {}
            for eval_indicator in ['ic_all_t', 'ic_all_c', 'ic_all_d']:
                factor_list[eval_indicator] = factor_evaluation.loc[inter_col, eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:individual_num]
            factor_set = set(factor_list['ic_all_t']).union(set(factor_list['ic_all_c'])).union(set(factor_list['ic_all_d']))
            factor_num = len(factor_set)
            if factor_num >= num:
                print('factor_num', factor_num)
                break
        return list(factor_set)

    def get_fix_factor_evaluation_intersection(self, num):
        sample = pd.read_hdf(self.feature_address + '20150309.h5', '20150309')
        factor_evaluation = pd.read_excel(root_path + '/external_data/后疫情时代的因子选择.xlsx').set_index('name')
        inter_col = list(set(factor_evaluation.index).intersection(set(self.using_factor_list)))
        for individual_num in range(num, num * 2):
            factor_list = {}
            for eval_indicator in ['ic_all_t', 'ic_all_c', 'ic_all_d']:
                factor_list[eval_indicator] = factor_evaluation.loc[inter_col, eval_indicator].apply(abs).sort_values(ascending=False).index.tolist()[:individual_num]
            factor_set = set(factor_list['ic_all_t']).intersection(set(factor_list['ic_all_c'])).intersection(set(factor_list['ic_all_d']))
            factor_num = len(factor_set)
            if factor_num >= num:
                print('factor_num', factor_num)
                break
        return list(factor_set)
