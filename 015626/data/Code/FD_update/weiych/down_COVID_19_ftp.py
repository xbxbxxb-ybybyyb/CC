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


def retriver():
    ftp_path = os.path.join('/XQuant/015626/ftp_data/COVID_19/COVID_19_cumulative.csv')
    target_path = os.path.join('/data/user/015626/data/share/COVID_19/COVID_19_cumulative.csv')
     
    ftp.downloadFile(ftp_path, target_path)
    print('retriver is done.')
      
retriver()


