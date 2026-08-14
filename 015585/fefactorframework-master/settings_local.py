# this file contains base path settings for fefactor framework

import os
from enum import Enum, unique

@unique
class RunMode(Enum):
    research = 0,
    remote_deploy = 1,
    prod_prepare = 2,

# TODO 更新路径
BASE_DIR = "/data/user/015585/01-因子挖掘/999-share/for system/20230911 因子平台化-数据样例"
Saturn_BASE_DIR = os.path.join(BASE_DIR, "Saturn&Sell")
Sell_BASE_DIR = os.path.join(BASE_DIR, "Saturn&Sell")
Jupiter_BASE_DIR = os.path.join(BASE_DIR, "Jupiter&Europa")
Europa_BASE_DIR = os.path.join(BASE_DIR, "Jupiter&Europa")

# Saturn/sell related data
Saturn_TTransaction_dir = os.path.join(Saturn_BASE_DIR, "TTransaction")
Saturn_T1mTransaction_dir = os.path.join(Saturn_BASE_DIR, "T1mTransaction")
# Saturn_T10mTransaction_dir = os.path.join(Saturn_BASE_DIR, "T10mTransaction")
Saturn_TTransaction_cs_dir = os.path.join(Saturn_BASE_DIR, "TTransaction_cs")
Saturn_T1mTransaction_cs_dir = os.path.join(Saturn_BASE_DIR, "T1mTransaction_cs")
Saturn_TTickab_dir = os.path.join(Saturn_BASE_DIR, "TTickab")
Saturn_T1mTickab_dir = os.path.join(Saturn_BASE_DIR, "T1mTickab")
Saturn_T1mTickab_cs_dir = os.path.join(Saturn_BASE_DIR, "T1mTickab_cs")
Saturn_TTickab_cs_dir = os.path.join(Saturn_BASE_DIR, "TTickab_cs")
Saturn_TOrder_dir = os.path.join(Saturn_BASE_DIR, "TOrder")
Saturn_T1mOrder_dir = os.path.join(Saturn_BASE_DIR, "T1mOrder")
Saturn_TOrder_cs_dir = os.path.join(Saturn_BASE_DIR, "TOrder_cs")
Saturn_T1mOrder_cs_dir = os.path.join(Saturn_BASE_DIR, "T1mOrder_cs")
Saturn_LastTouchTick_dir = os.path.join(Saturn_BASE_DIR, "LastTouchTick")
Saturn_LastTouchTick_cs_dir = os.path.join(Saturn_BASE_DIR, "LastTouchTick_cs")
Saturn_LastTouchTrans_dir = os.path.join(Saturn_BASE_DIR, "LastTouchTrans")
Saturn_LastTouchTrans_cs_dir = os.path.join(Saturn_BASE_DIR, "LastTouchTrans_cs")
Saturn_LastTouchOrder_dir = os.path.join(Saturn_BASE_DIR, "LastTouchOrder")
Saturn_LastTouchOrder_cs_dir = os.path.join(Saturn_BASE_DIR, "LastTouchOrder_cs")
Saturn_basic_dir = "/data/user/015585/01-因子挖掘/999-share/for system/20230911 因子平台化-数据样例/basic文件样例/basic_df_saturn&sell.pkl"

# sell related data
Sell_TTransaction_dir = os.path.join(Sell_BASE_DIR, "TTransaction")
Sell_T1mTransaction_dir = os.path.join(Sell_BASE_DIR, "T1mTransaction")
Sell_TTransaction_cs_dir = os.path.join(Sell_BASE_DIR, "TTransaction_cs")
Sell_T1mTransaction_cs_dir = os.path.join(Sell_BASE_DIR, "T1mTransaction_cs")
Sell_TTickab_dir = os.path.join(Sell_BASE_DIR, "TTickab")
Sell_T1mTickab_dir = os.path.join(Sell_BASE_DIR, "T1mTickab")
Sell_T1mTickab_cs_dir = os.path.join(Sell_BASE_DIR, "T1mTickab_cs")
Sell_TTickab_cs_dir = os.path.join(Sell_BASE_DIR, "TTickab_cs")
Sell_TOrder_dir = os.path.join(Sell_BASE_DIR, "TOrder")
Sell_T1mOrder_dir = os.path.join(Sell_BASE_DIR, "T1mOrder")
Sell_TOrder_cs_dir = os.path.join(Sell_BASE_DIR, "TOrder_cs")
Sell_T1mOrder_cs_dir = os.path.join(Sell_BASE_DIR, "T1mOrder_cs")
Sell_LastTouchTick_dir = os.path.join(Sell_BASE_DIR, "LastTouchTick")
Sell_LastTouchTick_cs_dir = os.path.join(Sell_BASE_DIR, "LastTouchTick_cs")
Sell_LastTouchTrans_dir = os.path.join(Sell_BASE_DIR, "LastTouchTrans")
Sell_LastTouchTrans_cs_dir = os.path.join(Sell_BASE_DIR, "LastTouchTrans_cs")
Sell_LastTouchOrder_dir = os.path.join(Sell_BASE_DIR, "LastTouchOrder")
Sell_LastTouchOrder_cs_dir = os.path.join(Sell_BASE_DIR, "LastTouchOrder_cs")
Sell_basic_dir = "/data/user/015585/01-因子挖掘/999-share/for system/20230911 因子平台化-数据样例/basic文件样例/basic_df_saturn&sell.pkl"

