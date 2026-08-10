import sys
sys.path.insert(4, 'C:\\Users\\harlighet\\AppData\\Roaming\\Universe')

import multifactor.IO.IO as IO
from multifactor.IO.IO_enums import *
import multifactor.IO.naming_config as nc
import multifactor.utility.dt as tdt
import multifactor.utility.common as ut
import math
import pandas as pd
import numpy as np
import datetime
import logging
import os


def get_trading_day_offset_helper(x, days):
    try:
        return tdt.get_trading_day_offset(x, days)[0]
    except:
        return x


class HS300IndexRebalancer:
    def __init__(self, rebalance_year, rebalance_month, output_path='.'):
        self.rebalance_year = rebalance_year
        assert rebalance_month in [6, 12]
        self.rebalance_month = rebalance_month
        self.index_name = 'HS300'
        if rebalance_month == 6:
            self.inspect_start_date = pd.Timestamp(self.rebalance_year - 1, 5, 1)
            self.inspect_end_date = pd.Timestamp(self.rebalance_year, 4, 30)
            self.suspend_deadline = pd.Timestamp(self.rebalance_year, 1, 30)
            self.financial_ref_date = pd.Timestamp(self.rebalance_year - 1, 12, 31)
        else:
            self.inspect_start_date = pd.Timestamp(self.rebalance_year - 1, 11, 1)
            self.inspect_end_date = pd.Timestamp(self.rebalance_year, 10, 31)
            self.suspend_deadline = pd.Timestamp(self.rebalance_year, 7, 31)
            self.financial_ref_date = pd.Timestamp(self.rebalance_year, 6, 30)
        if not os.path.exists(output_path):
            os.path.makedirs(output_path)
        self.output_path = os.path.join(output_path, '_'.join(['HS300_rebalance',
                                        str(self.rebalance_year), str(self.rebalance_month)]) + '.csv')
        self.logger = ut.add_file_logger('HS300', level=logging.INFO, mode='a',
                         file_name=os.path.join(output_path, 'HS300_rebalance.log'))
        self.logger.info('*' * 60)
        self.logger.info('Rebalance Period: %d - %d' % (self.rebalance_year, self.rebalance_month))
        self.base_data = None
        self.sampled_base_data = dict()
        self.sample_space = None
        self.prev_index_stock_list = None
        self.candidate_list = None
        self.final_list = None
        self.entry_list = None
        self.exit_list = None

    def retrieve_data(self):
        # retrieve previous index stock list
        ref_date = tdt.get_trading_day_offset(self.inspect_end_date, 0)[0]
        data = IO.read_data(ref_date, columns=nc.universe_mapper[self.index_name],
                            ftype=FType.UNIV, dsource=DSource.OPTM).rename(
                            columns=nc.reversed_universe_mapper).loc[ref_date, self.index_name]
        self.prev_index_stock_list = data.loc[data].index.tolist()
        # retrieve market data
        base_data = IO.read_data([self.inspect_start_date, self.inspect_end_date],
                                    columns=['amt', 'mkt_cap_ard', 'close'])
        base_data = ut.pd_unstack(base_data)  # unstack into dictionary
        capital_data = IO.read_data(columns=['CHANGE_DT', 'S_SHARE_TOTALA'], dtable=DTable.AShareCapitalization).reset_index()
        capital_data['CHANGE_DT'] = pd.to_datetime(capital_data['CHANGE_DT'], format='%Y%m%d')
        capital_data = capital_data.drop(columns=['dt']).rename(columns={'CHANGE_DT': 'dt'}).set_index(
                                        ['dt', 'Ticker'])['S_SHARE_TOTALA']
        base_data['S_SHARE_TOTALA'] = capital_data[~capital_data.index.duplicated()].unstack().fillna(method='pad')
        base_data['S_SHARE_TOTALA'] = base_data['S_SHARE_TOTALA'].reindex(index=base_data['close'].index,
                                                                          columns=base_data['close'].columns)
        base_data = ut.align_data(base_data, inner=False)
        for k, v in base_data.items():
            base_data[k] = v.fillna(method='pad')
        base_data['ASHARE_TOTCAP'] = base_data['close'] * base_data['S_SHARE_TOTALA']
        # filter first three days of trade information
        with pd.HDFStore(nc.listing_delisting_path, 'r') as hdf_store:
            list_date = hdf_store.SecDate.ipo_date
        shifted_list_date = list_date.apply(get_trading_day_offset_helper, args=(3,))
        _ = base_data['close']
        mask = pd.DataFrame(np.tile(_.index, (_.shape[1], 1)).T, index=_.index, columns=_.columns)
        shifted_list_date = shifted_list_date.reindex(mask.columns).fillna(pd.Timestamp.max)
        mask = mask.subtract(shifted_list_date, axis=1) >= 0
        mask = mask.replace(np.nan, False)
        suspend_mask = base_data['amt'] != 0
        is_suspended = base_data['amt'] == 0
        for k, v in base_data.items():
            base_data[k] = v[mask & suspend_mask]
        base_data['is_suspended'] = is_suspended.fillna(False)
        self.base_data = base_data

    def retrieve_start_up_filter(self):
        with pd.HDFStore(nc.listing_delisting_path, 'r') as hdf_store:
            list_date = hdf_store.SecDate.ipo_date
        list_date = list_date.loc[list_date.index.str.startswith('300')]
        shifted_list_date = list_date + pd.Timedelta('1095D')
        return shifted_list_date.loc[shifted_list_date >= self.inspect_end_date].index.unique().tolist()

    def retrieve_non_start_up_filter(self):
        with pd.HDFStore(nc.listing_delisting_path, 'r') as hdf_store:
            list_date = hdf_store.SecDate.ipo_date
        list_date = list_date.loc[~list_date.index.str.startswith('300')]
        shifted_list_date = list_date + pd.Timedelta('90D')
        hulk_list = self.base_data['ASHARE_TOTCAP'].mean().reindex(
                                    list_date.index).dropna().sort_values(ascending=True).tail(30).index
        return [item for item in shifted_list_date.loc[shifted_list_date >= self.inspect_end_date].index.unique() \
                if item not in hulk_list]

    def calc_sample_space(self):
        sample_space = self.base_data['close'].iloc[-1, :].index.tolist()
        st_filter = ut.retrieve_st_stocks(self.inspect_end_date)
        start_up_filter = self.retrieve_start_up_filter()
        non_start_up_filter = self.retrieve_non_start_up_filter()
        self.sample_space = list(set(sample_space).difference(set(st_filter)) \
                                                  .difference(set(start_up_filter)) \
                                                  .difference(set(non_start_up_filter)))
        self.logger.debug('init space:')
        self.logger.debug(sample_space)
        self.logger.debug('st filter:')
        self.logger.debug(st_filter)
        self.logger.debug('start upfilter:')
        self.logger.debug(start_up_filter)
        self.logger.debug('non start upfilter:')
        self.logger.debug(non_start_up_filter)
        self.logger.debug('sample space:')
        self.logger.debug(self.sample_space)
        for k, v in self.base_data.items():
            self.sampled_base_data[k] = v.reindex(columns=self.sample_space)

    def calc_candidate_list(self):
        amount = self.sampled_base_data['amt'].mean().dropna().sort_values(ascending=True)
        new_amount_candidates = [item for item in amount.tail(int(len(self.sample_space) * 0.5)).index \
                                 if item not in self.prev_index_stock_list]
        prev_amount_candidates = [item for item in amount.tail(int(len(self.sample_space) * 0.6)).index \
                                  if item in self.prev_index_stock_list]
        amount_candidates = new_amount_candidates + prev_amount_candidates
        market_cap = self.sampled_base_data['ASHARE_TOTCAP'].reindex(columns=amount_candidates)
        self.logger.debug('new amount candidates:')
        self.logger.debug(new_amount_candidates)
        self.logger.debug('prev amount candidates:')
        self.logger.debug(prev_amount_candidates)
        self.candidate_list = market_cap.mean().sort_values(ascending=False).index.tolist()

    def retrieve_illegal_filter(self):
        illegal = IO.read_data([self.inspect_start_date, self.inspect_end_date], dtable=DTable.AShareIllegality)
        illegal = illegal[illegal.PROCESSOR.str.contains('中国证券监督管理委员会')]
        illegal = illegal[illegal.RELATION_TYPE == 458001000]
        illegal = illegal[illegal.ILLEG_TYPE.str.contains('未及时披露公司重大事项') |
                          illegal.ILLEG_TYPE.str.contains('信息披露虚假或严重误导性陈述')]
        illegal = illegal[illegal.DISPOSAL_TYPE.str.contains('处罚')]
        return illegal.index.get_level_values(level=1).unique().tolist()

    def retrieve_negative_profit_filter(self):
        income = IO.read_data(self.financial_ref_date, columns=['STATEMENT_TYPE', 'NET_PROFIT_AFTER_DED_NR_LP'],
                              dtable=DTable.AShareIncome)
        income = income[income.STATEMENT_TYPE == 408001000].loc[self.financial_ref_date, 'NET_PROFIT_AFTER_DED_NR_LP'].dropna()
        return income[income < 0].index.unique().tolist()

    def retrieve_suspension_filter(self):
        def suspension_helper(x):
            _ = x.loc[x >= 25].index
            if len(_) > 0:
                return _[-1]
            else:
                return np.nan
        prev_candidate_list = [item for item in self.candidate_list if item in self.prev_index_stock_list]
        new_candidate_list = [item for item in self.candidate_list if item not in self.prev_index_stock_list]
        # deal with previous index stocks
        sliced = self.sampled_base_data['is_suspended'].reindex(columns=prev_candidate_list).astype('int')
        prev_suspend_days = sliced.apply(ut.continuous_groupby, axis=0, method='cumsum')
        prev_last_flagged_date = prev_suspend_days.apply(suspension_helper).dropna()
        prev_suspension_filter = prev_last_flagged_date.loc[prev_last_flagged_date == sliced.index[-1]].index.tolist()
        # deal with new stocks
        ref_date = self.inspect_end_date - pd.Timedelta('90D')
        sliced = self.sampled_base_data['is_suspended'].reindex(columns=new_candidate_list).astype('int')
        new_suspend_days = sliced.apply(ut.continuous_groupby, axis=0, method='cumsum')
        new_last_flagged_date = new_suspend_days.apply(suspension_helper).dropna()
        new_suspension_filter = new_last_flagged_date.loc[new_last_flagged_date >= ref_date].index.tolist()
        return prev_suspension_filter, new_suspension_filter

    def run(self):
        self.retrieve_data()
        self.calc_sample_space()
        self.calc_candidate_list()
        # split candidate list into two groups
        reserved_prev_candidates = [item for item in self.candidate_list[:360] \
                                        if item in self.prev_index_stock_list]
        reserved_new_candidates = [item for item in self.candidate_list[:240] \
                                   if item not in self.prev_index_stock_list]
        rest_candidates = [item for item in self.candidate_list[240:] \
                           if item not in list(reserved_prev_candidates + reserved_new_candidates)]
        self.logger.debug('reserved prev candidates:')
        self.logger.debug(reserved_prev_candidates)
        self.logger.debug('reserved new candidates:')
        self.logger.debug(reserved_new_candidates)
        self.logger.debug('rest candidates:')
        self.logger.debug(rest_candidates)
        # retrieve filters
        illegal_filter = self.retrieve_illegal_filter()
        negative_profit_filter = self.retrieve_negative_profit_filter()
        prev_susp_filter, new_susp_filter = self.retrieve_suspension_filter()
        prev_filter = list()
        new_filter = list(set(illegal_filter + negative_profit_filter + new_susp_filter))
        self.logger.debug('illegal filter:')
        self.logger.debug(illegal_filter)
        self.logger.debug('negative profit filter:')
        self.logger.debug(negative_profit_filter)
        self.logger.debug('prev suspension filter:')
        self.logger.debug(prev_susp_filter)
        self.logger.debug('new suspension filter:')
        self.logger.debug(new_susp_filter)
        # apply filters seperately
        filtered_prev_candidates = [item for item in reserved_prev_candidates \
                                    if item not in prev_filter]
        filtered_new_candidates = [item for item in reserved_new_candidates \
                                   if item not in new_filter]
        # just bifurcate
        def rest_candidate_helper(candidates, cond_a, cond_b, rule):
            result = list()
            for item in candidates:
                if item in rule:
                    if item not in cond_a:
                        result.append(item)
                else:
                    if item not in cond_b:
                        result.append(item)
            return result
        filtered_rest_candidates = rest_candidate_helper(rest_candidates, prev_filter, new_filter, self.prev_index_stock_list)
        final_rank = filtered_new_candidates + filtered_prev_candidates + filtered_rest_candidates
        final_candidate_list = final_rank[:300]
        new_entry = [item for item in final_candidate_list if item not in self.prev_index_stock_list]
        if len(new_entry) > 30:
            sliced_new_entry = new_entry[:30]
            sliced_prev_entry = [item for item in final_rank if item in self.prev_index_stock_list][:270]
            self.final_list = sliced_new_entry + sliced_prev_entry
        else:
            self.final_list = final_rank[:300]
        self.entry_list = [item for item in self.final_list if item not in self.prev_index_stock_list]
        self.exit_list = [item for item in self.prev_index_stock_list if item not in self.final_list]
        # dump data
        entry_ps = pd.Series(1, index=self.entry_list)
        exit_ps = pd.Series(-1, index=self.exit_list)
        entry_ps.append(exit_ps).to_csv(self.output_path)
        # evaluate result
        self.evaluate()
        assert len(self.final_list) == 300

    def evaluate(self, ref_file='aaa.xlsx'):
        if ref_file is None:
            return
        ref_data = pd.read_excel(ref_file)
        ref_data['dt'] = pd.to_datetime(ref_data['日期'])
        ref_data['month'] = ref_data['dt'].dt.month
        ref_data['year'] = ref_data['dt'].dt.year
        sliced = ref_data[(ref_data['month'] == self.rebalance_month) & (ref_data['year'] == self.rebalance_year)]
        ref_entry_list = sliced[sliced['状态'].str.contains('纳入')]['代码'].tolist()
        ref_exit_list = sliced[sliced['状态'].str.contains('剔除')]['代码'].tolist()
        diff_entry_list = [item for item in self.entry_list if item not in ref_entry_list]
        diff_exit_list = [item for item in self.exit_list if item not in ref_exit_list]
        ref_diff_entry_list = [item for item in ref_entry_list if item not in self.entry_list]
        ref_diff_exit_list = [item for item in ref_exit_list if item not in self.exit_list]
        self.logger.info('*' * 60)
        self.logger.info('实际调整数量：%d' % len(ref_entry_list))
        self.logger.info('预测调整数量：%d' % len(self.entry_list))
        self.logger.info('*' * 60)
        self.logger.info('预计误入：%s' % diff_entry_list)
        self.logger.info('该入未入：%s' % ref_diff_entry_list)
        self.logger.info('预计误出：%s' % diff_exit_list)
        self.logger.info('该出未出：%s' % ref_diff_exit_list)



if __name__ == '__main__':
    ir = HS300IndexRebalancer(2019, 6)
    ir.run()

