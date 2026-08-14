# @Time : 2020/6/9 15:15
# @Author : Zhichen Lu
# @File : stat_acc_all_stk.py
import os
from multiprocessing import Pool

import pandas as pd
from sklearn import metrics

# path = '/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_5min_from2017_origin_factor_20200622/'
path = '/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_5min_from2017_preday_padding_nodrop_factor_20200623/'
# '/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_5min_from2017_origin_nodrop_factor_20200623/'
# '/data/group/800319/junkData/IntraFactorModel/predictions/lr_model_rise_down_zero_20200528/'
file_list = os.listdir(path)
file_list = list(filter(lambda x: 'Wrong' not in x, file_list))
# result={'all':[]}

def calc_one_stk(file_name):
    res = {}
    stk_id = int(file_name.strip('.pkl'))
    compare, evaluate = pd.read_pickle(path + file_name)
    if compare.shape[0] == 0:
        print('None', stk_id)
        return pd.DataFrame({stk_id: pd.Series(res)})
    # compare = compare[compare['actual'].isin([1,-1])]
    count = compare.groupby('actual').size()
    acc = metrics.accuracy_score(y_true=compare['actual'],
                                 y_pred=compare['prediction'])
    res['all'] = acc - (count / count.sum()).max()
    print(stk_id, ':', acc, (count / count.sum()).max())
    compare['year'] = [x[0] // 10000 for x in compare.index]
    for year in set(compare.year):
        temp_compare = compare[compare['year'] == year]
        if temp_compare.shape[0] == 0:
            continue
        acc = metrics.accuracy_score(y_true=temp_compare['actual'], y_pred=temp_compare['prediction'])
        count = temp_compare.groupby('actual').size()
        temp_outperformance = acc - (count / count.sum()).max()
        res[year] = temp_outperformance
    res = pd.DataFrame({stk_id: pd.Series(res)})
    # print(stk_id)
    return res[stk_id]


def calc_one_stk_precision(file_name):
    res = {}
    stk_id = int(file_name.strip('.pkl'))
    compare, evaluate = pd.read_pickle(path + file_name)
    if compare.shape[0] == 0:
        print('None', stk_id)
        return pd.DataFrame({stk_id: pd.Series(res)})
    # compare = compare[compare['actual'].isin([1,-1])]
    res['all'] = pd.DataFrame(metrics.precision_recall_fscore_support(compare['actual'], compare['prediction'], labels=[0, 1, -1]),
                              index=['precision', 'recall', 'f1', 'count'], columns=[0, 1, -1])
    compare['year'] = [x[0] // 10000 for x in compare.index]
    for year in set(compare.year):
        temp_compare = compare[compare['year'] == year]
        if temp_compare.shape[0] == 0:
            continue
        res[year] = pd.DataFrame(metrics.precision_recall_fscore_support(temp_compare['actual'], temp_compare['prediction'], labels=[0, 1, -1]),
                                 index=['precision', 'recall', 'f1', 'count'], columns=[0, 1, -1])
    res = pd.Panel(res)

    # print(stk_id)
    return res.loc[:, 'precision', :]


def get_file(file_name):
    stk_id = int(file_name.strip('.pkl'))
    compare, evaluate = pd.read_pickle(path + file_name)
    return compare


"""
pool = Pool(10)
res_list = pool.map(get_file,file_list)
pool.close()
pool.join()

compare = pd.concat(res_list)
res = {}
res['all']= pd.DataFrame(metrics.precision_recall_fscore_support(compare['actual'],compare['prediction'],labels=[0,1,-1]),
                             index=['precision','recall','f1','count'],columns=[0,1,-1])
compare['year'] = [x[0] // 10000 for x in compare.index]
for year in set(compare.year):
    temp_compare = compare[compare['year'] == year]
    if temp_compare.shape[0] == 0:
        continue
    res[year] = pd.DataFrame(metrics.precision_recall_fscore_support(temp_compare['actual'],temp_compare['prediction'],labels=[0,1,-1]),
                         index=['precision','recall','f1','count'],columns=[0,1,-1])
res = pd.Panel(res)
print(res.loc[:,'precision',:])
"""

pool = Pool(10)
res_list = pool.map(calc_one_stk, file_list)
# pool_dict = {}
# for stk in file_list:
#     pool_dict[stk] = pool.apply_async(calc_one_stk_precision,(stk,))
pool.close()
pool.join()
result = pd.concat(res_list, axis=1)
yearly = result.mean(axis=1)
# res_dict = {}
# for stk in pool_dict:
#     res_dict[stk.strip('.pkl')] = pool_dict[stk].get()
#     if len(res_dict[stk.strip('.pkl')])==0:
#         res_dict.pop(stk.strip('.pkl'))
# result = pd.Panel(res_dict)
# yearly = result.mean(axis=0).T
# yearly = result.mean(axis=1)
# res_list = []
# for each in file_list:
#     temp_res = calc_one_stk(each)
#     res_list.append(temp_res)
#     print(each)


# i = 20
# compare = pd.read_pickle(model_file_path+'CNN_20200622/'+'label_compare.pkl')
# metrics.precision_recall_fscore_support(compare['label']+1,compare['prediction'])
#
# compare[(i-1)*compare.shape[0]//i:].groupby('prediction').size()/compare[(i-1)*compare.shape[0]//i:].groupby('label').size().sum()
