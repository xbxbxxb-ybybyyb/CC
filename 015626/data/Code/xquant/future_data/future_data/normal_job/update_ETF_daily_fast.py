def getdt(a,b):
    strdate = a + ' ' + b 
    return str(datetime.datetime.strptime(strdate, '%Y%m%d %H%M%S%f').strftime('%Y-%m-%d %H:%M:%S.%f'))
    
rootpath = '/data/user/015626/data/share/LOCAL_DATA/CSV/daily/CHINA_FUND/ETF_fast/'

droplist = ['MDRecordID','KLineType','MDDate','MDTime','SecurityID','HTSCSecurityID','PeriodType']

tdays = [x.date().strftime('%Y%m%d') for x in udt.get_trading_date_range(20170101, 20210618)]
tickerlist = []
for d in tdays:
    tickerlist = list(set(tickerlist + fd.get_fund_set(str(d), 'ETF')))

datelist = [x.date().strftime('%Y%m%d') for x in pd.date_range('20170101','20210618',freq='59D')] + ['20210617']

def get_fund_daily_by_ticker(ticker):
    print(ticker)
    for i in range(len(datelist) - 1):
        df = fd.get_fund_data(ticker, str(datelist[i])+" 070000000", str(datelist[i+1])+" 230000000", 'K_DAY')
        if len(df) == 0:
            continue
#        df['dt'] = df.apply(lambda x:getdt(x.MDDate, x.MDTime), axis = 1)
        df['dt'] = df['MDDate']
        df['Ticker'] = ticker
        df = df.drop(droplist,axis = 1)
        df = df.set_index(['dt','Ticker'])
        tickerpath = os.path.join(rootpath, ticker)
        if not os.path.exists(tickerpath):
            os.makedirs(tickerpath)
        df.to_csv(os.path.join(tickerpath, str(datelist[i])+'.csv'))

for ticker in tickerlist:
    get_fund_daily_by_ticker(ticker)

import glob
pathlist = glob.glob('/data/user/015626/data/share/LOCAL_DATA/CSV/daily/CHINA_FUND/ETF_fast/*/*.csv')

from multiprocessing import Pool
def getdf_bypath(path):
    a = pd.read_csv(path)
    a = a.rename(columns = {'OpenPx':'open','ClosePx':'close','HighPx':'high','LowPx':'low','TotalVolumeTrade':'volume','TotalValueTrade':'amount','NumTrades':'numtrades'})
    a = a[['dt', 'Ticker', 'open', 'close', 'high', 'low', 'numtrades', 'volume', 'amount','IOPV']]
    a['dt'] = a['dt'].astype('str')
    a['dt'] = pd.to_datetime(a['dt'])
    return a.set_index(['dt','Ticker'])
    
dflist = []
with Pool(24) as pool:
    dflist = pool.map(getdf_bypath, pathlist)
print('done')
totaldf = pd.concat(dflist, axis = 0).sort_index()

totaldfunique = totaldf[~totaldf.index.duplicated()].sort_index()

IO.pd_hdf5_writer(totaldfunique, '/data/user/015626/data/share/MD/CHINA_FUND/daily/MD_CHINA_ETF_DAILY.h5', dataset='MD_CHINA_ETF_DAILY')