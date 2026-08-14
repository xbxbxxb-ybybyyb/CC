# coding: utf-8
# Author：fengchi863
# Date ：2021/3/9 16:53

'''
版本V1：初次推送成功
版本V2：每天改为推送今天的以及昨天盘中盘后发布的但是Wind列为当天的，以及盘中涨停检测只检测当天发布的
版本V3：增加朝阳永续一致预期数据
版本V4：添加一季报未来五个交易日预计披露一季报的个股列表
'''

import os
import sys
sys.path.append('/data/group/800319')
sys.path.append('/data/user/fengchi/MyWork')
sys.path.append('/data/user/fengchi/MyWork/ShortTermTrading')
from xquant.factordata import FactorData
from ShortTermTrading.dataApi import getData
from ShortTermTrading.dataApi import tradeDate
from ShortTermTrading.dataApi import stockList
from ShortTermTrading.dataApi import indName
from ShortTermTrading.Util.System import get_stock_name_dict, get_latest_kuaibao, \
    get_latest_nianbao, get_latest_yugao, get_cfs_c4_data, get_eod_data
from ShortTermTrading.Util.tools import send_file, save_pickle
import numpy as np, pandas as pd
from ShortTermTrading.conf.path_conf import junk_path, report_monitor_output_path
from tqdm import tqdm
import datetime as dt

output_dict = dict()
stk_code_name_dict = get_stock_name_dict()

monitor_dict = dict()

def get_cfs(cfs_df, stk_id, year, date):
    if type(stk_id) == str:
        stk_id = stockList.trans_windcode2int(stk_id)
    date = str(tradeDate.get_pre_trade_date(int(date)))
    if (stk_id, year, date) not in cfs_df.index:
        return
    else:
        return cfs_df.loc[(stk_id, year, date), 'cfs_c4']

def get_cfs_type(cfs_df, stk_id, year, date):
    if type(stk_id) == str:
        stk_id = stockList.trans_windcode2int(stk_id)
    date = str(tradeDate.get_pre_trade_date(int(date)))
    if (stk_id, year, date) not in cfs_df.index:
        return
    else:
        return cfs_df.loc[(stk_id, year, date), 'cfs_c4_type']

def get_live_days(today_date, stk_id):
    if type(stk_id) == str:
        stk_id = stockList.trans_windcode2int(stk_id)
    live_stk_list = live_days.columns.tolist()
    if stk_id not in live_stk_list:
        return np.nan
    else:
        return live_days.at[tradeDate.get_pre_trade_date(today_date), stk_id]

def get_pct_and_max_pct():
    daily_close_badj = getData.get_daily_1factor('close_badj')
    daily_high_badj = getData.get_daily_1factor('high_badj')
    daily_pct_chg = getData.get_daily_1factor('pct_chg') / 100
    daily_max_pctchg = daily_high_badj / daily_close_badj.shift(1) - 1
    return daily_pct_chg, daily_max_pctchg

def get_df_content(df, date, stk_id):
    if stk_id not in df.columns.tolist():
        return np.nan
    if date not in df.index.tolist():
        return np.nan
    if np.isnan(date):
        return np.nan
    else:
        return df.loc[date, stk_id]

def rm_reported_stk(df, reported_list):
    ret = df[df['股票代码'].apply(lambda x: False if x in reported_list else True)]
    return ret

def get_lyr_profit(df, stk_code):
    if stk_code not in df.index:
        return
    else:
        return df.loc[stk_code, '去年归母净利润']

def get_ttm_profit(df, stk_code):
    if stk_code not in df.index:
        return
    else:
        return df.loc[stk_code, '年报归母净利润']

def get_mv(df, stk_code):
    if stk_code not in df.index:
        return
    else:
        return df.loc[stk_code, '总市值']

daily_pct_chg, daily_max_pctchg = get_pct_and_max_pct()

# 记录运行时间
today_dt = dt.datetime.today()
today_date = int(today_dt.strftime('%Y%m%d'))
yes_date = tradeDate.get_pre_trade_date(today_date)
cfs_df = get_cfs_c4_data(yes_date)
eod_profit = get_eod_data(yes_date)

