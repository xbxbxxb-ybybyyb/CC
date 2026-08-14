# coding: utf-8
# Author：fengchi863
# Date ：2025/1/9 13:52

from MixedWork.Analysis.d20250108_yearly_report_analysis.System import *
import time
from LucienUtil import IO
from xquant.factordata import FactorData
from dataApi.tradeDate import get_date_range

def get_latestN(dat, N=30):
    date_list = get_date_range(dat, tradeDate.get_pre_trade_date(dat, -N + 1))
    return list(map(lambda x: str(x), date_list))

def get_lives_day(dat, base_date):
    if base_date < 20170101:
        return 5000
    else:
        return tradeDate.get_trade_date_interval(dat, base_date)

t1 = time.time()

fd = FactorData()
# date_list = get_date_range(20231101, 20250116)
# date_list = list(map(lambda x: str(x), date_list))
# yugao_all_df = get_latest_yugao(type='all', early_year=20240101)

date_list = get_date_range(20211101, 20220930)
date_list = list(map(lambda x: str(x), date_list))
yugao_all_df = get_latest_nianbao(type='all', early_year=20210101, late_year=20211231)
yugao_all_df = yugao_all_df.sort_values(['股票代码', '预计披露日期首次交易日']).drop_duplicates(['股票代码', '预计披露日期首次交易日'], keep='first')
yugao_all_df = yugao_all_df.sort_values('预计披露日期首次交易日')
# yugao_all_df = yugao_all_df.query('预告首次交易日 <= 20241231')

stock_list = list(set(yugao_all_df['股票代码'].tolist()))
stock_list = list(filter(lambda x: not str(x).endswith('BJ'), stock_list))
# stock_list = list(filter(lambda x: not str(x).startswith('688'), stock_list))
yugao_all_df = yugao_all_df.query(f'股票代码 in {stock_list}')
yugao_all_df = yugao_all_df.set_index(['预计披露日期首次交易日', '股票代码'])
yugao_all_df.index.names = ['mddate', 'stock']
yugao_all_df = yugao_all_df.reset_index()

daily_data = fd.get_factor_value('Basic_factor', factor_names=['pre_close_badj', 'close_badj', 'open_badj', 'high_badj', 'stpt', 'mdc_maxpx','adjfactor', 'maxupordown'], mddate=date_list, stock=stock_list)
new_data = fd.get_factor_value('Basic_factor', stock_list, [], ['listing_date'])
yugao_all_df = yugao_all_df.loc[(~yugao_all_df['mddate'].isna())]
yugao_all_df['mddate'] = yugao_all_df['mddate'].map(int)
yugao_all_df['距离上市日期天数'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: get_lives_day(x['mddate'], base_date=new_data.loc[x['stock'], 'listing_date']), axis=1)
yugao_all_df = yugao_all_df.query('距离上市日期天数 > 0')
yugao_all_df = yugao_all_df.query('年报预计披露日首次交易日 > 0')
print(yugao_all_df.shape)
print(len(stock_list))

yugao_all_df['距离0430距离'] = yugao_all_df['年报预计披露日首次交易日'].apply(lambda x: tradeDate.get_trade_date_interval(x, base_date=20220430) + 1)

def get_bin(x):
    if x > 0: return -1
    if x == 0: return 0
    if -3 <= x <=-1: return 1
    if -15 <= x <= -4: return 2
    if -30 <= x <= -16: return 3
    if -60 <= x <= -31: return 4
    if x < -60: return 5

yugao_all_df['距离范围'] = yugao_all_df['距离0430距离'].apply(lambda x: get_bin(x))

#%% 加入index涨跌幅
index_data = fd.get_factor_value('Basic_factor', factor_names=['pre_close'], mddate=date_list, stock=['000905.SH'])
index_data_unstack = index_data['pre_close'].unstack()
index_pct1 = index_data_unstack.shift(-1) / index_data_unstack - 1
index_pct5 = index_data_unstack.shift(-5) / index_data_unstack - 1
index_pct10 = index_data_unstack.shift(-10) / index_data_unstack - 1

