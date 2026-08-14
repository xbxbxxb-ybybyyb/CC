# coding: utf-8
# Author：fengchi863
# Date ：2021/6/7 20:39

from FaaMonitor.personal.fengchi.generate3DailyStock.LowPointStock import LowPointStock
from FaaMonitor.personal.fengchi.generate3DailyStock.MiddlePoint import MiddlePoint
from FaaMonitor.personal.fengchi.generate3DailyStock.FirstCloudy import FirstCloudy
from FaaMonitor.personal.fengchi.generate3DailyStock.TrendStock import TrendStock
from FaaMonitor.Util.DtUtil import DtUtil
import pandas as pd, numpy as np
from ShortTermTrading.Util.tools import save_xlsx, send_file
from ShortTermTrading.conf.path_conf import junk_path

class Add2Excel:
    def __init__(self):
        date = DtUtil.get_today_date()

        if DtUtil.get_now_hm() < 1500:
            raise Exception('当日收盘数据还未更新，无法生成股票池')

        self.date = date

    def start_convert(self, df):
        if not path:
            raise Exception('文件地址未提供！')

        lps = LowPointStock(self.date)
        mp = MiddlePoint(self.date)
        fc = FirstCloudy(self.date)
        ts = TrendStock(end_date=self.date)

        df = lps.add2excel(df)
        df = mp.add2excel(df)
        df = fc.add2excel(df)
        df = ts.add2excel(df)

        return df

if __name__ == '__main__':
    a2e = Add2Excel()

    path = '/data/group/800442/800319/Afengchi/同花顺概念/概念板块同花顺_reverse_%d.xlsx' % a2e.date
    df1 = pd.read_excel(path)
    # df1 = df1.rename(columns={'Unnamed: 0': '股票代码'})

    res = a2e.start_convert(df1)
    res = res.drop(res.columns[0], axis=1)
    columns_list = ['股票代码', '股票名称'] + ['低位股', '补涨/中位股', '龙头首阴', '趋势股'] + ['同花顺板块']
    res = res[columns_list]
    save_xlsx(res, junk_path, '主题个股监控%d.xlsx' % a2e.date)
    send_file(['015614'], junk_path + '主题个股监控%d.xlsx' % a2e.date)
    print('已发送到xquant')

