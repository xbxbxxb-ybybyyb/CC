import sys
sys.path.insert(4, '/dfs/user/015626/JupyterNotebooks/utils/')

import pandas as pd
import numpy as np
import datetime, math
from multifactor.IO import IO
from tqdm import tqdm
import os, json
from copy import copy
import multifactor.utility.dt as udt
from multiprocessing import Pool
from xquant.investment.strategyfile import *

from xquant.thirdpartydata.marketdata import MarketData

import re
def get_prod_id(s):
    return re.sub(r'\d', '', s)

from super_link import LinkMessage

def send_link(message):
    lm = LinkMessage(['015626', '012398'])
#    lm = LinkMessage(['015626'])
    lm.sendMessage(str(message))
    del(lm)

def send_link_all(message):
    lm = LinkMessage(['015626', '013542', '012398'])
    #lm = LinkMessage(['015626'])
    lm.sendMessage(str(message))
    del(lm)

send_link('start spiral')

is_prod = True
use_para_basis = True
long_basis_ratio_t = 0.05
short_basis_ratio_t = -0.05

date = datetime.datetime.now().strftime('%Y%m%d')
# date = '20250818'
trade_root = '/dfs/group/800466/trade/spiral/'
min_order_qty_path = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/INFO/min_order_qty.csv'
mo_qty_dict = pd.read_csv(min_order_qty_path, index_col=['Ticker'])['min_order_qty'].to_dict()
# 存储交易参数的路径
if is_prod: 
    para_rootpath = f'/data/user/015626/data/share/para/Spiral/Spiral/{date}/'
else:
    para_rootpath = f'/data/user/015626/data/share/para/Spiral/Spiral/{date}_sim/'
back_para_path = os.path.join(para_rootpath, 'back_para')
front_para_path = os.path.join(para_rootpath, 'front_para')
os.makedirs(back_para_path, exist_ok=True)
os.makedirs(front_para_path, exist_ok=True)

trigger_time = datetime.time(14, 55)
minute_data_start_time = datetime.time(20, 50)
trade_stop_time = datetime.time(14, 59, 30)

if is_prod:
    zone = "801101"  # 注意参数dict中也有zoneid
else:
    zone = "304301"  # 注意参数dict中也有zoneid

account_dict = {
    'SHF':{'trade_account':'204510', 'security_account':'82001277'},
    'INE':{'trade_account':'204510', 'security_account':'82001277'},
    'DCE':{'trade_account':'204510', 'security_account':'05525773'},
    'ZCE':{'trade_account':'204510', 'security_account':'99849147'},
    'GFE':{'trade_account':'204510', 'security_account':'05283525'},
}


# excel参数列表
# trade para
put_order_stime = trigger_time.strftime('%H:%M:%S')
put_order_etime = trade_stop_time.strftime('%H:%M:%S')

trade_account = "204510"
security_account = '82001277'

base_para_dict = {
    "zoneid": zone,
    "账户登录信息": [{"TradingAccount": trade_account}],
    "是否平今仓": False, 
    '合约代码': '',
    '合约张数': 0,
    '买卖方向': '',
    '下单开始时间': put_order_stime,
    '下单结束时间': put_order_etime,
    '每次下单数量': 1,
    '单笔最小委托数量': 1,
    '单笔最大委托数量': 30,
    '买入交易账户': trade_account,
    '卖出交易账户': trade_account,
    '买入证券账户': security_account,
    '卖出证券账户': security_account,

    '当日所有合约开仓数量上限': 500,
    '过去1s所有合约开仓成交数量与挂单数量上限': 50,
    '最小下单间隔': 3,
    '最大下单次数': 600,
    '最大撤单次数': 300,
    '最大撤废次数': 100,
    '过去1分钟最大下单次数': 120,
    '过去1分钟最大撤单次数': 120,
    '当日废单次数上限': 300}

log_path = os.path.join(trade_root, 'log', date)
os.makedirs(log_path, exist_ok=True)
plan_path = os.path.join(trade_root, 'plan', date)
os.makedirs(plan_path, exist_ok=True)

global has_trade_today
has_trade_today = False # 今天有交易吗

import logging

