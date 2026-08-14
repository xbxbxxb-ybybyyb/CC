from FactorCalculator_old.UsefulList import MaterialList, LowFreqList, MinuteList, DesampleMethod
from FactorCalculator_old.Desample import ReduceMaterial
from FactorCalculator_old.Operators import *
import pandas as pd
import numpy as np
import time
import dask
import os
import gc
import re

realtime_path = '/data/group/800442/realtime_data/%s/%s/stock/'
# realtime_path = '/data/group/800002/realtime/alpha/market_data/%s/%s/stock/'
# realtime_path = '/data/group/800442/simulate_data/%s/%s/stock/'
base_data_path = '/data/group/800442/800319/strategy_HFfactor2/'
# factor_list = pd.read_pickle(f'{base_data_path}20210715/DateCode/factor_list.pkl')
reduce = ReduceMaterial()

print(realtime_path)
def search_index(bench_mark, a):
    x = np.asanyarray(bench_mark)
    y = np.asanyarray(a)
    index = np.argsort(x)
    sorted_x = x[index]
    sorted_index = np.searchsorted(sorted_x, y)
    y_index = np.take(index, sorted_index, mode="clip")
    mask = x[y_index] != y
    result = np.ma.array(y_index, mask=mask, fill_value=0)
    return result


class MinFactorCalculator(object):
    def __init__(self, date, log=print):
        self.date = date
        self.log = log
        self.Data = {}
        self.M5Data = {}
        self.pre_bar = 0

        hist_min_path = f'{base_data_path}/{date}/TmrMinMaterial/'
        hist_dp_path = f'{base_data_path}/{date}/TmrDesampleMaterial/'
        hist_lf_path = f'{base_data_path}/{date}/TmrLowFreq/'
        hist_dc_path = f'{base_data_path}/{date}/DateCode/'
        hist_mv_path = f'{base_data_path}/{date}/TmrMeanStd/'

        for each in [hist_min_path, hist_dp_path, hist_lf_path, hist_dc_path, hist_mv_path]:
            if not os.path.exists(each):
                raise Exception(f'{each} not exist')

        # 检查数据更新
        for name in MaterialList:
            self.check_file_mod_time(f'{hist_min_path}/{name}.npy')
        for name in MaterialList:
            self.check_file_mod_time(f'{hist_dp_path}/{name}.npy')
        for name in LowFreqList:
            self.check_file_mod_time(f'{hist_lf_path}/{name}.npy')
        for name in ['date_list', 'code_list']:
            self.check_file_mod_time(f'{hist_dc_path}/{name}.pkl')
        del name

        # 加载历史数据
        self.multidask('加载历史数据',
                       [[self.load_hist_data, (hist_min_path, x)] for x in MaterialList] +
                       [[self.load_m5_hist_data, (hist_dp_path, x)] for x in MaterialList] +
                       [[self.load_hist_data, (hist_lf_path, x)] for x in LowFreqList] +
                       [[self.load_hist_data, (hist_dc_path, 'code_list')]])
        self.Data['vwap'] = np.empty((1, 242, len(self.Data['code_list'])))

        # 调整股本
        if 'pre_close' in self.Data:
            _participation = np.where(self.Data['share_ratio'] > 0,
                                      (self.Data['_close'] - self.Data['pre_close'] - self.Data['payout_ratio']) / (
                                              self.Data['pre_close'] * self.Data['share_ratio'] - self.Data[
                                          'receive_ratio']), 1)
            _participation[~ np.isfinite(self.Data['pre_close'])] = 1
            _share_adjust = 1 + self.Data['share_ratio'] * _participation
            del _participation, self.Data['pre_close']
        else:
            _share_adjust = 1 + self.Data['share_ratio']
        _share_adjust[~ np.isfinite(_share_adjust)] = 1
        self.Data['free_float_shares'] *= _share_adjust
        self.Data['total_shares'] *= _share_adjust
        del _share_adjust, self.Data['_close']
        del self.Data['payout_ratio'], self.Data['share_ratio'], self.Data['receive_ratio']

        # 财务辅助
        self.Data['growth'] *= self.Data['profit']
        self.Data['growth'] /= self.Data['total_shares']
        self.Data['growth'] /= 1e4
        self.Data['ocf'] /= self.Data['total_shares']
        self.Data['ocf'] /= 1e4
        self.Data['rtdearn'] /= self.Data['total_shares']
        self.Data['rtdearn'] /= 1e4
        self.Data['profit'] /= self.Data['total_shares']
        self.Data['profit'] /= 1e4
        self.Data['f_profit'] /= self.Data['total_shares']
        self.Data['f_equity'] /= self.Data['total_shares']

        self.Data['_peg_hist'] = self.Data['growth']
        self.Data['_pcf_hist'] = self.Data['ocf']
        self.Data['_pb_hist'] = self.Data['rtdearn']
        self.Data['_pe_hist'] = self.Data['profit']
        self.Data['_pe_f2'] = self.Data['f_eps']
        self.Data['_pe_f1'] = self.Data['f_profit']
        self.Data['_pb_f1'] = self.Data['f_equity']

        del self.Data['total_shares'], self.Data['growth'], self.Data['ocf'], self.Data['rtdearn'], \
            self.Data['profit'], self.Data['f_eps'], self.Data['f_profit'], self.Data['f_equity']

        # 加载因子均值标准差
        self.factor_list = pd.read_pickle(f'{hist_dc_path}/factor_list.pkl')
        self.MV = pd.read_pickle(f'{hist_mv_path}/MV.pkl')
        self.FACTOR = {}
        self.FACTOR_REVIEW = {x[0]: np.full((242, len(self.Data['code_list'])), np.nan) for x in self.factor_list}

        # 加载降采样因子均值标准差
        self.desample_factor_list = pd.read_pickle(f'{hist_dc_path}/desample_factor_list.pkl')
        self.DpMV = pd.read_pickle(f'{hist_mv_path}/DpMV.pkl')
        self.M5FACTOR = {}
        self.M5FACTOR_REVIEW = {x[0]: np.full(
            (242, len(self.Data['code_list'])), np.nan) for x in self.desample_factor_list}
        self.factor = pd.DataFrame(index=[x[0] for x in self.factor_list] + [x[0] for x in self.desample_factor_list],
                                   columns=self.Data['code_list'], dtype='float32')
        gc.collect()

    def calc_bar_data(self, now_time, pre_time=0, ignore_col=True, threads=1):
        pre_bar = MinuteList.index(pre_time) if pre_time else self.pre_bar
        bar = MinuteList.index(now_time)
        self.TEMP = {}
        self.multidask(f'{now_time}加载日内行情', [
            [self.load_bar_data, ('close', 'close', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('open', 'opn', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('high', 'high', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('low', 'low', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('volume', 'vol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('amt', 'adj_amt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('close_adj', 'adj_close', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('open_adj', 'adj_opn', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('high_adj', 'adj_high', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('low_adj', 'adj_low', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('volume_adj', 'adj_vol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('buytradenum', 'num_buy', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('selltradenum', 'num_sell', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('numtrade', 'num_total', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('accamountbuy', 'accamountbuy', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('accamountsell', 'accamountsell', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('activebuyorderamt', 'activebuyorderamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('activebuyordervol', 'activebuyordervol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('activesellorderamt', 'activesellorderamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('activesellordervol', 'activesellordervol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('buyorderamt', 'buyorderamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('buyordercanceledamt', 'buyordercanceledamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('buyordercanceledvol', 'buyordercanceledvol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('buyordervol', 'buyordervol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('buytradeamt', 'buytradeamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('buytradevol', 'buytradevol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('passivebuyorderamt', 'passivebuyorderamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('passivebuyordervol', 'passivebuyordervol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('passivesellorderamt', 'passivesellorderamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('passivesellordervol', 'passivesellordervol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('sellorderamt', 'sellorderamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('sellordercanceledamt', 'sellordercanceledamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('sellordercanceledvol', 'sellordercanceledvol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('sellordervol', 'sellordervol', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('selltradeamt', 'selltradeamt', now_time, bar, pre_bar, ignore_col)],
            [self.load_bar_data, ('selltradevol', 'selltradevol', now_time, bar, pre_bar, ignore_col)],
        ])

        # 基础处理
        _ = time.time()
        ret_close_lag = np.empty_like(self.TEMP['adj_close'])
        ret_close_lag[0] = self.TEMP['_adj_close']
        ret_close_lag[1:] = self.TEMP['adj_close'][:-1]
        ret_close = self.TEMP['adj_close'] / ret_close_lag
        np.log(ret_close, out=ret_close)
        ret_close *= 1e3

        vwap = np.where(self.TEMP['vol'] > 99, self.TEMP['adj_amt'] / self.TEMP['vol'], self.TEMP['opn'])
        _vwap = self.Data['vwap'][-1, pre_bar - 2] if pre_bar >= 2 else self.Data['_adj_close']
        ret_vwap = np.empty_like(vwap)
        ret_vwap[0] = np.log(vwap[0] / _vwap) * 1e3 if pre_bar >= 2 else ret_close[0]
        ret_vwap[1:] = np.log(vwap[1:] / vwap[:-1]) * 1e3
        self.TEMP['ret_close'] = ret_close
        self.TEMP['ret_vwap'] = ret_vwap
        self.TEMP['vwap'] = vwap
        self.log(f'{now_time}基础处理: 用时{round(time.time() - _, 3)}秒')

        self.multidask(f'{now_time}笔数量纲_增强合并_高频财务_基础收益', [
            [self.calc_deal_num, ('num_buy',)],
            [self.calc_deal_num, ('num_sell',)],
            [self.calc_deal_num, ('num_total',)],
            [self.calc_dev_add, ('buyordercanceledamt', 'sellordercanceledamt', 'ordercanceledamt')],
            [self.calc_dev_add, ('buyordercanceledvol', 'sellordercanceledvol', 'ordercanceledvol')],
            [self.calc_dev_add, ('passivebuyorderamt', 'passivesellorderamt', 'passiveorderamt')],
            [self.calc_dev_add, ('passivebuyordervol', 'passivesellordervol', 'passiveordervol')],
            [self.calc_dev_add, ('activebuyorderamt', 'activesellorderamt', 'activeorderamt')],
            [self.calc_dev_add, ('activebuyordervol', 'activesellordervol', 'activeordervol')],
            [self.calc_dev_add, ('accamountbuy', 'accamountsell', 'accamount')],
            [self.calc_dev_add, ('buytradeamt', 'selltradeamt', 'tradeamt')],
            [self.calc_dev_add, ('buytradevol', 'selltradevol', 'tradevol')],
            [self.calc_dev_add, ('buyorderamt', 'sellorderamt', 'orderamt')],
            [self.calc_dev_add, ('buyordervol', 'sellordervol', 'ordervol')],
            [self.calc_fin_ratio, ('_pe_hist', 'pe_hist')],
            [self.calc_fin_ratio, ('_pb_hist', 'pb_hist')],
            [self.calc_fin_ratio, ('_pcf_hist', 'pcf_hist')],
            [self.calc_fin_ratio, ('_peg_hist', 'peg_hist')],
            [self.calc_fin_ratio, ('_pe_f2', 'pe_f2')],
            [self.calc_fin_ratio, ('_pe_f1', 'pe_f1')],
            [self.calc_fin_ratio, ('_pb_f1', 'pb_f1')],
            [self.calc_base_ret, ('close', 'vwap', 'ret_close_vwap')],
            [self.calc_base_ret, ('high', 'vwap', 'ret_high')],
            [self.calc_base_ret, ('low', 'vwap', 'ret_low')],
            [self.calc_base_ret, ('high', 'close', 'ret_high_close')],
            [self.calc_base_ret, ('low', 'close', 'ret_low_close')],
        ])

        self.multidask(f'{now_time}计算增强收益', [
            [self.calc_dev_ret, ('trade', 'ret_trade')],
            [self.calc_dev_ret, ('order', 'ret_order')],
            [self.calc_dev_ret, ('buytrade', 'ret_trade_buy')],
            [self.calc_dev_ret, ('selltrade', 'ret_trade_sell')],
            [self.calc_dev_ret, ('ordercanceled', 'ret_cancel')],
            [self.calc_dev_ret, ('buyordercanceled', 'ret_cancel_buy')],
            [self.calc_dev_ret, ('sellordercanceled', 'ret_cancel_sell')],
            [self.calc_dev_ret, ('buyorder', 'ret_order_buy')],
            [self.calc_dev_ret, ('sellorder', 'ret_order_sell')],
            [self.calc_dev_ret, ('activeorder', 'ret_order_active')],
            [self.calc_dev_ret, ('activebuyorder', 'ret_order_active_buy')],
            [self.calc_dev_ret, ('activesellorder', 'ret_order_active_sell')],
            [self.calc_dev_ret, ('passiveorder', 'ret_order_passive')],
            [self.calc_dev_ret, ('passivebuyorder', 'ret_order_passive_buy')],
            [self.calc_dev_ret, ('passivesellorder', 'ret_order_passive_sell')],
        ])

        self.multidask(f'{now_time}计算增强换手', [
            [self.calc_dev_turn, ('', 'turn_total')],
            [self.calc_dev_turn, ('buytrade', 'turn_trade_buy')],
            [self.calc_dev_turn, ('selltrade', 'turn_trade_sell')],
            [self.calc_dev_turn, ('ordercanceled', 'turn_cancel')],
            [self.calc_dev_turn, ('buyordercanceled', 'turn_cancel_buy')],
            [self.calc_dev_turn, ('sellordercanceled', 'turn_cancel_sell')],
            [self.calc_dev_turn, ('order', 'turn_order')],
            [self.calc_dev_turn, ('buyorder', 'turn_order_buy')],
            [self.calc_dev_turn, ('sellorder', 'turn_order_sell')],
            [self.calc_dev_turn, ('activeorder', 'turn_order_active')],
            [self.calc_dev_turn, ('activebuyorder', 'turn_order_active_buy')],
            [self.calc_dev_turn, ('activesellorder', 'turn_order_active_sell')],
            [self.calc_dev_turn, ('passiveorder', 'turn_order_passive')],
            [self.calc_dev_turn, ('passivebuyorder', 'turn_order_passive_buy')],
            [self.calc_dev_turn, ('passivesellorder', 'turn_order_passive_sell')],
            [self.calc_dev_turn_acc, ('accamount', 'turn_acc')],
            [self.calc_dev_turn_acc, ('accamountbuy', 'turn_acc_buy')],
            [self.calc_dev_turn_acc, ('accamountsell', 'turn_acc_sell')],
        ])

        self.multidask(f'{now_time}合并基础因子', [[self.concat_min_data, (x, bar, pre_bar)]
                                             for x in MaterialList + ['vwap']])

        self.multidask(f'{now_time}降采样基础因子', [
            [self.desample_min_data, (x,)] for x in MaterialList])

        self.multidask(f'{now_time}计算因子', [[self.calc_mul_factor, (
            self.factor_list[x::threads], bar, pre_bar)] for x in range(threads)])

        self.multidask(f'{now_time}计算降采样因子', [[self.calc_dp_mul_factor, (
            self.desample_factor_list[x::threads], bar, pre_bar)] for x in range(threads)])
        del self.TEMP
        self.pre_bar = bar

    def check_file_mod_time(self, file):
        try:
            mod_time = int(time.strftime('%Y%m%d%H%M%S', time.localtime(os.path.getmtime(file))))
        except FileNotFoundError:
            self.log(f'文件不存在: {file}')
        else:
            target_time = self.date * 1000000
            if mod_time <= target_time:
                self.log(f'可能未更新: {file}, mode time: {mod_time}')

    def multidask(self, dask_name, dask_list):
        lines = len(dask_list)
        batches = []
        t = time.time()
        self.log(f'{dask_name}: 等待{lines}条线程全部完成...')
        for j in range(lines):
            batches.append(dask.delayed(dask_list[j][0])(*dask_list[j][1]))
        dask.compute(batches)
        t = round(time.time() - t, 3)
        self.log(f'{dask_name}: 多线程结束, 用时{t}秒')

    def load_hist_data(self, path, name):
        ext = 'npy' if name not in ['date_list', 'code_list'] else 'pkl'
        func = np.load if ext == 'npy' else pd.read_pickle
        try:
            self.Data[name] = func(f'{path}/{name}.{ext}')
        except:
            pass

    def load_m5_hist_data(self, path, name):
        ext = 'npy' if name not in ['date_list', 'code_list'] else 'pkl'
        func = np.load if ext == 'npy' else pd.read_pickle
        try:
            self.M5Data[name] = func(f'{path}/{name}.{ext}')
        except:
            pass

    def load_bar_data(self, name_in, name_out, now_time, bar, pre_bar, ignore_col=True):
        while True:
            try:
                arr = pd.read_pickle(realtime_path % (self.date, now_time) + f'/{name_in}.pkl')
                # TODO
                from dataApi.stockList import trans_int2windcode
                __code_list = [trans_int2windcode(x) for x in self.Data['code_list']]
                arr = arr.reindex(columns=__code_list)
                # TODO
            except FileNotFoundError:
                continue
            else:
                break

        if not ignore_col:
            columns = [int(x[:-3]) for x in arr.columns.to_list()]
            code_index = search_index(self.Data['code_list'], columns)
        arr = arr.values
        if not ignore_col:
            arr = arr[:, ~code_index.mask]

        if name_in == 'close_adj':
            self.TEMP['_adj_close'] = arr[[pre_bar - 2]] if pre_bar >= 2 else self.Data['_adj_close']
        arr = arr[max(pre_bar - 1, 0): bar]
        self.TEMP[name_out] = arr

    def calc_dev_add(self, name1_in, name2_in, name_out):
        self.TEMP[name_out] = self.TEMP[name1_in] + self.TEMP[name2_in]

    def calc_fin_ratio(self, name_in, name_out):
        self.TEMP[name_out] = self.Data[name_in] / self.TEMP['close']

    def calc_base_ret(self, name1_in, name2_in, name_out):
        self.TEMP[name_out] = np.log(self.TEMP[name1_in] / self.TEMP[name2_in]) * 1e3

    def calc_deal_num(self, name_in):
        self.TEMP[name_in] /= 100

    def calc_dev_ret(self, name_in, name_out):
        self.TEMP[name_in + 'amt'] /= self.TEMP[name_in + 'vol']
        self.TEMP[name_in + 'amt'] /= self.TEMP['vwap']
        self.TEMP[name_in + 'amt'][~ (self.TEMP[name_in + 'vol'] > 99)] = 1
        np.log(self.TEMP[name_in + 'amt'], out=self.TEMP[name_in + 'amt'])
        self.TEMP[name_in + 'amt'] *= 1e3
        self.TEMP[name_out] = self.TEMP[name_in + 'amt']
        del self.TEMP[name_in + 'amt']

    def calc_dev_turn(self, name_in, name_out):
        self.TEMP[name_in + 'vol'] /= self.Data['free_float_shares']
        self.TEMP[name_out] = self.TEMP[name_in + 'vol']
        del self.TEMP[name_in + 'vol']

    def calc_dev_turn_acc(self, name_in, name_out):
        self.TEMP[name_in] /= self.TEMP['vwap']
        self.TEMP[name_in] /= 20
        self.TEMP[name_in] /= self.Data['free_float_shares']
        self.TEMP[name_out] = self.TEMP[name_in]
        del self.TEMP[name_in]

    def concat_min_data(self, name_in, bar, pre_bar):
        self.Data[name_in][-1, max(pre_bar - 1, 0): bar] = self.TEMP[name_in]

    def desample_min_data(self, name_in):
        self.M5Data[name_in][-1] = getattr(reduce, DesampleMethod[name_in])(
            self.Data[name_in][-1:])[0]

    def calc_sig_factor(self, name, formula, lag_days, bar, pre_bar, no_dt=False):
        replace = lambda x: x[1] + ("self.Data['%s'][-lag_days-1:, :bar]" if no_dt
                                    else "self.Data['%s'][-lag_days-1:]") % x[2] + x[3]
        formula = re.sub('([\u0020\u0028])([a-zA-Z_]+[12]?)([\u0029\u002c])', replace, formula)
        self.FACTOR[name] = eval(formula)[-1, :bar]
        self.FACTOR[name][~ np.isfinite(self.FACTOR[name])] = np.nan
        self.FACTOR[name] -= self.MV['mean'][name]
        self.FACTOR[name] /= self.MV['std'][name]
        self.FACTOR[name].clip(-6, 6, out=self.FACTOR[name])
        self.FACTOR[name][~ np.isfinite(self.FACTOR[name])] = 0
        self.FACTOR_REVIEW[name][pre_bar: bar] = self.FACTOR[name][pre_bar: bar]
        self.factor.loc[name] = self.FACTOR[name][-1]

    def calc_dp_sig_factor(self, name, formula, lag_days, bar, pre_bar, no_dt=False):
        m5_bar = reduce.first_idx.index(bar)
        m5_pre_bar = reduce.first_idx.index(pre_bar) if pre_bar in reduce.first_idx else 0
        replace = lambda x: x[1] + ("self.M5Data['%s'][-lag_days-1:, :m5_bar]" if no_dt
                                    else "self.M5Data['%s'][-lag_days-1:]") % x[2] + x[3]
        formula = re.sub('([\u0020\u0028])([a-zA-Z_]+[12]?)([\u0029\u002c])', replace, formula)
        self.M5FACTOR[name] = eval(formula)[-1, :m5_bar]
        self.M5FACTOR[name][~ np.isfinite(self.M5FACTOR[name])] = np.nan
        self.M5FACTOR[name] -= self.DpMV['mean'][name]
        self.M5FACTOR[name] /= self.DpMV['std'][name]
        self.M5FACTOR[name].clip(-6, 6, out=self.M5FACTOR[name])
        self.M5FACTOR[name][~ np.isfinite(self.M5FACTOR[name])] = 0
        self.M5FACTOR_REVIEW[name][m5_pre_bar: m5_bar] = self.M5FACTOR[name][m5_pre_bar: m5_bar]
        self.factor.loc[name] = self.M5FACTOR[name][-1]

    def calc_mul_factor(self, sub_list, bar, pre_bar):
        for fac in sub_list:
            self.calc_sig_factor(fac[0], fac[1], fac[2], bar, pre_bar, fac[3])

    def calc_dp_mul_factor(self, sub_list, bar, pre_bar):
        for fac in sub_list:
            self.calc_dp_sig_factor(fac[0], fac[1], fac[2], bar, pre_bar, fac[3])

# self = MinFactorCalculator(20210715)
# self.calc_bar_data(1400, threads=24)
# formula = '''div2(dt_lwm(relu(sub2(ret_order_passive, ret_order)), 242), dt_lwm(relu(sub2(ret_order, ret_order_passive)), 242))'''
# lag_days = 60
# bar = 31
# pre_bar = 0
#
# for x in self.factor_list:
#     print(x[1])
#     self.calc_sig_factor(x[0], x[1], x[2], 1000, 0, x[3])
