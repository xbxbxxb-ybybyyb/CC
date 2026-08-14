# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')

import xgboost as xgb
import os, gc, time, datetime
from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
from tqdm import tqdm

from dataApi.tradeDate import get_pre_trade_date,get_date_range,get_recent_trade_date
from dataApi.FixFactorRollPrepare import load_fix_data,feature_engineering
import pandas as pd
import torch
from torch import nn
import numpy as np
torch.set_default_tensor_type(torch.FloatTensor)

class DNN(nn.Module):

    def __init__(self, dim_in=1000, dim_out=400, cuda=0):
        super().__init__()
        self.layer_dnn1 = nn.Linear(dim_in, 800)
        self.layer_dnn2 = nn.Linear(800, dim_out)
        self.dropout = nn.Dropout(0.5)
        self.bn = nn.BatchNorm1d(dim_out)
        self.device = torch.device(f'cuda:{cuda}') if cuda >= 0 else torch.device('cpu')
        self.to(device=self.device)
        self.dim_in = dim_in
        self.dim_out = dim_out

    def forward(self, X):
        dnn = self.layer_dnn1(X)
        dnn = self.dropout(dnn)
        nn.ReLU(inplace=True)(dnn)
        dnn = self.layer_dnn2(dnn)
        dnn = self.bn(dnn)
        return dnn



