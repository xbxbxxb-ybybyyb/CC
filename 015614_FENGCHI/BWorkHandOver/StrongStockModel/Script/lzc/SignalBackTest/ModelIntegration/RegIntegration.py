# @Time : 2021/2/18 9:20
# @Author : Zhichen Lu
# @File : RegIntegration.py

import pandas as pd
from sklearn.linear_model import LinearRegression
import os
from multiprocessing import Pool,Manager
from tqdm import tqdm

para_list = [(0, (20150309, 20151225, 20151228, 20160111)),
 (1, (20150323, 20160111, 20160112, 20160125)),
 (2, (20150407, 20160125, 20160126, 20160215)),
 (3, (20150421, 20160215, 20160216, 20160229)),
 (4, (20150506, 20160229, 20160301, 20160314)),
 (5, (20150520, 20160314, 20160315, 20160328)),
 (6, (20150603, 20160328, 20160329, 20160412)),
 (7, (20150617, 20160412, 20160413, 20160426)),
 (8, (20150702, 20160426, 20160427, 20160511)),
 (9, (20150716, 20160511, 20160512, 20160525)),
 (10, (20150730, 20160525, 20160526, 20160608)),
 (11, (20150813, 20160608, 20160613, 20160624)),
 (12, (20150827, 20160624, 20160627, 20160708)),
 (13, (20150914, 20160708, 20160711, 20160722)),
 (14, (20150928, 20160722, 20160725, 20160805)),
 (15, (20151019, 20160805, 20160808, 20160819)),
 (16, (20151102, 20160819, 20160822, 20160902)),
 (17, (20151116, 20160902, 20160905, 20160920)),
 (18, (20151130, 20160920, 20160921, 20161011)),
 (19, (20151214, 20161011, 20161012, 20161025)),
 (20, (20151228, 20161025, 20161026, 20161108)),
 (21, (20160112, 20161108, 20161109, 20161122)),
 (22, (20160126, 20161122, 20161123, 20161206)),
 (23, (20160216, 20161206, 20161207, 20161220)),
 (24, (20160301, 20161220, 20161221, 20170104)),
 (25, (20160315, 20170104, 20170105, 20170118)),
 (26, (20160329, 20170118, 20170119, 20170208)),
 (27, (20160413, 20170208, 20170209, 20170222)),
 (28, (20160427, 20170222, 20170223, 20170308)),
 (29, (20160512, 20170308, 20170309, 20170322)),
 (30, (20160526, 20170322, 20170323, 20170407)),
 (31, (20160613, 20170407, 20170410, 20170421)),
 (32, (20160627, 20170421, 20170424, 20170508)),
 (33, (20160711, 20170508, 20170509, 20170522)),
 (34, (20160725, 20170522, 20170523, 20170607)),
 (35, (20160808, 20170607, 20170608, 20170621)),
 (36, (20160822, 20170621, 20170622, 20170705)),
 (37, (20160905, 20170705, 20170706, 20170719)),
 (38, (20160921, 20170719, 20170720, 20170802)),
 (39, (20161012, 20170802, 20170803, 20170816)),
 (40, (20161026, 20170816, 20170817, 20170830)),
 (41, (20161109, 20170830, 20170831, 20170913)),
 (42, (20161123, 20170913, 20170914, 20170927)),
 (43, (20161207, 20170927, 20170928, 20171018)),
 (44, (20161221, 20171018, 20171019, 20171101)),
 (45, (20170105, 20171101, 20171102, 20171115)),
 (46, (20170119, 20171115, 20171116, 20171129)),
 (47, (20170209, 20171129, 20171130, 20171213)),
 (48, (20170223, 20171213, 20171214, 20171227)),
 (49, (20170309, 20171227, 20171228, 20180111)),
 (50, (20170323, 20180111, 20180112, 20180125)),
 (51, (20170410, 20180125, 20180126, 20180208)),
 (52, (20170424, 20180208, 20180209, 20180301)),
 (53, (20170509, 20180301, 20180302, 20180315)),
 (54, (20170523, 20180315, 20180316, 20180329)),
 (55, (20170608, 20180329, 20180330, 20180416)),
 (56, (20170622, 20180416, 20180417, 20180502)),
 (57, (20170706, 20180502, 20180503, 20180516)),
 (58, (20170720, 20180516, 20180517, 20180530)),
 (59, (20170803, 20180530, 20180531, 20180613)),
 (60, (20170817, 20180613, 20180614, 20180628)),
 (61, (20170831, 20180628, 20180629, 20180712)),
 (62, (20170914, 20180712, 20180713, 20180726)),
 (63, (20170928, 20180726, 20180727, 20180809)),
 (64, (20171019, 20180809, 20180810, 20180823)),
 (65, (20171102, 20180823, 20180824, 20180906)),
 (66, (20171116, 20180906, 20180907, 20180920)),
 (67, (20171130, 20180920, 20180921, 20181012)),
 (68, (20171214, 20181012, 20181015, 20181026)),
 (69, (20171228, 20181026, 20181029, 20181109)),
 (70, (20180112, 20181109, 20181112, 20181123)),
 (71, (20180126, 20181123, 20181126, 20181207)),
 (72, (20180209, 20181207, 20181210, 20181221)),
 (73, (20180302, 20181221, 20181224, 20190108)),
 (74, (20180316, 20190108, 20190109, 20190122)),
 (75, (20180330, 20190122, 20190123, 20190212)),
 (76, (20180417, 20190212, 20190213, 20190226)),
 (77, (20180503, 20190226, 20190227, 20190312)),
 (78, (20180517, 20190312, 20190313, 20190326)),
 (79, (20180531, 20190326, 20190327, 20190410)),
 (80, (20180614, 20190410, 20190411, 20190424)),
 (81, (20180629, 20190424, 20190425, 20190513)),
 (82, (20180713, 20190513, 20190514, 20190527)),
 (83, (20180727, 20190527, 20190528, 20190611)),
 (84, (20180810, 20190611, 20190612, 20190625)),
 (85, (20180824, 20190625, 20190626, 20190709)),
 (86, (20180907, 20190709, 20190710, 20190723)),
 (87, (20180921, 20190723, 20190724, 20190806)),
 (88, (20181015, 20190806, 20190807, 20190820)),
 (89, (20181029, 20190820, 20190821, 20190903)),
 (90, (20181112, 20190903, 20190904, 20190918)),
 (91, (20181126, 20190918, 20190919, 20191009)),
 (92, (20181210, 20191009, 20191010, 20191023)),
 (93, (20181224, 20191023, 20191024, 20191106)),
 (94, (20190109, 20191106, 20191107, 20191120)),
 (95, (20190123, 20191120, 20191121, 20191204)),
 (96, (20190213, 20191204, 20191205, 20191218)),
 (97, (20190227, 20191218, 20191219, 20200102)),
 (98, (20190313, 20200102, 20200103, 20200116)),
 (99, (20190327, 20200116, 20200117, 20200207)),
 (100, (20190411, 20200207, 20200210, 20200221)),
 (101, (20190425, 20200221, 20200224, 20200306)),
 (102, (20190514, 20200306, 20200309, 20200320)),
 (103, (20190528, 20200320, 20200323, 20200403)),
 (104, (20190612, 20200403, 20200407, 20200420)),
 (105, (20190626, 20200420, 20200421, 20200507)),
 (106, (20190710, 20200507, 20200508, 20200521)),
 (107, (20190724, 20200521, 20200522, 20200604)),
 (108, (20190807, 20200604, 20200605, 20200618)),
 (109, (20190821, 20200618, 20200619, 20200706)),
 (110, (20190904, 20200706, 20200707, 20200720)),
 (111, (20190919, 20200720, 20200721, 20200803)),
 (112, (20191010, 20200803, 20200804, 20200817)),
 (113, (20191024, 20200817, 20200818, 20200831)),
 (114, (20191107, 20200831, 20200901, 20200914)),
 (115, (20191121, 20200914, 20200915, 20200928)),
 (116, (20191205, 20200928, 20200929, 20201020)),
 (117, (20191219, 20201020, 20201021, 20201103)),
 (118, (20200103, 20201103, 20201104, 20201117)),
 (119, (20200117, 20201117, 20201118, 20201201)),
 (120, (20200210, 20201201, 20201202, 20201215)),
 (121, (20200224, 20201215, 20201216, 20201229)),
 (122, (20200309, 20201229, 20201230, 20210113)),
 (123, (20200323, 20210113, 20210114, 20210127)),
 (124, (20200407, 20210127, 20210128, 20210210)),
 (125, (20200421, 20210210, 20210218, 20210218))]

