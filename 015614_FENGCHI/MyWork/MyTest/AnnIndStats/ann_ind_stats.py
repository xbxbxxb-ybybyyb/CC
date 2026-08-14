# coding: utf-8
# Author：fengchi863
# Date ：2021/12/27 13:55

import os
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from ShortTermTrading.dataApi import tradeDate, getData, stockList
from ShortTermTrading.Util.tools import save_pickle, send_file
from ShortTermTrading.conf.path_conf import junk_path
from FaaMonitor.Util.MyUtil import MyUtil

trade_months = [20201130, 20201231, 20210129, 20210226, 20210331, 20210430, 20210531,
                20210630, 20210730, 20210831, 20210930, 20211029, 20211130, 20211224]


class AnnIndStats:
    def __init__(self):
        sw_ind_df, sw2_close, sw2_amt = self.get_basic_data()
        daily_sw2_pct = sw2_close.pct_change(1)
        sw_index_sector = pd.read_excel('/data/group/800442/800319/Faamonitor/basic/新申万行业.xlsx', index_col=0)
        sw_ind_name = sw_index_sector['二级行业简称'].to_dict()

        sw2_close_pct = sw2_close.pct_change(1)
        sw2_close_up_days = sw2_close_pct > 0

        daily_stk_close = getData.get_daily_1factor('close_badj', date_list=tradeDate.get_date_range(20201130, 20211224))

        sw2_stk_code = sw_ind_df['S_INFO_WINDCODE']
        sw2_stk_list = dict()
        for sw2_code in set(sw2_stk_code.values):
            sw2_stk_list[sw2_code] = list(map(lambda x: stockList.trans_windcode2int(x), sw2_stk_code[sw2_stk_code == sw2_code].index.tolist()))

        self.sw_ind_df = sw_ind_df
        self.sw2_close = sw2_close
        self.sw2_close_up_days = sw2_close_up_days
        self.sw2_amt = sw2_amt
        self.sw_ind_name = sw_ind_name
        self.daily_sw2_pct = daily_sw2_pct
        self.daily_stk_close = daily_stk_close
        self.sw2_stk_list = sw2_stk_list
        self.stk_code_sw2_dict = sw_ind_df['S_INFO_WINDCODE'].to_dict()

    @staticmethod
    def get_basic_data():
        if os.path.exists(junk_path + 'sw2_amt.pkl'):
            sw_ind_df = pd.read_pickle(junk_path + 'sw_ind_df.pkl')
            sw2_close = pd.read_pickle(junk_path + 'sw2_close.pkl')
            sw2_amt = pd.read_pickle(junk_path + 'sw2_amt.pkl')
        else:
            fd = FactorData()
            sw_index_sector = pd.read_excel('/data/group/800442/800319/Faamonitor/basic/新申万行业.xlsx', index_col=0)
            sw_ind_list = sw_index_sector.index.tolist()
            sw_ind_list.remove('801011.SI')
            sw_ind_df = fd.get_factor_value('WIND_SWIndexMembers',
                                            factors=['S_CON_WINDCODE', 'S_INFO_WINDCODE', 'CUR_SIGN'],
                                            S_INFO_WINDCODE=sw_ind_list).set_index('S_CON_WINDCODE')
            sw_ind_df = sw_ind_df.query('CUR_SIGN == 1').sort_index()
            sw_ind_name = sw_index_sector['二级行业简称'].to_dict()
            sw_ind_df['二级行业简称'] = sw_ind_df['S_INFO_WINDCODE'].apply(lambda x: sw_ind_name[x])

            sw2_info = fd.get_factor_value('WIND_ASWSIndexEOD',
                                            factor_names=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_CLOSE', 'S_DQ_AMOUNT'],
                                            S_INFO_WINDCODE=sw_ind_list,
                                            TRADE_DT=[f'>20201129'])
            sw2_close = sw2_info.pivot(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_CLOSE')
            sw2_amt = sw2_info.pivot(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_AMOUNT')
            sw2_amt = sw2_amt * 1e5
            sw2_close.index = sw2_close.index.map(int)
            sw2_amt.index = sw2_amt.index.map(int)
            save_pickle(sw2_close, junk_path, 'sw2_close.pkl')
            save_pickle(sw_ind_df, junk_path, 'sw_ind_df.pkl')
            save_pickle(sw2_amt, junk_path, 'sw2_amt.pkl')
        return sw_ind_df, sw2_close, sw2_amt

    def get_sw2_pct(self, start_date, end_date):
        return self.sw2_close.loc[end_date, :] / self.sw2_close.loc[start_date, :] - 1

    def get_monthly_pct(self):
        month_period = [(trade_months[x], trade_months[x+1]) for x in range(0, 13)]
        monthly_stats = dict()
        monthly_sw2_pct = pd.DataFrame()
        monthly_sw2_amt = pd.DataFrame()
        monthly_sw2_up_days_pct = pd.DataFrame()
        monthly_stk_pct = pd.DataFrame()
        for idx, period in enumerate(month_period):
            date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(period[0], -1), period[1])
            tmp_pct = self.get_sw2_pct(period[0], period[1])
            tmp_amt = self.sw2_amt.loc[date_list, :].sum()
            tmp_up_days_pct = self.sw2_close_up_days.loc[date_list].sum() / len(date_list)
            tmp_pct.name = idx
            tmp_amt.name = idx
            tmp_up_days_pct.name = idx
            monthly_sw2_pct = monthly_sw2_pct.append(tmp_pct)
            monthly_sw2_amt = monthly_sw2_amt.append(tmp_amt)
            monthly_sw2_up_days_pct = monthly_sw2_up_days_pct.append(tmp_up_days_pct)

            tmp_stk_pct = self.daily_stk_close.loc[period[1]] / self.daily_stk_close.loc[period[0]] - 1
            tmp_stk_pct.name = idx
            monthly_stk_pct = monthly_stk_pct.append(tmp_stk_pct)

        monthly_sw2_amt_pct = monthly_sw2_amt.pct_change(1)
        monthly_sw2_amt_ratio = monthly_sw2_amt / monthly_sw2_amt.sum()
        monthly_sw2_amt_ratio_pct = monthly_sw2_amt_ratio.pct_change(1)
        yearly_date_list = tradeDate.get_date_range(trade_months[1], trade_months[-1])
        yearly_days_up_pct = self.sw2_close_up_days.loc[yearly_date_list].sum() / len(yearly_date_list)
        for idx, period in enumerate(month_period):
            if idx == 0:
                continue
            top10_sw2_code = list(reversed(monthly_sw2_pct.loc[idx, :].sort_values().index.tolist()[-10:]))
            bottom10_sw2_code = list(reversed(monthly_sw2_pct.loc[idx, :].sort_values().index.tolist()[:10]))
            index_list = top10_sw2_code + bottom10_sw2_code
            monthly_ret = pd.DataFrame(index=index_list)
            monthly_ret['行业名称'] = monthly_ret.index.map(lambda x: self.sw_ind_name[x])
            monthly_ret['涨跌幅'] = monthly_ret.index.map(lambda x: monthly_sw2_pct.loc[idx, x])
            monthly_ret['成交额较上月变化幅度'] = monthly_ret.index.map(lambda x: monthly_sw2_amt_pct.loc[idx, x])
            monthly_ret['成交额占全市场占比'] = monthly_ret.index.map(lambda x: monthly_sw2_amt_ratio.loc[idx, x])
            monthly_ret['成交额占全市场占比较上月提升幅度'] = monthly_ret.index.map(lambda x: monthly_sw2_amt_ratio_pct.loc[idx, x])

            monthly_ret['行业当月的中位数涨幅'] = monthly_ret.index.map(lambda x: monthly_stk_pct.loc[idx, self.sw2_stk_list[x]].median())
            monthly_ret['当月上涨的天数占比'] = monthly_ret.index.map(lambda x: monthly_sw2_up_days_pct.loc[idx, x])
            monthly_ret['本年上涨的天数占比'] = monthly_ret.index.map(lambda x: yearly_days_up_pct.loc[x])
            monthly_stats[idx] = monthly_ret

        with pd.ExcelWriter(junk_path + 'ann_ind_stats_part1.xlsx') as writer:
            for each in monthly_stats:
                monthly_stats[each].to_excel(writer, str(each))

        send_file(['015614'], junk_path + 'ann_ind_stats_part1.xlsx')

    @staticmethod
    def maxdrawdown(arr):
        i = np.argmax((np.maximum.accumulate(arr) - arr) / np.maximum.accumulate(arr))  # end of the period
        j = np.argmax(arr[:i])
        return 1 - arr[i] / arr[j]

    @staticmethod
    def mdd_dura(nav):
        a = nav.values
        tmp_date_list = nav.index.tolist()
        duration = 0
        maxd = 0
        end_date = np.argmax((np.maximum.accumulate(a) - a) / np.maximum.accumulate(a))  # 最大回撤结束日（回撤期最低点日期）
        start_date = np.argmax(a[:end_date])  # 最大回撤开始日
        end_date = tmp_date_list[end_date]
        start_date = tmp_date_list[start_date]
        timedelta = tradeDate.get_trade_date_interval(end_date, base_date=start_date)
        # for i in range(len(a)):
        #     maxa = max(a[:i + 1])
        #     if a[i] < maxa:
        #         duration = duration + 1
        #         if maxd < duration:
        #             maxd = duration  # 回撤开始到再创新高时间
        #     else:
        #         duration = 0
        # restore = maxd - timedelta  # 回撤期最低点到创新高时间
        # print('最大回撤持续期%d, 最大回撤恢复期%d, 最大回撤整段%d' % (timedelta, restore, maxd))
        return start_date, end_date, timedelta

    def get_sw2_ann_pct(self):
        ret = pd.DataFrame(index=self.sw2_close.columns,
                           columns=['行业简称', '最大回撤', '最大回撤区间段', '持续时间', '成分股涨跌幅中位数'])
        ret['行业简称'] = ret.index.map(lambda x: self.sw_ind_name[x])

        ann_stk_pct = self.daily_stk_close.loc[trade_months[-1]] / self.daily_stk_close.loc[trade_months[1]] - 1
        for sw2_code in ret.index:
            tmp = self.sw2_close[sw2_code].loc[trade_months[1]:trade_months[-1]]
            max_drawdown = self.maxdrawdown(tmp.values)
            start_date, end_date, timedelta = self.mdd_dura(tmp)
            ret.loc[sw2_code, '最大回撤'] = max_drawdown
            ret.loc[sw2_code, '最大回撤区间段'] = f'{start_date}-{end_date}'
            ret.loc[sw2_code, '持续时间'] = timedelta
            ret.loc[sw2_code, '成分股涨跌幅中位数'] = np.nanmedian(ann_stk_pct[self.sw2_stk_list[sw2_code]].values)

        ret.to_excel(junk_path + 'ann_ind_stats_part3.xlsx')
        send_file(['015614'], junk_path + 'ann_ind_stats_part3.xlsx')

    def get_sw2_ind(self, stk_id):
        if stockList.trans_int2windcode(stk_id) not in list(self.stk_code_sw2_dict.keys()):
            return None
        else:
            return self.sw_ind_name[self.stk_code_sw2_dict[stockList.trans_int2windcode(stk_id)]]

    def get_sw2_pct(self, stk_id, ann_sw2_pct):
        if stockList.trans_int2windcode(stk_id) not in list(self.stk_code_sw2_dict.keys()):
            return None
        else:
            return ann_sw2_pct[self.stk_code_sw2_dict[stockList.trans_int2windcode(stk_id)]]

    def get_stk_ann_pct(self):
        date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(trade_months[1], -1), trade_months[-1])
        ann_stk_pct = self.daily_stk_close.loc[trade_months[-1]] / self.daily_stk_close.loc[trade_months[1]] - 1
        ann_sw2_pct = self.sw2_close.loc[trade_months[-1]] / self.sw2_close.loc[trade_months[1]] - 1
        stk_up_days = self.daily_stk_close.pct_change(1) > 0
        stk_up_days_pct = stk_up_days.loc[date_list].sum(axis=0) / len(date_list)
        stk_list_df = stockList.clean_stock_list(no_ST=True, start_date=trade_months[0], end_date=trade_months[0])
        stk_list0= stk_list_df.iloc[-1][stk_list_df.iloc[-1]].index.tolist()
        stk_list_df = stockList.clean_stock_list(no_ST=True, least_live_days=250, start_date=trade_months[-1],
                                                 end_date=trade_months[-1])
        stk_list1 = stk_list_df.iloc[-1][stk_list_df.iloc[-1]].index.tolist()
        stk_list = list(set(stk_list0).intersection(set(stk_list1)))
        top20_stk_code = list(reversed(ann_stk_pct[stk_list].sort_values().index.tolist()[-20:]))
        bottom20_stk_code = list(reversed(ann_stk_pct[stk_list].sort_values().index.tolist()[:20]))
        index_list = top20_stk_code + bottom20_stk_code
        monthly_ret = pd.DataFrame(index=index_list,
                                   columns=['股票名称', '本年涨跌幅', '本年上涨天数占比', '所属申万二级行业', '对应申万二级行业涨跌幅'])
        monthly_ret['股票名称'] = monthly_ret.index.map(lambda x: MyUtil.get_1stock_name(x))
        monthly_ret['本年涨跌幅'] = monthly_ret.index.map(lambda x: ann_stk_pct.loc[x])
        monthly_ret['本年上涨天数占比'] = monthly_ret.index.map(lambda x: stk_up_days_pct[x])
        monthly_ret['所属申万二级行业'] = monthly_ret.index.map(lambda x: self.get_sw2_ind(x))
        monthly_ret['对应申万二级行业涨跌幅'] = monthly_ret.index.map(lambda x: self.get_sw2_pct(x, ann_sw2_pct))

        monthly_ret.to_excel(junk_path + 'ann_ind_stats_part4.xlsx')
        send_file(['015614'], junk_path + 'ann_ind_stats_part4.xlsx')

    def get_wind_dragon_index(self):
        date_list = tradeDate.get_date_range(tradeDate.get_pre_trade_date(trade_months[1], -1), trade_months[-1])
        ann_stk_pct = self.daily_stk_close.loc[trade_months[-1]] / self.daily_stk_close.loc[trade_months[1]] - 1
        ann_sw2_pct = self.sw2_close.loc[trade_months[-1]] / self.sw2_close.loc[trade_months[1]] - 1
        stk_up_days = self.daily_stk_close.pct_change(1) > 0
        stk_up_days_pct = stk_up_days.loc[date_list].sum(axis=0) / len(date_list)
        fd = FactorData()
        w_dragon_df = fd.get_factor_value('WIND_AIndexMembersWIND',
                                        factors=['S_CON_WINDCODE'],
                                        CUR_SIGN=[1],
                                        F_INFO_WINDCODE=['884254.WI'])
        stk_list = w_dragon_df['S_CON_WINDCODE'].tolist()
        stk_list = list(map(lambda x: stockList.trans_windcode2int(x), stk_list))
        top20_stk_code = list(reversed(ann_stk_pct[stk_list].dropna().sort_values().index.tolist()[-20:]))
        bottom20_stk_code = list(reversed(ann_stk_pct[stk_list].dropna().sort_values().index.tolist()[:20]))
        index_list = top20_stk_code + bottom20_stk_code
        ret = pd.DataFrame(index=index_list,
                           columns=['股票名称', '本年涨跌幅', '本年上涨天数占比', '所属申万二级行业', '对应申万二级行业涨跌幅'])

        ret['股票名称'] = ret.index.map(lambda x: MyUtil.get_1stock_name(x))
        ret['本年涨跌幅'] = ret.index.map(lambda x: ann_stk_pct.loc[x])
        ret['本年上涨天数占比'] = ret.index.map(lambda x: stk_up_days_pct[x])
        ret['所属申万二级行业'] = ret.index.map(lambda x: self.get_sw2_ind(x))
        ret['对应申万二级行业涨跌幅'] = ret.index.map(lambda x: self.get_sw2_pct(x, ann_sw2_pct))

        ret.to_excel(junk_path + 'ann_ind_stats_part5.xlsx')
        send_file(['015614'], junk_path + 'ann_ind_stats_part5.xlsx')

    def get_month12_sw2_pct(self):
        trade_months = [20210930, 20211029, 20211130, 20211224]
        date_list = tradeDate.get_date_range(trade_months[-2], trade_months[-1])
        ann_stk_pct = self.daily_stk_close.loc[trade_months[-1]] / self.daily_stk_close.loc[trade_months[-2]] - 1
        sw2_amt_month12 = self.sw2_amt.loc[20211201:20211224].sum()
        sw2_amt_month11 = self.sw2_amt.loc[20211101:20211130].sum()
        sw2_amt_mom = sw2_amt_month12 / sw2_amt_month11 - 1

        sw2_pct = self.sw2_close.loc[trade_months[-1]] / self.sw2_close.loc[trade_months[-2]] - 1
        ret = pd.DataFrame(index=sw2_pct.index.tolist())
        ret['行业简称'] = ret.index.map(lambda x: self.sw_ind_name[x])
        ret['12月份涨跌幅'] = sw2_pct.values
        ret['中位数涨幅'] = ret.index.map(lambda x: np.nanmedian(ann_stk_pct[self.sw2_stk_list[x]].values))
        ret['环比'] = ret.index.map(lambda x: sw2_amt_mom.loc[x])

        ret.to_excel(junk_path + '12月份申万二级行业.xlsx')
        send_file(['015614'], junk_path + '12月份申万二级行业.xlsx')

    def get_q4_sw2_pct(self):
        trade_months = [20210630, 20210930, 20211224]
        date_list = tradeDate.get_date_range(trade_months[-2], trade_months[-1])
        ann_stk_pct = self.daily_stk_close.loc[trade_months[-1]] / self.daily_stk_close.loc[trade_months[-2]] - 1
        sw2_amt_month12 = self.sw2_amt.loc[tradeDate.get_pre_trade_date(20210930, -1):20211224].sum()
        sw2_amt_month11 = self.sw2_amt.loc[tradeDate.get_pre_trade_date(20210630, -1):20210930].sum()
        sw2_amt_mom = sw2_amt_month12 / sw2_amt_month11 - 1

        sw2_pct = self.sw2_close.loc[trade_months[-1]] / self.sw2_close.loc[trade_months[-2]] - 1
        ret = pd.DataFrame(index=sw2_pct.index.tolist())
        ret['行业简称'] = ret.index.map(lambda x: self.sw_ind_name[x])
        ret['四季度涨跌幅'] = sw2_pct.values
        ret['中位数涨幅'] = ret.index.map(lambda x: np.nanmedian(ann_stk_pct[self.sw2_stk_list[x]].values))
        ret['环比'] = ret.index.map(lambda x: sw2_amt_mom.loc[x])

        ret.to_excel(junk_path + '四季度申万二级行业.xlsx')
        send_file(['015614'], junk_path + '四季度申万二级行业.xlsx')

    def get_sw2_ratio(self):
        trade_months = [20181228, 20201231, 20211224]

        fd = FactorData()
        sw_index_sector = pd.read_excel('/data/group/800442/800319/Faamonitor/basic/新申万行业.xlsx', index_col=0)
        sw_ind_list = sw_index_sector.index.tolist()
        sw_ind_list.remove('801011.SI')
        sw_ind_df = fd.get_factor_value('WIND_SWIndexMembers',
                                        factors=['S_CON_WINDCODE', 'S_INFO_WINDCODE', 'CUR_SIGN'],
                                        S_INFO_WINDCODE=sw_ind_list).set_index('S_CON_WINDCODE')
        sw_ind_df = sw_ind_df.query('CUR_SIGN == 1').sort_index()
        sw_ind_name = sw_index_sector['二级行业简称'].to_dict()
        sw_ind_df['二级行业简称'] = sw_ind_df['S_INFO_WINDCODE'].apply(lambda x: sw_ind_name[x])

        sw2_info = fd.get_factor_value('WIND_ASWSIndexEOD',
                                       factor_names=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_CLOSE', 'S_DQ_AMOUNT'],
                                       S_INFO_WINDCODE=sw_ind_list,
                                       TRADE_DT=[f'>20181129'])
        sw2_close = sw2_info.pivot(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_CLOSE')
        sw2_amt = sw2_info.pivot(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_AMOUNT')
        sw2_amt = sw2_amt * 1e5
        sw2_close.index = sw2_close.index.map(int)
        sw2_amt.index = sw2_amt.index.map(int)

        # sw2_close = sw2_close.fillna(method='bfill')
        sw2_pct2020 = sw2_close / sw2_close.loc[trade_months[0]] - 1
        sw2_pct2021 = sw2_close / sw2_close.loc[trade_months[1]] - 1
        sw2_max_pct2020 = sw2_pct2020.max()
        sw2_max_pct2021 = sw2_pct2021.max()
        sw2_max_pct_ratio = sw2_max_pct2021 / sw2_max_pct2020

        sw2_2020_maxdrawdown = sw2_close.columns.map(lambda x: self.maxdrawdown(sw2_close.loc[trade_months[0]:trade_months[1], x].values))
        sw2_2021_maxdrawdown = sw2_close.columns.map(lambda x: self.maxdrawdown(sw2_close.loc[trade_months[1]:trade_months[2], x].values))
        sw2_maxdrawdown_ratio = sw2_2021_maxdrawdown / sw2_2020_maxdrawdown
        sw2_maxdrawdown_ratio = pd.Series(sw2_maxdrawdown_ratio, index=sw2_close.columns)
        sw2_2020_maxdrawdown = pd.Series(sw2_2020_maxdrawdown, index=sw2_close.columns)
        sw2_2021_maxdrawdown = pd.Series(sw2_2021_maxdrawdown, index=sw2_close.columns)

        ret = pd.DataFrame(index=sw2_close.columns.tolist())
        ret['行业简称'] = ret.index.map(lambda x: self.sw_ind_name[x])
        ret['2019年以来最大上涨'] = ret.index.map(lambda x: sw2_max_pct2020.loc[x])
        ret['2021年以来最大上涨'] = ret.index.map(lambda x: sw2_max_pct2021.loc[x])
        ret['上涨幅度比例'] = ret.index.map(lambda x: sw2_max_pct_ratio.loc[x])

        ret['2019年以来最大回撤'] = ret.index.map(lambda x: sw2_2020_maxdrawdown.loc[x])
        ret['2021年以来最大回撤'] = ret.index.map(lambda x: sw2_2021_maxdrawdown.loc[x])
        ret['调整深度'] = ret.index.map(lambda x: sw2_maxdrawdown_ratio.loc[x])

        ret.to_excel(junk_path + '申万二级行业调整深度.xlsx')
        send_file(['015614'], junk_path + '申万二级行业调整深度.xlsx')

    def get_sw1_ratio(self):
        trade_months = [20181228, 20201231, 20211224]

        fd = FactorData()
        sw_index_sector = pd.read_excel('/data/group/800442/800319/Faamonitor/basic/新申万一级行业.xlsx', index_col=0)
        sw_ind_list = sw_index_sector.index.tolist()
        sw_ind_df = fd.get_factor_value('WIND_SWIndexMembers',
                                        factors=['S_CON_WINDCODE', 'S_INFO_WINDCODE', 'CUR_SIGN'],
                                        S_INFO_WINDCODE=sw_ind_list).set_index('S_CON_WINDCODE')
        sw_ind_df = sw_ind_df.query('CUR_SIGN == 1').sort_index()
        sw_ind_name = sw_index_sector['一级行业简称'].to_dict()
        sw_ind_df['一级行业简称'] = sw_ind_df['S_INFO_WINDCODE'].apply(lambda x: sw_ind_name[x])

        sw1_info = fd.get_factor_value('WIND_ASWSIndexEOD',
                                       factor_names=['S_INFO_WINDCODE', 'TRADE_DT', 'S_DQ_CLOSE', 'S_DQ_AMOUNT'],
                                       S_INFO_WINDCODE=sw_ind_list,
                                       TRADE_DT=[f'>20181129'])
        sw1_close = sw1_info.pivot(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_CLOSE')
        sw1_amt = sw1_info.pivot(index='TRADE_DT', columns='S_INFO_WINDCODE', values='S_DQ_AMOUNT')
        sw1_amt = sw1_amt * 1e5
        sw1_close.index = sw1_close.index.map(int)
        sw1_amt.index = sw1_amt.index.map(int)

        sw1_pct2020 = sw1_close / sw1_close.loc[trade_months[0]] - 1
        sw1_pct2021 = sw1_close / sw1_close.loc[trade_months[1]] - 1
        sw1_max_pct2020 = sw1_pct2020.max()
        sw1_max_pct2021 = sw1_pct2021.max()
        sw1_max_pct_ratio = sw1_max_pct2021 / sw1_max_pct2020

        sw1_2020_maxdrawdown = sw1_close.columns.map(
            lambda x: self.maxdrawdown(sw1_close.loc[trade_months[0]:trade_months[1], x].values))
        sw1_2021_maxdrawdown = sw1_close.columns.map(
            lambda x: self.maxdrawdown(sw1_close.loc[trade_months[1]:trade_months[2], x].values))
        sw1_maxdrawdown_ratio = sw1_2021_maxdrawdown / sw1_2020_maxdrawdown
        sw1_maxdrawdown_ratio = pd.Series(sw1_maxdrawdown_ratio, index=sw1_close.columns)
        sw1_2020_maxdrawdown = pd.Series(sw1_2020_maxdrawdown, index=sw1_close.columns)
        sw1_2021_maxdrawdown = pd.Series(sw1_2021_maxdrawdown, index=sw1_close.columns)

        ret = pd.DataFrame(index=sw1_close.columns.tolist())
        ret['行业简称'] = ret.index.map(lambda x: sw_ind_name[x])
        ret['2019年以来最大上涨'] = ret.index.map(lambda x: sw1_max_pct2020.loc[x])
        ret['2021年以来最大上涨'] = ret.index.map(lambda x: sw1_max_pct2021.loc[x])
        ret['上涨幅度比例'] = ret.index.map(lambda x: sw1_max_pct_ratio.loc[x])

        ret['2019年以来最大回撤'] = ret.index.map(lambda x: sw1_2020_maxdrawdown.loc[x])
        ret['2021年以来最大回撤'] = ret.index.map(lambda x: sw1_2021_maxdrawdown.loc[x])
        ret['调整深度'] = ret.index.map(lambda x: sw1_maxdrawdown_ratio.loc[x])

        ret.to_excel(junk_path + '申万一级行业调整深度.xlsx')
        send_file(['015614'], junk_path + '申万一级行业调整深度.xlsx')

    @staticmethod
    def get_sw2_stk_pct():
        fd = FactorData()
        sw_index_sector = pd.read_excel('/data/group/800442/800319/Faamonitor/basic/新申万行业.xlsx', index_col=0)
        sw_ind_list = sw_index_sector.index.tolist()
        sw_ind_list.remove('801011.SI')
        sw_ind_df = fd.get_factor_value('WIND_SWIndexMembers',
                                        factors=['S_CON_WINDCODE', 'S_INFO_WINDCODE', 'CUR_SIGN', 'S_CON_INDATE', 'S_CON_OUTDATE'],
                                        S_INFO_WINDCODE=sw_ind_list).set_index('S_CON_WINDCODE')
        tar_date = 20210101
        sw_ind_df = sw_ind_df.query(f'S_CON_INDATE < \'{tar_date}\' & S_CON_OUTDATE < \'{tar_date}\'')

        # 取历史成分股个数，万德可以直接取
        # 取历史成分股个数，万德可以直接取
        # 取历史成分股个数，万德可以直接取


if __name__ == '__main__':
    ais = AnnIndStats()
    # ais.get_monthly_pct()
    # ais.get_sw2_ann_pct()
    # ais.get_stk_ann_pct()
    # ais.get_wind_dragon_index()

    # ais.get_month12_sw2_pct()
    # ais.get_q4_sw2_pct()
    # ais.get_sw2_ratio()
    # ais.get_sw1_ratio()
    ais.get_sw2_stk_pct()

