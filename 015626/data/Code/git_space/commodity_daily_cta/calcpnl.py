import sys
sys.path.insert(4,'/dfs/user/012398/working_code/prod_zhangf/')
from multifactor.IO import IO
import multifactor.utility.dt as dt
import pandas as pd
import datetime,os,time,warnings
from xquant.thirdpartydata.marketdata import MarketData
warnings.filterwarnings('ignore')
from link import LinkMessage


ma = MarketData()
def get_close(ticker, date):
    mdf = ma.getMDSecurityKLineDataFrame(ticker,  date + "145500",  date + "150100", 10, 20)
    close = mdf['ClosePx'].iloc[-1]
    return close
    
#def check_xdb_data(date, ticker):
#    try:
#        fd.get_tickex(date, ticker)
#        return True
#    except:
#        return False
        
date =  pd.Timestamp(datetime.date.today()).strftime('%Y%m%d')
#date = '20250728'
pre_date = dt.get_trading_day_offset(date,-1)[0].strftime('%Y%m%d')
res_path = '/data/user/011477/Arrow'
exchange_dict = {'上期所':'SHF','郑商所':'ZCE','广期所':'GFE','能源交易所':'INE','大商所':'DCE'}
filename = os.path.join(res_path, date + '_Spiral.xlsx')

while True:
    if not os.path.exists(filename):
        print('wait pos exel!')
        time.sleep(60)
    else:
        pos_holding_last = pd.read_excel(os.path.join(res_path, pre_date + '_Spiral.xlsx'),sheet_name = 'Spiral持仓情况',index_col = 0)
        pos_trading = pd.read_excel(os.path.join(res_path, date + '_Spiral.xlsx'),sheet_name = 'Spiral成交情况',index_col = 0)
        pos_trading['证券代码'] = pos_trading['证券代码'].fillna(method = 'pad')
        pos_holding_cur = pd.read_excel(os.path.join(res_path, date + '_Spiral.xlsx'),sheet_name = 'Spiral持仓情况',index_col = 0)    
        break
pos_trading['exchange'] = pos_trading['交易市场'].apply(lambda x:exchange_dict[x])
pos_trading['Ticker'] = pos_trading['证券代码'].apply(lambda x: x.upper()) + '.' + pos_trading['exchange']
pos_holding_last['exchange'] = pos_holding_last['交易市场'].apply(lambda x:exchange_dict[x])
pos_holding_last['Ticker'] = pos_holding_last['证券代码'].apply(lambda x: x.upper()) + '.' + pos_holding_last['exchange']
pos_trading['direction'] = pos_trading['委托方向'].apply(lambda x:{'买':1,'卖':-1}[x[0]])

## check xdb data
#ticker = pos_trading['Ticker'].iloc[0]
#while not check_xdb_data(date, ticker):
#    print('wait xdb data!')
#    time.sleep(300)
    
pos_holding_last['pre_close'] = pos_holding_last['Ticker'].apply(lambda x:get_close(x, pre_date))
pos_holding_last['close'] = pos_holding_last['Ticker'].apply(lambda x:get_close(x, date))
pos_trading['close'] = pos_trading['Ticker'].apply(lambda x:get_close(x, date))

pos_holding_last = pos_holding_last.set_index('Ticker')
pos_trading = pos_trading.set_index('Ticker')
data_test = IO.read_data(pre_date,alt = '/dfs/group/800466/warehouse/prod/CHINA_COMMODITY/MD/DAILY/MD_CHINA_FUTURE_DAILY.h5')
multp = data_test.loc[pd.Timestamp(pre_date)]['multiplier']

pos_holding_last = pos_holding_last.join(multp)
pos_trading = pos_trading.join(multp)

holding_pnl = ((pos_holding_last['close'] - pos_holding_last['pre_close']) * pos_holding_last['multiplier'] * pos_holding_last['多空符号'] * pos_holding_last['当前数量']).sum()
trading_pnl = ((pos_trading['close'] - pos_trading['成交价格']) * pos_trading['multiplier'] * pos_trading['direction'] * pos_trading['成交数量']).sum()

if len(pos_trading) == 0:
    feecost = 0
    buy_num = 0
    buy_value = 0
    sell_num = 0
    sell_value = 0
else:
    feecost = pos_trading['交易费'].sum()
    buy_num = len(pos_trading[pos_trading['direction'] == 1])
    buy_value = pos_trading[pos_trading['direction'] == 1]['成交金额'].sum()
    sell_num = len(pos_trading[pos_trading['direction'] == -1])
    sell_value = pos_trading[pos_trading['direction'] == -1]['成交金额'].sum()

total_pnl = holding_pnl + trading_pnl - feecost
pos_holding_cur = pos_holding_cur[pos_holding_cur['当前数量']!=0]
hold_num = len(pos_holding_cur)
hold_value = pos_holding_cur["持仓市值(元)"].sum()

pnl = pd.DataFrame([[holding_pnl, trading_pnl, total_pnl, buy_num, buy_value, sell_num, sell_value, hold_num, hold_value, feecost]],
                  columns = ['holding_pnl','trading_pnl','total_pnl','buy_num','buy_value','sell_num','sell_value','hold_num','hold_value','fee'],
                  index = [pd.Timestamp(date)])
pnl.index.name = 'dt'

pnl_old = pd.read_csv('/data/group/800466/warehouse/prod/tradingstats/Spiral/pnl.csv',index_col = 0, parse_dates = True)
pnl_old = pnl_old[~pnl_old.index.isin(pnl.index)]
pnl_new = pd.concat([pnl_old,pnl],axis=0).sort_index()
pnl_new.to_csv('/data/group/800466/warehouse/prod/tradingstats/Spiral/pnl.csv')

link_messager = LinkMessage(['012398','015626'])
link_messager.sendMessage("Spiral_%s: total_pnl: %d, trading_pnl: %d, holding_pnl: %d"%(date, total_pnl, trading_pnl, holding_pnl))