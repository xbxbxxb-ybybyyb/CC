import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from dataApi.getData import get_quarter_1factor, get_ttm_quarter, \
    get_single_quarter, fill_quarter2daily_by_issue_date, get_qoq
from dataApi.tradeDate import get_date_range, get_pre_trade_date, \
    get_trade_date_interval
from dataApi.dividend import getEXRightDividend
from HFfactor.MinFactorSuper.Utility.LoadBigData import \
    get_minute_data, get_daily_data, get_con_data, get_all_stock
from HFfactor.MinFactorSuper.Utility.Parallel import multidask
from HFfactor.MinFactorSuper.Utility.ExtendNumpy import store_augmented_matrix
from HFfactor.MinFactorSuper.RealTime.UsefulList import \
    MaterialList, DesampleMethod, MaterialDistAdjust
from HFfactor.MinFactorSuper.RealTime.Desample import ReduceMaterial
import pandas as pd
import numpy as np
import time
import gc


class MakeMaterial(object):

    def __init__(self, start_date=20140101, end_date=None,
                 root_path='/arch1/group/800442/800319/MinFactorSuper/'):
        gc.collect()
        t = time.time()
        self.date_list = get_date_range(start_date, end_date)
        self.end_date = self.date_list[-1]
        self.start_date = self.date_list[0]
        self.date_offset = get_trade_date_interval(self.start_date, 20140101)
        self.code_list = get_all_stock(self.end_date)

        self.root_path = root_path
        self.Data = {}

        multidask('导入历史分钟数据', [
            [self.calc_min_data, ('close', 'close')],
            [self.calc_min_data, ('open', 'opn')],
            [self.calc_min_data, ('high', 'high')],
            [self.calc_min_data, ('low', 'low')],
            [self.calc_min_data, ('volume', 'vol')],
            [self.calc_min_data, ('amt', 'adj_amt')],
            [self.calc_min_data, ('close_adj', 'adj_close')],
            [self.calc_min_data, ('open_adj', 'adj_opn')],
            [self.calc_min_data, ('high_adj', 'adj_high')],
            [self.calc_min_data, ('low_adj', 'adj_low')],
            [self.calc_min_data, ('volume_adj', 'adj_vol')],
            [self.calc_min_data, ('buytradenum', 'num_buy')],
            [self.calc_min_data, ('selltradenum', 'num_sell')],
            [self.calc_min_data, ('numtrade', 'num_total')],
            [self.calc_min_data, ('accamountbuy', 'accamountbuy')],
            [self.calc_min_data, ('accamountsell', 'accamountsell')],
            [self.calc_min_data, ('activebuyorderamt', 'activebuyorderamt')],
            [self.calc_min_data, ('activebuyordervol', 'activebuyordervol')],
            [self.calc_min_data, ('activesellorderamt', 'activesellorderamt')],
            [self.calc_min_data, ('activesellordervol', 'activesellordervol')],
            [self.calc_min_data, ('buyorderamt', 'buyorderamt')],
            [self.calc_min_data, ('buyordercanceledamt', 'buyordercanceledamt')],
            [self.calc_min_data, ('buyordercanceledvol', 'buyordercanceledvol')],
            [self.calc_min_data, ('buyordervol', 'buyordervol')],
            [self.calc_min_data, ('buytradeamt', 'buytradeamt')],
            [self.calc_min_data, ('buytradevol', 'buytradevol')],
            [self.calc_min_data, ('passivebuyorderamt', 'passivebuyorderamt')],
            [self.calc_min_data, ('passivebuyordervol', 'passivebuyordervol')],
            [self.calc_min_data, ('passivesellorderamt', 'passivesellorderamt')],
            [self.calc_min_data, ('passivesellordervol', 'passivesellordervol')],
            [self.calc_min_data, ('sellorderamt', 'sellorderamt')],
            [self.calc_min_data, ('sellordercanceledamt', 'sellordercanceledamt')],
            [self.calc_min_data, ('sellordercanceledvol', 'sellordercanceledvol')],
            [self.calc_min_data, ('sellordervol', 'sellordervol')],
            [self.calc_min_data, ('selltradeamt', 'selltradeamt')],
            [self.calc_min_data, ('selltradevol', 'selltradevol')],
        ])

        # 日频数据
        self.Data['_free_float_shares'], self.Data['_free_float_shares_tmr'] = get_daily_data(
            'free_float_shares', self.date_list, self.code_list)
        self.Data['_total_shares'], self.Data['_total_shares_tmr'] = get_daily_data(
            'total_shares', self.date_list, self.code_list)
        self.Data['_close'], self.Data['_close_tmr'] = get_daily_data(
            'close', self.date_list, self.code_list)
        self.Data['_pre_close'] = get_daily_data(
            'pre_close', self.date_list, self.code_list, lag=False, ffill=False)
        self.Data['_adj_close'] = get_minute_data(
            'close_adj', [get_pre_trade_date(self.date_list[0])], self.code_list)[-1, -1:]

        self.Data['_dividend'] = getEXRightDividend()
        self.Data['_payout_ratio'] = self.Data['_dividend'].pivot(
            'date', 'code', 'payoutRatio')
        self.Data['_payout_ratio_tmr'] = self.Data['_payout_ratio'].reindex(
            [get_pre_trade_date(self.date_list[-1], -1)], self.code_list).fillna(0).values
        self.Data['_payout_ratio'] = self.Data['_payout_ratio'].reindex(
            self.date_list, self.code_list).fillna(0).values[:, None]

        self.Data['_receive_ratio'] = self.Data['_dividend'].pivot(
            'date', 'code', 'receiveRatio')
        self.Data['_receive_ratio_tmr'] = self.Data['_receive_ratio'].reindex(
            [get_pre_trade_date(self.date_list[-1], -1)], self.code_list).fillna(0).values
        self.Data['_receive_ratio'] = self.Data['_receive_ratio'].reindex(
            self.date_list, self.code_list).fillna(0).values[:, None]

        self.Data['_share_ratio'] = self.Data['_dividend'].pivot(
            'date', 'code', 'shareRatio')
        self.Data['_share_ratio_tmr'] = self.Data['_share_ratio'].reindex(
            [get_pre_trade_date(self.date_list[-1], -1)], self.code_list).fillna(0).values
        self.Data['_share_ratio'] = self.Data['_share_ratio'].reindex(
            self.date_list, self.code_list).fillna(0).values[:, None]

        self.Data['_participation'] = np.where(self.Data['_share_ratio'] > 0, (
                self.Data['_close'] - self.Data['_pre_close'] - self.Data['_payout_ratio']) / (
                                                       self.Data['_pre_close'] * self.Data['_share_ratio'] - self.Data[
                                                   '_receive_ratio']), 1)
        self.Data['_share_adjust'] = 1 + self.Data['_share_ratio'] * self.Data['_participation']
        self.Data['_share_adjust'][~ np.isfinite(self.Data['_share_adjust'])] = 1
        self.Data['_free_float_shares'] *= self.Data['_share_adjust']
        self.Data['_total_shares'] *= self.Data['_share_adjust']

        # 财报数据
        self.Data['profit'] = fill_quarter2daily_by_issue_date(get_single_quarter(
            'net_profit_after_ded_nr_lp')).ffill()
        self.Data['profit_tmr'] = self.Data['profit'].loc[self.date_list[-1]].reindex(self.code_list).values[None, :]
        self.Data['profit'] = self.Data['profit'].shift().reindex(self.date_list, self.code_list).values[:, None, :]

        self.Data['rtdearn'] = fill_quarter2daily_by_issue_date(
            get_quarter_1factor('surplus_rsrv').add(get_quarter_1factor(
                'undistributed_profit_b'), fill_value=0).sub(get_quarter_1factor('less_tsy_stk'), fill_value=0)).ffill()
        self.Data['rtdearn_tmr'] = self.Data['rtdearn'].loc[self.date_list[-1]].reindex(self.code_list).values[None, :]
        self.Data['rtdearn'] = self.Data['rtdearn'].shift().reindex(self.date_list, self.code_list).values[:, None, :]

        self.Data['ocf'] = fill_quarter2daily_by_issue_date(get_ttm_quarter('net_cash_flows_oper_act')).ffill()
        self.Data['ocf_tmr'] = self.Data['ocf'].loc[self.date_list[-1]].reindex(self.code_list).values[None, :]
        self.Data['ocf'] = self.Data['ocf'].shift().reindex(self.date_list, self.code_list).values[:, None, :]

        self.Data['growth'] = fill_quarter2daily_by_issue_date(
            get_qoq(get_ttm_quarter('oper_profit').add(get_ttm_quarter(
                'less_selling_dist_exp'), fill_value=0).add(get_ttm_quarter('less_gerl_admin_exp'), fill_value=0).add(
                get_ttm_quarter('less_fin_exp'), fill_value=0).add(get_ttm_quarter(
                'less_impair_loss_assets'), fill_value=0))).ffill()
        self.Data['growth_tmr'] = self.Data['growth'].loc[self.date_list[-1]].reindex(self.code_list).values[None, :]
        self.Data['growth'] = self.Data['growth'].shift().reindex(self.date_list, self.code_list).values[:, None, :]

        # 预期数据
        self.Data['f_eps'], self.Data['f_eps_tmr'] = get_con_data('cfs_c1', self.date_list, self.code_list, 2)
        self.Data['f_profit'], self.Data['f_profit_tmr'] = get_con_data('cfc2s_c13', self.date_list, self.code_list)
        self.Data['f_equity'], self.Data['f_equity_tmr'] = get_con_data('cfc3s_cgb', self.date_list, self.code_list)

        # 财务辅助
        self.Data['_pe_hist'] = self.Data['profit'] / self.Data['_total_shares'] / 1e4
        self.Data['_pb_hist'] = self.Data['rtdearn'] / self.Data['_total_shares'] / 1e4
        self.Data['_pcf_hist'] = self.Data['ocf'] / self.Data['_total_shares'] / 1e4
        self.Data['_peg_hist'] = self.Data['profit'] * self.Data['growth'] / self.Data['_total_shares'] / 1e4
        self.Data['_pe_f2'] = self.Data['f_eps']
        self.Data['_pe_f1'] = self.Data['f_profit'] / self.Data['_total_shares']
        self.Data['_pb_f1'] = self.Data['f_equity'] / self.Data['_total_shares']

        # 基础处理
        self.Data['ret_close'] = self.Data['adj_close'].reshape(-1, self.Data['adj_close'].shape[2])
        self.Data['ret_close_lag'] = np.empty_like(self.Data['ret_close'])
        self.Data['ret_close_lag'][0] = self.Data['_adj_close']
        self.Data['ret_close_lag'][1:] = self.Data['ret_close'][:-1]
        self.Data['ret_close'] = self.Data['ret_close'] / self.Data['ret_close_lag']
        np.log(self.Data['ret_close'], out=self.Data['ret_close'])
        self.Data['ret_close'] *= 1e3
        self.Data['ret_close'] = self.Data['ret_close'].reshape(-1, 242, self.Data['ret_close'].shape[1])
        self.Data['_adj_close_tmr'] = self.Data['adj_close'][-1, -1:]

        self.Data['vwap'] = np.where(self.Data['vol'] > 99, self.Data['adj_amt'] / self.Data['vol'], self.Data['opn'])
        self.Data['ret_vwap'] = np.empty_like(self.Data['vwap'])
        self.Data['ret_vwap'][:, 0] = self.Data['ret_close'][:, 0]
        self.Data['ret_vwap'][:, 1:] = np.log(self.Data['vwap'][:, 1:] / self.Data['vwap'][:, :-1]) * 1e3

        multidask('调整量纲_增强合并_高频财务_基础收益', [
            [self.calc_dimension, ('num_buy',)],
            [self.calc_dimension, ('num_sell',)],
            [self.calc_dimension, ('num_total',)],
            [self.calc_dimension, ('adj_amt',)],
            [self.calc_dimension, ('adj_vol',)],
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

        multidask('计算增强收益', [
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

        multidask('计算增强换手', [
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

        multidask('基础因子异常值处理', [[self.calc_clip_arr, (x,)] for x in MaterialList])

        multidask('存储基础材料', [[self.calc_f1_arr, (x,)] for x in MaterialList])

        self.reduce = ReduceMaterial()
        multidask('存储降采样材料', [[self.calc_desample_f1_arr, (x,)] for x in MaterialList])

        print('总用时秒数：', time.time() - t)
        del self.Data
        gc.collect()

    def calc_min_data(self, name_in, name_out):
        self.Data[name_out] = get_minute_data(name_in, self.date_list, self.code_list)

    def calc_dev_add(self, name1_in, name2_in, name_out):
        self.Data[name_out] = self.Data[name1_in] + self.Data[name2_in]

    def calc_fin_ratio(self, name_in, name_out):
        self.Data[name_out] = self.Data[name_in] / self.Data['close']

    def calc_base_ret(self, name1_in, name2_in, name_out):
        self.Data[name_out] = np.log(self.Data[name1_in] / self.Data[name2_in]) * 1e3

    def calc_dimension(self, name_in):
        if name_in in ['num_buy', 'num_sell', 'num_total']:
            self.Data[name_in] *= 1e-2
        if name_in in ['adj_amt', 'adj_vol']:
            self.Data[name_in] *= 1e-4

    def calc_dev_ret(self, name_in, name_out):
        self.Data[name_in + 'amt'] /= self.Data[name_in + 'vol']
        self.Data[name_in + 'amt'] /= self.Data['vwap']
        self.Data[name_in + 'amt'][~ (self.Data[name_in + 'vol'] > 99)] = 1
        np.log(self.Data[name_in + 'amt'], out=self.Data[name_in + 'amt'])
        self.Data[name_in + 'amt'] *= 1e3
        self.Data[name_out] = self.Data[name_in + 'amt']
        del self.Data[name_in + 'amt']

    def calc_dev_turn(self, name_in, name_out):
        self.Data[name_in + 'vol'] /= self.Data['_free_float_shares']
        self.Data[name_out] = self.Data[name_in + 'vol']
        del self.Data[name_in + 'vol']

    def calc_dev_turn_acc(self, name_in, name_out):
        self.Data[name_in] /= self.Data['vwap']
        self.Data[name_in] /= self.Data['_free_float_shares']
        self.Data[name_out] = self.Data[name_in]
        del self.Data[name_in]

    def calc_clip_arr(self, name_in):
        max_val = MaterialDistAdjust[name_in][0]
        min_val = MaterialDistAdjust[name_in][1]
        np.clip(self.Data[name_in], min_val, max_val, self.Data[name_in])

    def calc_f1_arr(self, name_in):
        self.Data[name_in] = np.ascontiguousarray(self.Data[name_in], dtype='float32')
        store_augmented_matrix(self.Data[name_in], f'{self.root_path}/Material/{name_in}.npy',
                               axis=2, length=6000, offset_days=self.date_offset)

    def calc_desample_f1_arr(self, name_in):
        self.Data[name_in] = getattr(self.reduce, DesampleMethod[name_in])(self.Data[name_in])
        store_augmented_matrix(self.Data[name_in], f'{self.root_path}/ReduceMaterial/{name_in}.npy',
                               axis=2, length=6000, offset_days=self.date_offset)


if __name__ == '__main__':
    for year in [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021]:
    # for year in [2020, 2021]:
        start = year * 10000 + 101
        end = year * 10000 + (1231 if year < 2021 else 901)
        mk = MakeMaterial(start, end)
        del mk
        gc.collect()
