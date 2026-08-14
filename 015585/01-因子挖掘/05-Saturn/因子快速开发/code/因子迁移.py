import os
import pandas as pd

import pickle
def save_pickle(result_dic, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(result_dic, input, protocol=pickle.HIGHEST_PROTOCOL)
#
# res = {}
res = pd.read_pickle('/dfs/user/015585/01_factor_develop_store/fast_factor/saturn/done_factor/done_factor.pkl')
path_i = '/dfs/user/015585/01_factor_develop_store/fast_factor/saturn/h5/20240308lastztlasttick/'
i = '20240308lastztlasttick'
res_i = []
for j in os.listdir(path_i):
    if j[-2:] == 'h5':
        j = j.replace('_20160101_20191231','')
        res_i.append(j[:-3])
res_i = pd.DataFrame({'name':res_i})
res[i] = res_i
print(len(res_i))
save_pickle(res, save_path='/dfs/user/015585/01_factor_develop_store/fast_factor/saturn/done_factor/done_factor.pkl')