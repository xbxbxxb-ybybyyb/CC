# @Time : 2021/7/6 16:04
# @Author : Zhichen Lu
# @File : FTPTransfer.py

from ftplib import FTP
import os, datetime


def transfer_dir_from_FTP60(target_path, file_list=None, address='168.8.2.60', user='zsd', pwd='zsd',
                            file_path='015664'):
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    ftp = FTP()
    ftp.encoding = 'gb18030'
    ftp.connect(address)
    ftp.login(user=user, passwd=pwd)
    for each in file_path.split('/'):
        ftp.cwd(each)

    if file_list is None:
        file_list = ftp.nlst()
    print(file_list)
    for file_name in file_list:
        if file_name not in ftp.nlst():
            raise Exception('No exist file', file_name)
        bufsize = 2048
        file_handler = open(f'{target_path}{file_name}', 'wb').write
        ftp.retrbinary('RETR %s' % os.path.basename(file_name), file_handler, bufsize)
        ftp.set_debuglevel(0)
        print(file_name, 'done')
    ftp.quit()


def transfer_dir_from_FTP68(target_path, target_name, file_list=None, address='168.8.2.68', user='xquant', pwd='Xquant-32',
                            file_path='015664'):
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    ftp = FTP()
    ftp.encoding = 'gb18030'
    ftp.connect(address)
    ftp.login(user=user, passwd=pwd)
    for each in file_path.split('/'):
        ftp.cwd(each)

    if file_list is None:
        file_list = ftp.nlst()
    file_name = sorted(file_list)[-1]
    if file_name not in ftp.nlst():
        raise Exception('No exist file', file_name)
    bufsize = 2048
    file_handler = open(f'{target_path}{target_name}', 'wb').write
    ftp.retrbinary('RETR %s' % os.path.basename(file_name), file_handler, bufsize)
    ftp.set_debuglevel(0)
    print(file_name, 'done')
    ftp.quit()

# today = int(datetime.date.today().strftime('%Y%m%d'))

# transfer_dir_from_FTP60(f'/data/group/800319/strategy_local_path3/restrict_list/{today}/',target_name='解禁池.xlsx',file_path=f'XQuant/015664/解禁申请/')
