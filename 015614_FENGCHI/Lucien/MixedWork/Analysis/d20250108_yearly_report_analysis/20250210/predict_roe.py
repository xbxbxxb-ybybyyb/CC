# coding: utf-8
# Author：fengchi863
# Date ：2025/2/14 10:36

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
fd = FactorData()

#%% 存在一些股票如果最近三年内都没有进行过分红，那么就没有这只股票的样本，所以要获取一下全部股票样本
from dataApi.stockList import get_all_stock_ever_appear, trans_int2windcode
all_stock_list = get_all_stock_ever_appear(20201231)
all_stock_list = list(map(lambda x: trans_int2windcode(x), all_stock_list))

table_name = 'AShareDividend'
year_list = ['20211231', '20221231', '20231231']

#%% 归属于不同年份的分红值，这条在Wind终端上的信息一致，但是Wind终端上显示的近3年现金分红值，和列出的分红总额有出入
share_divide_df = fd.get_factor_value('WIND_' + table_name, REPORT_PERIOD=['>=%d' % 20210101, '<=%d' % 20241231])
# check = share_divide_df.query('S_INFO_WINDCODE == "000925.SZ"')
# check = share_divide_df.query('S_INFO_WINDCODE == "000933.SZ"')
# check = share_divide_df.query('"20230501" < REPORT_PERIOD < "20231231"')
# check = share_divide_df.query('"20241201" < REPORT_PERIOD < "20241231"')
col = ['REPORT_PERIOD', 'S_INFO_WINDCODE', 'TOT_CASH_DVD', 'S_DIV_PRELANDATE']
raw_date_predict = share_divide_df[col]
raw_date_predict['REPORT_YEAR'] = raw_date_predict['REPORT_PERIOD'].map(lambda x: x[:4])
raw_date_predict['所属年份'] = raw_date_predict['REPORT_YEAR'].map(int)
raw_date_predict = raw_date_predict.dropna()
raw_date_predict = raw_date_predict.groupby(['S_INFO_WINDCODE', '所属年份']).sum().reset_index()
# check = raw_date_predict.query('S_INFO_WINDCODE == "000925.SZ"')
# check = raw_date_predict.query('S_INFO_WINDCODE == "000008.SZ"')
# check = raw_date_predict.query('REPORT_PERIOD == "20231231"')
# check = check.sort_values('S_DIV_PRELANDATE')

# all_stock_list_index = pd.MultiIndex.from_product([all_stock_list, year_list])
# raw_date_predict.set_index(['S_INFO_WINDCODE', '所属年份']).reindex()

