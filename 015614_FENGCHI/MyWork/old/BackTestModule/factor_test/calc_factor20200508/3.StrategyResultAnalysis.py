# coding: utf-8
# Author：fengchi863
# Date ：2020/5/8 16:34

import os
from tqdm import tqdm
import pandas as pd
from multiprocessing import Pool
import time

strat_result_root_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/boll_factor_20200508/'
boll_description_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/boll_description.xlsx'
os.chdir(strat_result_root_path)
file_name_list = os.listdir(strat_result_root_path)
factor_name_list = ['_'.join(x.split('_')[:2]) for x in file_name_list]

xlxs_columns = '买入股票数	买入股票金额	卖出股票数	卖出股票金额	当日收盘持股数量	当日收盘持仓市值	日收益	日收益率	持有收益率	每日强平数量	指数收益率	每日alpha	每日持有alpha	每日交易alpha	累计收益率	累计超额收益率	持有天数	现货收益	基准收益	alpha	alpha胜率	买次数	卖次数	总次数	下午成交占比	14成交占比'
xlxs_columns = xlxs_columns.split(' ')[0].split('\t')

e = time.time()
# for turnover in [0.1, 0.3, 0.5]:
#     for num in num_list:
#         target_holding_num, buy_pool_num = num
def main(turnover, target_holding_num, buy_pool_num):
    bar = tqdm(factor_name_list)
    res = pd.DataFrame(columns=xlxs_columns)
    for idx, factor_name in enumerate(bar):
        if factor_name.__contains__('evaluation'):
            factor_name = factor_name.split('_')[0]
        bar.set_description(factor_name+' '+str(turnover)+' '+str(target_holding_num)+' '+str(buy_pool_num))
        factor_evaluation_name = factor_name+'_evaluation_'+str((turnover, target_holding_num, buy_pool_num))
        if not os.path.exists(factor_evaluation_name+'.xlsx'):
            print(factor_evaluation_name, '不存在')
            continue

        tmp_io = pd.io.excel.ExcelFile(strat_result_root_path + factor_name+'_evaluation_'+str((turnover, target_holding_num, buy_pool_num))+'.xlsx')
        tmp_df = pd.read_excel(tmp_io, sheet_name='总体信息', index_col=0)
        res.loc[factor_name, '买入股票数'] = tmp_df['买入股票数'].mean()
        res.loc[factor_name, '买入股票金额'] = tmp_df['买入股票金额'].mean()
        res.loc[factor_name, '卖出股票数'] = tmp_df['卖出股票数'].mean()
        res.loc[factor_name, '卖出股票金额'] = tmp_df['卖出股票金额'].mean()
        res.loc[factor_name, '当日收盘持股数量'] = tmp_df['当日收盘持股数量'].mean()
        res.loc[factor_name, '当日收盘持仓市值'] = tmp_df['当日收盘持仓市值'].mean()
        res.loc[factor_name, '日收益'] = tmp_df['日收益'].mean()
        res.loc[factor_name, '日收益率'] = tmp_df['日收益率'].mean()
        res.loc[factor_name, '持有收益率'] = tmp_df['持有收益率'].mean()
        res.loc[factor_name, '每日强平数量'] = tmp_df['当日强平数量'].mean()
        res.loc[factor_name, '指数收益率'] = tmp_df['指数收益率'].mean()
        res.loc[factor_name, '每日alpha'] = tmp_df['每日alpha'].mean()
        res.loc[factor_name, '每日持有alpha'] = tmp_df['每日持有alpha'].mean()
        res.loc[factor_name, '每日交易alpha'] = tmp_df['每日交易alpha'].mean()
        res.loc[factor_name, '累计收益率'] = tmp_df['累计收益率'].iloc[-1]
        res.loc[factor_name, '累计超额收益率'] = tmp_df['累计超额收益率'].iloc[-1]

        tmp_df = pd.read_excel(tmp_io, sheet_name='每笔持仓统计', index_col=0)
        res.loc[factor_name, '持有天数'] = tmp_df['持有天数'].mean()
        res.loc[factor_name, '现货收益'] = tmp_df['现货收益'].mean()
        res.loc[factor_name, '基准收益'] = tmp_df['基准收益'].mean()
        res.loc[factor_name, 'alpha'] = tmp_df['alpha'].mean()

        tmp_df = pd.read_excel(tmp_io, sheet_name='收益胜率', index_col=0)
        res.loc[factor_name, 'alpha胜率'] = tmp_df.loc['alpha','胜率']
        res.loc[factor_name, '买次数'] = tmp_df.loc['买次数','均值']
        res.loc[factor_name, '卖次数'] = tmp_df.loc['卖次数','均值']
        res.loc[factor_name, '总次数'] = tmp_df.loc['总次数','均值']

        tmp_df = pd.read_excel(tmp_io, sheet_name='成交额日内分布', index_col=0)
        res.loc[factor_name, '下午成交占比'] = tmp_df[['H1330.0', 'H1400.0', 'H1430.0', 'H1500.0']].mean().sum()
        res.loc[factor_name, '14成交占比'] = tmp_df[['H1430.0', 'H1500.0']].mean().sum()

    # 所有结果汇总完成
    print(factor_name, turnover, target_holding_num, buy_pool_num, '所有结果汇总完成')

    para_description = pd.DataFrame({'目标换手率': turnover,
                                     '买入股票池数量': buy_pool_num,
                                     '目标持仓数量': target_holding_num
                                     }, index=['参数值']).T

    #  读取日内因子描述表格，用于拼接
    factor_description = pd.read_excel(boll_description_path, index_col=0)
    factor_description.set_index('因子名称', inplace=True)
    res = pd.concat([factor_description, res], axis=1)

    res.reset_index(inplace=True)
    res = res.rename({'index':'因子名称'}, axis=1)
    # 重新设置索引
    cols = xlxs_columns
    cols.insert(0, '因子名称')
    cols += ['因子逻辑', '类别', '备注']
    res = res[cols]

    res_output_file_name = strat_result_root_path + '日内因子净值回测结果(20200508新增)_' + \
                           str((turnover, target_holding_num, buy_pool_num)) + '.xlsx'
    with pd.ExcelWriter(res_output_file_name) as writer:
        para_description.to_excel(writer, '回测参数')
        res.to_excel(writer, '测试结果')

def wraper(para):
    turnover, target_holding_num, buy_pool_num = para
    main(turnover, target_holding_num, buy_pool_num)

para_list = []
num_list = [(200,400)]
for turnover in [0.5]:
    for num in num_list:
        target_holding_num, buy_pool_num = num
        para_list.append((turnover, target_holding_num, buy_pool_num))
pool = Pool(9)
r = pool.map(wraper, para_list)
pool.close()
pool.join()
print('汇总所需时间', time.time()-e)