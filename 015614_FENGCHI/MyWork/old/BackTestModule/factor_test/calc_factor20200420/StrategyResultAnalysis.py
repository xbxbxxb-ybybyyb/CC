# coding: utf-8
# Author：fengchi863
# Date ：2020/4/21 8:44

import os
from tqdm import tqdm
import pandas as pd
from multiprocessing import Pool
import time

strat_result_root_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200420/'
os.chdir(strat_result_root_path)
file_name_list = os.listdir(strat_result_root_path)

xlxs_columns = '买入股票数	买入股票金额	卖出股票数	卖出股票金额	当日收盘持股数量	当日收盘持仓市值	日收益	日收益率	持有收益率	每日强平数量	指数收益率	每日alpha	每日持有alpha	每日交易alpha	累计收益率	累计超额收益率	持有天数	现货收益	基准收益	alpha	alpha胜率	买次数	卖次数	总次数	下午成交占比	14成交占比'
xlxs_columns = xlxs_columns.split(' ')[0].split('\t')

# file_dir = r'/data/group/800319/storeFactor/qrr_combine_factor20200420/'
file_dir = r'/data/group/800319/storeFactor/combine_ffactor20200421/'
factor_name_list = sorted([os.path.splitext(x)[0].replace(' ','') for x in os.listdir(file_dir)])

e = time.time()
# for turnover in [0.1, 0.3, 0.5]:
#     for num in num_list:
#         target_holding_num, buy_pool_num = num
def main(turnover, target_holding_num, buy_pool_num):
    bar = tqdm(factor_name_list)
    res = pd.DataFrame(columns=xlxs_columns)
    for idx, factor_name in enumerate(bar):
        # # test
        # file_name = 'alpha17 _evaluation_(0.1,200,400).xlsx'
        # factor_name = 'alpha17'

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
        res.loc[factor_name, '下午成交占比'] = tmp_df[[1330, 1400, 1430, 1500]].mean().sum()
        res.loc[factor_name, '14成交占比'] = tmp_df[[1430, 1500]].mean().sum()

    # 所有结果汇总完成
    print(factor_name, turnover, target_holding_num, buy_pool_num, '所有结果汇总完成')
    xlsx_index = 'boll3	alpha123	boll4	alpha23	alpha184	boll6	factor_dev02	boll5	alpha56	factor119	alpha16	factor_dev08	alpha168	boll7	alpha46	alpha153	alpha17	factor78	alpha52	alpha40	boll8	factor110	factor83	factor64	factor98	alpha31	alpha7	alpha13	alpha145	alpha9	factor74	alpha36	alpha18	factor_dev05	alpha126_2	factor91	factor99	factor105	alpha32	alpha47	alpha179	alpha41	factor101	factor69	factor_dev07	factor62	alpha19	alpha11	alpha45	alpha142	factor113	alpha181	factor68	factor72	alpha29	alpha191	alpha171	factor61	alpha151	alpha166	alpha5	alpha21	alpha35	factor90	alpha178	alpha48	alpha50	alpha14	alpha37	alpha3	alpha163	alpha42	factor63	alpha28	alpha1	alpha147	factor114	alpha135	boll10	factor_dev03	alpha25	alpha49	factor73	alpha176	alpha38	alpha22	alpha24	alpha139	alpha39	factor71	alpha141	alpha12	alpha59	alpha122	alpha134	factor118	factor112	alpha8	boll9	factor116	alpha6	boll12	alpha169	boll11	factor86	factor94	factor106	factor106	factor107	alpha43	alpha133_1	alpha156	factor92	alpha27'
    xlsx_index = xlsx_index.split(' ')[0].split('\t')

    para_description = pd.DataFrame({'挂单时长': 1,
                                     '挂单数量': target_holding_num / 200,
                                     '目标换手率': turnover,
                                     '买入股票池数量': buy_pool_num,
                                     '目标持仓数量': target_holding_num
                                     }, index=['参数值']).T

    #  读取日内因子描述表格，用于拼接
    factor_description_io = pd.io.excel.ExcelFile(strat_result_root_path + '日内因子净值回测结果_(0.1, 200, 400).xlsx')
    factor_summary = pd.read_excel(factor_description_io, sheet_name='汇总结果', index_col=0)
    factor_check = pd.read_excel(factor_description_io, sheet_name='check', index_col=0)
    factor_description = factor_check[['编号', '因子名称', '开发人员', '因子逻辑', '类别', '备注']]
    factor_description.sort_values(['因子名称'], inplace=True) # 不用对齐会根据index来对齐
    factor_description.set_index('编号', inplace=True)

    # res['编号'] = pd.Series(res.index).apply(lambda x: factor_description[factor_description['因子名称']==x].index.tolist()[0]).values
    # res.set_index('编号',inplace=True)

    # res2 = pd.concat([factor_description, res], axis=1)
    # res2 = res2.reindex(factor_check['编号'], axis=0) # 匹配编号

    with pd.ExcelWriter('日内因子净值回测结果(22-33)_'+str((turnover, target_holding_num, buy_pool_num))+'.xlsx') as writer:
        para_description.to_excel(writer, '回测参数')
        factor_summary.to_excel(writer, '汇总结果')
        # factor_check.to_excel(writer, 'check')
        res.to_excel(writer, '与量比结合后的因子表现')

def wraper(para):
    turnover, target_holding_num, buy_pool_num = para
    main(turnover, target_holding_num, buy_pool_num)

para_list = []
num_list = [(200,400)]
for turnover in [0.1]:
    for num in num_list:
        target_holding_num, buy_pool_num = num
        para_list.append((turnover, target_holding_num, buy_pool_num))
pool = Pool(9)
r = pool.map(wraper, para_list)
pool.close()
pool.join()
print('汇总所需时间', time.time()-e)