# 使用实际的量计算实际买入的股票的模拟第一版收益
"""
Saturn 931 别称 项目二931
"""
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
from xquant.marketdata import MarketData
mdp = MarketData()
s = FactorData()
from LucienUtil import IO
import datetime as dt
import sys
import time
import os

if len(sys.argv) > 1:
    date = sys.argv[1]
else:
    date = s.tradingday(dt.datetime.now().strftime('%Y%m%d'), -1)[0]  # 判断当前的日期
    # date = '20240802' # 若未在当个交易日晚上运行程序，需要在次日早上修改date
print('pj2_931更新实盘触发标签文件：current date = %s' % date)

Adate = date[0:4] + '-' + date[4:6] + '-' + date[6:8]
lastdate = s.tradingday(date, -2)[0]
Alastdate = lastdate[0:4] + '-' + lastdate[4:6] + '-' + lastdate[6:8]
IO_mother_dir = '/data/group/800080/warehouse_event'
MD_data_prod_dir = IO_mother_dir + '/prod/LOCAL_DATA/FLAG/%s/' % date
md_data_wind_path = '/data/group/800463/日内强势股/实盘分析记录/日内强势股成交记录/前置数据/md_data_wind/'
start_date = s.tradingday(date, -20)[0]
md_data = pd.read_pickle(md_data_wind_path + f'{start_date}-{date}.pkl')

# ----------------------------更新项目二触发文件，添加形态和v2o10d1信息-------------------------------
t1 = time.time()
need_columns_tot = ['dt', 'Ticker', '前日形态', 'TN_v2o10d1', 'p2shouldBuySignal', '买入时点', 'T_c2o10d1', 'close_zt', 'high_zt', 'T_o2pre']
need_columns = ['dt', 'Ticker', '前日形态', 'TN_v2o10d1', 'p2shouldBuySignal', '买入时点']
# 获取昨天的标签汇总、今天的因子耗时和模型差异
if lastdate <= '20210621':
    Labels_prod_summary_old = pd.DataFrame(columns = need_columns_tot)
else:
    Labels_prod_summary_old = pd.read_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二931标签汇总_%s.xlsx' % Alastdate)
if 'twap2o10d1' not in Labels_prod_summary_old.columns:
    Labels_prod_summary_old['twap2o10d1'] = np.nan
raw_last_date_factor_time_cost_pj2 = pd.read_excel('/data/group/800463/日内强势股/saturn_log_parse/因子耗时/因子耗时_%s_prod.xlsx' % Alastdate, sheet_name='因子耗时Saturn')
raw_last_date_model_compare_pj2 = pd.read_excel('/data/group/800463/日内强势股/saturn_log_parse/模型差异/%s/模型差异_%s_prod_pj2_931.xlsx' % (lastdate, lastdate)
                                                , sheet_name='本地投票结果').rename(columns={'Ticker': 'Unnamed: 0'})

# 当前项目二买入时点为931
raw_last_date_model_compare_pj2['买入时点'] = 931
# 获取模型的预测结果
# 如果昨天有模型没有给出预测（比如没有前日涨停样本、或者没有前高样本等分场景），则在模型差异中的投票结果中新建一个空的列
raw_last_date_model_compare_pj2 = raw_last_date_model_compare_pj2[['Unnamed: 0'] + ['买入时点']].rename(columns={'Unnamed: 0': 'Ticker'}) * 1
raw_last_date_model_compare_pj2['dt'] = pd.Timestamp(Alastdate)
if len(raw_last_date_factor_time_cost_pj2) != 0:
    # 计算买入时形态
    for index, row in raw_last_date_factor_time_cost_pj2.iterrows():
        stock_code, pre_date = row['Unnamed: 0'], lastdate
        saturn_basic_info = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')
        raw_last_date_factor_time_cost_pj2.loc[index, '前日形态'] = saturn_basic_info.loc[lastdate, stock_code]['lzt_label_pattern']
    # 将耗时、模型预测拼入标签汇总
    raw_last_date_factor_time_cost_pj2['dt'] = pd.Timestamp(lastdate)
    raw_last_date_factor_time_cost_pj2['TN_v2o10d1'] = np.nan
    raw_last_date_factor_time_cost_pj2 = raw_last_date_factor_time_cost_pj2.rename(columns={'Unnamed: 0': 'Ticker'})
    Labels_prod_summary_new = pd.concat([Labels_prod_summary_old,
                                         raw_last_date_factor_time_cost_pj2.set_index(['dt', 'Ticker']).join(
                                             raw_last_date_model_compare_pj2.set_index(['dt', 'Ticker'])).reset_index()[need_columns]]) \
        .reset_index()[need_columns_tot + ['twap2o10d1']]
