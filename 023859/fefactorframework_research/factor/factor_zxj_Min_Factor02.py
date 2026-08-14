import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

class factor_zxj_Min_Factor02(BaseFactor):
    strategy_name = "neptune"
    factor_name = "zxj_Min_Factor02"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "zxj"
    factor_explain = "vol(ori) * bid_ask_spread / order_book_depth"
    zcz_adjusted = "否"
    logic_type = ""
    low_cost = ""
    t_day_data = []

    ROLLING_WINDOW = 20

    xdb_data = [
        {
        'name': 'xdb_tick1m',
        'lag': 3,
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database

        def f_calc_rolling_std(series):
            return np.std(series[~np.isnan(series)], ddof=1)

        df_minute = database['xdb_tick1m'].copy()

        df_minute['mid_price'] = (df_minute['Sell1Price'] + df_minute['Buy1Price']) / 2
        df_minute['relative_spread'] = (df_minute['Sell1Price'] - df_minute['Buy1Price']) / df_minute['mid_price']
        df_minute['total_depth_l1'] = df_minute['Buy1OrderQty'] + df_minute['Sell1OrderQty']
        df_minute['ofi_ratio'] = (df_minute['TotalBidQty'] - df_minute['TotalOfferQty']) / (df_minute['TotalBidQty'] + df_minute['TotalOfferQty'])

        df_minute.replace([np.inf, -np.inf], np.nan, inplace=True)

        tech_result = df_minute.groupby(['dt', 'Ticker']).agg(
            avg_bid_ask_spread=('relative_spread', 'mean'),
            order_book_depth=('total_depth_l1', 'mean'),
            order_flow_imbalance=('ofi_ratio', 'mean')
        )
        
        min_periods = int(self.ROLLING_WINDOW / 2)
        
        ofi_volatility_raw = tech_result.groupby(level='Ticker')['order_flow_imbalance'] \
                                        .rolling(window=self.ROLLING_WINDOW, min_periods=min_periods) \
                                        .apply(f_calc_rolling_std, raw=True)

        ofi_volatility = ofi_volatility_raw.reset_index(level=0, drop=True)
        
        tech_result['order_book_depth'].replace(0, np.nan, inplace=True)
        market_fragility = (ofi_volatility * tech_result['avg_bid_ask_spread']) / tech_result['order_book_depth']

        market_fragility.replace([np.inf, -np.inf], np.nan, inplace=True)

        res = market_fragility.to_frame(name=self.factor_name)
        
        database['pre_T_N'] = res
        return database

    def prepare_T_data(self, database):
        # 如果加载数据阶段出现某些T日高频数据或者xdb数据缺失，则跳过该日计算
        if database["skip"] == True:
            return database
        else:
            return database

    def calculate(self, database):
        if database["skip"] == True:  # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return pd.Series({self.factor_name: np.nan})
        else:
            res = database['pre_T_N'][self.factor_name].values[0]
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)