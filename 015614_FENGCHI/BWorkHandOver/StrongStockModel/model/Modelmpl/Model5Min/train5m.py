

from StrongStockModel.model.Modelmpl.Model5Min.BaseModel5M import Factor5MinLoader

import numpy as np
import pandas as pd
import gc
import os

from xquant.xqutils.helper import link
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


os.environ["CUDA_VISIBLE_DEVICES"] = "-1"

factor_list = pd.read_excel('/data/group/800319/HFfactor/DTC1210/result/factor1231_nolimit.xlsx')['name'].to_list()[:200]
factor_list = [str(x) for x in factor_list]

bm = Factor5MinLoader(
    start_date=20150306,
    end_date=20210526,
    freq=48,
    factor_list=factor_list,
    load_address='/data/group/800319/HFfactor/DTC2021/data/') #TODO:define


test_date_idx = [-1, -3, -5, -7, -9]
train_start,train_end,predict_start,predict_end = para_list[0][1]

X_train, y_train, X_test, y_test, d_test, t_test, c_test, X_pred, y_pred, idx_date, idx_time, idx_code = \
    bm.lazy_reach_data(train_start, train_end, predict_start, predict_end, test_date_idx, limit=0.2)

