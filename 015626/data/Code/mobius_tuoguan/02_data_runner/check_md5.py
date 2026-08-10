import os
import hashlib
import subprocess
from xquant.factordata import FactorData
import notice


# 发送铃克消息
def send_link_message(msg):
    lm = notice.LinkMessage()
    lm.sendMessage(msg)


def get_file_md5(filename):
    md5_hash = hashlib.md5()
    with open(filename, "rb") as file:
        for chunk in iter(lambda: file.read(32768), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def get_md5_from_cmd(source_file):
    exe_array = ['/usr/bin/md5sum', source_file]
    run = subprocess.Popen(exe_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = run.communicate()
    result = stdout.decode('utf-8')
    return result.split(' ')[0]


def check(source_path, dest_path):
    for root, dirs, files in os.walk(source_path):    
        for file_name in files:
            if file_name.endswith('.SH') or file_name.endswith('.SH') or file_name.startswith('FS_'):
                source_file = os.path.join(source_path, file_name)
                dest_file = os.path.join(dest_path, file_name)
                source_md5 = get_md5_from_cmd(source_file)
                dest_md5 = get_md5_from_cmd(dest_file)
                if dest_md5 != source_md5:
                    print("***** {} diff ******".format(source_file))
                    send_link_message('file={} not diff, retry copy again'.format(file_name))
                #else:

                    # print("file={} ------ source={}, dest={} ------".format(file_name, source_md5, dest_md5))


if __name__ == '__main__':
    s = FactorData()
    today = '20250317'
    trading_list = s.tradingday(today, -21)

    for day in trading_list:
        source = f'/dfs/user/666466/06_prod_data/02_FactorData/{day}/offset_0/01_Indicator'
        dest = f'/dfs/user/666466/03_mobius/02_FactorData/{day}/offset_0/01_Indicator'
        check(source, dest)
