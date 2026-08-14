# xdb + T
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import * # 添加公共函数
class factor_qyh_newmet_20240307_1(BaseFactor):
    strategy_name = "metis"
    factor_name = "qyh_newmet_20240307_1"
    fill_na_value = 0
    need_pre_calculate_T_N = False
    owner = "qyh"  # 开发人员姓名
    factor_explain = "T日首次接近涨停后,买1-卖1的峰度" # 因子逻辑解释
    zcz_adjusted = "是" # 是否针对注册制调整：是/否
    logic_type = "卖单强度-总量强度" # 逻辑类别
    low_cost = "是" # 是否低耗时
    #
    t_day_data = ['TTickab_MetisAll']
    xdb_data = []
    t_1_factor_data = []  # T-N factor数据，格式如上
    t_1_factor_data_types = [] # T-1的h5文件类型列表

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True:
            database['pre_T_N'] = pd.DataFrame({self.factor_name: [np.nan]})
            return database
        return database
    def prepare_T_data(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return database
        else:
            tick_df = database['TTickab_MetisAll']
            dt, ticker = tick_df.index[0]
            dt = dt.strftime('%Y%m%d')
            zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
            database['TTickab_MetisAll'] = filter_930(database['TTickab_MetisAll'])
            database['zcz'] = zcz
            return database
    def calculate(self, database):
        # 覆写时需要写(如果加载数据阶段出现某些日频率数据或者xdb数据缺失，则跳过该日计算)：
        if database["skip"] == True:
            return pd.Series({self.factor_name: np.nan})
        else:
            tick_df = database['TTickab_MetisAll']
            t_fzt = tick_df[tick_df['LastPx'] >= round_(tick_df['LastPx'].max(), 2)]['MDTime'].min()  # 首次逼近涨停时间
            tick_df = tick_df[tick_df['MDTime'] >= t_fzt]
            #
            tick_df['factor'] = (tick_df['Buy1Price'] - tick_df['Sell1Price'])/(tick_df['pre_close'])
            zcz = database['zcz']
            if zcz:
                tick_df['factor'] = tick_df['factor']/2
            res = tick_df['factor'].kurt()
            factor_dict = {self.factor_name: res}
            # ---------------------------------------------------------------------------------------------------------------
            return pd.Series(factor_dict)