model_date_list = {0: (20160229, 20161219, 20161221, 20170104),
 1: (20160314, 20170103, 20170105, 20170118),
 2: (20160328, 20170117, 20170119, 20170208),
 3: (20160412, 20170207, 20170209, 20170222),
 4: (20160426, 20170221, 20170223, 20170308),
 5: (20160511, 20170307, 20170309, 20170322),
 6: (20160525, 20170321, 20170323, 20170407),
 7: (20160608, 20170406, 20170410, 20170421),
 8: (20160624, 20170420, 20170424, 20170508),
 9: (20160708, 20170505, 20170509, 20170522),
 10: (20160722, 20170519, 20170523, 20170607),
 11: (20160805, 20170606, 20170608, 20170621),
 12: (20160819, 20170620, 20170622, 20170705),
 13: (20160902, 20170704, 20170706, 20170719),
 14: (20160920, 20170718, 20170720, 20170802),
 15: (20161011, 20170801, 20170803, 20170816),
 16: (20161025, 20170815, 20170817, 20170830),
 17: (20161108, 20170829, 20170831, 20170913),
 18: (20161122, 20170912, 20170914, 20170927),
 19: (20161206, 20170926, 20170928, 20171018),
 20: (20161220, 20171017, 20171019, 20171101),
 21: (20170104, 20171031, 20171102, 20171115),
 22: (20170118, 20171114, 20171116, 20171129),
 23: (20170208, 20171128, 20171130, 20171213),
 24: (20170222, 20171212, 20171214, 20171227),
 25: (20170308, 20171226, 20171228, 20180111),
 26: (20170322, 20180110, 20180112, 20180125),
 27: (20170407, 20180124, 20180126, 20180208),
 28: (20170421, 20180207, 20180209, 20180301),
 29: (20170508, 20180228, 20180302, 20180315),
 30: (20170522, 20180314, 20180316, 20180329),
 31: (20170607, 20180328, 20180330, 20180416),
 32: (20170621, 20180413, 20180417, 20180502),
 33: (20170705, 20180427, 20180503, 20180516),
 34: (20170719, 20180515, 20180517, 20180530),
 35: (20170802, 20180529, 20180531, 20180613),
 36: (20170816, 20180612, 20180614, 20180628),
 37: (20170830, 20180627, 20180629, 20180712),
 38: (20170913, 20180711, 20180713, 20180726),
 39: (20170927, 20180725, 20180727, 20180809),
 40: (20171018, 20180808, 20180810, 20180823),
 41: (20171101, 20180822, 20180824, 20180906),
 42: (20171115, 20180905, 20180907, 20180920),
 43: (20171129, 20180919, 20180921, 20181012),
 44: (20171213, 20181011, 20181015, 20181026),
 45: (20171227, 20181025, 20181029, 20181109),
 46: (20180111, 20181108, 20181112, 20181123),
 47: (20180125, 20181122, 20181126, 20181207),
 48: (20180208, 20181206, 20181210, 20181221),
 49: (20180301, 20181220, 20181224, 20190108),
 50: (20180315, 20190107, 20190109, 20190122),
 51: (20180329, 20190121, 20190123, 20190212),
 52: (20180416, 20190211, 20190213, 20190226),
 53: (20180502, 20190225, 20190227, 20190312),
 54: (20180516, 20190311, 20190313, 20190326),
 55: (20180530, 20190325, 20190327, 20190410),
 56: (20180613, 20190409, 20190411, 20190424),
 57: (20180628, 20190423, 20190425, 20190513),
 58: (20180712, 20190510, 20190514, 20190527),
 59: (20180726, 20190524, 20190528, 20190611),
 60: (20180809, 20190610, 20190612, 20190625),
 61: (20180823, 20190624, 20190626, 20190709),
 62: (20180906, 20190708, 20190710, 20190723),
 63: (20180920, 20190722, 20190724, 20190806),
 64: (20181012, 20190805, 20190807, 20190820),
 65: (20181026, 20190819, 20190821, 20190903),
 66: (20181109, 20190902, 20190904, 20190918),
 67: (20181123, 20190917, 20190919, 20191009),
 68: (20181207, 20191008, 20191010, 20191023),
 69: (20181221, 20191022, 20191024, 20191106),
 70: (20190108, 20191105, 20191107, 20191120),
 71: (20190122, 20191119, 20191121, 20191204),
 72: (20190212, 20191203, 20191205, 20191218),
 73: (20190226, 20191217, 20191219, 20200102),
 74: (20190312, 20191231, 20200103, 20200116),
 75: (20190326, 20200115, 20200117, 20200207),
 76: (20190410, 20200206, 20200210, 20200221),
 77: (20190424, 20200220, 20200224, 20200306),
 78: (20190513, 20200305, 20200309, 20200320),
 79: (20190527, 20200319, 20200323, 20200403),
 80: (20190611, 20200402, 20200407, 20200420),
 81: (20190625, 20200417, 20200421, 20200507),
 82: (20190709, 20200506, 20200508, 20200521),
 83: (20190723, 20200520, 20200522, 20200604),
 84: (20190806, 20200603, 20200605, 20200618),
 85: (20190820, 20200617, 20200619, 20200706),
 86: (20190903, 20200703, 20200707, 20200720),
 87: (20190918, 20200717, 20200721, 20200803),
 88: (20191009, 20200731, 20200804, 20200817),
 89: (20191023, 20200814, 20200818, 20200831),
 90: (20191106, 20200828, 20200901, 20200914),
 91: (20191120, 20200911, 20200915, 20200928),
 92: (20191204, 20200925, 20200929, 20201020),
 93: (20191218, 20201019, 20201021, 20201103),
 94: (20200102, 20201102, 20201104, 20201117),
 95: (20200116, 20201116, 20201118, 20201201),
 96: (20200207, 20201130, 20201202, 20201215),
 97: (20200221, 20201214, 20201216, 20201229),
 98: (20200306, 20201228, 20201230, 20210113),
 99: (20200320, 20210112, 20210114, 20210127),
 100: (20200403, 20210126, 20210128, 20210210),
 101: (20200420, 20210209, 20210218, 20210303),
 102: (20200507, 20210302, 20210304, 20210317),
 103: (20200521, 20210316, 20210318, 20210331),
 104: (20200604, 20210330, 20210401, 20210415),
 105: (20200618, 20210414, 20210416, 20210429),
 106: (20200706, 20210428, 20210430, 20210518),
 107: (20200720, 20210517, 20210519, 20210601),
 108: (20200803, 20210531, 20210602, 20210616),
 109: (20200817, 20210615, 20210617, 20210630),
 110: (20200831, 20210629, 20210701, 20210714),
 111: (20200914, 20210713, 20210715, 20210728)}


