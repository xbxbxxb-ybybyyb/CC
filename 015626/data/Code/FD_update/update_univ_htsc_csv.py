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
logger = Log('update_universe')

    

def convert_path(path: str) -> str:
    seps = r'\/'
    sep_other = seps.replace(os.sep, '')
    return path.replace(sep_other, os.sep) if sep_other in path else path


ftp_base_path = '/XQuant/015626/ftp_data/UNIV/HTSC/'
base_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/stock_universe/HTSC'

ftp.downloadFile(os.path.join(ftp_base_path, 'ftp_path.txt'), os.path.join(base_path, 'ftp_path.txt'))

for line in open(os.path.join(base_path, 'ftp_path.txt'),"r"):
    line = line[:-1]
    remotepath = line.split('&')[0]
    localpath = convert_path(line.split('&')[1])
    if localpath.startswith('Z'):
        localpath = localpath.replace('Z:','/data/group/800080')
    else:
        localpath = localpath.replace('A:',base_path)
    ftp.downloadFile(remotepath, localpath)
    print(localpath + '  is done')


