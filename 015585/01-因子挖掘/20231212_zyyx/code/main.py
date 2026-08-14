import pandas as pd
import os
import IO
import datetime
'''
der_prob_excess_stock 表数据暂时缺失，待沟通获取
1、分析师最新预期 > 分析师历史预期
2、最新基本面信息 > 分析师历史预期
3、最新基本面信息 > 历史基本面预期
'''
'''
财报跳空因子JOR
1、T日发布财报，则T-2到T+1的累计超额收益为因子值
2、T日发布财报，T+1日最低价相对于前收盘价的涨跌幅 - 中证1000
3、超预期事件
'''
'''
整体思路：
1、根据标题等，在固定时间点选出文本上超预期的股票池，时间一般为过去2个月
2、在超预期股票池中，根据JOR或者其他因子打分，选择靠前的（股票），可以处理为对行业打分
'''
'''
declare_date = 收入的日期（核心/分析师调升，文本标题/摘要） / 财报超预期 = 
report_year = 财报的就是财报的预告和年度 / 研报的预测年份 
'''
# 超预期股票池
##
df_ori = pd.read_excel('der_prob_excess_stock.xlsx')
df_ori['STOCK_CODE'] = df_ori['STOCK_CODE'].apply(lambda x : str(x).zfill(6))
df_ori['STOCK_CODE'] = df_ori['STOCK_CODE'].apply(lambda x : x + '.SH' if x.startswith('6') else x + '.SZ')
## 对每个交易日的过去2个月，选择满足：1）存在n篇或以上的标题超预期 2）5个以上上调预期净利润（1or2）的股票列表
md_data = IO.read_data([20160101, 20191231],
                      columns=['amt'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_data['is_beyond_est'] = 0
dt_list = list(set(md_data.index.get_level_values(0)))
dt_list.sort()
n1 = 1 # 标题/摘要超预期数量
n2 = 5 # 调升数量
for date in dt_list:
    df_ori_i = df_ori[(df_ori['DECLARE_DATE'] <= date) & (df_ori['DECLARE_DATE'] >= (date - datetime.timedelta(days = 30)))]
    #
    df_ori_i1 = df_ori_i[df_ori_i['INFORMATION_CODE'].isin([2011,2012])] # 筛选出标题/摘要超预期
    df_res1 = df_ori_i1.groupby('STOCK_CODE').count()['STOCK_NAME'].sort_values()
    set_res1 = set(df_res1[df_res1 >= n1].index)
    #
    df_ori_i2 = df_ori_i[df_ori_i['INFORMATION_CODE'].isin([213,215])] # 筛选出调升
    df_res2 = df_ori_i2.groupby('STOCK_CODE').count()['STOCK_NAME'].sort_values()
    set_res2 = set(df_res2[df_res2 >= n2].index)
    #
    res_list = list(set_res1.union(set_res2))
    print(date,res_list)
    res_list_adddate = []
    for j in res_list:
        res_list_adddate.append((date,j))
    md_data.loc[list(set(res_list_adddate) & set(md_data.index)),'is_beyond_est'] = 1
md_data.to_pickle('/data/user/015585/01-因子挖掘/20231212_zyyx/file/is_beyond_est.pkl')
## 计算多个因子打分值
