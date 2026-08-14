# @Time : 2021/5/11 10:55
# @Author : Zhichen Lu
# @File : stat_order_info.py
import itertools,os
import pandas as pd
from tqdm import tqdm
import numpy as np

in_file = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivityWithOrderInfo/record/record_XGB_lightGBM_CatBoostWithMax5thresholdAlphaTriggerPoolV3Top600_real600_deal_ratio_0.1_per_ratio_%.4f_threshold_%.2f_inital_%dVolConsider_UpBuy100_10bp_cost.pkl'

para_list = list(itertools.product([0.005, 0.007, 0.009, 0.01, 0.02, 0.025, 0.05], [0.03, 0.04, 0.05, 0.06], [2e8,4e8,6e8,8e8,1e9]))


def get_order_stat(para):
    _, _, _, order_info = pd.read_pickle(in_file % para)
    key_list = list(order_info.keys())
    res_list = []
    for key in key_list:
        temp = order_info[key]
        if len(temp) == 0:
            continue
        temp = pd.DataFrame({'可委托量占(初始规模*委托占比)的比例': temp['orderable'] / temp['target'], '委托完成率': temp['deal_vol'] / temp['sent_order']})
        temp['完全成交'] = np.isclose(temp['委托完成率'], 1)
        temp['委托金额=初始规模*委托占比'] = temp['可委托量占(初始规模*委托占比)的比例'] >= 1
        temp.index = pd.MultiIndex.from_tuples([key + (x,) for x in temp.index])
        res_list.append(temp)
    res_list = pd.concat(res_list)
    return res_list.mean()


res = {}
for p in tqdm(para_list):
    if not os.path.exists(in_file % p):
        print(p)
    res[p] = get_order_stat(p)
res = pd.DataFrame(res).T
pd.to_pickle(res,'/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/统计下单成交比例.pkl')
base_path = '/data/user/015664/AFuckingTrigger/限制买入和持仓/OnlineEraSensitivity/'
with pd.ExcelWriter(f'{base_path}信号完成率统计_不同初始规模.xlsx') as writer:
    for col in res.columns:
        res.reset_index().pivot_table(index=['level_2','level_0'],columns='level_1',values=col).to_excel(writer,sheet_name=col.replace('*','.'))
writer.close()

from dataApi.sendInfo import send_file
send_file(['015664'],f'{base_path}信号完成率统计_不同初始规模.xlsx')

# import pandas as pd
# check1 = pd.read_pickle('/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample/20210415.pkl')
# check2 = pd.read_pickle('/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample/20210415_original.pkl')
# compare = pd.DataFrame({'new':check1['prediction'],'old':check2['prediction']})
