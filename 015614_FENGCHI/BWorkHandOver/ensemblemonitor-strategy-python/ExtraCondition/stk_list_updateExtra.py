# @Time : 2021/3/1 19:44
# @Author : Zhichen Lu
# @File : stk_list_update.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/')
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
import pandas as pd
# from online_conf import code_list_path, holding_info_path, local_config_path, path_for_930
import shutil, os
from dataApi.getData import get_pre_trade_date
import datetime
from xquant.xqutils.helper import link
import ftplib
import traceback
import requests, json
from dataApi.sendInfo import send_message,send_file
from ExtraTools import get_path_conf


lm = link.LinkMessage()
date = int(datetime.date.today().strftime('%Y%m%d'))
pre_date = get_pre_trade_date(date)
account = 201001



today = int(datetime.date.today().strftime('%Y%m%d'))
path_conf = get_path_conf(f'/data/group/800319/strategy_local_path3_ForExtraSim/')
# path_conf = get_path_conf(f'/data/group/800442/800319/strategy_local_path_sim/strategy_local_path3_sim{today}/')


code_list_path, holding_info_path, local_config_path, path_for_930 =\
    [path_conf[x] for x in 'code_list_path,holding_info_path,local_config_path,path_for_930'.split(',')]

try:
    source_path = '/data/group/800442/800319/strategy_local_path/code_list_no688/'
    import time

    while True:
        if os.path.exists(f'{source_path}{pre_date}.pkl'):
            break
        else:
            send_message(['015664'], '股票池未更新')
            continue
    if os.path.exists(f'{source_path}{pre_date}.pkl'):
        if not os.path.exists(f'{code_list_path}{pre_date}.pkl'):
            shutil.copy(f'{source_path}{pre_date}.pkl', f'{code_list_path}{pre_date}.pkl')
            print('copied')
        else:
            pass
    else:
        raise Exception('No code list')

    code_list = pd.read_pickle(f'{code_list_path}{pre_date}.pkl')
    holding_info = pd.read_pickle(f'{holding_info_path}{pre_date}.pkl')
    if os.path.exists(f'{path_for_930}{pre_date}/StrategyOut/holding{pre_date}.pkl'):
        holding_930 = pd.read_pickle(f'{path_for_930}/{pre_date}/StrategyOut/holding{pre_date}.pkl')
    else:
        holding_930 = {'cash':0}
    if os.path.exists(f'{local_config_path}morning_model/val_sign_backup/{date}.pkl'):
        signal_930 = pd.read_pickle(f'{local_config_path}morning_model/val_sign_backup/{date}.pkl')
    elif os.path.exists(f'{local_config_path}morning_model/val_sign/{date}.pkl'):
        signal_930 = pd.read_pickle(f'{local_config_path}morning_model/val_sign/{date}.pkl')
    else:
        signal_930 = pd.Series()
        lm.sendMessage('930信号未生成')
    _ = holding_930.pop('cash')
    _ = holding_info.pop('cash')
    code_list = sorted(list(set(code_list).union({x for x in holding_info}).union(set(holding_930.keys())).union(set(signal_930.index.tolist()))))

    portfolio_file = pd.DataFrame({
        '买入交易账户': account,
        '卖出交易账户': account,
        # '买入证券账户':5160503,
        # '卖出证券账户':5160503,
        '买入证券数量': 10000000,
        '卖出证券数量': pd.Series(holding_info).reindex(code_list).fillna(0)+pd.Series(holding_930).reindex(code_list).fillna(0)
    }, index=code_list).reset_index().rename(columns={'index': '证券代码'})
    portfolio_file['卖出证券数量'] = portfolio_file['卖出证券数量'].fillna(0)
    port_file_path = f'{local_config_path}/portfolio_file/{date}/'
    if not os.path.exists(port_file_path):
        os.mkdir(port_file_path)
    portfolio_file.to_excel(f'{port_file_path}/EMPortFile{date}_{account}_with_930.xlsx')
    # send_file(['015664'],f'{local_config_path}/portfolio_file/EMPortFile{date}_{account}_with_930.xlsx')
    # portfolio_file.to_excel(f'/data/user/011477/Trade_Docs/{date}/EnsembleMonitor_{date}/EnsembleMonitor_{date}_{account}.xlsx')
    # upload(f'/data/user/011477/Trade_Docs/{date}/EnsembleMonitor_{date}/EnsembleMonitor_{date}_{account}.xlsx', f'EnsembleMonitor_{date}_{account}.xlsx')
    # lm.sendMessage(f'交易组合生成成功{account}----------------')
except:
    lm.sendMessage('交易组合生成失败！！！！！！！！！！！！')
    info = traceback.format_exc()
    print(info)
    lm.sendMessage(info)

