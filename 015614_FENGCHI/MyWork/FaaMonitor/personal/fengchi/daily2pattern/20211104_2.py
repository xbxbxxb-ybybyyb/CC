# coding: utf-8
# Author：fengchi863
# Date ：2021/11/4 13:55

'''
20211104使用修改后的趋势股每日跟踪，每天的股票池也更换为这里的股票
'''

from dataApi.stockList import clean_stock_list, trans_windcode2int
from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.Util.tools import get_stock_name_dict, save_xlsx, get_df_sum
from ShortTermTrading.conf.path_conf import faamonitor_path, junk_path, man_made_concept_data_path, daily_monitor_path
from ShortTermTrading.Util.System import check_shape, add_stock_name, fetch_man_made_monitor_list
import pandas as pd, numpy as np
from xquant.factordata import FactorData
from tqdm import tqdm
from ShortTermTrading.Util.tools import *
from FaaMonitor.Util.DtUtil import DtUtil
from FaaMonitor.conf.path_conf import ths_reverse_path, ths_concept_rank_path
# import talib
import time


class SignalGenerator:

    def __init__(self, start_date=20200101, end_date=20201231):
        today_date = DtUtil.get_today_date()
        # today_date = 20220701
        shift_start_date = get_pre_trade_date(start_date, 5)
        shift_end_date = get_pre_trade_date(end_date, 5)
        date_list = get_date_range(shift_start_date, end_date)
        daily_st = clean_stock_list(no_pause=False, no_ST=True, least_live_days=0, start_date=shift_start_date,
                                    end_date=end_date)
        stk_list = sorted(daily_st.columns.tolist())

        daily_close_badj = get_daily_1factor('close_badj', code_list=stk_list, date_list=date_list)
        daily_pre_close_badj = get_daily_1factor('pre_close_badj', code_list=stk_list, date_list=date_list)
        daily_high_badj = get_daily_1factor('high_badj', code_list=stk_list, date_list=date_list)
        daily_low_badj = get_daily_1factor('low_badj', code_list=stk_list, date_list=date_list)
        daily_open_badj = get_daily_1factor('open_badj', code_list=stk_list, date_list=date_list)
        daily_pctchg = get_daily_1factor('pct_chg', code_list=stk_list, date_list=date_list)
        daily_amt = get_daily_1factor('amt', code_list=stk_list, date_list=date_list)
        daily_limit_up = get_daily_1factor('limit_up', code_list=stk_list, date_list=date_list)
        daily_limit_down = get_daily_1factor('limit_down', code_list=stk_list, date_list=date_list)

        ths_concept = pd.read_json(ths_concept_rank_path + f'同花顺概念排名{today_date}.json', typ='dict').to_dict()

        self.date_list = date_list
        self.shift_start_date = shift_start_date
        self.shift_end_date = shift_end_date
        self.start_date = start_date
        self.end_date = end_date
        self.stk_list = stk_list
        self.daily_st = daily_st
        self.daily_close_badj = daily_close_badj
        self.daily_pre_close_badj = daily_pre_close_badj
        self.daily_high_badj = daily_high_badj
        self.daily_low_badj = daily_low_badj
        self.daily_open_badj = daily_open_badj
        self.daily_pctchg = daily_pctchg
        self.daily_amt = daily_amt
        self.daily_limit_up = daily_limit_up
        self.daily_limit_down = daily_limit_down

        self.stk_code_name_dict = get_stock_name_dict()
        self.ths_concept = ths_concept

    # 日间条件
    def add_st_cond(self):
        return self.daily_st

    # 流通市值条件
    def add_mkt_cap_cond(self, cap=250):
        stk_daily_mkt_cap = get_daily_1factor('float_a_shares', code_list=self.stk_list, date_list=self.date_list)
        stk_daily_close = get_daily_1factor('close', code_list=self.stk_list, date_list=self.date_list)
        stk_daily_float_cap = stk_daily_mkt_cap * stk_daily_close
        stk_daily_float_cap = stk_daily_float_cap / 10000
        stk_daily_float_cap_cond = stk_daily_float_cap >= cap
        return stk_daily_float_cap_cond

    # 前5(不含近3日)涨跌幅<=15%
    def add_t5_cond(self):
        low_t5 = self.daily_low_badj.rolling(5).min().shift(3)
        close_low_t5 = self.daily_close_badj.shift(3) / low_t5 - 1
        close_low_cond = close_low_t5 <= 0.15
        return close_low_cond

    # 多头排列条件
    def add_multi_arrange_cond(self):
        data = pd.read_pickle(faamonitor_path + '中期趋势股%d.pkl' % self.end_date)
        data.columns = list(map(trans_windcode2int, data.columns.tolist()))
        data.index = list(map(int, data.index.tolist()))
        data = data.reindex(columns=self.stk_list, index=self.date_list).fillna(False)
        return data.loc[self.shift_start_date:self.end_date]

    # 最近5日价格有三天在ma5上方
    def add_ma_cond(self):
        ma5 = self.daily_close_badj.rolling(5).mean()
        cond = self.daily_close_badj > ma5
        cond = cond.rolling(5).sum()
        cond = cond >= 3
        return cond.shift(1)

    # 最近的一日价格不能低于ma5*0.95
    def add_ma_cond2(self):
        ma5 = self.daily_close_badj.rolling(5).mean()
        cond = self.daily_close_badj > ma5 * 0.95
        return cond.shift(1)

    def add_ma_cond3(self):
        ma5 = self.daily_close_badj.rolling(5).mean()
        ma5_pct1d = ma5.pct_change(1)
        ma5_pct1d_cond = ma5_pct1d > 0
        ma5_pct1d_cond = ma5_pct1d_cond.rolling(5).sum() > 3
        ma5_pct5d = ma5.pct_change(5)
        ma5_pct5d_cond = ma5_pct5d > 0
        cond = ma5_pct1d_cond & ma5_pct5d_cond
        return cond

    # 五日的收盘价最大回撤不超过12%
    def add_withdraw_cond(self):
        cond = self.daily_close_badj.rolling(5).apply(lambda x: ((np.maximum.accumulate(x) - x) / x).max())
        cond = cond < 0.12
        return cond

    # 前5日涨跌幅<=15%，剔除在一波上涨的高位触发信号
    def add2_t5_cond(self):
        low_t1 = self.daily_low_badj.rolling(5).min().shift(1)
        close_low_t1 = self.daily_close_badj.shift(1) / low_t1 - 1
        close_low_cond = close_low_t1 <= 0.15
        return close_low_cond

    def add_limit_cond(self):
        cond1 = self.daily_limit_up.rolling(5).sum() <= 2
        cond2 = self.daily_limit_down.rolling(5).sum() == 0
        cond = cond1 & cond2
        return cond.shift(1)

    def calc_daily_stock_v2(self):
        st_cond = self.add_st_cond()
        mkt_cap_cond = self.add_mkt_cap_cond(cap=250)
        t5_cond = self.add2_t5_cond()
        multi_arrange_cond = self.add_multi_arrange_cond()
        ma_cond = self.add_ma_cond()
        ma_cond2 = self.add_ma_cond2()
        ma_cond3 = self.add_ma_cond3()
        limit_cond = self.add_limit_cond()
        withdraw_cond = self.add_withdraw_cond()

        check_shape(st_cond, mkt_cap_cond, multi_arrange_cond, t5_cond, ma_cond,
                    limit_cond, ma_cond2, ma_cond3, withdraw_cond)
        daily_cond = st_cond & mkt_cap_cond & multi_arrange_cond & t5_cond & ma_cond & \
                     limit_cond & ma_cond2 & ma_cond3 & withdraw_cond
        daily_cond = daily_cond.fillna(False)
        return daily_cond

    @staticmethod
    def get_stock_concept(stk_code, concept_df: pd.DataFrame):
        concept_list = concept_df[concept_df['股票代码'] == stockList.trans_int2windcode(stk_code)]['主题'].tolist()
        return ','.join(concept_list)

    @staticmethod
    def get_top3_concept(stk_code, concept_dict:dict):
        if type(stk_code) is int:
            stk_code = trans_int2windcode(stk_code)
        return concept_dict[stk_code]

    def add_concept_col(self, df):
        concept_str = df.index.to_series().apply(lambda x: self.ths_concept[stockList.trans_int2windcode(x)])
        for stk_id in concept_str.index:
            tmp = concept_str[stk_id]
            # concept_str[stk_id] = ','.join(self.del_concept(tmp.split('，')))
            concept_str[stk_id] = ','.join(self.del_concept(tmp.split(',')))
        df['concept'] = concept_str
        return df


