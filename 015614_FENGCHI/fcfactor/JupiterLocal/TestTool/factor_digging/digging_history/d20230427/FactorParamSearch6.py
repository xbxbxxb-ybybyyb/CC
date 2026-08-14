# coding: utf-8
# Author：fengchi863
# Date ：2023/4/6 15:09
import pandas as pd
from JupiterLocal.TestTool.test1_factor_demo import strongFactorTest
from JupiterLocal.TestTool.run_factor_demo import run_factor
import IO
from multiprocessing import Pool
from itertools import product
from xquant.factordata import FactorData
from datetime import datetime
import os
from tqdm import tqdm
import numpy as np
import datetime as dt
s = FactorData()

def multiprocess(kernal_num, func, iterable, *args):
    pool = Pool(kernal_num)
    print('多进程启动')
    pool_apply_async = {}
    parts = len(iterable) // kernal_num
    remainder = len(iterable) % kernal_num
    iter_start = 0
    for j in range(kernal_num):
        if remainder > 0:
            iter_end = iter_start + parts + 1
            remainder = remainder - 1
        else:
            iter_end = iter_start + parts
        sub_iter = iterable[iter_start: iter_end]
        pool_apply_async[j] = pool.apply_async(func, (sub_iter,) + args)
        iter_start = iter_end
    pool.close()
    pool.join()
    print('多进程结束')
    return pool_apply_async

def fun_get_time(time1, sec_delta):
    # 计算给定时间戳time1在sec_delta秒后的时间戳
    tmp_time = dt.datetime.strptime(str(time1)[:-3], '%H%M%S')
    tmp_time2 = tmp_time + dt.timedelta(seconds=sec_delta)
    tmp_time2_str = tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
    if (int(tmp_time2_str) > 113000000) & (time1 <= 113000000):
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 130000000) & (time1 >= 130000000):
        adj_tmp_time2 = tmp_time2 - dt.timedelta(seconds=1.5 * 3600)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    elif (int(tmp_time2_str) < 93000000) & (time1 >= 93000000):
        adj_tmp_time2_str = '92500000'
        return int(adj_tmp_time2_str)
    elif time1 < 93000000:
        adj_tmp_time2 = tmp_time2 + dt.timedelta(seconds=4 * 60)
        adj_tmp_time2_str = adj_tmp_time2.strftime('%H%M%S') + str(time1)[-3:]
        return int(adj_tmp_time2_str)
    else:
        return int(tmp_time2_str)