# 创建日志记录器
logger = logging.getLogger('spiral_logger')
logger.setLevel(logging.DEBUG)  # 设置日志记录器的最低日志级别为DEBUG
   
# 创建文件处理器
file_handler = logging.FileHandler(os.path.join(log_path, f"spiral_{datetime.datetime.now().strftime('%Y%m%d %H%M%S')}.log"))
file_handler.setLevel(logging.DEBUG)  # 文件处理器记录DEBUG及以上级别的日志
file_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
)

# 将处理器添加到日志记录器
logger.addHandler(file_handler)

logger.info('strategy start')

def set_755_permission(path):
    for root, dirs, files in os.walk(path):
        # 设置目录权限为 755
        for d in dirs:
            dir_path = os.path.join(root, d)
            os.chmod(dir_path, 0o755)

def generate_json_para(para_dict, contract, num, direction, suffix = ''):
    prod_id = get_prod_id(contract)
    mo_qty = mo_qty_dict.get(prod_id, 1)
    para_dict['合约代码'] = contract
    para_dict['合约张数'] = int(num)
    para_dict['每次下单数量'] = math.ceil(int(num) / 60)
    if mo_qty > 1:
        para_dict['每次下单数量'] = max(para_dict['每次下单数量'], mo_qty)
        para_dict['单笔最小委托数量'] = mo_qty
    para_dict['买卖方向'] = direction

    _trade_account = account_dict[contract.split('.')[-1]]['trade_account']
    _security_account = account_dict[contract.split('.')[-1]]['security_account']
    para_dict['买入交易账户'] = _trade_account
    para_dict['卖出交易账户'] = _trade_account
    para_dict['买入证券账户'] = _security_account
    para_dict['卖出证券账户'] = _security_account
    para_dict["账户登录信息"] = [{"TradingAccount": _trade_account}]

    final_para_dict = {
        "date": "20250101",
        "servers": [para_dict]
    }
    with open(os.path.join(plan_path, f'{contract}{suffix}_{date}.json'), 'w', encoding='utf-8') as file:
        json.dump(final_para_dict, file, indent=4, ensure_ascii=False)
    
    no_exg_contract = contract.split('.')[0]
    contract_back_para_path = os.path.join(back_para_path, f'{no_exg_contract}{suffix}')
    os.makedirs(contract_back_para_path, exist_ok = True)
    with open(os.path.join(contract_back_para_path, f'settings.json'), 'w', encoding='utf-8') as file:
        json.dump(final_para_dict, file, indent=4, ensure_ascii=False)
    
    front_para = {
        "path":f"/home/appadmin/cppParam/Spiral/{no_exg_contract}{suffix}/"
    }
    with open(os.path.join(front_para_path, f'{no_exg_contract}{suffix}#{zone}.json'), 'w', encoding='utf-8') as file:
        json.dump(front_para, file, indent=4, ensure_ascii=False)
    
    global has_trade_today
    has_trade_today = True

def get_basis_ratio(contract_list, close_list, close_main):
    _con_list = [re.findall(r'\d+', x)[0] for x in contract_list]
    first_str_list = [x[0] for x in _con_list]
    if '9' in first_str_list and '0' in first_str_list:
        reform_list = [int('1' + x) if x[0] != '9' else int(x) for x in _con_list]
    else:
        reform_list = [int('1' + x) for x in _con_list]
    pd_s = pd.Series(close_list, index=reform_list).sort_index()
    if (pd_s.iloc[0] - pd_s.iloc[1]) * (pd_s.iloc[1] - pd_s.iloc[2]) <= 0:
        basis_ratio = np.nan
    else:
        basis_ratio = (pd_s.iloc[2] - pd_s.iloc[0]) / ((pd_s.index[2] - pd_s.index[0]) % 88) * 12 / close_main
    return basis_ratio

def get_top3_contracts(contractlist, oi_list):
    # 将合约与对应的OI值配对
    combined = list(zip(oi_list, contractlist))
    # 按OI值降序排序
    sorted_combined = sorted(combined, key=lambda x: -x[0])
    # 提取前三个合约
    top3_contracts = [contract for _, contract in sorted_combined[:3]]
    return top3_contracts

