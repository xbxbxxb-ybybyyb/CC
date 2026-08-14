# coding: utf-8
# Author：fengchi863
# Date ：2024/2/28 14:53

"""
提前计算当天的买入时形态，做数据持有化处理
之前都是在后面的代码进行计算，重复的代码出现过10处左右，导致耗时非常长

20250724：对于低频策略，这个文件无需修改，因为只针对打板个股进行pattern计算
"""
import os
import numpy as np
import pandas as pd
from xquant.marketdata import MarketData
mdp = MarketData()
import datetime as dt
from xquant.factordata import FactorData
import sys
import time
from tqdm import tqdm
s = FactorData()

print('0-1.开始准备形态前置数据')
output_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/历史交易日样本形态数据/'

from ProdWork.intra_strong.add_mimas.func_Basic_zt import cal_Basic_zt
if len(sys.argv) > 1:
    today_date = sys.argv[1]
else:
    today_date = dt.datetime.today().strftime('%Y%m%d')
    # today_date = '20241227'

while True:
    md_data = s.get_factor_value('WIND_AShareEODPrices',
                                 factors=['S_INFO_WINDCODE', 'S_DQ_PRECLOSE', 'S_DQ_CLOSE'],
                                 TRADE_DT=today_date).rename(columns={'S_INFO_WINDCODE': 'Ticker', 'S_DQ_PRECLOSE': 'pre_close', 'S_DQ_CLOSE': 'close'})
    if len(md_data) > 0:  # 当日有数据
        md_data['dt'] = pd.to_datetime(today_date)
        md_data = md_data.set_index(['dt', 'Ticker']).sort_index()
        break
    else:
        print(f'{today_date}_WIND数据未完备')
        time.sleep(60)

t1 = time.time()
today_date_str = today_date[:4] + '-' + today_date[4:6] + '-' + today_date[6:]
# 计算因子解析出的全部触发样本，触板的样本
# jupiter与europa不是包含关系，而且有交集，所以要取并集；metis是jupiter或者
jupiter_samples = pd.read_excel(f'/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_{today_date_str}_prod.xlsx', sheet_name='因子耗时', index_col=0)
europa_samples = pd.read_excel(f'/data/group/800463/日内强势股/log_parse/因子耗时/因子耗时_{today_date_str}_prod.xlsx', sheet_name='因子耗时New', index_col=0)
metis_samples = pd.read_excel(f'/data/group/800463/日内强势股/metis_log_parse/因子耗时/因子耗时_{today_date_str}_prod.xlsx', sheet_name='因子耗时Metis', index_col=0)
leda_samples = pd.read_excel(f'/data/group/800463/日内强势股/leda_log_parse/因子耗时/因子耗时_{today_date_str}_prod.xlsx', sheet_name='因子耗时', index_col=0)

jup_lattern = pd.read_hdf('/data/group/800463/project/project1_prod/left_v2310/Basic_zt/Basic_zt.h5')[['label_pattern']]
eur_lattern = pd.read_hdf('/data/group/800463/project/project1_prod/left_v2212/Basic_zt_test/Basic_zt_001.h5')[['label_pattern']]
metis_lattern = pd.read_hdf('/data/group/800463/project/project1_prod/left_v2212/Basic_metis/Basic_metis.h5')[['label_pattern']]
leda_lattern = pd.read_hdf('/data/group/800463/project/project1_prod/left_v2310/Basic_zt/Basic_zt.h5')[['label_pattern']]

new_samples = list(sorted(list(set(jupiter_samples.index).union(europa_samples.index).union(metis_samples.index).union(leda_samples.index))))

# 优化：提前使用多进程提前运算
from LucienUtil.SpeedUtil import SpeedUtil

def get_stk_pattern(stk_code_list):
    ret_list = list()
    # for idx, stk_code in tqdm(enumerate(stk_code_list)):
    for stk_code in tqdm(stk_code_list):
        # if idx < 6:
        #     continue
        pre_close, close = md_data.loc[pd.to_datetime(today_date), stk_code][['pre_close', 'close']].values
        ret_list.append(cal_Basic_zt(mdp, stk_code, today_date, pre_close, close)['label_pattern'].values[0])
    return ret_list

ret_dict = SpeedUtil.multiprocess(24, get_stk_pattern, new_samples)
# ret_dict = get_stk_pattern(new_samples)
ret_result = dict()
ret_list = list()
for k in ret_dict:
    try:
        ret_result[k] = ret_dict[k].get()
    except Exception as e:
        print('多进程内部出错')
        print(e)
for k in ret_result:
    ret_list.extend(ret_result[k])

# ret_list = get_stk_pattern(new_samples[0:])

today_pattern = pd.DataFrame(ret_list,
          index=pd.MultiIndex.from_product([[pd.to_datetime(today_date)], new_samples]), columns=['label_pattern'])
tot_lattern = pd.concat([jup_lattern, eur_lattern, metis_lattern, today_pattern], axis=0).sort_index().reset_index().drop_duplicates(subset=['dt', 'Ticker'], keep='first').set_index(['dt', 'Ticker']).sort_index()
tot_lattern.to_pickle(output_path + f'{today_date}.pkl')
print(f'{today_date}当日所有形态数据均以计算完成并保存')
print(f'0-1.calc_label_pattern耗时{round(time.time() - t1, 6)}秒')