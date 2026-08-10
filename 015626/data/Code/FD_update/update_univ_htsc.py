'''
if reload history data, you should remove csv in SH50 by hand first.
weiych
'''


from xquant.xqutils.xqfile import FTPFile
ftp = FTPFile()

from multifactor.IO import IO
from multifactor.data.utils import *
import time

from log import Log
logger = Log('update_univ_htsc_h5')

def retriver(target_path):
 
    while not os.path.exists(target_path):
        logger.info('file is not exist, download from ftp')
        
        try:
            ftp.downloadFile('015626/ftp_data/UNIV/UNIV_CHINA_STOCK_DAILY_HTSC.h5', target_path)
        except Exception as e:
            print(e)
            print('***  files are not in ftp  ***')
        time.sleep(300)
    
    print('retriver finish!')
    

sdate,edate,cdate_list = check_update_date()
flag_root = '/data/user/015626/FLAG/' + str(edate) + '/'
if not os.path.exists(flag_root):
    os.makedirs(flag_root)
flag_path_start = flag_root + str(edate) + '_' + 'univ_htsc.start'

with open(flag_path_start,'w') as file:
    pass 
    
target_path = '/data/group/800080/warehouse/prod/UNIV/CHINA_STOCK/DAILY/HTSC/UNIV_CHINA_STOCK_DAILY_HTSC.h5'
if os.path.exists(target_path):
    os.remove(target_path)    
    
retriver(target_path)

print('h5 is done.')

flag_path_success = flag_root + str(edate) + '_' + 'univ_htsc.success'
with open(flag_path_success,'w') as file:
    pass 