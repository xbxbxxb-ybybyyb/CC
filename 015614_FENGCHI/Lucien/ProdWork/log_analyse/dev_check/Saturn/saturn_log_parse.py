# coding: utf-8
# Author：fengchi863
# Date ：2025/6/12 16:13

import pandas as pd
import gzip
import re

# root_path = '/data/group/800463/日内强势股/cpp_log_parse/日志拆分/20250612_prod环境/'
# root_path = '/data/user/015614/shared/for_XT/Ceres/logs/'
# root_path = '/data/user/013551/forXT/Ceres/log/'
junk_path = '/data/user/015614/junkData/'
root_path = '/data/group/800463/StrategyLog/xsim/'
log_fpath = 'CeresStrategy-2025-07-24-20250729230956-407-0-00000000.log.gz'
log_fpath = 'SaturnStrategy-2025-08-13-20250813170913-413-0-00000000.log.gz'
# log_fpath = '20250516_60-60.log'

def getValueByKeyFromLine(line, by, form='(.*?)[,\n]'):
    if by not in line:
        return ''
    try:
        return re.findall(r"%s=%s" % (by, form), line)[0]
    except:
        return 'other'

def add_excel(parse_str, log_time, line, log_tuple_list):

    if re.findall(parse_str, line):
        stock_code = getValueByKeyFromLine(line, by='symbol')
        log_tuple_list.append((log_time, stock_code, parse_str, line))

def parse_log2df(fpath):
    if fpath.endswith('.log') or fpath.endswith('.txt'):
        g_file = open(fpath)
        lines = g_file.readlines()
    elif fpath.endswith('.gz'):
        g_file = gzip.GzipFile(fpath)
        lines = g_file.readlines()
    else:
        lines = list()
        print('Error')

    if type(lines[0]) != str:
        lines = list(filter(lambda x: str(x).startswith("b'2025-"), lines))
    else:
        lines = list(filter(lambda x: str(x).startswith("2025-"), lines))

    log_tuple_list = list()

    #%% 开始解析其中的字段
    for line in lines:
        line = str(line)
        log_time = line[:19]
        if 'INFO' in line:
            line = line.split(" INFO ")[1]
        if 'exception' in line.lower() or 'error' in line.lower():
            print(line)
        # add_excel('Triggered', log_time, line[:100], log_tuple_list)
        add_excel('NewOrderPlaced', log_time, line, log_tuple_list)
        # add_excel('Order updated', log_time, line, log_tuple_list)
        # add_excel('Order info', log_time, line, log_tuple_list)
        # add_excel('Order was rejected', log_time, line, log_tuple_list)
        # add_excel('predict signals', log_time, line, log_tuple_list)
        add_excel('send_log', log_time, line, log_tuple_list)
        add_excel('to Sell', log_time, line, log_tuple_list)
        # add_excel('to jupiter', log_time, line, log_tuple_list)
        # add_excel('to Ceres', log_time, line, log_tuple_list)
        add_excel('set_priority', log_time, line, log_tuple_list)
        add_excel('get assigned', log_time, line, log_tuple_list)
        add_excel('need_assign', log_time, line, log_tuple_list)
        add_excel('credit manager', log_time, line, log_tuple_list)
        add_excel('prediction.*shouldBuy', log_time, line, log_tuple_list)
        add_excel('set current', log_time, line, log_tuple_list)
        # add_excel('to ', log_time, line, log_tuple_list)

    log_df = pd.DataFrame(log_tuple_list, columns=['时间戳', '证券代码', '日志类型', '日志内容'])
    # log_df = log_df.sort_values('时间戳')
    return log_df


if __name__ == '__main__':
    log_df = parse_log2df(root_path + log_fpath)
    log_df.to_excel(junk_path + '20250813_day_saturn_log_df.xlsx')
    # log_df.to_excel(junk_path + 'log_df.xlsx')