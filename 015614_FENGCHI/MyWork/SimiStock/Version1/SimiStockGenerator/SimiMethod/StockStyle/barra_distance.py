# coding: utf-8
# Author：fengchi863
# Date ：2022/3/24 14:23

"""
储存barra因子距离数据
"""

from SimiStock.Version1.DataPrepare.BarraFactor import BarraFactor
from SimiStock.Version1.SimiStockGenerator.util import util
from SimiStock.Version1.config.path_config import *
import pandas as pd
import numpy as np
from tqdm import tqdm
from SimiStock.dataApi import tradeDate, getData


class StyleSelection:
    def __init__(self, start_date=20180101, end_date=20211231, concept='SW1', method_name=None):
        block_data = pd.read_pickle(data_path + 'block_data.pkl')
        rong_df = pd.read_pickle(data_path + '2rong.pkl')
        clean_stock = pd.read_pickle(data_path + 'clean_stock.pkl')
        shift_start_date = tradeDate.get_pre_trade_date(start_date, 260)
        shift_end_date = tradeDate.get_pre_trade_date(end_date, -120)
        date_list = tradeDate.get_date_range(start_date, end_date)
        shift_date_list = tradeDate.get_date_range(shift_start_date, shift_end_date)

        self.date_list = date_list
        self.shift_date_list = shift_date_list

        code_list = np.load(barra_path + 'code_list.npy')
        self.code_list = list(code_list)

        self.block_data = block_data.query(f'{start_date} <= 交易日期 <= {end_date}')
        self.rong_df = rong_df
        concept_df = self.get_concept_df(concept=concept)
        self.concept_df = concept_df
        self.clean_stock = clean_stock
        self.ss = BarraFactor()  # barra数据接口

        self.method_name = method_name

    def get_concept_df(self, concept='SW1'):
        if concept in ['SW1', 'SW2', 'SW3', 'CITICS1', 'CITICS2', 'CITICS3']:
            df = getData.get_daily_1factor(concept, date_list=self.date_list)
            return df
        elif concept is 'allMarket':
            df = getData.get_daily_1factor('SW1', date_list=self.date_list)
            df[~np.isnan(df)] = 1
            return df
        else:
            raise Exception('concept is not given correctly')

    def get_concept_list(self, stk_id, trade_date):
        row = self.concept_df.loc[trade_date]
        ind_code = row[stk_id]
        stk_list = row[row == ind_code].index.tolist()
        rong_row = self.rong_df.loc[trade_date]
        rong_list = rong_row[rong_row == 1].index.tolist()
        stk_list = list(set(stk_list).intersection(set(rong_list)))
        clean_row = self.clean_stock.loc[trade_date]
        clean_list = clean_row[clean_row == 1].index.tolist()
        stk_list = list(set(stk_list).intersection(set(clean_list)))
        # 临时取出来为了获取1次数据，但大宗票不一定是两融票
        if stk_id not in stk_list:
            stk_list.append(stk_id)
        return stk_list

    def calc_distance(self, factor_list, stk_id, trade_date):
        barra = self.ss.get_factors(factor_list, trade_date)
        stk_factor = barra[stk_id]
        distance = abs(barra.values - stk_factor.values)
        ret = [trade_date, stk_id]
        ret.extend(distance.tolist()[0])
        return ret

    def calc_distances(self, stk_date_list, factor_list):
        ret_list = list()
        pbar = tqdm(range(len(stk_date_list)))
        for idx in pbar:
            stk_id, trade_date = stk_date_list[idx]
            pbar.set_description('并行生成中|%s|%s' % (int(stk_id), int(trade_date)))
            hedge = self.calc_distance(factor_list, stk_id, trade_date)
            ret_list.append(hedge)
        return ret_list

    def get_values(self, factor_list, mode='serial', kernal_num=10):
        ret_list = []
        if mode is 'serial':
            pbar = tqdm(range(len(self.block_data)))
            for idx in pbar:
                row = self.block_data.iloc[idx]
                stk_id = row['股票代码']
                trade_date = row['交易日期']
                pbar.set_description('串行生成中|%s|%s' % (int(stk_id), int(trade_date)))
                ret_list.append(self.calc_distance(factor_list, stk_id, trade_date))

        if mode is 'multi':
            stk_date_list = list(zip(self.block_data['股票代码'].tolist(), self.block_data['交易日期'].tolist()))
            ret_dict = util.multiprocess(kernal_num, self.calc_distances, stk_date_list, factor_list)

            ret_result = dict()
            for k in ret_dict:
                try:
                    ret_result[k] = ret_dict[k].get()
                except:
                    print('这个记录没有')

            for k in ret_result:
                ret_list.extend(ret_result[k])

        return ret_list


if __name__ == '__main__':
    ss = StyleSelection(start_date=20180101, end_date=20200630, concept='SW1', method_name=['市值'])
    factor_list = ['LNCAP', 'DASTD']
    # factor_list = ['MIDCAP',
    #      'BETA', 'HSIGMA', 'CMRA',
    #      'STOM', 'STOQ', 'STOQ', 'STOA', 'ATVR',
    #      'STREV', 'SEASON', 'INDMOM', 'HA',
    #      'MLEV', 'BLEV', 'DTOA', 'VSAL', 'VERN', 'VFLO', 'ETOPF_STD', 'ABS', 'ACF', 'ATO', 'GP','GPM', 'AGRO','IGRO','CXGRO',
    #      'BTOP','TETOP','APETP','CETOP','EM','LTRSTR','LTHALPHA',
    #      'PG3Y','EGRO','SGRO',
    #      'RRIBS','EARNC','EPIBSC']
    for factor in factor_list:
        ret_list = ss.get_values(factor_list=[factor], mode='serial')
        ret_df = pd.DataFrame(ret_list)
        ret_df.columns = ['trade_date', 'stk_id'] + ss.code_list
        ret_df = ret_df.set_index(['trade_date', 'stk_id'])
        util.save_df2pkl(ret_df, factor_path, f'{factor}.pkl')


