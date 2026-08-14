# coding: utf-8
# Author：fengchi863
# Date ：2021/12/28 13:03

from ShortTermTrading.dataApi import tradeDate, stockList, getData
from FaaMonitor.Util.MyUtil import MyUtil
import pandas as pd
import numpy as np
from ShortTermTrading.Util.tools import save_pickle, send_file
from ShortTermTrading.conf.path_conf import junk_path

trade_months = [20201130, 20201231, 20210129, 20210226, 20210331, 20210430, 20210531,
                20210630, 20210730, 20210831, 20210930, 20211029, 20211130, 20211224]


class AnnIndStats2:
    def __init__(self):
        stk_list_df = stockList.clean_stock_list(least_live_days=30)
        stk_list = stk_list_df.columns.tolist()
        date_list = tradeDate.get_date_range(trade_months[0], trade_months[-1])
        close = getData.get_daily_1factor('close_badj', date_list=date_list, code_list=stk_list)

        stk_close_pct = close.pct_change(1)
        stk_close_up_days = stk_close_pct > 0

        self.stk_list = stk_list
        self.stk_list_df = stk_list_df
        self.close = close
        self.stk_close_up_days = stk_close_up_days

    def get_stk_pct(self, start_date, end_date):
        return self.close.loc[end_date] / self.close.loc[start_date] - 1

    def get_monthly_pct(self):
        month_period = [(trade_months[x], trade_months[x + 1]) for x in range(0, 13)]
        monthly_stats = dict()
        monthly_stk_pct = pd.DataFrame()
        monthly_stk_up_days_pct = pd.DataFrame()
        for idx, period in enumerate(month_period):
            date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(period[0], -1), period[1])
            tmp_pct = self.get_stk_pct(period[0], period[1])
            tmp_up_days_pct = self.stk_close_up_days.loc[date_list].sum() / len(date_list)
            tmp_pct.name = idx
            tmp_up_days_pct.name = idx
            monthly_stk_pct = monthly_stk_pct.append(tmp_pct)
            monthly_stk_up_days_pct = monthly_stk_up_days_pct.append(tmp_up_days_pct)

        yearly_date_list = tradeDate.get_date_range(trade_months[1], trade_months[-1])
        yearly_days_up_pct = self.stk_close_up_days.loc[yearly_date_list].sum() / len(yearly_date_list)
        for idx, period in enumerate(month_period):
            if idx == 0:
                continue
            stk_list = self.stk_list_df.loc[period[1]][self.stk_list_df.loc[period[1]]].index.tolist()
            monthly_stk_pct_copy = monthly_stk_pct[stk_list]
            top10_sw2_code = list(reversed(monthly_stk_pct_copy.loc[idx, :].dropna().sort_values().index.tolist()[-10:]))
            bottom10_sw2_code = list(reversed(monthly_stk_pct_copy.loc[idx, :].dropna().sort_values().index.tolist()[:10]))
            index_list = top10_sw2_code + bottom10_sw2_code
            monthly_ret = pd.DataFrame(index=index_list)
            monthly_ret['股票名称'] = monthly_ret.index.map(lambda x: MyUtil.get_1stock_name(x))
            monthly_ret['当月涨跌幅'] = monthly_ret.index.map(lambda x: monthly_stk_pct_copy.loc[idx, x])
            monthly_ret['当月上涨的天数占比'] = monthly_ret.index.map(lambda x: monthly_stk_up_days_pct.loc[idx, x])
            monthly_ret['本年上涨的天数占比'] = monthly_ret.index.map(lambda x: yearly_days_up_pct.loc[x])
            monthly_stats[idx] = monthly_ret

        with pd.ExcelWriter(junk_path + 'ann_ind_stats_part2.xlsx') as writer:
            for each in monthly_stats:
                monthly_stats[each].to_excel(writer, str(each))

        send_file(['015614'], junk_path + 'ann_ind_stats_part2.xlsx')


if __name__ == '__main__':
    ais = AnnIndStats2()
    ais.get_monthly_pct()