# 读取昨日的报告
yes_q1_yugao_df = pd.read_excel(report_monitor_output_path + '业绩报告跟踪%d.xlsx' % yes_date, sheet_name='1季度业绩报告跟踪表', index_col=0)
yes_kuaibao_df = pd.read_excel(report_monitor_output_path + '业绩报告跟踪%d.xlsx' % yes_date, sheet_name='年报业绩快报跟踪表', index_col=0)
yes_nianbao_df = pd.read_excel(report_monitor_output_path + '业绩报告跟踪%d.xlsx' % yes_date, sheet_name='年报跟踪表', index_col=0)
yes_q1_yugao_reported_list = yes_q1_yugao_df[yes_q1_yugao_df['预告首次公告日'] < today_date]['股票代码'].tolist()
yes_kuaibao_reported_list = yes_kuaibao_df[yes_kuaibao_df['快报公告日'] < today_date]['股票代码'].tolist()
yes_nianbao_reported_list = yes_nianbao_df[yes_nianbao_df['年报预计披露日'] < today_date]['股票代码'].tolist()

##################### 专门处理一季报数据 ####################
# 对季度预告做处理
live_days = getData.get_daily_1factor('live_days')
raw_yugao_q1_df = get_latest_yugao(type='q1')
jibao_df = get_latest_nianbao(type='q1')
yugao_q1_df = raw_yugao_q1_df
yugao_q1_df['上市天数'] = yugao_q1_df.apply(lambda x: get_live_days(today_date, x['股票代码']), axis=1)
yugao_q1_df = yugao_q1_df[yugao_q1_df['上市天数'] > 10]

# 排序并重命名
yugao_q1_df = yugao_q1_df.sort_values(['预告首次公告日', '股票代码'])
yugao_q1_df = yugao_q1_df.reset_index(drop=True)

append_date_list = [tradeDate.get_pre_trade_date(today_date, -1),
                    tradeDate.get_pre_trade_date(today_date, -2),
                    tradeDate.get_pre_trade_date(today_date, -3),
                    tradeDate.get_pre_trade_date(today_date, -4),
                    tradeDate.get_pre_trade_date(today_date, -5)]
jibao_df = jibao_df[jibao_df['年报预计披露日'].astype(int).isin(append_date_list)]

stk_code_name_dict = get_stock_name_dict()
jibao_df['股票名称'] = jibao_df['股票代码'].apply(lambda x: stk_code_name_dict[stockList.trans_int2windcode(x)]
            if stockList.trans_int2windcode(x) in stk_code_name_dict.keys() else x)
jibao_df = jibao_df[['股票代码', '股票名称', '年报预计披露日']]
jibao_df = jibao_df.rename(columns={'年报预计披露日': '预告首次公告日'})
jibao_df = jibao_df.sort_values('预告首次公告日').reset_index(drop=True)

# 保存
output_yugao_q1_df = yugao_q1_df[(yugao_q1_df['预告首次交易日']==today_date) |
                                     (yugao_q1_df['预告首次交易日']==yes_date)]
output_yugao_q1_df = rm_reported_stk(output_yugao_q1_df, yes_q1_yugao_reported_list)
if len(output_yugao_q1_df) > 0:
    monitor_dict['季报跟踪'] = output_yugao_q1_df['股票代码'].tolist()
    part1 = output_yugao_q1_df[['股票代码', '股票名称', '预告首次公告日', '预告类型',
                        '预告摘要', '变动幅度']].reset_index(drop=True)
    all_part = part1.append(jibao_df, ignore_index=True)
    all_part = all_part[['股票代码', '股票名称', '预告首次公告日', '预告类型',
                        '预告摘要', '变动幅度']]
    output_dict['1季度业绩报告跟踪表'] = all_part
else:
    output_yugao_q1_df = pd.DataFrame(['当日无新增季度预告'])
    output_dict['1季度业绩报告跟踪表'] = output_yugao_q1_df

if len(output_yugao_q1_df.columns) > 1:
    print('隔夜已发布一季度预告的个股有: ', '，'.join(output_yugao_q1_df['股票名称'].tolist()))
print('季报处理完成')

#########################################处理年度快报#########################################
yugao_all_df = get_latest_yugao(type='all')
yugao_all_df = yugao_all_df[yugao_all_df['年份']==2020]

# 筛选公告日日期不正常的
# yugao_all_df = yugao_all_df[(yugao_all_df['预告公告日'].astype(int) <= 20210131) & (yugao_all_df['预告公告日'].astype(int) >= 20201201)]
yugao_all_df = yugao_all_df.sort_values(['股票名称', '预告公告日']).drop_duplicates('股票名称', keep='first')

