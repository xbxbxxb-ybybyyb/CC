# coding: utf-8
# Author：fengchi863
# Date ：2020/4/24 13:23
'''
根据全量的回测结果进行汇总整合，一些指标会有修改，需要进行重新对齐
生成的结果文件保存在strat_result_root_path目录下
全量回测参考描述文件在上一层，所有excel文件也放在这一层，除了该文件以外，其他文件需要在文件名中增加时间说明

'''

import os
from tqdm import tqdm
import pandas as pd
from multiprocessing import Pool
import time

# 策略回测框架的result地址
strat_result_root_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200428/'
os.chdir(strat_result_root_path)
file_name_list = os.listdir(strat_result_root_path)

# 所需要统计的指标
xlsx_columns = '买入股票数	买入股票金额	卖出股票数	卖出股票金额	当日收盘持股数量	当日收盘持仓市值	日收益	日收益率	持有收益率	每日强平数量	指数收益率	每日alpha	每日持有alpha	每日交易alpha	累计收益率	累计超额收益率	持有天数	现货收益	基准收益	alpha	alpha胜率	买次数	卖次数	总次数	下午成交占比	14成交占比'
xlsx_columns = xlsx_columns.split(' ')[0].split('\t')

# 获取所有因子
file_dir = r'/data/group/800319/storeFactor/original_intrafactor/'
factor_name_list = sorted([os.path.splitext(x)[0] for x in os.listdir(file_dir)])
print(len(factor_name_list))

e = time.time()

def main(turnover, target_holding_num, buy_pool_num):
    bar = tqdm(factor_name_list)
    res = pd.DataFrame(columns=xlsx_columns)
    for idx, factor_name in enumerate(bar):
        # # test
        # file_name = 'alpha17 _evaluation_(0.1,200,400).xlsx'
        # factor_name = 'alpha17'

        bar.set_description(factor_name+' '+str(turnover)+' '+str(target_holding_num)+' '+str(buy_pool_num))
        factor_evaluation_name = factor_name+'_evaluation_'+str((turnover, target_holding_num, buy_pool_num))
        if not os.path.exists(factor_evaluation_name+'.xlsx'):
            print(factor_evaluation_name, '不存在')
            continue

        tmp_io = pd.io.excel.ExcelFile(strat_result_root_path + factor_evaluation_name +'.xlsx')
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
    res.reset_index(inplace=True)

    para_description = pd.DataFrame({'目标换手率': turnover,
                                     '买入股票池数量': buy_pool_num,
                                     '目标持仓数量': target_holding_num
                                     }, index=['参数值']).T

    #  读取日内因子描述表格，用于拼接
    factor_description = pd.read_excel('/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/' + \
                                                '因子全量测试专用.xlsx', index_col=0)
    factor_description = factor_description[['因子名称', '开发人员', '因子逻辑', '类别', '备注']]
    factor_description.sort_values(['因子名称'], inplace=True) # 源文件已经排序对齐了

    res = pd.concat([factor_description, res], axis=1)

    # 重新设置索引
    cols = xlsx_columns
    cols.insert(0, '因子名称')
    cols += ['因子逻辑', '类别', '备注']
    res = res[cols]

    res_output_file_name = strat_result_root_path + '日内因子净值回测结果(20200428全量)_'+ \
                           str((turnover, target_holding_num, buy_pool_num))+'.xlsx'
    with pd.ExcelWriter(res_output_file_name) as writer:
        para_description.to_excel(writer, '回测参数')
        res.to_excel(writer, '全量测试结果')

def wraper(para):
    turnover, target_holding_num, buy_pool_num = para
    main(turnover, target_holding_num, buy_pool_num)

para_list = []
num_list = [(200,400)]
for turnover in [0.1, 0.3, 0.5]:
    for num in num_list:
        target_holding_num, buy_pool_num = num
        para_list.append((turnover, target_holding_num, buy_pool_num))
pool = Pool(9)
r = pool.map(wraper, para_list)
pool.close()
pool.join()
print('汇总所需时间', '%.2f' % ((time.time()-e)/60))