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
        factor_name = str(param_tuple)
        func1, param1, param2, param3, func2 = param_tuple

        if return_fillna_dic:
            # 返回因子为nan时的填充值
            return {factor_name: 0}

        dt, Ticker = df.index[0]
        zcz = (Ticker[0] == '3' and dt.strftime('%Y-%m-%d') >= '2020-08-24') or (Ticker[0:2] == '68')

        df = df[df['TradePrice'] > 0]
        df['buy_sell'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(int)
        df = df[df['MDTime'] >= 93000000]
        pre_close = df.iloc[-1]['pre_close']
        ul_time = df.iloc[-1]['MDTime']

        # ----------------------------------
        # 触发前30/60/300秒
        if func1 == 'time':
            target_time = fun_get_time(int(ul_time), -param1)
            df = df.query(f'MDTime >= {target_time}')
        # 触发前100/500/1000单
        elif func1 == 'deal_num':
            if len(df) > param2:
                df = df.iloc[-param2:]
            else:
                df = df
        # 首次超过0.09, 0.095, 0.098
        elif func1 == 'pct':
            df['idx'] = range(0, len(df))
            pct9_price = pre_close * (1 + 0.09) if not zcz else pre_close * (1 + 0.09 * 2)
            first_idx = df.query(f'TradePrice >= {pct9_price}').iloc[0]['idx']
            df = df.query(f'idx >= {first_idx}')

        # ----------------------------------
        if func2 == 'big':
            buy_deal_df = df.query(f'TradeMoney > 200000 & buy_sell == 1')
        elif func2 == 'mid':
            buy_deal_df = df.query(f'50000 <= TradeMoney < 200000 & buy_sell == 1')
        elif func2 == 'sml':
            buy_deal_df = df.query(f'TradeMoney < 50000 & buy_sell == 1')

        if buy_deal_df.shape[0] != 0:
            ret = buy_deal_df.groupby('TradeBuyNo')['TradeMoney'].sum().max() / df.query('buy_sell == 1').groupby('TradeBuyNo')['TradeMoney'].sum().max()
        else:
            ret = 0

        factor = ret
        factor_dict = {factor_name: factor}

        return pd.Series(factor_dict)


if __name__ == '__main__':
    note = '大中小买单金额最大值与全天占比&group以后'
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