# coding: utf-8
# Author：fengchi863
# Date ：2023/3/17 9:28

"""
因子筛选方案V1：采用随机森林进行多区间筛选
"""
import sys
sys.path.append('/data/user/015614/Lucien')
from Zeus.Europa.v4_0_46.path_conf import *
import pandas as pd
import numpy as np
from tscv import GapWalkForward
from sklearn.ensemble import RandomForestRegressor
from LucienUtil.FileUtil import FileUtil
from LucienUtil.SpeedUtil import SpeedUtil
from tqdm import tqdm
import time
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)

class FactorSelect:
    def __init__(self, start_date, end_date):
        self.X_train, self.y_train = None, None
        self.start_date, self.end_date = start_date, end_date
        self.label = 'label_pct_graded'
        self.strategy_name = 'Europa'
        self.version = 'v4_0_46'

        self.X, self.y = None, None
        self.train_months = None
        self.model = None
        self.get_dataset(data_all_fpath)

    def get_dataset(self, path):
        samples = pd.read_pickle(path)
        X = samples[filter(lambda x: x.find('label'), samples.columns.tolist())]
        X = X.dropna(how='any', axis=0)
        X = samples.loc[X.index]

        # TODO：更新了收益文件，也就是更新了标签
        # y = pd.read_hdf(profit_data_fpath)
        y = samples[[self.label]]
        y.columns = [self.label]

        y = y.reindex(index=X.index)

        y = y.drop(np.isnan(y)[self.label][np.isnan(y)[self.label]].index)
        X = X.reindex(index=y.index)

        factor_info = pd.read_excel(eval(f'factor_score_{self.end_date}_fpath'), index_col=0).set_index('factor_name')
        factor_info = factor_info[~factor_info['factor_type'].isin(['other', 'label'])]
        factor_info = factor_info[factor_info['factor_owner'] != 'emotion']
        factor_info = factor_info[factor_info['lowCost'] == 1]
        factor_list = factor_info.index.tolist()
        X = X[factor_list]

        self.X = X
        self.y = y

    def get_train_data(self):
        X_copy = self.X.copy()
        y_copy = self.y.copy()
        X_copy = X_copy.drop(X_copy.filter(regex='label*').columns.tolist(), axis=1)
        y_copy = y_copy.reindex(index=X_copy.index)

        X_copy['trade_date'] = X_copy.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()
        y_copy['trade_date'] = y_copy.index.get_level_values(0).strftime('%Y%m%d').astype(int).tolist()

        X_train = X_copy.query(f'trade_date >= {self.start_date} & trade_date <= {self.end_date}')
        y_train = y_copy.query(f'trade_date >= {self.start_date} & trade_date <= {self.end_date}')

        y_train = y_train[[self.label]]

        self.train_months = list(sorted(set((X_train['trade_date'] // 100).tolist())))

        X_train = X_train.drop('trade_date', axis=1)

        self.X_train, self.y_train = X_train, y_train

    def train_model(self, X_train, y_train):
        rf = RandomForestRegressor(n_estimators=100, random_state=2023, n_jobs=-1, max_depth=3)
        rf.fit(X_train, y_train)
        self.model = rf

    def kcv_factor_imptc_eval(self):
        gap_kfold = GapWalkForward(n_splits=10, max_train_size=36, test_size=0)
        factor_imptc_df = pd.DataFrame(index=self.X_train.columns)
        for idx, (train_month_arr, _) in enumerate(gap_kfold.split(self.train_months)):
            t1 = time.time()
            train_month_list = list(np.array(self.train_months)[train_month_arr])
            X_train_all = self.X_train.copy()
            y_train_all = self.y_train.copy()
            X_train_all['trade_month'] = X_train_all.index.get_level_values(0).strftime('%Y%m').astype(int)
            y_train_all['trade_month'] = y_train_all.index.get_level_values(0).strftime('%Y%m').astype(int)
            X_train = X_train_all.query(f'trade_month in {train_month_list}').drop('trade_month', axis=1)
            y_train = y_train_all.query(f'trade_month in {train_month_list}').drop('trade_month', axis=1)
            self.train_model(X_train, y_train.values.ravel())
            factor_imptc_df.loc[:, idx] = self.model.feature_importances_

            time_cost = round(time.time() - t1, 2)
            print(f'当前第{idx}折，耗时{time_cost}秒')
        return factor_imptc_df

    def launch(self):
        self.get_train_data()
        factor_imptc_df = self.kcv_factor_imptc_eval()
        return factor_imptc_df


if __name__ == '__main__':
    period_list = ['period1', 'period2', 'period3']
    # period_list = ['period1']

    def launch_1period(period):
        period = period[0]
        train_start_date = date_config[period]['train_start_date']
        train_end_date = date_config[period]['valid_end_date']

        FS = FactorSelect(train_start_date, train_end_date)
        stats = pd.DataFrame()
        factor_imptc_df = FS.launch()
        # 中间结果
        # FileUtil.save_df2pkl(factor_imptc_df, factor_select_path + f'{FS.strategy_name}/{FS.version}/', f'tmp_rf_cv_score_{period}.pkl')
        # FileUtil.save_df2pkl(factor_imptc_df, factor_select_path + f'{FS.strategy_name}/{FS.version}/', f'tmp_rf_cv_score_afterZ_{period}.pkl')

        # 进行筛选
        check = factor_imptc_df.rank(axis=0, method='min') - 1
        stats['times'] = (check > 0).sum(axis=1)
        stats['mean'] = check.mean(axis=1)
        stats = stats.sort_values('times', ascending=False)
        selected_factor_list = stats.query(f'mean >= 300').index.tolist()
        print(f'{period}筛选出rffs因子数量{len(selected_factor_list)}个')
        FileUtil.save_list2pkl(selected_factor_list, factor_select_path + f'{FS.strategy_name}/{FS.version}/', f'rffs_{period}.pkl')

    # SpeedUtil.multiprocess(len(period_list), launch_1period, period_list)
    launch_1period(['period5'])
