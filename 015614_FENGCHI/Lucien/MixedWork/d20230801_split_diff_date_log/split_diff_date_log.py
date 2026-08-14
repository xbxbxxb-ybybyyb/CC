# coding: utf-8
# Author：fengchi863
# Date ：2023/8/1 8:56

import gzip
log_fpath = '/data/group/800463/StrategyLog/sim/StrongStrategy-2023-07-31.log.gz'
log_g_file = gzip.GzipFile(log_fpath)
log_lines = log_g_file.readlines()
log_lines = list(filter(lambda x: str(x).startswith("b'2023-"), log_lines))

log20230724 = ''
log20230725 = ''
log20230726 = ''
log20230727 = ''
log20230728 = ''

for line in log_lines:
    format_time = str(line[11:19])[2:-1]
    if '19:40:00' <= str(format_time) <= '20:40:59':
        log20230724 += bytes.decode(line, errors='ignore')
    elif '20:41:00' <= str(format_time) <= '22:48:59':
        log20230725 += bytes.decode(line, errors='ignore')
    elif '20:49:00' <= str(format_time) <= '23:42:59':
        log20230726 += bytes.decode(line, errors='ignore')
    elif '23:43:00' <= str(format_time)  or str(format_time) <= '00:49:59':
        log20230727 += bytes.decode(line, errors='ignore')
    elif '00:50:00' <= str(format_time) <= '06:00:00':
        log20230728 += bytes.decode(line, errors='ignore')

save_path = '/data/group/800463/StrategyLog/sim/StrongStrategy.log.gz/'
for dat in ['20230724', '20230725', '20230726', '20230727', '20230728']:
    dat_str = dat[:4] + '-' + dat[4:6] + '-' + dat[6:]
    f = open(save_path + f'StrongStrategy-{dat_str}.log', 'w')
    tmp_log = eval(f'log{dat}')
    f.writelines(tmp_log)
    f.close()

    f_ungz = open(save_path + f'StrongStrategy-{dat_str}.log', 'rb')
    f_gz = gzip.open(save_path + f'StrongStrategy-{dat_str}.log.gz', 'wb')
    f_gz.writelines(f_ungz)
    f_ungz.close()
    f_gz.close()



