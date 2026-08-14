# coding: utf-8
# Author：fengchi863
# Date ：2022/3/16 13:32

from SimiStock.config.path_config import data_path
from SimiStock.dataApi import stockList, tradeDate

df = stockList.clean_stock_list(no_ST=True,
                                least_live_days=60,
                                no_pause=True,
                                least_recover_days=10,
                                no_pause_limit=0.5,
                                no_pause_stats_days=120,
                                no_limit_up=False,
                                no_limit_down=False)
appear_stock = stockList.get_all_stock_ever_appear(tradeDate.get_today())
df = df.reindex(columns=appear_stock).fillna(False)
df.to_pickle(data_path + 'clean_stock.pkl')