# 统计涨跌幅
daily_data['limit_max'] = daily_data['adjfactor'] * daily_data['mdc_maxpx']
daily_data_pre_close_badj_unstack = daily_data['pre_close_badj'].unstack()
pct1 = daily_data_pre_close_badj_unstack.shift(-1) / daily_data_pre_close_badj_unstack - 1
pct5 = daily_data_pre_close_badj_unstack.shift(-5) / daily_data_pre_close_badj_unstack - 1
pct10 = daily_data_pre_close_badj_unstack.shift(-10) / daily_data_pre_close_badj_unstack - 1

pct1_alpha = pd.DataFrame(pct1.values - index_pct1.values, index=pct1.index, columns=pct1.columns)
pct5_alpha = pd.DataFrame(pct5.values - index_pct5.values, index=pct5.index, columns=pct5.columns)
pct10_alpha = pd.DataFrame(pct10.values - index_pct10.values, index=pct10.index, columns=pct10.columns)

yugao_all_df['pct1'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: pct1.loc[str(x['mddate']), x['stock']], axis=1)
yugao_all_df['pct5'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: pct5.loc[str(x['mddate']), x['stock']], axis=1)
yugao_all_df['pct10'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: pct10.loc[str(x['mddate']), x['stock']], axis=1)

yugao_all_df['pct1_alpha'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: pct1_alpha.loc[str(x['mddate']), x['stock']], axis=1)
yugao_all_df['pct5_alpha'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: pct5_alpha.loc[str(x['mddate']), x['stock']], axis=1)
yugao_all_df['pct10_alpha'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: pct10_alpha.loc[str(x['mddate']), x['stock']], axis=1)

# 统计被ST的可能
st_df = daily_data['stpt'].unstack()
st_df = st_df.fillna(0).applymap(int) - st_df.fillna(0).applymap(int).shift(1)

yugao_all_df['1天内是否被ST'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: st_df.loc[get_latestN(x['mddate'], 1), x['stock']].fillna(0).map(int).sum(), axis=1) > 0
yugao_all_df['5天内是否被ST'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: st_df.loc[get_latestN(x['mddate'], 5), x['stock']].fillna(0).map(int).sum(), axis=1) > 0
yugao_all_df['10天内是否被ST'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: st_df.loc[get_latestN(x['mddate'], 10), x['stock']].fillna(0).map(int).sum(), axis=1) > 0

yugao_all_df['1天内是否被ST'] = yugao_all_df['1天内是否被ST'] > 0
yugao_all_df['5天内是否被ST'] = yugao_all_df['5天内是否被ST'] > 0
yugao_all_df['10天内是否被ST'] = yugao_all_df['10天内是否被ST'] > 0

# 统计跌停情况
zdt_df = daily_data['maxupordown'].unstack()

yugao_all_df['1天内跌停次数'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: (zdt_df.loc[get_latestN(x['mddate'], 1), x['stock']].fillna(0).map(int) == -1).sum(), axis=1)
yugao_all_df['5天内跌停次数'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: (zdt_df.loc[get_latestN(x['mddate'], 5), x['stock']].fillna(0).map(int) == -1).sum(), axis=1)
yugao_all_df['10天内跌停次数'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: (zdt_df.loc[get_latestN(x['mddate'], 10), x['stock']].fillna(0).map(int) == -1).sum(), axis=1)

yugao_all_df['1天内是否跌停'] = yugao_all_df['1天内跌停次数'] > 0
yugao_all_df['5天内是否跌停'] = yugao_all_df['5天内跌停次数'] > 0
yugao_all_df['10天内是否跌停'] = yugao_all_df['10天内跌停次数'] > 0

