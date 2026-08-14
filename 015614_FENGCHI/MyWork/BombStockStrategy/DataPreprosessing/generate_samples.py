# coding: utf-8
# Author：fengchi863
# Date ：2021/9/13 21:19

'''
用于生成炸板股样本
'''

from ShortTermTrading.ConceptApi.ConceptApi import get_basic_values
from ShortTermTrading.dataApi import tradeDate, stockList
from BombStockStrategy.conf.path_conf import samples_path
from ShortTermTrading.Util.tools import save_pickle


class SamplesGen:
    def __init__(self, start_date=20140701, end_date=20210531):

        self.start_date = start_date
        self.end_date = end_date
        self.date_list = tradeDate.get_date_range(start_date, end_date)

    def calc_samples(self):
        bomb_df = (get_basic_values('Open_Board_stock').loc[self.date_list])
        filter_stock = stockList.clean_stock_list(least_live_days=5, trade_mode=True, no_pause=False,
                                                  least_recover_days=1,
                                                  no_pause_limit=0.5, no_pause_stats_days=0)
        filter_stk_list = list(set(bomb_df.columns.tolist()).intersection(set(filter_stock.columns.tolist())))
        filter_stk_list = [x for x in filter_stk_list if x // 1000 != 688]  # 不要科创板
        return bomb_df[filter_stk_list] & filter_stock[filter_stk_list]


if __name__ == '__main__':
    sg = SamplesGen(start_date=20140701, end_date=20210531)
    samples = sg.calc_samples()
    samples_tuple_list = samples.stack()[samples.stack()].index.tolist()
    save_pickle(samples_tuple_list, samples_path, 'samples_tuple_list.pkl')
