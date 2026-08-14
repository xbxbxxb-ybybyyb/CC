# coding: utf-8
# Author：fengchi863
# Date ：2023/3/22 14:26

"""
20230322，给王敬传两份日志，去重操作
"""

import datetime
import gzip
import os

from tqdm import tqdm

date = datetime.datetime.today().strftime('%Y%m%d')
output_log_path = '/data/group/800463/xiely/日内强势股/log/'

def get_lines(fpath):
    g_file = gzip.GzipFile(fpath)
    return list(map(lambda x: bytes.decode(x), g_file.readlines()))

parse_file_fpath_list = [
    output_log_path + 'StrongStrategy-2023-03-06-uat_lite-20230328.log.gz',
    output_log_path + 'StrongStrategy-2023-03-07-uat_lite-20230328.log.gz',
]

tcp2version_dcit = {'168.62.9.55': 'low_median_96',
                    '168.62.1.38': 'low_median_96',
                    '168.62.1.39': 'low_median_96',
                    '100.69.9.53': 'low_median_48',
                    '100.69.9.54': 'low_median_48',
                    '100.69.9.52': 'down_high_48',
                    '168.62.1.83': 'down_high_48',
                    '168.62.1.80': 'up_high_48',
                    '168.62.1.82': 'up_high_48'}

wangj_log_path = '/data/user/015614/shared/for_wj/log/'
xiely_new_log_path = '/data/group/800463/fengc/for_xly/log/'

def dropdup(parse_file_fpath):
    wangj_log = ''
    xiely_log = ''
    lines = get_lines(parse_file_fpath)

    # 给敬姐看
    print('parse log for wangj')
    if len(lines) > 0:
        for line in tqdm(lines):
            machine_code = line[line.find('[StrongStrategy-algo'):line.find('-n0]')]
            machine_code = machine_code.split('-')[-1]
            if machine_code[-2:] in ['55', '38', '39']:
                wangj_log += line
            if machine_code[-2:] in ['55', '38', '39'] and 'ParamsLog' not in line and 'OpenPX' not in line:
                xiely_log += line
        f = open(wangj_log_path + f'{os.path.basename(parse_file_fpath)[:-7]}' + '.txt', 'w')
        f.write(wangj_log)
        f.close()

        f = open(xiely_new_log_path + f'{os.path.basename(parse_file_fpath)[:-7]}' + '.txt', 'w')
        f.write(xiely_log)
        f.close()


if __name__ == '__main__':
    for parse_file_fpath in parse_file_fpath_list:
        dropdup(parse_file_fpath)