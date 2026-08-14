# coding: utf-8
# Author：fengchi863
# Date ：2023/4/6 15:09
import sys
sys.path.append('/data/user/015614/fcfactor')

import pandas as pd
from EuropaLocal.TestTool.test1_factor_demo import strongFactorTest
from EuropaLocal.TestTool.run_factor_demo import run_factor
import IO
from multiprocessing import Pool
from itertools import product
from xquant.factordata import FactorData
from datetime import datetime
import os
from tqdm import tqdm
import datetime as dt
import numpy as np
import decimal
s = FactorData()

def round_(x, n=0):
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

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

def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    cov = np.nanmean(d_x * d_y, axis=0)
    var = (np.nanvar(x, axis=0) * np.nanvar(y, axis=0)) ** 0.5
    return cov / var

def array_rcorr_np(x, y):
    rank_x = np.argsort(np.argsort(x, axis=0), axis=0)
    rank_y = np.argsort(np.argsort(y, axis=0), axis=0)
    d_x, d_y = rank_x - np.nanmean(rank_x, axis=0), rank_y - np.nanmean(rank_y, axis=0)
    cov = np.nanmean(d_x * d_y, axis=0)
    var = (np.nanvar(rank_x, axis=0) * np.nanvar(rank_y, axis=0)) ** 0.5
    return cov / var

def weight_mean(elements, weights=None):
    if not weights:
        weights = [i / len(elements) for i in range(1, len(elements) + 1)]
    if len(elements) == 0 or len(weights) == 0:
        return 0
    else:
        return np.mean([x*y for x, y in zip(elements, weights)])

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

def cal_time_delta(start, end):
    start_str = str(start)
    end_str = str(end)
    time_delta = (int(end_str[:~6]) - int(start_str[:~6])) * 3600000 + \
                 (int(end_str[~6:~4]) - int(start_str[~6:~4])) * 60000 + \
                 (int(end_str[~4:~2]) - int(start_str[~4:~2])) * 1000 + \
                 (int(end_str[~2:]) - int(start_str[~2:]))
    if (start < 120000000) & (end > 120000000):
        time_delta = time_delta - 5400000
    return time_delta

def fun_shift_time(start_time, shift_time):
    start_str = str(start_time)
    end_int = int(start_str[:~6]) * 3600000 + \
              int(start_str[~6:~4]) * 60000 + \
              int(start_str[~4:~2]) * 1000 + \
              int(start_str[~2:]) + shift_time
    end_time = int((end_int - np.floor(end_int / 1000) * 1000) + \
                   (np.floor(end_int / 1000) - np.floor(end_int / 60000) * 60) * 1000 + \
                   (np.floor(end_int / 60000) - np.floor(end_int / 3600000) * 60) * 100000 + \
                   (np.floor(end_int / 3600000)) * 10000000)
    if (start_time < 113000000) & (end_time > 113000000) & (end_time < 130000000):
        end_time = fun_shift_time(end_time, 5400000)
    if (start_time > 130000000) & (end_time < 130000000) & (end_time > 113000000):
        end_time = fun_shift_time(end_time, -5400000)
    return max(93000000, end_time)

import decimal
def round_(x, n=0):
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))), rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

