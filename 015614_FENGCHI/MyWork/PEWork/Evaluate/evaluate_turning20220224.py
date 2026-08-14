# coding: utf-8
# Author：fengchi863
# Date ：2022/2/22 15:53
"""
本版本只计算不同拐点版本的差异，带来的收益情况
"""

import warnings

import numpy as np
import pandas as pd
from tqdm import tqdm

warnings.filterwarnings('ignore')
from ShortTermTrading.conf.path_conf import junk_path
from ShortTermTrading.Util.tools import send_file
from dataApi import tradeDate


def search_neibor(s, max_close, min_close):
    """输入为一段从大到小排序的Series，index为时间戳"""
    trade_minutes = tradeDate.trade_minutes
    lowest_indexes = s[s == min_close].index.tolist()
    highest_indexes = s[s == max_close].index.tolist()
    lowest_ret = list()
    highest_ret = list()
    for lowest_index in lowest_indexes:
        idx = trade_minutes.index(lowest_index)
        start = idx - 3 if idx - 3 >= 0 else 0
        end = idx + 4 if idx + 4 <= len(trade_minutes) + 1 else len(trade_minutes) + 1
        lowest_ret += trade_minutes[start:end]
    for highest_index in highest_indexes:
        idx = trade_minutes.index(highest_index)
        start = idx - 3 if idx - 3 >= 0 else 0
        end = idx + 4 if idx + 4 <= len(trade_minutes) + 1 else len(trade_minutes) + 1
        highest_ret += trade_minutes[start:end]
    return list(set(lowest_ret)), list(set(highest_ret))