# Jupiter related data
Jupiter_TTransaction_dir = os.path.join(Jupiter_BASE_DIR, "TTransaction")
Jupiter_TOrder_dir = os.path.join(Jupiter_BASE_DIR, "TOrder")
Jupiter_TTickab_dir = os.path.join(Jupiter_BASE_DIR, "TTickab")
Jupiter_LastTouchTTick_dir = os.path.join(Jupiter_BASE_DIR, "LastTouchTTick")
Jupiter_MarketTTick_dir = os.path.join(Jupiter_BASE_DIR, "MarketTTick")
Jupiter_Market1TTick_dir = os.path.join(Jupiter_BASE_DIR, "Market1TTick")
Jupiter_MarketIndTTick_dir = os.path.join(Jupiter_BASE_DIR, "MarketIndTTick")
Jupiter_basic_dir = "/data/user/015585/01-因子挖掘/999-share/for system/20230911 因子平台化-数据样例/basic文件样例/basic_df_europa&jupiter.pkl"

# Europa related data
Europa_TTransaction_dir = os.path.join(Europa_BASE_DIR, "TTransaction")
Europa_TOrder_dir = os.path.join(Europa_BASE_DIR, "TOrder")
Europa_TTickab_dir = os.path.join(Europa_BASE_DIR, "TTickab")
Europa_LastTouchTTick_dir = os.path.join(Europa_BASE_DIR, "LastTouchTTick")
Europa_MarketTTick_dir = os.path.join(Europa_BASE_DIR, "MarketTTick")
Europa_Market1TTick_dir = os.path.join(Europa_BASE_DIR, "Market1TTick")
Europa_MarketIndTTick_dir = os.path.join(Europa_BASE_DIR, "MarketIndTTick")
Europa_basic_dir = "/data/user/015585/01-因子挖掘/999-share/for system/20230911 因子平台化-数据样例/basic文件样例/basic_df_europa&jupiter.pkl"

path_dict = {
    "saturn": {
        "TTransaction": Saturn_TTransaction_dir,
        "T1mTransaction": Saturn_T1mTransaction_dir,
        "TTransaction_cs": Saturn_TTransaction_cs_dir,
        "T1mTransaction_cs": Saturn_T1mTransaction_cs_dir,
        "TTickab": Saturn_TTickab_dir,
        "T1mTickab": Saturn_T1mTickab_dir,
        "T1mTickab_cs": Saturn_T1mTickab_cs_dir,
        "TTickab_cs": Saturn_TTickab_cs_dir,
        "TOrder": Saturn_TOrder_dir,
        "T1mOrder": Saturn_T1mOrder_dir,
        "TOrder_cs": Saturn_TOrder_cs_dir,
        "T1mOrder_cs": Saturn_T1mOrder_cs_dir,
        "LastTouchTick": Saturn_LastTouchTick_dir,
        "LastTouchTick_cs": Saturn_LastTouchTick_cs_dir,
        "LastTouchTrans": Saturn_LastTouchTrans_dir,
        "LastTouchTrans_cs": Saturn_LastTouchTrans_cs_dir,
        "LastTouchOrder": Saturn_LastTouchOrder_dir,
        "LastTouchOrder_cs": Saturn_LastTouchOrder_cs_dir,
        "Basic": Saturn_basic_dir
    },
    "sell": {
        "TTransaction": Sell_TTransaction_dir,
        "T1mTransaction": Sell_T1mTransaction_dir,
        "TTransaction_cs": Sell_TTransaction_cs_dir,
        "T1mTransaction_cs": Sell_T1mTransaction_cs_dir,
        "TTickab": Sell_TTickab_dir,
        "T1mTickab": Sell_T1mTickab_dir,
        "T1mTickab_cs": Sell_T1mTickab_cs_dir,
        "TTickab_cs": Sell_TTickab_cs_dir,
        "TOrder": Sell_TOrder_dir,
        "T1mOrder": Sell_T1mOrder_dir,
        "TOrder_cs": Sell_TOrder_cs_dir,
        "T1mOrder_cs": Sell_T1mOrder_cs_dir,
        "LastTouchTick": Sell_LastTouchTick_dir,
        "LastTouchTick_cs": Sell_LastTouchTick_cs_dir,
        "LastTouchTrans": Sell_LastTouchTrans_dir,
        "LastTouchTrans_cs": Sell_LastTouchTrans_cs_dir,
        "LastTouchOrder": Sell_LastTouchOrder_dir,
        "LastTouchOrder_cs": Sell_LastTouchOrder_cs_dir,
        "Basic": Sell_basic_dir
    },
    "jupiter": {
        "TTransaction": Jupiter_TTransaction_dir,
        "TOrder": Jupiter_TOrder_dir,
        "TTickab": Jupiter_TTickab_dir,
        "LastTouchTTick": Jupiter_LastTouchTTick_dir,
        "MarketTTick": Jupiter_MarketTTick_dir,
        "Market1TTick": Jupiter_Market1TTick_dir,
        "MarketIndTTick": Jupiter_MarketIndTTick_dir,
        "Basic": Jupiter_basic_dir
    },
    "europa": {
        "TTransaction": Europa_TTransaction_dir,
        "TOrder": Europa_TOrder_dir,
        "TTickab": Europa_TTickab_dir,
        "LastTouchTTick": Europa_LastTouchTTick_dir,
        "MarketTTick": Europa_MarketTTick_dir,
        "Market1TTick": Europa_Market1TTick_dir,
        "MarketIndTTick": Europa_MarketIndTTick_dir,
        "Basic": Europa_basic_dir
    },
}