class FactorParamSearch:
    def __init__(self, note=None):
        self.start_date = 20160101
        self.end_date = 20191231
        note = note
        self.basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_001.h5'

        cur_datetime = datetime.today().strftime('%Y%m%d%H%M%S')
        self.res_path = f'/data/user/015614/factor/factor_digging_{cur_datetime}_{note}/'
        os.makedirs(self.res_path)

    def wrapper(self, param_list):
        for param_tuple in tqdm(param_list):
            factor_name = str(param_tuple)
            # TODO: 第三个参数因子类型需要根据回测需求进行更改
            factor_df = run_factor(self.calc_factor, factor_name, 'TTransaction',
                           self.start_date, self.end_date, self.basic_file_path, self.res_path, param_tuple=param_tuple, interval_res=False)
            # factor_df = self.calc_factor(self.start_date, self.end_date, param_tuple) # 这个计算出来的因子有问题，比如没有填充、没有平移
            self.start_backtest(factor_df, param_tuple)

    def start_backtest(self, factor_df, param_tuple):
        bt_columns = ['nan_num', 'same_rate', 'value_diff_score', 'value_stability_score', 'mixed_diff_score',
                      'mixed_stability_score', 'score', 'corr_tot', 'mic_tot', 'high_corr_factor', 'high_corr_factor_corr']
        res_df = pd.DataFrame(columns=bt_columns)

        sft = strongFactorTest(self.start_date, self.end_date)
        res_dict = sft.factor_test(factor_df, result_path=self.res_path, factor_corr_test=True, generate_pdf=True)

        nan_num = res_dict['factor_information'].loc['Nan|Inf Count', 'Factor Info']
        same_rate = res_dict['other_sta'].loc['', 'same_rate']
        value_diff_score = res_dict['check_score_res'].loc['score', 'value_diff_score']
        value_stability_score = res_dict['check_score_res'].loc['score', 'value_stability_score']
        mixed_diff_score = res_dict['check_score_res'].loc['score', 'mixed_diff_score']
        mixed_stability_score = res_dict['check_score_res'].loc['score', 'mixed_stability_score']
        score = res_dict['check_score_res'].loc['score', 'tot_score']
        corr_tot = res_dict['corr_sta'].loc['corr_tot', 'value']
        mic_tot = res_dict['corr_sta'].loc['mic_tot', 'value']

        high_corr_s = res_dict['factor_corr'].query('factor_corr >= 0.7')
        if len(high_corr_s) == 0:
            high_corr_s = res_dict['factor_corr'].iloc[:2]
        else:
            high_corr_s = res_dict['factor_corr'].iloc[:len(high_corr_s) + 2]

        high_corr_factor_list_str = '，'.join(high_corr_s.index.tolist())
        high_corr_factor_corr_list_str = '，'.join(high_corr_s['factor_corr'].map(lambda x: round(x, 4)).map(str).tolist())

        res_df.loc[str(param_tuple)] = [nan_num, same_rate, value_diff_score, value_stability_score,
                                   mixed_diff_score, mixed_stability_score, score, corr_tot, mic_tot, high_corr_factor_list_str, high_corr_factor_corr_list_str]
        print(str(param_tuple), ': ', score)
        res_df.to_excel(self.res_path + f'{str(param_tuple)}.xlsx')
        factor_df.to_pickle(self.res_path + f'{str(param_tuple)}.pkl')

    @staticmethod
    def calc_factor(df, param_tuple, return_fillna_dic=False):
        factor_name = 'test'

        if return_fillna_dic:
            return {factor_name: 0}

        dt, Ticker = df.index[0]
        ff_shares = df['ff_shares'].iloc[0]
        df = df[df['TradeMoney'] > 0]
        df['buy_flag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(float)
        df = df[df['MDTime'] >= 93000000]

        sell_df = df[df['buy_flag'] == 0]
        group_sell_df = sell_df.groupby('TradeSellNo').agg({'TradeMoney': sum,
                                                            'TradeIndex': max})   # 保留大户
        big_group_sell = group_sell_df.query('TradeMoney > 200000')
        last_index = big_group_sell['TradeIndex'].iloc[-1] if len(big_group_sell) > 0 else 0
        last_buy = df[df['TradeIndex'] > last_index] if len(sell_df) != 0 else df

        if len(last_buy) == 0:
            ret = 0
        else:
            buy_deal_qty_max = last_buy.groupby('TradeBuyNo')['TradeQty'].sum().max()
            ret = buy_deal_qty_max / ff_shares / 1e4 # 最后最大买单的换手

        factor_dict = {factor_name: ret}

        return pd.Series(factor_dict)

if __name__ == '__main__':
    note = '主买最大换手'
    fps = FactorParamSearch(note=note)
    param_list = [['time', 'deal_num', 'pct'],
                  [30, 60, 300],
                  [100, 500, 1000],
                  [0.09, 0.095, 0.098],
                  ['big', 'mid', 'sml']]
    # param_list = [[5],  # param0
    #               ['corr']]  # func1
    param_list = list(product(*param_list))
    # multiprocess(20, fps.wrapper, param_list)
    # multiprocess(1, fps.wrapper, param_list)
    fps.wrapper([(5, 'corr')]) # 用于调试

    # check1 = IO.read_data([20160101, 20181231], alt='/data/user/018107/share_file/for_fc/fc_stk_zz1000_r_5.h5')
    # check2 = IO.read_data([20160101, 20181231], alt='/data/user/015614/factor/factor_digging_20230424160441新框架下与市场相关性测试/(5, \'corr\').h5')
    # check3 = IO.read_data([20160101, 20181231], alt='/data/user/015614/factor/factor_digging_20230424204144第二次跑并行测试一致性/(5, \'corr\').h5')
    # cmp = pd.concat([check1, check2], axis=1)
    # check1.mean()
    # check2.mean()