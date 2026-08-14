# coding: utf-8
# Author：fengchi863
# Date ：2021/11/18 11:15

'''
统计定增数据
'''

import time
import gc
import numpy as np
import pandas as pd
from xquant.factordata import FactorData
from FaaMonitor.Util.MyUtil import MyUtil
from FaaMonitor.Util.DtUtil import DtUtil
from ShortTermTrading.dataApi import getData, tradeDate, stockList
from ShortTermTrading.conf.path_conf import junk_path
from FaaMonitor.Util.tools import send_file

import random


class PPStats:
    def __init__(self, start_date=20190101, end_date=20211121):
        start_date = start_date
        end_date = end_date
        date_list = tradeDate.get_date_range(start_date, end_date)
        close_badj = getData.get_daily_1factor('close_badj', date_list=date_list)

        self.close_badj = close_badj
        up_trend = self.calc_stk_trend()
        self.up_trend = up_trend

    @staticmethod
    def get_pp_data():
        fd = FactorData()
        pp_df = fd.get_factor_value('WIND_AShareSEO', PRICINGDATE=['>=20200214'])
        col = ['S_INFO_WINDCODE',
               'S_FELLOW_DATE',
               'PRICINGDATE',
               'PRICE_DT_TYPE',
               'S_FELLOW_OFFERINGOBJECT',
               'S_SEO_HOLDERSUBSMODE',
               'S_SEO_HOLDERSUBSRATE']
        pp_df = pp_df[col]

        rename_dict = {
            'S_INFO_WINDCODE': '股票代码',
            'S_FELLOW_DATE': '定增发行日期',
            'PRICINGDATE': '定价基准日',
            'PRICE_DT_TYPE': '定价基准日类型',
            'S_FELLOW_OFFERINGOBJECT': '发行对象',
            'S_SEO_HOLDERSUBSMODE': '大股东认购方式',
            'S_SEO_HOLDERSUBSRATE': '大股东认购比例'
        }
        pp_df = pp_df.rename(columns=rename_dict)

        pp_df['定价基准日'] = pp_df['定价基准日'].astype(int)
        pp_df = pp_df.sort_values(['定价基准日'])
        pp_df = pp_df.query('定价基准日类型 != \'董事会决议公告日\'')
        pp_df = pp_df.reset_index(drop=True)
        pp_df['股票名称'] = pp_df['股票代码'].apply(lambda x: MyUtil.get_1stock_name(x))
        return pp_df

    def get_range_pct(self, stk_id, start_date, end_date):
        if type(stk_id) is str:
            stk_id = stockList.trans_windcode2int(stk_id)
        start = tradeDate.get_pre_trade_date(start_date, 1)
        end = tradeDate.get_pre_trade_date(end_date, 1)
        pct = self.close_badj.loc[end, stk_id] / self.close_badj.loc[start, stk_id] - 1
        return pct

    def calc_stk_trend(self):
        ma5 = self.close_badj.rolling(5).mean()
        ma20 = self.close_badj.rolling(20).mean()
        ma60 = self.close_badj.rolling(60).mean()
        up_trend1 = (ma5 > ma20) & (ma20 > ma60)
        # down_trend1 = (ma5 < ma20 < ma60)

        short_expma = self.close_badj.ewm(span=12, adjust=False).mean()
        long_expma = self.close_badj.ewm(span=50, adjust=False).mean()
        up_trend2 = (self.close_badj > long_expma) & (short_expma > long_expma)
        # down_trend2 = (short_expma < long_expma) & (self.close_badj < long_expma)

        up_trend = up_trend1 | up_trend2
        # down_trend = down_trend1 | down_trend2
        # other_trend = 1 - (up_trend | down_trend)

        # return up_trend.shift(1), down_trend.shift(1), other_trend.shift(1)
        return up_trend.shift(1)

    def calc_up2down_days_num(self, stk_id, start_date, end_date, shift_days_num):
        if type(stk_id) is str:
            stk_id = stockList.trans_windcode2int(stk_id)

        trend = self.up_trend.copy()
        trend = np.array(trend.loc[start_date:end_date, stk_id].tolist())

        sub1 = trend[::-1].cumsum()
        sub2 = (trend[::-1] == 0) * sub1
        sub2 = np.where(sub2 == 0, np.nan, sub2)
        sub2 = pd.Series(sub2.tolist()).fillna(method='ffill').tolist()
        res = (sub1 - sub2)[::-1]

        search_start_idx = np.flatnonzero((res[1:] > 0) & (res[:-1] == 0))
        start_idx = search_start_idx + 1
        search_end_idx = np.flatnonzero(res == 1)
        end_idx = search_end_idx + 1

        date_list = tradeDate.get_date_range(start_date, end_date)
        start_date_list, end_date_list = list(), list()
        for start in start_idx:
            start_date_list.append(date_list[start])
        for end in end_idx:
            end_date_list.append(date_list[end])

        up_date_list = list()
        for start_date in start_date_list:
            for end_date in end_date_list:
                if end_date > start_date:
                    up_date_list.append((start_date, end_date))
                    break

        ret = list()
        for batch in up_date_list:
            start, end = batch
            period_len = tradeDate.get_trade_date_interval(end, start)
            start2pricing = tradeDate.get_trade_date_interval(end_date, start)
            end2pricing = tradeDate.get_trade_date_interval(end_date, end)
            pct_chg = self.close_badj.loc[end, stk_id] / self.close_badj.loc[start, stk_id] - 1
            ret.append((shift_days_num, start, end, period_len, pct_chg, start2pricing, end2pricing))

        return ret

    @staticmethod
    def judge_holder(offer_obj):
        strong_stock_holder_list = ['大股东', '大股东关联方', '公司股东']
        strings = offer_obj.split(',')
        if len(set(strong_stock_holder_list) & set(strings)) > 0:
            return '是'
        else:
            return '否'


