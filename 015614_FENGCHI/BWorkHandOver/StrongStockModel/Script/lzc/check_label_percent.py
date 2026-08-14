# @Time : 2020/9/16 15:01
# @Author : Zhichen Lu
# @File : check_label_percent.py

from System.LoadLabel.LabelDataSet import LabelDataSet
import pandas as pd
from dataApi.stockList import clean_stock_list

stock_pool = clean_stock_list(stock_list='ALL', no_ST=True, least_live_days=240,
                                  no_pause=True, least_recover_days=1,
                                  no_pause_limit=0.5, no_pause_stats_days=120,
                                  no_limit_up=False, no_limit_down=False,
                                  other_limit=None, start_date=20160101, end_date=20181231)
isin = stock_pool.sum()
stk_list = isin[isin>0].index.tolist()

lds = LabelDataSet()
stk_count_daily = pd.DataFrame()
dataset_percent = pd.DataFrame()
for th in range(11):
    label = lds.calc_pctchg_N(stk_list,20160101,20181231,kind='clf',threshold=th*0.01)
    trigger = label.eq(1)
    trigger['date'] = [x[0] for x in label.index]
    stk_count_daily[th] = (trigger.groupby('date').sum()>0).sum(axis=1)
    label = label.stack().to_frame()
    dataset_percent[th] = label.groupby(0).size()/label.shape[0]
    print(th)


with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/样本比例统计.xlsx') as writer:
    pd.concat([dataset_percent.rename(index={1:'正类比例',-1:'负类比例'}),
                pd.DataFrame(stk_count_daily.mean()).T.rename(index={0:'日均触发数量'}),
               stk_count_daily]).to_excel(writer,sheet_name='真实标签每日触发股票数量')

pred_prob = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt/0_pct_w46/XGB_train200_test10.pkl')
pred_prob = pred_prob.reset_index().pivot_table(index=['level_0','level_2'],columns='level_1',values='prediction')
stk_count_daily = pd.DataFrame()
dataset_percent = pd.DataFrame()
for th in range(11):
    label = (pred_prob>th*0.1)*1
    trigger = label.eq(1)
    trigger['date'] = [x[0] for x in label.index]
    stk_count_daily[th] = (trigger.groupby('date').sum()>0).sum(axis=1)
    label = label.stack().to_frame()
    dataset_percent[th] = label.groupby(0).size()/label.shape[0]
    print(th)

with pd.ExcelWriter('/data/user/015664/AFuckingTrigger/XGB不同分类阈值样本比例统计.xlsx') as writer:
    pd.concat([dataset_percent.rename(index={1:'正类比例',0:'负类比例'}),
                pd.DataFrame(stk_count_daily.mean()).T.rename(index={0:'日均触发数量'}),
               stk_count_daily]).to_excel(writer,sheet_name='真实标签每日触发股票数量')