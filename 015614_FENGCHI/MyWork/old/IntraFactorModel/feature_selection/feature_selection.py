# coding: utf-8
# Author：fengchi863
# Date ：2020/5/26 16:59

from sklearn.linear_model import RidgeClassifier, RandomizedLasso
from sklearn.preprocessing import MinMaxScaler
from sklearn.feature_selection import f_classif
import pandas as pd
from conf.model_param_config import *
from minepy import MINE
import time

def rank_to_dict(ranks, feature_names, ascending=True):
    minmax = MinMaxScaler()
    ranks = minmax.fit_transform(ascending * np.array([ranks]).T).T[0]
    ranks = map(lambda x: round(x, 2), ranks)
    return dict(zip(feature_names, ranks))

def get_tuple_list(corr, min_corr, max_corr):
    _corr = corr.stack()
    _res = _corr[(_corr>min_corr) & (_corr<max_corr)].index.tolist()
    res = []
    for idx, cont in enumerate(_res):
        cont1, cont2 = cont
        if cont1 == cont2:
            continue
        else:
            if not res.__contains__(set([cont1,cont2])):
                res.append(set([cont1,cont2]))
    return res

if __name__ == '__main__':

    # step1: 剔除计算复杂的因子
    complex_factor_list = []

    # step2: 较难实盘中获取数据的因子
    non_realtime_factor_list = []

    # others
    drop_list = [
        # corr
        'alpha167',
        'alpha31',
        'alpha46',
        'boll9',
        'factor_dev05',
        'factor_dev07',
        'alpha129',
        'alpha161',
        'boll11', # boll12
        'alpha14', # alpha21
        'alpha18', # alpha19
        'alpha47',
        'alpha49', # alpha50
        'boll4', # boll3
        'boll5',
        'boll7', # boll8
        'boll9',
        'boll12', # boll11
        'alpha147', # alpha151
    ]

    drop_list = drop_list + complex_factor_list + non_realtime_factor_list

    ranks = {}

    # 因子值之间的相关性
    # corr_list = []
    # corr_path = '/data/group/800319/junkData/IntraFactorModel/feature_selection/'
    # corr = pd.read_excel(corr_path + 'corr_factor.xlsx', index_col=0)
    # corr_list = get_tuple_list(corr, min_corr=0.9, max_corr=1.)

    t_start = time.clock()

    # 使用LR筛选
    lr_model = model_choice['lr'][0](start_date=20170103, end_date=20181231)
    X_train, y_train = lr_model.get_train_data(1, 'twap')
    X_train = X_train.drop(drop_list, axis=1)
    model = lr_model.model_train(X_train, y_train, best_param_clf_lr)
    ranks['lr'] = rank_to_dict(np.abs(model.coef_.reshape(-1)), X_train.columns.tolist())
    print("lr completed!")

    # 使用XGBoost树模型筛选
    xgb_model = model_choice['xgb'][0](start_date=20170103, end_date=20181231)
    model = xgb_model.model_train(X_train, y_train, best_param_clf_xgboost)
    ranks['xgb'] = rank_to_dict(model.feature_importances_, X_train.columns.tolist())
    print("xgb completed!")

    # 使用Ridge筛选
    ridge = RidgeClassifier(alpha=7)
    ridge.fit(X_train, y_train)
    ranks['ridge'] = rank_to_dict(np.abs(ridge.coef_.reshape(-1)), X_train.columns.tolist())
    print("ridge completed!")

    # 使用Lasso筛选
    lasso = RandomizedLasso(alpha=0.04)
    lasso.fit(X_train, y_train)
    ranks["lasso"] = rank_to_dict(np.abs(lasso.scores_), X_train.columns.tolist())
    print("lasso completed!")

    # f_classif
    f, pval = f_classif(X_train, y_train)
    ranks['corr'] = rank_to_dict(f, X_train.columns.tolist())
    print('corr completed')

    # 最大信息系数，耗时很长，大概8h
    mine = MINE()
    mic_scores = []
    for col in X_train.columns.tolist():
        print('MIC', col)
        mine.compute_score(X_train.loc[:, col], y_train)
        m = mine.mic()
        mic_scores.append(m)
    ranks['MIC'] = rank_to_dict(mic_scores, X_train.columns.tolist())
    print('MIC completed!')

    methods = sorted(ranks.keys())
    feature_selection = pd.DataFrame(index=X_train.columns.tolist(), columns=sorted(methods))

    for feature in X_train.columns.tolist():
        for method in methods:
            feature_selection.loc[feature, method] = ranks[method][feature]

    t_finish = time.clock()
    print('=======Costs time : %s s=======' % str(t_finish - t_start))