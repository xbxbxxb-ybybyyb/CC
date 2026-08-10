import pandas as pd
import numpy as np
from utils_wsc.help_functions_temp import DatetimeConvert
from sklearn.linear_model import LogisticRegression

########################################################################################################################
'''数据导入'''
ic_need = pd.read_hdf('/data/user/')
factors_selected_low_corr = pd.read_hdf('/data/user/')
y_return = ic_need['long_ret_after_fee']['2016':'2020-03']
label = '±1'  # y_label的取值

if label == 'O_1':
    y_return = ic_need['long_ret_after_fee']['2016':'2020-03']
    y_true = y_return.copy()
    y_true[y_true > 0] = 1
    y_true[y_true < 1] = 0
    y_true = y_true.fillna(0)
    y_return = y_return.fillna(0)
elif label == '±1':
    y_return = ic_need['long_ret_after_fee']['2016':'2020-03'].dropna()
    y_true = np.sign(y_return)

x = factors_selected_low_corr.reindex(y_true.index)
x = x.fillna(0)
x['year_month'] = [DatetimeConvert(i).timestamp_to_int() // 100 for i in y_true.index]

########################################################################################################################
'''
模型训练：rolling_window，输出分类
'''
predict_period = 20
train_period = 360
if (y_true.shape[0] - train_period) % predict_period != 0:
    iter_num = (y_true.shape[0] - train_period) // predict_period + 1
else:
    iter_num = (y_true.shape[0] - train_period) // predict_period

y_predict_final = None

for i in range(iter_num):
    x_train = x.iloc[i * predict_period:(train_period + i * predict_period)].drop('year_month', axis=1)
    y_train = y_true.reindex(x_train.index)
    y_return_train = y_return.reindex(x_train.index)
    x_test = x.iloc[(train_period + i * predict_period):(train_period + (i + 1) * predict_period)].drop('year_month',
                                                                                                        axis=1)
    y_test = y_true.reindex(x_test.index)
    lr_clf = LogisticRegression(random_state=10, penalty='l2', tol=1e-5, C=0.01, solver='liblinear', max_iter=200,
                                verbose=1, n_jobs=-1).fit(x_train, y_train,
                                                          sample_weight=abs(y_return_train) / abs(y_return_train).sum())
    y_predict = lr_clf.predict(x_test)
    y_predict_final = y_predict if y_predict_final is None else np.hstack((y_predict_final, y_predict))

y_predict_final = pd.Series(y_predict_final, index=x.iloc[train_period:].index)
