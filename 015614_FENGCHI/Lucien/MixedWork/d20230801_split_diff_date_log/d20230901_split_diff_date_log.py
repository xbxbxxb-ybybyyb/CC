# coding: utf-8
# Author：fengchi863
# Date ：2023/9/1 11:14

import gzip
log_fpath = '/data/group/800463/StrategyLog/sim/EventDrivenCpp-2023-08-31.log.gz'
log_g_file = gzip.GzipFile(log_fpath)
log_lines = log_g_file.readlines()
log_lines = list(filter(lambda x: str(x).startswith("b'2023-"), log_lines))

log20230831 = ''

for line in log_lines:
    format_time = str(line[11:19])[2:-1]
    if '22:00:00' <= str(format_time) or '00:00:00' <= str(format_time) <= '06:00:00':
        log20230831 += bytes.decode(line, errors='ignore')

save_path = '/data/group/800463/StrategyLog/sim/StrongStrategy.log.gz/'
for dat in ['20230831']:
    dat_str = dat[:4] + '-' + dat[4:6] + '-' + dat[6:]
    f = open(save_path + f'EventDrivenCpp-{dat_str}.log', 'w')
    tmp_log = eval(f'log{dat}')
    f.writelines(tmp_log)
    f.close()

    f_ungz = open(save_path + f'EventDrivenCpp-{dat_str}.log', 'rb')
    f_gz = gzip.open(save_path + f'EventDrivenCpp-{dat_str}.log.gz', 'wb')
    f_gz.writelines(f_ungz)
    f_ungz.close()
    f_gz.close()