paradf_origin = pd.read_csv(os.path.join(trade_root, 'para', f'para_{date}.csv'), index_col=['Ticker'])
paradf = paradf_origin.dropna(subset=['curcontract', 'maincontract', 'contractlist'])
if len(paradf_origin) != len(paradf):
    send_link('spiral parsdf contract column has nan')
    logger.warning('spiral parsdf contract column has nan')
paradf = paradf[~paradf.index.astype(str).str.endswith('CFE')]

if use_para_basis:
    paradf_basis = pd.read_csv(os.path.join(trade_root, 'para_basis', f'para_basis_{date}.csv'), index_col=['Ticker']).dropna(subset=['curcontract', 'maincontract', 'contractlist'])
    paradf_basis = paradf_basis[~paradf_basis.index.astype(str).str.endswith('CFE')]
    ticker_list_basis = sorted(list(set(paradf_basis.index.tolist())))

ticker_list = sorted(list(set(paradf.index.tolist())))

def get_ticker(ticker):
    pre_date = udt.get_trading_day_offset(date, -1)[0].strftime('%Y%m%d')

    tpara = paradf.loc[ticker]
    if isinstance(tpara, pd.Series):
        tpara = tpara.to_dict()
    else:
        tpara = tpara[tpara.shares_holding > 0].loc[ticker].to_dict()

    contractlist = tpara['contractlist'].split(',')
    maincontract = tpara['maincontract']
    curcontract = tpara['curcontract']
    all_contract_list = list(set(contractlist + [maincontract]))

    data_dict = {}
    for contract in all_contract_list:
        ma = MarketData()
        mdf = ma.getMDSecurityKLineDataFrame(contract,  f"{pre_date}{minute_data_start_time.strftime('%H%M%S')}",  f"{date}{trigger_time.strftime('%H%M%S')}", 10, 20)
        logger.debug(contract + ' data lenth: ' + str(len(mdf)))
        if len(mdf) == 0 and contract != maincontract:
            continue
        ohlc_dict = {}
        ohlc_dict['LastTime'] = mdf['MDTime'].iloc[-1]
        ohlc_dict['open'] = mdf['OpenPx'].iloc[0]
        ohlc_dict['high'] = np.nanmax(mdf['HighPx'].tolist())
        ohlc_dict['low'] = np.nanmin(mdf['LowPx'].tolist())
        ohlc_dict['close'] = mdf['ClosePx'].iloc[-1]
        ohlc_dict['oi'] = mdf['OpenInterest'].iloc[-1]
        data_dict[contract] = ohlc_dict
        del(ma)
    
    oi_list = []
    for con in contractlist:
        oi_list.append(data_dict[con]['oi'])

    new_maincontract = contractlist[oi_list.index(np.nanmax(oi_list))]
    main_data_dict = data_dict[maincontract]
    main_data_dict['preclose'] = tpara['cls_main_org']

    top3_contracts = get_top3_contracts(contractlist, oi_list)
    close_list = []
    for con in top3_contracts:
        close_list.append(data_dict[con]['close'])

    tr = max(abs(main_data_dict['close']-main_data_dict['preclose']), abs(main_data_dict['open']-main_data_dict['preclose']),(main_data_dict['high']-main_data_dict['low']))
    trlist = eval(tpara['trlist']) + [tr]
    atr = np.nanmean(trlist)
    
    rt = main_data_dict['close'] / main_data_dict['preclose'] - 1
    rtlist = eval(tpara['rtlist']) + [rt]
    nstd = np.std(rtlist, ddof = 1)

    basis_ratio_origin = get_basis_ratio(top3_contracts, close_list, main_data_dict['close'])
    basislist = eval(tpara['basislist'].replace('nan','np.nan')) + [basis_ratio_origin]
    cleaned_basis = [x for x in basislist if isinstance(x, (int, float)) and not np.isnan(x)]
    basis_ratio = np.nanmean(cleaned_basis) if len(cleaned_basis) >= 3 else np.nan
    logger.info(ticker + ' basis_ratio ' + str(basis_ratio) + ' basislist ' + str(basislist))
    nstd8 = nstd * 8
    if long_basis_ratio_t is not None:
        _long_basis_ratio_t = min(long_basis_ratio_t, nstd8)
    else:
        _long_basis_ratio_t = None
    if short_basis_ratio_t is not None:
        _short_basis_ratio_t = -1 * min(abs(short_basis_ratio_t), nstd8)
    else:
        _short_basis_ratio_t = None

    
    new_shares_adj = min(main_data_dict['close'] / atr/ 20, 10)
    new_shares = int(tpara['cap'] * 1e4 / main_data_dict['close'] / tpara['multiplier'] * new_shares_adj)

    close = main_data_dict['close']
    para_dict = base_para_dict.copy()
    para_dict['合约代码'] = new_maincontract

    high = main_data_dict['high']
    high_new = data_dict[new_maincontract]['high']
    hold_value = 0

    if tpara['pos'] == 1:
        hold_value = tpara['shares_holding'] * high * tpara['multiplier']
        if tpara['shares_holding'] != 0 and (nstd > tpara['std_thd'] or close > tpara['longout_up'] or close < tpara['longout_down']):
            reason = ' '
            if nstd > tpara['std_thd']:
                reason += ' std>t '
            if close > tpara['longout_up']:
                reason += ' close>longout_up '
            if close < tpara['longout_down']:
                reason += ' close<longout_down '
            logger.info(curcontract + ' trade sell_close ' + str(tpara['shares_holding']) + reason)
            send_link(curcontract + ' trade sell_close ' + str(tpara['shares_holding']) + reason)
            generate_json_para(base_para_dict.copy(), curcontract, tpara['shares_holding'], 'sell_close')
        elif tpara['shares_holding'] != 0 and curcontract != new_maincontract:
            logger.info(curcontract + ' yicang ' + str(tpara['shares_holding']))
            send_link(curcontract + ' yicang ' + str(tpara['shares_holding']))
            generate_json_para(base_para_dict.copy(), curcontract, tpara['shares_holding'], 'sell_close')
            generate_json_para(base_para_dict.copy(), new_maincontract, tpara['shares_holding'], 'buy_open')
    
    elif tpara['pos'] == -1:
        hold_value = tpara['shares_holding'] * high * tpara['multiplier']
        if tpara['shares_holding'] != 0 and (nstd > tpara['std_thd'] or close > tpara['shortout_up'] or close < tpara['shortout_down']):
            reason = ' '
            if nstd > tpara['std_thd']:
                reason += ' std>t '
            if close > tpara['shortout_up']:
                reason += ' close>shortout_up '
            if close < tpara['shortout_down']:
                reason += ' close<shortout_down '
            logger.info(curcontract + ' trade buy_close ' + str(tpara['shares_holding']) + reason)
            send_link(curcontract + ' trade buy_close ' + str(tpara['shares_holding']) + reason)
            generate_json_para(base_para_dict.copy(), curcontract, tpara['shares_holding'], 'buy_close')
        elif tpara['shares_holding'] != 0 and curcontract != new_maincontract:
            logger.info(curcontract + ' yicang ' + str(tpara['shares_holding']))
            send_link(curcontract + ' yicang ' + str(tpara['shares_holding']))
            generate_json_para(base_para_dict.copy(), curcontract, tpara['shares_holding'], 'buy_close')
            generate_json_para(base_para_dict.copy(), new_maincontract, tpara['shares_holding'], 'sell_open')
            
    elif tpara['pos'] == 0:
        if nstd < tpara['std_thd']:
            if close > tpara['longin_down'] and close < tpara['longin_up']:
                if _long_basis_ratio_t is None or (_long_basis_ratio_t is not None and basis_ratio < _long_basis_ratio_t):
                    logger.info(new_maincontract + ' trade buy_open ' + str(new_shares))
                    send_link(new_maincontract + ' trade buy_open ' + str(new_shares))
                    generate_json_para(base_para_dict.copy(), new_maincontract, new_shares, 'buy_open')
                    hold_value = new_shares * high_new * tpara['multiplier']
            elif close > tpara['shortin_down'] and close < tpara['shortin_up']:
                if _short_basis_ratio_t is None or (_short_basis_ratio_t is not None and basis_ratio > _short_basis_ratio_t):
                    logger.info(new_maincontract + ' trade sell_open ' + str(new_shares))
                    send_link(new_maincontract + ' trade sell_open ' + str(new_shares))
                    generate_json_para(base_para_dict.copy(), new_maincontract, new_shares, 'sell_open')
                    hold_value = new_shares * high_new * tpara['multiplier']
        if hold_value == 0:
            hold_value = tpara['shares_holding'] * high * tpara['multiplier']

    tpara['main_data_dict'] = str(main_data_dict)
    tpara['oi_list'] = str(oi_list)
    tpara['new_maincontract'] = new_maincontract
    tpara['tr'] = tr
    tpara['atr'] = atr
    tpara['nstd'] = nstd
    tpara['new_shares_adj'] = new_shares_adj
    tpara['new_shares'] = new_shares
    tpara['hold_value'] = hold_value
    tpara['oi_top3_contracts'] = str(top3_contracts)
    tpara['close_list'] = str(close_list)
    tpara['basis_ratio'] = basis_ratio
    tpara['all_basislist'] = str(basislist)
    tpara['nstd8'] = nstd8
    tpara['_long_basis_ratio_t'] = _long_basis_ratio_t
    tpara['_short_basis_ratio_t'] = _short_basis_ratio_t
