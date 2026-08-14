# coding: utf-8
# Author：fengchi863
# Date ：2021/9/8 19:34

import sys
sys.path.append('/data/group/800442/800319')
from ShortTermTrading.dataApi import stockList, getData, tradeDate
from ShortTermTrading.ConceptApi.ConceptApi import get_basic_values
from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.Util.tools import save_pickle
import pandas as pd
import numpy as np
from xquant.factordata import FactorData
import ftplib
s = FactorData()


def upload_excel(path, name):
    ftp = ftplib.FTP()
    ftp.encoding = 'gbk'
    ftp.connect('168.8.2.60')
    ftp.login(user='zsd', passwd='zsd')
    ftp.cwd('015630')
    ftp.cwd('行业监控')
    fp = open(path, 'rb')
    buf_size = 1024
    ftp.storbinary("STOR {}".format(name), fp, buf_size)
    fp.close()
    ftp.quit()
    print('上传成功')


start_date = 20140101
end_date = 20210903
date_list = tradeDate.get_date_range(start_date, end_date)

close = getData.get_daily_1factor('close', date_list=date_list)
high = getData.get_daily_1factor('high', date_list=date_list)
opn = getData.get_daily_1factor('open', date_list=date_list)
low = getData.get_daily_1factor('low', date_list=date_list)
pre_close = getData.get_daily_1factor('pre_close', date_list=date_list)[close.columns]
limit_up = getData.get_daily_1factor('limit_up', date_list=date_list)

zhaban_origin = (get_basic_values('Open_Board_stock').loc[date_list])
stocks = stockList.clean_stock_list(least_live_days=5, trade_mode=True, no_pause=False, least_recover_days=1,
                                    no_pause_limit=0.5, no_pause_stats_days=0)
stock_list = list(set(zhaban_origin.columns.tolist()).intersection(set(stocks.columns.tolist())).intersection(
    set(opn.columns.tolist())))
stock_list = [x for x in stock_list if x // 1000 != 688]
stock_list.sort()
zhaban_origin = zhaban_origin[stock_list] & stocks.loc[zhaban_origin.index, stock_list]
# 收阳线
# 炸板后的跌幅占当天振幅的比例不高于0.3
zhaban = zhaban_origin & \
         (opn[stock_list] < close[stock_list]) & \
         ((high[stock_list] - close[stock_list]) / (high[stock_list] - low[stock_list]) < 0.3)

close_min = getData.get_minute_1factor('close', start_datetime=date_list[0] * 10000 + 925,
                                       end_datetime=date_list[-1] * 10000 + 1500)

stocklist_inner = list(set(close_min.columns.tolist()).intersection(set(stock_list)))
stocklist_inner.sort()
zhaban = zhaban[stocklist_inner]
limit_up_price = (get_basic_values('Limit_price').loc[date_list, stocklist_inner])
close_min = close_min[stocklist_inner]

limit_up_price_min = pd.DataFrame(np.array(limit_up_price.loc[close_min.index.get_level_values('date')]),
                                  index=close_min.index,
                                  columns=limit_up_price.columns)

zt_match = limit_up_price_min == close_min
zt_time_sum = zt_match.reset_index().drop('time', axis=1).groupby('date').sum()
zt_time_sum.head().sum().sum()
# 涨停时间大于15分钟
zt_time = zt_time_sum > 15
# 收盘价低于涨停价的0.99
zhaban_df = zhaban & zt_time & (close[stocklist_inner] < limit_up_price * 0.99)
save_pickle(zhaban_df, junk_path, 'zhaban_zt_time_15_20210909.pkl')
