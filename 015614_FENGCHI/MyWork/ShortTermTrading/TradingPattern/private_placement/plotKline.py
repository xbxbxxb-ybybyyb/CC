# coding: utf-8
# Author：fengchi863
# Date ：2021/11/24 8:55

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime
import mplfinance as mpf
import pandas as pd
import numpy as np
import warnings
from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.dataApi import tradeDate, getData, stockList
from FaaMonitor.Util.MyUtil import MyUtil
warnings.filterwarnings('ignore')
plt.rcParams['font.sans-serif'] = [u'SimHei']
plt.rcParams['axes.unicode_minus'] = False
myfont = matplotlib.font_manager.FontProperties(fname='msyh.ttf')


class PlotKLine:
    def __init__(self, start_date=20190101, end_date=20211120):
        date_list = tradeDate.get_date_range(start_date, end_date)
        open_badj = getData.get_daily_1factor('open_badj', date_list=date_list)
        high_badj = getData.get_daily_1factor('high_badj', date_list=date_list)
        low_badj = getData.get_daily_1factor('low_badj', date_list=date_list)
        close_badj = getData.get_daily_1factor('close_badj', date_list=date_list)
        volume = getData.get_daily_1factor('volume', date_list=date_list)

        my_color = mpf.make_marketcolors(up='red', down='cyan', edge='i',
                                         wick='black')
        my_style = mpf.make_mpf_style(base_mpf_style='charles', marketcolors=my_color,
                                      gridaxis='both', gridstyle='-.',
                                      y_on_right=False)

        self.open = open_badj
        self.high = high_badj
        self.low = low_badj
        self.close = close_badj
        self.volume = volume
        self.date_list = date_list

        self.my_style = my_style

    @staticmethod
    def get_pp_df():
        pp_df = pd.read_pickle(junk_path + '定增数据原始样本.pkl')
        col_name = ['股票代码', '股票名称', '定价基准日']
        pp_df = pp_df[col_name]
        return pp_df

    def generate_single_stk_df(self, stk_id):
        if type(stk_id) is str:
            stk_id = stockList.trans_windcode2int(stk_id)
        ret = pd.DataFrame(index=self.date_list)
        ret['Open'] = self.open.loc[:, stk_id]
        ret['High'] = self.high.loc[:, stk_id]
        ret['Low'] = self.low.loc[:, stk_id]
        ret['Close'] = self.close.loc[:, stk_id]
        ret['Volume'] = self.volume.loc[:, stk_id]
        return ret

    def plot_kline(self, stk_id, start_date, end_date):
        if type(stk_id) is str:
            stk_id = stockList.trans_windcode2int(stk_id)
        df = self.generate_single_stk_df(stk_id)
        data = df.loc[start_date:end_date]
        data.index = pd.DatetimeIndex(data.index.map(str))
        mpf.plot(data, type='candle', mav=(5, 10, 20),
                 volume=True,
                 style=self.my_style,
                 title=f'{str(stk_id).zfill(6)}',
                 figscale=2,
                 figratio=(8, 6))
        stock_name = MyUtil.get_1stock_name(stk_id).replace('*', '')
        plt.savefig(junk_path + '定增绘图/' + f'{str(stk_id).zfill(6)}_{stock_name}_{end_date}.png')


if __name__ == '__main__':
    pkl = PlotKLine()
    pp_df = pkl.get_pp_df()
    for idx in range(len(pp_df)):
        print(f'{idx}/{len(pp_df)}')
        stk_code = pp_df.iloc[idx]['股票代码']
        end_date = pp_df.iloc[idx]['定价基准日']
        start_date = tradeDate.get_pre_trade_date(end_date, 80)
        pkl.plot_kline(stk_code, start_date, end_date)
