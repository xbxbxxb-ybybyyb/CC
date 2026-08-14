# coding: utf-8
# Author：fengchi863
# Date ：2020/7/28 13:45

import numpy as np
import pandas as pd
from sklearn import metrics
from sklearn.linear_model import LogisticRegression
from StrongStockModel.model.ModelBase.ModelBase import ModelBase
import random


def get_resplit_dataset(y_train):
    label_count = y_train.groupby(0).size()
    label_count = (label_count / label_count.min()).apply(round)
    if label_count[1] > 1:
        split_label = 1
        fix_label = -1
    elif label_count[-1] > 1:
        split_label = -1
        fix_label = 1
    else:
        dataset_idx = list(range(y_train.shape[0]))
        random.shuffle(dataset_idx)
        return [dataset_idx]
    idx_list = np.array(list(range(y_train.shape[0])))
    y_arr = y_train.values.reshape(y_train.shape[0])
    fix_label_idx = idx_list[y_arr == fix_label].tolist()
    split_label_lists = np.array_split(idx_list[y_arr == split_label], label_count[split_label])
    dataset_idx_list = []
    for split_part in split_label_lists:
        dataset_idx = split_part.tolist() + fix_label_idx
        random.shuffle(dataset_idx)
        dataset_idx_list.append(dataset_idx)
    return dataset_idx_list

class LR(ModelBase):
    def __init__(self, start=20170103, end=20191231, stock_pool=None, feature_address=None):
        super().__init__(start, end, stock_pool, feature_address)

    def train_model(self, X_train, y_train, params):
        dataset_idx_list = get_resplit_dataset(y_train)
        model_list = []
        print('param', params)
        for dataset_idx in dataset_idx_list:
            model = LogisticRegression(n_jobs=-1)
            model.set_params(**params)
            model.fit(X_train.values[dataset_idx], y_train.values[dataset_idx])
            model_list.append(model)
        return model_list

    def predict(self, model_list, X_test):
        label_prob = np.zeros((X_test.shape[0], 2))
        for model in model_list:
            pre_prob = model.predict_proba(X_test)
            label_prob = label_prob + pre_prob
        pre_label = label_prob / len(model_list)
        return pre_label[:, 1]

    def training_methodology(self, params, period=10, predict_period=10):
        compare = self.rolling_train_and_predict(params=params, period=period, predict_period=predict_period)
        if len(compare) == 0:
            return pd.DataFrame(), {'acc': np.nan, 'precision': np.nan, 'recall': np.nan, 'f1': np.nan}
        acc = metrics.accuracy_score(y_true=compare['actual_label'], y_pred=compare['prediction'])
        precision = metrics.precision_score(y_true=compare['actual_label'], y_pred=compare['prediction'],
                                            average='micro')
        recall = metrics.recall_score(y_true=compare['actual_label'], y_pred=compare['prediction'], average='micro')
        f1 = metrics.f1_score(y_true=compare['actual_label'], y_pred=compare['prediction'], average='micro')
        print({'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1})
        return compare, {'acc': acc, 'precision': precision, 'recall': recall, 'f1': f1}


# def main():
#     # strong_pool = pd.read_pickle(strong_stock_path)
#     strong_pool = pd.read_pickle(ghost_stock_path)
#     strong_pool.columns = [int(x[:-3]) for x in strong_pool.columns]
#     strong_pool.index = strong_pool.index.astype(int)
#     best_param_clf_lr = {
#         'C': 0.07212442211840354,
#         'class_weight': 'balanced',
#         'n_jobs': -1,
#         'penalty': 'l2'
#     }
#     lr = LR(20170103, 20181231,strong_pool.loc[20170103:20181231])
#     label = lr.rolling_train_and_predict(params=best_param_clf_lr,period=20, predict_period=10,label_param={'threshold':0.7})
#     pd.to_pickle(label,'/data/group/800319/Faamonitor/PL/LR_strong_th7.pkl')
#     # os.mkdir('/data/group/800319/Faamonitor/PL/')
# main()