class FactorParamSearch:
    def __init__(self, note=None):
        self.start_date = 20160101
        self.end_date = 20191231
        note = note
        self.basic_file_path = '/data/group/800463/data/project1_public/factor_lib_v2/Basic_zt_001.h5'

        cur_datetime = datetime.today().strftime('%Y%m%d%H%M%S')
        self.res_path = f'/data/user/015614/factor/{note}_{cur_datetime}/'
        os.makedirs(self.res_path)

    def wrapper(self, param_list):
        for param_tuple in tqdm(param_list):
            factor_name = str(param_tuple)
            # TODO: 第三个参数因子类型需要根据回测需求进行更改
            factor_df = run_factor(self.calc_factor, factor_name, 'TTransaction',
                           self.start_date, self.end_date, self.basic_file_path, self.res_path, param_tuple=param_tuple, interval_res=False, multi=False)
            # factor_df = self.calc_factor(self.start_date, self.end_date, param_tuple) # 这个计算出来的因子有问题，比如没有填充、没有平移
            self.start_backtest(factor_df, param_tuple)

    def start_backtest(self, factor_df, param_tuple):
        bt_columns = ['nan_num', 'same_rate', 'value_diff_score', 'value_stability_score', 'mixed_diff_score',
                      'mixed_stability_score', 'score', 'corr_tot', 'mic_tot', 'high_corr_factor', 'high_corr_factor_corr', 'high_corr_s_num']
        res_df = pd.DataFrame(columns=bt_columns)

        # filter_factor = pd.read_pickle('/data/group/800463/data/project1_public/factor_lib_v2/filter_quickrise.pkl')
        # sft = strongFactorTest(self.start_date, self.end_date, filter_factor=filter_factor, filter_name='quickrise')
        sft = strongFactorTest(self.start_date, self.end_date)  # 全样本下测试
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

        high_corr_s = res_dict['factor_corr'].query('factor_corr >= 0.685')
        high_corr_s_num = len(res_dict['factor_corr_summary'])  # 分区间对比的 可为0、1、2
        if len(high_corr_s) == 0:
            high_corr_s = res_dict['factor_corr'].iloc[:2]
        else:
            high_corr_s = res_dict['factor_corr'].iloc[:len(high_corr_s) + 2]

        high_corr_factor_list_str = '，'.join(high_corr_s.index.tolist())
        high_corr_factor_corr_list_str = '，'.join(high_corr_s['factor_corr'].map(lambda x: round(x, 4)).map(str).tolist())

        res_df.loc[str(param_tuple)] = [nan_num, same_rate, value_diff_score, value_stability_score,
                                   mixed_diff_score, mixed_stability_score, score, corr_tot, mic_tot, high_corr_factor_list_str, high_corr_factor_corr_list_str, high_corr_s_num]
        print(str(param_tuple), ': ', score)
        res_df.to_excel(self.res_path + f'{str(param_tuple)}.xlsx')
        factor_df.to_pickle(self.res_path + f'{str(param_tuple)}.pkl')

    @staticmethod
    def calc_factor(df, param_tuple, return_fillna_dic=False):
        factor_name = str(param_tuple)
        param1, param2, param3 = param_tuple

        if return_fillna_dic:
            return {factor_name: 1}

        dt, Ticker = df.index[0]
        zcz = ((Ticker[0:2] == '30') & (dt.strftime('%Y%m%d') >= '20200824')) | (Ticker[0:2] == '68')
        ZT_Time = df['MDTime'].max()
        pre_close = df['pre_close'].iloc[0]
        df = df.query('TradeType == 0 & TradePrice > 0')
        df['TradeBSFlag'] = (df['TradeBuyNo'] > df['TradeSellNo']).astype(int)

        start_time1 = max(fun_get_time(ZT_Time, -param1), 93000000)
        start_time2 = max(fun_get_time(ZT_Time, -param2), 93000000)
        part_df1 = df.query(f'TradeMoney >= {param3} & MDTime >= {start_time1}')
        part_df2 = df.query(f'TradeMoney >= {param3} & {start_time2} >= MDTime >= {start_time1}')

        def calc_res(df_):
            if df_.query('TradeBSFlag == 1').shape[0] == 0 or df_.query('TradeBSFlag == 0').shape[0] == 0:
                ret = 1
            else:
                ret = df_.query('TradeBSFlag == 1').shape[0] / df_.query('TradeBSFlag == 0').shape[0]
            return ret

        res = calc_res(part_df1) - calc_res(part_df2)

        # print(res)
        factor_dict = {factor_name: res}
        # ---------------------------------------------------------------------------------------------------------------

        """
        MDTime: 时间 如101215000
        TradeBSFlag：不用这个
        TradeIndex：成交编号，与OrderIndex可匹配
        TradeBuyNo：买方委托序号 TradeBuyNo > TradeSellNo 主动买入 否则被动买入
        TradeSellNo：卖方委托序号
        # 以上委托序号与OrderIndex相同
        TradeType：成交类别
        TradeBSFlag：成交方向 1买 2卖
        TradePrice：成交价格
        TradeQty：成交数量
        TradeMoney：成交金额，等于0是撤单的股票
        pre_close：昨收价
        ff_shares：流通股数
        """
        return pd.Series(factor_dict)


if __name__ == '__main__':
    note = 'dig_TTrans4'
    fps = FactorParamSearch(note=note)
    param_list = [[5, 10, 30, 60, 90, 120, 300, 600, 1200, 1800, 3600, 6000, 7200],
                  [5, 10, 30, 60, 90, 120, 300, 600, 1200, 1800, 3600, 6000, 7200],
                  [0, 10000, 50000, 100000, 200000]]
    param_list = list(product(*param_list))
    param_list = list(filter(lambda x: x[0] < x[1], param_list))
    multiprocess(24, fps.wrapper, param_list)
    # multiprocess(1, fps.wrapper, param_list[0])
    # fps.wrapper([(6000, 7200, 0)]) # 用于调试