#    logger.debug(ticker + ' trade info: ' + str(tpara))
    return pd.DataFrame(tpara, index = [ticker])

def get_ticker_for_para_basis(ticker):
    pre_date = udt.get_trading_day_offset(date, -1)[0].strftime('%Y%m%d')

    tpara = paradf_basis.loc[ticker]
    if isinstance(tpara, pd.Series):
        tpara = tpara.to_dict()
    else:
        tpara = tpara[tpara.shares_holding > 0].loc[ticker].to_dict()

    contractlist = tpara['contractlist'].split(',')
    maincontract = tpara['maincontract']
    curcontract = tpara['curcontract']
    all_contract_list = list(set(contractlist + [maincontract]))

    data_dict = {}
    for contract in all_contract_list:
        ma = MarketData()
        mdf = ma.getMDSecurityKLineDataFrame(contract,  f"{pre_date}{minute_data_start_time.strftime('%H%M%S')}",  f"{date}{trigger_time.strftime('%H%M%S')}", 10, 20)
        logger.debug('para_basis ' + contract + ' data lenth: ' + str(len(mdf)))
        if len(mdf) == 0 and contract != maincontract:
            continue
        ohlc_dict = {}
        ohlc_dict['LastTime'] = mdf['MDTime'].iloc[-1]
        ohlc_dict['open'] = mdf['OpenPx'].iloc[0]
        ohlc_dict['high'] = np.nanmax(mdf['HighPx'].tolist())
        ohlc_dict['low'] = np.nanmin(mdf['LowPx'].tolist())
        ohlc_dict['close'] = mdf['ClosePx'].iloc[-1]
        ohlc_dict['oi'] = mdf['OpenInterest'].iloc[-1]
        data_dict[contract] = ohlc_dict
        del(ma)
    
    oi_list = []
    for con in contractlist:
        oi_list.append(data_dict[con]['oi'])

    new_maincontract = contractlist[oi_list.index(np.nanmax(oi_list))]
    main_data_dict = data_dict[maincontract]
    main_data_dict['preclose'] = tpara['cls_main_org']

    top3_contracts = get_top3_contracts(contractlist, oi_list)
    close_list = []
    for con in top3_contracts:
        close_list.append(data_dict[con]['close'])

    tr = max(abs(main_data_dict['close']-main_data_dict['preclose']), abs(main_data_dict['open']-main_data_dict['preclose']),(main_data_dict['high']-main_data_dict['low']))
    trlist = eval(tpara['trlist']) + [tr]
    atr = np.nanmean(trlist)
    
    rt = main_data_dict['close'] / main_data_dict['preclose'] - 1
    rtlist = eval(tpara['rtlist']) + [rt]
    nstd = np.std(rtlist, ddof = 1)

    basis_ratio_origin = get_basis_ratio(top3_contracts, close_list, main_data_dict['close'])
    basislist = eval(tpara['basislist'].replace('nan','np.nan')) + [basis_ratio_origin]
    cleaned_basis = [x for x in basislist if isinstance(x, (int, float)) and not np.isnan(x)]
    basis_ratio = np.nanmean(cleaned_basis) if len(cleaned_basis) >= 3 else np.nan
    logger.info(ticker + ' basis_ratio ' + str(basis_ratio) + ' basislist ' + str(basislist))
    nstd8 = nstd * 8
    nstd2 = nstd * 2
    
    new_shares_adj = min(main_data_dict['close'] / atr/ 20, 10)
    new_shares = int(tpara['cap'] * 1e4 / main_data_dict['close'] / tpara['multiplier'] * new_shares_adj)

    close = main_data_dict['close']
    para_dict = base_para_dict.copy()
    para_dict['合约代码'] = new_maincontract

    high = main_data_dict['high']
    high_new = data_dict[new_maincontract]['high']
    hold_value = 0

    if tpara['pos'] == 1:
        hold_value = tpara['shares_holding'] * high * tpara['multiplier']
        if tpara['shares_holding'] != 0 and (nstd > tpara['std_thd'] or close > tpara['longout_up'] or close < tpara['longout_down'] or basis_ratio > -1 * nstd2):
            reason = ' '
            if nstd > tpara['std_thd']:
                reason += ' std>t '
            if close > tpara['longout_up']:
                reason += ' close>longout_up '
            if close < tpara['longout_down']:
                reason += ' close<longout_down '
            logger.info('para_basis ' + curcontract + ' trade sell_close ' + str(tpara['shares_holding']) + reason)
            send_link('para_basis ' + curcontract + ' trade sell_close ' + str(tpara['shares_holding']) + reason)
            generate_json_para(base_para_dict.copy(), curcontract, tpara['shares_holding'], 'sell_close', suffix='_added')
        elif tpara['shares_holding'] != 0 and curcontract != new_maincontract:
            logger.info('para_basis ' + curcontract + ' yicang ' + str(tpara['shares_holding']))
            send_link('para_basis ' + curcontract + ' yicang ' + str(tpara['shares_holding']))
            generate_json_para(base_para_dict.copy(), curcontract, tpara['shares_holding'], 'sell_close')
            generate_json_para(base_para_dict.copy(), new_maincontract, tpara['shares_holding'], 'buy_open', suffix='_added')
    
    elif tpara['pos'] == -1:
        hold_value = tpara['shares_holding'] * high * tpara['multiplier']
        if tpara['shares_holding'] != 0 and (nstd > tpara['std_thd'] or close > tpara['shortout_up'] or close < tpara['shortout_down'] or basis_ratio < nstd2):
            reason = ' '
            if nstd > tpara['std_thd']:
                reason += ' std>t '
            if close > tpara['shortout_up']:
                reason += ' close>shortout_up '
            if close < tpara['shortout_down']:
                reason += ' close<shortout_down '
            logger.info('para_basis ' + curcontract + ' trade buy_close ' + str(tpara['shares_holding']) + reason)
            send_link('para_basis ' + curcontract + ' trade buy_close ' + str(tpara['shares_holding']) + reason)
            generate_json_para(base_para_dict.copy(), curcontract, tpara['shares_holding'], 'buy_close', suffix='_added')
        elif tpara['shares_holding'] != 0 and curcontract != new_maincontract:
            logger.info('para_basis ' + curcontract + ' yicang ' + str(tpara['shares_holding']))
            send_link('para_basis ' + curcontract + ' yicang ' + str(tpara['shares_holding']))
            generate_json_para(base_para_dict.copy(), curcontract, tpara['shares_holding'], 'buy_close')
            generate_json_para(base_para_dict.copy(), new_maincontract, tpara['shares_holding'], 'sell_open', suffix='_added')
            
    elif tpara['pos'] == 0:
        if nstd < tpara['std_thd']:
            if close > tpara['longin_down'] and close < tpara['longin_up']:
                if basis_ratio < -1 * nstd8:
                    logger.info('para_basis ' + new_maincontract + ' trade buy_open ' + str(new_shares))
                    send_link('para_basis ' + new_maincontract + ' trade buy_open ' + str(new_shares))
                    generate_json_para(base_para_dict.copy(), new_maincontract, new_shares, 'buy_open', suffix='_added')
                    hold_value = new_shares * high_new * tpara['multiplier']
            elif close > tpara['shortin_down'] and close < tpara['shortin_up']:
                if basis_ratio > nstd8:
                    logger.info('para_basis ' + new_maincontract + ' trade sell_open ' + str(new_shares))
                    send_link('para_basis ' + new_maincontract + ' trade sell_open ' + str(new_shares))
                    generate_json_para(base_para_dict.copy(), new_maincontract, new_shares, 'sell_open', suffix='_added')
                    hold_value = new_shares * high_new * tpara['multiplier']
        if hold_value == 0:
            hold_value = tpara['shares_holding'] * high * tpara['multiplier']

    tpara['main_data_dict'] = str(main_data_dict)
    tpara['oi_list'] = str(oi_list)
    tpara['new_maincontract'] = new_maincontract
    tpara['tr'] = tr
    tpara['atr'] = atr
    tpara['nstd'] = nstd
    tpara['new_shares_adj'] = new_shares_adj
    tpara['new_shares'] = new_shares
    tpara['hold_value'] = hold_value
    tpara['oi_top3_contracts'] = str(top3_contracts)
    tpara['close_list'] = str(close_list)
    tpara['basis_ratio'] = basis_ratio
    tpara['all_basislist'] = str(basislist)
    tpara['nstd8'] = nstd8
    tpara['nstd2'] = nstd2
