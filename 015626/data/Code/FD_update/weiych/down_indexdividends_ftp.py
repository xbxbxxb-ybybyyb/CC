'''
if reload history data, you should remove csv in SH50 by hand first.
weiych
'''
import datetime as dt

from multifactor.data.utils import *
from multifactor.utility.dt import *

from xquant.xqutils.xqfile import FTPFile
ftp = FTPFile()

from multifactor.IO import IO
from multifactor.data.utils import *
import time


def retriver(tommorrow):
    
    ftp_path = os.path.join('/XQuant/015626/ftp_data/IndexDividends', 'IndexDividends_' + tommorrow + '.xlsx')
    target_path = os.path.join('/data/user/015626/data/share/IndexDividends', 'IndexDividends_' + tommorrow + '.xlsx')
        
    while not os.path.exists(target_path):    
        try:
            ftp.downloadFile(ftp_path, target_path)
        except Exception as e:
            print(e)
            print('***  files are not in ftp  ***')
        time.sleep(300)
    
    print('retriver finish!')
    

sdate,edate,cdate_list = check_update_date()
nowtime = dt.datetime.strptime(str(sdate),'%Y%m%d')
tradingDates = get_trading_date_range(nowtime - dt.timedelta(30),(nowtime + dt.timedelta(30)).strftime('%Y%m%d'))
tradingDates = [d.strftime('%Y%m%d') for d in tradingDates]
tommorrow = tradingDates[tradingDates.index(str(sdate)) + 1]
print(tommorrow)
retriver(tommorrow)

print('retriver is done.')
