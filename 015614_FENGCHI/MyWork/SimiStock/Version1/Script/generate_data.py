# coding: utf-8
# Author：fengchi863
# Date ：2022/4/16 16:56

"""
把2020年的样本换到2018年
把2017年的样本换到2019年
"""

from SimiStock.config.path_config import *
from SimiStock.SimiStockGenerator.util import util
import pandas as pd
import numpy as np
from SimiStock.dataApi import tradeDate
np.random.seed(2022)


def rand_date(start_date, end_date):
    date_list = tradeDate.get_date_range(start_date, end_date)
    date = date_list[np.random.randint(len(date_list))]
    return date

# 生成第一份替换的数据
check = pd.read_pickle(data_path + 'block_data_95.pkl')
check1 = check.query('20200101 <= 交易日期 <= 20201231')
check1['交易日期'] = check['交易日期'].apply(lambda x: rand_date(20180101, 20181231))
util.save_df2pkl(check1, data_path, '2020to2018_block_data_95.pkl')

# 生成第二份替换的数据
check2 = check.query('20170101 <= 交易日期 <= 20171231')
check2['交易日期'] = check['交易日期'].apply(lambda x: rand_date(20190101, 20191231))
util.save_df2pkl(check2, data_path, '2017to2019_block_data_95.pkl')