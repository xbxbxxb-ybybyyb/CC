# coding: utf-8
# Author：fengchi863
# Date ：2023/10/12 16:21

import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from xquant.marketdata import MarketData
mdp = MarketData()
s = FactorData()
import datetime as dt
import time
import os
from ProdWork.Param_config_data import thred_dict_metis_v1 as thred_dict
import sys

if len(sys.argv) > 1:
    date = sys.argv[1]
else:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
    # date = '20250122' # 若未在当个交易日晚上运行程序，需要在次日早上修改date
print('leda更新实盘触发标签文件：current date = %s' % date)

Adate = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
lastdate = s.tradingday(date, -2)[0]
Alastdate = lastdate[0:4] + '-' + lastdate[4:6] + '-' + lastdate[6:8]
print('当前交易日date = %s，前一交易日lastdate = %s' % (date, lastdate))

IO_mother_dir = '/data/group/800080/warehouse_event'
MD_data_prod_dir = IO_mother_dir + '/prod/LOCAL_DATA/FLAG/%s/' % date  # 大概每日5点20好
md_data_wind_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/md_data_wind/'
start_date = s.tradingday(date, -20)[0]
md_data = pd.read_pickle(md_data_wind_path + f'{start_date}-{date}.pkl')
tot_pattern_df = pd.read_pickle(f'/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/历史交易日样本形态数据/{date}.pkl')

# ----------------------------更新日内强势股触发文件，添加形态和o2ul信息-------------------------------
t1 = time.time()
need_columns = ['dt', 'Ticker', 'ZT_Time', '买入时形态', 'TN_o2ul', 'shouldBuySignal']
model_columns = list(thred_dict.keys())
model_columns = [x + '_local_prob' for x in model_columns]

# 获取昨天的标签汇总、今天的因子耗时和模型差异
if lastdate <= '20240401':
    Labels_prod_summary_old = pd.DataFrame(columns=need_columns)
else:
    Labels_prod_summary_old = pd.read_excel(f'/data/group/800463/日内强势股/leda_log_parse/因子耗时/实盘触发标签汇总Leda_{Alastdate}.xlsx')

model_columns = list(set(model_columns + Labels_prod_summary_old.filter(regex='_local_prob').columns.tolist()))
# print(model_columns)
raw_last_date_factor_time_cost = pd.read_excel(f'/data/group/800463/日内强势股/leda_log_parse/因子耗时/因子耗时_{Alastdate}_prod.xlsx', sheet_name='因子耗时')
raw_last_date_factor_time_cost = raw_last_date_factor_time_cost[~raw_last_date_factor_time_cost['Unnamed: 0'].duplicated()]

raw_last_date_model_compare = pd.read_excel(f'/data/group/800463/日内强势股/leda_log_parse/模型差异/{lastdate}/模型差异Leda_{lastdate}_prod.xlsx',
                                            sheet_name='本地投票结果').rename(columns={'Ticker': 'Unnamed: 0'})
# 获取模型的预测结果
# 如果昨天有模型没有给出预测（比如没有前日涨停样本、或者没有前高样本等分场景），则在模型差异中的投票结果中新建一个空的列
for model_name in model_columns:
    if model_name not in raw_last_date_model_compare.columns:
        raw_last_date_model_compare[model_name] = np.nan
raw_last_date_model_compare = raw_last_date_model_compare[['Unnamed: 0'] + model_columns].rename(columns={'Unnamed: 0': 'Ticker'}) * 1
raw_last_date_model_compare['dt'] = pd.Timestamp(Alastdate)

# 计算买入时形态，by fengc 20240228，不对每个进行调用cal_Basic_zt函数，耗时太长，直接读取卖出文件
# 触发过的就都计算，直接读取卖出记录确实不可行
for index, row in raw_last_date_factor_time_cost.iterrows():
    stock_code, pre_date = row['Unnamed: 0'], lastdate
    APre_date = pre_date[0:4] + '-' + pre_date[4:6] + '-' + pre_date[6:8]
    raw_last_date_factor_time_cost.loc[index, '买入时形态'] = tot_pattern_df.loc[(pd.to_datetime(APre_date), stock_code), 'label_pattern']

# 将耗时、模型预测拼入标签汇总
raw_last_date_factor_time_cost['dt'] = pd.Timestamp(lastdate)
raw_last_date_factor_time_cost['TN_o2ul'] = np.nan
raw_last_date_factor_time_cost = raw_last_date_factor_time_cost.rename(columns={'Unnamed: 0': 'Ticker'})
Labels_prod_summary_new = pd.concat([Labels_prod_summary_old, raw_last_date_factor_time_cost.set_index(['dt', 'Ticker']).join(
                                         raw_last_date_model_compare.set_index(['dt', 'Ticker'])).reset_index()[need_columns + model_columns]]).reset_index()[need_columns]
# TODO: 如果昨天的模型差异文件没生，直接运行下面这句，不运行上面那部分即可
# Labels_prod_summary_new = Labels_prod_summary_old.reset_index()[need_columns]

# 对于o2ul还未算出的样本进行计算
o2ul_nan_samples = Labels_prod_summary_new[Labels_prod_summary_new['TN_o2ul'].isnull()]
# date_ini = o2ul_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).min()
# end_date = o2ul_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).max()

md_data['trigger_price'] = md_data['ul_price'] - 0.01
md_data['trigger_price'] = md_data['trigger_price'] * md_data['adjfactor']
Labels_prod_summary_new.set_index(['dt', 'Ticker'], inplace=True)
Labels_prod_summary_new['label_Tc2Tul'] = md_data.loc[Labels_prod_summary_new.index, 'label_Tc2Tul']
Labels_prod_summary_new['label_T1o2Tc'] = md_data.loc[Labels_prod_summary_new.index, 'label_T1o2Tc']
Labels_prod_summary_new['label_T1c2Tc'] = md_data.loc[Labels_prod_summary_new.index, 'label_T1c2Tc']
Labels_prod_summary_new['label_T1_zt'] = md_data.loc[Labels_prod_summary_new.index, 'label_T1_zt']
Labels_prod_summary_new = Labels_prod_summary_new.reset_index()
Labels_prod_summary_new_copy = Labels_prod_summary_new.copy()

tmp_df = 100 * md_data.reindex(Labels_prod_summary_new_copy.set_index(['dt', 'Ticker']).index)['label_TN_o2ul']
for i in o2ul_nan_samples.index:
    buy_date = Labels_prod_summary_new.loc[i]['dt']
    stock = Labels_prod_summary_new.loc[i]['Ticker']
    Labels_prod_summary_new.loc[i, 'TN_o2ul'] = tmp_df.loc[buy_date.strftime('%Y%m%d'), stock]

Labels_prod_summary_new.to_excel('/data/group/800463/日内强势股/leda_log_parse/因子耗时/实盘触发标签汇总Leda_%s.xlsx' % Adate, index=False)
print('create file %s!!!!!!!!!!' % '/data/group/800463/日内强势股/leda_log_parse/因子耗时/实盘触发标签汇总Leda_%s.xlsx' % Adate)
print(f'2-5.label_summary_leda耗时{round(time.time() - t1, 6)}秒')