# coding: utf-8
# Author：fengchi863
# Date ：2021/12/9 17:43

'''
网格搜索最优参数
对日均股票池个数最多的个股进行筛选
后续可以通过回测检测这些条件的有效性
'''

import numpy as np
import pandas as pd

from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.dataApi import tradeDate
from FaaMonitor.Util.tools import send_message

ma_types = {'type1': 'ma5>ma10>ma20>ma40>ma60',
            'type2': 'ma5>ma10>ma20>ma40',
            'type3': 'ma5>ma10>ma20',
            'type4': 'ma5>ma10',
            'type5': 'close>ma5>ma10>ma20',
            'type6': 'close>ma5>ma10',
            'type7': 'close>ma5',
            }

if __name__ == '__main__':
    start_date = 20200101
    end_date = 20211131

    ma_score_60d_enum = [40, 50, 60, 70]
    ma_score_120d_enum = [40, 50, 60, 70]
    dis60_enum = [0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4]
    ma_pct_enum = [0.4, 0.45, 0.5, 0.55, 0.6]

    score_60d = pd.read_pickle(junk_path + 'ma_score60.pkl')
    score_120d = pd.read_pickle(junk_path + 'ma_score120.pkl')
    dis_60d = pd.read_pickle(junk_path + 'dis60.pkl')
    ma_pct_20d = pd.read_pickle(junk_path + 'ma_pct.pkl')

    ret_list = list()
    for ma_type in ma_types.keys():
        ma_arrange = pd.read_hdf(junk_path + 'ma_cond.h5', key=ma_type)
        for ma_score_60d in ma_score_60d_enum:
            ma_score_60d_cond = pd.DataFrame(score_60d.fillna(0).values > ma_score_60d,
                                             index=score_60d.index, columns=score_60d.columns)
            for ma_score_120d in ma_score_120d_enum:
                ma_score_120d_cond = pd.DataFrame(score_120d.fillna(0).values > ma_score_120d,
                                                  index=score_120d.index, columns=score_120d.columns)
                for dis60 in dis60_enum:
                    dis60_cond = pd.DataFrame(dis_60d.fillna(0).values > dis60,
                                              index=dis_60d.index, columns=dis_60d.columns)
                    for ma_pct in ma_pct_enum:
                        print([ma_type, ma_score_60d, ma_score_120d, dis60, ma_pct])
                        ma_pct_cond = pd.DataFrame(ma_pct_20d.fillna(1).values < ma_pct,\
                                                   index=ma_pct_20d.index, columns=ma_pct_20d.columns)
                        # 整合计算
                        tmp_ret = ma_arrange & ma_score_60d_cond & ma_score_120d_cond & dis60_cond & ma_pct_cond
                        stock_num_sum = tmp_ret.loc[start_date:end_date].values.sum()
                        all_sum = np.nansum(np.isfinite(tmp_ret), axis=1).sum()
                        trend_pct = stock_num_sum / all_sum
                        everyday_stock_num = stock_num_sum / len(tradeDate.get_date_range(start_date, end_date))

                        stock_pool = tmp_ret.stack()[tmp_ret.stack()]
                        stock_pool = stock_pool.reset_index()
                        stock_pool = stock_pool.set_index('mddate')
                        stock_pool = stock_pool.sort_index(ascending=False)
                        stock_pool = stock_pool['level_1']

                        output_file = junk_path + 'trend_test/' + \
                                      f'ma({ma_type})_score60d({ma_score_60d})_score120d({ma_score_120d})_' \
                                          f'trend_dis60({dis60})_pct({ma_pct}).xlsx'
                        stock_pool.to_excel(output_file)
                        ret_list.append([ma_type, ma_score_60d, ma_score_120d, dis60, ma_pct,
                                         stock_num_sum, trend_pct, everyday_stock_num])

    ret = pd.DataFrame(ret_list)
    ret.columns = ['均线排列类型', '60日均线得分', '120日均线得分', '60日均线距离', '20日内满足ma5<ma20的比例',
                   '趋势个股总数', '趋势个股比例', '日均趋势个股数量']
    ret['均线排列详细类型'] = ret['均线排列类型'].apply(lambda x: ma_types[x])
    ret.to_excel(junk_path + 'trend_test/summary.xlsx')
    send_message(['015614'], '已完成')

