# coding: utf-8
# Author：fengchi863
# Date ：2025/2/12 11:12

"""
判断业绩预告是否准确
"""

import pandas as pd
from MixedWork.Analysis.d20250108_yearly_report_analysis.System import *
import time
from LucienUtil import IO
from xquant.factordata import FactorData
from dataApi.tradeDate import get_date_range
from tqdm import tqdm


stats_year = 2023
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

yugao_table_name = 'AShareIncome'
nianbao = fd.get_factor_value('WIND_' + yugao_table_name, REPORT_PERIOD='20231231')

res = pd.DataFrame(columns=['股票代码', '实际净利润', '差值'])

for idx in tqdm(range(len(yugao_all_df))):
    try:
        profit, min_profit, max_profit = 0, 0, 0
        stk_code = yugao_all_df.iloc[idx]['股票代码']
        digest = yugao_all_df.iloc[idx]['预告摘要']
        if digest == '不确定':
            continue
        elif '-' in digest:
            digest = digest[6:]
            split_list = digest.split('-')
            if len(split_list) == 2:
                min_profit, max_profit = int(split_list[0]), int(split_list[1])
            else:
                min_profit, max_profit = -int(split_list[1]), -int(split_list[-1])
        else:
            profit = int(digest[6:])

        publish_start_date = (stats_year + 1) * 10000 + 101
        publish_end_date = (stats_year + 1) * 10000 + 1231
        tmp_nianbao = nianbao.query(f'WIND_CODE == "{stk_code}" and STATEMENT_TYPE == "408001000"')
        if len(tmp_nianbao) == 0:
            continue
        else:
            true_profit = tmp_nianbao['NET_PROFIT_INCL_MIN_INT_INC'].values[0] / 1e4    # 净利润(含少数股东损益)
            if profit != 0:
                diff = (true_profit - profit) / abs(true_profit)
            else:
                if min_profit != 0 and max_profit != 0:
                    if min_profit <= true_profit <= max_profit:
                        diff = 0
                    elif true_profit < min_profit:
                        diff = (true_profit - min_profit) / abs(true_profit)
                    elif true_profit > max_profit:
                        diff = (true_profit - max_profit) / abs(true_profit)

        res.loc[idx, '股票代码'] = stk_code
        res.loc[idx, '预告摘要'] = yugao_all_df.iloc[idx]['预告摘要']
        res.loc[idx, '预告类型'] = yugao_all_df.iloc[idx]['预告类型']
        res.loc[idx, '实际净利润'] = true_profit
        res.loc[idx, '差值'] = diff

        if res.loc[idx, '预告类型'] in ['续亏', '首亏'] and true_profit > 0:
            res.loc[idx, '是否反向'] = 1
        elif res.loc[idx, '预告类型'] not in ['续亏', '首亏'] and true_profit < 0:
            res.loc[idx, '是否反向'] = -1
        else:
            res.loc[idx, '是否反向'] = 0
    except:
        continue

def box(x):
    if x < -0.1:
        return '实际少，幅度大于10%'
    if -0.1 <= x <= -0.05:
        return '实际少，幅度在5%-10%'
    if -0.05 < x < 0:
        return '实际少，幅度小于5%'
    if x == 0:
        return '实际范围正常'
    if 0.05 > x > 0:
        return '实际多，幅度小于5%'
    if 0.05 <= x <= 0.1:
        return '实际多，幅度在5%-10%'
    if x > 0.1:
        return '实际多，幅度大于10%'

res['预测大小'] = res['差值'].apply(lambda x: box(x))
group = res.groupby(['预告类型', '预测大小'])['股票代码'].count()
save_dict = {'准确性比对原始数据': res,
             '统计数据': group}
from LucienUtil.FileUtil import FileUtil
FileUtil.save_dict2xls(save_dict, '/data/user/015614/junkData/', '预告准确率评测.xlsx')
from dataApi.sendInfo import send_file
send_file('/data/user/015614/junkData/预告准确率评测.xlsx')




