# @Time : 2021/3/8 13:59
# @Author : Zhichen Lu
# @File : NNExtractor.py
import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd

from StrongStockModel.model.ModelBase.ModelNewLoading import ModelNewLoading
import os,time,gc,datetime
from StrongStockModel.conf.path_config import root_path
from tqdm import tqdm
from dataApi.tradeDate import get_date_range,get_pre_trade_date
from sklearn.decomposition import KernelPCA
from sklearn.externals import joblib
from xquant.compute.aimr import AIMR


class PCAExtractor(ModelNewLoading):

    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address='/data/group/800319/LittleJunkFix/', factor_eval_indicator=None, factor_num=None):
        super().__init__(start, end, stock_pool, feature_address, factor_eval_indicator, factor_num=factor_num)

    def get_fix_factor_evaluation(self, num,end_index):
        factor_evaluation = pd.read_pickle(root_path+'external_data/ic_half.pkl')#.set_index('name')
        factor_evaluation = pd.DataFrame(factor_evaluation)
        if not self.eval_indicator in factor_evaluation.index.levels[0]:
            raise Exception('Unavailable indicator')
        factor_evaluation = factor_evaluation.loc[self.eval_indicator]
        target_date = max(list(filter(lambda x :x<end_index,factor_evaluation.index)))
        factor_evaluation = factor_evaluation.loc[target_date]
        inter_col = list(set(factor_evaluation.index).intersection(set(self.using_factor_list)))
        factor_list = factor_evaluation.loc[inter_col].apply(abs).sort_values(ascending=False).index.tolist()[:num]
        self.sorted_factor_list = factor_list.copy()
        return sorted(factor_list)

    def train_model(self, X_train, y_train, params, end_date=None):
        if not os.path.exists(params['train_log_path']):
            os.mkdir(params['train_log_path'])
        if not os.path.exists(params['model_conf_path']):
            os.mkdir(params['model_conf_path'])
        if not os.path.exists(params['feature_path']):
            os.mkdir(params['feature_path'])
        pd.to_pickle(X_train.columns.tolist(),params['feature_path']+'%d.pkl'%end_date)
        model = KernelPCA(kernel='sigmoid',n_jobs=-1,n_components=100)
        if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.pkl' % end_date):
            model = joblib.load(params['model_conf_path'] + '%d.pkl' % end_date)
            print('load model from local')
        else:
            model.fit(X_train)
            joblib.dump(model,params['model_conf_path'] + '%d.pkl' % end_date)
        return model

    def predict(self, model, X_test, end_date_idx=None):
        # pre_label = model.predict(X_test.values)
        return pd.DataFrame()

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
            fix_factor_list = self.get_fix_factor_evaluation(factor_nums, train_end_idx)
            pre_100_day = get_pre_trade_date(train_start_idx, 100)
            pre_1_day = get_pre_trade_date(train_start_idx, 1)
            X_train, y_train, X_test, y_test, feature_engineering_time = \
                self.get_dataset((get_pre_trade_date(train_end_idx,40), train_end_idx), (test_start_idx, test_end_idx),
                                 sorted(self.sorted_factor_list[300:]), None, label_methodology, label_param, kernel=kernel)
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
                pred_label = self.predict(model, X_test, train_end_idx)
                pred_label = pd.DataFrame(pred_label,index=y_test.index)
                corr = pred_label.corrwith(y_test[y_test.columns[0]]).apply(abs)
                print('ic_mean',corr.mean(),'ic_max',corr.max(),'ic_min',corr.min())
                del X_train, y_train, X_test, y_test, pred_label
                gc.collect()
        return label


import configparser

conf = configparser.ConfigParser()
conf.read('/data/group/800319/strategy_local_path_offline/period_info.ini')
para_list = eval(conf['period_info']['period_info'])

def main(i):
    N = 40
    train_period = 200
    test_period = 10
    factor_num = 700
    indicator = 'ic_half_dtc'
    out_file = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FeatureEngineeringExplore/PCAExtractorSigmoid_%s_train%d_test%d_factor_num%d_norm_window_%d.pkl' % (
        indicator, train_period, test_period, factor_num, N)
    base_dir = out_file.replace('.pkl', '/')
    train_start, train_end, test_start, test_end = para_list[i][1]
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    if os.path.exists(base_dir + '%d.pkl' % train_end):
        print(train_end, 'exist')
        # return
    print(out_file)
    model = PCAExtractor(train_start, test_end, None, feature_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/', factor_eval_indicator=indicator, factor_num=factor_num)

    # best_param_clf_xgb['objective'] = 'reg:squarederror'
    best_param_clf_nn = {}
    best_param_clf_nn['feature_path'] = out_file.replace('.pkl', '_feature_path/')
    best_param_clf_nn['train_log_path'] = out_file.replace('.pkl', '_train_log/')
    best_param_clf_nn['model_conf_path'] = out_file.replace('.pkl', '_model_conf/')
    best_param_clf_nn['load local model'] = True
    # best_param_clf_xgb['train_pred_path'] = out_file.replace('.pkl','_train_pred/')
    label = model.rolling_train_and_predict(params=best_param_clf_nn, period=train_period, predict_period=test_period,
                                            label_param={'kind': 'reg'}, kernel=15, factor_nums=factor_num)
    # pd.to_pickle(label, base_dir + '%d.pkl' % train_end)
    print(base_dir + '%d.pkl' % train_end)
    # os.mkdir('/data/group/800319/Faamonitor/PL/')

idx_origin = list(range(73))
idx_origin = [idx_origin[len(idx_origin) * i // 9:(i + 1) * len(idx_origin) // 9] for i in range(6)]
# idx_list = eval(AIMR.getParam())
idx_list_list = list(zip(*idx_origin))[::-1]
for idx_list in idx_list_list:
    for idx in idx_list:
        main(idx)
        gc.collect()