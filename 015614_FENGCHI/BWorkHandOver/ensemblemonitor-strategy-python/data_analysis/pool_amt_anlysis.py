# @Time : 2022/5/30 16:23
# @Author : Zhichen Lu
# @File : pool_amt_anlysis.py
import pandas as pd
from ExtraTools import get_nonfix_in_val
from dataApi.getData import get_daily_1factor,trans_windcode2int
from dataApi.tradeDate import get_date_range,get_pre_trade_date
from online_conf import local_config_path

amt = get_daily_1factor('amt',date_list=get_date_range(get_pre_trade_date(20220529,20),20220529))
amt = amt.rolling(5).mean()
code_list = get_nonfix_in_val('code_list',20220530,local_config_path)
code_list = [trans_windcode2int(x) for x in code_list]
amt.iloc[-1].rank(pct=True).loc[code_list].median()
today = 20220530
order_info = pd.read_excel( f'/data/user/015664/AFuckingTrigger/实盘/{today}/成交明细及收盘持仓情况{today}.xlsx')
buy_list = order_info[order_info['类型']=='当日买入']['证券代码'].apply(trans_windcode2int).tolist()
amt.iloc[-1].rank(pct=True).loc[buy_list].median()
