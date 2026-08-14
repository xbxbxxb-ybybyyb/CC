# coding: utf-8
# Author：fengchi863
# Date ：2021/9/10 13:41

import pandas as pd

from FaaMonitor.conf.path_conf import ths_path
from ShortTermTrading.Util.tools import save_pickle
from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.dataApi import tradeDate, stockList

start_date = 20210701
end_date = 20210903
zhaban_stock = pd.read_pickle(junk_path + 'zhaban_zt_time_15_20210909.pkl')

ths_dic = pd.read_json(ths_path + '概念板块同花顺%d.json' % 20210805, typ='dict')
main_concept_df = pd.DataFrame().reindex_like(zhaban_stock)
main_concept_df.iloc[:, :] = False


def generate_daily_active_stock(main_dict, ret_df):
    for date_tuple, concepts in main_dict.items():
        date_list = tradeDate.get_date_range(date_tuple[0], date_tuple[1])
        stk_list = list()
        for concept in concepts:
            stk_list += list(ths_dic[concept].keys())
        stk_list = list(map(lambda x: stockList.trans_windcode2int(x), list(set(stk_list))))
        stk_list = list(set(stk_list).intersection(set(zhaban_stock.columns.tolist())))
        ret_df.loc[date_list, stk_list] = True
    return ret_df


main_dict = {(20210701, 20210715): ['盐湖提锂', '第三代半导体', '锂电池', '光伏概念', '半导体及元件', '汽车整车', '稀土永磁'],
             (20210719, 20210730): ['半导体及元件', '光刻胶', '第三代半导体', '光伏概念', '国防军工', '盐湖提锂', '稀土永磁'],
             (20210730, 20210830): ['国防军工', '盐湖提锂', '稀土永磁', '有机硅'],
             (20210715, 20210809): ['光伏概念'],
             (20210819, 20210902): ['光伏概念'],
             (20210811, 20210903): ['磷化工'],
             (20210831, 20210903): ['煤炭开采加工', '电力', '云游戏', '天然气']
             }
main_concept_df = generate_daily_active_stock(main_dict, main_concept_df)

ret_df = zhaban_stock & main_concept_df
save_pickle(ret_df, junk_path, '叠加板块zhaban_zt_time_15_20210909.pkl')
