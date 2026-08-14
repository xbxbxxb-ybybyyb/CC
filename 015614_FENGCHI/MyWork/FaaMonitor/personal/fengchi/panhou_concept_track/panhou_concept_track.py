# coding: utf-8
# Author：fengchi863
# Date ：2021/7/13 14:17

from FaaMonitor.dataApi import getData, tradeDate, stockList
from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.Util.MyUtil import MyUtil
from xquant.thirdpartydata.marketdata import MarketData
from xquant.factordata import FactorData
from FaaMonitor.conf.path_conf import ths_path
from FaaMonitor.Util.tools import send_message
import pandas as pd

class ConceptTrack:
    def __init__(self, end_date=None):
        date = DtUtil.get_today_date()
        yes_date = DtUtil.get_yesterday_date()
        shift_date = tradeDate.get_pre_trade_date(date, 160)
        if not end_date:
            end_date = yes_date  # 因为一般在三点后运行该文件，所以当天的数据获取不到
        date_list = tradeDate.get_date_range(shift_date, end_date)
        daily_close = getData.get_daily_1factor('close_badj', date_list=date_list)
        daily_pctchg = getData.get_daily_1factor('pct_chg', date_list=date_list)
        limit_up = getData.get_daily_1factor('limit_up', date_list=date_list)
        daily_amt = getData.get_daily_1factor('amt', date_list=date_list)

        self.today_date = date
        self.end_date = end_date
        self.shift_date = shift_date
        self.yes_date = yes_date
        self.daily_close = daily_close
        self.daily_pctchg = daily_pctchg
        self.limit_up = limit_up
        self.daily_amt = daily_amt

        df = self.get_recent_close()
        df.index = df.index.map(stockList.trans_windcode2int)

        self.daily_close.loc[self.today_date, :] = df['close_badj']
        self.limit_up.loc[self.today_date, :] = df['limit_up']
        self.zhaban_list = df['炸板'][df['炸板']].index.tolist()

    def get_recent_close(self):
        md = MarketData()
        s = FactorData()
        df = pd.concat([md.getMDSecurityRecordBySourceTypes(securityIDSource=101),
                        md.getMDSecurityRecordBySourceTypes(securityIDSource=102)]).iloc[:, [0, 3, 4, 5, 6, 8, 9, 10]]
        df.columns = ['code', 'vol', 'amt', 'close', 'open', 'high', 'low', 'pre_close']
        df['avg_price'] = df['amt'] / df['vol']
        df = df[df['code'].map(lambda x: x[0]).isin(('0', '3', '6'))]
        df.loc[df['close'] < 0.01, ['close', 'open', 'high', 'low', 'avg_price']] = df.loc[
            df['close'] < 0.01, 'pre_close']
        df['pct'] = (df['close'] / df['pre_close'] - 1) * 100
        df = df.set_index('code')

        data = s.get_factor_value('Basic_factor',
                                  factor_names=['mdc_adjfactor', 'mdc_maxpx', 'mdc_minpx'],
                                  mddate=[str(self.today_date)])
        mdc_adjfactor = data.iloc[:, 0].unstack()
        mdc_maxpx = data.iloc[:, 1].unstack()
        mdc_minpx = data.iloc[:, 2].unstack()

        df['adj_factor'] = mdc_adjfactor.loc[str(self.today_date), df.index]
        df['mdc_maxpx'] = mdc_maxpx.loc[str(self.today_date), df.index]
        df['mdc_minpx'] = mdc_minpx.loc[str(self.today_date), df.index]

        df['close_badj'] = df['close'] * df['adj_factor']
        df['maxupordown'] = (df['mdc_maxpx'] == df['close']).astype(int) - (
                    df['mdc_minpx'] == df['close']).astype(int)
        df['limit_up'] = (df['mdc_maxpx'] == df['close']).astype(int)
        df['limit_down'] = (df['mdc_minpx'] == df['close']).astype(int)
        df['炸板'] = (df['high'] == df['mdc_maxpx']) & (df['close'] != df['mdc_maxpx'])
        return df

    def get_stock(self, concept_name=None, dragon_num=100, popular_num=10):
        ths_dic = pd.read_json(ths_path + '概念板块同花顺20210715.json', typ='dict')
        if concept_name is None:
            return
        else:
            stock_list = list(map(stockList.trans_windcode2int, list(ths_dic[concept_name].keys())))
        # 条件一
        limitup5d = self.limit_up.rolling(5).sum()[stock_list]
        tmp = limitup5d >= 2
        dragon_list = tmp.iloc[-1][tmp.iloc[-1]].index.tolist()
        dragon_list = list(map(lambda x: MyUtil.get_1stock_name(x), dragon_list))

        # 条件二
        pctchg5d = self.daily_close.pct_change(5)
        tmp = pctchg5d[stock_list]
        tmp = tmp.iloc[-1].rank(ascending=False)
        popular_list = tmp[tmp <= popular_num].index.tolist()
        popular_list = list(map(lambda x: MyUtil.get_1stock_name(x), popular_list))

        # 条件三
        zhaban_list = self.zhaban_list
        zhaban_list = list(set(zhaban_list).intersection(set(stock_list)))
        zhaban_list = list(map(lambda x: MyUtil.get_1stock_name(x), zhaban_list))

        return dragon_list, popular_list, zhaban_list


if __name__ == '__main__':
    ct = ConceptTrack()
    dragon_list, popular_list, zhaban_list = ct.get_stock(concept_name='燃气水务', popular_num=10)
    a = '龙头个股有%s' % '，'.join(dragon_list)
    b = '人气股有%s' % '，'.join(popular_list)
    c = '炸板股有%s' % '，'.join(zhaban_list)
    print(a)
    print(b)
    print(c)
    send_message(['015614'], a+'\n'+b+'\n'+c)