def wrapper(start_date, end_date):
    print('start', start_date, end_date)
    sg = SignalGenerator(start_date=start_date, end_date=end_date)
    print('初始化完成')
    daily_cond = sg.calc_daily_stock_v2()
    to_deal_list = daily_cond.iloc[-1][daily_cond.iloc[-1]].index.tolist()
    to_deal_name_list = list(map(get_stock_name, to_deal_list))
    print('准备监控的个股：', ','.join(to_deal_name_list))
    message = '%d趋势个股：' % end_date + ','.join(to_deal_name_list)
    send_message(['015614'], message)

    df = pd.DataFrame([to_deal_list, to_deal_name_list], index=['股票代码', '股票名称']).T
    df['所属主题'] = df['股票代码'].apply(lambda x: sg.get_top3_concept(x, sg.ths_concept))

    return df


if __name__ == '__main__':
    start_date = 20211001
    end_date = DtUtil.get_today_date()
    # end_date = 20220701
    res = wrapper(start_date, end_date)

    save_xlsx(res, daily_monitor_path + '趋势股低吸/%d/' % end_date, '趋势股低吸%d.xlsx' % end_date)
    send_file(['015614'], daily_monitor_path + '趋势股低吸/%d/' % end_date + '趋势股低吸%d.xlsx' % end_date)