kuaibao_df = get_latest_kuaibao()
kuaibao_df_index_list = kuaibao_df.index.tolist()
def get_kuaibao_report_date(kuaibao_df, stk_code, year, col_name):
    if (year, stk_code) in kuaibao_df_index_list:
        return kuaibao_df.loc[(year, stk_code), col_name]

yugao_all_df['预告公布日涨跌幅'] = yugao_all_df[['股票代码', '预告首次交易日']].apply(lambda x: get_df_content(daily_pct_chg, x['预告首次交易日'], stockList.trans_windcode2int(x['股票代码'])), axis=1)
yugao_all_df['预告公布日盘中最大涨跌幅'] = yugao_all_df[['股票代码', '预告首次交易日']].apply(lambda x: get_df_content(daily_max_pctchg, x['预告首次交易日'], stockList.trans_windcode2int(x['股票代码'])), axis=1)
kuaibao_df['快报公布日涨跌幅'] = kuaibao_df[['股票代码', '快报公告首次交易日']].apply(lambda x: get_df_content(daily_pct_chg, x['快报公告首次交易日'], stockList.trans_windcode2int(x['股票代码'])), axis=1)
kuaibao_df['快报公布日盘中最大涨跌幅'] = kuaibao_df[['股票代码', '快报公告首次交易日']].apply(lambda x: get_df_content(daily_max_pctchg, x['快报公告首次交易日'], stockList.trans_windcode2int(x['股票代码'])), axis=1)
kuaibao_df['快报公布日一致预期归母净利润'] = kuaibao_df[['股票代码', '年份', '快报公告日']].apply(lambda x: get_cfs(cfs_df, x['股票代码'], x['年份'], x['快报公告日']), axis=1)
kuaibao_df['一致预期类型'] = kuaibao_df[['股票代码', '年份', '快报公告日']].apply(lambda x: get_cfs_type(cfs_df, x['股票代码'], x['年份'], x['快报公告日']), axis=1)
kuaibao_df['去年归母净利润'] = kuaibao_df['股票代码'].apply(lambda x: get_lyr_profit(eod_profit, x))
kuaibao_df['快报归母净利润'] = kuaibao_df['去年归母净利润'] * (1 + kuaibao_df['快报归母利润同比'] / 100)
kuaibao_df['总市值'] = kuaibao_df['股票代码'].apply(lambda x: get_mv(eod_profit, x))

# 这是拼到年报的表上
kuaibao_df_merge = pd.merge(kuaibao_df, yugao_all_df, 'left', ['股票代码', '年份'])

# 更新股票名称列
kuaibao_df_merge['股票名称'] = kuaibao_df_merge['股票代码'].apply(lambda x: stk_code_name_dict[stockList.trans_int2windcode(x)]
        if stockList.trans_int2windcode(x) in stk_code_name_dict.keys() else x)

output_kuaibao_df = kuaibao_df_merge[(kuaibao_df_merge['快报公告首次交易日']==today_date) |
                                     (kuaibao_df_merge['快报公告首次交易日']==yes_date)]
output_kuaibao_df = rm_reported_stk(output_kuaibao_df, yes_kuaibao_reported_list)
if len(output_kuaibao_df) > 0:
    output_dict['年报业绩快报跟踪表'] = output_kuaibao_df[['股票代码', '股票名称', '快报公告日', '总市值', '快报摘要',
                                                  '快报归母净利润', '快报公布日一致预期归母净利润', '一致预期类型',
                                                  '快报营业收入同比', '快报归母利润同比',
                                       '预告首次公告日', '预告类型', '预告摘要', '变动幅度', '预告公布日涨跌幅',
                                       '预告公布日盘中最大涨跌幅']].sort_values('快报公告日').reset_index(drop=True)
    monitor_dict['年报业绩快报跟踪'] = output_kuaibao_df['股票代码'].tolist()
else:
    output_kuaibao_df = pd.DataFrame(['当日无新增快报'])

print('预告处理完成')

