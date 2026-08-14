# T+h5
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数

class factor_qyh_newmetis_20240201_2(BaseFactor):
    strategy_name = "metis"
    factor_name = "qyh_newmetis_20240201_2"
    fill_na_value = 0
    need_pre_calculate_T_N = False # 纯T日数据不需要pre_T_N
    owner = "qyh"  # 开发人员姓名
    factor_explain = "买均和成交价差对应涨跌幅的min，再除以最近5日的收盘均值" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "价格波动" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ["TTickab_MetisAll"]
    t_1_factor_data = [
        {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 10, #注意为正数
         'column': ['close']
    }]
    t_1_factor_data_types = ['MD'] # 用了t_1_factor_data，types一定不能省略
    #
    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        else:
            df_ori = database['MD_CHINA_STOCK_DAILY_WIND'] # 和上面t-1_factor_data的name一致
            res = df_ori['close'].unstack().rolling(5,1).mean().iloc[[-1]].stack().replace(0,np.nan).to_frame(name='res')
            database["pre_T_N"] = res
            return database
    def prepare_T_data(self, database):
        if database["skip"] == True:
            return database
        else:
            tick_df = database['TTickab_MetisAll']
            tick_df = filter_930(tick_df)
            database['TTickab_MetisAll'] = tick_df
            dt, ticker = tick_df.index[0]
            database['ticker'] = ticker
        return database

    def calculate(self, database):
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            EPS = 1e-9
            tick_df = database['TTickab_MetisAll']
            if tick_df.shape[0] > 0:
                xx = tick_df['pre_close']
                yy = tick_df['WeightedAvgBidPx'] - tick_df['LastPx']
                res = xx / (EPS+yy)
                result = res.min()
            else:
                result = 0.0
            ticker = database['ticker']
            md_data = database['pre_T_N'][['res']]
            res1 = md_data.query("Ticker == '{}'".format(ticker))['res'].values
            res1 = res1[0] if len(res1) > 0 else np.nan
            factor_dict = {self.factor_name: result / res1}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)
