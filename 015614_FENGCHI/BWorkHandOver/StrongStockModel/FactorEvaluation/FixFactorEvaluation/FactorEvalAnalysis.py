# @Time : 2021/4/13 20:51
# @Author : Zhichen Lu
# @File : FactorEvalAnalysis.py
import pandas as pd
import os
from tqdm import tqdm
res_path =  '/data/user/015664/AFuckingTrigger/FixFactorEvaluationFixly/'

file_list = os.listdir(res_path)
file_list = list(filter(lambda x : x.endswith('.pkl'),file_list))

all_factor_res = {
    x:{i:{} for i in ['year','half_year','quater','month','all']} for x in ['ic_c', 'ic_c_fix', 'ic_d', 'ic_d_fix', 'ic_t']
}


for file_name in tqdm(file_list):
    factor_name = file_name.replace('.pkl','')
    res = pd.read_pickle(res_path+file_name)
    for ic_type in res:
        for freq in res[ic_type]:
            if isinstance(res[ic_type][freq],pd.DataFrame):
                all_factor_res[ic_type][freq][factor_name] =res[ic_type][freq].stack()
            elif isinstance(res[ic_type][freq],pd.Series):
                all_factor_res[ic_type][freq][factor_name] = res[ic_type][freq]

for ic_type in all_factor_res:
    for freq in all_factor_res[ic_type]:
        all_factor_res[ic_type][freq] = pd.DataFrame(all_factor_res[ic_type][freq])

pd.to_pickle(all_factor_res,'/data/user/015664/AFuckingTrigger/FixFactorEvaluationFixly/res_integration/all_res.pkl')