#    logger.debug(ticker + ' trade info: ' + str(tpara))
    return pd.DataFrame(tpara, index = [ticker])


rlist = []
for ticker in ticker_list:
    try:
        rlist.append(get_ticker(ticker))
    except Exception as e:
        print(ticker, e)
        send_link(ticker + str(e))
        logger.error(ticker + str(e))

if use_para_basis:
    rlist_basis = []
    for ticker in ticker_list_basis:
        try:
            rlist_basis.append(get_ticker_for_para_basis(ticker))
        except Exception as e:
            print('para_basis', ticker, e)
            send_link('para_basis ' + ticker + str(e))
            logger.error('para_basis ' + ticker + str(e))

if has_trade_today:
    set_755_permission(para_rootpath)
    send_link('spiral 今日有交易')
    logger.info('spiral 今日有交易, 开始上传参数')
    if is_prod:
        upload_gccstrategy_file(strategy_id = "Spiral", strategy_date = str(date),
                     upload_file_path=back_para_path, is_tradingsession=True)
        for kind in os.listdir(back_para_path):
            # 前台
            upload_strategy_file(strategy_id = "Spiral", strategy_date = str(date), file_type = 1, 
                            upload_file_path = os.path.join(front_para_path, f'{kind}#{zone}.json'), is_delete=False,  is_ready=1, disable_instance_validation=0, max_instance=1)   
    else:
        sim_upload_gccstrategy_file(strategy_id = "Spiral", strategy_date = str(date),
                     upload_file_path=back_para_path, is_tradingsession=True)
        for kind in os.listdir(back_para_path):
            # 前台
            sim_upload_strategy_file(strategy_id = "Spiral", strategy_date = str(date), file_type = 1, 
                            upload_file_path = os.path.join(front_para_path, f'{kind}#{zone}.json'), is_delete=False,  is_ready=1)    

rdf = pd.concat([x for x in rlist]).sort_index()
rdf.to_csv(os.path.join(log_path, f'log_{date}.csv'))
hold_value_sum = rdf['hold_value'].sum()
if use_para_basis:
    rdf_basis = pd.concat([x for x in rlist_basis]).sort_index()
    rdf_basis.to_csv(os.path.join(log_path, f'log_{date}_para_basis.csv'))
    hold_value_sum += rdf_basis['hold_value'].sum()

bond_money = math.ceil(hold_value_sum * 0.3 / 10000)
send_link_all(f'Spiral今日持仓价值为{hold_value_sum}，保证金保留{bond_money}万')