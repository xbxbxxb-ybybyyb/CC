# coding: utf-8
# Author：fengchi863
# Date ：2021/12/9 14:08

'''
准备趋势均线排列的不同条件生成的DataFrame和HDF5文件
'''

import pandas as pd

from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.dataApi import getData, tradeDate

ma_types = {'type1': 'ma5>ma10>ma20>ma40>ma60',
            'type2': 'ma5>ma10>ma20>ma40',
            'type3': 'ma5>ma10>ma20',
            'type4': 'ma5>ma10',
            'type5': 'close>ma5>ma10>ma20',
            'type6': 'close>ma5>ma10',
            'type7': 'close>ma5',
            }


class MaCond:
    def __init__(self):
        pass

    @staticmethod
    def ma_score(close, n):
        pre = close
        stat = pd.DataFrame(0, index=close.index, columns=close.columns)
        for i in range(1, n + 1):
            cur = close.rolling(i).mean()
            stat += (pre > cur).applymap(lambda x: 100 if x else 0)
            pre = cur
        stat /= n
        return stat

    @staticmethod
    def distance(close, n):
        pre = close
        dis = pd.DataFrame(0, index=close.index, columns=close.columns)
        for i in range(1, n + 1):
            cur = close.rolling(i).mean()
            dis += abs(pre - cur) / pre
            pre = cur
        return dis

    @staticmethod
    def ranks(x):
        return pd.Series(x).rank(pct=True,axis=0).values[-1]


if __name__ == '__main__':
    mc = MaCond()
    start_date = 20130101
    end_date = 20211131
    date_list = tradeDate.get_date_range(start_date, end_date)
    close = getData.get_daily_1factor('close_badj', date_list=date_list)
    ma5 = close.rolling(5).mean()
    ma10 = close.rolling(10).mean()
    ma20 = close.rolling(20).mean()
    ma40 = close.rolling(40).mean()
    ma60 = close.rolling(60).mean()

    dis60 = mc.distance(close, 60)
    dis60.to_pickle(junk_path + 'dis60.pkl')
    ma_score60 = mc.ma_score(close, 60)
    ma_score60.to_pickle(junk_path + 'ma_score60.pkl')
    ma_score120 = mc.ma_score(close, 120)
    ma_score120.to_pickle(junk_path + 'ma_score120.pkl')

    ma_pct = (ma5 < ma20).rolling(20).sum() / 20
    ma_pct.to_pickle(junk_path + 'ma_pct.pkl')

    type1 = (ma5 > ma10) & (ma10 > ma20) & (ma20 > ma40) & (ma40 > ma60)
    type2 = (ma5 > ma10) & (ma10 > ma20) & (ma20 > ma40)
    type3 = (ma5 > ma10) & (ma10 > ma20)
    type4 = (ma5 > ma10)
    type5 = (close > ma5) & (ma5 > ma10) & (ma10 > ma20)
    type6 = (close > ma5) & (ma5 > ma10)
    type7 = (close > ma5)

    for item in ma_types.keys():
        eval(item).to_hdf(junk_path + 'ma_cond.h5', key=item)

    # dis60 = pd.read_pickle(junk_path + 'dis60.pkl')
    # avg_score60 = pd.read_pickle(junk_path + 'avg_score60.pkl')
    # avg_score120 = pd.read_pickle(junk_path + 'avg_score120.pkl')
    #
    # # 20日内满足状态的比例
    # ma_cond = (ma5 > ma10) & (ma10 > ma20) & (ma20 > ma40) & (ma40 > ma60)
    # score60_cond = pd.DataFrame(avg_score60.values > 60, index=avg_score60.index,
    #                             columns=avg_score60.columns)
    # score120_cond = pd.DataFrame(avg_score120.values > 60, index=avg_score120.index,
    #                              columns=avg_score120.columns)
    # dis60_cond = pd.DataFrame(dis60.values > 0.2, index=dis60.index,
    #                           columns=dis60.columns)
    #
    # cond_pct = (ma5 < ma20).rolling(20).sum() / 20
    # cond_pct_cond = pd.DataFrame(cond_pct.values < 0.5, index=cond_pct.index,
    #                              columns=cond_pct.columns)
    #
    # ret = ma_cond & score60_cond & score120_cond & dis60_cond & cond_pct_cond
    # check_date = 20211202
    # check1 = ret.loc[check_date][ret.loc[check_date]]
    #
    # check = pd.read_pickle(faamonitor_path + '中期趋势股20211208.pkl')
    # check2 = check.loc[f'{check_date}'][check.loc[f'{check_date}']]
    #
    # a2 = sorted(list(check2.index.map(stockList.trans_windcode2int)))
    # a1 = sorted(check1.index.tolist())
    # list(set(a2) - (set(a1)))
    # list(set(a1) - (set(a2)))
    #