class XGBRegressionFactorEvalYearly(ModelNewLoading):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None, factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)

    def get_dataset(self, train_idx, test_idx, fix_factor_list, interday_factor, label_method, label_param={}, kernel=10):
        # self.dp = FixFactorRollPrepare(start_date=train_idx[0], end_date=test_idx[-1], freq=7, model_time_len=1, factor_list=fix_factor_list,
        #                                load_address=self.feature_address)
        gc.collect()
        e = time.time()

        if train_idx[-1] == test_idx[0] and train_idx[-1] == test_idx[-1]:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(train_idx[0], get_pre_trade_date(train_idx[-1]),
                                                                                                                      fix_factor_list)
        else:
            train_feature, train_label, nolimit_train, train_idx_date, train_idx_code, train_idx_time = load_fix_data(train_idx[0], train_idx[-1], fix_factor_list)
        train_feature, train_label, train_idx_date, train_idx_time, train_idx_code = feature_engineering(train_feature, train_label, nolimit_train, train_idx_date,
                                                                                                         train_idx_time, train_idx_code)

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

            index_test = pd.MultiIndex.from_tuples(list(zip(test_idx_date.tolist(), test_idx_time.tolist(), test_idx_code.tolist())))

            test_feature, test_label = pd.DataFrame(test_feature, index=index_test, columns=fix_factor_list), pd.DataFrame({'actual_label': test_label}, index=index_test)

        return train_feature, train_label, test_feature, test_label, time.time() - e


    def predict(self, model_, X_test, end_date=None,label_param={}):
        model,NN = model_
        X_test = pd.DataFrame(NN(torch.from_numpy(X_test.values)).detach().numpy(),index=X_test.index)
        dtest = xgb.DMatrix(X_test)
        model.set_param('predictor','cpu_predictor')
        pre_label = model.predict(dtest)
        return pre_label

    def train_model(self, X_train, y_train, params, end_date=None):

        NN = DNN(1529, 400,-1)
        for i in range(112):
            if model_date_list[i][1]>end_date:
                break
        i-=1
        print(f'{end_date} use NN for period {model_date_list[i]}')
        NN.load_state_dict(torch.load(f'/arch1/group/800442/800319/HXmodel/20210811/{self.eval_indicator}/NN/{i}.pkl'))
        NN.float()
        index,columns = X_train.index,X_train.columns
        X_train = NN(torch.from_numpy(X_train.values).float()).detach().numpy()
        X_train = pd.DataFrame(X_train,index=index)


        key_list = set(params.keys()).intersection(
            set(['booster', 'colsample_bytree', 'gamma', 'max_depth', 'min_child_weight', 'n_estimators', 'sampling_method', 'subsample', 'tree_method']))
        args_param = {x: params[x] for x in key_list}
        print(args_param)
        date_list = get_date_range(X_train.index[0][0], end_date)
        val_date = [date_list[i] for i in [-1, -3, -5, -7, -9, -11]]
        date_list = list(set(date_list) - set(val_date))

        pd.to_pickle(columns.tolist(), params['feature_path'] + '%d.pkl' % end_date)

        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.json' % end_date):
            model = xgb.Booster(args_param)
            model.load_model(params['model_conf_path'] + '%d.json' % end_date)
            print('load from local', end_date)
            # return model
        else:
            print('no exist model conf')
            if not os.path.exists(params['model_conf_path']):
                os.mkdir(params['model_conf_path'])
            ########################
            train_features, train_label = X_train.loc[date_list], y_train.loc[date_list]
            d_train = xgb.DMatrix(train_features[:-50000], label=train_label[:-50000].values)
            d_eval = xgb.DMatrix(train_features[-50000:], label=train_label[-50000:].values)
            model = xgb.train(args_param, d_train, num_boost_round=params['n_estimators'], evals=[(d_eval, 'd_eval')], early_stopping_rounds=15, verbose_eval=True)
            model.save_model(params['model_conf_path'] + '%d.json' % end_date)
            print(params['model_conf_path'] + '%d.json' % end_date)

        if 'val_pred_path' in params:
            if not os.path.exists(params['val_pred_path']):
                os.mkdir(params['val_pred_path'])
            val_features, val_labels = X_train.loc[val_date[1:]], y_train.loc[val_date[1:]]
            d_val = xgb.DMatrix(val_features)
            val_labels['prediction'] = model.predict(d_val)
            pd.to_pickle(val_labels, params['val_pred_path'] + '%d.pkl' % end_date)
        return model,NN

    def rolling_train_and_predict(self, params={}, period=10, predict_period=10, label_methodology='fix_window', label_param={}, factor_nums=200, kernel=10):
        rolling_train_test_idx_list = self.get_rolling_index(period, predict_period)
        label = pd.DataFrame()
        bar = tqdm(rolling_train_test_idx_list)
        loading_time, training_time, feature_engineering_time, training_sample = 0, 0, 0, 0
        model = None

        for idx, cell_idx in bar:
            bar.set_description(
                "%s | %d | %d-%d || loading %.1f | feature engineering %.1f | training %.1f | training sample %d" % (
                    datetime.datetime.now().strftime('%H:%M:%S'),
                    os.getpid(), cell_idx[2], cell_idx[3], loading_time, feature_engineering_time,
                    training_time, training_sample))
            train_start_idx, train_end_idx, test_start_idx, test_end_idx = \
                cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3]
            e = time.time()
            print('check', cell_idx[0], cell_idx[1], cell_idx[2], cell_idx[3])
            # if test_end_idx!= 20170607:
            #     continue
            fix_factor_list = pd.read_pickle('/arch1/group/800442/800319/HXmodel/20210811/factor_list.pkl')#self.get_fix_factor_evaluation(factor_nums, train_end_idx)
            X_train, y_train, X_test, y_test, feature_engineering_time = \
                self.get_dataset((train_start_idx, train_end_idx), (test_start_idx, test_end_idx),
                                 fix_factor_list, None, label_methodology, params, kernel=kernel)
            gc.collect()
            training_sample = X_train.shape[0]
            loading_time = time.time() - e - feature_engineering_time
            e = time.time()

            if len(X_train) > 2000 and len(set(y_train[y_train.columns[0]])) > 1:
                print('re-train in this round')
                model = self.train_model(X_train, y_train, params, train_end_idx)
            if model is None:
                continue
            training_time = time.time() - e
            if len(X_test) == 0:
                print('zero sample')
                continue
            else:
                pred_label = self.predict(model, X_test, train_end_idx,params)
                y_test.columns = ['actual_label']
                y_test['prediction'] = pred_label
                print('test_ic', train_end_idx, y_test.corr())
                label = label.append(y_test)
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label


