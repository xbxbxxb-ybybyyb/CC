import os
import pandas as pd

import pickle
def save_pickle(result_dic, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(result_dic, input, protocol=pickle.HIGHEST_PROTOCOL)
#
path = '/data/user/015585/01-因子挖掘/03-Jupyter/因子快速开发/h5/'
list_date = os.listdir(path)
list_date = [x for x in list_date if x.startswith('2023')]
res = {}
for i in list_date:
    path_i = path + i + '/'
    print(path_i)
    res_i = []
    for j in os.listdir(path_i):
        if j[-2:] == 'h5':
            j = j.replace('_20160101_20191231','')
            res_i.append(j[:-3])
    res_i = pd.DataFrame({'name':res_i})
    res[i] = res_i
save_pickle(res, save_path='/dfs/user/015585/01_factor_develop_store/fast_factor/europa/done_factor/done_factor.pkl')