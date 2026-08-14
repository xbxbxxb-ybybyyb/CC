# coding: utf-8
# Author：fengchi863
# Date ：2022/3/28 15:35

"""
储存pctchg相似度数据
"""

from SimiStock.SimiStockGenerator.util import util
from SimiStock.config.path_config import *
import pandas as pd
import numpy as np
from tqdm import tqdm
from SimiStock.dataApi import tradeDate, getData


class PctCorr:
    def __init__(self, start_date=20180101, end_date=20211231, pre_days_num=120, method_name=None):
        block_data = pd.read_pickle(data_path + 'block_data_95.pkl')
        shift_start_date = tradeDate.get_pre_trade_date(start_date, 260)
        shift_end_date = tradeDate.get_pre_trade_date(end_date, -120)
        date_list = tradeDate.get_date_range(start_date, end_date)
        shift_date_list = tradeDate.get_date_range(shift_start_date, shift_end_date)

        self.date_list = date_list
        self.shift_date_list = shift_date_list

        pctchg = getData.get_daily_1factor('pct_chg', date_list=self.shift_date_list)
        code_list = np.load(barra_path + 'code_list.npy')
        self.code_list = list(code_list)

        self.block_data = block_data.query(f'{start_date} <= 交易日期 <= {end_date}')
        self.pctchg = pctchg

        self.method_name = method_name
        self.pre_days_num = pre_days_num

    def calc_corr(self, stk_id, trade_date):
        start_date = tradeDate.get_pre_trade_date(trade_date, self.pre_days_num)
        end_date = tradeDate.get_pre_trade_date(trade_date, 1)
        date_list = tradeDate.get_date_range(start_date, end_date)
        stk_pct = self.pctchg[stk_id][date_list]
        res_list = list()
        # for stk in self.code_list:
        #     compare = self.pctchg[stk][date_list]
        #     if np.isfinite(compare).sum() == 0:
        #         continue
        #     corr = np.corrcoef(stk_pct, compare)[0, 1]
        #     res_list.append(corr)
        # ret = [trade_date, stk_id]
        # ret = ret + res_list
        compare = self.pctchg[self.code_list].loc[date_list]
        corr = compare.corrwith(stk_pct)
        res_list = corr.values.tolist()
        ret = [trade_date, stk_id]
        ret = ret + res_list
        return ret

    def calc_corrs(self, stk_date_list):
        ret_list = list()
        pbar = tqdm(range(len(stk_date_list)))
        for idx in pbar:
            stk_id, trade_date = stk_date_list[idx]
            pbar.set_description('并行生成中|%s|%s' % (int(stk_id), int(trade_date)))
            hedge = self.calc_corr(stk_id, trade_date)
            ret_list.append(hedge)
        return ret_list

    def get_values(self, mode='serial', kernal_num=10):
        ret_list = []
        if mode is 'serial':
            pbar = tqdm(range(len(self.block_data)))
            for idx in pbar:
                row = self.block_data.iloc[idx]
                stk_id = row['股票代码']
                trade_date = row['交易日期']
                pbar.set_description('串行生成中|%s|%s' % (int(stk_id), int(trade_date)))
                ret_list.append(self.calc_corr(stk_id, trade_date))

        if mode is 'multi':
            stk_date_list = list(zip(self.block_data['股票代码'].tolist(), self.block_data['交易日期'].tolist()))
            ret_dict = util.multiprocess(kernal_num, self.calc_corrs, stk_date_list)

            ret_result = dict()
            for k in ret_dict:
                ret_result[k] = ret_dict[k].get()

            for k in ret_result:
                ret_list.extend(ret_result[k])

        return ret_list


if __name__ == '__main__':
    pc = PctCorr(start_date=20180101, end_date=20200630, pre_days_num=120)
    # ret_list = pc.get_values(mode='multi', kernal_num=10)
    ret_list = pc.get_values(mode='multi', kernal_num=10)
    ret_df = pd.DataFrame(ret_list)
    ret_df.columns = ['trade_date', 'stk_id'] + pc.code_list
    ret_df = ret_df.sort_values(['trade_date', 'stk_id'])
    ret_df = ret_df.set_index(['trade_date', 'stk_id'])
    util.save_df2pkl(ret_df, factor_path, f'pct_pearson_corr.pkl')
    # check = pd.read_pickle('/data/group/800442/800319/Afengchi/SimiStock/factors/pct_corr.pkl')
