import os
import pandas as pd
import multifactor.utility.dt as udt
from overnight.naming_config import trade_root
from overnight.utility import get_current_futures_contract, save_pickle
from xquant.thirdpartydata.marketdata import MarketData
ma = MarketData()
#from xquant.xqutils.helper import link
from overnight.link_v3 import LinkMessage
lm = LinkMessage(['015626', '012398'])


def get_amp_singleday(t0):
    t1 = udt.get_trading_day_offset(t0, -1)[0]
    t0_str = t0.strftime('%Y%m%d')
    t1_str = t1.strftime('%Y%m%d')
    
    ic_rm = get_current_futures_contract(prod_id='IC.CFE', trade_date=t1, mode='recent')[:-1]
    if_rm = get_current_futures_contract(prod_id='IF.CFE', trade_date=t1, mode='recent')[:-1]
    ih_rm = get_current_futures_contract(prod_id='IH.CFE', trade_date=t1, mode='recent')[:-1]

    ic_b = ma.getMDSecurityTickDataFrame(ic_rm, f"{t1_str}145000", f"{t1_str}150000", 1)['Sell1Price'].mean()
    ic_s = ma.getMDSecurityTickDataFrame(ic_rm, f"{t0_str}093000", f"{t0_str}094000", 1)
    ic_s = ic_s[ic_s['Buy1Price'] > 0]['Buy1Price'].mean()
    if_b = ma.getMDSecurityTickDataFrame(if_rm, f"{t1_str}145000", f"{t1_str}150000", 1)['Sell1Price'].mean()
    if_s = ma.getMDSecurityTickDataFrame(if_rm, f"{t0_str}093000", f"{t0_str}094000", 1)
    if_s = if_s[if_s['Buy1Price'] > 0]['Buy1Price'].mean()
    ih_b = ma.getMDSecurityTickDataFrame(ih_rm, f"{t1_str}145000", f"{t1_str}150000", 1)['Sell1Price'].mean()
    ih_s = ma.getMDSecurityTickDataFrame(ih_rm, f"{t0_str}093000", f"{t0_str}094000", 1)
    ih_s = ih_s[ih_s['Buy1Price'] > 0]['Buy1Price'].mean()
    ic_ret = ic_s / ic_b - 1
    if_ret = if_s / if_b - 1
    ih_ret = ih_s / ih_b - 1
    result = abs(ic_ret + if_ret + ih_ret) / 3
    print('get amp', t0, ic_ret, if_ret, ih_ret)
    
    return result
    
    
def get_std_intraday(t0=None):
    if t0 is None:
        t0 = pd.Timestamp.now()
    t0_str = t0.strftime('%Y%m%d')
    ic_rm = get_current_futures_contract(prod_id='IC.CFE', trade_date=t0, mode='recent')[:-1]
    if_rm = get_current_futures_contract(prod_id='IF.CFE', trade_date=t0, mode='recent')[:-1]
    ih_rm = get_current_futures_contract(prod_id='IH.CFE', trade_date=t0, mode='recent')[:-1]
    im_rm = get_current_futures_contract(prod_id='IM.CFE', trade_date=t0, mode='recent')[:-1]
    ic_price = ma.getMDSecurityKLineDataFrame (ic_rm, f"{t0_str}093000", f"{t0_str}144000", 10, 20)['ClosePx']
    if_price = ma.getMDSecurityKLineDataFrame (if_rm, f"{t0_str}093000", f"{t0_str}144000", 10, 20)['ClosePx']
    ih_price = ma.getMDSecurityKLineDataFrame (ih_rm, f"{t0_str}093000", f"{t0_str}144000", 10, 20)['ClosePx']
    im_price = ma.getMDSecurityKLineDataFrame (im_rm, f"{t0_str}093000", f"{t0_str}144000", 10, 20)['ClosePx']
    ic_std = ic_price.pct_change().std()
    if_std = if_price.pct_change().std()
    ih_std = ih_price.pct_change().std()
    im_std = im_price.pct_change().std()
    lm.sendMessage(f'intraday volatility(0930~1440): IC={ic_std:.2e}, IF={if_std:.2e}, IH={ih_std:.2e}, IM={im_std:.2e}')
    
    
def get_amp_last5d(t0=None):
    if t0 is None:
        t0 = pd.Timestamp.now()
    date_list = udt.get_trading_day_offset(t0, [x for x in range(0, -20, -1)])
    result = 0
    day_count = 0
    for date in date_list:
        date_1 = udt.get_trading_day_offset(date, -1)[0]
        if (date - date_1).days not in [1, 3]:
            continue
        result += get_amp_singleday(date)
        day_count += 1
        if day_count == 5:
            break
    result = result / 5
    lm.sendMessage(f'5day-amp: {result:.2e}.')
    os.makedirs(os.path.join(trade_root, 'hot', t0.strftime('%Y%m%d')), exist_ok=True)
    out_path = os.path.join(trade_root, 'hot', t0.strftime('%Y%m%d'), 'amp_5d.pkl')
    save_pickle(result, out_path)
    return 
    
if __name__ == '__main__':
#    get_amp_singleday(pd.Timestamp('20240910'))
#    get_std_intraday()
    get_amp_last5d()
    
    