else:
    Labels_prod_summary_new = Labels_prod_summary_old

# 对于v2o10d1还未算出的样本进行计算
v2o10d1_nan_samples = Labels_prod_summary_new[(Labels_prod_summary_new['TN_v2o10d1'].isnull()) | (Labels_prod_summary_new['T_c2o10d1'].isnull())]
if len(v2o10d1_nan_samples) != 0:
    # date_ini = v2o10d1_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).min()
    # end_date = v2o10d1_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).max()

    Labels_prod_summary_new_copy = Labels_prod_summary_new.copy()
    for i in v2o10d1_nan_samples.index:
        # i = 31
        buy_date = Labels_prod_summary_new.loc[i]['dt'].strftime('%Y%m%d')
        stock = Labels_prod_summary_new.loc[i]['Ticker']
        saturn_basic_hf_info = pd.read_hdf('/data/group/800463/project/project2_prod/daily_data/Basic/Basic_closed_hf_finish.h5')
        T_day_931_10_twap_before_ZT = saturn_basic_hf_info['T_day_931_10_twap_before_ZT'].loc[buy_date, stock]
        this_buy_price = md_data['adjfactor'].loc[buy_date, stock] * T_day_931_10_twap_before_ZT
        this_v2o10d1 = (md_data['next_vwap'].loc[buy_date, stock] / this_buy_price - 1) * 100
        T_c2o10d1 = (md_data['vwap'].loc[buy_date, stock] / this_buy_price - 1) * 100
        if T_day_931_10_twap_before_ZT == -1:
            this_v2o10d1, T_c2o10d1 = -1, -1
        if T_day_931_10_twap_before_ZT == -3:
            this_v2o10d1, T_c2o10d1 = -3, -3
        Labels_prod_summary_new.loc[i, 'TN_v2o10d1'] = this_v2o10d1
        Labels_prod_summary_new.loc[i, 'T_c2o10d1'] = T_c2o10d1

# ------------------------------------更新触发文件，计算模拟收益-------------------------------------------------
import sys
sys.path.append("../../")
sys.path.append("/../..")
from xquant.factordata import FactorData

s = FactorData()
if __name__ == "__main__":
    # -----计算卖出收益-----
    if 'close_zt' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['close_zt'] = np.nan
    if 'high_zt' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['high_zt'] = np.nan
    if 'T_o2pre' not in Labels_prod_summary_new.columns:
        Labels_prod_summary_new['T_o2pre'] = np.nan

    close_high_zt_nan_samples = Labels_prod_summary_new[Labels_prod_summary_new['close_zt'].isnull() | Labels_prod_summary_new['high_zt'].isnull()]
    if len(close_high_zt_nan_samples) != 0:
        # date_ini = close_high_zt_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).min()
        # end_date = close_high_zt_nan_samples['dt'].apply(lambda x: x.strftime('%Y%m%d')).max()
        for i in close_high_zt_nan_samples.index:
            buy_date = Labels_prod_summary_new.loc[i]['dt'].strftime('%Y%m%d')
            stock = Labels_prod_summary_new.loc[i]['Ticker']
            Labels_prod_summary_new.loc[i, 'high_zt'] = (md_data['ul_price'] == md_data['high']).loc[buy_date, stock]
            Labels_prod_summary_new.loc[i, 'close_zt'] = (md_data['ul_price'] == md_data['close']).loc[buy_date, stock]
            Labels_prod_summary_new.loc[i, 'T_o2pre'] = 100 * ((md_data['open'] / md_data['pre_close']) - 1).loc[buy_date, stock]

    Labels_prod_summary_new.to_excel('/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二931标签汇总_%s.xlsx' % Adate, index=False)
    print('create file %s!!!!!!!!!!!!'%'/data/group/800463/日内强势股/log_parse/因子耗时/实盘触发项目二931标签汇总_%s.xlsx' % Adate)
    print(f'2-2.label_summary_pj2_931耗时{round(time.time() - t1, 6)}秒')