model_list = [
'/data/group/800319/wyl/model_record/catboostnew2_ic_all_t.pkl',
 '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40.pkl',
'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40.pkl',
]

def linear_integration_by_period(point,pct_threshold):
    train_set = {}
    test_set = {}
    train_indexes, test_indexes = None, None
    for each in model_list:
        pred_path = each.replace('.pkl','/')
        val_path = each.replace('.pkl','_val_pred/')
        train_set[each] = pd.read_pickle(f'{val_path}{point}.pkl')
        test_set[each] = pd.read_pickle(f'{pred_path}{point}.pkl')
        if train_indexes is None:
            train_indexes = set(train_set[each].index.tolist())
        else:
            train_indexes = train_indexes.intersection(set(train_set[each].index.tolist()))
        if test_indexes is None:
            test_indexes = set(test_set[each].index.tolist())
        else:
            test_indexes = test_indexes.intersection(set(test_set[each].index.tolist()))
    train_indexes,test_indexes = sorted(list(train_indexes)),sorted(list(test_indexes))

    train_set = {x:train_set[x].loc[train_indexes] for x in train_set}
    test_set = {x:test_set[x].loc[test_indexes] for x in test_set}

    train_set,test_set = pd.Panel(train_set),pd.Panel(test_set)

    train_features,train_label = train_set.minor_xs('prediction'),train_set.minor_xs('actual_label').mean(axis=1)
    test_feature,test_label = test_set.minor_xs('prediction'),test_set.minor_xs('actual_label').mean(axis=1)

    mid = train_features.shape[0]//2

    model = LinearRegression()
    model.fit(train_features[:mid],train_label[:mid])
    val_pred = pd.DataFrame({'actual_label':train_label[mid:],'prediction':model.predict(train_features[mid:])})
    test_pred = pd.DataFrame({'actual_label':test_label,'prediction':model.predict(test_feature)})
    if test_pred.shape[0]>0:
        corr[point] = val_pred.corr().values[0,1]
    #############
    percentile = (val_pred['actual_label'] < pct_threshold).sum() / val_pred.shape[0]
    threshold = val_pred['prediction'].quantile(percentile)
    test_pred['signal'] = test_pred['prediction'] > threshold
    signal.append(test_pred)
    return test_pred