#########################################处理年度报告###########################################
nianbao_df = get_latest_nianbao(type='all')
nianbao_df['pre_5day'] = nianbao_df['年报预计披露日'].apply(lambda x: tradeDate.get_pre_trade_date(int(x), 5))
nianbao_df['pre_4day'] = nianbao_df['年报预计披露日'].apply(lambda x: tradeDate.get_pre_trade_date(int(x), 4))
nianbao_df['pre_3day'] = nianbao_df['年报预计披露日'].apply(lambda x: tradeDate.get_pre_trade_date(int(x), 3))
nianbao_df['pre_2day'] = nianbao_df['年报预计披露日'].apply(lambda x: tradeDate.get_pre_trade_date(int(x), 2))
nianbao_df['pre_1day'] = nianbao_df['年报预计披露日'].apply(lambda x: tradeDate.get_pre_trade_date(int(x), 1))
nianbao_df['next_day'] = nianbao_df['年报预计披露日'].apply(lambda x: tradeDate.get_pre_trade_date(int(x), -1))

nianbao_df['年报披露日一致预期归母净利润'] = nianbao_df[['股票代码', '年份', '年报预计披露日']].apply(lambda x: get_cfs(cfs_df, x['股票代码'], x['年份'], x['年报预计披露日']), axis=1)
nianbao_df['一致预期类型'] = nianbao_df[['股票代码', '年份', '年报预计披露日']].apply(lambda x: get_cfs_type(cfs_df, x['股票代码'], x['年份'], x['年报预计披露日']), axis=1)
nianbao_df['去年归母净利润'] = nianbao_df['股票代码'].apply(lambda x: get_lyr_profit(eod_profit, x))
nianbao_df['总市值'] = nianbao_df['股票代码'].apply(lambda x: get_mv(eod_profit, x))
nianbao_df['年报归母净利润'] = nianbao_df[['股票代码', '年报预计披露日']].apply(lambda x: get_ttm_profit(eod_profit, x['股票代码'])
                                                              if x['年报预计披露日'] <= str(today_date) else np.NaN, axis=1)

# 这是拼到年报的表上
tmp_kuaibao_df = kuaibao_df.drop(['报告期', '快报公布日一致预期归母净利润', '去年归母净利润', '总市值', '一致预期类型'], axis=1)
tmp_yugao_all_df = yugao_all_df.drop(['预告报告期', '股票名称'], axis=1)
tmp_all_df = pd.merge(nianbao_df, tmp_kuaibao_df, how='left', on=['股票代码', '年份'])
all_df = pd.merge(tmp_all_df, tmp_yugao_all_df, how='left', on=['股票代码', '年份'])

all_df = all_df.reset_index()
all_df['股票名称'] = all_df['股票代码'].apply(lambda x: stk_code_name_dict[stockList.trans_int2windcode(x)]
        if stockList.trans_int2windcode(x) in stk_code_name_dict.keys() else x)

total_table = pd.DataFrame()
for pre_day_num in ['next_day', '年报实际披露日首次交易日', 'pre_1day', 'pre_2day', 'pre_3day', 'pre_4day', 'pre_5day']:
    tmp_nianbao_df = all_df[all_df[pre_day_num]==today_date]
    tmp_nianbao_df = tmp_nianbao_df[['股票代码', '股票名称', '年报预计披露日', '总市值',
                                     '年报归母净利润', '年报披露日一致预期归母净利润', '一致预期类型', '去年归母净利润',
                                     '预告公告日', '预告类型', '预告摘要', '变动幅度',
                                     '预告公布日涨跌幅', '预告公布日盘中最大涨跌幅',
                                     '快报公告日', '快报摘要', '快报营业收入同比', '快报归母利润同比',
                                     '快报公布日涨跌幅', '快报公布日盘中最大涨跌幅']]
    total_table = pd.concat([total_table, tmp_nianbao_df], axis=0)

if len(total_table) == 0:
    total_table = pd.DataFrame(['近期无年报发布'])
else:
    total_table = rm_reported_stk(total_table, yes_nianbao_reported_list) # 剔除昨日已经发布过的
    monitor_dict['年报报告跟踪'] = total_table[total_table['年报预计披露日'] <= str(today_date)]['股票代码'].tolist()

output_dict['年报跟踪表'] = total_table.sort_values(['年报预计披露日']).reset_index(drop=True)

print('年报处理完成')

# 保存
output_path = report_monitor_output_path + '业绩报告跟踪%d.xlsx' % today_date
with pd.ExcelWriter(output_path) as writer:
    for each in output_dict:
        output_dict[each].to_excel(writer, each)

send_file(['fengchi'], output_path)
print('已发送至目标铃客')

# 保存monitor_dict给判断涨停服务调用
save_pickle(monitor_dict, report_monitor_output_path, '监控股票池%d.pkl' % today_date)