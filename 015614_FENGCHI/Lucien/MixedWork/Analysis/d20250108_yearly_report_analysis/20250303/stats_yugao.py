# coding: utf-8
# Author：fengchi863
# Date ：2025/2/10 14:18

import pandas as pd
from MixedWork.Analysis.d20250108_yearly_report_analysis.System import *
import time
from LucienUtil import IO
from xquant.factordata import FactorData
from dataApi.tradeDate import get_date_range
from tqdm import tqdm

stats_year = 2023

def get_latestN(dat, N=30):
    date_list = get_date_range(dat, tradeDate.get_pre_trade_date(dat, -N + 1))
    return list(map(lambda x: str(x), date_list))

def get_lives_day(dat, base_date):
    if base_date < 20160101:
        return 5000
    else:
        return tradeDate.get_trade_date_interval(dat, base_date)

t1 = time.time()

#%% 统计业绩预告信息
fd = FactorData()
start_date = stats_year * 10000 + 1101
end_date = (stats_year + 1) * 10000 + 1101
date_list = get_date_range(start_date, end_date)
date_list = list(map(lambda x: str(x), date_list))
yugao_all_df = get_latest_yugao(type='all', early_year=stats_year * 10000 + 101, late_year=stats_year * 10000 + 1231)
yugao_all_df = yugao_all_df.sort_values(['股票名称', '预告公告日']).drop_duplicates(['股票名称', '预告公告日'], keep='first')
yugao_all_df = yugao_all_df.sort_values('预告首次交易日')
yugao_all_df['预告营业收入下限'].isna().sum() / len(yugao_all_df)
yugao_all_df['预告扣除后营业收入下限'].isna().sum() / len(yugao_all_df)

yugao_all_df['is_loss'] = yugao_all_df['预告类型'].apply(lambda x: x in ['续亏', '首亏'])
yugao_all_df['is_nan'] = yugao_all_df['预告扣除后营业收入下限'].apply(lambda x: np.isnan(x))
yugao_all_df = yugao_all_df.query('(is_loss == True and is_nan == False) or (is_loss == False)')

yugao_all_df = yugao_all_df.query('预告首次交易日 <= 20241231')

#%% 从首次交易日到披露日前的所有时间，统计这段时间样本的label信息
nianbao_all_df = get_latest_nianbao(type='all', early_year=stats_year * 10000 + 101, late_year=stats_year * 10000 + 1231)

#%% 数据处理并统计
yg_df = yugao_all_df[['股票代码', '预告类型', '预告首次交易日']].set_index('股票代码')
nb_df = nianbao_all_df[['股票代码', '年报预计披露日', '预计披露日期公告日', '预计披露日期首次交易日']].set_index('股票代码')
concat_df = pd.merge(yg_df, nb_df, left_index=True, right_index=True, how='left')
concat_df = concat_df.reset_index()
concat_df['年报预计披露日'] = concat_df['年报预计披露日'].fillna(str((stats_year + 1) * 10000 + 430)).map(int)

europa_df = pd.read_hdf('/data/group/800463/sunss/europa/profit/20240828/LabelProfit_zt_twap_0.10_2000_300_SH100_SZ10.h5')

start, end = 20200101, 20250131
basic = IO.read_data([start,end],alt='/data/group/800463/project/project1_prod/left_v2310/Basic_zt_test/Basic_zt_001.h5')
label = IO.read_data([start,end],alt='/data/group/800463/project/project1_prod/left_v2310/Label_zt_test/Label_zt_001.h5')
all_df = basic.join(label)
filter_df = all_df[(all_df['ZT_Time'] >= 93000000) & (all_df['ZT_Time'] <= 143000000) & (all_df['open_is_zt'] == 0)
                   & (all_df['T_o2pre'] >= -0.05) & (all_df['after_not_ul_len'] > 10) & (all_df['pre_close'] >= 2)
                   & (all_df['high_price'] < (all_df['trigger_price'])) & (all_df['last_is_zt'] == 0)].copy()

europa_df = europa_df.loc[filter_df.index]
europa_df = europa_df.reset_index()
europa_df['trade_date'] = europa_df['dt'].apply(lambda x: int(x.strftime('%Y%m%d')))

#%% 统计发布预告后到年报预计披露日前
res = pd.DataFrame()
for idx in tqdm(range(len(concat_df))):
    row = concat_df.iloc[idx]
    stock_code = row['股票代码']
    date_list = tradeDate.get_date_range(row['预告首次交易日'], row['年报预计披露日'])
    tmp = europa_df.query(f'Ticker == "{stock_code}" and trade_date in {date_list}')
    tmp['预告首次交易日'] = row['预告首次交易日']
    tmp['年报预计披露日'] = row['年报预计披露日']
    tmp['预告类型'] = row['预告类型']
    res = pd.concat([res, tmp])

res1 = res.groupby('预告类型').agg({'Ticker': 'count', 'pct': ('min', 'max', 'mean', 'median')})

#%% 统计年报预计披露日前10天到年报预计披露日前
ress = pd.DataFrame()
for idx in range(len(concat_df)):
    row = concat_df.iloc[idx]
    stock_code = row['股票代码']
    date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(row['年报预计披露日'], 10), row['年报预计披露日'])
    tmp = europa_df.query(f'Ticker == "{stock_code}" and trade_date in {date_list}')
    tmp['预告首次交易日'] = row['预告首次交易日']
    tmp['年报预计披露日'] = row['年报预计披露日']
    tmp['预告类型'] = row['预告类型']
    ress = pd.concat([ress, tmp])

ress1 = ress.groupby('预告类型').agg({'Ticker': 'count', 'pct': ('min', 'max', 'mean', 'median')})

res_dict = {f'{stats_year}年度原始数据': res,
            f'{stats_year}按预告类型分类': res1,
            f'{stats_year}年度原始数据前10天': ress,
            f'{stats_year}按预告类型前10天': ress1}
from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(res_dict, '/data/user/015614/junkData/', f'{stats_year}业绩预告后样本表现.xlsx')
from dataApi.sendInfo import send_file
send_file(f'/data/user/015614/junkData/{stats_year}业绩预告后样本表现.xlsx')