#%% 获取全年净利润，经核查，利润正确
yugao_table_name = 'AShareIncome'   # 全年净利润
nianbao = fd.get_factor_value('WIND_' + yugao_table_name, REPORT_PERIOD=['>=%d' % 20211231, '<=%d' % 20241231])
# check = nianbao.query('S_INFO_WINDCODE == "000812.SZ"')
col = ['REPORT_PERIOD', 'S_INFO_WINDCODE', 'NET_PROFIT_INCL_MIN_INT_INC', 'TOT_OPER_REV', 'STATEMENT_TYPE']
nianbao = nianbao[col]
nianbao = nianbao.query(f'REPORT_PERIOD in {year_list} and STATEMENT_TYPE == "408001000"')  # 只筛选年报的利润
nianbao['所属年份'] = nianbao['REPORT_PERIOD'].map(int)
nianbao = nianbao.sort_values(['S_INFO_WINDCODE', '所属年份', 'NET_PROFIT_INCL_MIN_INT_INC'])
nianbao = nianbao.drop_duplicates(['S_INFO_WINDCODE', '所属年份', 'NET_PROFIT_INCL_MIN_INT_INC'], keep='first')
nianbao['所属年份'] = nianbao['REPORT_PERIOD'].map(lambda x: int(x) // 10000)
# check = nianbao.query('S_INFO_WINDCODE == "000925.SZ"')
# check = nianbao.query('S_INFO_WINDCODE == "000007.SZ"')

#%% 期末未分配利润表
table_name = 'AShareUndistributedProfit'
unprofit_df = fd.get_factor_value('WIND_' + table_name, REPORT_PERIOD=['>=%d' % 20211231, '<=%d' % 20241231],
                                  ITEM_DATA='未分配利润', ANN_ITEM='期末未分配利润(未分配利润)')
col = ['REPORT_PERIOD', 'S_INFO_COMPCODE', 'ITEM_TYPE_CODE', 'ITEM_AMOUNT']
unprofit_df = unprofit_df[col]
unprofit_df = unprofit_df.query('ITEM_TYPE_CODE == "2901"')

id_table_name = 'WindCustomCode'
id_df = fd.get_factor_value('WIND_' + id_table_name, S_INFO_COUNTRYCODE='CN', S_INFO_SECTYPEBCODE='100001000')
unprofit_df2 = pd.merge(unprofit_df, id_df[['S_INFO_COMPCODE', 'S_INFO_WINDCODE']], how='left', on='S_INFO_COMPCODE')
unprofit_df2 = unprofit_df2[['S_INFO_WINDCODE', 'REPORT_PERIOD', 'ITEM_AMOUNT', 'ITEM_TYPE_CODE']].sort_values(['S_INFO_WINDCODE', 'REPORT_PERIOD'])
unprofit_df2 = unprofit_df2.drop_duplicates('S_INFO_WINDCODE', keep='last')
unprofit_df2 = unprofit_df2[unprofit_df2['S_INFO_WINDCODE'].map(lambda x: x[-2:] in ['SH', 'SZ', 'BJ'])]
net_un_profit_stock_list = unprofit_df2.query('ITEM_AMOUNT < 0')['S_INFO_WINDCODE'].tolist()

#%% 合并净利润和现金分红表，计算每年的股利支付率
concat_df = pd.merge(nianbao, raw_date_predict, on=['S_INFO_WINDCODE', '所属年份'], how='left')
concat_df['TOT_CASH_DVD'] = concat_df['TOT_CASH_DVD'].fillna(0)
concat_df = concat_df.sort_values(['S_INFO_WINDCODE', '所属年份'])
concat_df['yearly_roe'] = concat_df['TOT_CASH_DVD'] / concat_df['NET_PROFIT_INCL_MIN_INT_INC']
# check = concat_df.query('S_INFO_WINDCODE == "000925.SZ"')
# check = concat_df.query('S_INFO_WINDCODE == "000007.SZ"')
check = concat_df.query('S_INFO_WINDCODE == "600858.SH"')

print(1)

# check = concat_df.groupby('S_INFO_WINDCODE').count()
# check = concat_df.query('NET_PROFIT_INCL_MIN_INT_INC < 0') # 有272条，净利润为负，仍然分红
concat_df['yearly_roe'] = concat_df[['yearly_roe', 'NET_PROFIT_INCL_MIN_INT_INC']].apply(lambda x: x['yearly_roe'] if x['NET_PROFIT_INCL_MIN_INT_INC'] > 0 else 0, axis=1)
group_df = concat_df.groupby('S_INFO_WINDCODE')['yearly_roe'].mean()    # 近三年平均ROE作为新的一年ROE
# len(group_df)
# check = group_df["000925.SZ"]
# check = group_df["000007.SZ"]

#%% 获取业绩预告信息，然后拼接
yugao_table_name = 'AShareProfitNotice'
raw_yugao_df = fd.get_factor_value('WIND_' + yugao_table_name, S_PROFITNOTICE_PERIOD=['20241231'])
col = ['S_INFO_WINDCODE', 'S_PROFITNOTICE_STYLE', 'S_PROFITNOTICE_NETPROFITMIN', 'S_PROFITNOTICE_PERIOD', '预告类型']
yugao_kind_dict = {454001000: '不确定',
                       454002000: '略减',
                       454003000: '略增',
                       454004000: '扭亏',
                       454005000: '其他',
                       454006000: '首亏',
                       454007000: '续亏',
                       454008000: '续盈',
                       454009000: '预减',
                       454010000: '预增',
                       }
raw_yugao_df['预告类型'] = raw_yugao_df['S_PROFITNOTICE_STYLE'].apply(lambda x: yugao_kind_dict[x])
raw_yugao_df = raw_yugao_df[col]
# check = raw_yugao_df[raw_yugao_df['S_PROFITNOTICE_NETPROFITMIN'].isna()]

filter_col = ['略减', '略增', '扭亏', '其他', '续盈', '预减', '预增']
raw_yugao_df = raw_yugao_df.query(f'预告类型 in {filter_col}')
# 匹配标准： 最近一个会计年度净利润为正值且母公司报表年度末未分配利润为正值的公司，
# 其最近三个会计年度累计现金分红总额低于最近三个会计年度年均净利润的30%，且最近三个会计年度累计现金分红金额低于5000万元
append_df = pd.DataFrame(index=range(len(raw_yugao_df)), columns=['S_INFO_WINDCODE', 'REPORT_PERIOD', 'NET_PROFIT_INCL_MIN_INT_INC', 'yearly_roe'])
for idx in range(len(raw_yugao_df)):
    stock_code = raw_yugao_df.iloc[idx]['S_INFO_WINDCODE']
    net_profit = raw_yugao_df.iloc[idx]['S_PROFITNOTICE_NETPROFITMIN']
    report_period = '20241231'
    if stock_code in group_df.index.tolist():
        yearly_roe = group_df.loc[stock_code]
    else:
        yearly_roe = np.nan

    append_df.loc[idx, 'S_INFO_WINDCODE'] = stock_code
    append_df.loc[idx, 'REPORT_PERIOD'] = report_period
    append_df.loc[idx, 'NET_PROFIT_INCL_MIN_INT_INC'] = net_profit
    append_df.loc[idx, 'yearly_roe'] = yearly_roe

append_df['predict_TOT_CASH_DVD'] = append_df['NET_PROFIT_INCL_MIN_INT_INC'] * append_df['yearly_roe']
# check = append_df.query('S_INFO_WINDCODE == "000925.SZ"')
# check = append_df.query('S_INFO_WINDCODE == "000007.SZ"')

# 判断2024年已发放现金分红
append_df['所属年份'] = append_df['REPORT_PERIOD'].map(lambda x: int(x[:4]))
has_fenhong2024 = raw_date_predict.query('所属年份 == 2024')
append_df = pd.merge(append_df, has_fenhong2024, on=['S_INFO_WINDCODE', '所属年份'], how='left')
append_df['TOT_CASH_DVD'] = append_df['TOT_CASH_DVD'] / 1e4
# check = append_df.query('S_INFO_WINDCODE == "000925.SZ"')
# (append_df['predict_TOT_CASH_DVD'] > append_df['TOT_CASH_DVD']).sum()   # 有165条记录满足条件
append_df['predict_TOT_CASH_DVD_fix'] = append_df[['predict_TOT_CASH_DVD', 'TOT_CASH_DVD']].apply(lambda x: max(x['predict_TOT_CASH_DVD'], x['TOT_CASH_DVD']), axis=1)
append_df['predict_TOT_CASH_DVD_fix'] = append_df['predict_TOT_CASH_DVD_fix'].fillna(0)
append_df['TOT_CASH_DVD'] = append_df['predict_TOT_CASH_DVD_fix']
# 剔除掉发布了业绩预告但是净利润下限为空值的
# check = append_df.loc[~append_df['NET_PROFIT_INCL_MIN_INT_INC'].isna()]
# check = append_df.query('S_INFO_WINDCODE == "000925.SZ"')
# check = append_df.query('S_INFO_WINDCODE == "000007.SZ"')

# 和之前年份的进行拼接，取最近3年
concat_df = pd.concat([concat_df, append_df])
year_list = ['2022', '2023', '2024']
concat_df = concat_df.query(f'所属年份 in {year_list}')
stats_num = concat_df.groupby('S_INFO_WINDCODE')['所属年份'].count()
stock_list = stats_num[stats_num==3].index.tolist() # 只有这些满足三年都有值的条件，且最近一个会计年度利润为正值，主要是预告个数就不多
print(f'原本有{len(stock_list)}只个股')
stock_list = list(set(stock_list).difference(set(net_un_profit_stock_list)))    # 去除最近一个报告期净利润为负的个股
print(f'去除未分配净利润为负之后有{len(stock_list)}只个股')

# check = concat_df.query('S_INFO_WINDCODE == "920002.BJ"')
# len(stock_list)

concat_df['NET_PROFIT_INCL_MIN_INT_INC'] = concat_df['NET_PROFIT_INCL_MIN_INT_INC'].fillna(0)

cond1 = concat_df.groupby('S_INFO_WINDCODE').agg({'NET_PROFIT_INCL_MIN_INT_INC': np.nanmean,
                                                  'TOT_CASH_DVD': np.nansum}, axis=1)
cond1['ratio'] = cond1['TOT_CASH_DVD'] / cond1['NET_PROFIT_INCL_MIN_INT_INC'] * 1e4 # 三年分红总额 / 年平均净利润
cond1 = cond1.loc[stock_list]
len(stock_list)
cond1['是否为主板'] = cond1.index.map(lambda x: x[0] in ['6', '0'] and x[:3] not in ['688'])
cond1['是否为主板'] = cond1['是否为主板'].fillna(False)

check1 = cond1.query('0 <= ratio < 0.3 and TOT_CASH_DVD < 5e7 and 是否为主板 == True')
check2 = cond1.query('0 <= ratio < 0.3 and TOT_CASH_DVD < 3e7 and 是否为主板 == False')
res = pd.concat([check1, check2], axis=0)
res = res.sort_values('S_INFO_WINDCODE')

#%% 增加上市天数列
list_date = pd.read_excel('/data/user/015614/junkData/全市场个股上市日期补充.xlsx')
res = pd.merge(res, list_date, how='left', left_on=['S_INFO_WINDCODE'], right_on=['证券代码'])


res_dict = {'不符合分红标准的个股': res,
            '年度现金分红金额': raw_date_predict,
            '年度净利润': nianbao,
            '未分配净利润': unprofit_df2,
            '股利支付率计算': append_df,
            '最新预测': cond1}
from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(res_dict, '/data/user/015614/junkData/', '现金分红条件筛选个股.xlsx')
from dataApi.sendInfo import send_file
send_file('/data/user/015614/junkData/现金分红条件筛选个股.xlsx')
"""
存在一部分股票，明明进行了分红，但是从数据中没有看到分红，比如000925.SZ，在2024年下半年的1000万分红【已解决】
一部分股票从来没有进行过分红，这部分需要设置ratio==0进行筛选【已解决】
发现筛选出很多归母净利润未分配 为负 的个股，这部分个股要进行剔除，使用去年的未分配归母净利润进行剔除【已解决】
"""