# 统计涨停情况
yugao_all_df['1天内涨停次数'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: (zdt_df.loc[get_latestN(x['mddate'], 1), x['stock']].fillna(0).map(int) == 1).sum(), axis=1)
yugao_all_df['5天内涨停次数'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: (zdt_df.loc[get_latestN(x['mddate'], 5), x['stock']].fillna(0).map(int) == 1).sum(), axis=1)
yugao_all_df['10天内涨停次数'] = yugao_all_df[['mddate', 'stock']].apply(lambda x: (zdt_df.loc[get_latestN(x['mddate'], 10), x['stock']].fillna(0).map(int) == 1).sum(), axis=1)

yugao_all_df['1天内是否涨停'] = yugao_all_df['1天内涨停次数'] > 0
yugao_all_df['5天内是否涨停'] = yugao_all_df['5天内涨停次数'] > 0
yugao_all_df['10天内是否涨停'] = yugao_all_df['10天内涨停次数'] > 0

yugao_all_df.to_pickle('/data/user/015614/junkData/yugao_all_df.pkl')


print('耗时', time.time() - t1)
print(1)

res = yugao_all_df[['mddate', 'stock', '距离范围', '距离0430距离', '年报预计披露日首次交易日', '年报预计披露日',
                    'pct1', 'pct5', 'pct10',
                    'pct1_alpha', 'pct5_alpha', 'pct10_alpha',
                    '1天内是否被ST', '5天内是否被ST', '10天内是否被ST',
                    '1天内涨停次数', '5天内涨停次数', '10天内涨停次数',
                    '1天内跌停次数', '5天内跌停次数', '10天内跌停次数',
                    '1天内是否涨停', '5天内是否涨停', '10天内是否涨停',
                    '1天内是否跌停', '5天内是否跌停', '10天内是否跌停']]
# res.to_excel('/data/user/015614/junkData/2024业绩预告结果.xlsx')
res.to_excel('/data/user/015614/junkData/2022年度年报披露结果.xlsx')

res2 = res.groupby('距离范围').agg({'mddate': 'count',
                                'pct1': np.mean, 'pct5': np.mean, 'pct10': np.mean,
                                'pct1_alpha': np.mean, 'pct5_alpha': np.mean, 'pct10_alpha': np.mean,
                                '1天内是否被ST': np.sum, '5天内是否被ST': np.sum, '10天内是否被ST': np.sum,
                                '1天内涨停次数': np.sum, '5天内涨停次数': np.sum, '10天内涨停次数': np.sum,
                                '1天内跌停次数': np.sum, '5天内跌停次数': np.sum, '10天内跌停次数': np.sum,
                                '1天内是否涨停': np.sum, '5天内是否涨停': np.sum, '10天内是否涨停': np.sum,
                                '1天内是否跌停': np.sum, '5天内是否跌停': np.sum, '10天内是否跌停': np.sum}, axis=1)
res2 = res2.rename({'mddate': '样本个数',
                    '1天内涨停次数': '1天内总涨停次数',
                    '1天内跌停次数': '1天内总跌停次数',
                    '5天内涨停次数': '5天内总涨停次数',
                    '5天内跌停次数': '5天内总跌停次数',
                    '10天内涨停次数': '10天内总涨停次数',
                    '10天内跌停次数': '10天内总跌停次数',
                    '1天内是否涨停': '1天内总涨停个股数',
                    '1天内是否跌停': '1天内总跌停个股数',
                    '5天内是否涨停': '5天内总涨停个股数',
                    '5天内是否跌停': '5天内总跌停个股数',
                    '10天内是否涨停': '10天内总涨停个股数',
                    '10天内是否跌停': '10天内总跌停个股数',
                    }, axis=1)
res2 = res2.rename({'mddate': '样本个数'}, axis=1)

output_dict = {'原始数据': res,
               '统计数据': res2}
from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(output_dict, '/data/user/015614/junkData/', '年报披露日公告后表现统计2021.xlsx')
from dataApi.sendInfo import send_file
send_file('/data/user/015614/junkData/年报披露日公告后表现统计2021.xlsx')