class TurningEvaluation:
    def __init__(self, stk_id):
        floder_path = f'/data/user/015624/缠论拐点/{stk_id}/'
        date_list = tradeDate.get_date_range(20210101, 20211231)
        compare_dict = {'2V1_剔除': ['第二类拐点类型', '拐点类型'],
                        '3V2_剔除': ['第三类拐点类型', '第二类拐点类型'],
                        '2V1_增加': ['第二类拐点类型', '拐点类型'],
                        '3V2_增加': ['第三类拐点类型', '第二类拐点类型']}

        self.date_list = date_list
        self.floder_path = floder_path
        self.compare_dict = compare_dict
        self.stk_id = stk_id

    def calc_daily_indicator(self, prefix):
        rec_list = list()
        for date in tqdm(self.date_list):
            daily_rec = list()  # 未来5日收益率，未来10日收益率，相对收盘价的收益率，相对全天最值点的位置，出现到收盘的位置
            df = pd.read_pickle(self.floder_path + f'{prefix}{date}.pkl')
            close = df.loc[1500, 'close']
            df['拐点类型'] = df['拐点类型'].fillna(0)
            df['第二类拐点类型'] = df['第二类拐点类型'].fillna(0)
            df['第三类拐点类型'] = df['第三类拐点类型'].fillna(0)
            df['未来5分钟收益率'] = df['close'].pct_change(5)
            df['未来10分钟收益率'] = df['close'].pct_change(10)
            df['相对收盘价的收益率'] = df.loc[1500, 'close'] / df['close'] - 1
            min_close = df['close'].min()
            max_close = df['close'].max()
            df['相对全天最值点的位置'] = (df['close'] - min_close) / (max_close - min_close)
            df['出现到收盘的位置'] = df['close'][::-1].expanding(1).apply(lambda x: x.argsort().argsort()[-1] / (len(x) - 1))[::-1]

            for key in self.compare_dict:
                compare = self.compare_dict[key]
                compare_df = df.loc[(df[compare[0]] != df[compare[1]]) & (df[compare[0]] * df[compare[1]] == 0)]
                if '增加' in key:
                    compare_df = compare_df[compare_df[compare[1]] == 0]
                    buy_df = compare_df.query(f'{compare[0]}==1')
                    sell_df = compare_df.query(f'{compare[0]}==-1')
                else:
                    compare_df = compare_df[compare_df[compare[0]] == 0]
                    buy_df = compare_df.query(f'{compare[1]}==1')
                    sell_df = compare_df.query(f'{compare[1]}==-1')

                # one day
                buy_num = len(buy_df)
                buy_pct5m = buy_df['未来5分钟收益率'].mean()
                buy_pct10m = buy_df['未来10分钟收益率'].mean()
                buy_rel_close = buy_df['相对收盘价的收益率'].mean()
                buy_quantile_allday = buy_df['相对全天最值点的位置'].mean()
                buy_quantile2close = buy_df['出现到收盘的位置'].mean()
                buy_mean_close = buy_df['close'].mean()

                sell_num = len(sell_df)
                sell_pct5m = sell_df['未来5分钟收益率'].mean()
                sell_pct10m = sell_df['未来10分钟收益率'].mean()
                sell_rel_close = sell_df['相对收盘价的收益率'].mean()
                sell_quantile_allday = sell_df['相对全天最值点的位置'].mean()
                sell_quantile2close = sell_df['出现到收盘的位置'].mean()
                sell_mean_close = sell_df['close'].mean()

                if np.isnan(sell_mean_close) and ~np.isnan(buy_mean_close):
                    daily_profit = close / buy_mean_close - 1
                elif np.isnan(buy_mean_close) and ~np.isnan(sell_mean_close):
                    daily_profit = sell_mean_close / close - 1
                else:
                    daily_profit = sell_mean_close / buy_mean_close - 1

                """计算几种最值点"""
                swing = max_close - min_close
                max_close2 = max_close - min(max_close * 0.02, swing * 0.2)
                min_close2 = min_close + min(min_close * 0.02, swing * 0.2)

                buy_tmp = buy_df['close'].map(lambda x: True if x < min_close2 else False)
                # buy_pct1 = len(buy_tmp[buy_tmp]) / len(buy_df) if len(buy_df) != 0 else 0
                sell_tmp = sell_df['close'].map(lambda x: True if x > max_close2 else False)
                # sell_pct1 = len(sell_tmp[sell_tmp]) / len(sell_df) if len(sell_df) != 0 else 0

                buy_neibor_minutes, sell_neibor_minutes = search_neibor(df['close'], max_close, min_close)
                buy_df['is_neibor'] = buy_df.index.map(lambda x: x in buy_neibor_minutes).values | buy_tmp.values
                sell_df['is_neibor'] = sell_df.index.map(lambda x: x in sell_neibor_minutes).values | sell_tmp.values
                buy_pct1 = buy_df['is_neibor'].sum() / len(buy_df) if len(buy_df) != 0 else np.nan
                sell_pct1 = sell_df['is_neibor'].sum() / len(sell_df) if len(sell_df) != 0 else np.nan

                daily_up_rec = [date, key, '向上', buy_num, buy_pct5m, buy_pct10m, buy_rel_close,
                                daily_profit, buy_quantile_allday, buy_quantile2close, buy_pct1]
                daily_down_rec = [date, key, '向下', sell_num, sell_pct5m, sell_pct10m, sell_rel_close,
                                  daily_profit, sell_quantile_allday, sell_quantile2close, sell_pct1]
                rec_list.append(daily_up_rec)
                rec_list.append(daily_down_rec)
        df = pd.DataFrame(rec_list)
        df.columns = ['日期', '对比类型', '拐点方向', '拐点个数', '未来5分钟收益率', '未来10分钟收益率', '相对收盘价的收益率',
                      '买卖点日收益率', '相对全天最值点的位置', '出现到收盘的位置', '当天在最值点分钟处比例']
        return df

    def evaluate(self):
        """文件名前缀"""
        # prefix_list = ['调整拐点', '80%调整拐点', '90%调整拐点']
        prefix_list = ['90%调整拐点']
        # prefix_list = ['调整拐点']
        # prefix_list = ['第二类调整', '第二类调整再叠加']

        for prefix in prefix_list:
            df = self.calc_daily_indicator(prefix)
            df['日期'] = df['日期'].map(str)
            rec_dict = dict()
            for key in self.compare_dict:
                rec_df = df[df['对比类型'] == key]
                rec_df = rec_df.set_index(['日期', '拐点方向'])
                rec_df['年度包含率'] = rec_df['当天在最值点分钟处比例'] > 0
                rec_df['买卖点日收益胜率'] = rec_df['买卖点日收益率'] > 0
                group_df = rec_df.groupby(['拐点方向']).agg({'拐点个数': 'mean',
                                                         '未来5分钟收益率': 'mean',
                                                         '未来10分钟收益率': 'mean',
                                                         '相对收盘价的收益率': 'mean',
                                                         '买卖点日收益率': 'mean',
                                                         '买卖点日收益胜率': 'sum',
                                                         '相对全天最值点的位置': 'mean',
                                                         '出现到收盘的位置': 'mean',
                                                         '当天在最值点分钟处比例': 'mean',
                                                         '年度包含率': 'sum'})
                group_df['年度包含率'] = group_df['年度包含率'] / len(self.date_list)
                group_df['买卖点日收益胜率'] = group_df['买卖点日收益胜率'] / len(self.date_list)

                rec_dict[f'{key}_按日统计'] = rec_df
                rec_dict[f'{key}_按年统计'] = group_df
            filename = f'{self.stk_id}_{prefix}统计结果_不同点对比.xlsx'
            self.save_result(rec_dict, filename)
            # send_file(['015614', '015624'], junk_path + filename)
            send_file(['015614'], junk_path + filename)

    @staticmethod
    def save_result(rec_dict, filename, folder_path=junk_path):
        with pd.ExcelWriter(folder_path + filename) as writer:
            for each in rec_dict:
                rec_dict[each].to_excel(writer, each)


if __name__ == '__main__':
    """601021春秋航空  858五粮液  300750宁德时代"""
    te = TurningEvaluation(601021)
    te.evaluate()

