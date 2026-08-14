# @Time : 2022/2/17 9:14
# @Author : Zhichen Lu
# @File : NonFixSample.py

from StrongStockModel.model.ModelBase.ModelNonFixWindow import ModelNonFixWindow
from dataApi.tradeDate import get_date_range
import configparser
import pandas as pd

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


class SubClass(ModelNonFixWindow):

    def __init__(self, start, end, stock_pool, feature_address, label_path, future_bar_num, **param):
        super().__init__(start, end, stock_pool, feature_address, label_path, future_bar_num)

    def train_model(self, X_train, y_train, params, end_date=None):
        date_list = get_date_range(X_train.index[0][0], end_date)
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9, -11]]
        date_list = list(set(date_list) - set(val_date))
        y_train['actual_label']  # 现在y_train有两个columns "actual_label" 和"1_day_label",请使用"actual_label"训练


def main_window_search(i, future_bar_num):
    train_period = 200
    test_period = 10
    factor_num = 400
    train_start, train_end, test_start, test_end = para_list[i][1]
    md = SubClass(train_start, test_end, None, future_bar_num=future_bar_num)
    res = md.rolling_train_and_predict(period=train_period, predict_period=test_period, factor_nums=factor_num)
    pd.to_pickle(res, '')


idx_list = list(range(134))[24:]  # [::-1]
for f_bar in list(range(1, 9)):
    for i in idx_list:
        main_window_search(i, future_bar_num=f_bar)