from xquant.xqutils.helper import link
import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800442/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])


def main_window_search(i, indicator):
    train_period = 200
    test_period = 10
    factor_num = 800

    tag = 'XGBUseHXNNExtractor_%s_train%d_test%d_factor_num%d' % (indicator, train_period, test_period, factor_num)
    out_file = f'/data/group/800442/800319/Strong_stock/C3PO/{tag}/{tag}.pkl'

    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(train_end, 'exist')
        return
    print(out_file)

    best_param_clf_xgb = { 'n_estimators': 100,'subsample': 0.8, 'tree_method': 'gpu_hist'}
    best_param_clf_xgb['val_pred_path'] = out_file.replace('.pkl', '_val_pred/')
    best_param_clf_xgb['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_xgb['feature_path'] = out_file.replace('.pkl', '_factor_list/')

    model = XGBRegressionFactorEvalYearly(train_start, test_end, None, feature_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/',
                                          factor_eval_indicator=indicator,
                                          factor_num=factor_num)
    if not os.path.exists(best_param_clf_xgb['model_conf_path']):
        os.mkdir(best_param_clf_xgb['model_conf_path'])
    if not os.path.exists(best_param_clf_xgb['feature_path']):
        os.mkdir(best_param_clf_xgb['feature_path'])
    best_param_clf_xgb['load local model'] = True
    label = model.rolling_train_and_predict(params=best_param_clf_xgb, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    pd.to_pickle(label, base_dir + '%d.pkl' % train_end)
    print(base_dir + '%d.pkl' % train_end)

from multiprocessing import Process

idx_list = list(range(24,138))
for i in tqdm(idx_list):
    if datetime.datetime.now()>=datetime.datetime(2021, 8, 27, 6, 15, 51, 780926):
        break
    for ind_name in ['ic_c']:
    # for ind_name in ['top_ret'][::-1]:
        pro = Process(target=main_window_search,args=(i, ind_name))
        # main_window_search(i, ind_name)
        pro.start()
        pro.join()
        del pro
from dataApi.sendInfo import send_message
send_message(['015664'],f'GPU released {datetime.datetime.now()}')

# for i in tqdm(idx_list):
#     for ind_name in ['ic_t']:
#     # for ind_name in ['top_ret'][::-1]:
#         pro = Process(target=main_window_search,args=(i, ind_name))
#         # main_window_search(i, ind_name)
#         pro.start()
#         pro.join()
#         del pro
#
# for i in tqdm(idx_list):
#     for ind_name in ['ic_c']:
#         main_window_search(i, ind_name)
#         # pro = Process(target=main_window_search,args=(i, ind_name))
#         # pro.start()
#         # pro.join()
#         # del pro