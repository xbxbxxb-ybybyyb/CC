import pandas as pd
import numpy as np
import os
import datetime
from multifactor.data.utils import *
import warnings
import multifactor.utility.dt as udt
from multifactor.data.utils import *
from xquant.xqutils.helper import link
from link_modified import LinkMessage

warnings.filterwarnings("ignore")
_,eedate,date_list = check_update_date()
edate = str(eedate)

date = udt.get_trading_day_offset(edate,1)[0].strftime('%Y%m%d')
#date = '20220802'
category = 'IC'
print(date)
b = date


user_ids = [
    '012315',
    '012398',
    '015626',  
    '016700',
    '017024'
]

def path_check(b = b):
    if os.path.exists('/data/user/011477/order/O32/51606/综合信息查询_成交回报明细_%s_51606.xls'%b):
        return True
    else:
        return False

print('------wait data flag')
while True:
    if path_check(date):
        break
    time.sleep(5)


for category in ['IC', 'IF']:
    if category == 'IC':
        beishu = 200
        trail = ''
    else:
        beishu = 300
        trail = '_if'
    future_traded = [item[:-3] for item in list(pd.read_excel('/data/user/016700/Data/para/Mobius_%s/MobiusStrategy_%s_%s.xlsx'%(str(b).replace('-', ''), category, str(b).replace('-', '')), sheetname = '期初持仓列表')['合约代码'])]
    trading_stats = pd.read_excel('/data/user/011477/order/O32/51606/综合信息查询_成交回报明细_%s_51606.xls'%b)
    trading_stats = trading_stats.loc[trading_stats['日期'].isna() == False]
    trading_stats['成交时间1'] = pd.to_datetime(trading_stats['成交时间'].apply(lambda x: (b + str(x).replace(':', ''))[:-2]))


    trading_stats = trading_stats[(trading_stats['证券代码'].isin(future_traded))&(trading_stats['组合编号'].isin([5160604, 5160701])) & (trading_stats['成交时间1'] >= pd.to_datetime(b + '0939')) & (trading_stats['成交时间1'] <= pd.to_datetime(b + '1450'))].sort_values(by = '成交时间')

    def direction(x):
        if '买'  in x:
            return 1
        elif '卖' in x:
            return -1
        else:
            pass

    df_trade = trading_stats.set_index('成交时间1')
    df_trade.index.name = 'dt'

    deal_records = (df_trade['证券代码'].resample('1min').count() * df_trade['委托方向'].apply(lambda x: direction(x)).resample('1min').first()).dropna()

    try:
        trading_stats['发生金额(全价)'] = trading_stats['发生金额(全价)'].apply(lambda x:float(x.replace(',', '')))
        print('#')
    except:
        pass

    tc = (trading_stats['成交数量'] * trading_stats['成交价格'] * beishu * 0.000023 * 1.01).sum()
    pnl = trading_stats['发生金额(全价)'].sum() - tc


    df = pd.DataFrame()
    df['成交时间'] = trading_stats['成交时间']
    df['合约'] = trading_stats['证券名称']
    df['成交价'] = trading_stats['成交价格']
    df['成交量'] = trading_stats['成交数量']
    df['发生金额'] = trading_stats['发生金额(全价)']
    df['委托方向'] = trading_stats['委托方向']
    df = df.set_index('成交时间')
    df['交易费用'] = df['成交量'] * df['成交价'] * beishu * 0.000028
    #df.to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/log_%s.xlsx'%b)

    pnl_df = pd.DataFrame()
    pnl_df['date'] = [int(b)]
    pnl_df['pnl'] = [pnl]
    pnl_df = pnl_df.set_index('date')
    pnl_df['transaction_cost'] = tc

    pnl_df['contracts_traded'] = trading_stats[trading_stats['委托方向'].isin(['买入平仓', '买入开仓'])]['成交数量'].sum()
    pnl_df['单边金额总数（买入）'] = abs(trading_stats[trading_stats['委托方向'].isin(['买入平仓', '买入开仓'])]['发生金额(全价)'].sum())
    pnl_df_fh = pd.read_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl%s.xlsx'%trail, index_col = 0)
    if 'contracts_traded' not in pnl_df.columns:
        pnl_df['contracts_traded'] = np.nan
        pnl_df['单边金额总数（买入）'] = np.nan

    tempdf = pd.concat([pnl_df_fh, pnl_df]).sort_index()
    tempdf = tempdf[~tempdf.index.duplicated(keep='last')]
    tempdf.to_excel('/data/group/800466/warehouse/prod/tradingstats/Mobius/pnl%s.xlsx'%trail)


    #lm = link.LinkMessage()
    #lm.sendMessage(category + '_' + str(tempdf.iloc[-1]['pnl']))
    
    lm = LinkMessage(user_ids)
    lm.sendMessage(category + ':  ' + str(round(int(tempdf.iloc[-1]['pnl'])/10000, 1)) + '万')
    
    
    
    del lm

