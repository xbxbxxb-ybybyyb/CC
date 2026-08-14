# coding: utf-8
# Author：fengchi863
# Date ：2020/4/16 10:29
import os
from tqdm import tqdm
import pandas as pd
from multiprocessing import Pool
import time

strat_result_root_path = '/data/group/800319/junkData/temp_factor_by_fc/StrategyBackTest/strats_append_with_defalt_factor_20200415/'
os.chdir(strat_result_root_path)
file_name_list = os.listdir(strat_result_root_path)

xlxs_columns = '买入股票数	买入股票金额	卖出股票数	卖出股票金额	当日收盘持股数量	当日收盘持仓市值	日收益	日收益率	持有收益率	每日强平数量	指数收益率	每日alpha	每日持有alpha	每日交易alpha	累计收益率	累计超额收益率	持有天数	现货收益	基准收益	alpha	alpha胜率	买次数	卖次数	总次数	下午成交占比	14成交占比'
xlxs_columns = xlxs_columns.split(' ')[0].split('\t')

file_dir = r'/data/group/800319/storeFactor'
factor_name_list = sorted([os.path.splitext(x)[0].replace(' ','') for x in os.listdir(file_dir)])
factor_name_list.remove('corrcoef')

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
    xlsx_index = 'alpha1	alpha2	alpha3	alpha4	alpha5	alpha6	alpha7	alpha8	alpha9	alpha10	alpha11	alpha12	alpha13	alpha14	alpha16	alpha17	alpha18	alpha19	alpha21	alpha22	alpha23	alpha24	alpha25	alpha27	alpha28	alpha29	alpha31	alpha32	alpha35	alpha36	alpha37	alpha38	alpha39	alpha40	alpha41	alpha42	alpha43	alpha45	alpha46	alpha47	alpha48	alpha49	alpha50	alpha52	alpha53	alpha55	alpha56	alpha57	alpha58	alpha59	alpha60	boll1	boll2	boll3	boll4	boll5	boll6	boll7	boll8	boll9	boll10	boll11	boll12	factor63	factor98	factor118	factor72	factor107	factor69	factor114	factor68	factor99	factor113	factor64	factor105	factor90	factor62	factor91	factor83	factor101	factor73	factor119	factor74	factor_dev04	factor81	factor_dev02	factor120	factor106	factor_dev05	factor_dev07	factor86	factor106	factor78	factor_dev03	factor_dev08	factor71	factor_dev01	factor61	factor116	factor110	factor87	factor92	factor103	factor75	factor94	factor112	alpha122	alpha123	alpha124	alpha126_1	alpha126_2	alpha127	alpha129	alpha133_1	alpha133_2	alpha134	alpha135	alpha139	alpha140	alpha141	alpha142	alpha145	alpha147	alpha151	alpha153	alpha156	alpha161	alpha163	alpha164	alpha166	alpha167	alpha168	alpha169	alpha170	alpha171	alpha174	alpha180	alpha181	alpha184	alpha187	alpha188	alpha189	alpha191	alpha175	alpha176	alpha177	alpha178	alpha179'
    xlsx_index = xlsx_index.split(' ')[0].split('\t')
    res = res.reindex(index=xlsx_index).reset_index()
    para_description = pd.DataFrame({'挂单时长': 1,
                                     '挂单数量': target_holding_num / 200,
                                     '目标换手率': turnover,
                                     '买入股票池数量': buy_pool_num,
                                     '目标持仓数量': target_holding_num
                                     }, index=['参数值']).T
    #  读取日内因子描述表格，用于拼接
    factor_description = pd.read_excel(strat_result_root_path+'日内因子测试简要结果.xlsx')
    factor_description = factor_description[['编号','因子名称','开发人员','因子逻辑','类别','备注']]
    # factor_description.sort_values(['因子名称'], inplace=True) # 不用对齐会根据index来对齐
    res.sort_values(['index'], inplace=True)
    res2 = pd.concat([factor_description, res], axis=1)
    res2.drop('index', axis=1, inplace=True)
    with pd.ExcelWriter('日内因子净值回测结果_'+str((turnover, target_holding_num, buy_pool_num))+'.xlsx') as writer:
        para_description.to_excel(writer, '回测参数')
        res2.to_excel(writer, '汇总结果')

def wraper(para):
    turnover, target_holding_num, buy_pool_num = para
    main(turnover, target_holding_num, buy_pool_num)

para_list = []
num_list = [(200,400), (300,600), (500,800)]
for turnover in [0.1, 0.3, 0.5]:
    for num in num_list:
        target_holding_num, buy_pool_num = num
        para_list.append((turnover, target_holding_num, buy_pool_num))
pool = Pool(9)
r = pool.map(wraper, para_list)
pool.close()
pool.join()
print('汇总所需时间', time.time()-e)