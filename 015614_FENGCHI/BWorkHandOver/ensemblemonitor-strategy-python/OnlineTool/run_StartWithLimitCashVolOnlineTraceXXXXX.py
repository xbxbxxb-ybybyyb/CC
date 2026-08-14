# @Time : 2020/12/16 21:24
# @Author : Zhichen Lu
# @File : run_StartWithLimitCash.py
import sys, datetime

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from StrongStockModel.conf.path_config import deal_price_path
from StrongStockModel.backtest.StrategyBackTest.DerivativeStrategy.StartWithLimitCashVolConsiderChangingCash import StartWithLimitCashVolConsiderChangingCash, \
    InitailCashBasedEvaluationHelper
from StrongStockModel.model.ModelResultLoadingTool import get_signal_by_val_pct_threshold_integration
import pandas as pd
from dataApi.tradeDate import get_date_range, get_pre_trade_date
import configparser, os
from online_conf import code_list_path, local_config_path
from Script.lzc.pitches_integration import model_list, out_signal
from dataApi.getData import trans_windcode2int
from OnlineTool.daily_statOnline import main_compare



today = 20210629#int(datetime.date.today().strftime('%Y%m%d'))

main_compare(today)



