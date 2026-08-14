#
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_met_20240307_3(BaseFactor):
    strategy_name = "metis"
    factor_name = "qyh_met_20240307_3"
    fill_na_value = 0
    need_pre_calculate_T_N = True
    owner = "qyh"  # 开发人员姓名
    factor_explain = "T日逼近涨停价后，挂卖金额之和 / 过去3天平均成交额" # 因子逻辑解释
    zcz_adjusted = "否" # 是否针对注册制调整：是/否
    logic_type = "放量角度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTickab_MetisAll']
    xdb_data = []
    t_1_factor_data = [ {'name': 'MD_CHINA_STOCK_DAILY_WIND', # 同一个因子内的name不能重复，同一批计算因子间不同表(以路径为准，与lag、column无关)不能相同名字（可以相同表叫不同名字）
         'path': '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5',
         'lag': 10, #注意为正数
         'column': ['amt']
    }]  # T-N factor数据，格式如上
    t_1_factor_data_types = ['MD'] # T-1的h5文件类型列表

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            return database
        df_ori = database['MD_CHINA_STOCK_DAILY_WIND']  # 和上面t-1_factor_data的name一致
        res = df_ori['amt'].unstack().rolling(3, 1).mean().iloc[[-1]].stack().replace(0, np.nan).to_frame(name='res')
        database["pre_T_N"] = res
        return database
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            tick_df = database['TTickab_MetisAll']
            dt,ticker = tick_df.index[0]
            database['TTickab_MetisAll'] = filter_930(tick_df)
            database['ticker'] = ticker
            return database
    def calculate(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['TTickab_MetisAll']
            ticker = database['ticker']
            md_data = database['pre_T_N'][['res']]
            res1 = md_data.query("Ticker == '{}'".format(ticker))['res'].values
            res1 = res1[0] if len(res1) > 0 else np.nan # 过去3天的amt均值
            #
            res2 = (tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']).sum()
            factor_dict = {self.factor_name: res2 / res1 if round_(res1,1) > 10 else np.nan}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

