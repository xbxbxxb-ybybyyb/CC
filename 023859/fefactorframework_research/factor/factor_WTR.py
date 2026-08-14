import numpy as np
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
from xfactor.BaseFactor import BaseFactor
from xfactor.FactorDataPrepareUtil import *

# 财务CS
class factor_WTR(BaseFactor):
    strategy_name = "neptune"
    factor_name = "WTR"
    fill_na_value = 1
    need_pre_calculate_T_N = True
    owner = "wenj"  # 开发人员姓名
    factor_explain = "过去3个月分析师预测目标价与预测时前收盘价的比值的均值" # 因子逻辑解释
    zcz_adjusted = "" # 是否针对注册制调整：是/否
    logic_type = "" # 逻辑类别
    low_cost = "" # 是否低耗时

    xdb_data = [{
        'name':'xdb_reporttargetpriceadj_cs',
        'lag':110
    }]

    def pre_calculate_T_N_data(self, database):
        if database["skip"] == True: # 纯h5文件的T-1_Factor保留这一段，但不产生影响
            return database
        else:
            data = database['xdb_reporttargetpriceadj_cs']
            # -------------------------------------------------------------------------------------------------------------------
            # 因子逻辑部分
            data['target_price'] = np.where(
            ( ~data['CURRENTTARGETPRICE'].isna() ) ,
            data['CURRENTTARGETPRICE'],
            np.where(
                ~data['PREVIOUSTARGETPRICE'].isna(),
                data['PREVIOUSTARGETPRICE'],
                data['CURRENTPRICE']
                ) 
            )
            tick_list = data.index.get_level_values(1).unique()
            dt = data.index.get_level_values(0)[0]
            st = (dt + relativedelta(months=-3)).strftime('%Y%m%d')
            
            tmp = data[data['MDDate'] >= st]
            tmp = tmp.drop_duplicates(subset=['MDDate', 'REPORTID'], keep='first')

            res = (tmp['target_price'] / tmp['CURRENTPRICE']).groupby('Ticker',group_keys=False).mean()
            res = res.reindex(tick_list).fillna(1)
            res = res.to_frame(self.factor_name) 
            res = pd.concat({dt:res}, names=['dt'])
            # -------------------------------------------------------------------------------------------------------------------
            database['pre_T_N'] = res[[self.factor_name]] # cs要返回df
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
            res = database['pre_T_N']
            # ---------------------------------------------------------------------------------------------------------------
            return res