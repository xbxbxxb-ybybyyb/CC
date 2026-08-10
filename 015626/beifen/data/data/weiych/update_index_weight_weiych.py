# -*- coding: utf-8 -*-
"""
update_index_weight
@weiych
"""

import ftplib
from zipfile import ZipFile
from multifactor.data.utils import *

def ftp_reader(ftp_obj, remote_file, local_file):
    remote_file_dir = os.path.dirname(remote_file)
    remote_file = os.path.basename(remote_file)
    if remote_file_dir:
        ftp_obj.cwd(remote_file_dir)
    with open(local_file, 'wb') as fout:
        def callback(data):
            fout.write(data)

        ftp_obj.retrbinary('RETR %s' % remote_file, callback)


def ftp_download(check_date):
    ftp = ftplib.FTP('183.195.154.145')
    ftp.login('csiht', '35708572')
    # check_date = datetime.datetime.now().date().strftime('%Y%m%d')
    for idx in ['000300', '000905', '000016']:
        try:
            weight_col = {'000300': 'HS300', '000905': 'ZZ500', '000016': 'SH50'}[idx]
            csv_path = r'Z:\warehouse\prod\LOCAL_DATA\CSV\stock_universe\%s' % weight_col
            stash_path = r'Z:\warehouse\prod\LOCAL_DATA\INDEX_BACKUP\excel_raw\%s' % idx
            local_file = os.path.join(stash_path, '%s.zip' % check_date)
            ftp_reader(ftp, '/idxdata/data/asharedata/%s/weight_for_next_trading_day/%sweightnextday%s.zip' % (
            idx, idx, check_date),
                       local_file)
            with ZipFile(local_file, 'r') as zipObj:
                zipObj.extractall(stash_path)
            os.remove(local_file)
            data = pd.read_excel(os.path.join(stash_path, '%sweightnextday%s.xls' % (idx, check_date)),
                                 dtype={'成分券代码\nConstituent Code': str})
            data['Ticker'] = data['成分券代码\nConstituent Code'] + \
                             data['交易所\nExchange'].apply(lambda x: {'Shenzhen': '.SZ', 'Shanghai': '.SH'}[x])
            data = data[['Ticker', '权重(%)\nWeight(%)']]

            data.columns = ['Ticker', weight_col]
            data = data.set_index('Ticker')
            data[weight_col] = data[weight_col]
            data.to_csv(os.path.join(csv_path, str(check_date) + '.csv'))
        except Exception as _exp:
            print('%s raised: %s' % (idx, _exp))
    ftp.close()

if __name__ == '__main__':
    sdate,edate,cdate_list = check_update_date()
    print(sdate, ' %%%%%%%%%%%%%%%%%%%')
    ftp_download(str(sdate))


