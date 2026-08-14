# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

"""
*因子名 : MoneyMaker
*因子功能描述 : ep与净利润环比增长率夏普排名之和
*因子逻辑：选取优质稳定赚钱的公司
*作者 : 沈天琦
*因子创建日期 : 2020.03.25
"""   
class MoneyMaker(BaseFactor):
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.WIND_AShareFinancialIndicator','FactorData.Basic_factor.close']
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 5
    # reform_window = 5
    financial_lag = 400

    def calc_single(self, database):

        name_eps = 'S_QFA_EPS'
        name_cgr_pg = 'S_QFA_CGRPROFIT'
        name_ann_dt = 'ANN_DT'

        close = database.depend_data['FactorData.Basic_factor.close']

        wind_data = database.depend_data['FactorData.WIND_AShareFinancialIndicator'][[name_eps,name_cgr_pg,name_ann_dt]]
        
        eps = wind_data[name_eps].unstack().fillna(method='ffill')
        eps = eps.reindex(columns=close.columns)
        cgr_pg = wind_data[name_cgr_pg].unstack().fillna(method='ffill')
        cgr_pg = cgr_pg.reindex(columns=close.columns)
        ann_dt = wind_data[name_ann_dt].unstack().fillna(method='ffill')
        ann_dt = ann_dt.reindex(columns=close.columns)

        trading_date_list = close.index.tolist()

        eps_ad = self.get_daily_df_from_quarter_field(ann_dt,eps,trading_date_list)

        ep = (eps_ad / close).mean(axis=0)
        cgr_pg_sharpe = cgr_pg.iloc[-4:].mean() / cgr_pg.iloc[-4:].std()


        result = ep.rank() + cgr_pg_sharpe.rank()

        return result       


    def get_daily_df_from_quarter_field(self, stm_issuingdate, df_quarter, trading_date_list):
        stm_issuingdate = stm_issuingdate.astype(float).values
        daily_array = np.nan * np.ones((len(trading_date_list), len(df_quarter.columns)))
        for idx, date in enumerate(trading_date_list):
            daily_array[idx] = pd.DataFrame(np.where(stm_issuingdate <= int(date), df_quarter, np.nan)).fillna(
                method='ffill').iloc[-1].values
        return pd.DataFrame(daily_array, index=trading_date_list, columns=df_quarter.columns)