if __name__ == '__main__':
    ppstats = PPStats()
    # 统计锁价前5/10/20/30/40/60个交易日的涨跌幅
    pricing_date = '定价基准日'
    shift_days_nums = [5, 10, 20, 30, 40, 60]
    today_date = DtUtil.get_today_date()
    t = time.time()
    pp_df = ppstats.get_pp_data()

    # 生成原表
    output_df4 = pp_df.copy()

    for shift_days_num in shift_days_nums:
        col_name = f'锁价前{shift_days_num}个交易日'
        pp_df[col_name] = pp_df[pricing_date].\
            apply(lambda x: tradeDate.get_pre_trade_date(x, shift_days_num))
        pp_df[f'锁价前{shift_days_num}日涨跌幅'] = pp_df[['股票代码', pricing_date, col_name]].\
            apply(lambda x: ppstats.get_range_pct(x['股票代码'], x[col_name], x[pricing_date]), axis=1)

    # 同时保存锁价前N日涨跌幅
    for shift_days_num in shift_days_nums:
        output_df4[f'锁价前{shift_days_num}日涨跌幅'] = pp_df[f'锁价前{shift_days_num}日涨跌幅']

    # 不同分位数的涨跌幅
    index_list = ['锁价前%d日涨跌幅' % d for d in shift_days_nums]
    col_float_list = list(np.arange(11) / 10)
    # col_name_list = ['MIN', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', 'MAX']
    output_df1 = pd.DataFrame(index=col_float_list, columns=index_list)
    for shift_days_num in shift_days_nums:
        for percentile in col_float_list:
            col_name = f'锁价前{shift_days_num}日涨跌幅'
            output_df1.loc[percentile, col_name] = pp_df[col_name].quantile(q=percentile)

    # 统计平均数、盈亏比等信息
    index_list = ['锁价前%d日涨跌幅' % d for d in shift_days_nums]
    col_name_list = ['收益率平均值', '中位数', '盈利个数', '亏损个数', '胜率', '盈亏比', '收益率方差']
    output_df5 = pd.DataFrame(index=col_name_list, columns=index_list)
    for shift_days_num in shift_days_nums:
        col_name = f'锁价前{shift_days_num}日涨跌幅'
        output_df5.loc['收益率平均值', col_name] = pp_df[col_name].mean()
        output_df5.loc['中位数', col_name] = pp_df[col_name].median()
        output_df5.loc['盈利个数', col_name] = len(pp_df[pp_df[col_name] > 0])
        output_df5.loc['亏损个数', col_name] = len(pp_df[pp_df[col_name] < 0])
        output_df5.loc['胜率', col_name] = len(pp_df[pp_df[col_name] > 0]) / len(pp_df)
        output_df5.loc['个数比', col_name] = len(pp_df[pp_df[col_name] > 0]) / len(pp_df[pp_df[col_name] < 0])
        output_df5.loc['盈亏比', col_name] = -pp_df[pp_df[col_name] > 0][col_name].mean() / \
            pp_df[pp_df[col_name] < 0][col_name].mean()
        output_df5.loc['收益率方差', col_name] = pp_df[col_name].std()

    # 统计含有大股东参与定增的项目的收益情况
    pp_df['是否有大股东参与'] = pp_df['发行对象'].apply(lambda x: ppstats.judge_holder(x))
    strong_pp_df = pp_df[pp_df['是否有大股东参与'] == '是']
    other_pp_df = pp_df[pp_df['是否有大股东参与'] == '否']
    index_list = ['锁价前%d日涨跌幅' % d for d in shift_days_nums]
    tmp_df1 = pd.DataFrame(index=col_name_list, columns=index_list)
    tmp_df2 = pd.DataFrame(index=col_name_list, columns=index_list)
    for shift_days_num in shift_days_nums:
        col_name = f'锁价前{shift_days_num}日涨跌幅'
        tmp_df1.loc['收益率平均值', col_name] = strong_pp_df[col_name].mean()
        tmp_df1.loc['中位数', col_name] = strong_pp_df[col_name].median()
        tmp_df1.loc['盈利个数', col_name] = len(strong_pp_df[strong_pp_df[col_name] > 0])
        tmp_df1.loc['亏损个数', col_name] = len(strong_pp_df[strong_pp_df[col_name] < 0])
        tmp_df1.loc['胜率', col_name] = len(strong_pp_df[strong_pp_df[col_name] > 0]) / len(strong_pp_df)
        tmp_df1.loc['个数比', col_name] = len(strong_pp_df[strong_pp_df[col_name] > 0]) / \
            len(strong_pp_df[strong_pp_df[col_name] < 0])
        tmp_df1.loc['盈亏比', col_name] = -strong_pp_df[strong_pp_df[col_name] > 0][col_name].mean() / \
            strong_pp_df[strong_pp_df[col_name] < 0][col_name].mean()
        tmp_df1.loc['收益率方差', col_name] = strong_pp_df[col_name].std()
    tmp_df1 = tmp_df1.reset_index()
    tmp_df1['发行对象分类'] = '有大股东参与'
    for shift_days_num in shift_days_nums:
        col_name = f'锁价前{shift_days_num}日涨跌幅'
        tmp_df2.loc['收益率平均值', col_name] = other_pp_df[col_name].mean()
        tmp_df2.loc['中位数', col_name] = other_pp_df[col_name].median()
        tmp_df2.loc['盈利个数', col_name] = len(other_pp_df[other_pp_df[col_name] > 0])
        tmp_df2.loc['亏损个数', col_name] = len(other_pp_df[other_pp_df[col_name] < 0])
        tmp_df2.loc['胜率', col_name] = len(other_pp_df[other_pp_df[col_name] > 0]) / len(other_pp_df)
        tmp_df2.loc['个数比', col_name] = len(other_pp_df[other_pp_df[col_name] > 0]) / \
            len(other_pp_df[other_pp_df[col_name] < 0])
        tmp_df2.loc['盈亏比', col_name] = -other_pp_df[other_pp_df[col_name] > 0][col_name].mean() / \
            other_pp_df[other_pp_df[col_name] < 0][col_name].mean()
        tmp_df2.loc['收益率方差', col_name] = other_pp_df[col_name].std()
    tmp_df2 = tmp_df2.reset_index()
    tmp_df2['发行对象分类'] = '无大股东参与'
    output_df6 = pd.concat([tmp_df1, tmp_df2], axis=0, ignore_index=True)
    output_df6 = output_df6.set_index(['发行对象分类', 'index'])
    output_df6.index.names = ['发行对象分类', '指标']
    gc.collect()

    # 大股东参与比例分层分析
    layer = [0, 25, 50, 75, 100]
    df_list = list()
    for idx in range(1, len(layer)):
        low_threshold = layer[idx - 1]
        high_threshold = layer[idx]
        strong_tmp_df = strong_pp_df.query(f'{high_threshold} > 大股东认购比例 >= {low_threshold}')
        tmp_df = pd.DataFrame(index=col_name_list, columns=index_list)
        for shift_days_num in shift_days_nums:
            col_name = f'锁价前{shift_days_num}日涨跌幅'
            tmp_df.loc['收益率平均值', col_name] = strong_tmp_df[col_name].mean()
            tmp_df.loc['中位数', col_name] = strong_tmp_df[col_name].median()
            tmp_df.loc['盈利个数', col_name] = len(strong_tmp_df[strong_tmp_df[col_name] > 0])
            tmp_df.loc['亏损个数', col_name] = len(strong_tmp_df[strong_tmp_df[col_name] < 0])
            tmp_df.loc['胜率', col_name] = len(strong_tmp_df[strong_tmp_df[col_name] > 0]) / len(strong_tmp_df)
            tmp_df.loc['盈亏比', col_name] = -strong_tmp_df[strong_tmp_df[col_name] > 0][col_name].mean() / \
                strong_tmp_df[strong_tmp_df[col_name] < 0][col_name].mean()
            tmp_df.loc['收益率方差', col_name] = strong_tmp_df[col_name].std()
        tmp_df = tmp_df.reset_index()
        tmp_df['股东认购比例'] = f'{low_threshold}%-{high_threshold}%'
        df_list.append(tmp_df)

    strong_tmp_df = strong_pp_df.query('大股东认购比例==100')
    tmp_df = pd.DataFrame(index=col_name_list, columns=index_list)
    for shift_days_num in shift_days_nums:
        col_name = f'锁价前{shift_days_num}日涨跌幅'
        tmp_df.loc['收益率平均值', col_name] = strong_tmp_df[col_name].mean()
        tmp_df.loc['中位数', col_name] = strong_tmp_df[col_name].median()
        tmp_df.loc['盈利个数', col_name] = len(strong_tmp_df[strong_tmp_df[col_name] > 0])
        tmp_df.loc['亏损个数', col_name] = len(strong_tmp_df[strong_tmp_df[col_name] < 0])
        tmp_df.loc['胜率', col_name] = len(strong_tmp_df[strong_tmp_df[col_name] > 0]) / len(strong_tmp_df)
        tmp_df.loc['盈亏比', col_name] = -strong_tmp_df[strong_tmp_df[col_name] > 0][col_name].mean() / \
                                      strong_tmp_df[strong_tmp_df[col_name] < 0][col_name].mean()
        tmp_df.loc['收益率方差', col_name] = strong_tmp_df[col_name].std()
    tmp_df = tmp_df.reset_index()
    tmp_df['股东认购比例'] = f'100%'
    df_list.append(tmp_df)

    output_df7 = pd.concat(df_list, axis=0, ignore_index=True)
    output_df7 = output_df7.set_index(['股东认购比例', 'index'])
    output_df7.index.names = ['股东认购比例', '指标']

    # 超过某一涨跌幅的占比
    index_list = ['锁价前%d日涨跌幅' % d for d in shift_days_nums]
    col_float_list = [0.5, 0.4, 0.3, 0.2, 0.1, 0, -0.1, -0.2, -0.3, -0.4, -0.5]
    output_df2 = pd.DataFrame(index=col_float_list, columns=index_list)
    for shift_days_num in shift_days_nums:
        for pct_threshold in col_float_list:
            col_name = f'锁价前{shift_days_num}日涨跌幅'
            output_df2.loc[pct_threshold, col_name] = len(pp_df[pp_df[col_name] > pct_threshold]) / len(pp_df)

    # 统计60日内任一天到锁价日的涨跌幅
    fc_shift_days_nums = list(range(1, 150))
    for shift_days_num in fc_shift_days_nums:
        col_name = f'锁价前{shift_days_num}个交易日'
        pp_df[col_name] = pp_df[pricing_date]. \
            apply(lambda x: tradeDate.get_pre_trade_date(x, shift_days_num))
        pp_df[f'锁价前{shift_days_num}日涨跌幅'] = pp_df[['股票代码', pricing_date, col_name]]. \
            apply(lambda x: ppstats.get_range_pct(x['股票代码'], x[col_name], x[pricing_date]), axis=1)

    # 统计平均数、盈亏比等信息
    index_list = ['锁价前%d日涨跌幅' % d for d in fc_shift_days_nums]
    col_name_list = ['收益率平均值', '中位数', '盈利个数', '亏损个数', '胜率', '盈亏比', '收益率方差']
    output_df8 = pd.DataFrame(index=col_name_list, columns=index_list)
    for shift_days_num in fc_shift_days_nums:
        col_name = f'锁价前{shift_days_num}日涨跌幅'
        output_df8.loc['收益率平均值', col_name] = pp_df[col_name].mean()
        output_df8.loc['中位数', col_name] = pp_df[col_name].median()
        output_df8.loc['盈利个数', col_name] = len(pp_df[pp_df[col_name] > 0])
        output_df8.loc['亏损个数', col_name] = len(pp_df[pp_df[col_name] < 0])
        output_df8.loc['胜率', col_name] = len(pp_df[pp_df[col_name] > 0]) / len(pp_df)
        output_df8.loc['个数比', col_name] = len(pp_df[pp_df[col_name] > 0]) / len(pp_df[pp_df[col_name] < 0])
        output_df8.loc['盈亏比', col_name] = -pp_df[pp_df[col_name] > 0][col_name].mean() / \
                                          pp_df[pp_df[col_name] < 0][col_name].mean()
        output_df8.loc['收益率方差', col_name] = pp_df[col_name].std()

    # 模拟仿真机器人，前14天内存在60%的正确率，然后15-60天内存在40%的正确率
    t1 = time.time()
    simulator_time = 2000
    col_name_list = ['收益率平均值', '中位数', '盈利个数', '亏损个数', '胜率', '盈亏比', '收益率方差']
    output_df9 = pd.DataFrame(index=range(simulator_time), columns=col_name_list)
    for sim_time in range(simulator_time):
        print(f'{sim_time}/{simulator_time}')
        # 第一种平均分布的方式
        # proj_idx = list(range(len(pp_df)))
        #
        # random.shuffle(proj_idx)
        # interval1 = int(np.floor(0.8 * len(proj_idx)))
        # interval2 = len(proj_idx) - interval1
        #
        # robot1 = dict(zip(proj_idx[:interval1], np.random.randint(1, 60, interval1)))
        # robot2 = dict(zip(proj_idx[interval1:], np.random.randint(61, 130, interval2)))

        # 第二种靠后分布的方式：10%：0-20,70%：20-60,20%：60-130
        proj_idx = list(range(len(pp_df)))

        random.shuffle(proj_idx)
        interval1 = int(np.floor(0.1 * len(proj_idx)))
        interval2 = interval1 + int(np.floor(0.7 * len(proj_idx)))

        robot1 = dict(zip(proj_idx[:interval1], np.random.randint(1, 20, len(proj_idx[:interval1]))))
        robot2 = dict(zip(proj_idx[interval1:interval2], np.random.randint(21, 60, len(proj_idx[interval1:interval2]))))
        robot3 = dict(zip(proj_idx[interval2:], np.random.randint(61, 130, len(proj_idx[interval2:]))))

        # 第二种前20日
        return_list = list()
        for idx in robot1.keys():
            lead_days = robot1[idx]
            col_name = f'锁价前{lead_days}日涨跌幅'
            return_list.append(pp_df.iloc[idx][col_name])
        for idx in robot2.keys():
            lead_days = robot2[idx]
            col_name = f'锁价前{lead_days}日涨跌幅'
            return_list.append(pp_df.iloc[idx][col_name])
        for idx in robot3.keys():
            lead_days = robot3[idx]
            col_name = f'锁价前{lead_days}日涨跌幅'
            return_list.append(pp_df.iloc[idx][col_name])

        output_df9.loc[sim_time, '收益率平均值'] = np.mean(return_list)
        output_df9.loc[sim_time, '中位数'] = np.median(return_list)
        output_df9.loc[sim_time, '盈利个数'] = len([i for i in return_list if i > 0])
        output_df9.loc[sim_time, '亏损个数'] = len([i for i in return_list if i < 0])
        output_df9.loc[sim_time, '胜率'] = len([i for i in return_list if i > 0]) / len(return_list)
        output_df9.loc[sim_time, '盈亏比'] = -np.mean([i for i in return_list if i > 0]) / \
                                          np.mean([i for i in return_list if i < 0])
        output_df9.loc[sim_time, '收益率方差'] = np.std(return_list)
    print('消耗时间：', time.time() - t1)

    # 上行趋势走到震荡趋势
    t1 = time.time()
    shift_days_nums = [20, 30, 40, 60]
    # ppstats.calc_up2down_days_num(300763, 20200828, 20201102)
    for shift_days_num in shift_days_nums:
        col_name = f'锁价前{shift_days_num}个交易日'
        pp_df[col_name + '趋势统计'] = pp_df[['股票代码', col_name, pricing_date]]. \
            apply(lambda x: ppstats.calc_up2down_days_num(x['股票代码'], x[col_name], x[pricing_date], \
                                                          shift_days_num), axis=1)
    print(time.time() - t1)

    # 拆解
    col_list = ['股票代码',
                pricing_date]
    add_col_list = ['锁价前N天', '开始日期', '结束日期', '持续时长', '区间涨跌幅', '开始到锁价间隔', '结束到锁价间隔']
    redefine_col = col_list + add_col_list
    output_df3 = pd.DataFrame()

    pp_df = pp_df.set_index(col_list)
    col_list = ['锁价前%d个交易日趋势统计' % d for d in shift_days_nums]

    for idx in range(len(pp_df)):
        print(f'{idx}/{len(pp_df)}')
        for shift_days_num in shift_days_nums:
            stk_code = pp_df.iloc[idx].name[0]
            price_date = pp_df.iloc[idx].name[1]
            col_name = f'锁价前{shift_days_num}个交易日趋势统计'
            trend_infos = pp_df.loc[(stk_code, price_date), col_name]
            for trend_info in trend_infos:
                n, start, end, period_len, pctchg, start2pricing, end2pricing = trend_info
                output_df3 = output_df3.append([[stk_code, price_date] +
                                               [n, start, end, period_len, pctchg, start2pricing, end2pricing]])

    output_df3.columns = redefine_col
    output_df3['股票名称'] = output_df3['股票代码'].apply(lambda x: MyUtil.get_1stock_name(x))
    index_list = ['股票代码', '股票名称', '定价基准日', '锁价前N天']
    output_df3 = output_df3.sort_values(index_list)
    output_df3 = output_df3.set_index(index_list)

    # 保存
    save_dict = {'原始样本': output_df4,
                 '样本统计值': output_df5,
                 '前60日任一天买入结果': output_df8.T,
                 '模拟机器人结果': output_df9,
                 '不同分位数涨跌幅': output_df1,
                 '不同涨跌幅占比': output_df2,
                 '趋势统计': output_df3,
                 '有无大股东参与收益分类': output_df6,
                 '大股东不同认购比例下的收益分层': output_df7
                 }
    output_path = junk_path + '历史定增数据统计.xlsx'
    with pd.ExcelWriter(output_path) as writer:
        for each in save_dict:
            save_dict[each].to_excel(writer, each)
    print('保存原始样本')
    output_df4.to_pickle(junk_path + '定增数据原始样本.pkl')
    print('已保存至：', junk_path + '定增数据原始样本.pkl')
    send_file(['015614'], output_path)