def max_ic_integration_by_period(point,pct_threshold):
    train_set = {}
    test_set = {}
    train_indexes, test_indexes = None, None
    for each in model_list:
        pred_path = each.replace('.pkl','/')
        val_path = each.replace('.pkl','_val_pred/')
        train_set[each] = pd.read_pickle(f'{val_path}{point}.pkl')
        test_set[each] = pd.read_pickle(f'{pred_path}{point}.pkl')
        if train_indexes is None:
            train_indexes = set(train_set[each].index.tolist())
        else:
            train_indexes = train_indexes.intersection(set(train_set[each].index.tolist()))
        if test_indexes is None:
            test_indexes = set(test_set[each].index.tolist())
        else:
            test_indexes = test_indexes.intersection(set(test_set[each].index.tolist()))
    train_indexes,test_indexes = sorted(list(train_indexes)),sorted(list(test_indexes))

    train_set = {x:train_set[x].loc[train_indexes] for x in train_set}
    test_set = {x:test_set[x].loc[test_indexes] for x in test_set}

    train_set,test_set = pd.Panel(train_set),pd.Panel(test_set)

    train_features,train_label = train_set.minor_xs('prediction'),train_set.minor_xs('actual_label').mean(axis=1)
    test_feature,test_label = test_set.minor_xs('prediction'),test_set.minor_xs('actual_label').mean(axis=1)

    train_features['label'] = train_label
    weight = train_features.corr()['label'].drop('label')
    weight = weight/weight.sum()
    train_features = train_features.drop('label',axis=1)

    val_pred = pd.DataFrame({'actual_label':train_label,'prediction':train_features.dot(weight)})
    test_pred = pd.DataFrame({'actual_label':test_label,'prediction':test_feature.dot(weight)})
    if test_pred.shape[0]>0:
        corr[point] = val_pred.corr().values[0,1]
    #############
    percentile = (val_pred['actual_label'] < pct_threshold).sum() / val_pred.shape[0]
    threshold = val_pred['prediction'].quantile(percentile)
    test_pred['signal'] = test_pred['prediction'] > threshold
    signal.append(test_pred)
    return test_pred

head = 73
bar = tqdm(total=head)

def update(*param):
    bar.update()
    if bar.last_print_n==bar.total:
        bar.close()

signal = Manager().list()
corr = Manager().dict()
pct = 0.05

# a = max_ic_integration_by_period(20151225,pct)

pool = Pool(20)
for _,cell in para_list[:73]:
    train_start,train_end,test_start,test_end = cell
    # pool.apply_async(linear_integration_by_period,(train_end,pct),callback=update)
    pool.apply_async(max_ic_integration_by_period,(train_end,pct),callback=update)
    # print(train_end)
pool.close()
pool.join()

signal = pd.concat(signal._getvalue()).sort_index()
corr = pd.Series(corr._getvalue()).sort_index()
pred_ret = signal.reset_index().pivot_table(index=['level_0','level_1'],columns='level_2',values='prediction')
sig = signal.reset_index().pivot_table(index=['level_0','level_1'],columns='level_2',values='signal')
pd.to_pickle([sig,pred_ret],'/data/user/015664/AFuckingTrigger/限制买入和持仓/信号存储/signal_XGB_Cat_Light_MaxIC_%.2f.pkl' % (pct))


