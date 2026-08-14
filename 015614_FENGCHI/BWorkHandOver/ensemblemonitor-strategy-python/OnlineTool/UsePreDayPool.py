# @Time : 2021/11/26 8:36
# @Author : Zhichen Lu
# @File : UsePreDayPool.py
import shutil
from online_conf import code_list_path,local_config_path
from dataApi.tradeDate import get_recent_trade_date,get_pre_trade_date


recent_day = get_recent_trade_date()
next_day = get_pre_trade_date(recent_day,-1)
pre_date = get_pre_trade_date(recent_day)

print(pre_date,recent_day,next_day)

shutil.copy(f'{code_list_path}{pre_date}.pkl',f'{code_list_path}{recent_day}.pkl')
shutil.copy(f'{code_list_path}{pre_date}.pkl',f'/data/group/800319/strategy_local_path3_ForMatrix/code_list/{recent_day}.pkl')
shutil.copy(f'{local_config_path}morning_model/val_sign/{recent_day}.pkl',f'{local_config_path}morning_model/val_sign/{next_day}.pkl')

